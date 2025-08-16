Supplementary Information for: Electron
Localization and Mobility in Monolayer
Fullerene Networks
Amedeo Capobianco,† Julia Wiktor,‡ Alessandro Landi,∗,† Francesco
Ambrosio,∗,¶,† and Andrea Peluso†
†Dipartimento di Chimica e Biologia Adolfo Zambelli, Università di Salerno, Via Giovanni
Paolo II, I-84084 Fisciano (SA), Italy
‡Department of Physics, Chalmers University of Technology, SE-412 96 Gothenburg,
Sweden
¶Dipartimento di Scienze, Università degli Studi della Basilicata, Viale dell’Ateneo
Lucano, 10 - 85100 Potenza, Italy
E-mail: alelandi1@unisa.it; francesco.ambrosio@unibas.it
Computational Details: Electronic Structure Calculations on Periodic Supercells
Construction of Koopman’s compliant functional
The supercells employed to determine polaron binding energies are depicted in Figure S1 along with the lattice constants. We model vdW C60 by constructing a 2×2×2 cubic supercell with a=28.52 Å corresponding to the experimental crystal structure at room temperature,1 and including 32 C60 molecules. For qHP C60, we consider the experimental structure of qHP Mg4C60 provided in Ref. 2, from which we extract a monolayer of the fullerene network, and build a periodic 2D supercell with a =36.6748 Å and b =30.84293 Å containing 16 C60
molecules.
Electronic structure calculations on these supercells are performed using the freely available CP2K-QUICKSTEP package,3 which combines atomic basis sets with an auxiliary plane-wave basis set to re-expand the electron density. In particular, we use the MOLOPT double-zeta polarized basis set and a cutoff of 800 Ry for the plane waves. Core electrons are treated with the analytical Goedecker-Teter-Hutter pseudopotentials.4 Furthermore, we employ the auxiliary density matrix method, as implemented in CP2K, with the cFIT aux-
iliary basis set,5,6 to speed up the calculation of exchange integrals in hybrid functional
calculations.5,6
To estimate the fraction of Fock exchange, αK, to be incorporated in the PBE(αK) functional for the fulfillment of the generalized Koopmans’ condition, we employ the probe method, formalized in Ref. 7. This method is based on the fact that, in exact DFT, the Kohn-Sham energy level associated with a localized state within the band gap of a material does not vary upon change of occupation. Therefore, we insert a single fluorine atom in the vdW C60 supercell, thus introducing a localized state in the band gap of the organic semiconductor, cf. Figure S2 (a). Then, we calculate the single-particle energy level for both the neutral ϵ(F0) and negatively charged ϵ(F−) states at the PBE(α) level, considering three
 
Figure S1: Stick&ball representation of the supercells employed to study vdW and qHP C60. different values of α. Hence, in exact DFT the following equivalence holds:
	 ,	(S1)
where ϵ−corr is a correction term which accounts for the electrostatic finite-size error, arising from periodic boundary conditions in supercell calculations with localized charges.8 We employ the correction term derived in Ref. 9 for Kohn-Sham levels, which is connected with the Freysoldt-Neugebauer-Van de Walle (FNV) scheme commonly employed for total
energies:8,10
	ϵ−corr = 2Ecorr−	(S2)
The FNV correction term Ecorr− includes two contributions: (i) the Madelung energy, accounting for the monopole charge subject to periodic boundary conditions and (ii) an alignmentlike term due to the finite extent of the charge distribution. The latter alignment term is calculated from the shift of the C 2s in a region far from the charged defect. The former depends on the dielectric response of the material, which is here taken into account using the high-frequency dielectric constant of vdW C60 crystal, ε∞, as calculations are performed without relaxing the positions of the nuclei.
Two limit values of ε∞ are reported in the literature: 3.611 and 4.0812, which would entail a difference in calculated ϵ−corr of 0.04 eV, cf. Table S1. This, in turn, would translate into a slightly different intersection between the linear evolution of the energy levels for occupied and empty states, corresponding to 20.9% < αK < 21.4% as highlighted by the shaded window in Figure S2 (b). To test the dielectric properties achieved with hybridDFT calculations are consistent with the experimental characterization, we here estimate ε∞, combining DFT calculations with a formulation of the polarization based on a discrete Berry phase.13 In particular, we perform PBE0 calculations14,15 in the presence of a finite electric field E of 0.0001 a.u. applied along the a axis, at fixed nuclear coordinates. ε∞ for the cubic vdW C60 is hence defined as:13
	 	(S3)
