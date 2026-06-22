import pandas as pd
import numpy as np
import os

def run_biological_validation():
    csv_path = "datasets/thought_train_ADNI.csv"
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    results = []
    
    print("| PTID | Clinical Transition (Cycle) | Omega Warning (<90%) | Lead Time (Years) | Omega/Atrophy Corr |")
    print("|---|---|---|---|---|")
    
    for ptid, group in df.groupby("PTID"):
        group = group.sort_values("cycle")
        
        # 1. Clinical Transition
        # Find the first cycle where DX is not 'CN'
        transition_rows = group[group["DX"] != "CN"]
        t_clinical = transition_rows["cycle"].iloc[0] if not transition_rows.empty else group["cycle"].max()
        
        # 2. Omega Warning
        # First breach of 90% (skipping baseline)
        warning_rows = group[(group["VISCODE"] != "bl") & (group["Omega"] < 90)]
        t_warning = warning_rows["cycle"].iloc[0] if not warning_rows.empty else group["cycle"].max()
        
        # Lead Time in Years (since 'cycle' is AGE)
        lead_time = t_clinical - t_warning
        
        # 3. Correlation between Omega and Hippocampal Volume
        corr = group["Omega"].corr(group["Hippocampus_Volume"], method='spearman')
        
        # We only care about progressors for lead-time analysis
        if not transition_rows.empty:
            print(f"| {ptid} | {t_clinical:.1f} | {t_warning:.1f} | {lead_time:+.1f} yrs | {corr:.4f} |")
            results.append(lead_time)
            
    if results:
        print(f"\nAverage Biological Structural Lead-Time: {np.mean(results):.2f} years")
    else:
        print("\nNo clinical progressors detected in the sample.")

if __name__ == "__main__":
    run_biological_validation()
