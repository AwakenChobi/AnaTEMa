#REMEMBER! If i=0, m/q = 2
hydrogen = [0] * 50
hydrogen[0] = 1           # m/z=2 (H₂⁺)

deuterium = [0] * 50
deuterium[0] = 0.0159     # m/z=2 (D₂⁺)
deuterium[1] = 1          # m/z=3 (D⁺)

methane = [0] * 50
methane[10] = 0.038004    # m/z=12 
methane[11] = 0.106911    # m/z=13
methane[12] = 0.24220     # m/z=14 (CH₂⁺)
methane[13] = 0.88799     # m/z=15 (CH₃⁺)
methane[14] = 1.00000     # m/z=16 (CH₄⁺ **main peak**)
methane[15] = 0.0164      # m/z=17

ammonia = [0.00000] * 50
ammonia[12] = 0.022002    # m/z=14 (NH₂⁺ fragment)
ammonia[13] = 0.0751075   # m/z=15 (NH₂⁺)
ammonia[14] = 0.80842     # m/z=16 (NH₃⁺)
ammonia[15] = 1.00000     # m/z=17 (NH₄⁺, main peak)
ammonia[16] = 0.00400     # m/z=18

water = [0] * 50
water[14] = 0.0090009    # m/z=16
water[15] = 0.212221     # m/z=17
water[16] = 1.00000      # m/z=18 (H₂O⁺, main peak)
water[17] = 0.0050005    # m/z=19
water[18] = 0.003003     # m/z=20

acetilene = [0] * 50
acetilene[10] = 0.0070007# m/z=12
acetilene[11] = 0.0032003# m/z=13
acetilene[12] = 0.001    # m/z=14
acetilene[22] = 0.050005 # m/z=24
acetilene[23] = 0.1912191# m/z=25
acetilene[24] = 1.00000  # m/z=26
acetilene[25] = 0.0022002# m/z=27
acetilene[26] = 0.001    # m/z=28

hydrogen_cyanide = [0] * 50
hydrogen_cyanide[10] = 0.04200   # m/z=12
hydrogen_cyanide[11] = 0.0170016 # m/z=13
hydrogen_cyanide[12] = 0.0170016 # m/z=14
hydrogen_cyanide[13] = 0.0010000 # m/z=15
hydrogen_cyanide[24] = 0.1682168 # m/z=26
hydrogen_cyanide[25] = 1.0000000 # m/z=27
hydrogen_cyanide[26] = 0.0170017 # m/z=28
hydrogen_cyanide[27] = 0.0010001 # m/z=29

carbon_monoxide = [0] * 50
carbon_monoxide[10] = 0.04700470 # m/z=12
carbon_monoxide[14] = 0.01700170 # m/z=16
carbon_monoxide[26] = 1.00000000 # m/z=28
carbon_monoxide[27] = 0.01200120 # m/z=29

nitrogen = [0] * 50
nitrogen[12] = 0.1379137 # m/z=14
nitrogen[26] = 1.0000000 # m/z=28
nitrogen[27] = 0.0074007 # m/z=29

ethylene = [0] * 50
ethylene[0] = 0.0010001   # m/z=2
ethylene[10] = 0.0050005 # m/z=12
ethylene[11] = 0.0090009 # m/z=13
ethylene[12] = 0.0210021 # m/z=14
ethylene[13] = 0.0030003 # m/z=15
ethylene[22] = 0.0230023 # m/z=24
ethylene[23] = 0.0781078 # m/z=25
ethylene[24] = 0.5295530 # m/z=26
ethylene[25] = 0.6236624 # m/z=27
ethylene[26] = 1.0000000 # m/z=28 (C₂H₄⁺, main peak)
ethylene[27] = 0.0230023 # m/z=29

diborane = [0] * 50
diborane[8] = 0.0631063  # m/z=10
diborane[9] = 0.2843284  # m/z=11
diborane[10] = 0.1812181 # m/z=12
diborane[11] = 0.2442244 # m/z=13
diborane[12] = 0.0070007 # m/z=14
diborane[13] = 0.0010001 # m/z=15
diborane[19] = 0.0190019 # m/z=21
diborane[20] = 0.1121112 # m/z=22
diborane[21] = 0.4574457 # m/z=23
diborane[22] = 0.8968897 # m/z=24
diborane[23] = 0.5675568 # m/z=25 (B₂H₅⁺, fragment)
diborane[24] = 1.0000000 # m/z=26 (B₂H₆⁺, main peak)
diborane[25] = 0.9749975 # m/z=27
diborane[26] = 0.0030003 # m/z=28

nitric_oxide = [0] * 50
nitric_oxide[12] = 0.0751075  # m/z=14
nitric_oxide[13] = 0.0240024  # m/z=15
nitric_oxide[14] = 0.0150015  # m/z=16
nitric_oxide[28] = 1.0000000  # m/z=30 (NO⁺, main peak)
nitric_oxide[29] = 0.0040004  # m/z=31
nitric_oxide[30] = 0.0020002  # m/z=32

formaldehyde = [0] * 50
formaldehyde[10] = 0.010001  # m/z=12
formaldehyde[11] = 0.010001  # m/z=13
formaldehyde[12] = 0.010001  # m/z=14
formaldehyde[13] = 0.020002  # m/z=15
formaldehyde[26] = 0.240024  # m/z=28
formaldehyde[27] = 1.000000  # m/z=29 (HCHO⁺, main peak)
formaldehyde[28] = 0.580058  # m/z=30
formaldehyde[29] = 0.005001  # m/z=31

