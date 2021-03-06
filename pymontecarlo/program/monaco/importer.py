#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- Monaco results importer
================================================================================

.. module:: importer
   :synopsis: Monaco results importer

.. inheritance-diagram:: pymontecarlo.program.monaco.output.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import csv

# Third party modules.
import numpy as np

from pyxray.transition import from_string

# Local modules.
from pymontecarlo.program.importer import Importer as _Importer, ImporterException

from pymontecarlo.options.detector import PhotonIntensityDetector, PhiZDetector

from pymontecarlo.results.result import \
    PhotonKey, PhotonIntensityResult, PhiZResult

# Globals and constants variables.

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._importers[PhotonIntensityDetector] = self._import_photon_intensity
        self._importers[PhiZDetector] = self._import_phi_z

    def _import(self, options, dirpath, *args, **kwargs):
        return self._run_importers(options, dirpath, *args, **kwargs)

    def _import_photon_intensity(self, options, name, detector, jobdir):
        intensities_filepath = os.path.join(jobdir, 'intensities_%s.csv' % name)
        if not os.path.exists(intensities_filepath):
            raise ImporterException('Result file "intensites_%s.csv" not found in job directory (%s)' % \
                                    (name, jobdir))

        intensities = {}

        with open(intensities_filepath, 'r') as fp:
            reader = csv.DictReader(fp, delimiter=';')
            try:
                row = next(reader)
            except StopIteration:
                row = {}

        for transition, intensity in row.items():
            transition = from_string(transition.strip())
            enf = (float(intensity.strip().replace(',', '.')), 0.0) # FIXME: Hack to handle locale problem
            intensities[PhotonKey(transition, True, PhotonKey.P)] = enf

        return PhotonIntensityResult(intensities)

    def _import_phi_z(self, options, name, detector, jobdir):
        prz_filepath = os.path.join(jobdir, 'phi_%s.csv' % name)
        if not os.path.exists(prz_filepath):
            raise ImporterException('Result file "phi_%s.csv" not found in job directory (%s)' % \
                                    (name, jobdir))

        with open(prz_filepath, 'r') as fp:
            reader = csv.reader(fp, delimiter=';')
            header = next(reader)

            data = {}
            for row in reader:
                for i, val in enumerate(row):
                    data.setdefault(header[i], []).append(float(val.replace(',', '.'))) # FIXME: Hack to handle locale problem

        rzs = np.array(data.pop('rho z'))

        distributions = {}
        for transition, values in data.items():
            transition = from_string(transition.strip())
            enf = np.array([rzs, values]).transpose()
            distributions[PhotonKey(transition, True, PhotonKey.P)] = enf

        return PhiZResult(distributions)
