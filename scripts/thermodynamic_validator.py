import pandas as pd
import numpy as np
import os

def run_all():
    datasets = ["FD001", "FD002", "FD003", "FD004"]
    results = []

    for ds in datasets:
        csv_path = os.path.join(os.path.dirname(__file__), f"../datasets/siriaq_train_{ds}.csv")
        if not os.path.exists(csv_path):
            continue
            
        df = pd.read_csv(csv_path)
        
        # 1. Lead-Time Test
        lead_times = []
        for unit_id, g in df.groupby("unit_id"):
            g = g.sort_values("cycle")
            baseline_omega = g.head(30)["Omega"].mean()
            std_var = g.head(30)["variance_score"].std() or 1e-6
            baseline_var = g.head(30)["variance_score"].mean()
            
            omega_threshold = baseline_omega * 0.95
            var_threshold = baseline_var + 2 * std_var
            
            omega_trigger_cycles = g[g["Omega"] < omega_threshold]["cycle"]
            var_trigger_cycles = g[g["variance_score"] > var_threshold]["cycle"]
            
            omega_trigger = omega_trigger_cycles.iloc[0] if not omega_trigger_cycles.empty else g["cycle"].max()
            var_trigger = var_trigger_cycles.iloc[0] if not var_trigger_cycles.empty else g["cycle"].max()
            
            if not omega_trigger_cycles.empty and not var_trigger_cycles.empty:
                lead_times.append(var_trigger - omega_trigger)
                
        avg_lead_time = np.mean(lead_times) if lead_times else 0
        pos_lead = sum(1 for x in lead_times if x > 0)
        total_lead = len(lead_times)
        
        # 2. Benchmark Correlation
        corr_omega = df["Omega"].corr(df["RUL"], method='spearman')
        corr_var = df["variance_score"].corr(df["RUL"], method='spearman')

        results.append({
            "Dataset": ds,
            "Engines": df["unit_id"].nunique(),
            "Avg_Lead_Time": avg_lead_time,
            "Pos_Lead_Ratio": f"{pos_lead}/{total_lead}",
            "Corr_Omega": corr_omega,
            "Corr_Var": corr_var
        })

    print("| Dataset | Avg Lead Time | Positive Leads | Omega/RUL Corr | Var/RUL Corr |")
    print("|---|---|---|---|---|")
    
    for r in results:
        ds = r['Dataset']
        print(f"| {ds} | {r['Avg_Lead_Time']:.2f} cycles | {r['Pos_Lead_Ratio']} | {r['Corr_Omega']:.4f} | {r['Corr_Var']:.4f} |")

if __name__ == "__main__":
    run_all()
