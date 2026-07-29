
# -*- coding: utf-8 -*-

u'''(INTERNAL) C{pybelbg} access to some private C{pygeodesy} attributes.
'''
import os.path as os_path
import sys  # PYCHOK used!

_missing_ = 'missing'  # PYCHOK used!
_requires = '26.7.27'  # in README.rst, requirements.txt, setup.py


def _PyGeodesy_dir(requires):
    # Adjust sys.path to enable import pygeodesy
    d = None
    try:
        from pygeodesy import version as _v
    except ImportError:
        _v = _missing_
        # PYTHONPATH=.../PyBeLBG for development ONLY
        p = os_path.abspath(__file__)
        p = os_path.dirname(p)  # pybelbg_abspath
        p = os_path.dirname(p)  # PyBeLBG
        p = os_path.dirname(p)  # ../
        g = os_path.join(p, 'PyGeodesy')
        if g != p and g not in sys.path:
            sys.path.insert(0, g)
            try:
                from pygeodesy import version as _v  # PYCHOK redef
                d = g
            except ImportError:
                pass
#           finally:
#               try:
#                   sys.path.remove(g)
#               except ValueError:
#                   pass

    def _t(v):
        return tuple(map(int, v.split('.')))  # _DOT_

    if _v == _missing_ or _t(_v) < _t(requires):
        _v = ' %s, need %s or newer' % (_v, requires)
        raise ImportError('pygeodesy' + _v)

    return d  # or None

_PyGeodesy_dir = _PyGeodesy_dir(_requires)  # PYCHOK path or None

from pygeodesy.basics import _xinstanceof, _xsubclassof  # noqa: F401
from pygeodesy.constants import (_1_0, _3600_0,  # noqa: F401
                                 _isNAN, _isNAN0)  # noqa: F401
from pygeodesy.ellipsoidalBase import LatLonEllipsoidalBase as _LLEB  # noqa: F401
from pygeodesy.errors import _ValueError, _xkwds  # noqa: F401
from pygeodesy.internals import machine, _secs2str, _versions  # noqa: F401
from pygeodesy.interns import (_COMMA_, _DASH_, _easting_,  # noqa: F401
                               _H_, _height_, _lat_, _lon_, _N_,  # noqa: F401
                               _name_, _northing_, _SPACE_)  # noqa: F401
from pygeodesy.lazily import _ALL_DOCS, _ALL_OTHER, _FOR_DOCS  # noqa: F401
from pygeodesy.named import _NamedBase, _NamedTuple, _Pass  # noqa: F401
from pygeodesy.namedTuples import (EasNor2Tuple, LatLon2Tuple, PhiLam2Tuple,
                                  _isinside, _resize4)
from pygeodesy.streprs import Fmt  # noqa: F401

from pygeodesy import (Datums, Easting, Height, Lamd, Lat, Lon, Meter,
                       Northing, Phid, Property_RO)


class BeLBGError(_ValueError):
    '''Error raised for C{pybelbg}, C{hBG18}, unzip and other issues.
    '''
    pass


class BeLBG7Tuple(_NamedTuple):
    '''7-Tuple C{(easting, northing, H, lat, lon, height, beLBG)} with I{local}
       Belgian C{easting}, C{northing} and orthometric height C{H}, geodetic C{lat},
       C{lon} and ellipsoidal C{height} and C{beLBG} the C{Be*LBG} instance with
       C{lat} and C{lon} in C{degrees} and with C{easting}, C{northing}, C{H} and
       C{height} in C{meter}, conventionally.
    '''
    _Names_ = (_easting_, _northing_, _H_,    _lat_, _lon_, _height_, 'beLBG')
    _Units_ = ( Easting,   Northing,   Height,  Lat,   Lon,   Height,  _Pass)

    @Property_RO
    def datum(self):
        '''Get the C{beLBG}'s datum (C{Datum}).
        '''
        return self.beLBG.datum  # PYCHOK beLBG

