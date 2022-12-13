#!/usr/bin/env python
import numpy as np
import pandas as pd

__author__ = "Demetris Chrysostomou"
__credits__ = ["Demetris Chrysostomou", "Jose Luis Rueda Torres", "Jochen Lorenz Cremer"]
__version__ = "1.0.0"
__maintainer__ = "Demetris Chrysostomou"
__email__ = "D.Chrysostomou@tudelft.nl"
__status__ = "Production"


def check_line_current_limits(net, upper_limit=100):
    """ Check if the power flow result on the network caused respects the loading limitations in all lines

    :param net: network model [PandaPower Network]
    :param upper_limit: upper loading percentage limit [int/float]
    :return: True/False if the loading of any line exceeds the upper limit
    """
    return all(upper_limit >= abs(x) for x in net.res_line['loading_percent'])


def check_trafo_current_limits(net, upper_limit=100):
    """ Check if the power flow result on the network caused respects the loading limitations in all transformers

    :param net: network model [PandaPower Network]
    :param upper_limit: upper loading percentage limit [int/float]
    :return: True/False if the loading of any line exceeds the upper limit
    """
    return all(upper_limit >= abs(x) for x in net.res_trafo['loading_percent'])


def check_voltage_limits(voltages, upper_limit, lower_limit):
    """ Check if the power flow result on the network caused respects the loading limitations in all lines

    :param voltages: list of component voltages to be evaluated [list of floats]
    :param upper_limit: upper voltage percentage limit [float]
    :param lower_limit: lower voltage percentage limit [float]
    :return: True/False if the voltage of any component exceeds the upper limit, or is lower than the lower limit
    """
    return all(upper_limit >= x >= lower_limit for x in voltages)


def update_pqs(net, flex_wt=None, flex_pv=None, profile=None,  scale_w=1, scale_pv=1):
    """ Update network DG FSP P,Q based on the input values

    :param net: network model, [PandaPower network]
    :param flex_wt: Indices of flexible wind turbines, [list of int]
    :param flex_pv: Indices of flexible pv, [list of int]
    :param profile: P,Q values for each FSP for one iteration on the Monte Carlo algorithm
    [list of (FSPs) list of (P,Q) floats]
    :param scale_w: If a network with different wt penetration is used, this parameter will scale the wt accordingly,
    (default=1, no scaling), [int/float]
    :param scale_pv: If a network with different pv penetration is used, this parameter will scale the pv accordingly,
    (default=1, no scaling), [int/float]
    :return: updated network model [PandaPower network]
    """
    if profile:
        for i in range(0, len(profile)):
            if i == len(net.sgen)-1:
                scale = scale_w
            else:
                scale = scale_pv
            # only update sgen which are fsp
            if i in flex_pv or i in flex_wt:
                net.sgen['p_mw'][i] = profile[i][0]*scale
                net.sgen['q_mvar'][i] = profile[i][1]*scale
            else:
                net.sgen['p_mw'][i] = net.sgen['p_mw'][i]*scale
                net.sgen['q_mvar'][i] = net.sgen['p_mw'][i]*scale
    else:
        for i in range(0, len(net.sgen)):
            if i == len(net.sgen)-1:
                scale = scale_w
            else:
                scale = scale_pv
            net.sgen['p_mw'][i] = net.sgen['p_mw'][i]*scale
            net.sgen['q_mvar'][i] = net.sgen['q_mvar'][i]*scale
    return net


def get_input_busses_pq(net, input_buses):
    """ Get P and Q of all bus indices in {input_buses} list

    :param net: network model, [PandaPower network]
    :param input_buses: bus indices whose P,Q values are needed, [list of int]
    :return: p= list of P of busses of interest, q= list of Q of busses of interest
    """
    p = []
    q = []
    for bus in net.res_bus.iterrows():
        if bus[0] in input_buses:
            p.append(bus[1]['p_mw'])
            q.append(bus[1]['q_mvar'])
    return p, q


