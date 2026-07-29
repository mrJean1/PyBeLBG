
# -*- coding: utf-8 -*-

u'''Main classes L{Be08LBG}, L{Be72LBG}, L{Be72NLBG}, L{Be72RLBG} and L{Be50LBG} implementing
the C{Belgian Lambert 2018}, C{-1972}, C{-1972N}, C{-1972R} respectively C{-1950} conic projection
and quasi-geoid heights with bilinear interpolation from C{Belgian hybrid quasi-geoid} U{hBG18
<https://DOI.org/10.5880/isg.2018.003>}.

Each of the 5 classes provides a C{forward} method to transform a geodetic lat-, longitude and
(ellipsoidal) height to local easting, northing and (orthometric) height and a C{reverse} method
for converting local to geodetic coordinates and (orthometric to ellipsoidal) height.

All classes use the same hybrid quasi-geoid C{hBG18} C{region4} but slighly different C{bounds4}
for valid lat- and longitudes.  Heights for points outside C{region4} are not interpolated and
are C{NAN} or throw a L{BeLBGError} exception.  Likewise, lat-, longitudes I{below} C{bounds4}
and easting, northing I{below} C{bounds4(asLb)} are considered invalid and replaced with C{NAN}
or raise a L{BeLBGError}.
'''
# make sure int/int division yields float quotient in Py2-
from __future__ import division as _; del _  # noqa: E702 ;

from pybelbg.__pygeodesy import (BeLBGError, BeLBG7Tuple, LatLonN3Tuple, Lb4Tuple,
                                _1_0, _3600_0, _isNAN, _name_,
                                _ALL_DOCS, _all_OTHER, _FOR_DOCS,
                                _isinside, _NamedBase, _NamedTuple)
from pybelbg.__pygeodesy import _COMMA_, _SPACE_  # PYCHOK used!
from pygeodesy import (typename, NAN, NN,  # "consterns"
                       Conics, Bounds4Tuple,  # lcc, namedTuples
                       property_RO, property_ROver,  # props
                       Degrees, Easting, Height, Lat, Lon, Northing)  # units

from math import ceil, floor

__all__ = ()
__version__ = '26.07.28'

_bounds__   = ' bounds '
_forward_   = 'forward'
_outside__  = 'outside '
_region4hBG =  Bounds4Tuple(48.5, 1.0, 52.5, 7.0, name='hBG region ')  # <https://EPSG.io/4937>
_reverse_   = 'reverse'
_Uccle_     = 'Uccle'  # PYCHOK == _BelBGbase.Uccle.name


class _BeLBGbase(_NamedBase):
    '''(INTERNAL) C{Be*LBG} base class.
    '''
    _bounds2 = None  # overloaded
    _conic   = None  # overloaded
    _latD    = Lat(latD=36 / _3600_0)  # 36"
    _lonD    = Lon(lonD=54 / _3600_0)  # 54"
    _raiser  = False

    def __init__(self, datum=None, raiser=False, **name):
        '''New C{Be*LBG} instance, optionally with a different C{conic}'s datum.

           @kwarg datum: Conic's datum to use (C{pygeodesy.Datums}, ellipsoidal only).
           @kwarg raiser: If C{True} raise a L{BeLBGError} for lat- or longitudes
                          outside L{region4} or below L{bounds4} (C{bool}).
           @kwarg name: Optional name C{B{name}='Be*LBG'} (C{str}).
        '''
        if name:  # typename(self)
            self.name = name
        if datum:
            c = self._conic.toDatum(datum)
            if self._conic is not c:
                self._conic = c
#           E = self.datum.ellipsoid
#           if not E.isOblate:
#               raise BeLBGError(repr(E), txt='not oblate')
        if raiser:
            self.raiser = True
