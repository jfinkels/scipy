"""
Test Scipy functions versus mpmath, if available.

"""
import numpy as np
from numpy.testing import *
from test_data import Data
import scipy.special as sc

try:
    import mpmath
except ImportError:
    try:
        import sympy.mpmath as mpmath
    except ImportError:
        mpmath = None

def mpmath_check(min_ver):
    if mpmath is None:
        return dec.skipif(True, "mpmath library is not present")

    def try_int(v):
        try: return int(v)
        except ValueError: return v

    def get_version(v):
        return map(try_int, v.split('.'))

    return dec.skipif(get_version(min_ver) > get_version(mpmath.__version__),
                      "mpmath %s required" % min_ver)


#------------------------------------------------------------------------------
# expi
#------------------------------------------------------------------------------

@mpmath_check('0.10')
def test_expi_complex():
    dataset = []
    for r in np.logspace(-99, 2, 10):
        for p in np.linspace(0, 2*np.pi, 30):
            z = r*np.exp(1j*p)
            dataset.append((z, mpmath.ei(z)))
    dataset = np.array(dataset, dtype=np.complex_)

    Data(sc.expi, dataset, 0, 1).check()


#------------------------------------------------------------------------------
# hyp2f1
#------------------------------------------------------------------------------

@mpmath_check('0.12')
@dec.knownfailureif(True,
                    "Currently, special.hyp2f1 uses a *different* convention from mpmath and Mathematica for the cases a=c or b=c negative integers")
def test_hyp2f1_strange_points():
    pts = [
        (2,-1,-1,3),
        (2,-2,-2,3),
    ]
    dataset = [p + (float(mpmath.hyp2f1(*p)),) for p in pts]
    dataset = np.array(dataset, dtype=np.float_)

    Data(sc.hyp2f1, dataset, (0,1,2,3), 4, rtol=1e-10).check()

@mpmath_check('0.13')
def test_hyp2f1_real_some_points():
    pts = [
        (1,2,3,0),
        (1./3, 2./3, 5./6, 27./32),
        (1./4, 1./2, 3./4, 80./81),
        (2,-2,-3,3),
        (2,-3,-2,3),
        (2,-1.5,-1.5,3),
        (1,2,3,0),
        (0.7235, -1, -5, 0.3),
        (0.25, 1./3, 2, 0.999),
        (0.25, 1./3, 2, -1),
        (2,3,5,0.99),
        (3./2,-0.5,3,0.99),
        (2,2.5,-3.25,0.999),
    ]
    dataset = [p + (float(mpmath.hyp2f1(*p)),) for p in pts]
    dataset = np.array(dataset, dtype=np.float_)

    Data(sc.hyp2f1, dataset, (0,1,2,3), 4, rtol=1e-10).check()

@mpmath_check('0.14')
def test_hyp2f1_some_points_2():
    # Taken from mpmath unit tests -- this point failed for mpmath 0.13 but
    # was fixed in their SVN since then
    pts = [
        (112, 51./10, -9./10, -0.99999),
    ]
    dataset = [p + (float(mpmath.hyp2f1(*p)),) for p in pts]
    dataset = np.array(dataset, dtype=np.float_)

    Data(sc.hyp2f1, dataset, (0,1,2,3), 4, rtol=1e-10).check()

@mpmath_check('0.13')
def test_hyp2f1_real_some():
    dataset = []
    for a in [-10, -5, -1.8, 1.8, 5, 10]:
        for b in [-2.5, -1, 1, 7.4]:
            for c in [-9, -1.8, 5, 20.4]:
                for z in [-10, -1.01, -0.99, 0, 0.6, 0.95, 1.5, 10]:
                    try:
                        v = float(mpmath.hyp2f1(a, b, c, z))
                    except (TypeError, mpmath.libhyper.NoConvergence):
                        continue
                    dataset.append((a, b, c, z, v))
    dataset = np.array(dataset, dtype=np.float_)
    Data(sc.hyp2f1, dataset, (0,1,2,3), 4, rtol=1e-9).check()

@mpmath_check('0.12')
@dec.slow
def test_hyp2f1_real_random():
    dataset = []

    npoints = 500
    dataset = np.zeros((npoints, 5), np.float_)

    np.random.seed(1234)
    dataset[:,0] = np.random.pareto(1.5, npoints)
    dataset[:,1] = np.random.pareto(1.5, npoints)
    dataset[:,2] = np.random.pareto(1.5, npoints)
    dataset[:,3] = 2*np.random.rand(npoints) - 1

    dataset[:,0] *= (-1)**np.random.randint(2, npoints)
    dataset[:,1] *= (-1)**np.random.randint(2, npoints)
    dataset[:,2] *= (-1)**np.random.randint(2, npoints)

    for ds in dataset:
        if mpmath.__version__ < '0.14':
            # mpmath < 0.14 fails for c too much smaller than a, b
            if abs(ds[:2]).max() > abs(ds[2]):
                ds[2] = abs(ds[:2]).max()
        ds[4] = float(mpmath.hyp2f1(*tuple(ds[:4])))

    Data(sc.hyp2f1, dataset, (0,1,2,3), 4, rtol=1e-9).check()
