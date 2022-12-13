#!/usr/bin/env python
import time
from utils import update_pqs, check_voltage_limits, check_line_current_limits, update_pqs_wl, check_trafo_current_limits
import pandapower as pp
from tqdm import tqdm

__author__ = "Demetris Chrysostomou"
__credits__ = ["Demetris Chrysostomou", "Jose Luis Rueda Torres", "Jochen Lorenz Cremer"]
__version__ = "1.0.0"
__maintainer__ = "Demetris Chrysostomou"
__email__ = "D.Chrysostomou@tudelft.nl"
__status__ = "Production"


def all_pf_simulations(settings, net, pq_profiles):
    """ main function running all power flow simulations based on which FSP types will be used

    :param settings: Information of the json file, [object]
    :param net: Network on which the simulations will be performed [PandaPower network]
    :param pq_profiles: P and Q values for each FSP for each iteration in the Monte Carlo simulation
    :return: feasible P, [list of floats], feasible Q, [list of floats], infeasible P, [list of floats],
    infeasible Q, [list of floats], duration of simulations, [s],
    New FSP PQ values for the feasible y, [list  of (iterations) list of (FSPs) list of (P,Q) floats],
    New FSP PQ values for the infeasible y, [list  of (iterations) list of (FSPs) list of (P,Q) floats]
    """
    if settings.fsps == 'DG only':
        return run_all_samples(settings, net, pq_profiles)
    elif settings.fsps == 'All' or settings.fsps == 'Load only':
        return run_all_samples_wl(settings, net, pq_profiles)
    else:
        assert False, 'Error: Choose FSPs from {All, Load only, DG only}'
    return


def run_all_samples(settings, net, pq_profiles):
    """ Run all power flows for scenarios where only DG are used as FSP

    :param settings: Information of the json file, [object]
    :param net: Network on which the simulations will be performed [PandaPower network]
    :param pq_profiles: P and Q values for each FSP for each iteration in the Monte Carlo simulation
    :return: feasible P, [list of floats], feasible Q, [list of floats], infeasible P, [list of floats],
    infeasible Q, [list of floats], duration of simulations, [s],
    New FSP PQ values for the feasible y, [list  of (iterations) list of (FSPs) list of (P,Q) floats],
    New FSP PQ values for the infeasible y, [list  of (iterations) list of (FSPs) list of (P,Q) floats]
    """
    max_curr = settings.max_curr
    max_volt = settings.max_volt
    min_volt = settings.min_volt
    fsp_pv = settings.fsp_pv
    fsp_wt = settings.fsp_wt
    x_flexible = []
    y_flexible = []
    x_non_flexible = []
    y_non_flexible = []
    t_start_run_mc_pf = time.time()
    prof_flexible = []
    prof_non_flexible = []
    for profile in tqdm(pq_profiles, desc="Power flows Completed:"):
        net = update_pqs(net, flex_wt=fsp_wt, flex_pv=fsp_pv, profile=profile)
        try:
            pp.runpp(net)
            pq_value = [net.res_ext_grid['p_mw'], net.res_ext_grid['q_mvar']]
            if check_voltage_limits(net.res_bus['vm_pu'], max_volt, min_volt) and \
                    check_line_current_limits(net, max_curr) and check_trafo_current_limits(net, max_curr):  # True -> Flexible, False -> Limit passed
                x_flexible.append(pq_value[0])
                y_flexible.append(pq_value[1])
                prof_flexible.append(profile)
            else:
                x_non_flexible.append(pq_value[0])
                y_non_flexible.append(pq_value[1])
                prof_non_flexible.append(profile)
        except:
            print(f"Power flow did not converge for profile {profile}")
    t_stop_run_mc_pf = time.time()
    print(f"{settings.no_samples} MC Power flows needed {t_stop_run_mc_pf - t_start_run_mc_pf} seconds")
    print(f"Pf run {len(y_flexible)+len(y_non_flexible)}")
    return x_flexible, y_flexible, x_non_flexible, y_non_flexible, t_stop_run_mc_pf - t_start_run_mc_pf, \
           prof_flexible, prof_non_flexible


def run_all_samples_wl(settings, net, pq_profiles):
    """ Run all power flows for scenarios where loads are included in the FSP

    :param settings: Information of the json file, [object]
    :param net: Network on which the simulations will be performed [PandaPower network]
    :param pq_profiles: P and Q values for each FSP for each iteration in the Monte Carlo simulation
    :return: feasible P, [list of floats], feasible Q, [list of floats], infeasible P, [list of floats],
    infeasible Q, [list of floats], duration of simulations, [s],
    New FSP PQ values for the feasible y, [list  of (iterations) list of (FSPs) list of (P,Q) floats],
    New FSP PQ values for the infeasible y, [list  of (iterations) list of (FSPs) list of (P,Q) floats]
    """
    fsp_pv = settings.fsp_pv
    fsp_wt = settings.fsp_wt
    fsp_load = settings.fsp_load
    max_curr = settings.max_curr
    max_volt = settings.max_volt
    min_volt = settings.min_volt

    x_flexible = []
    y_flexible = []
    x_non_flexible = []
    y_non_flexible = []
    t_start_run_mc_pf = time.time()
    prof_flexible = []
    prof_non_flexible = []
    for profile in tqdm(pq_profiles, desc="Power flows Completed:"):
        net = update_pqs_wl(net, flex_wt=fsp_wt, flex_pv=fsp_pv, profile=profile, load_ind=fsp_load)
        try:
            pp.runpp(net)
            pq_value = [net.res_ext_grid['p_mw'], net.res_ext_grid['q_mvar']]
            if check_voltage_limits(net.res_bus['vm_pu'], max_volt, min_volt) and \
                    check_line_current_limits(net, max_curr) and check_trafo_current_limits(net, max_curr):  # True -> Flexible, False -> Limit passed
                x_flexible.append(pq_value[0])
                y_flexible.append(pq_value[1])
                prof_flexible.append(profile)
            else:
                x_non_flexible.append(pq_value[0])
                y_non_flexible.append(pq_value[1])
                prof_non_flexible.append(profile)
        except:
            print(f"Power flow did not converge for profile {profile}")
    t_stop_run_mc_pf = time.time()
    print(f"{len(x_flexible)} flex non flex {len(x_non_flexible)}")

    print(f"{settings.no_samples} MC Power flows needed {t_stop_run_mc_pf - t_start_run_mc_pf} seconds")

    return x_flexible, y_flexible, x_non_flexible, y_non_flexible, t_stop_run_mc_pf - t_start_run_mc_pf, \
           prof_flexible, prof_non_flexible