#           T = self.datum.transform
#           if not T.isunity:
#               raise BeLBGError(repr(T), txt='not unity')

    def _as4Lb(self, t4, name=NN):
        # return C{t4} as L{Lb4Tuple}
        S, W, N, E = t4
        s, w, _ = self._forward3(False, S, W, None)
        n, e, _ = self._forward3(False, N, E, None)
        return Lb4Tuple(s, w, n, e, name=name or t4.name)

    def _belowError(self, raiser, coords, bounds2):
        # throw a below bounds2 exception if requested
        if raiser or (raiser is None and self.raiser):
            raise BeLBGError(coords, txt=_outside__ + bounds2.toRepr())
        return True

    @property_RO
    def _bounds2Lb(self):  # overwrite __class__._bounds2Lb
        # get lower-left of C{bounds4} as C{_Lb2Tuple}
        b =  self.bounds4(True)
        b = _Lb2Tuple(b.minE, b.minN, name=b.name)
        self.__class__._bounds2Lb = b
        return b

    def bounds4(self, asLb=False):
        '''Get the South, West, North and East bounds of this C{Lambert} conic projection.

           @kwarg asLb: Use C{B{asLb}=True} for the bounds in local C{Lambert} easting and
                        northing, otherwise in geodetic lat- and longitudes (C{bool}).

           @return: A L{Bounds4Tuple}C{(latS, lonW, latN, lonE)} with (WGS84) geodetic lat-
                    and longitudes in C{degrees} or an L{Lb4Tuple}C{(minE, minN, maxE, maxN)}
                    in C{meter}.

           @note: The C{bounds4} cover Belgium, Belgium's U{EEZ<http://MarineRegions.org/mrgid/3293>},
                  the Netherlands, the Netherlands' U{EEZ<http://MarineRegions.org/mrgid/5668>}
                  and Luxemburg.
        '''
        return self._bounds4Lb if asLb else self._bounds4

    @property_ROver
    def _bounds4BeNeLux(self):
        # BeNeLux covering BE, BE EEZ, NL, NL EEZ and LU
        def _b4(swne):  # <http://MarineRegions.org/mrgid/XXXX>
            return Bounds4Tuple(*swne.split(_COMMA_)).toUnits()

        b = _b4('49 26 50.6N, 5 44  5.6E, 50 10 59.9N, 6 31 49.2E')  # Lux <2233>
        b = _b4('50 45  5.8N, 3 21 31.3E, 53 33 38.5N, 7 13 37.9E').union(b)  # Ne <15>
        b = _b4('51 19 48.6N, 2 32 21.6E, 55 45 54.0N, 7 12 37.0E').union(b)  # Ne EEZ <5668>
        b = _b4('49 29 50.3N, 2 32 47.8E, 51 30 15.1N, 6 24 27.0E').union(b)  # Be <14>
        b = _b4('51  2 23.1N, 2 14 18.0E, 51 52 34.0N, 4 24  7.3E').union(b)  # Be EEZ <3293>
        # BeNeLux bounds (latS=49.447389, lonW=2.238333, latN=55.765, lonE=7.227194)
        return b.toUnits(name='BeNeLux' + _bounds__)

    @property_RO
    def _bounds4(self):  # overwrite class._bounds4
        # get C{bounds4} with lower-left adjusted upward
        s, w       = self._bounds2
        S, W, N, E = self._bounds4BeNeLux
        n = typename(self) + _bounds__
        b = Bounds4Tuple(max(s, S), max(w, W), N, E, name=n)
        self.__class__._bounds4 = b
        return b

    @property_RO
    def _bounds4Lb(self):  # overwrite class._bounds4Lb
        # get C{bounds4} as C{Lb4Tuple}
        b = self._as4Lb(self._bounds4)
        self.__class__._bounds4Lb = b
        return b

    def _c_f_N_f6(self, lat, lon):
        # return (int(ceil), int(floor), Normalized less floor) of C{lat}) + \
        #        (int(ceil), int(floor), Normalized less floor) of C{lon})
        S, W, _, _ = _region4hBG
        return _c_f_N_f3(lat, S, self._latD) + \
               _c_f_N_f3(lon, W, self._lonD)

    @property_RO
    def conic(self):
        '''Get the C{Lambert} conic (C{pygeodesy.Conic}).
        '''
        return self._conic

    @property_RO
    def datum(self):
        '''Get the C{Lambert} conic's datum (C{pygeodesy.Datum}).
        '''
        return self.conic.datum

    def _EasNor5(self, e, n, raiser=None, name=_reverse_):
        # return e, n, ... if non-NAN and not below bounds2Lb
        e, n = t = Easting(e), Northing(n)
        if _isNAN(e) or _isNAN(n):
            _NAN = True
        elif t < self._bounds2Lb:
            _NAN = self._belowError(raiser, t, self._bounds2Lb)
        else:
            _NAN = False
        return e, n, _NAN, raiser, name

    def forward(self, lat, lon, height=0, **raiser_name):
        '''Convert geodetic C{(B{lat}, B{lon})} and (ellipsoidal) B{C{height}}
           to C{easting}, C{northing} and (orthometric) height C{H}.

           @arg lat: Latitude (C{degrees}, geodetic).
           @arg lon: Longitude (C{degrees}, geodetic).
           @kwarg height: The (ellipsoidal) height (C{meter}, conventionally) or
                          C{None} to ignore C{hBGh} interpolation.

           @return: A L{BeLBG7Tuple}C{(easting, northing, H, lat, lon, height, beLBG)}
                    with C{easting}, C{northing} and (orthometric) height C{H} in
                    C{meter} or C{NAN} and C{beLBG} is this C{Be*LBG} instance.

           @raise BeLBGError: If the point is outside the C{BG} region and property
                              C{raiser is True} or keyword argument C{B{raiser}=True}.

           @note: C{H}, C{easting} and C{northing} will all be C{NAN} if B{C{lat}} or
                  B{C{lon}} is below this converter's L{bounds4}.

           @note: Orthometric height C{(H = h - N)} euals ellipsoidal height C{h}
                  less (hybrid quasi-) geoid height C{N}.
        '''
        lat, lon, _NAN, raiser, name = self._LatLon5(lat, lon, **raiser_name)
        if _NAN:
            e = n = H = NAN
        else:
            e, n, H = self._forward3(raiser, lat, lon, height)
        return BeLBG7Tuple(e, n, H, lat, lon, height, self, name=name)

    def _forward3(self, raiser, lat, lon, height):  # in .__main__
        # C{forward} core, returning C{(easting, northing, H)}
        H       = NAN if height is None or _isNAN(height) else (
                  Height(height) - self._hBGh(lat, lon, raiser))
        e, n, _ = self._conic.forward3(lat, lon)
        return e, n, H

    def hBGh(self, lat, lon):
        '''Interpolate the hybrid quasi-geoid C{hBG} height for a geodetic point.

           @arg lat: Latitude (C{degrees}, geodetic).
           @arg lon: Longitude (C{degrees}, geodetic).

           @return: Hybrid quasi-geoid C{hBG} height C{N} (C{meter}) or C{NAN}
                    if B{C{lat}} or B{C{lon}} is outside L{region4}.
        '''
        lat, lon, _NAN, _, _ = self._LatLon5(lat, lon, False)
        return NAN if _NAN else self._hBGh(lat, lon)

    def _hBGh(self, lat, lon, raiser=False):
        # interpolate C{N} at C{(lat, lon)} or C{NAN} if
        # outside or ... if _isNAN(lat) or _isNAN(lon)
        if _isinside(lat, lon, 0, _region4hBG):
            c_f_N_f6 = self._c_f_N_f6(lat, lon)
            N = _bilinear(self._hBG18, *c_f_N_f6)
            N =  Height(N=N)
        elif raiser or (raiser is None and self._raiser):
            raise self._outsidError(lat, lon)
        else:
            N =  NAN
        return N

    def hBGh3(self, easting, northing):
        '''Interpolate the hybrid quasi-geoid C{hBG} height for a local point.

           @arg easting: Easting (C{meter}, local).
           @arg northing: Northing (C{meter}, local).

           @return: L{LatLonN3Tuple}C{(lat, lon, N)} with the (hybrid
                    quasi-) geoid C{hBG} height C{N} in C{meter} or
                    C{NAN} if C{lat} or C{lon} is outside C{region4}.
        '''
        r = self.reverse(easting, northing, H=0, raiser=False)
        return LatLonN3Tuple(r.lat, r.lon, r.height, name=self.name)

    @property_ROver
    def _hBG18(self):  # load the hBG18 geoid, I{once}
        from pybelbg.hBG18 import _hBG18 as hBG
        S, W, N, E = _region4hBG
        assert int(_degN(N, S, self._latD) + _1_0) == len(hBG)
        assert int(_degN(E, W, self._lonD) + _1_0) == len(hBG)
        return hBG

    def isinside(self, lat, lon, eps=0):
        '''Is geodetic C{(B{lat}, B{lon})} inside the C{hBG} region?

           @arg lat: Latitude (C{degrees}, geodetic).
           @arg lon: Longitude (C{degrees}, geodetic).
           @kwarg eps: Over-/undersize the C{hBG} region (C{degrees}).

           @return: C{None} if B{C{lat}} or B{C{lon}} is NAN, C{False}
                    if outside the C{hBG} region, C{True} otherwise.

           @see: Method C{isinside} of L{bounds4<_BeLBGbase.bounds4>},
                 L{region4<_BeLBGbase.region4>} and L{bounds4(asLb)
                 <Lb4Tuple.isinside>}, L{region4(asLB)<Lb4Tuple.isinside>}
        '''
        lat, lon, _NAN, _, _ = self._LatLon5(lat, lon, False)
        return None if _NAN else _isinside(lat, lon, Degrees(eps=eps),
                                                    _region4hBG)

    def _LatLon5(self, lat, lon, raiser=None, name=_forward_):
        # return lat, lon, ... if non-NAN and not below bounds2
        lat, lon = t = Lat(lat), Lon(lon)
        if _isNAN(lat) or _isNAN(lon):
            _NAN = True
        elif t < self._bounds2:
            _NAN = self._belowError(raiser, t, self._bounds2)
        else:
            _NAN = False
        return lat, lon, _NAN, raiser, name

    def _outsidError(self, *lat_lon):
        # format an BeLBGError for C{lat_lon} outside the C{hBG} region
        return BeLBGError(lat_lon, txt=_outside__ + _region4hBG.toRepr())

    @property
    def raiser(self):
        '''Is an C{BeLBGError} thrown for points outside the C{hBG} region?
        '''
        return self._raiser

    @raiser.setter  # PYCHOK setter!
    def raiser(self, raiser):
        '''Use C{True} to throw an C{BeLBGError} for points outside the C{hBG} region.
        '''
        self._raiser = bool(raiser)

    def region4(self, asLb=False):
        '''Get the South, West, North and East bounds of the C{hBG} region.

           @kwarg asLb: Use C{B{asLb}=True} for the bounds in local C{Lambert}
                        easting and northing, otherwise in geodetic lat- and
                        longitudes (C{bool}).

           @return: A L{Bounds4Tuple}C{(latS, lonW, latN, lonE)} with (WGS84)
                    geodetic lat- and longitudes in C{degrees} or an
                    L{Lb4Tuple}C{(minE, minN, maxE, maxN)} in C{meter}.

           @note: The C{hBG} region covers all of Belgium, Luxemburg and the
                  southern half of the Netherlands.
        '''
        return self._region4Lb if asLb else _region4hBG

    @property_RO
    def _region4Lb(self):  # overwrite class._region4Lb
        n = _region4hBG.name.split()
        n = _SPACE_(typename(self), *n[1:])
        r =  self._as4Lb(_region4hBG, name=n)
        self.__class__._region4Lb = r
        return r

    def reverse(self, easting, northing, H=0, **raiser_name):
        '''Convert local B{C{easting}}, B{C{northing}} and (orthometric) height
           B{C{H}} to geodetic C{lat-}, C{longitude} and (ellipsoidal) C{height}.

           @arg easting: Easting (C{meter}, local).
           @arg northing: Northing (C{meter}, local).
           @kwarg H: The (orthometric) height (C{meter}, conventionally) or C{None}
                     to ignore C{hBGh} interpolation.

           @return: A L{BeLBG7Tuple}C{(easting, northing, H, lat, lon, height, beLBG)}
                    with geodetic C{lat} and C{lon} and (ellipsoidal) C{height} in
                    C{meter} or C{NAN} and C{beLBG} is this C{Be*LBG} instance.

           @raise BeLBGError: If the point is outside the C{hBG} region and property
                              C{raiser is True} or keyword argument C{B{raiser}=True}.

           @note: All C{lon}, C{lat} and C{height} will be C{NAN} if B{C{easting}} or
                  B{C{northing}} is below this converter's C{bounds4(asLb)}.

           @note: Ellipsoidal height C{(h = H + N)} equals orthometric height C{H}
                  plus (hybrid quasi-) geoid height C{N}.
        '''
        e, n, _NAN, raiser, name = self._EasNor5(easting, northing, **raiser_name)
        if _NAN:
            lat = lon = height = NAN
        else:
            lat, lon, height = self._reverse3(raiser, e, n, H)
        return BeLBG7Tuple(e, n, H, lat, lon, height, self, name=name)

    def _reverse3(self, raiser, e, n, H):  # in .__main__
        # C{reverse} core, returning C{(lat, lon, height)}
        lat, lon, _, _= self._conic.reverse4(e, n)
        height        = NAN if H is None or _isNAN(H) else (
                        Height(H=H) + self._hBGh(lat, lon, raiser))
        return lat, lon, height

    def toStr(self, prec=9, **unused):  # PYCHOK signature
        '''Return this C{Be*LBG} instance as a string.

           @kwarg prec: Precision, number of decimal digits (C{int}, 0..9).

           @return: This C{Be*LBG} (C{str}).
        '''
        return self.attrs(_name_, 'conic', 'raiser', prec=prec)  # _datum_, _Uccle_

    @property_RO
    def Uccle(self):  # overwrite class.Uccle
        '''Get C{Uccle<https://ROBinfo.OMA.BE/en/astro-info/geographical-coordinates-of-our-sites>} (aka Ukkel) as L{BelBG7Tuple}.
        '''
        lat, lon, H = self._Uccle3
        h = self.hBGh(lat, lon) + H  # height=147.815887  Be08LBG
        u = self.forward(lat, lon, height=h, name=_Uccle_)  # Be08LBG easting=649250.118675, northing=665257.86004
        self.__class__.Uccle = u
        return u

    @property_ROver
    def _Uccle3(self):
        # # lat=50.797778, lon=4.358111, H=104.9
        return Lat('50 47 52N'), Lon('4 21 29.2E'), Height(H=104.9)