where P E and P ′ are the values of the polarization along the a axis with and without applied electric field, respectively. We here achieve ε∞ = 3.80, an estimate within the experimental range.
Table S1: Calculated values of ϵ−corr (eV) and αK (%) for vdW C60 at different experimental and calculated values of ε∞.
	ε∞	ϵ−corr	αK
Expt. (Ref. 11)	3.60	0.390	20.78
Expt. (Ref. 12)	4.08	0.350	21.29
Calc. (PBE0)	3.80	0.375	21.00
Then, we test the performance of the constructed hybrid functional in the simulation of the structural properties of vdW C60. To this end, we consider, as a reference, the lowtemperature experimental crystal structure of the solid (cf. Table S2).16 Then, we perform cell optimizations on a 2×2×2 supercell in which the lattice parameters are allowed to relax within the imposed cubic symmetry. To enable for a comprehensive comparison of the individual factors influencing the result, we carry out these calculations with (i) the semi-local
 
Figure S2: (a) Stick&ball representation of the fluorine probe (yellow, enlarged) inserted in a periodic supercell of crystalline vdW C60 (side view, 110 direction) along with the isodensity representation of the corresponding highest occupied molecular orbital, showing localization on the 2s of fluorine. (b) Single-particle energy levels of the interstitial fluorine as a function of the fraction of Fock exchange α used in the PBE(α) functional. Energies are referred to the average electrostatic potential. The solid lines delimit the shaded area representing values achieved employing the limit experimental values of ε∞, while the dashed line is obtained using the calculated value.
PBE functional,17 (ii) the rVV10 functional which includes non-local electron correlation within the scheme proposed by Vydrov and Voorhis. The b parameter of rV110 governing the extent of vdW interactions is fixed at its original value, b = 6.3 (rVV10-b6.3),18,19(iii) the constructed PBE(αK) functional, and (iV) PBE(αK)+rVV10-b6.3 functional accounting for both Fock exchange and vdW interactions. As expected, the PBE functional yields a significant underestimation of the material’s density, a consequence of the lack of vdW interactions in this method. In stark contrast, the rVV10-b6.3 functional is found to guarantee a more reliable description of the weak interactions within the molecular solid, as it provides a value of a with an error below 0.05%, with respect to the experiment. When switching to the hybrid PBE(αK) functional, the accord with the experiment is only slightly improved with respect to PBE, still being very unsatisfactory (error above 5%). In contrast, when combining the hybrid functional with the original rVV10-b6.3 formulation, the lattice parameter is found to be underestimated by ≈0.1 Å. We note that the optimal b parameter when rVV10 is used in conjunction with hybrid functionals is known to be different than that pertinent to the semi-local counterpart, see Ref. 20. We here find that using a value of b = 7.8 allows us to retrieve a remarkable agreement with the experimental structure.
Table S2: Experimental and Calculated values of a (Å) and Ec (eV).
 
 
	PBE(αK)	14.782
	PBE(αK)+rVV10-b6.3	13.960	2.4
	PBE(αK)+rVV10-b7.8	14.073	2.1
 
To further corroborate the validity of our computational approach, for both the rVV10 and the PBE(αK)+rVV10 functionals, we calculate the cohesive energy of the crystal defined
as:
	Ec = Esc/N − Emol,	(S4)
where Esc is the total energy of the supercell with relaxed lattice parameters and nuclei positions, N is the total number of molecules in the model, Emol is the total energy of the isolated C60, corrected via the counterpoise method for the basis-set superimposition error,22 which is found to be ≈ 0.1 eV for the employed basis set. To compare the calculated Ec with an experimental reference, we estimate it by subtracting 2RT from the experimental sublimation enthalpy23 from Ref. 21. This procedure provides Ec=2.1 eV. For both the rVV10 and the PBE(αK)+rVV10b6.3, we calculate Ec =2.4 eV, a value 0.3 eV above the experimental one. When the PBE(αK)+rVV10-b7.8 is employed, we obtain a value of 2.1 eV, in perfect agreement with that extrapolated from thermogravimetry measurements.21 The PBE(αK)+rVV10-b7.8 functional is then used to produce the results presented in the main text as it simultaneously ensures a reliable description of structural and energetic features, while neutralizing the self-interaction error affecting electronic properties in DFT.
Gas-phase ionization potential and electron affinity of C60
In Table S3, we report the calculated gas-phase adiabatic ionization potential and electron affinity for C60. The values are found to be in fair agreement with average experimental estimates reported in Ref. 24.
Table S3: Experimental and calculated adiabatic ionization potentials and electron affinities of gas-phase C60. Calculations are performed at the PBE(αK)+rVV10-b7.8 level of theory,
	Theory	Experiment
