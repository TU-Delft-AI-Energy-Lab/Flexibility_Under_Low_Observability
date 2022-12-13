#!/usr/bin/env python
import pandapower.networks as pn
import numpy as np
import pandapower as pp
from utils import update_pqs

__author__ = "Demetris Chrysostomou"
__credits__ = ["Demetris Chrysostomou", "Jose Luis Rueda Torres", "Jochen Lorenz Cremer"]
__version__ = "1.0.0"
__maintainer__ = "Demetris Chrysostomou"
__email__ = "D.Chrysostomou@tudelft.nl"
__status__ = "Production"


def get_network(settings):
    """ Gen the network specified in settings. Currently, only "CIGRE MV" with der "pv_wind" is implemented

    :param settings: json file input data [Object]
    :return: network model [PandaPower Network]
    """
    if settings.net_name == 'CIGRE MV':
        return pn.create_cigre_network_mv(with_der="pv_wind")


def update_settings(settings):
    """ Update settings by changing observable and unobservable bus and line information based on the loaded network

    :param settings: settings: json file input data [Object]
    :return: settings= updated settings object [Object]
    """
    settings.net = get_network(settings)
    settings = get_observable_lines_buses(settings)
    settings = get_unobservable_lines_buses_indices(settings)
    settings = get_fsp(settings)
    return settings


def get_fsp(settings):
    """ Get indices of FSPs if any of them are specified as -1.
    This value , -1, is used to say 'I do not know the indices but all components of type x are assumed FSPs

    :param settings: settings: json file input data [Object]
    :return: settings= updated settings object [Object]
    """
    net = settings.net
    if settings.fsp_wt[0] == -1:
        settings.fsp_wt = [len(net.sgen)-1]
    if settings.fsp_pv[0] == -1:
        settings.fsp_pv = np.arange(0, len(net.sgen))
    if settings.fsp_load[0] == -1:
        settings.fsp_load = np.arange(0, len(net.load))
    return settings


def get_unobservable_lines_buses_indices(settings):
    """ Gen indices of network unobservable lines (all lines not specified as observable)

    :param settings: settings: json file input data [Object]
    :return: settings= updated settings object [Object]
    """
    net = settings.net
    u_line_indices = []
    for i in range(0, len(net.line)):
        if i not in settings.observ_lines:
            u_line_indices.append(i)
    u_bus_indices = []
    for i in range(0, len(net.bus)):
        if i not in settings.observ_buses:
            u_bus_indices.append(i)
    settings.non_observ_lines = u_line_indices
    settings.non_observ_buses = u_bus_indices
    return settings


def get_observable_lines_buses(settings):
    """ Get indices of observable lines and buses if any of them are specified as -1.
    This value , -1, is used to say 'I do not know the indices but all components of type x are assumed observable

    :param settings: settings: json file input data [Object]
    :return: settings= updated settings object [Object]
    """
    net = settings.net
    if settings.observ_lines[0] == -1:
        settings.observ_lines = np.arange(0, len(net.line))
    if settings.observ_buses[0] == -1:
        settings.observ_buses = np.arange(0, len(net.bus))
    return settings


def get_operating_point(settings):
    """ Get network PCC P,Q (y)

    :param settings: settings: json file input data [Object]
    :return: Network PCC P,Q (y) [list of floats]
    """
    net = get_network(settings)
    net = update_pqs(net, scale_pv=settings.scale_pv, scale_w=settings.scale_wt)  # scale DG generation times higher
    pp.runpp(net)
    return [net.res_ext_grid['p_mw'], net.res_ext_grid['q_mvar']]


def apply_uss(net, settings):
    """ Apply USS scenario shifts on the network

    :param net: Network model for scenario [PandaPower network]
    :param settings: settings: settings: json file input data [Object]
    :return: net= network updated for the USS# case, pq=network new PCC P,Q (y) [list of floats]
    """
    max_volt = settings.max_volt
    min_volt = settings.min_volt
    max_curr = settings.max_curr
    scenario = settings.scenario_type_dict['no.']
    p234 = [0.3, 1]
    p7 = [0.414, 0.045]
    p13 = [0.7275, 1.06]
    q7 = [0.276, 0.492]
    q13 = [0.3, 1]
    q14 = [0.3, 1.431]

    net.load['p_mw'][2] = net.load['p_mw'][2] - 0.43165
    net.load['p_mw'][3] = net.load['p_mw'][3] - 0.7275
    net.load['p_mw'][4] = net.load['p_mw'][4] - 0.54805
    net.load['p_mw'][14] = net.load['p_mw'][14] + 0.54805

    net.load['q_mvar'][2] = net.load['q_mvar'][2] - p234[scenario-1]
    net.load['q_mvar'][3] = net.load['q_mvar'][3] - p234[scenario-1]
    net.load['q_mvar'][4] = net.load['q_mvar'][4] - p234[scenario-1]
    net.load['p_mw'][7] = net.load['p_mw'][7] + p7[scenario-1]
    net.load['p_mw'][13] = net.load['p_mw'][13] + p13[scenario-1]
    net.load['q_mvar'][7] = net.load['q_mvar'][7] + q7[scenario-1]
    net.load['q_mvar'][13] = net.load['q_mvar'][13] + q13[scenario-1]
    net.load['q_mvar'][14] = net.load['q_mvar'][14] + q14[scenario-1]
    pp.runpp(net)
    return net, [net.res_ext_grid['p_mw'], net.res_ext_grid['q_mvar']]


def apply_tss(net, settings):
    """Apply TSS scenario shifts on the network

    :param net: Network model for scenario [PandaPower network]
    :param settings: settings: settings: json file input data [Object]
    :return: net= network updated for the TSS# case, pq=network new PCC P,Q (y) [list of floats]
    """
    max_volt = settings.max_volt
    min_volt = settings.min_volt
    max_curr = settings.max_curr
    scenario = settings.scenario_type_dict['no.']
    if scenario == 1:
        net.load['q_mvar'][11] = net.load['q_mvar'][11] - 0.067
        net.load['p_mw'][11] = net.load['p_mw'][11] - 0.031
        net.switch['closed'][2] = True
        net.switch['closed'][1] = True
        net.line['in_service'][6] = False  # 8 - 9
        net.line['in_service'][2] = False  # 3-4
    elif scenario == 2:
        net.load['q_mvar'][11] = net.load['q_mvar'][11] - 0.03
        net.switch['closed'][2] = True
        net.switch['closed'][1] = True
        net.line['in_service'][6] = False  # 8 - 9
        net.line['in_service'][4] = False  # 5-6
    elif scenario == 3:
        net.load['q_mvar'][11] = net.load['q_mvar'][11] + 1.111
        net.load['p_mw'][11] = net.load['p_mw'][11] + 2.14
        net.load['q_mvar'][7] = net.load['q_mvar'][7] - 1.115
        net.load['p_mw'][7] = net.load['p_mw'][7] - 2.13
        net.switch['closed'][2] = True
        net.switch['closed'][1] = True
        net.line['in_service'][9] = False  # 3 - 8
        net.line['in_service'][2] = False  # 3-4
        net.switch['closed'][4] = True
    pp.runpp(net)
    return net, [net.res_ext_grid['p_mw'], net.res_ext_grid['q_mvar']]


