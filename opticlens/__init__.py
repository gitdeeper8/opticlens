"""OPTICLENS: Optical Phenomena, Turbulence & Imaging — Light Environmental Nonlinearity System"""

__version__ = "10.0.0"
__author__ = "Samir Baladi"
__email__ = "gitdeeper@gmail.com"
__license__ = "CC BY 4.0"
__doi__ = "10.5281/zenodo.18907508"

from opticlens.scattering.mie_v10 import Q_ext, MieModelV10

__all__ = ['Q_ext', 'MieModelV10']
