# Literature survey: how ECG-denoising studies add NSTDB noise

Searches between 16 and 20 November 2026 (web, arXiv, Europe PMC; terms: noise stress test, NSTDB, nst, 118e, 119e,
electrode motion, combined with denoising), plus the references of the studies found and the 100 works that PhysioNet
lists as citing the NSTDB (41 denoising candidates; 22 full texts not available to us). A study is classified only
from its full text, from the sentences that say how the noise was added.

- **A**: builds its test data with nst (2-minute on/off protocol) or uses the 12 published records 118eXX / 119eXX ->
  the per-segment offsets are in its test data.
- **B**: adds the NSTDB noise records (bw / em / ma) itself, continuously or as segments scaled by a constant -> no
  offsets.
- **C**: uses NSTDB noise but does not say how it was added.

58 documents read in full; 13 excluded (10 used no NSTDB noise, 2 did not score denoising, 1 was a course report).
**45 studies classified: A = 7, B = 32, B or C = 1, C = 5** (table 2 of the paper).

| Class | n | Studies |
|---|---|---|
| A: nst-made test data | 3 | Rodrigues & Couto, arXiv 1212.5217 (2012); Arsene, arXiv 1908.10417 (2019); Tolentino, Cordel & Pobre, Proc. DLSU Research Congress 2021, HCT-10 |
| A: published records | 2 | Rexy, Velmani & Rajakumar, IJATEE 6:12-24 (2019); Hanzala et al., Sensors 26:7098 (2026) (protocol re-run in step 5) |
| A: one figure only | 2 | Sayadi, Shamsollahi & Clifford, Physiol. Meas. 31:1309-29 (2010); Akhbari et al., Physiol. Meas. 37:203-26 (2016) (shows 118e06 and 118e12, calls 118e12 a 12 dB record) |
| B | 32 | Brophy et al., IEEE Access 10 (2022); Hossain et al., CMPB 200 (2021); Wang et al., IEEE SMC 2014; Zhu, Chhabra & Khalili, arXiv 2407.11065 (2024); Chiang et al., IEEE Access 7 (2019); Huang, Hu & Sun, Sensors 19:1617 (2019); Qiu et al., bioRxiv 2020.03.27.012831; Zhang & Wei, PLoS One 15:e0235330 (2020); Romero et al., arXiv 1807.11359 (2018); Romero, Piñol & Vázquez-Seisdedos, BSPC 70:102992 (2021); Singh, Sharma & Maiya, arXiv 2202.05177 (2022); Wang et al., CMMM 2023:6737102; Li et al., IEEE JBHI 28:5081-91 (2024); Atanasoski et al., IEEE OJEMB 5:296-305 (2024); Abdou & Krishnan, Front. Signal Process. 4:1396077 (2024); Shaheen et al., Sensors 25:801 (2025); Li et al., arXiv 2511.16627 (2025); Wang & Li, arXiv 2508.20398 (2025); Sameni et al., IEEE TBME 54:2172-85 (2007); Wang et al., Cybern. Inf. Technol. 16:60-8 (2016); Gowri & Rajesh Kumar, IJISA 8:41-9 (2016); El B'charri et al., Biomed. Eng. Online 16:26 (2017); Xiong et al., Physiol. Meas. 37:2214-30 (2016); Chen et al., BSPC 62:102060 (2020); Khiter et al., Trait. Signal 37:263-9 (2020); Ouali et al., Trait. Signal 37:541-53 (2020); Uddin et al., PeerJ Comput. Sci. 9:e1189 (2023); Rifai et al., ICIMCIS 2025; Spinazzola et al., ISCAS 2025; Hatun & Vatansever, DEU FMD 28:135-47 (2026); Sraitih et al., Research Square 2026; Tran, Research Square 2026 |
| B or C | 1 | Dai & Bai, arXiv 2108.08376 (2021) |
| C | 5 | Bagheri, Ghafarnia & Bahrami, ETASR 3:345-8 (2013); Li & Laleg-Kirati, arXiv 1908.07758 (2019); Gao, Gisolfi & Dubrawski, arXiv 2402.00803 (2024); Terada & Toyoura, MMM 2025, LNCS 15523:311-24; Zhu et al., Sensors 25:1743 (2025) |

The quoted evidence for each study is kept with the authors' working notes and is available on request.
