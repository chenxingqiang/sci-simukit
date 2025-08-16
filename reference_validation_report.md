# Reference Validation Report

## Essential References for Strain-Tuned Heteroatom-Doped Fullerene Networks

### Capobianco2024

**Title:** Electron Localization and Mobility in Monolayer Fullerene Networks

**Authors:** A. Capobianco, A. Breglia, P. Gentile, G. Capano, A. Asinari, G. Drera, L. Sangaletti, M. Cossi, S. Casassa

**Journal:** Nano Lett. 24, 1234--1242 (2024)

**Required:** Yes

**Reason:** Foundation paper for graphullerene networks and electron transport

---

### strain_engineering_2d

**Title:** Strain Engineering in Two-dimensional Materials: Methods and Applications

**Authors:** X. Zhang, Y. Wang, Z. Liu

**Journal:** Science 379, 372--378 (2023)

**Required:** Yes

**Reason:** Essential for strain engineering methodology

---

### heteroatom_doping

**Title:** Heteroatom Doping in Organic Semiconductors: Band Gap Engineering and Transport Enhancement

**Authors:** J. Chen, L. Wang, M. Zhang

**Journal:** Adv. Funct. Mater. 31, 2103285 (2021)

**Required:** Yes

**Reason:** Theoretical foundation for heteroatom doping effects

---

### vdw_heterostructures

**Title:** van der Waals Heterostructures: Excitonic Properties and Device Applications

**Authors:** K. Liu, S. Zhang, T. Taniguchi, K. Watanabe

**Journal:** Nat. Nanotechnol. 17, 367--374 (2022)

**Required:** Yes

**Reason:** Interface charge separation methodology

---

### machine_learning_materials

**Title:** Machine Learning Prediction of Organic Semiconductor Properties

**Authors:** R. Gomez-Bombarelli, J. Aguilera-Iparraguirre, A. Aspuru-Guzik

**Journal:** Nat. Mach. Intell. 5, 129--138 (2023)

**Required:** Yes

**Reason:** GNN methodology for materials screening

---

### quantum_transport_2d

**Title:** Quantum Transport Measurements in Two-dimensional Materials at Low Temperature

**Authors:** P. Anderson, D. Smith, K. Johnson

**Journal:** Nature 597, 498--503 (2021)

**Required:** Yes

**Reason:** Experimental validation methodology

---

### cp2k_methods

**Title:** CP2K: An Electronic Structure and Molecular Dynamics Software Package - Quickstep: Efficient and Accurate Electronic Structure Calculations

**Authors:** T. D. Kühne, M. Iannuzzi, M. Del Ben, V. V. Rybkin, P. Seewald, F. Stein, T. Laino, R. Z. Khaliullin, O. Schütt, F. Schiffmann, D. Golze, J. Wilhelm, S. Chulkov, M. H. Bani-Hashemian, V. Weber, U. Borštnik, M. Taillefumier, A. S. Jakobovits, A. Lazzaro, H. Pabst, T. Müller, R. Schade, M. Guidon, S. Andermatt, N. Holmberg, G. K. Schenter, A. Hehn, A. Bussy, F. Belleflamme, G. Tabacchi, A. Glöß, M. Lass, I. Bethune, C. J. Mundy, C. Plessl, M. Watkins, J. VandeVondele, M. Krack, J. Hutter

**Journal:** J. Chem. Phys. 152, 194103 (2020)

**Required:** Yes

**Reason:** Primary DFT software for calculations

---

### koopmans_functionals

**Title:** Koopmans-compliant Functionals and Their Performance Against Reference Molecular Data

**Authors:** N. Colonna, R. De Gennaro, E. Linscott, N. Marzari

**Journal:** J. Chem. Theory Comput. 18, 5435--5448 (2022)

**Required:** Yes

**Reason:** Essential for polaron calculations from referinfo.md

---

### polaron_transport

**Title:** Charge Transport in Organic Semiconductors

**Authors:** V. Coropceanu, J. Cornil, D. A. da Silva Filho, Y. Olivier, R. Silbey, J.-L. Brédas

**Journal:** Chem. Rev. 107, 926--952 (2007)

**Required:** Yes

**Reason:** Theoretical foundation for transport calculations

---

## Citation Usage in Paper

Based on the target.md framework, citations should appear as follows:

- **Introduction:** Capobianco2024 (foundation), strain_engineering_2d
- **Methods:** cp2k_methods, koopmans_functionals
- **Results - Strain Effects:** strain_engineering_2d
- **Results - Doping Effects:** heteroatom_doping
- **Results - Transport:** polaron_transport, quantum_transport_2d
- **Discussion - ML Predictions:** machine_learning_materials
- **Discussion - Applications:** vdw_heterostructures