#   def diff(self, other, datum=None, **name):
#       '''Return the difference between this and an C{other} C{BeLBG7Tuple}.
#
#          @kwarg datum: Datum C{diff} (C{Datum}, None or NAN).
#          @kwarg name: Optional name (C{str}).
#
#          @return: An L{BeLBG7Tuple} with the C{fabs(diff)} for each item,
#                   except C{datum} as B{C{datum}}.
#       '''
#       def _diff(a, b):
#           try:
#               return fabs(a - b)
#           except TypeError:
#               return datum
#
#       _xinstanceof(BeLBG7Tuple, other=other)
#       t = map2(_diff, self, other)
#       return BeLBG7Tuple(t, **name)

    @Property_RO
    def eastingnorthing(self):
        '''Get easting and northing (L{EasNor2Tuple}C{(easting, northing)}).
        '''
        return EasNor2Tuple(self.easting, self.northing, name=self.name)

    @Property_RO
    def eastingnorthingHeight(self):
        '''Get easting, northing and orthometric height (L{EasNorH3Tuple}C{(easting, northing, H)}).
        '''
        return EasNorH3Tuple(self.easting, self.northing, self.H, name=self.name)

    @Property_RO
    def lam(self):
        '''Get the longitude (B{C{radians}}).
        '''
        return Lamd(self.lon)  # PYCHOK lon

    @Property_RO
    def latlon(self):
        '''Get the lat-, longitude in C{degrees} (L{LatLon2Tuple}C{(lat, lon)}).
        '''
        return LatLon2Tuple(self.lat, self.lon, name=self.name)

    @Property_RO
    def latlonheight(self):
        '''Get the lat-, longitude in C{degrees} and height (L{LatLon3Tuple}C{(lat, lon, height)}).
        '''
        return self.latlon.to3Tuple(self.height)

    @Property_RO
    def latlonheightdatum(self):
        '''Get the lat-, longitude in C{degrees} with height and datum (L{LatLon4Tuple}C{(lat, lon, height, datum)}).
        '''
        return self.latlonheight.to4Tuple(self.datum)

    @Property_RO
    def latlonNgeoid(self):
        '''Get the lat-, longitude in C{degrees} and geoid height (L{LatLonN3Tuple}C{(lat, lon, N)}).
        '''
        return LatLonN3Tuple(self.lat, self.lon, self.N, name=self.name)

    @Property_RO
    def N(self):
        '''Get the geoid height C{N} (C{meter}, conventionally).
        '''
        return Height(N=self.height - self.H)

    @Property_RO
    def phi(self):
        '''Get the latitude (B{C{radians}}).
        '''
        return Phid(self.lat)  # PYCHOK lat

    @Property_RO
    def philam(self):
        '''Get the lat- and longitude in C{radians} (L{PhiLam2Tuple}C{(phi, lam)}).
        '''
        return PhiLam2Tuple(self.phi, self.lam, name=self.name)  # PYCHOK lam, phi

    @Property_RO
    def philamheight(self):
        '''Get the lat-, longitude in C{radians} and height (L{PhiLam3Tuple}C{(phi, lam, height)}).
        '''
        return self.philam.to3Tuple(self.height)  # PYCHOK height

    @Property_RO
    def philamheightdatum(self):
        '''Get the lat-, longitude in C{radians} with height and datum (L{PhiLamn4Tuple}C{(phi, lam, height, datum)}).
        '''
        return self.philamheight.to4Tuple(self.datum)

#   def toDatum(self, datum2, name=NN):
#       '''Convert this C{lat}, C{lon} and C{height} to B{C{datum2}}.
#
#          @arg datum2: Datum to convert I{to} (L{Datum}).
#          @kwarg name: Optional name (C{str}), overriding this name.
#
#          @return: An L{BeLBG7Tuple} with transformed C{lat}, C{lon} and C{height}
#                   or this L{BeLBG7Tuple} if this.datum is B{C{datum2}}.
#       '''
#       _xinstanceof(Datum, datum2=datum2)
#       if self.datum is datum2 or self.datum == datum2:  # PYCHOK datum
#           return self
#       g = self.toLatLon(_LLEB).toDatum(datum2)
#       h = NAN if _isNAN(self.height) else g.height  # PYCHOK preserve height NAN
#       return self.dup(lat=g.lat, lon=g.lon, datum=g.datum, height=h,
#                                             name=name or self.name)

