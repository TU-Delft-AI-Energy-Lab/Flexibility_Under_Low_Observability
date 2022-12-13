#!/usr/bin/env python
import json

__author__ = "Demetris Chrysostomou"
__credits__ = ["Demetris Chrysostomou", "Jose Luis Rueda Torres", "Jochen Lorenz Cremer"]
__version__ = "1.0.0"
__maintainer__ = "Demetris Chrysostomou"
__email__ = "D.Chrysostomou@tudelft.nl"
__status__ = "Production"


class SettingReader:
    """ Class parsing through the json scenario input files, checking their validity and saving their information
    """
    def __init__(self, scenario_name='unaltered_network'):
        """ Initialize the class, read the input scenario file, test if the information is as expected, and save
        it for further usage

        :param scenario_name: name of the scenario file within the scenarios folder (excluding the folder and the .json)
        , [str]
        """
        if 'scenarios' not in scenario_name:
            f = open(f'scenarios/{scenario_name}.json')
        else:
            f = open(f'{scenario_name}.json')
        self.data = json.load(f)
        self.name = self.data.get('name', 'Unnamed').replace(' ', '_')
        self.scenario_settings = self.data.get('scenario_settings', {})
        self.net_name = self.scenario_settings.get("network", "CIGRE MV")
        self.no_samples = self.scenario_settings.get("no_samples", 100)
        self.distribution = self.scenario_settings.get("distribution", "Normal_Limits_Oriented")
        self.keep_mp = self.scenario_settings.get("keep_mp", False)
        self.max_curr = self.scenario_settings.get("max_curr_per", 100)
        self.max_volt = self.scenario_settings.get("max_volt_pu", 1.05)
        self.min_volt = self.scenario_settings.get("min_volt_pu", 0.95)
        self.mc_sim = self.scenario_settings.get("Monte_Carlo_simulation", True)
        self.fsps = self.scenario_settings.get("FSPs", "All")
        self.fsp_wt = self.scenario_settings.get("FSP_WT_indices", [-1])
        self.fsp_pv = self.scenario_settings.get("FSP_PV_indices", [-1])
        self.fsp_load = self.scenario_settings.get("FSP_load_indices", [-1])
        self.observ_lines = self.scenario_settings.get("observable_lines_indices", [0, 1, 10, 11])
        self.observ_buses = self.scenario_settings.get("observable_buses_indices", [0, 1, 2, 3, 12, 13, 14])
        self.scenario_type_dict = self.scenario_settings.get("scenario_type", {})
        self.plot_settings_dict = self.scenario_settings.get("plot_settings", {})
        self.scale_pv = self.scenario_settings.get("scale_pv", 1)
        self.scale_wt = self.scenario_settings.get("scale_wt", 1)
        self.tester()
        return

    def tester(self):
        """ Test that the imported information from the file is as expected and should not cause issues later.
        """
        if self.scenario_settings == {}:
            assert False, "Please give scenario settings within the input json file"
        if self.net_name != "CIGRE MV":
            assert False, f"Currently only 'CIGRE MV' network is supported, not {self.net_name}"
        if type(self.no_samples) != int:
            assert False, f"Only integer number of samples supported, not {type(self.no_samples)}"
        if self.distribution not in ["Normal_Limits_Oriented", "Uniform", "Normal"]:
            assert False, f"Only 'Normal_Limits_Oriented', 'Uniform', and 'Normal' distributions supported," \
                          f" not {self.distribution}"
        if self.keep_mp not in [True, False]:
            assert False, f"keep_mp should be given as a boolean 'true/false' not {self.keep_mp}"
        if type(self.max_curr) != int and type(self.max_curr) != float:
            assert False, f"Only integer or float maximum component loading supported, not {type(self.max_curr)}"
        if type(self.max_volt) != float:
                assert False, f"Only float maximum voltage supported, not {type(self.max_volt)}"
        if type(self.min_volt) != float:
                assert False, f"Only float minimum voltage supported, not {type(self.min_volt)}"
        if self.mc_sim not in [True, False]:
            assert False, f"Monte_Carlo_simulation should be given as a boolean 'true/false' not {self.mc_sim}"
        if self.fsps not in ['DG only', 'Load only', 'All']:
            assert False, f"FSPs currently supported are 'All' 'DG only', or 'Load only', not {self.fsps}"
        if type(self.fsp_wt) != list:
            assert False, f"Please set WT indices which are FSP as a list, not {type(self.fsp_wt)}"
        if type(self.fsp_pv) != list:
            assert False, f"Please set PV indices which are FSP as a list, not {type(self.fsp_pv)}"
        if type(self.fsp_load) != list:
            assert False, f"Please set load indices which are FSP as a list, not {type(self.fsp_load)}"
        if type(self.observ_lines) != list:
            assert False, f"Please set observable line indices as a list, not {type(self.observ_lines)}"
        if type(self.observ_buses) != list:
            assert False, f"Please set observable bus indices as a list, not {type(self.observ_buses)}"
        return
