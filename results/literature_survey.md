# Literature survey: how ECG-denoising studies add NSTDB noise (in progress)

Only studies whose full text was read are classified.
- **A**: uses the 12 published records 118eXX / 119eXX, or makes its records with nst (2-minute on/off protocol) -> the
  per-segment offsets are in its test data.
- **B**: adds the NSTDB noise records (bw / em / ma) itself, as segments scaled by a constant -> no offsets.
- **C**: uses NSTDB noise but does not say how it was added.

Status 2026-11-20: 30 relevant studies, A = 7, B = 18-19, C = 4-5. The full table with the quoted evidence for each
study will be added here with the paper.

| Class | Studies |
|---|---|
| A | Hanzala et al., Sensors 26(22):7098, 2026 (protocol re-run in step 5); Rodrigues & Couto, arXiv 1212.5217, 2012; Arsene, arXiv 1908.10417, 2019; Rana, ResearchGate report, ~2025; Rexy et al., IJATEE 6(50), 2019; Sayadi et al., Physiol Meas 31(10), 2010 (one figure only); Tolentino et al., DLSU Research Congress 2021 |
| B | Brophy et al., IEEE Access 10, 2022; Hossain et al., CMPB 200, 2021; Wang et al., IEEE SMC 2014; Zhu et al., arXiv 2407.11065, 2024; Romero et al., DeepFilter, arXiv 2101.03423; Li et al., DeScoD-ECG, IEEE JBHI 2023; Li et al., TFCDiff, arXiv 2511.16627; Wang & Li, TF-TransUNet1D, arXiv 2508.20398; Romero et al., arXiv 1807.11359; Wang et al., Comput Math Methods Med 2023; IEEE OJEMB 2024 (doi 10.1109/OJEMB.2024.3380352); Ahmed et al., Sensors 25(3):801, 2025; PLoS One 2020 (doi 10.1371/journal.pone.0235330); Abdou & Krishnan, Front Signal Process 2024; Qiu et al., bioRxiv 2020; Sensors 19(7):1617, 2019; Singh et al., arXiv 2202.05177; Chiang et al., IEEE Access 7, 2019; (arXiv 2108.08376, B/C) |
| C | Gao et al., arXiv 2402.00803, 2024; Terada & Toyoura, MMM 2025; Zhu et al., Sensors 25(6):1743, 2025; Li & Laleg-Kirati, arXiv 1908.07758 |