#   def toLatLon(self, LatLon, **LatLon_kwds):
#       '''Return this C{lat}, C{lon}, C{datum} and C{height} as B{C{LatLon}}.
#
#          @arg LatLon: An ellipsoidal C{LatLon} class (C{pygeodesy.ellipsoidal*}).
#          @kwarg LatLon_kwds: Optional, additional B{C{LatLon}} keyword arguments.
#
#          @return: An B{C{LatLon}} instance.
#
#          @raise TypeError: B{C{LatLon}} not ellipsoidal or an other issue.
#       '''
#       _xsubclassof(_LLEB, LatLon=LatLon)
#       h    = _isNAN0(self.height)  # PYCHOK height
#       kwds = _xkwds(LatLon_kwds, name=self.name, height=h)
#       return LatLon(self.lat, self.lon, datum=self.datum, **kwds)  # PYCHOK datum

#   @Property_RO
#   def xy(self):
#       '''Get the I{local} easting, northing) coordinates (L{Vector2Tuple}C{(x, y)}).
#       '''
#       return Vector2Tuple(self.easting, self.northing, name=self.name)

#   @Property_RO
#   def xyz(self):
#       '''Get the I{local} easting, northing and (orthometric) height (L{Vector3Tuple}C{(x, y, z)}).
#       '''
#       return Vector3Tuple(self.easting, self.northing, self.H, name=self.name)


class EasNorH3Tuple(_NamedTuple):  # XXX move to pygeodesy
    '''3-Tuple C{(easting, northing, H)}, all in C{meter}, conventionally
       with orthometric height C{H}.
    '''
    _Names_ = EasNor2Tuple._Names_ + (_H_,)
    _Units_ = EasNor2Tuple._Units_ + (Height,)


class LatLonN3Tuple(_NamedTuple):  # XXX move to pygeodesy
    '''3-tuple C{(lat, lon, N)} with geoid height C{N} in C{meter}, conventionally.
    '''
    _Names_ = (_lat_, _lon_, _N_)
    _Units_ = ( Lat,   Lon,   Height)


class Lb4Tuple(_NamedTuple):
    '''4-Tuple C{(minE, minN, maxE, maxN)} with local C{Lambert} lower-left
       C{(minE, minN)} and upper-right C{(maxE, maxN)} bounds in C{meter},
       conventionally.
    '''
    _Names_ = ('minE',  'minN',   'maxE',  'maxN')
    _Units_ = ( Easting, Northing, Easting, Northing)

    def isinside(self, easting, northing, eps=0):
        '''Are B{C{easting}} and B{C{northing}} inside these C{Lambert} bounds?

           @arg easting: Easting (C{meter}).
           @arg northing: Northing (C{meter}).
           @kwarg eps: Over-/undersize the C{Lb} bounds (C{meter}).

           @return: C{False} if B{C{easting}} or B{C{northing}} is outsize
                    these C{Lb} bounds or C{NAN}, C{True} otherwise.
        '''
        z = Meter(eps=eps) if eps else 0
        return _isinside(Easting(easting), Northing(northing), z, self)

    def resize(self, eps):
        '''Get these C{Lambert} bounds, over- or undersized by C{B{eps}}.

           @arg eps: In- or decrease (C{meter}).

           @return: An L{Lb4Tuple}C{(minE, minN, maxE, maxN)} with all
                    4 bounds resized.
        '''
        return _resize4(self, Meter(eps=eps))


def _all_OTHER(*objs):  # PYCHOK shared
    # collect all __all__ lists or tuples
    _all = _ALL_OTHER(*objs)
    _all__all__.extend(_all)
    return _all

_all__all__ = []  # PYCHOK in .__init__

__all__ = _all_OTHER(machine, BeLBGError, BeLBG7Tuple, Datums,
                              EasNorH3Tuple, LatLonN3Tuple, Lb4Tuple)
__version__ = '26.07.28'

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