class Be08LBG(_BeLBGbase):
    '''Belgian Lambert 2008 C{pygeodesy.Conics.Be08Lb} converter.
    '''
    _conic = Conics.Be08Lb

    @property_ROver
    def _bounds2(self):
        return _bounds2(44.77, -3.82, self)


class Be72LBG(_BeLBGbase):
    '''Belgian Lambert 1972 C{pygeodesy.Conics.Be72Lb} converter.
    '''
    _conic = Conics.Be72Lb

    @property_ROver
    def _bounds2(self):
        return _bounds2(49.30, 2.31, self)


class Be72NLBG(_BeLBGbase):
    '''Belgian Lambert 1972N C{pygeodesy.Conics.Be72NLb} converter.
    '''
    _conic = Conics.Be72NLb

    @property_ROver
    def _bounds2(self):
        return _bounds2(49.31, 2.15, self)


class Be72RLBG(_BeLBGbase):
    '''Belgian Lambert 1972R C{pygeodesy.Conics.Be72RLb} converter.
    '''
    _conic = Conics.Be72RLb

    @property_ROver
    def _bounds2(self):
        return _bounds2(49.21, 2.14, self)


class Be50LBG(_BeLBGbase):
    '''Belgian Lambert 1950 C{pygeodesy.Conics.Be50Lb} converter.
    '''
    _conic = Conics.Be50Lb

    @property_ROver
    def _bounds2(self):
        return _bounds2(49.31, 5.26, self)


