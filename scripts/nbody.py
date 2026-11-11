"""N-body sky for epochs beyond the JPL ephemerides (REBOUND, WHFast symplectic integrator).

Sun + Mercury..Pluto barycentres (Earth-Moon barycentre as one body), initial state from
JPL DE440s at J2000 TDB, GM values from DE440. Units: AU, day, solar mass.
General relativity is not modelled; it matters only for Mercury (perihelion advance of
42.98"/century), which is corrected afterwards by rotating Mercury's perihelion.
"""
import os
from pathlib import Path

import numpy as np
import rebound
from jplephem.spk import SPK

# JPL DE440s (32 MB, https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp):
# set DE440S_BSP, or put the file in <project>/ephemeris/.
DE440S = Path(os.environ.get("DE440S_BSP", Path(__file__).resolve().parents[1] / "ephemeris" / "de440s.bsp"))
AU_KM = 149_597_870.7
JD_J2000 = 2451545.0
GAUSS_K = 0.01720209895
# GM (km^3/s^2), JPL DE440 (Park et al. 2021)
GM = {"sun": 132712440041.279419, "mercury": 22031.868551, "venus": 324858.592000,
      "emb": 403503.235625, "mars": 42828.375816, "jupiter": 126712764.100000, "saturn": 37940584.841800,
      "uranus": 5794556.400000, "neptune": 6836527.100580, "pluto": 975.500000}
SEG = {"sun": 10, "mercury": 1, "venus": 2, "emb": 3, "mars": 4, "jupiter": 5, "saturn": 6, "uranus": 7,
       "neptune": 8, "pluto": 9}
ORDER = ["sun", "mercury", "venus", "emb", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
OBLIQUITY_J2000 = np.radians(84381.406 / 3600.0)
GR_MERCURY_ARCSEC_PER_CY = 42.98


def build_sim(dt_days=2.0):
    kernel = SPK.open(str(DE440S))
    sim = rebound.Simulation()
    sim.G = GAUSS_K ** 2
    sim.integrator = "whfast"
    sim.integrator.safe_mode = 0     # REBOUND 5: integrator fields live on sim.integrator
    sim.integrator.corrector = 11    # 11th-order symplectic corrector
    for name in ORDER:
        pos, vel = kernel[0, SEG[name]].compute_and_differentiate(JD_J2000)  # km, km/day
        sim.add(m=GM[name] / GM["sun"], x=pos[0] / AU_KM, y=pos[1] / AU_KM, z=pos[2] / AU_KM,
                vx=vel[0] / AU_KM, vy=vel[1] / AU_KM, vz=vel[2] / AU_KM)
    kernel.close()
    sim.move_to_com()
    sim.dt = dt_days
    sim.t = 0.0  # days from J2000
    return sim


def state(sim):
    xyz = np.zeros((sim.N, 3))
    vxyz = np.zeros((sim.N, 3))
    sim.serialize_particle_data(xyz=xyz, vxvyvz=vxyz)
    return xyz, vxyz


def ecliptic_pole(xyz, vxyz):
    """Pole of the Earth-Moon barycentre's heliocentric orbit (the ecliptic of date), ICRF axes."""
    r = xyz[3] - xyz[0]
    v = vxyz[3] - vxyz[0]
    h = np.cross(r, v)
    return h / np.linalg.norm(h)


def mercury_gr_correction(xyz, vxyz, days_from_j2000):
    """Rotate Mercury's heliocentric position about its orbit normal by the GR perihelion advance it lacks.

    Going back in time the true perihelion lies further back by 42.98"/cy; the mean longitude is
    kept, so the planet moves with its ellipse (first-order change in the equation of centre)."""
    r = xyz[1] - xyz[0]
    v = vxyz[1] - vxyz[0]
    mu = GAUSS_K ** 2 * (1 + GM["mercury"] / GM["sun"])
    h = np.cross(r, v)
    hn = h / np.linalg.norm(h)
    evec = np.cross(v, h) / mu - r / np.linalg.norm(r)
    e = np.linalg.norm(evec)
    dpi = np.radians(GR_MERCURY_ARCSEC_PER_CY / 3600.0 * days_from_j2000 / 36525.0)
    # change of true anomaly when the perihelion shifts by dpi at fixed mean longitude:
    # dnu ~ -dpi + d(equation of centre); first order: position angle shift = dpi * (1 - dnu/dM) ~ dpi*(1 - (1+e cos nu)^2/(1-e^2)^1.5)
    cosnu = np.dot(evec / e, r / np.linalg.norm(r))
    shift = dpi * (1 - (1 + e * cosnu) ** 2 / (1 - e ** 2) ** 1.5)
    c, s = np.cos(shift), np.sin(shift)
    rot = r * c + np.cross(hn, r) * s + hn * np.dot(hn, r) * (1 - c)
    out = xyz.copy()
    out[1] = xyz[0] + rot
    return out


def star_vector(ra_deg, dec_deg, pmra_mas, pmdec_mas, plx_mas, rv_kms, years_from_j2000):
    """Barycentric unit vector of a star after linear 3-D space motion (pc, km/s)."""
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    dist_pc = 1000.0 / plx_mas
    pos = dist_pc * np.array([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])
    # unit vectors: radial, east (ra), north (dec)
    rhat = pos / dist_pc
    ehat = np.array([-np.sin(ra), np.cos(ra), 0.0])
    nhat = np.array([-np.sin(dec) * np.cos(ra), -np.sin(dec) * np.sin(ra), np.cos(dec)])
    k = 4.740470446  # km/s per (arcsec/yr * pc)
    v_kms = rv_kms * rhat + k * dist_pc * (pmra_mas / 1000.0) * ehat + k * dist_pc * (pmdec_mas / 1000.0) * nhat
    pc_per_kms_yr = 1.0227121650537077e-06  # pc per (km/s * yr)
    new = pos + v_kms * pc_per_kms_yr * years_from_j2000
    return new / np.linalg.norm(new)


def lon_in_plane(vec, pole, ref):
    """Longitude (deg) of vec in the plane with normal `pole`, measured from direction `ref`."""
    def proj(a):
        a = a - np.dot(a, pole) * pole if a.ndim == 1 else a - np.outer(a @ pole, pole)
        return a
    x = proj(ref)
    x = x / np.linalg.norm(x)
    y = np.cross(pole, x)
    v = proj(vec)
    return np.degrees(np.arctan2(v @ y, v @ x)) % 360.0
