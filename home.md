

### The Bank of Korea's inflation rate forecasts
- The red line is the actual realized inflation rate,
- And the dashed lines are the forecasts of each *Economic Outlook* issue.


### AR(1) Bias correction strategy
- We find strong evidence that the forecast errors follow the AR(1) process.
- Hence, we utilize this finding to correct the inflation forecast bias.
- Model: $e_{h,t}=\alpha e_{h,t-1}+u_{h,t}$ for $h=0,1,2,3$. 
  - $h$ represents the forecast horizon (in quarters).
  - In the paper we find that AR(1) with *recursive* window is the best.

### Real-time Bias-corrections
- Again, the red line is the actual realized values,
- and the dashed lines are the BoK's forecasts.
- The blue line is the *real-time* bias corrections of the BoK's forecasts.
  [Last Update:]