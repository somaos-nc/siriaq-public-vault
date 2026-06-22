import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve

def run_longitudinal_prediction():
    print("====================================================")
    print("Thought B2B COMMERCIAL PIPELINE: LONGITUDINAL PREDICTION")
    print("Target: CN \u2192 MCI/AD Converter Analysis (Baseline \u03A9 Only)")
    print("====================================================\n")

    # Load Data
    demog = pd.read_csv("datasets/adni4_raw/RMT_PTDEMOG_15Jun2026.csv")
    apoe = pd.read_csv("datasets/adni4_raw/RMT_APOERES_15Jun2026.csv")
    screen = pd.read_csv("datasets/adni4_raw/RMT_Screening_15Jun2026.csv")
    story = pd.read_csv("datasets/adni4_raw/RMT_STORYTELLER_15Jun2026.csv", low_memory=False)

    # 1. Prepare Base Features
    story['SCREENER_SCORE'] = pd.to_numeric(story['SCREENER_SCORE'], errors='coerce')
    story['SCREENER_RECOMMEND'] = pd.to_numeric(story['SCREENER_RECOMMEND'], errors='coerce')
    
    # 2. Map Clinical Covariates for H_bio_risk
    df_cov = demog[['ADNIOnlineID', 'Age_Baseline', 'RMT_Education']].drop_duplicates()
    df_cov = df_cov.merge(apoe[['ADNIOnlineID', 'GENOTYPE']].drop_duplicates(), on='ADNIOnlineID', how='left')
    
    screen['RMT_MntlHlth'] = pd.to_numeric(screen['RMT_MntlHlth'], errors='coerce').fillna(0)
    screen['RMT_FamAD'] = pd.to_numeric(screen['RMT_FamAD'], errors='coerce').fillna(0)
    df_cov = df_cov.merge(screen[['ADNIOnlineID', 'RMT_FamAD', 'RMT_MntlHlth']].drop_duplicates(), on='ADNIOnlineID', how='inner')
    
    df_cov['APOE_e4'] = df_cov['GENOTYPE'].apply(lambda x: 1 if str(x) in ['3/4', '2/4', '4/4'] else 0)
    df_cov['Age_Baseline'] = pd.to_numeric(df_cov['Age_Baseline'], errors='coerce').fillna(df_cov['Age_Baseline'].median())
    df_cov['Age75'] = (df_cov['Age_Baseline'] >= 75).astype(int)
    df_cov['Edu'] = pd.to_numeric(df_cov['RMT_Education'], errors='coerce').fillna(12)
    df_cov['HighEdu'] = (df_cov['Edu'] > 12).astype(int)
    
    df_cov['C_clinical'] = 10*df_cov['APOE_e4'] + 5*df_cov['RMT_FamAD'] - 3*df_cov['HighEdu'] + 4*df_cov['Age75'] + 3*df_cov['RMT_MntlHlth']
    max_c = df_cov['C_clinical'].max()
    df_cov['H_bio_risk'] = df_cov['C_clinical'] / max_c if max_c > 0 else 0

    # 3. Longitudinal Tracking (Isolate Converters vs. Stable CN)
    # Baseline records (m00)
    bl_story = story[story['RMT_Timepoint'] == 'm00'].dropna(subset=['SCREENER_SCORE', 'SCREENER_RECOMMEND'])
    fu_story = story[story['RMT_Timepoint'] != 'm00'].dropna(subset=['SCREENER_RECOMMEND'])
    
    # Merge baseline scores with covariates
    bl_df = bl_story[['ADNIOnlineID', 'SCREENER_SCORE', 'SCREENER_RECOMMEND']].merge(df_cov, on='ADNIOnlineID', how='inner')
    
    # Calculate Baseline Omega (Same empirical formula as cross-sectional)
    bl_df['Cognitive_coherence'] = 1.755 * bl_df['SCREENER_SCORE'] - 69.77
    bl_df['Cognitive_coherence'] = bl_df['Cognitive_coherence'].clip(0, 100)
    raw_omega = bl_df['Cognitive_coherence'] * 0.90 + (1 - bl_df['H_bio_risk']) * 20.3
    bl_df['Omega_BIO_pilot'] = raw_omega * 1.25 - 13.0
    bl_df['Omega_BIO_pilot'] = bl_df['Omega_BIO_pilot'].clip(0, 100)
    
    # Filter to only subjects who are Cognitively Normal (CN) at baseline
    cn_baseline = bl_df[bl_df['SCREENER_RECOMMEND'] == 0].copy()
    
    # Find subsequent conversions in follow-up
    converters_ids = set(fu_story[fu_story['SCREENER_RECOMMEND'] == 1]['ADNIOnlineID'])
    stable_ids = set(fu_story[fu_story['SCREENER_RECOMMEND'] == 0]['ADNIOnlineID']) - converters_ids
    
    # Label the baseline dataset
    def label_conversion(uid):
        if uid in converters_ids: return 1
        if uid in stable_ids: return 0
        return np.nan # No follow-up
        
    cn_baseline['Converted'] = cn_baseline['ADNIOnlineID'].apply(label_conversion)
    analytical_cohort = cn_baseline.dropna(subset=['Converted']).copy()
    
    print("1. COHORT DEFINITION")
    n_stable = len(analytical_cohort[analytical_cohort['Converted'] == 0])
    n_convert = len(analytical_cohort[analytical_cohort['Converted'] == 1])
    print(f"   Stable CN (No Conversion): {n_stable}")
    print(f"   Converters (CN \u2192 MCI/AD): {n_convert}")
    
    # 4. Probabilistic Prediction Metrics (using BASELINE Omega to predict FUTURE conversion)
    y_true = analytical_cohort['Converted'].values
    # Invert Omega for risk probability (lower omega = higher risk)
    y_scores = 100 - analytical_cohort['Omega_BIO_pilot'].values
    
    auc = roc_auc_score(y_true, y_scores)
    print("\n2. TRUE PREDICTIVE METRICS (B2B Gold-Standard)")
    print(f"   Longitudinal ROC-AUC Score: {auc:.4f}")
    
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    J = tpr - fpr
    optimal_idx = np.argmax(J)
    optimal_threshold_inverted = thresholds[optimal_idx]
    optimal_omega = 100 - optimal_threshold_inverted
    
    sensitivity = tpr[optimal_idx]
    specificity = 1 - fpr[optimal_idx]
    
    print(f"   Optimal Predictive Threshold: Baseline \u03A9 < {optimal_omega:.1f}")
    print(f"   Sensitivity (True Positive Rate): {sensitivity*100:.1f}%")
    print(f"   Specificity (True Negative Rate): {specificity*100:.1f}%")
    
    # 5. Lead-Time Calculation
    print("\n3. PREDICTIVE LEAD-TIME DISTRIBUTION")
    lead_times = []
    converters_fu = fu_story[(fu_story['ADNIOnlineID'].isin(converters_ids)) & (fu_story['SCREENER_RECOMMEND'] == 1)]
    for uid, group in converters_fu.groupby('ADNIOnlineID'):
        first_conversion = group['RMT_Timepoint'].min()
        # Parse 'm06', 'm12', 'm18', 'm24'
        if str(first_conversion).startswith('m'):
            try:
                months = int(first_conversion[1:])
                lead_times.append(months)
            except: pass
            
    if lead_times:
        mean_lt = np.mean(lead_times)
        max_lt = np.max(lead_times)
        print(f"   Mean Lead-Time to Clinical Conversion: {mean_lt:.2f} months")
        print(f"   Maximum Precursor Horizon Detected:    {max_lt:.1f} months")
    else:
        print("   Insufficient follow-up timestamp data for empirical lead-time.")
        
    # Generate Plot
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='#ff007f', lw=2, label=f'Longitudinal ROC Curve (AUC = {auc:.3f})')
    plt.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--')
    plt.scatter(fpr[optimal_idx], tpr[optimal_idx], marker='o', color='gold', s=100, label=f'Optimal \u03A9={optimal_omega:.1f}')
    plt.xlabel('False Positive Rate (1 - Specificity)')
    plt.ylabel('True Positive Rate (Sensitivity)')
    plt.title('Thought $\Omega_{BIO}$ Predictive Trajectory Analysis (CN \u2192 MCI/AD)')
    plt.legend(loc="lower right")
    plt.savefig('graphics/roc_auc_longitudinal.png', dpi=300)
    plt.close()
    
    print("\nGenerated Probabilistic Trajectory Graphics:")
    print("  -> graphics/roc_auc_longitudinal.png")

if __name__ == '__main__':
    run_longitudinal_prediction()