ethane = [0] * 50
ethane[0] = 0.0020002  # m/z=2
ethane[10] = 0.004004  # m/z=12
ethane[11] = 0.010001  # m/z=13
ethane[12] = 0.030003  # m/z=14
ethane[13] = 0.044004  # m/z=15
ethane[14] = 0.001000  # m/z=16
ethane[22] = 0.050005  # m/z=24
ethane[23] = 0.035003  # m/z=25
ethane[24] = 0.232223  # m/z=26
ethane[25] = 0.332332  # m/z=27
ethane[26] = 1.000000  # m/z=28 (C₂H₆⁺, main peak)
ethane[27] = 0.215222  # m/z=29
ethane[28] = 0.262226  # m/z=30
ethane[29] = 0.005001  # m/z=31

methylamine = [0] * 50
methylamine[11] = 0.0020002  # m/z=13
methylamine[12] = 0.0040004 # m/z=14


oxygen = [0] * 50
silane = [0] * 50
methyl_alcohol = [0] * 50
hydrazine = [0] * 50
hydroxylamine = [0] * 50
hydrogen_sulfide = [0] * 50



phosphine = [0] * 50
methyl_fluoride = [0] * 50
methan_d3_ol = [0] * 50
hydrogen_chloride = [0] * 50
methanol_d4 = [0] * 50
argon = [0] * 50
cyclopropene = [0] * 50
allene = [0] * 50
propine = [0] * 50
methyl_isocyanide = [0] * 50
acetonitrile = [0] * 50
ketene = [0] * 50
methane_diazo = [0] * 50
cyabamide = [0] * 50
borane_carbonyl = [0] * 50
propene = [0] * 50
cyclopropane = [0] * 50
hydrogen_azide = [0] * 50
ethylenimine = [0] * 50
carbon_dioxide = [0] * 50
nitrous_oxide = [0] * 50
ethyne_fluoro = [0] * 50
acetaldehyde = [0] * 50
ethylene_oxide = [0] * 50
propane = [0] * 50
formamide = [0] * 50
methane_nitroso = [0] * 50
dimethylamine = [0] * 50
ethylamine = [0] * 50
nitrogen_dioxide = [0] * 50
formic_acid = [0] * 50
ethene_fluoro = [0] * 50
silane_methyl = [0] * 50
dimethyl_ether = [0] * 50
ethanol = [0] * 50
hydrazine_methyl = [0] * 50
hydroxylamine_o_methyl = [0] * 50
methanethiol = [0] * 50
phosphine_methyl = [0] * 50
ethane_fluoro = [0] * 50
chloromethane = [0] * 50
butadiyne_1_3 = [0] * 50

NIST_MASS_SPECTRA = {
    'Mass/Charge peaks': [
        2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
        39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51
    ],
    'H2: Hydrogen': hydrogen,
    'D2: Deuterium': deuterium,
    'CH4: Methane': methane,
    'H3N: Ammonia': ammonia,
    'H2O: Water': water,
    'C2H2: Acetilene': acetilene,
    'HCN: Hydrogen cyanide': hydrogen_cyanide,
    'CO: Carbon monoxide': carbon_monoxide,
    'N2: Nitrogen': nitrogen,
    'C2H4: Ethylene': ethylene,
    'B2H6: Diborane': diborane,
    'NO: Nitric oxide': nitric_oxide,
    'HCHO: Formaldehyde': formaldehyde,
    'C2H6: Ethane': ethane,
    'CH5N: Methylamine': methylamine,
    'O2: Oxygen': oxygen,
    'SiH4: Silane': silane,
    'CH4O: Methyl Alcohol': methyl_alcohol,
    'N2H4: Hydrazine': hydrazine,
    'H3NO: Hydroxylamine': hydroxylamine,
    'H2S: Hydrogen sulfide': hydrogen_sulfide,
    'Phosphine': phosphine,
    'Methyl fluoride': methyl_fluoride,
    'Methan-d3-ol': methan_d3_ol,
    'Hydrogen chloride': hydrogen_chloride,
    'Methanol-D4': methanol_d4,
    'Ar: Argon': argon,
    'Cyclopropene': cyclopropene,
    'Allene': allene,
    'Propine': propine,
    'Methyl isocyanide': methyl_isocyanide,
    'Acetonitrile': acetonitrile,
    'Ketene': ketene,
    'Methane, diazo-': methane_diazo,
    'Cyabamide': cyabamide,
    'Borane carbonyl': borane_carbonyl,
    'Propene': propene,
    'Cyclopropane': cyclopropane,
    'Hydrogen azide': hydrogen_azide,
    'Ethylenimine': ethylenimine,
    'Carbon dioxide': carbon_dioxide,
    'Nitrous oxide': nitrous_oxide,
    'Ethyne, fluoro-': ethyne_fluoro,
    'Acetaldehyde': acetaldehyde,
    'Ethylene oxide': ethylene_oxide,
    'Propane': propane,
    'Formamide': formamide,
    'Methane, nitroso-': methane_nitroso,
    'Dimethylamine': dimethylamine,
    'Ethylamine': ethylamine,
    'Nitrogen dioxide': nitrogen_dioxide,
    'Formic acid': formic_acid,
    'Ethene, fluoro-': ethene_fluoro,
    'Silane, methyl-': silane_methyl,
    'Dimethyl ether': dimethyl_ether,
    'Ethanol': ethanol,
    'Hydrazine, methyl-': hydrazine_methyl,
    'Hydroxylamine, O-methyl-': hydroxylamine_o_methyl,
    'Methanethiol': methanethiol,
    'Phosphine, methyl-': phosphine_methyl,
    'Ethane, fluoro-': ethane_fluoro,
    'Chloromethane': chloromethane,
    '1,3-Butadiyne': butadiyne_1_3
}