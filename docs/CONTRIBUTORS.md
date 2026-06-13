# Contributors & Acknowledgments

The SIRIAQ (Özbil Score / Fisher-Coherence) framework is the result of a cross-disciplinary collaboration between theoretical physics and software engineering.

## Principal Architects

### Halil Özbil
**Principal Theoretical Architect**
- Authored the foundational theoretical papers (*The Cherenkov Fisher Formula*, *LGC Geometric Information Loss Law*, *Özbil Score V2.1*).
- Developed the core mathematical framework linking Fisher Information, Cramér-Rao Lower Bound expansion, and geometric consistency loss.
- Formulated the Özbil Score ($\Omega$) as a continuous state functional for structural integrity.
- Provided rigorous scientific steering and independent verification protocols for the Quad-Domain Proof.

### Noam Cohen
**Principal Software Architect & Lead Engineer**
- Engineered the SIRIAQ multi-domain implementation and the HarpiaOS / Quantum Core Zero environment.
- Invented the **Domain-Adaptive Structural Normalization (DASN)** protocol, allowing the theoretical math to interface with real-world, noisy sensor data across varied physical domains.
- Developed the data processing pipelines, 3D WebGL visualization engine, and the comprehensive test suites for C-MAPSS, IMS Bearing, NASA Battery, and ADNI validation.
- Executed the empirical data-science modeling that established the Quad-Domain lead-time advantages.

## Institutional Datasets
We acknowledge the invaluable open datasets that made the empirical validation of this theory possible:
- **NASA Prognostics Center of Excellence (PCoE):** C-MAPSS Jet Engine and Battery Aging datasets.
- **University of Cincinnati:** IMS Bearing Dataset.
- **FEMTO-ST Institute:** PRONOSTIA Bearing Dataset.
- **ADNI (Alzheimer's Disease Neuroimaging Initiative):** For the longitudinal clinical benchmarks guiding the biological hypothesis.

---
*Note: The theoretical principles outlined in `SCIENTIFIC_FOUNDATION.md` and `WHITEPAPER.md` are documented for public scientific review. The specific codebase implementation, DASN logic, and real-time visualization engine (HarpiaOS) remain proprietary.*
