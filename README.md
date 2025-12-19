# streamlit
Sandbox for streamlit study

## 자동 전망 업데이트 파이프라인
한국은행 경제전망분석 발표 직후 데이터를 자동 갱신하려면 `data_pipeline.py`를 사용하세요.

### 준비물
- 파이썬 의존성: `pip install -r requirements.txt`
- 인덱스 페이지 URL(발표 자료가 연결된 페이지) 또는 로컬로 받은 엑셀/CSV 파일

### 사용법
1. **크롤링 + 다운로드 + 정규화**
   ```bash
   python data_pipeline.py \
     --index-url "https://example.bok.or.kr/..." \
     --keyword "경제전망" \
     --time-column t \
     --forecast-column forecast \
     --realized-column realized \
     --horizon-columns cpi0 cpi1 cpi2 cpi3 cpi4
   ```
   - 인덱스 페이지에서 `keyword`가 들어간 최신 링크를 찾아 다운로드합니다.
   - `data/processed/cpi_inflation.csv`, `data/processed/infl.csv`, `data/processed/metadata.json`을 갱신합니다.

2. **로컬 파일로 시험 실행**
   ```bash
   python data_pipeline.py --local-file path/to/release.xlsx --forecast-column 202501
   ```
   - 크롤링 없이 지정 파일을 사용해 동일한 산출물을 만듭니다.

3. **Streamlit 앱 반영**
   - 앱은 `data/processed/*.csv`가 있으면 자동으로 사용하고, 없으면 루트의 기본 CSV로 fallback 합니다.
   - `data/processed/metadata.json`에 기록된 `downloaded_at`과 `source_url`이 앱의 “Last Update”에 표시됩니다.

### 작업 순서 예시(서버/배치)
1. 발표일 직후 크론에서 `python data_pipeline.py --index-url ...` 실행
2. 성공 시 `data/processed` 산출물을 앱이 자동 사용
3. 실패 알림 시 이전 CSV가 그대로 사용되도록 유지
