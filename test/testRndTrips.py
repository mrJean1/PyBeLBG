
# -*- coding: utf-8 -*-

# Test L{PyBeLBG} with round-trips of random lat-/longitudes inside.

from bases import Datums, TestsBase, NAN, startswith, typename

from pybelbg import (Be08LBG, Be72LBG, Be72NLBG, Be72RLBG, Be50LBG,
                     BeLBG7Tuple)
from pybelbg.belbgs import _isNAN

from math import fabs
from random import random, seed
from time import localtime

__all__ = ()
__version__ = '26.07.29'

# random repeatable all day
seed(localtime().tm_yday)
del localtime, seed

_ndigits = 8  # 9 cause 95 v1 failures
_nrandom = 64


def _anyNAN(t):
    return any(map(_isNAN, t))


def _rnd(f):
    return round(f, _ndigits)


def _str(t, ndigits=8):
    t = tuple(round(f, ndigits) for f in t[:6])
    return str(t)


class Tests(TestsBase):

    def testBe_LBG(self, B):
        t = B.toStr()
        self.test('Be_LBG', t, t, nl=1)

        t = B.region4().toRepr()
        self.test(B.name, t, t)
        t = B.bounds4().toRepr()
        self.test(B.name, t, t, nt=1)

        t = B.region4(True).toRepr()
        self.test(B.name, t, t)
        t = B.bounds4(True).toRepr()
        self.test(B.name, t, t, nt=1)

        self.test(B.name, 'Antwerp', 'Antwerp')  # ISG -42.383 <https://www.ISGeoid.PoliMi.IT/Geoid/height_conversion.html>
        self.testRndTrip(B, 51.21989, 4.40346,  # .H = -42.383352
                            eas_nor='(652419.16905189, 712216.88762658)')
        U = B.Uccle
        self.test(B.name, U.name, U.name)
        self.testRndTrip(B, U.lat, U.lon, U.height,
                            eas_nor=U.eastingnorthing.toStr(prec=8))
        self.test(B.name, 'Maastricht', 'Maastricht')  # ISG -43.382
        self.testRndTrip(B, 50.851368, 5.690973,  # .H = -43.381897
                            eas_nor='(743103.01343191, 672060.17452257)')
        self.test(B.name, 'Rotterdam', 'Rotterdam')  # ISG -41.22
        self.testRndTrip(B, 51.9225, 4.47917,  # -41.220305
                            eas_nor='(657582.42979196, 790403.36687921)')
        # Z001_ETRS89andRDNAP.txt first point
        self.test(B.name, 'id 30010000', 'id 30010000')  # ISG -41.425
        self.testRndTrip(B, 51.728601274, 4.712120126, 301.7981,  # .H = -41.425494
                            eas_nor='(673714.94919006, 768876.34323137)')  # 258.0057

    def testRandom(self, B, **nl):
        S, W, N, E = B.bounds4()
        E_W = E - W
        N_S = N - S
        r   = random.__name__
        self.test(B.name, r, r, **nl)
        for _ in range(_nrandom):
            self.testRndTrip(B, _rnd(random() * N_S + S),
                                _rnd(random() * E_W + W))