def get_input_busses_v(net, input_buses):
    """Get voltage magnitude |v| and angle θ of all bus indices in {input_buses} list

    :param net: network model, [PandaPower network]
    :param input_buses: bus indices whose |v|, θ values are needed, [list of int]
    :return: p= list of |v| of busses of interest, q= list of θ of busses of interest
    """
    p = []
    q = []
    for bus in net.res_bus.iterrows():
        if bus[0] in input_buses:
            p.append(bus[1]['vm_pu'])
            q.append(bus[1]['va_degree'])
    return p, q


def get_input_lines_pq(net, input_lines):
    """Get P and Q of all line indices in {input_lines} list

    :param net: network model, [PandaPower network]
    :param input_buses: line indices whose P,Q values are needed, [list of int]
    :return: p= list of P of lines of interest, q= list of Q of lines of interest
    """
    p = []
    q = []
    for line in net.res_line.iterrows():
        if line[0] in input_lines:
            p.append(line[1]['p_from_mw'])
            q.append(line[1]['q_from_mvar'])
    return p, q


def update_pqs_wl(net, flex_wt=None, flex_pv=None, profile=None, scale_w=1., scale_pv=1., load_ind=[]):
    """Update network FSP P,Q including loads based on the input values

    :param net: network model, [PandaPower network]
    :param flex_wt: Indices of flexible wind turbines, [list of int]
    :param flex_pv: Indices of flexible pv, [list of int]
    :param profile: P,Q values for each FSP for one iteration on the Monte Carlo algorithm
    [list of (FSPs) list of (P,Q) floats]
    :param scale_w: If a network with different wt penetration is used, this parameter will scale the wt accordingly,
    (default=1, no scaling), [int/float]
    :param scale_pv: If a network with different pv penetration is used, this parameter will scale the pv accordingly,
    (default=1, no scaling), [int/float]
    :return: updated network model [PandaPower network]
    :param load_ind: indices of flexible loads [list on int]
    :return: net=updated network model [PandaPower network]
    """
    if profile:
        for i in range(0, len(profile)):
            if i < len(net.sgen):
                if i == len(net.sgen)-1:
                    scale = scale_w
                else:
                    scale = scale_pv
                if i in flex_pv or i in flex_wt:
                    net.sgen['p_mw'][i] = profile[i][0] * scale
                    net.sgen['q_mvar'][i] = profile[i][1] * scale
                else:
                    net.sgen['p_mw'][i] = net.sgen['p_mw'][i] * scale
                    net.sgen['q_mvar'][i] = net.sgen['p_mw'][i] * scale
            else:
                j = load_ind[i-len(net.sgen)]
                net.load['p_mw'][j] = profile[i][0]
                net.load['q_mvar'][j] = profile[i][1]
    else:
        for i in range(0, len(net.sgen)):
            if i == len(net.sgen)-1:
                scale = scale_w
            else:
                scale = scale_pv
            net.sgen['p_mw'][i] = net.sgen['p_mw'][i]*scale
            net.sgen['q_mvar'][i] = net.sgen['q_mvar'][i]*scale
    return net


def write_result(x_flexible, x_non_flexible, y_flexible, y_non_flexible, name):
    """ Sve Monte Carlo simulation result on the csv_results folder
    :param x_flexible: feasible P, [list of floats]
    :param x_non_flexible: infeasible P, [list of floats]
    :param y_flexible: feasible Q, [list of floats]
    :param y_non_flexible: infeasible Q, [list of floats]
    :param name: name to be used in filename, [str]
    """
    max_len = max(len(x_flexible), len(x_non_flexible))
    x_flexible_df = np.zeros(max_len)
    x_non_flexible_df = np.zeros(max_len)
    y_flexible_df = np.zeros(max_len)
    y_non_flexible_df = np.zeros(max_len)
    for i in range(0, len(x_flexible)):
        x_flexible_df[i] = float(x_flexible[i])
        y_flexible_df[i] = float(y_flexible[i])
    for i in range(0, len(x_non_flexible)):
        x_non_flexible_df[i] = float(x_non_flexible[i])
        y_non_flexible_df[i] = float(y_non_flexible[i])
    df = pd.DataFrame(list(zip(x_flexible_df, y_flexible_df, x_non_flexible_df, y_non_flexible_df)),
                      columns=['x flex', 'y flex', 'x non-flex', 'y non-flex'])
    df.to_csv(f'csv_results/Flexibility_area_{name}')
    return


