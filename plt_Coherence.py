import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import os, sys, re
import pycce as pc
import ase
from ase.io import read, write
from ase.visualize import view
from mpl_toolkits import mplot3d
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
from time import sleep
from progress.bar import Bar
#hosts= ['BN', 'CaI2', 'MgBr2', 'MgI2', 'MoS2', 'V2O5', 'SiS2', 'GeS']
pristinepath=[]
hosts= ['YCl3', 'ZnCl2']
for p in hosts:
    pristinepath.append(Path("./" + f'{p}'))
for P in range(len(pristinepath)):
    if (pristinepath[P]/'Coherence.json').is_file():
        if not (pristinepath[P]/'Coherence.png').is_file():
            Coherence=read_json(pristinepath[P]/'Coherence.json')
            try:
                plt.plot(Coherence['Time(ms)'], Coherence['Coherence'], label='{}'.format(pristinepath[P]), ls='--')
                plt.xlabel('Time (ms)')
                plt.ylabel('Coherence')
                plt.legend()
                plt.savefig(pristinepath[P]/f'Coherence.png')
                plt.close()
                print('Plotting the Coherence function for {} system.'.format(pristinepath[P]))
                with Bar('Processing...') as bar:
                    for i in range(100):
                        sleep(0.05)
                        bar.next()
            except Exception:
                pass
                print('WARNING: Coherence function could not be plotted for {} system.'.format(pristinepath[P]))
