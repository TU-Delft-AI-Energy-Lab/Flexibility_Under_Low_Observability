#!/usr/bin/env python
from monte_carlo import all_pf_simulations
from utils import report_pf_results, print_scenario_shift_pf_results, return_hull_areas, write_result
from plotting import plot_mc, plot_6_mc_flex_from_file, get_convex_hull_combination, get_multiplicity, get_convex_hull
from json_reader import SettingReader
from scenario_setup import update_settings, get_operating_point, apply_uss, apply_tss
from data_sampler import profile_creation
import pandapower as pp
import warnings
import sys

scenario_name = str(sys.argv[1])

__author__ = "Demetris Chrysostomou"
__credits__ = ["Demetris Chrysostomou", "Jose Luis Rueda Torres", "Jochen Lorenz Cremer"]
__version__ = "1.0.0"
__maintainer__ = "Demetris Chrysostomou"
__email__ = "D.Chrysostomou@tudelft.nl"
__status__ = "Production"

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=UserWarning)


if __name__ == "__main__":
    """ Main file running the scenario
    """
    # Read scenario and update it based on the input model
    settings = SettingReader(scenario_name=scenario_name)
    settings = update_settings(settings)
    net = settings.net
    # Run power flow on the initial model
    pp.runpp(net)
    operating_point = get_operating_point(settings)
    pcc_operating_point = operating_point

    # Read the initial unaltered network results
    unaltered_net_results = report_pf_results(net, settings)
    new_op = []
    # Update the network based on the scenario
    if settings.scenario_type_dict['name'] == 'USS':
        net, new_op = apply_uss(net, settings)
        pcc_operating_point = new_op
    elif settings.scenario_type_dict['name'] == 'TSS':
        net, new_op = apply_tss(net, settings)
        pcc_operating_point = new_op
    # Create the new PQ values which will be used in each power flow
    if settings.no_samples >= 2:
        pq_profiles, dur_samples = profile_creation(settings.no_samples, net, settings.distribution,
                                                    settings.keep_mp, services=settings.fsps,
                                                    flexible_loads=settings.fsp_load)
    # Get the altered network values for comparison
    altered_net_results = report_pf_results(net, settings)
    # Print the differences between the initial and the altered scenarios
    print_scenario_shift_pf_results(operating_point, new_op, unaltered_net_results, altered_net_results,
                                    settings.observ_buses, settings.non_observ_buses,
                                    settings.observ_lines, settings.non_observ_lines, settings.scenario_type_dict)
    # If Monte Carlo simulations will be run go here
    if settings.mc_sim:
        x_flx, y_flx, x_non_flx, y_non_flx, t_pf, prf_flx, prf_non_flx = all_pf_simulations(settings, net, pq_profiles)
        plot_mc(x_flx, y_flx, x_non_flx, y_non_flx, pcc_operating_point, settings.no_samples,
                settings.name, dur_samples, t_pf)
        write_result(x_flx, x_non_flx, y_flx, y_non_flx, settings.name.replace(" ", "_"))
    # If 6 scenarios' flexibility will be plot in one figure go here
    if settings.plot_settings_dict.get("plot_combination", False):
        plot_6_mc_flex_from_file(filenames=settings.plot_settings_dict.get("filenames"),
                                 legends=settings.plot_settings_dict.get("legends"),
                                 operating_point=settings.plot_settings_dict.get("operating_points"),
                                 name=settings.name.replace(" ", "_"),
                                 plot_type=settings.plot_settings_dict.get("output type"))
    # If the convex hull area of a scenarios will be plotted go here
    if settings.plot_settings_dict.get("convex_hull", False):
        # If 1 plot will include 6 areas
        if settings.plot_settings_dict.get("plot_combination", False):
            hull = get_convex_hull_combination(filenames=settings.plot_settings_dict.get("filenames"),
                                               legends=settings.plot_settings_dict.get("legends"),
                                               operating_point=settings.plot_settings_dict.get("operating_points"),
                                               name=settings.name.replace(" ", "_"),
                                               plot_type=settings.plot_settings_dict.get("output type"))
        else:
            # if n plots will include 1 area each
            hull = get_convex_hull(filenames=settings.plot_settings_dict.get("filenames"),
                                   legends=settings.plot_settings_dict.get("legends"),
                                   operating_point=settings.plot_settings_dict.get("operating_points"),
                                   name=settings.name.replace(" ", "_"),
                                   plot_type=settings.plot_settings_dict.get("output type"))
        return_hull_areas(hull)
    # If the multiplicity of a scenario will be plotted go here
    if settings.plot_settings_dict.get("multiplicity", False):
        get_multiplicity(filenames=settings.plot_settings_dict.get("filenames"),
                         legends=settings.plot_settings_dict.get("legends"),
                         name=settings.name.replace(" ", "_"),
                         plot_type=settings.plot_settings_dict.get("output type"),
                         decimals=1, step=0.1)
