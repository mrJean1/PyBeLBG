
# -*- coding: utf-8 -*-

u'''Run some C{Be*LBG}C{.forward} and C{.reverse} conversion examples.

Use C{"python3 -m pybelbg -h | --help"} to get the usage options:

C{usage: python3 -m pybelbg  [ -h | -help ]  [ -v | --version ]  [ -precision <ndigits> ]}

C{  [ -08 | -72 | -72N | -72R | -50 ] -forward  <lat> <lon> [ <height> ]}

C{  [ -08 | -72 | -72N | -72R | -50 ] -reverse  <easting> <northing> [ <H> ]}

C{  [ -08 | -72 | -72N | -72R | -50 ] -Uccle}

C{  [ -08 | -72 | -72N | -72R | -50 ] -Lb4tuple [ <ndigits> ]}
'''
from pybelbg import (Be08LBG, Be72LBG, Be72NLBG, Be72RLBG, Be50LBG, Lb4Tuple,
                    _pybelbg_, _versions)
from pybelbg.__pygeodesy import _DASH_, _isNAN
from pygeodesy import Lat, Lon, NAN, print_, truncate, typename

import os
import sys

__all__ = ()
__version__ = '26.07.27'

_Bs = {}
for _B in (Be08LBG, Be72LBG, Be72NLBG, Be72RLBG, Be50LBG):
    _b = '-' + typename(_B)[2:-3]
    _Bs[_b] = _B(name=_b)
_b    = '-08'
_B    = _Bs[_b]
_HT   = '\t'
_prec =  6


class _Lb4Tuple(object):
    '''(INTERNAL) Get the C{hBG} region bounds as L{Lb4Tuple},
       truncated to non-NAN round-trips and millimeter.
    '''
    iters = 0

    def __init__(self, B, ndigits):
        m = pow(10.0, -ndigits)  # centi-, milli-, ...meter
        r = B.region4()
        t = self._corner2(B, r.latS, r.lonW,  m) + \
            self._corner2(B, r.latN, r.lonE, -m)
        self._T = Lb4Tuple(t, name=typename(B))

    def __str__(self):
        return self._T.toRepr()

    def _corner2(self, B, lat, lon, m):
        i = 0
        x, y, H = B._forward3(False, lat, lon, NAN)
        while _isNAN(H):
            latlonh = B._reverse3(False, x, y, 0)
            _, _, H = B._forward3(False, *latlonh)
            x += m
            y += m
            i += 1
        self.iters += i
        return x, y

    def truncate(self, ndigits):
        s, w, n, e = self._T
        m = pow(10.0, -ndigits)
        s = truncate(s + m, ndigits)  # ceil
        w = truncate(w + m, ndigits)  # ceil
        n = truncate(n    , ndigits)  # floor
        e = truncate(e    , ndigits)  # floor
        self._T = Lb4Tuple(s, w, n, e, name=self._T.name)
        return self


def _llh(lat, lon, h=0):  # allow lat, lon as DMS str
    return Lat(lat), Lon(lon), float(h)


