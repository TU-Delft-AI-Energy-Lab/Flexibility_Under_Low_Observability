#!/usr/bin/env python
import numpy as np
import time

__author__ = "Demetris Chrysostomou"
__credits__ = ["Demetris Chrysostomou", "Jose Luis Rueda Torres", "Jochen Lorenz Cremer"]
__version__ = "1.0.0"
__maintainer__ = "Demetris Chrysostomou"
__email__ = "D.Chrysostomou@tudelft.nl"
__status__ = "Production"


def profile_creation(no_samples, net, distribution, keep_mp, services='DG Only', flexible_loads=[]):
    """ Creation of {no_samples} of new [P, Q] for each FSP. These new [P,Q] are
       a flexibility activation [ΔP, ΔQ] applied on the initial output [P_0, Q_0] of each FSP.
       Based on the services (i.e. DG, Load, or Both), the more specific functions for sample creation are called.

    :param no_samples: Amount of shifts that the algorithm will create and run, [int]
    :param net: PandaPower network in which the simulations are performed, [Pandapower Network]
    :param distribution: Type of distribution by which the new [P,Q] samples are obtained, [str]
    :param keep_mp: Boolean whether the DG FSP shifts only concern the output power factor
    (keeping maximum output power), or can also reduce the DG FSP power output/consumption, [Bool]
    :param services: If FSPs are DG, Loads or both, [str]
    :param flexible_loads: Which Loads are considered FSPs, [list of int]
    :return: profiles=The new active and reactive power for each FSP, for all power flow simulations [list],
             dur_samples=The duration in seconds for the sample creations [float]
    """
    rng = np.random.RandomState(21)
    if services == 'DG only':
        profiles, dur_samples = create_samples(no_samples, net, distribution=distribution, keep_mp=keep_mp, rng=rng)
    elif services == 'All':
        # This case, takes 50% of the samples for action sequences where both loads and generators are changed,
        # and 50% where only DG or only Load are shifted, to explore different regions of the flexibility area
        pq_profiles, dur_samples = create_samples(int(no_samples/2), net, distribution=distribution, keep_mp=keep_mp,
                                                  rng=rng)
        pq_load_profiles, dur_load_samples = create_load_samples(int(no_samples/2), net, distribution=distribution,
                                                                 flex_loads=flexible_loads, rng=rng)
        profiles = np.concatenate((pq_profiles, pq_load_profiles), axis=1).tolist()
        dur_samples += dur_load_samples

        pq_profiles_new, dur_new = create_samples(int(1*no_samples/8), net, distribution='No_change', keep_mp=keep_mp,
                                                  rng=rng)
        profiles_new = np.concatenate((pq_profiles_new, pq_load_profiles[:int(1*no_samples/8)]), axis=1).tolist()
        profiles = np.concatenate((profiles, profiles_new), axis=0).tolist()

        pq_load_profiles, dur_load_samples = create_load_samples(int(3*no_samples/8), net, distribution='No_change',
                                                                 flex_loads=flexible_loads, rng=rng)
        profiles_new = np.concatenate((pq_profiles[:int(3*no_samples/8)], pq_load_profiles), axis=1).tolist()
        profiles = np.concatenate((profiles, profiles_new), axis=0).tolist()
        dur_samples += dur_new + dur_load_samples
    elif services == 'Load only':
        pq_profiles, dur_samples = create_samples(no_samples, net, distribution='No_change', keep_mp=keep_mp, rng=rng)
        pq_load_profiles, dur_load_samples = create_load_samples(no_samples, net, distribution=distribution,
                                                                 flex_loads=flexible_loads, rng=rng)
        profiles = np.concatenate((pq_profiles, pq_load_profiles), axis=1).tolist()
        dur_samples += dur_load_samples
    else:
        assert False, 'Error: Choose FSPs from {All, Load only, DG only}'
    return profiles, dur_samples


def create_load_samples(no_samples, net, distribution, flex_loads, rng):
    """ Creation of {no_samples} of new [P, Q] for each load FSP. These new [P,Q] are
       a flexibility activation [ΔP, ΔQ] applied on the initial output [P_0, Q_0] of each load FSP.

    :param no_samples: Amount of shifts that the function will create, [int]
    :param net: PandaPower network in which the simulations are performed, [Pandapower Network]
    :param distribution: Type of distribution by which the new [P,Q] samples are obtained, [str]
    :param flex_loads: Which Loads are considered FSPs, [list of int]
    :param rng: Function by which the random numbers are generated
    :return: pq_profiles=The new active and reactive power for each load FSP, for the {no_samples} [list],
             dur_samples=The duration in seconds for the sample creations [float]
    """
    if flex_loads == []:
        flex_load_len = len(net.load)
    else:
        flex_load_len = len(flex_loads)
    t_start_create_mc_samples = time.time()
    random_p = sample_from_rng(distribution, no_samples*flex_load_len, 2, rng)
    pq_profiles = sample_new_load_point(net.load, random_p, no_samples, flex_loads)
    t_stop_create_mc_samples = time.time()
    print(f"{no_samples} MC PQ values sampled from {distribution} distribution needed "
          f"{t_stop_create_mc_samples - t_start_create_mc_samples} seconds")
    return pq_profiles, t_stop_create_mc_samples - t_start_create_mc_samples