AIP	7.78	7.624
AEA	2.43	2.524
Calculation of the band gap at room temperature
The band gap at room temperature Eg(T) is defined as:
	Eg(T) = Eg(0) + ∆Eg(T),	(S5)
where Eg(0) is the band gap calculated for the ordered room-temperature crystal, while ∆Eg(T) is the thermal renormalization, which is often relevant in organic semiconductors.25–27 To calculate ∆Eg(T), molecular dynamics simulations at 300 K are carried out for vdW and qHP C60 periodic supercells with CP2K. The sampling of the NVT ensem-
ble is controlled by a by a Nosé-Hoover thermostat,28,29 and the time-step is set to 1 fs.
Production runs of 5 ps are preceded by an equilibration run of 2 ps. MD simulations are
performed employing the rVV10-b6.3 functional.18,19 We employ smaller supercells to alleviate the computational burden: for vdW C60, we employ a cubic supercell with a = 12.26 Å. For qHP, a cell with a = 15.805, b = 18.256 Å is chosen. Both supercells include four
fullerene molecules.
Table S4: Calculated values of ∆Eg(T), ∆EV(T), and ∆EC(T) at the rVV10-b6.3 and PBE(αK)+rVV10-b7.8 (eV) levels of theory.
vdW	∆Eg(T)	∆EV(T)	∆EC(T)
αK)+rVV10-b7.8	 0.16	0.03	0.13
			
rVV10-b6.3	0.10	0.03	0.07
PBE(αK)+rVV10-b7.8	0.13	0.04	0.11
The electronic structure is then re-evaluated at the PBE(αK)+rVV10-b7.8 level on a sample of structural configurations to verify the effect of the hybrid functional on ∆Eg(T). We note that ∆Eg(T) can be split into the contributions provided by the renormalization of the band edges:
	∆EV(T) = EV(T) − EV(0),	(S6)
and
	∆EC(T) = EC(0) − EC(T),	(S7)
where EV(T) and EC(T) are the valence and conduction band edges calculated for the disordered room-temperature structure, while EV(0) and EC(0) those calculated on the ordered crystallographic structure at the same temperature.27 Estimated values of ∆Eg(T), ∆EV(T), and ∆EC(T) are reported in Table S4.
Band alignment at the interface between vdW/qHP C60 and vacuum
To align the band edges of the fullerene-based semiconductors with respect to the vacuum level, we perform slab calculations including a vacuum layer of at least 30 Å. Then, to refer the band edges to the vacuum level, we calculate the plane-averaged electrostatic potential across the z direction, e.g. Figure S4 for vdW C60.
 
Figure S3: Representation of the employed slab for vdW C60 and calculated plane-averaged electrostatic potential.
Inverse participation ratio of the polaron vs fully localized/delocalized states
A quantitative assessment of the localization extent is yielded by the inverse participation ratio, defined for an orbital ψ as:
	IPR = 	(S8)
where N is the number of volume elements in the supercell. For each material, the calculated value for the polaron is compared with the limit values represented by HOMO of the negatively charged supercell upon injection (full delocalization) and the HOMO of isolated C−60 anion in a supercell of identical size (molecular localization). The calculated values of IPR are reported in Table S5.
Table S5: Calculated values of IPR for HOMO of the negatively charged supercell upon injection, IPRdeloc, the HOMO of isolated C−60 anion in a supercell of identical size, IPRmol, and the HOMO associated with with the charged supercell upon polaron formation, IPRpol.
	IPRdeloc	IPRmol	IPRpol
vdW	5	231	34
	IPRdeloc	IPRmol	IPRpol
