from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urljoin, urlsplit

import pandas as pd
import requests


log = logging.getLogger(__name__)


class AnchorCollector(HTMLParser):
    """Minimal HTML anchor collector to avoid external parsing dependencies."""

    def __init__(self) -> None:
        super().__init__()
        self.links: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


def _score_url(url: str) -> tuple[int, str]:
    """
    Score URLs so we can select the latest-looking candidate.
    We look for YYYY, YYYYQ#, or YYYYMM patterns and then fall back to the URL string.
    """
    tokens = re.findall(r"20\d{2}Q\d|20\d{2}[01]\d|20\d{2}", url)
    numeric_token = max(tokens) if tokens else ""
    return (int(numeric_token[:4]) if numeric_token else 0, numeric_token, url)


@dataclass
class PipelineConfig:
    index_url: Optional[str] = None
    keyword: str = "경제전망"
    raw_dir: Path = Path("data/raw")
    output_dir: Path = Path("data/processed")
    base_cpi_path: Path = Path("cpi_inflation.csv")
    base_infl_path: Path = Path("infl.csv")
    time_column: str = "t"
    forecast_column: str = "forecast"
    realized_column: str = "realized"
    horizon_columns: List[str] = field(default_factory=lambda: ["cpi0", "cpi1", "cpi2", "cpi3", "cpi4"])
    issue: Optional[str] = None
    extensions: tuple[str, ...] = (".xlsx", ".xls", ".csv")


