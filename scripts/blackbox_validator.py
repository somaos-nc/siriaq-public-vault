import pandas as pd
import numpy as np
import os

def run_battery_validation():
    datasets = ["B0005", "B0006", "B0007", "B0018"]
    results = []

    print("| Battery | EOL Cycle (Cap<1.4) | Omega Warning (<90%) | Lead Time (Cycles) | Omega/Cap Corr |")
    print("|---|---|---|---|---|")

    for ds in datasets:
        csv_path = f"datasets/siriaq_train_{ds}.csv"
        if not os.path.exists(csv_path):
            continue
            
        df = pd.read_csv(csv_path)
        
        # EOL: Capacity drops below 1.4 Ahr
        eol_cycles = df[df["capacity"] < 1.4]["cycle"]
        t_eol = eol_cycles.iloc[0] if not eol_cycles.empty else df["cycle"].max()
        
        # Omega Warning: First breach of 90%
        # We skip the very first few cycles to avoid initialization noise
        warning_cycles = df[(df["cycle"] > 5) & (df["Omega"] < 90)]["cycle"]
        t_warning = warning_cycles.iloc[0] if not warning_cycles.empty else df["cycle"].max()
        
        lead_time = t_eol - t_warning
        
        # Correlation between Omega and Capacity
        corr = df["Omega"].corr(df["capacity"], method='spearman')
        
        print(f"| {ds} | {t_eol} | {t_warning} | {lead_time} | {corr:.4f} |")
        
        results.append({
            "Battery": ds,
            "T_EOL": t_eol,
            "T_Warning": t_warning,
            "Lead_Time": lead_time,
            "Correlation": corr
        })

    avg_lead = np.mean([r["Lead_Time"] for r in results])
    print(f"\nAverage Structural Lead Time: {avg_lead:.2f} cycles")

if __name__ == "__main__":
    run_battery_validation()