def _runx():  # run several examples
    x = 0
    for cmd in ('-v', '--help',
                '-08 -forward 52.15616 5.3876389',
                '-08 -reverse 155000 463000',
                '-72 -forward 52.15616 5.3876389',
                '-72 -reverse 155000 463000',
                '-50 -forward 52.15616 5.3876389',
                '-50 -reverse 155000 463000',
                '-08 -Uccle'):
        cmd = 'python3.14 -m pybelbg ' + os.path.join(*cmd.split('/'))
        print_('%', cmd, nl=2)
        x = max(os.system(cmd) // 256, x)
    sys.exit(x)


def _usage(x):
    _t = '\t[ -08 | -72 | -72N | -72R | -50 ]'
    print_('usage: python3 -m', _pybelbg_, ' [ -h | -help ]',
                                           ' [ -v | --version ]',
                                           ' [ -precision <ndigits> ]')
    print_(_t, '-forward  <lat> <lon> [ <height> ]')
    print_(_t, '-reverse  <easting> <northing> [ <H> ]')
    print_(_t, '-Uccle')
#   print_(_t, '-Lb4Tuple [ <ndigits> ]')
#   print_(_t, '-unzip  [ -force ]')
    sys.exit(x)  # $status


argv = sys.argv[1:]
while argv and argv[0].startswith(_DASH_):  # MCCABE 13
    arg  = argv.pop(0)
    larg = len(arg)
    narg = len(argv)
    if arg == '-h' or ('--help'.startswith(arg) and larg > 2):
        _usage(0)
    elif arg == '-v' or ('--version'.startswith(arg) and larg > 2):
        print_(_versions())
        sys.exit(0)
    elif arg in _Bs:
        _b =  arg
        _B = _Bs[_b]
    elif '-precision'.startswith(arg) and larg > 1 and narg > 0:
        try:
            _prec = int(argv.pop(0))
        except ValueError:
            pass

    elif '-forward'.startswith(arg) and larg > 1 and narg > 1:
        f = _B.forward(*_llh(*argv[:3]))
        print_(f.toRepr(prec=_prec))
        r = _B.reverse(f.easting, f.northing, f.H)
        print_(r.toRepr(prec=_prec))

    elif '-reverse'.startswith(arg) and larg > 1 and narg > 1:
        r = _B.reverse(*map(float, argv[:3]))
        print_(r.toRepr(prec=_prec))
        f = _B.forward(r.lat, r.lon, r.height)
        print_(f.toRepr(prec=_prec))

    elif '-Uccle'.startswith(arg) and larg > 1:
        print_(_B.Uccle.toRepr(prec=_prec))

    elif '-Lb4Tuple'.startswith(arg) and larg > 3:
        n =  int(argv.pop(0)) if narg > 0 else 3
        t = _Lb4Tuple(_B, n)
        print_(t, t.iters)
        t =  t.truncate(n)
        print_(t, n)

    elif '-runx'.startswith(arg) and larg > 3:
        _runx()

#   elif '-unzip'.startswith(arg) and larg > 3:
#       from pybelbg.v_grids import _v_gridz_unzip
#       _f = bool(argv and argv[0] == '-force')
#       _v_gridz_unzip(_b[2], force=_f, verbose=True)
    else:
        print_('invalid option:', repr(arg))
        _usage(1)


# % python3.14 -m pybelbg -v
# pybelbg 26.7.27 pygeodesy 26.7.27 Python 3.14.6 64bit arm64 macOS 26.5.2


# % python3.14 -m pybelbg --help
# usage: python3 -m pybelbg  [ -h | -help ]  [ -v | --version ]  [ -precision <ndigits> ]
# 	[ -08 | -72 | -72N | -72R | -50 ] -forward  <lat> <lon> [ <height> ]
# 	[ -08 | -72 | -72N | -72R | -50 ] -reverse  <easting> <northing> [ <H> ]
#   [ -08 | -72 | -72N | -72R | -50 ] -Uccle


# % python3.14 -m pybelbg -08 -forward 52.15616 5.3876389
# forward(easting=719734.655165, northing=816890.903691, H=-40.910143, lat=52.15616, lon=5.387639, height=0.0, beLBG=Be08LBG(name='-08', conic=Conic(name='Be08Lb', lat0=50.797815, lon0=4.35921583, par1=49.83333333, par2=51.16666667, E0=649328, N0=665262, k0=1, SP=2, datum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84)), raiser=False))
# reverse(easting=719734.655165, northing=816890.903691, H=-40.910143, lat=52.15616, lon=5.387639, height=0.0, beLBG=Be08LBG(name='-08', conic=Conic(name='Be08Lb', lat0=50.797815, lon0=4.35921583, par1=49.83333333, par2=51.16666667, E0=649328, N0=665262, k0=1, SP=2, datum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84)), raiser=False))


# % python3.14 -m pybelbg -08 -reverse 155000 463000
# reverse(easting=155000.0, northing=463000.0, H=0, lat=NAN, lon=NAN, height=NAN, beLBG=Be08LBG(name='-08', conic=Conic(name='Be08Lb', lat0=50.797815, lon0=4.35921583, par1=49.83333333, par2=51.16666667, E0=649328, N0=665262, k0=1, SP=2, datum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84)), raiser=False))
# forward(easting=NAN, northing=NAN, H=NAN, lat=NAN, lon=NAN, height=NAN, beLBG=Be08LBG(name='-08', conic=Conic(name='Be08Lb', lat0=50.797815, lon0=4.35921583, par1=49.83333333, par2=51.16666667, E0=649328, N0=665262, k0=1, SP=2, datum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84)), raiser=False))


# % python3.14 -m pybelbg -72 -forward 52.15616 5.3876389
# forward(easting=219843.842978, northing=316827.541843, H=-40.910143, lat=52.15616, lon=5.387639, height=0.0, beLBG=Be72LBG(name='-72', conic=Conic(name='Be72Lb', lat0=90, lon0=4.36748667, par1=51.16666723, par2=49.8333339, E0=150000.013, N0=5400088.438, k0=1, SP=2, datum=Datum(name='ED50', ellipsoid=Ellipsoids.Intl1924, transform=Transforms.ED50)), raiser=False))
# reverse(easting=219843.842978, northing=316827.541843, H=-40.910143, lat=52.15616, lon=5.387639, height=0.0, beLBG=Be72LBG(name='-72', conic=Conic(name='Be72Lb', lat0=90, lon0=4.36748667, par1=51.16666723, par2=49.8333339, E0=150000.013, N0=5400088.438, k0=1, SP=2, datum=Datum(name='ED50', ellipsoid=Ellipsoids.Intl1924, transform=Transforms.ED50)), raiser=False))


# % python3.14 -m pybelbg -72 -reverse 155000 463000
# reverse(easting=155000.0, northing=463000.0, H=0, lat=53.472891, lon=4.442684, height=NAN, beLBG=Be72LBG(name='-72', conic=Conic(name='Be72Lb', lat0=90, lon0=4.36748667, par1=51.16666723, par2=49.8333339, E0=150000.013, N0=5400088.438, k0=1, SP=2, datum=Datum(name='ED50', ellipsoid=Ellipsoids.Intl1924, transform=Transforms.ED50)), raiser=False))
# forward(easting=155000.0, northing=462999.999999, H=NAN, lat=53.472891, lon=4.442684, height=NAN, beLBG=Be72LBG(name='-72', conic=Conic(name='Be72Lb', lat0=90, lon0=4.36748667, par1=51.16666723, par2=49.8333339, E0=150000.013, N0=5400088.438, k0=1, SP=2, datum=Datum(name='ED50', ellipsoid=Ellipsoids.Intl1924, transform=Transforms.ED50)), raiser=False))


# % python3.14 -m pybelbg -50 -forward 52.15616 5.3876389
# forward(easting=219843.829998, northing=316739.060917, H=-40.910143, lat=52.15616, lon=5.387639, height=0.0, beLBG=Be50LBG(name='-50', conic=Conic(name='Be50Lb', lat0=90, lon0=4.36748667, par1=49.83333333, par2=51.16666667, E0=150000, N0=5400000, k0=1, SP=2, datum=Datum(name='ED50', ellipsoid=Ellipsoids.Intl1924, transform=Transforms.ED50)), raiser=False))
# reverse(easting=219843.829998, northing=316739.060917, H=-40.910143, lat=52.15616, lon=5.387639, height=0.0, beLBG=Be50LBG(name='-50', conic=Conic(name='Be50Lb', lat0=90, lon0=4.36748667, par1=49.83333333, par2=51.16666667, E0=150000, N0=5400000, k0=1, SP=2, datum=Datum(name='ED50', ellipsoid=Ellipsoids.Intl1924, transform=Transforms.ED50)), raiser=False))


# % python3.14 -m pybelbg -50 -reverse 155000 463000
# reverse(easting=155000.0, northing=463000.0, H=0, lat=NAN, lon=NAN, height=NAN, beLBG=Be50LBG(name='-50', conic=Conic(name='Be50Lb', lat0=90, lon0=4.36748667, par1=49.83333333, par2=51.16666667, E0=150000, N0=5400000, k0=1, SP=2, datum=Datum(name='ED50', ellipsoid=Ellipsoids.Intl1924, transform=Transforms.ED50)), raiser=False))
# forward(easting=NAN, northing=NAN, H=NAN, lat=NAN, lon=NAN, height=NAN, beLBG=Be50LBG(name='-50', conic=Conic(name='Be50Lb', lat0=90, lon0=4.36748667, par1=49.83333333, par2=51.16666667, E0=150000, N0=5400000, k0=1, SP=2, datum=Datum(name='ED50', ellipsoid=Ellipsoids.Intl1924, transform=Transforms.ED50)), raiser=False))


# % python3.14 -m pybelbg -08 -Uccle
# Uccle(easting=649250.118675, northing=665257.86004, H=104.9, lat=50.797778, lon=4.358111, height=147.815887, beLBG=Be08LBG(name='-08', conic=Conic(name='Be08Lb', lat0=50.797815, lon0=4.35921583, par1=49.83333333, par2=51.16666667, E0=649328, N0=665262, k0=1, SP=2, datum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84)), raiser=False))

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