class OutlookPipeline:
    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        self.config.raw_dir.mkdir(parents=True, exist_ok=True)
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    def discover_latest_url(self) -> str:
        if not self.config.index_url:
            raise ValueError("index_url is required when local file is not provided.")

        log.info("Requesting index page: %s", self.config.index_url)
        response = requests.get(self.config.index_url, timeout=30)
        response.raise_for_status()

        collector = AnchorCollector()
        collector.feed(response.text)

        candidates = []
        for href in collector.links:
            lower_href = href.lower()
            if not lower_href.endswith(self.config.extensions):
                continue
            if self.config.keyword not in href:
                continue
            candidates.append(urljoin(self.config.index_url, href))

        if not candidates:
            raise RuntimeError("No downloadable candidates were found on the index page.")

        latest = sorted(candidates, key=_score_url)[-1]
        log.info("Selected latest candidate: %s", latest)
        return latest

    def download(self, url: str) -> Path:
        filename = urlsplit(url).path.split("/")[-1] or "download"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        destination = self.config.raw_dir / f"{timestamp}_{filename}"

        log.info("Downloading %s -> %s", url, destination)
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(destination, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return destination

    def _load_release(self, path: Path) -> pd.DataFrame:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            return pd.read_csv(path)
        if suffix in {".xls", ".xlsx"}:
            try:
                return pd.read_excel(path)
            except ImportError as exc:
                raise ImportError(
                    "Reading Excel files requires the optional dependency 'openpyxl'. "
                    "Install it and rerun the pipeline."
                ) from exc
        raise ValueError(f"Unsupported file type: {suffix}")

    def _infer_issue_name(self, release_path: Path) -> str:
        if self.config.issue:
            return self.config.issue

        matches = re.findall(r"20\d{2}[Qq]\d|20\d{2}[01]\d", release_path.name)
        if matches:
            return matches[0].replace("_", "").replace("-", "")
        return datetime.utcnow().strftime("%Y%m")

    def _prepare_release(self, df: pd.DataFrame) -> pd.DataFrame:
        required = {self.config.time_column, self.config.forecast_column}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Release file is missing required columns: {', '.join(sorted(missing))}")
        tidy = df[[self.config.time_column, self.config.forecast_column]].copy()
        tidy.rename(
            columns={
                self.config.time_column: "t",
                self.config.forecast_column: "new_forecast",
            },
            inplace=True,
        )
        return tidy

    def _update_cpi_inflation(self, release: pd.DataFrame, issue_name: str) -> Path:
        base = pd.read_csv(self.config.base_cpi_path)
        merged = base.merge(release, on="t", how="left")
        merged[issue_name] = merged["new_forecast"]
        merged.drop(columns=["new_forecast"], inplace=True)
        destination = self.config.output_dir / "cpi_inflation.csv"
        merged.to_csv(destination, index=False)
        return destination

    def _update_infl(self, raw_release: pd.DataFrame) -> Optional[Path]:
        missing = [col for col in [self.config.time_column, self.config.realized_column] if col not in raw_release.columns]
        missing += [col for col in self.config.horizon_columns if col not in raw_release.columns]
        if missing:
            log.warning("Skipping infl.csv update because columns are missing: %s", ", ".join(missing))
            return None

        base = pd.read_csv(self.config.base_infl_path)
        release = raw_release[[self.config.time_column, self.config.realized_column] + self.config.horizon_columns].copy()
        release.rename(columns={self.config.time_column: "time", self.config.realized_column: "realized_cpi"}, inplace=True)
        release.set_index("time", inplace=True)
        base.set_index("time", inplace=True)

        for i, col in enumerate(self.config.horizon_columns):
            target_col = f"cpi{i}"
            base.loc[release.index, target_col] = release[col]
        base.loc[release.index, "realized_cpi"] = release["realized_cpi"]
        base.sort_index(inplace=True)

        destination = self.config.output_dir / "infl.csv"
        base.reset_index().to_csv(destination, index=False)
        return destination

    def _write_metadata(self, source: str, issue: str, artifacts: Iterable[Path]) -> Path:
        metadata = {
            "source_url": source,
            "issue": issue,
            "downloaded_at": datetime.utcnow().isoformat() + "Z",
            "artifacts": [str(p) for p in artifacts],
        }
        destination = self.config.output_dir / "metadata.json"
        destination.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
        return destination

    def run(self, local_file: Optional[Path] = None) -> dict[str, Optional[Path]]:
        source_url = ""
        if local_file:
            release_path = local_file
            source_url = str(local_file)
        else:
            latest_url = self.discover_latest_url()
            release_path = self.download(latest_url)
            source_url = latest_url

        raw_release = self._load_release(release_path)
        release = self._prepare_release(raw_release)
        issue_name = self._infer_issue_name(release_path)

        artifacts: List[Path] = []
        cpi_path = self._update_cpi_inflation(release, issue_name)
        artifacts.append(cpi_path)

        infl_path = self._update_infl(raw_release)
        if infl_path:
            artifacts.append(infl_path)

        metadata_path = self._write_metadata(source_url, issue_name, artifacts)

        return {"cpi_inflation": cpi_path, "infl": infl_path, "metadata": metadata_path}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and normalize the latest Bank of Korea outlook release.")
    parser.add_argument("--index-url", help="Listing page that links to the latest outlook release.")
    parser.add_argument("--keyword", default="경제전망", help="Keyword to filter outlook links.")
    parser.add_argument("--local-file", type=Path, help="Use a local release file instead of crawling.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"), help="Directory to store downloaded files.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"), help="Directory to store processed CSVs.")
    parser.add_argument("--time-column", default="t", help="Name of the time column in the release file.")
    parser.add_argument("--forecast-column", default="forecast", help="Column containing the primary inflation forecast.")
    parser.add_argument("--realized-column", default="realized", help="Column containing realized inflation.")
    parser.add_argument(
        "--horizon-columns",
        nargs="+",
        default=["cpi0", "cpi1", "cpi2", "cpi3", "cpi4"],
        help="Forecast column names for horizons 0-4 used to refresh infl.csv.",
    )
    parser.add_argument("--issue", help="Override the inferred issue name for the new column.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    config = PipelineConfig(
        index_url=args.index_url,
        keyword=args.keyword,
        raw_dir=args.raw_dir,
        output_dir=args.output_dir,
        time_column=args.time_column,
        forecast_column=args.forecast_column,
        realized_column=args.realized_column,
        horizon_columns=args.horizon_columns,
        issue=args.issue,
    )
    pipeline = OutlookPipeline(config)
    artifacts = pipeline.run(local_file=args.local_file)
    for name, path in artifacts.items():
        log.info("%s -> %s", name, path)


if __name__ == "__main__":
    main()
