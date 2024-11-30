
---

### AR(1) Bias correction strategy
- We find strong evidence that the forecast errors follow the AR(1) process.
- Hence, we utilize this finding to correct the inflation forecast bias.
- Model: $e_{h,t}=\alpha e_{h,t-1}+u_{h,t}$ for $h=0,1,2,3,4$. 
  - $h$ represents the forecast horizon (in quarters).
  - Lee and Seong (2024) found that AR(1) with *recursive* window is the best.
  