def report_pf_results(net, settings):
    """ Get effects from USS/TSS scenarios on initial network configuration

    :param net: network model [PandaPower network]
    :param settings: json file input data [Object]
    :return: p_obs=list of P from observable buses, q_obs=list of Q from observable buses,
             v_obs=list of |v| from observable buses, d_obs=list of Θ from observable buses,
             p_line_obs=list of P from observable lines, q_line_obs=list of Q from observable lines,
             p_non_obs=list of P from unobservable buses, q_non_obs=list of Q from unobservable buses,
             v_non_obs=list of |v| from unobservable buses, d_non_obs=list of Θ from unobservable buses,
             p_line_non_obs=list of P from unobservable lines, q_line_non_obs=list of Q from unobservable lines
    """
    p_obs, q_obs = get_input_busses_pq(net, input_buses=settings.observ_buses)
    v_obs, d_obs = get_input_busses_v(net, input_buses=settings.observ_buses)
    p_line_obs, q_line_obs = get_input_lines_pq(net, input_lines=settings.observ_lines)

    p_non_obs, q_non_obs = get_input_busses_pq(net, input_buses=settings.non_observ_buses)
    v_non_obs, d_non_obs = get_input_busses_v(net, input_buses=settings.non_observ_buses)
    p_line_non_obs, q_line_non_obs = get_input_lines_pq(net, input_lines=settings.non_observ_lines)
    return [p_obs, q_obs, v_obs, d_obs, p_line_obs, q_line_obs, p_non_obs, q_non_obs, v_non_obs,
            d_non_obs, p_line_non_obs, q_line_non_obs]


