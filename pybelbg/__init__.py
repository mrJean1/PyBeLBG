
# -*- coding: utf-8 -*-

u'''A pure Python implementation of the C{Belgian hybrid quasi-geoid} U{hBG18
<https://DOI.org/10.5880/isg.2018.003>} with several Belgian C{Lambert 2018},
C{-1972s} and C{-1950} conic projections to convert between geodetic lat-,
longitudes and (ellipsoidal) height and local easting, northing and (orthometric)
height based on bilinear interpolation of quasi-geoid C{hBG18} heights.
'''
import os.path as os_path
import sys

# _isfrozen     = getattr(_sys, 'frozen', False)
pybelbg_abspath = os_path.dirname(os_path.abspath(__file__))  # _sys._MEIPASS + '/pyrdnap'
_pybelbg_       = __package__ or  os_path.basename(pybelbg_abspath)

# setting __path__ should ...
__path__ = [pybelbg_abspath]
try:  # ... make this import work, ...
    import pybelbg.__pygeodesy as _  # noqa: F401
except ImportError:  # ... if it doesn't, extend sys.path to include
    # this very directory such that all public and private sub-modules
    # can be imported (by epydoc, checked by PyChecker, etc.)
    if pybelbg_abspath not in sys.path:
        sys.path.insert(0, pybelbg_abspath)  # XXX __path__[0]

try:  # PYCHOK pygeodesy
    from pybelbg.__pygeodesy import *  # noqa: F403
except (AttributeError, ImportError) as x:
    raise AssertionError(str(x))

from pybelbg.belbgs import *  # noqa: F403


def _all__init__(*names):  # deleted below
    from pybelbg.__pygeodesy import _all__all__  # PYCHOK ...
    _all__all__.extend(names)
    _all__all__[:] = sorted(_all__all__)  # set(_all__all__)
    return _all__all__


def _versions():  # in .__main__, .v_self, .test/bases
    # Get the pyrdnap, pygeodesy, Python ... versions (C{str}).
    from pybelbg.__pygeodesy import _SPACE_, _versions as _pygeodesy_versions  # PYCHOK ...
    v  = __version__.replace('.0', '.')
    l_ = [_pybelbg_, v] + _pygeodesy_versions(None)
    return _SPACE_.join(l_)  # PYCHOK shadows?


__all__ = _all__init__('pybelbg_abspath')
__version__ = '26.07.29'
# del _all__init__

# **) MIT License
#
# Copyright (C) 2026-2026 -- mrJean1 at Gmail -- All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