class _Bounds2Tuple(_NamedTuple):
    '''2-Tuple C{(latS, lonW)} lower-left corner.
    '''
    _Names_ = Bounds4Tuple._Names_[:2]
    _Units_ = Bounds4Tuple._Units_[:2]


class _Lb2Tuple(_NamedTuple):
    '''2-Tuple C{(minE, minN)} lower-left corner.
    '''
    _Names_ = Lb4Tuple._Names_[:2]
    _Units_ = Lb4Tuple._Units_[:2]


def _bilinear(hBG, c_latI, f_latI, latN_f,
                   c_lonI, f_lonI, lonN_f):
    # interpolate hybrid quasi-geoid C{hBG} height
    ne, nw = hBG(c_latI, c_lonI, f_lonI)
    se, sw = hBG(f_latI, c_lonI, f_lonI)
    lonN_f1 = _1_0 - lonN_f  # == 1 - (lonN - f_lonN)
    return (ne * lonN_f + nw * lonN_f1) * latN_f + \
           (se * lonN_f + sw * lonN_f1) * (_1_0 - latN_f)


def _bounds2(latS, lonW, beLBG):
    # return the C{beLBG} lower-left bounds
    n = typename(beLBG) + _bounds__
    return _Bounds2Tuple(latS, lonW, name=n)


