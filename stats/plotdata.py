#!/usr/bin/env python
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
from statsapp.models import Record
from numpy import *
import pandas as pd
from pandas.tools.pivot import pivot_table
import numpy as np


def metric_vs_property(
    agent,
    scenario,
    scenario_parameter,
    metrics=('completion_time',),
    property='agent_parameter',
    aggfunc=np.mean
):
    qs = Record.objects.filter(
        agent=agent,
        scenario=scenario,
        scenario_parameter=scenario_parameter
    )
    df = pd.DataFrame(list(qs.values()))
    table = pivot_table(
        df,
        values=list(metrics),
        rows=[property],
        #cols=[metric],
        aggfunc=np.mean
    )
    return table


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-s", "--scenario", default="RandomWalkers")
    parser.add_option("-S", "--scenarioparameter", type="int", default=None)
    parser.add_option("-a", "--agent", default="RoadMap")
    parser.add_option("-A", "--agentparameter", type="int")
    parser.add_option("-t", "--plottype", type="string", default="goaltime")
    parser.add_option("-x", "--xaxis", type="string", default="")
    parser.add_option("-y", "--yaxis", type="string", default="")
    parser.add_option("-i", "--title", type="string", default="")

    actions = {
        'itertime': itertime,
        'collisions': collisions,
        'goaltime': time_to_goal,
        'dual': dual
    }

    (opts, args) = parser.parse_args()

    action = actions[opts.plottype]
    agent = opts.agent
    scenario = opts.scenario
    scenario_parameter = opts.scenarioparameter

    print metric_vs_property(
        agent='Arty',
        scenario='MarketSquare',
        scenario_parameter=None,
        metrics=['completion_time', 'max_iteration_time']
    )
