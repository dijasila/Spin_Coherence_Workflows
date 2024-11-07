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
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
def get_super(x):
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
    res = x.maketrans(''.join(normal), ''.join(super_s))
    return x.translate(res)
def get_sub(x):
    normal = "0123456789"
    sub_s = "₀₁₂₃₄₅₆₇₈₉"
    res = x.maketrans(''.join(normal), ''.join(sub_s))
    return x.translate(res)    
plt.rcParams["font.family"] = "Gulasch", "Times", "Times New Roman", "serif"
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
hosts= ['BN', 'CaI2', 'MgBr2', 'MgI2', 'MoS2', 'V2O5', 'SiS2', 'GeS']
#hosts= ['CaI2', 'MgBr2']
pristinepath=[]
for p in hosts:
    pristinepath.append(Path("./" + f'{p}'))
for P in range(len(pristinepath)):
    if (pristinepath[P]/'Coherence.json').is_file():
        Coherence=read_json(pristinepath[P]/'Coherence.json')
        Coh= Coherence['Coherence']
        Time=Coherence['Time(ms)']
        plt.plot(Time, Coh, label='{}'.format(str(pristinepath[P])), ls='--', alpha=0.95)
#plt.plot(Time1, fit_y, label=r'fit : exp(-t/T$_{2}$)$^{n}$',   color="r", alpha=0.65)
#plt.tick_params(axis='x', labelsize=15)
plt.xlabel('Time (ms)', fontsize=18)
plt.ylabel((u'$\u2112(t)$'), fontsize=18)
plt.legend(frameon=False, loc='best')
plt.ylim(0.02, 1.05)
plt.xlim(0.01, 50)
#plt.xticks(np.arange(0, 5, step=0.5), fontsize=16)
#plt.yticks(np.arange(0, 1, step=0.1), fontsize=15)
plt.minorticks_on()
#plt.title(r'MoS$_{2}$-v$_{S}^{-2}$', fontsize=16)
plt.xscale('log')
plt.margins(x=0.0)
plt.tight_layout()
plt.savefig('Cohernece-Function.pdf', dpi=1000)
plt.show()