qHP	3	210	30
Calculations of the band structure
Band structure calculations within vasp employ the projector augmented wave method. The plane wave cutoff is set to 450 eV. The Brillouin zone is sampled using a 6×6×6 grid. The geometry was first fully relaxed using the van-der-Waals-density functional with consistent exchange (vdW-DF-cx) method30 This resulted in lattice parameters of a = 15.805, and b = 9.128 Å. On top of this geometry, we calculate the band structure using the PBE(αK)+rVV10 functional, consistent with the one employed within the CP2K code. We obtain values of band gap, IP and EA (after renormalization due to thermal motion) equal to 1.75, 5.92, and
4.17 eV in good accord with the supercell calculations.
Isodensity representation of the valence and conduction band edges and electronic density of states for vdW C60
 
Figure S4: Isodensity representation of the valence band maximum and the conduction band minimum of vdW C60. Total and projected electronic density of states of the valence (purple) and conduction band edges (teal) of vdW C60.
Computational Details: Computational Modelling of the Franck-Condon Weighted Density of States
All the electronic calculations needed for the modeling of FCWD and of the electronic coupling are performed with the Gaussian 16 program31. In particular, DFT calculations at the B3LYP-D3/6-31G(d) level of theory31 are carried out for geometry optimizations and normal modes analysis. Time-dependent DFT calculations at the same level of theory are used to estimate the energy of excited states (vide infra).
Electronic coupling
For a simple two-state system, the energy difference between the adiabatic ground (E0) and first excited state (E1) is related to the diabatic potential energies Ei and Ef by:32
	 	(S9)
Specifically, for symmetric systems, Ei = Ef; in this case, the first adiabatic excitation energy, reads as follows:
	2Jfi = E1 − E0	(S10)
Therefore, the coupling term between two fullerene molecule is simply half of the energy difference between the ground electronic state of the anion dimer and the first excited state, i.e.32:
 (dimer)  (dimer)
	J =  	(S11)
2
These energies have been estimated from time-dependent DFT calculations on anionic dimers with inter-fullerene distances fixed to those occurring in the materials.
Franck-Condon Weighted Density of States
The Franck-Condon weighted density of states (FCWD), equation 6 in the main text, which we reproduce for convenience,
	 	(S12)
can be evaluated through the generating function (GF) approach33,34. In the framework of harmonic approximation for nuclear motion, the GF approach allows to compute F(∆Efi,T) considering the whole set of the molecular normal modes of both initial and final states. We take into account the effects due to both changes of the equilibrium positions and of vibrational frequencies, as well as the effects due to normal mode mixing. Furthermore, this technique allows to handle the infinite summations appearing in Eq. S12, by exploiting the integral representation of Dirac’s delta function and Duschinsky’s normal mode transforma-
tion:35
	Qf = JQi + K	(S13)
where J and K are the rotation matrix and the equilibrium displacement vector, respectively, while Qi and Qf are the normal coordinates of the initial and final electronic states,
respectively.
The FCWDs are here calculated using a development version of the MolFC package,36 in which the GF approach is implemented. We pinpoint that we use the curvilinear coordinate representation of normal modes, to prevent that large displacements of an angular coordinate could lead to large shifts from the equilibrium positions of the involved bond distances. Such an unphysical effect, unavoidable when using rectilinear coordinates, requires the use of high-
order anharmonic potentials for its correction.37,38 The employed methodology is found to nicely reproduce the experimental photoelectron spectrum of C , see Figure S5, thus making us confident of its use for predicting charge transfer rates.
In this regard, we note that, when using Equation 5 of the main text to calculate the electron hopping rate, an average of the calculate FCWD over about 400 cm−1 around F(∆Efi = 0,T) has been performed as a practical way to account for thermal energy.40
 
