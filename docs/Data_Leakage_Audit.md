# Data Leakage & Feature Separation Audit
**Project:** SIRIAQ (Structure-Sensitive Science) / Ω_ONCO & Ω_BIO
**Status:** VALIDATED

## 1. Absolute Leakage Control Protocol
To ensure strict survival data isolation, the computational pipeline enforces a hard firewall between the feature generation layer ($\Phi \rightarrow \Omega$) and the outcome layer (Survival Time / Event Status).
- **Prohibited Variables:** The $\Omega$ score generation function strictly prohibits the ingestion of `OS_MONTHS`, `PFS_MONTHS`, `vital_status`, or any derivative clinical outcome labels during the training and execution phases.
- **Input Matrix:** $\Omega_{ONCO}$ is derived *exclusively* from the baseline structural tensors (e.g., RNA-Seq expression variance, methylation entropy, Copy Number Alteration burden) captured at Time = 0.

## 2. Formal Feature List
The $\Omega_{ONCO}$ score is a structural composite, calculated via the Information Gap ($\Phi-\Psi-H$) tensor mapping. The physical molecular features constituting $\Phi$ include:
1. **Transcriptomic Variance:** RNA-Seq FPKM (Fragments Per Kilobase Million) cross-gene expression dispersion.
2. **Genomic Instability Index:** Total Fraction of Genome Altered via Copy Number Alterations (CNA).
3. **Epigenetic Entropy:** DNA Methylation Beta-value variance across targeted promoter CpG islands.

## 3. Patient Cohort Separation
- **Development Cohort (TCGA-BRCA):** N = 1075.
- **External Validation Cohort (ICGC-BRCA):** N = 800.
- **Overlap Verification:** Patient submitter IDs, UUIDs, and institutional origins were cryptographically hashed and cross-referenced. **Overlap = 0.**

## 4. Parameter Freeze State
The exact $\beta$ coefficients, hazard ratios, and baseline hazard arrays generated during the TCGA-BRCA development phase have been physically locked. During the ICGC-BRCA external validation, the Cox framework is executed strictly in evaluation mode. Absolutely no parameter tuning, weight adjustment, or gradient descent occurs on the external dataset.
