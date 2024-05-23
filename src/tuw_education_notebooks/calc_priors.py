import xarray as xr
import numpy as np
import datetime
from scipy.stats import norm
import matplotlib.pyplot as plt

RANGE = np.arange(-30, 0, 0.1)

sig0_dc = xr.open_dataset('data/s1_parameters/S1_CSAR_IWGRDH/SIG0/V1M1R1/EQUI7_EU020M/E054N006T3/SIG0_20180228T043908__VV_D080_E054N006T3_EU020M_V1M1R1_S1AIWGRDH_TUWIEN.nc')
hparam_dc = xr.open_dataset('data/tuw_s1_harpar/S1_CSAR_IWGRDH/SIG0-HPAR/V0M2R3/EQUI7_EU020M/E054N006T3/D080.nc')
plia_dc = xr.open_dataset('data/s1_parameters/S1_CSAR_IWGRDH/PLIA-TAG/V01R03/EQUI7_EU020M/E054N006T3/PLIA-TAG-MEAN_20200101T000000_20201231T235959__D080_E054N006T3_EU020M_V01R03_S1IWGRDH.nc')
sig0_dc['id'] = (('y', 'x'), np.arange(sig0_dc.SIG0.size).reshape(sig0_dc.SIG0.shape))
hparam_dc['id'] = (('y', 'x'), np.arange(sig0_dc.SIG0.size).reshape(sig0_dc.SIG0.shape))
plia_dc['id'] = (('y', 'x'), np.arange(sig0_dc.SIG0.size).reshape(sig0_dc.SIG0.shape))

def calc_water_prior(id, x=RANGE):
    point = plia_dc.where(plia_dc.id == id, drop=True)
    wbsc_mean = point.PLIA * -0.394181 + -4.142015
    wbsc_std = 2.754041
    return norm.pdf(x, wbsc_mean.to_numpy(), wbsc_std).flatten()

def expected_land_backscatter(data, dtime_str):
    w = np.pi * 2 / 365
    dt = datetime.datetime.strptime(dtime_str, "%Y-%m-%d")
    t = dt.timetuple().tm_yday
    wt = w * t

    M0 = data.M0
    S1 = data.S1
    S2 = data.S2
    S3 = data.S3
    C1 = data.C1
    C2 = data.C2
    C3 = data.C3
    hm_c1 = (M0 + S1 * np.sin(wt)) + (C1 * np.cos(wt))
    hm_c2 = ((hm_c1 + S2 * np.sin(2 * wt)) + C2 * np.cos(2 * wt))
    hm_c3 = ((hm_c2 + S3 * np.sin(3 * wt)) + C3 * np.cos(3 * wt))
    return hm_c3

def calc_land_prior(id, x=RANGE):
    point = hparam_dc.where(hparam_dc.id == id, drop=True)
    lbsc_mean = expected_land_backscatter(point, '2018-02-01')
    lbsc_std = point.STD
    return norm.pdf(x, lbsc_mean.to_numpy(), lbsc_std.to_numpy()).flatten()

def plot_priors(id, sig0_dc, water_prior, land_prior):
    point = sig0_dc.where(sig0_dc.id == id, drop=True).SIG0.to_numpy()
    y1_pdf, y2_pdf = water_prior, land_prior
    fig, ax = plt.subplots(1, 1)
    ax.plot(RANGE, y1_pdf, 'k-', lw=2)
    ax.vlines(x=point, ymin=0, ymax=np.max((y1_pdf, y2_pdf)), lw=3)
    ax.plot(RANGE, y2_pdf,'r-', lw=5, alpha=0.6)

def calc_priors(id, x=RANGE, plot=False):
    water_prior, land_prior = calc_water_prior(id=id, x=x), calc_land_prior(id=id, x=x)
    if plot:
        plot_priors(id, sig0_dc, water_prior, land_prior)
    return water_prior, land_prior

def plot_posteriors(id, f_post, nf_post):
    point = sig0_dc.where(sig0_dc.id == id, drop=True).SIG0.to_numpy()
    fig, ax = plt.subplots(1, 1)
    ax.plot(RANGE, f_post, 'k-', lw=2)
    ax.vlines(x=point, ymin=-0.1, ymax=1.1, lw=3)
    ax.plot(RANGE, nf_post,'r-', lw=5, alpha=0.6)