def _c_f_N_f3(*deg_SWD):
    # return int(ceil) and int(floor) of Normalized
    # and (Normalized less floor) of C{deg} degrees
    N = _degN(*deg_SWD)
    # assert N >= 0, N
    f =  floor(N)
    return int(ceil(N)), int(f), (N - f)


def _degN(deg, degSW, degD):
    # return C{deg} Normalized
    return (deg - degSW) / degD


_Be5LBGs = Be08LBG, Be72LBG, Be72NLBG, Be72RLBG, Be50LBG

if _FOR_DOCS:
    # for epydoc to include __doc__ for all classes
    for B in _Be5LBGs:
        B.bounds4  = _BeLBGbase.bounds4
        B.conic    = _BeLBGbase.conic
        B.datum    = _BeLBGbase.datum
        B.forward  = _BeLBGbase.forward
        B.hBGh     = _BeLBGbase.hBGh
        B.hBGh3    = _BeLBGbase.hBGh3
        B.isinside = _BeLBGbase.isinside
        B.region4  = _BeLBGbase.region4
        B.reverse  = _BeLBGbase.reverse

__all__ += _ALL_DOCS(_BeLBGbase)
__all__ += _all_OTHER(Conics, *_Be5LBGs)
del _ALL_DOCS, _all_OTHER, _Be5LBGs

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