def print_scenario_shift_pf_results(pcc_operating_point, new_op, unaltered_net_results, altered_net_results,
                                    obs_b, nobs_b, obs_l, nobs_l, scenario_type):
    """ Report effects from USS/TSS scenarios on initial network configuration (Incl Table 1 information from publ.)

    :param pcc_operating_point: unaltered network PCC P,Q, [list of floats]
    :param new_op: altered network PCC P,Q, [list of floats]
    :param unaltered_net_results: unaltered network observable and unobservable bus P,Q,|v|,Θ and line P,Q
    [list of list of floats]
    :param altered_net_results: altered network observable and unobservable bus P,Q,|v|,Θ and line P,Q
    [list of list of floats]
    :param obs_b: observable buses indices, [list of int]
    :param nobs_b: unobservable buses indices, [list of int]
    :param obs_l: observable lines indices, [list of int]
    :param nobs_l: unobservable lines indices, [list of int]
    """

    if new_op != []:
        print("---------------------------------------------------------------------------------------")
        print(f"|Scenario {scenario_type['name']} {scenario_type['no.']} PCC P={float(new_op[0])} [MW], and Q={float(new_op[1])}[MVAR]|")
        print("---------------------------------------------------------------------------------------")

        cols_v = ['Component |', 'Δ|v| %', r'Δθ %']
        rows_v = ['Obs. ' + str(x) + ' |' for x in obs_b] + ['Non-Obs. ' + str(x) + ' |' for x in nobs_b]
        cols_p = ['Component |', 'ΔP %', 'ΔQ %']
        rows_p = ['PCC' + ' |'] + ['Obs. ' + str(x) + ' |' for x in obs_l] + ['Non-Obs. ' + str(x) + ' |' for x in nobs_l]
        subtext = r'where |v| is the voltage magnitude, θ is the voltage angle, ' \
                  r'P is the active power, and Q the reactive power.'
        data_v = [[], []]
        for idx, val in enumerate(unaltered_net_results[2]):
            data_v[0].append(round(100*(altered_net_results[2][idx] - val) / val, 3))
        for idx, val in enumerate(unaltered_net_results[3]):
            data_v[1].append(round(100*(altered_net_results[3][idx] - val) / val, 3))

        for idx, val in enumerate(unaltered_net_results[8]):
            data_v[0].append(round(100*(altered_net_results[8][idx] - val) / val, 3))
        for idx, val in enumerate(unaltered_net_results[9]):
            data_v[1].append(round(100*(altered_net_results[9][idx] - val) / val, 3))
        data_v = np.transpose(np.array(data_v)).tolist()
        data_p = [[float(round(100*(new_op[0] - pcc_operating_point[0]) / pcc_operating_point[0], 3))],
                  [float(round(100*(new_op[1] - pcc_operating_point[1]) / pcc_operating_point[1], 3))]]
        for idx, val in enumerate(unaltered_net_results[4]):
            data_p[0].append(round(100*(altered_net_results[4][idx] - val) / val, 3))
        for idx, val in enumerate(unaltered_net_results[5]):
            data_p[1].append(round(100*(altered_net_results[5][idx] - val) / val, 3))
        for idx, val in enumerate(unaltered_net_results[10]):
            data_p[0].append(round(100*(altered_net_results[10][idx] - val) / val, 3))
        for idx, val in enumerate(unaltered_net_results[11]):
            data_p[1].append(round(100*(altered_net_results[11][idx] - val) / val, 3))
        data_p = np.transpose(np.array(data_p)).tolist()
        format_row_v = "{:>20}" * (len(cols_v))
        print("\n---------------------------------------------------------------------------------------")
        print(format_row_v.format(*cols_v))
        print("---------------------------------------------------------------------------------------")
        for name, row in zip(rows_v, data_v):
            print(format_row_v.format(name, *row))
        print("---------------------------------------------------------------------------------------")
        format_row_p = "{:>20}" * (len(cols_p))
        print("\n---------------------------------------------------------------------------------------")
        print(format_row_p.format(*cols_p))
        print("---------------------------------------------------------------------------------------")
        for name, row in zip(rows_p, data_p):
            print(format_row_p.format(name, *row))
        print("---------------------------------------------------------------------------------------")
        print(subtext)
    else:
        print("---------------------------------------------------------------------------------------")
        print('Observable components:\n')
        print(f"Operating point (p,q) of unaltered network {pcc_operating_point}")
        print(f"Observable bus voltage magnitudes of unaltered network {unaltered_net_results[2]}")
        print(f"Observable bus voltage angles of unaltered network {unaltered_net_results[3]}")
        print(f"Observable lines active powers of unaltered network {unaltered_net_results[4]}")
        print(f"Observable lines reactive powers of unaltered network {unaltered_net_results[5]}\n\n")
        print('Non observable components:\n')
        print(f"Non-observable bus voltage magnitudes of unaltered network {unaltered_net_results[8]}")
        print(f"Non-observable bus voltage angles of unaltered network {unaltered_net_results[9]}")
        print(f"Non-observable lines active powers of unaltered network {unaltered_net_results[10]}")
        print(f"Non-observable lines reactive powers of unaltered network {unaltered_net_results[11]}\n\n")
        print("---------------------------------------------------------------------------------------")
    return


def return_hull_areas(hull_dict):
    """ Report convex hull areas difference from n scenarios (Incl Table 2 information from publ.)

    :param hull_dict: dictionary with convex hull area value for each scenario, [dict]
    """
    print("---------------------------------------------------------------------------------------")
    print("Hull Areas Per Scenario")
    print("---------------------------------------------------------------------------------------")
    scenarios = []
    values = []
    base = 0.
    for key in hull_dict:
        scenarios.append(key)
        values.append(hull_dict[key])
        if key in ['Normal Model', 'Initial Model', 'Unaltered Model']:
            base = hull_dict[key]
    if base != 0.:
        diff = [100*(val-base)/base for val in values]
        data = [values, diff]
        columns = ['Area [MW MVAR]', 'Difference [%]']
    else:
        data = [values]
        columns = ['Area [MW MVAR]']
    data = np.transpose(np.array(data)).tolist()
    format_row = "{:>25}" * (len(columns) + 1)
    print(format_row.format("", *columns))
    for name, row in zip(scenarios, data):
        print(format_row.format(name, *row))
    print("---------------------------------------------------------------------------------------")
    return

