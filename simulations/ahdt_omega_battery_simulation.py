"""
AHDT-Ω Synthetic Battery Degradation Simulation
Reference: Halil Özbil, AHDT-Ω v1.2

Implements the Adaptive Hamiltonian Digital Twin Monte Carlo proof-of-concept.
"""

import numpy as np

def simulate_ahdt_trajectory(
    t_max=200, 
    t_0=120,          # Degradation onset
    k=0.05,           # Sigmoid steepness
    D_max=0.009,      # Max degradation impact on Hamiltonian
    sigma_H=0.0005,   # Hamiltonian noise
    sigma_V=0.015,    # Voltage noise
    alpha=120.0,      # Coherence sensitivity
    lambda_lgc=0.30,  # LGC correction factor
    eta=0.08,         # Adaptive update rate
    V_0=4.2,          # Initial Voltage
    k_V=9000.0,       # Voltage decay coupling
    V_thresh=3.70,    # Conventional alarm threshold
    Omega_thresh=0.75 # Structural alarm threshold
):
    """Simulates a single battery trajectory and compares AHDT-Ω vs Voltage monitoring."""
    
    # State tracking
    H_R = 1.0 # Real system energy tensor (scalar surrogate)
    H_D = 1.0 # Digital Twin energy tensor (scalar surrogate)
    
    history = []
    
    # Pre-generate noise to ensure reproducibility within the trajectory
    noise_H = np.random.normal(0, sigma_H, t_max)
    noise_V = np.random.normal(0, sigma_V, t_max)
    
    # Sigmoid degradation model
    def degradation(t):
        return D_max / (1.0 + np.exp(-k * (t - t_0)))
        
    for t in range(t_max):
        # 1. Real System Physics Update
        D_t = degradation(t)
        H_R_actual = 1.0 + D_t + noise_H[t]
        
        # Observable voltage (drops as degradation increases)
        V_t = V_0 - k_V * (D_t**2) + noise_V[t]
        
        # 2. AHDT-Ω Structural Error & Coherence (Algorithm 1: HAD-Ω)
        # Structural error (Frobenius drift scalar surrogate)
        E_H = H_R_actual - H_D
        delta_H = np.abs(E_H)
        
        # Coherence Score
        Omega_H = np.exp(-alpha * delta_H)
        
        # LGC Correction Layer
        Omega_star = Omega_H / (1.0 + lambda_lgc * np.log(1.0 + delta_H))
        
        # 3. Anomaly Detector
        alarm_AHDT = Omega_star < Omega_thresh
        alarm_Volt = V_t < V_thresh
        
        history.append({
            't': t,
            'V': V_t,
            'Delta_H': delta_H,
            'Omega_H': Omega_H,
            'Omega_star': Omega_star,
            'Alarm_AHDT': alarm_AHDT,
            'Alarm_Volt': alarm_Volt
        })
        
        # 4. Adaptive Digital Twin Update (Lyapunov-stable tracking)
        # H_D adapts to H_R slowly
        H_D = H_D + eta * E_H

    return history

def run_monte_carlo(N=1000):
    print(f"Running AHDT-Ω Monte Carlo Validation (N={N})...")
    
    ewg_list = []
    false_alarms = 0
    misses = 0
    
    for i in range(N):
        # Sample parameters uniformly as per paper protocol
        t_0 = np.random.uniform(90, 180)
        k = np.random.uniform(0.03, 0.07)
        D_max = np.random.uniform(0.007, 0.011)
        sigma_H = np.random.uniform(0.03 * D_max, 0.12 * D_max)
        sigma_V = np.random.uniform(0.008, 0.018)
        
        history = simulate_ahdt_trajectory(
            t_max=300, t_0=t_0, k=k, D_max=D_max, 
            sigma_H=sigma_H, sigma_V=sigma_V
        )
        
        t_ahdt = None
        t_volt = None
        fa_triggered = False
        
        for step in history:
            t = step['t']
            
            # Check false alarms in healthy window (e.g., t < 0.28 * t_0)
            if t < 0.28 * t_0 and step['Alarm_AHDT']:
                fa_triggered = True
                
            # First AHDT structural alarm
            if step['Alarm_AHDT'] and t_ahdt is None and t >= 0.28 * t_0:
                t_ahdt = t
                
            # First Voltage macroscopic alarm
            if step['Alarm_Volt'] and t_volt is None:
                t_volt = t
                
        if fa_triggered:
            false_alarms += 1
            
        if t_ahdt is not None and t_volt is not None:
            ewg_list.append(t_volt - t_ahdt)
        elif t_ahdt is None and t_volt is not None:
            misses += 1
            
    # Compile Results
    mean_ewg = np.mean(ewg_list)
    median_ewg = np.median(ewg_list)
    earlier_detection_rate = sum(1 for e in ewg_list if e > 0) / len(ewg_list) * 100
    fa_rate = false_alarms / N * 100
    miss_rate = misses / N * 100
    
    print("\nTABLE I: AHDT-Ω Monte Carlo Performance Summary")
    print("-" * 50)
    print(f"Mean EWG               : {mean_ewg:.1f} steps")
    print(f"Median EWG             : {median_ewg:.0f} steps")
    print(f"Earlier Detection Rate : {earlier_detection_rate:.1f}%")
    print(f"False Alarm Rate       : {fa_rate:.1f}%")
    print(f"Miss Rate              : {miss_rate:.1f}%")
    print("-" * 50)

if __name__ == "__main__":
    np.random.seed(42) # For reproducibility
    run_monte_carlo(N=1000)