Figure S5: Experimental (red full line) and computed (blue dashed line) photoelectron spectrum of C−60 at T = 300 K. The experimental spectrum has been digitized from Ref. 39.
References
(1)	Dorset, D. L.; McCourt, M. P. Disorder and the Molecular Packing of C60 Buckminsterfullerene: A Direct Electron-Crystallographic Analysis. Acta Crystallogr. A 1994, 50, 344–351.
(2)	Hou, L.; Cui, X.; Guan, B.; Wang, S.; Li, R.; Liu, Y.; Zhu, D.; Zheng, J. Synthesis of a Monolayer Fullerene Network. Nature 2022, 606, 507–510.
(3)	VandeVondele, J.; Krack, M.; Mohamed, F.; Parrinello, M.; Chassaing, T.; Hutter, J. Quickstep: Fast and Accurate Density Functional Calculations Using a Mixed Gaussian and Plane Waves Approach. Comput. Phys. Commun. 2005, 167, 103 – 128.
(4)	Hartwigsen, C.; Goedecker, S.; Hutter, J. Relativistic Separable Dual-Space Gaussian Pseudopotentials from H to Rn. Phys. Rev. B 1998, 58, 3641–3662.
(5)	Guidon, M.; Schiffmann, F.; Hutter, J.; VandeVondele, J. Ab Initio Molecular Dynamics Using Hybrid Density Functionals. J. Chem. Phys. 2008, 128, 214104.
(6)	Guidon, M.; Hutter, J.; VandeVondele, J. Auxiliary Density Matrix Methods for Hartree-Fock Exchange Calculations. J. Chem. Theory Comput. 2010, 6, 2348–2364.
(7)	Bischoff, T.; Reshetnyak, I.; Pasquarello, A. Adjustable Potential Probes for Band-Gap Predictions of Extended Systems through Nonempirical Hybrid Functionals. Phys. Rev. B 2019, 99, 201114.
(8)	Freysoldt, C.; Neugebauer, J.; Van de Walle, C. G. Fully Ab Initio Finite-Size Corrections for Charged-Defect Supercell Calculations. Phys. Rev. Lett. 2009, 102, 016402.
(9)	Chen, W.; Pasquarello, A. Correspondence of Defect Energy Levels in Hybrid Density Functional Theory and Many-Body Perturbation Theory. Phys. Rev. B 2013, 88,
115104.
(10)	Komsa, H.-P.; Rantala, T. T.; Pasquarello, A. Finite-Size Supercell Correction Schemes for Charged Defect Calculations. Phys. Rev. B 2012, 86, 045112.
(11)	Eklund, P.; Rao, A.; Wang, Y.; Zhou, P.; Wang, K.-A.; Holden, J.; Dresselhaus, M.; Dresselhaus, G. Optical properties of C60- and C70-Based Solid Films. Thin solid films 1995, 257, 211–232.
(12)	Ren, S.; Wang, Y.; Rao, A.; McRae, E.; Holden, J.; Hager, T.; Wang, K.; Lee, W.-T.;
Ni, H.; Selegue, J.; others Ellipsometric Determination of the Optical Constants of C60 (Buckminsterfullerene) films. Appl. Phys. Lett. 1991, 59, 2678–2680.
(13)	Umari, P.; Pasquarello, A. Ab initio Molecular Dynamics in a Finite Homogeneous
Electric Field. Phys. Rev. Lett. 2002, 89, 157602.
(14)	Perdew, J. P.; Ernzerhof, M.; Burke, K. Rationale for Mixing Exact Exchange with
Density Functional Approximations. J. Chem. Phys. 1996, 105, 9982–9985.
(15)	Adamo, C.; Barone, V. Toward Reliable Density Functional Methods without Adjustable Parameters: The PBE0 Model. J. Chem. Phys. 1999, 110, 6158–6170.
(16)	David, W. I.; Ibberson, R. M.; Matthewman, J. C.; Prassides, K.; Dennis, T. J. S.;
Hare, J. P.; Kroto, H. W.; Taylor, R.; Walton, D. R. Crystal Structure and Bonding of Ordered C60. Nature 1991, 353, 147–149.
(17)	Perdew, J. P.; Burke, K.; Ernzerhof, M. Generalized Gradient Approximation Made
Simple. Phys. Rev. Lett. 1996, 77, 3865.
(18)	Vydrov, O. A.; Van Voorhis, T. Nonlocal van der Waals Density Functional: The
Simpler the Better. J. Chem. Phys. 2010, 133, 244103.
(19)	Sabatini, R.; Gorni, T.; de Gironcoli, S. Nonlocal van der Waals Density Functional
Made Simple and Efficient. Phys. Rev. B 2013, 87, 041108.
(20)	Ambrosio, F.; Miceli, G.; Pasquarello, A. Structural, Dynamical, and Electronic Properties of Liquid Water: A Hybrid Functional Study. J. Phys. Chem. B 2016, 120, 7456–7470.
(21)	Martínez-Herrera, M.; Campos, M.; Torres, L. A.; Rojas, A. Enthalpies of Sublimation of Fullerenes by Thermogravimetry. Thermochim. Acta 2015, 622, 72–81.
(22)	Boys, S. F.; Bernardi, F. The Calculation of Small Molecular Interactions by the Differences of Separate Total Energies. Some Procedures with Reduced Errors. Mol. Phys. 1970, 19, 553–566.
(23)	Cutini, M.; Civalleri, B.; Corno, M.; Orlando, R.; Brandenburg, J. G.; Maschio, L.; Ugliengo, P. Assessment of Different Quantum Mechanical Methods for the Prediction of Structure and Cohesive Energy of Molecular Crystals. J. Chem. Theory Comput. 2016, 12, 3340–3352.
(24)	Schwenn, P. E.; Burn, P. L.; Powell, B. J. Calculation of solid state molecular ionisation energies and electron affinities for organic semiconductors. Org. Electron. 2011, 12, 394–403.
(25)	Brown-Altvater, F.; Antonius, G.; Rangel, T.; Giantomassi, M.; Draxl, C.; Gonze, X.;
Louie, S. G.; Neaton, J. B. Band Gap Renormalization, Carrier Mobilities, and the Electron-Phonon Self-Energy in Crystalline Naphthalene. Phys. Rev. B 2020, 101, 165102.
(26)	Rangel, T.; Berland, K.; Sharifzadeh, S.; Brown-Altvater, F.; Lee, K.; Hyldgaard, P.; Kronik, L.; Neaton, J. B. Structural and Excited-State Properties of Oligoacene Crystals from First Principles. Phys. Rev. B 2016, 93, 115206.
(27)	Ambrosio, F.; Wiktor, J.; Landi, A.; Peluso, A. Charge Localization in Acene Crystals from Ab Initio Electronic Structure. J. Phys. Chem. Lett. 2023, 14, 3343–3351.
(28)	Nosé, S. A Unified Formulation of the Constant Temperature Molecular Dynamics
Methods. J. Chem. Phys. 1984, 81, 511–519.
(29)	Hoover, W. G. Canonical Dynamics: Equilibrium Phase-Space Distributions. Phys. Rev. A 1985, 31, 1695–1697.
(30)	Berland, K.; Hyldgaard, P. Exchange Functional That Tests the Robustness of the
Plasmon Description of the Van Der Waals Density Functional. Phys. Rev. B 2014, 89, 035412.
(31)	Frisch, M. J. et al. Gaussian 16 Revision C.01. 2016; Gaussian Inc. Wallingford CT.
(32)	Manna, D.; Blumberger, J.; Martin, J. M. L.; Kronik, L. Prediction of Electronic Couplings for Molecular Charge Transfer Using Optimally Tuned Range-Separated Hybrid Functionals. Mol. Phys. 2018, 116, 2497–2505.
(33)	Kubo, R.; Toyozawa, Y. Application of the Method of Generating Function to Radiative and Non-Radiative Transitions of a Trapped Electron in a Crystal. Prog. Theor. Phys.
1955, 13, 160–182.
(34)	Lax, M. The Franck-Condon Principle and Its Application to Crystals. J. Chem. Phys. 1952, 20, 1752–1760.
(35)	Borrelli, R.; Peluso, A. Elementary Electron Transfer Reactions: From Basic Concepts to Recent Computational Advances. WIREs: Comput. Mol. Sci. 2013, 3, 542–559.
(36)	Borrelli, R.; Peluso, A. MolFC: A Program for Franck-Condon Integrals Calculation. https://github.com/rborrelli/molfc, accessed January 2024.
(37)	Borrelli, R.; Di Donato, M.; Peluso, A. Role of Intramolecular Vibrations in Long-range Electron Transfer between Pheophytin and Ubiquinone in Bacterial Photosynthetic
Reaction Centers. Biophys. J. 2005, 89, 830–841.
(38)	Peluso, A.; Borrelli, R.; Capobianco, A. Correction to “Photoelectron Spectrum of
Ammonia, a Test Case for the Calculation of Franck-Condon Factors in Molecules Undergoing Large Geometrical Displacements upon Photoionization”. J. Phys. Chem. A 2013, 117, 10985–10985.
(39)	Wang, X.-B.; Woo, H.-K.; Wang, L.-S. Vibrational cooling in a cold ion trap: Vibrationally resolved photoelectron spectroscopy of cold C60- anions. J. Chem. Phys. 2005, 123.
(40)	Landi, A.; Borrelli, R.; Capobianco, A.; Velardo, A.; Peluso, A. Second-Order Cumulant Approach for the Evaluation of Anisotropic Hole Mobility in Organic Semiconductors. J. Phys. Chem. C 2018, 122, 25849–25857.
