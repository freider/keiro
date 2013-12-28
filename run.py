#!/usr/bin/env python
from keiro.world import View
from agents import *
from scenarios import *
from keiro.scenario import ScenarioRegistrar
from keiro.agent import AgentRegistrar
import keiro.git

from keiro import ffmpeg_encode
import os
import random
import cProfile
import warnings
from optparse import OptionParser
from datetime import datetime

os.environ["DJANGO_SETTINGS_MODULE"] = "stats.settings"
from stats.statsapp import models


def run():
    git = keiro.git.Git()
    unstaged = git.unstaged_changes()
    uncommited = git.uncommited_changes()
    untracked = git.untracked_files()
    if (unstaged or uncommited or untracked):
        if unstaged:
            print "Unstaged changes in:"
            print '\n'.join(unstaged)
            print
        if uncommited:
            print "Uncommited changes in:"
            print '\n'.join(uncommited)
            print
        if untracked:
            print "Untracked files:"
            print '\n'.join(unstaged)
            print

        should_continue = "x"
        while should_continue not in ("", "n", "y"):
            should_continue = raw_input(
                "You should commit any changes that affect"
                "the robot before running a simulation.\n"
                "Do you want to continue? (y/N)").lower().strip()

        if not should_continue or should_continue == 'n':
            return

    parser = OptionParser()
    parser.add_option("-s", "--scenario", default="RandomWalkers")
    parser.add_option("-S", "--scenarioparameter", type="int")
    parser.add_option("-a", "--agent", default="RoadMap")
    parser.add_option("-A", "--agentparameter", type="int")
    parser.add_option("-r", "--seed", type="string", default="1")
    parser.add_option("-t", "--timestep", type="float", default=0.1)

    parser.add_option("-f", "--show-fps", action="store_true", default=False)
    parser.add_option("-p", "--profile", action="store_true", default=False)
    parser.add_option("-n", "--no-video", action="store_true", default=False)
    parser.add_option("-c", "--capture-path", metavar="PATH")

    (opts, args) = parser.parse_args()

    if ':' in opts.seed:
        startseed, numseeds = map(int, opts.seed.split(':'))
    else:
        startseed = int(opts.seed)
        numseeds = 1

    for currentseed in xrange(startseed, startseed + numseeds):
        random.seed(currentseed)
        ScenarioClass = ScenarioRegistrar.register[opts.scenario]
        AgentClass = AgentRegistrar.register[opts.agent]

        agent = AgentClass(opts.agentparameter)
        scenario = ScenarioClass(
            opts.scenarioparameter,
            agent,
            random_seed=currentseed+1
        )

        world = scenario.world
        world.set_timestep(opts.timestep)
        world.set_show_fps(opts.show_fps)

        agent.init(View(world.get_obstacles(), []))

        video = None
        if (not opts.no_video) and ffmpeg_encode.available():
            if opts.timestep == 0:
                warnings.warn("Can't use realtime simulations with video capture. Use a non-zero timestep when recording videos.")
            else:
                if opts.capture_path:
                    capture_path = opts.capture_path
                else:
                    filename = "{0}_{1}_{2}.mp4".format(
                        scenario,
                        agent,
                        currentseed
                    )
                    capture_path = os.path.join("videos", filename)

                approx_framerate = int(1 / opts.timestep)
                video = ffmpeg_encode.Video(path=capture_path,
                                            frame_rate=approx_framerate,
                                            frame_size=world.size)
                world.add_encoder(video)

        if opts.profile:
            cProfile.run("scenario.run()")
        else:
            if scenario.run():
                record = models.Record()
                record.date = datetime.now()
                record.scenario = opts.scenario
                record.scenario_parameter = scenario.parameter
                record.seed = currentseed
                record.agent = opts.agent
                record.agent_parameter = agent.parameter
                record.view_range = agent.view_range
                record.timestep = opts.timestep
                record.collisions = agent.collisions
                record.avg_iteration_time = agent.iterations.get_avg_iterationtime()
                record.max_iteration_time = agent.iterations.get_max_iterationtime()
                record.min_iteration_time = agent.iterations.get_min_iterationtime()
                record.completion_time = world.get_time()
                record.save()
                print("Saved record to database")
            else:
                print("User triggered quit, no record saved to database")
                quit()

        if video:
            video.close()

if __name__ == "__main__":
    run()