#   def testRDs(self, B):
#       self.test('_RD', _RD.toStr(), '_region4=RD region (latS=50.0, ', known=startswith, nl=1)
#       self.test('_RD0', A0.toStr(), "D0=Datum(name='Bessel1841', ", known=startswith, nl=1)
#
#       # B = RDNAP2018v1(name='Cover')
#       self.test('str', B, "name='v", known=startswith,nl=1)
#       t = B.forward(A0.LAT0, A0.LON0)
#       self.test('lat', t.lat, A0.LAT0, prec=8)
#       self.test('lon', t.lon, A0.LON0, prec=8)
#       self.test('latlon', t.latlon, '(52.156161, 5.387639)')
#       self.test('latlonheight', t.latlonheight, '(52.156161, 5.387639, 0)')
#       self.test('latlonheightdatum', t.latlonheightdatum, '(52.156161, 5.387639, 0, Datum', known=startswith)
#       self.test('lam', t.lam, A0.LAM0, prec=8)
#       self.test('phi', t.phi, A0.PHI0, prec=8)
#       self.test('philam', t.philam, '(0.910297, 0.094032)')
#       self.test('philamheight', t.philamheight, '(0.910297, 0.094032, 0)')
#       self.test('philamheightdatum', t.philamheightdatum, '(0.910297, 0.094032, 0, Datum', known=startswith, nt=1)
#
#       try:
#           r = B.rdNAPh(0, 0)  # raiser=True
#           self.test('rdNAPh', r, NAN)  # RDNAPError
#       except RDNAPError as r:
#           r = repr(r)
#           self.test('rdNAPh', r, NAN)
#
#       r = t.toETRS().toRepr()
#       self.test('toETRS', r, t.toRepr(), nl=1)
#       r = t.toRD()
#       s = r.toRepr()
#       self.test('toRD', s, s)
#       r = t.toDatum(r.datum).toRepr()
#       self.test('toDatum', r, r, nt=1)
#
#       r = B.region4()
#       t = r.toRepr()
#       self.test('region4', t, 'RD region (latS=50.0, lonW=2.0, latN=56.0, lonE=8.0)')
#       self.test('lowerleft', B.isinside(r.latS, r.lonW), True)
#       self.test('upperight', B.isinside(r.latN, r.lonE), True)
#       self.test('center',    B.isinside(r.latC, r.lonC), True)
#       self.test('origin',    B.isinside(0, 0), False)
#
#       r = B.region4(asRD=True)
#       t = r.toRepr()
#       self.test('region4RD', t, 'RD region (minRDx=-87', known=startswith)
#       t = B.reverse(r.minRDx, r.minRDy, None)
#       self.test('lowerleft', B.isinside(t.lat, t.lon), True)
#       self.test('lowerleft', B.isinsideRD(r.minRDx, r.minRDy), True)
#       t = B.reverse(r.maxRDx, r.maxRDy, None)
#       self.test('upperight', B.isinside(t.lat, t.lon), True)
#       self.test('upperight', B.isinsideRD(r.maxRDx, r.maxRDy), True)
#       self.test('origin',    B.isinside(0, 0), False)
#
#       for t in (B.forward(NAN, NAN),
#                 B.reverse(NAN, NAN)):
#           self.test('lat', t.lat, NAN, prec=8, nl=1)
#           self.test('lon', t.lon, NAN, prec=8)
#           self.test('latlon', t.latlon, '(NAN, NAN)')
#           self.test('latlonheight', t.latlonheight, '(NAN, NAN, ', known=startswith)
#           self.test('latlonheightdatum', t.latlonheightdatum, '(NAN, NAN, ', known=startswith)
#           self.test('lam', t.lam, NAN, prec=8)
#           self.test('phi', t.phi, NAN, prec=8)
#           self.test('philam', t.philam, '(NAN, NAN)')
#           self.test('philamheight', t.philamheight, '(NAN, NAN, ', known=startswith)
#           self.test('philamheightdatum', t.philamheightdatum, '(NAN, NAN, ', known=startswith, nt=1)

    def testRD11(self, B):  # <https://NL.WikiPedia.org/wiki/Rijksdriehoekscoördinaten>
        t = repr(B)
        self.test('RD11 Be', t, 'Be08LBG', known=startswith, nl=1)
        for x, y, lat, lon in (  # easting    northing        lat           lon         # near
                               (703388.884, 982718.346, "53 38 48.2N", "5 10 31.9E"),   # 30 km N  Terschelling
                               (662749.076, 953104.396, "53 23  0.6N", "4 33 38.4E"),   # 30 km  W Terschelling
                               (644154.890, 852744.282, "52 28 57.3N", "4 16 59.2E"),   # 20 km  W IJmuiden  inside!
                               (558691.272, 743476.005, "51 29 37.3N", "3  3 15.1E"),   # 20 km  W Westkapelle  inside
                               (559495.836, 687489.129, "50 59 26.4N", "3  4 46.8E"),   # 10 km NE Roeselare  inside
                               (667471.630, 689017.929, "51  0 39.9N", "4 37  3.9E"),   # 25 km NE Brussel  inside
                               (728113.308, 642862.589, "50 35 28.1N", "5 28 18.9E"),   # 10 km SW Luik  inside
                               (786098.956, 643658.989, "50 35 15.4N", "6 17 27.1E"),   # 25 km SE Aken  inside
                               (864908.076, 806739.099, "52  1 42.1N", "7 30  0.8E"),   # 10 km NW Münster
                               (862781.133, 969832.846, "53 29 32.4N", "7 34 19.3E"),   # 05 km NE Aurich
                               (821539.487, 984316.051, "53 38 12.0N", "6 57 34.1E")):  # 05 km Z  Juist
            r = BeLBG7Tuple(x, y, NAN, lat, lon, NAN, None).toUnits()
            t = B.forward(lat, lon, 0).dup(beLBG=None)  # ignore beLBG
            e = max(fabs(t.easting  - r.easting),
                    fabs(t.northing - r.northing))
            self.test('forward', t, r, error=e, known=e < 0.0007)
            self.test('hBGh', B.hBGh(lat, lon), t.N, known=_isNAN(t.N))
            t = B.reverse(x, y, NAN).dup(beLBG=None)  # ignore beLBG
            e = max(fabs(t.lat - r.lat),
                    fabs(t.lon - r.lon))
            self.test('reverse', t, r, error=e, known=e < 1e-10)
            self.test('hBGh3.N', B.hBGh3(x, y).N, t.N, known=_isNAN(t.N))

    def testRndTrip(self, B, lat, lon, h=NAN, eas_nor=None):
        llh = lat, lon, h
        f =  B.forward(*llh)
        s = _str(f)  # partial
        self.test('forward', s, s)
        if eas_nor:
            k = f.H is NAN or type(B) is not Be08LBG
            self.test('eas_nor', _str(f.eastingnorthing), eas_nor, known=k)

        r =  B.reverse(*f.eastingnorthingHeight)
        s = _str(r)
        self.test('reverse', s, s)

        t  = _rnd(r.lat), _rnd(r.lon)
        t += (NAN if h is NAN else (_rnd(r.height) or 0.0)),
        d  = max(fabs(f - r) for f, r in zip(llh, t))
        k  = d < 0.002 or r.lat is NAN or r.lon is NAN
        self.test(B.name, t, llh, known=k, error=d)

        f = B.forward(lat, lon)
        r = B.reverse(f.easting, f.northing)
        k = f.H is NAN or r.lat is NAN or r.lon is NAN
        t = _rnd(lat),   _rnd(lon)
        r = _rnd(r.lat), _rnd(r.lon)
        self.test('rounded', r, t, known=k, nt=1)

    def testUccle_(self, B):
        u = B.Uccle.toUnits()
        self.test('Uccle_', u.name, 'Uccle', nl=1)
        self.testRndTrip(B, u.lat, u.lon, 0)
        self.testRndTrip(B, u.lat, u.lon, u.height)
        self.testRndTrip(B, u.lat, u.lon, u.H)

        for a, x in (('beLBG', 'Be'),
                     ('datum', 'Datum'),
                     ('easting', 'easting'),
                     ('eastingnorthing', 'Uccle'),
                     ('eastingnorthingHeight', 'Uccle'),
                     ('H', 'H'),
                     ('height', 'height'),
                     ('lam', 'lon'),  # lam?
                     ('lat', 'lat'),
                     ('latlon', 'Uccle'),
                     ('latlonheight', 'Uccle'),
                     ('latlonheightdatum', 'Uccle'),
                     ('latlonNgeoid', 'Uccle'),
                     ('N', 'N'),
                     ('northing', 'northing'),
                     ('phi', 'lat'),  # phi?
                     ('philam', 'Uccle'),
                     ('philamheight', 'Uccle'),
                     ('philamheightdatum', 'Uccle')):
            t = getattr(u, a, None)
            self.test(a, t.toRepr(), x, known=startswith)


if __name__ == '__main__':

    t = Tests(__file__, __version__)
    for B in (Be72LBG, Be72NLBG, Be72RLBG, Be50LBG, Be08LBG):
        B = B(name=typename(B))
        t.testBe_LBG(B)
        t.testRandom(B)
        t.testUccle_(B)

    b = B._bounds4BeNeLux.toRepr()  # Be08LBG
    t.test(B.name, b, b, nl=1)

    t.testRD11(B)  # Be08LBG
    t.testRD11(Be08LBG(datum=Datums.WGS84, name='BeWGS84'))

#   t.testRDs(B)

    t.results()
    t.exit()