def create_samples(no_samples, net, distribution, keep_mp, rng):
    """ Creation of {no_samples} of new [P, Q] for each DG FSP. These new [P,Q] are
        a flexibility activation [ΔP, ΔQ] applied on the initial output [P_0, Q_0] of each DG FSP.

    :param no_samples: Amount of shifts that the function will create, [int]
    :param net: PandaPower network in which the simulations are performed, [Pandapower Network]
    :param distribution: Type of distribution by which the new [P,Q] samples are obtained, [str]
    :param keep_mp: Boolean whether the DG FSP shifts only concern the output power factor
    (keeping maximum output power), or can also reduce the DG FSP power output/consumption, [Bool]
    :param rng: Function by which the random numbers are generated
    :return: pq_profiles=The new active and reactive power for each DG FSP, for the {no_samples} [list],
             dur_samples=The duration in seconds for the sample creations [float]
    """
    t_start_create_mc_samples = time.time()
    if keep_mp:
        random_p = sample_from_rng(distribution, no_samples*len(net.sgen), 1, rng)
        pq_profiles = sample_new_point(net.sgen, random_p, no_samples)
    else:
        random_p = sample_from_rng(distribution, no_samples*len(net.sgen), 2, rng)
        pq_profiles = sample_new_non_mp_point(net.sgen, random_p, no_samples)
    t_stop_create_mc_samples = time.time()
    print(f"{no_samples} MC PQ values sampled from {distribution} distribution needed "
          f"{t_stop_create_mc_samples - t_start_create_mc_samples} seconds")
    return pq_profiles, t_stop_create_mc_samples - t_start_create_mc_samples


def sample_from_rng(distribution, no_samples_dg, dof, rng):
    """ Based on the type of distribution, this function generates {no_samples_dg} for the flexibility activations which
        do not yet concern for the limits of each FSP and will later be applied on each FSP.

    :param distribution: Type of distribution used for the data generation, [str]
    :param no_samples_dg: Number of samples to be generated, [int]
    :param dof: Generated based on the 'keep_mp' variable. If dof=1, the random number generated for the
           active power P also defines the shift for the reactive power Q to keep S constant, [int:1 or 2]
    :param rng: RNG function to be used to generate the data, is defined outside of the function to return the
           same results at each simulation (through a seed) but to avoid returning the same numbers if it is called
           multiple times in one simulation, [numpy rng function]
    :return: random_p=array of generated random values to be used for the FSP activations
    """
    if distribution == 'Normal':
        random_p = rng.normal(1, 0.02, [no_samples_dg, dof])
    elif distribution == 'Uniform':
        random_p = rng.uniform(0, 1, [no_samples_dg, dof])
    elif distribution == 'Normal_Limits_Oriented':
        if dof == 1:
            random_p = rng.normal(1, 1, [no_samples_dg, dof])
        elif dof == 2:
            # this scenario generates:
            #   25% of the samples for high shifts in P and high shifts in Q
            #   25% of the samples for high shifts in P and low shifts in Q
            #   25% of the samples for high shifts in Q and low shifts in P
            #   25% of the samples for medium shifts in P and medium shifts in Q
            random_p1 = rng.normal(0, 1, [1*int(no_samples_dg/4), 2])
            random_p2 = np.array(np.concatenate((rng.normal(0, 1, [int(no_samples_dg/4), 1]),
                                                 rng.normal(1, 1, [int(no_samples_dg/4), 1])), axis=1))
            random_p3 = np.array(np.concatenate((rng.normal(1, 1, [int(no_samples_dg/4), 1]),
                                                 rng.normal(0, 1, [int(no_samples_dg/4), 1])), axis=1))
            random_p4 = np.array(np.concatenate((rng.normal(0.5, 1, [no_samples_dg-int(no_samples_dg/4), 1]),
                                                 rng.normal(0.5, 1, [no_samples_dg-int(no_samples_dg/4), 1])), axis=1))
            random_p = np.array(np.concatenate((random_p1, random_p2, random_p3, random_p4)))
    elif distribution == 'No_change':
        random_p = np.ones((no_samples_dg, dof))
    else:
        assert False, f"Please specify a viable sampling distribution, i.e. 'Normal', 'Uniform', " \
                      f"'Normal_Limits_Oriented' or 'No_change'. Not {distribution}"
    return random_p


def sample_new_point(sgen, random_p, no_samples):
    """ This function is called when the keep_mp is true for DG FSPs.
    Based on the random values generated for active power shifts,
    it applies the shifts on P, and applies shifts is Q which will keep the S of the DG FSP same as the initial.

    :param sgen: DG FSP, [PandaPower list of objects]
    :param random_p: Random values for the P shift, [1 dimensional numpy array]
    :param no_samples: Number of samples for the applied shifts, [int]
    :return: {no_samples} of new P and Q values for the DG FSPs, [list or lists]
    """
    pq_profiles = []
    for j in range(0, no_samples):
        sample = []
        for i in range(0, len(sgen)):
            p_perc = random_p[len(sgen)*j + i][0]
            p_new = sgen['sn_mva'][i]*p_perc
            # s^2 = p^2 + q^2 -> q^2 = s^2-p^2
            # iteratively make q positive or negative
            q_new = (-1)**j * np.sqrt(sgen['sn_mva'][i]**2 - p_new**2)
            sample.append([p_new, q_new])
        pq_profiles.append(sample)
    return pq_profiles


