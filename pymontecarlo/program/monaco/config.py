#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- Monaco Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: Monaco Monte Carlo program configuration

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys

# Third party modules.

# Local modules.
from pymontecarlo.settings import get_settings
from pymontecarlo.program.config import Program
from pymontecarlo.program.monaco.converter import Converter
from pymontecarlo.program.monaco.exporter import Exporter
from pymontecarlo.program.monaco.importer import Importer
from pymontecarlo.program.monaco.worker import Worker

# Globals and constants variables.

class _MonacoProgram(Program):

    def __init__(self):
        autorun = True if sys.platform == 'win32' else False
        Program.__init__(self, 'Monaco', 'monaco', Converter, Worker,
                          Exporter, Importer, autorun)

    def validate(self):
        settings = get_settings()

        if 'monaco' not in settings:
            raise AssertionError("Missing 'monaco' section in settings")

        if 'basedir' not in settings.monaco:
            raise AssertionError("Missing 'basedir' option in 'monaco' section of settings")

        basedir = settings.monaco.basedir
        if not os.path.isdir(basedir):
            raise AssertionError("Specified Monaco base directory (%s) does not exist" % basedir)

        try:
            mccli32_exe = settings.monaco.exe
        except AttributeError:
            filename = 'Mccli32'
            if os.name == 'nt':
                filename += '.exe'
            mccli32_exe = os.path.join(settings.monaco.basedir, filename)
        if not os.path.isfile(mccli32_exe):
            raise AssertionError("No Mccli32.exe in Monaco base directory (%s)" % basedir)
        if not os.access(mccli32_exe, os.X_OK):
            raise AssertionError("Specified Monaco executable (%s) is not executable" % mccli32_exe)

    def autoconfig(self, programs_path):
        if sys.platform == 'linux':
            basedir_path = '/usr/share/monaco'
            if not os.path.exists(basedir_path):
                return False

            exe_path = '/usr/bin/mccli32'
            if not os.path.exists(exe_path):
                return False
        else:
            basedir_path = os.path.join(programs_path, self.alias)
            if not os.path.exists(basedir_path):
                return False

            exe_path = os.path.join(programs_path, self.alias, 'Mccli32.exe')
            if not os.path.exists(exe_path):
                return False

        settings = get_settings()
        settings.add_section('monaco').basedir = basedir_path
        settings.add_section('monaco').exe = exe_path
        return True

program = _MonacoProgram()
