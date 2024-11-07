import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import os, sys, re
import pycce as pc
import ase
from ase.io import read, write
from ase.visualize import view
from mpl_toolkits import mplot3d
from pycce.bath.array import BathArray
import warnings
from pycce.io.base import set_isotopes
from string import digits
import warnings
from pycce.utilities import rotmatrix
from collections import defaultdict
from pycce import BathArray
from pycce import common_concentrations
from ase.visualize.plot import plot_atoms
from pathlib import Path
from gpaw import GPAW, restart
from asr.core import command, option, ASRResult, prepare_result, read_json, write_json
import typing
from ase import Atoms
import shutil
import glob
#hosts= ['BN', 'CaI2', 'MgBr2', 'MgI2', 'MoS2', 'V2O5', 'SiS2', 'GeS']
hosts= ['BN']
pristinepath=[]
for p in hosts:
    pristinepath.append(Path("./" + f'{p}'))
seed = 80
np.random.seed(seed)
np.set_printoptions(suppress=True, precision=5)

from ase.build import bulk
#pristinepath = list(Path('.').glob('defects*'))
seed = 80
np.random.seed(seed)
np.set_printoptions(suppress=True, precision=5)

from ase.build import bulk

# Generate unitcell from ase
for P in range(len(pristinepath)):
    if not (pristinepath[P]/'Coherence.json').is_file():
        str_1 = read(pristinepath[P]/'structure.json')
        str_1 = pc.bath.BathCell.from_ase(str_1)
        str_1.zdir = [0, 0, 1]
        self = str_1
        size=1
        if not self.isotopes:
            isotopes = {}

            for a in self.atoms:

                try:
                    isotopes[a] = common_concentrations[a]
                except KeyError:
                    pass
        else:
            isotopes = self.isotopes

        rgen = np.random.default_rng(seed)

        axb = np.cross(self.cell[:, 0], self.cell[:, 1])
        bxc = np.cross(self.cell[:, 1], self.cell[:, 2])
        cxa = np.cross(self.cell[:, 2], self.cell[:, 0])

        anumber = int(size* np.linalg.norm(bxc) / (bxc @ self.cell[:, 0]) + 1)
        bnumber = int(size* np.linalg.norm(cxa) / (cxa @ self.cell[:, 1]) + 1)
        cnumber = int(size* np.linalg.norm(axb) / (axb @ self.cell[:, 2]) + 1)
        # print(anumber, bnumber, cnumber)
        dt = np.dtype([('N', np.unicode_, 16), ('xyz', np.float64, (3,))])
        atoms = []

        for a in isotopes:
            nsites = len(self.atoms[a])
                # print(nsites)
            sites_xyz = np.asarray(self.atoms[a]) @ self.cell.T
                # print(sites_xyz)
            maxind = np.array([anumber,
                               bnumber,
                               cnumber,
                               nsites], dtype=np.int32)

            natoms = np.prod(maxind, dtype=np.int32)
            atom_seedsites = np.arange(natoms, dtype=np.int32)
            mask = np.zeros(natoms, dtype=bool)
            for i in isotopes[a]:
                conc = isotopes[a][i]
                nisotopes = int(round(natoms * conc))
                seedsites = rgen.choice(atom_seedsites[~mask],
                                                nisotopes, replace=False,
                                                shuffle=False)
      
                mask += np.isin(atom_seedsites, seedsites)

                bcn =  anumber*bnumber*nsites
                cn = cnumber*nsites

                aindexes = seedsites // bcn - 1/2  # recenter at 0
                bindexes = (seedsites % bcn) // cn - 1/2  
                cindexes = ((seedsites % bcn) % cn) // nsites 

                # indexes of the sites
                nindexes = ((seedsites % bcn) % cn) % nsites

                indexes = np.column_stack((aindexes,
                                           bindexes,
                                            cindexes))

                uc_positions = np.einsum('jk,ik->ij', self.cell, indexes)

                subatoms = np.zeros(indexes.shape[0], dtype=dt)
                subatoms['N'] = i
                subatoms['xyz'] = uc_positions + sites_xyz[nindexes]
                atoms.append(subatoms)

        atoms = np.concatenate(atoms)
        # bath = bath[np.linalg.norm(bath['xyz'], axis=1) <= size]

#defective_atoms = defect(self.cell, atoms, add=add, remove=remove)
        bath_222 = BathArray(array=atoms)

        atoms_3=bath_222
#atoms_3 = BN_3.gen_supercell(1, seed=seed)

# Parameters of CCE calculations engine

# Order of CCE aproximation
        order = 2
# Bath cutoff radius
        r_bath = 30  # in A
# Cluster cutoff radius
        r_dipole = 12  # in A
# position of central spin
        position_3 = [2.5, 2.5, 350.0]
# Qubit levels (in Sz basis)
        alpha = [0, 0, 1]; beta = [0, 1, 0]
# ZFS Parametters of NV center in diamond
        D = 2.00 * 1e6  # in kHz
        E = 0.0          # in kHz

        spin_types = [('14N',  1,      1.9338,    20.44),
                      ('13C',  1 / 2,  6.72828),
                      ('29Si', 1 / 2, -5.3188),
                      ('10B', 3, 2.875),
                    ('11B', 3 / 2, 8.584),]

        calc_1 = pc.Simulator(spin=1, position=position_3,
                            alpha=alpha, beta=beta, D=D, E=E,
                            bath=atoms_3, r_bath=r_bath,
                            r_dipole=r_dipole, order=order)


# Time points
        time_space = np.linspace(0, 0.15, 1500)  # in ms
# Number of pulses in CPMG seq (0 = FID, 1 = HE)
        N = 1
# Mag. Field (Bx By Bz)
        B = np.array([0, 0, 500])  # in G
        try:
            l_conv_1 = calc_1.compute(time_space, pulses=N, magnetic_field=B,
                              method='cce', quantity='coherence', as_delay=False)    
            dict={
            "Coherence": l_conv_1.real,
            "Time(ms)": time_space,
            }
            print('INFO: writing the spin coherence of {} in folder {}.'.format(pristinepath[P], pristinepath[P]))
            write_json(pristinepath[P]/'Coherence.json', dict)
        except Exception:
            pass
            print('WARNING: Coherence function could not be computed for {} system.'.format(pristinepath[P]))