def sample_new_non_mp_point(sgen, random_p, no_samples):
    """ This function is called when keep_mp is false for DG FSPs.
    Based on the random values generated for active and reactive power shifts, it checks that:
        1.The active power shift percentages are between [0%, 100%], to avoid negative or increased generation values
        2.The reactive power shifts will not cause |S_new| > |S_initial|

    :param sgen: DG FSP, [PandaPower list of objects]
    :param random_p: Random values for the P Q shifts, [2 dimensional numpy array]
    :param no_samples: Number of samples for the applied shifts, [int]
    :return: {no_samples} of new P and Q values for the DG FSPs, [list or lists]
    """
    pq_profiles = []
    for j in range(0, no_samples):
        sample = []
        for i in range(0, len(sgen)):
            p_perc = random_p[len(sgen)*j + i][0]
            if p_perc >= 1:
                p_new = sgen['sn_mva'][i]
            elif p_perc <= 0:
                p_new = 0
            else:
                p_new = sgen['sn_mva'][i]*p_perc
            # s^2 = p^2 + q^2 -> q^2 = s^2-p^2
            # iteratively make q positive or negative
            q_max = np.sqrt(sgen['sn_mva'][i]**2 - p_new**2)
            if q_max >= abs(sgen['sn_mva'][i]*(random_p[len(sgen)*j + i][1])):
                q_new = (-1)**j*sgen['sn_mva'][i]*random_p[len(sgen)*j + i][1]
            else:
                q_new = (-1)**j*q_max
            sample.append([p_new, q_new])
        pq_profiles.append(sample)
    return pq_profiles


def sample_new_load_point(loads, random_p, no_samples, flex_loads=[]):
    """ This function is called to apply the generated random shifts on Load FSPs.
    Based on the random values generated for active and reactive power shifts, it checks that:
        1.The active power shift percentages are between [0%, 100%], to avoid negative or increased consumption values
        2.The reactive power shifts will not cause |S_new| > |S_initial|

    :param loads: Load FSP, [PandaPower list of objects]
    :param random_p: Random values for the P Q shifts, [2 dimensional numpy array]
    :param no_samples: Number of samples for the applied shifts, [int]
    :param flex_loads: Which loads of flexible out of all the network loads.
    If empty, it is assumed that all loads are flexible (since this function is called when at least 1 load is flexible,
    [list of int]
    :return: {no_samples} of new P and Q values for the Load FSPs, [list or lists]
    """
    pq_profiles = []
    load_change = 1
    if not flex_loads:
        for j in range(0, no_samples):
            sample = []
            for i in range(0, len(loads)):
                p_perc = random_p[len(loads)*j + i][0]
                if p_perc >= 1:
                    p_new = loads['p_mw'][i]
                elif p_perc <= 0:
                    p_new = 0
                else:
                    p_new = loads['p_mw'][i]*p_perc

                # s^2 = p^2 + q^2 -> q^2 = s^2-p^2
                # iteratively make q positive or negative
                p_new = load_change*p_new
                q_max = np.sqrt(load_change*load_change*(loads['sn_mva'][i]**2) - p_new**2)
                if q_max >= abs(load_change * loads['q_mvar'][i] * (random_p[len(loads) * j + i][1])):
                    q_new = loads['q_mvar'][i]*random_p[len(loads)*j + i][1]
                else:
                    q_new = q_max

                q_new = load_change*q_new
                sample.append([p_new, q_new])
            pq_profiles.append(sample)
    else:
        for j in range(0, no_samples):
            sample = []
            for idx, i in enumerate(flex_loads):
                p_perc = random_p[len(flex_loads) * j + idx][0]
                if p_perc >= 1:
                    p_new = loads['p_mw'][i]
                elif p_perc <= 0:
                    p_new = 0
                else:
                    p_new = loads['p_mw'][i] * p_perc

                # s^2 = p^2 + q^2 -> q^2 = s^2-p^2
                # iteratively make q positive or negative
                p_new = load_change * p_new

                q_max = np.sqrt(load_change * load_change * (loads['sn_mva'][i] ** 2) - p_new ** 2)
                if np.isnan(q_max):
                    print(loads['sn_mva'][i], p_new, i)
                if q_max >= abs(load_change * loads['q_mvar'][i] * (random_p[len(flex_loads) * j + idx][1])):
                    q_new = loads['q_mvar'][i] * random_p[len(flex_loads) * j + idx][1]
                else:
                    q_new = q_max

                q_new = load_change * q_new
                sample.append([p_new, q_new])
            pq_profiles.append(sample)
    return pq_profiles

