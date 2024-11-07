from ase.io import read
from asr.core import command, option, ASRResult, prepare_result, read_json
from asr.database.browser import make_panel_description, href
from gpaw import restart
import typing, os, sys
import numpy as np
from pathlib import Path
from ase import Atoms
from ase.io import read, write
def get_folder_from_txt(name):
    folder_list = []
    with open (name, 'rt') as myfile:
        for myline in myfile:
            line = myline.split()[0]
            if line.startswith('/home'):
                folder_list.append(line)
    return folder_list
folders= get_folder_from_txt('triplets_2.txt')
unique=[]
for folder in folders:
    def check_and_return_input():
        """Check whether folder structure is correct and return input."""
        pristinepath = list(Path(f'{folder}').glob('../../../defects.pristine*'))[0]
        try:
            pris_struc = read(pristinepath / 'structure.json')
        except FileNotFoundError:
            print('ERROR: pristine structure not available!')
        try:
            struc = read(folder+'structure.json')
            unrel = read(folder+'unrelaxed.json')
        except FileNotFoundError:
            print('ERROR: defect structure(s) not available!')
        try:
            prim_unrel = read(folder + '../../../unrelaxed.json')
        except FileNotFoundError:
            print('ERROR: primitive unrelaxed structure not available!')

        return struc, unrel, prim_unrel, pris_struc
    structure, unrelaxed, primitive, pristine = check_and_return_input()
    def is_vacancy(defectpath):
        """Check whether current defect is a vacancy."""
        try:
            defecttype = str(Path(f'{folder}').absolute()).split(
                '/')[-2].split('_')[-2].split('.')[-1]
            if defecttype == 'v':
                return True
            else:
                return False
        except IndexError:
            return False
    def get_defect_info(primitive, folder):
        """Return defecttype, and kind."""
        defecttype = str(Path(f'{folder}').absolute()).split(
            '/')[-2].split('_')[-2].split('.')[-1]
        defectpos = str(Path(f'{folder}').absolute()).split(
            '/')[-2].split('_')[-1]
        return defecttype, defectpos
    
    def return_defect_coordinates(structure, unrelaxed, primitive, pristine, folder):
        """Return the coordinates of the present defect."""
        deftype, defpos = get_defect_info(primitive, folder)
        if not is_vacancy(folder):
            for i in range(len(primitive)):
                if not (primitive.get_chemical_symbols()[i]
                        == structure.get_chemical_symbols()[i]):
                    label = i
                    break
                else:
                    label = 0
        elif is_vacancy(folder):
            for i in range(len(primitive)):
                if not (primitive.get_chemical_symbols()[i]
                        == structure.get_chemical_symbols()[i]):
                    label = i
                    break
                else:
                    label = 0

        pos = pristine.get_positions()[label]

        return pos
#d=return_defect_coordinates(structure, unrelaxed, primitive, pristine,
#                              defectpath)
    pris_sc=pristine
    defect_sc=unrelaxed
    name = Path(str(folder)).parts[8]

    from ase.atoms import Atoms
    def embedd(defect_sc, pris_sc):
        D=[defect_sc.get_cell()[0], defect_sc.get_cell()[1], [0.0, 0.0, 700]]
        dd=-return_defect_coordinates(structure, unrelaxed, primitive, pristine, folder)
        defect_sc.translate(dd)
        pris_sc.translate(dd)
        defect_sc.set_cell(D)
        pris_sc.set_cell(D)
        defect_sc.translate([0.0, 0.0, 350])
        pris_sc.translate([0.0, 0.0, 350])
        d=len(pris_sc)-len(defect_sc)
        pris_large_sc=pris_sc.repeat((30,30,1))
        pos1=pris_sc.get_positions()
        del pris_large_sc[0:len(pos1)]
        defective_bigger_sc = pris_large_sc + defect_sc
    #defective_bigger_sc.wrap()
        assert len(defective_bigger_sc) == 900*len(pris_sc) - d
        #defective_bigger_sc.translate([30, 30, 0.0])
        #defective_bigger_sc.wrap()
        os.mkdir(f'/home/niflheim/sajal/MagmomConvergence/doubledefects/double_defect/{name}/')
        write(f'/home/niflheim/sajal/MagmomConvergence/doubledefects/double_defect/{name}/structure.json'.format(defective_bigger_sc), defective_bigger_sc)
        return defective_bigger_sc
    
    folderlist = []
    structurelist = []
    i = 0

    try:
        if Path(folder + 'gs.gpw').is_file():
            _, calc = restart(folder + 'gs.gpw', txt=None)
            defect_sc=read(folder + 'structure.json')
            pris_sc=read(folder + '../../../defects.pristine_sc.000/structure.json')
            path = Path(folder).absolute()
            #name = path.parts[-2] + '_' + path.parts[-1]
            N_tot = calc.get_number_of_bands()
            E_F = calc.get_fermi_level()
            magmom = calc.get_magnetic_moment()
            if -0.1 <= abs(magmom) <= 5:
                print('INFO: {} in folder {}'.format(magmom, folder))
                try:
                    embedd(defect_sc, pris_sc)
                except AssertionError:
                    print(f'WARNING: Assertion error {folder}.')
                i += 1

    except AttributeError:
        print(f'WARNING: corrupted gs.gpw in folder {folder}.')