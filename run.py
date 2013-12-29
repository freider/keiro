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


def get_cli_options():
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
    return opts


def verify_untouched_files(git):
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
            print '\n'.join(untracked)
            print

        should_continue = "x"
        while should_continue not in ("", "n", "y"):
            should_continue = raw_input(
                "You should commit any changes that affect "
                "the robot before running a simulation.\n"
                "Do you want to continue? (y/N)").lower().strip()

        if not should_continue or should_continue == 'n':
            return


class Simulation(object):
    def __init__(self, git, opts, randomseed):
        self.opts = opts
        self.randomseed = randomseed
        self.git = git
        self._scenario = None
        self._agent = None

    def run(self):
        verify_untouched_files(self.git)
        self._setup_scenario()
        if self._check_video_available():
            video = self._get_video()

        self._scenario.world.add_encoder(video)

        if self.opts.profile:
            cProfile.run("scenario.run()")
        else:
            if self._scenario.run():
                self._save_results()
                print("Saved record to database")
            else:
                print("User triggered quit, no record saved to database")
                quit()

        if video:
            video.close()

    def _check_video_available(self):
        if (not self.opts.no_video) and ffmpeg_encode.available():
            if self.opts.timestep == 0:
                warnings.warn(
                    "Can't use realtime simulations with video capture. "
                    "Use a non-zero timestep when recording videos."
                )
            else:
                return True
        return False

    def _get_video(self):
        # TODO: use temporary output path, then rename video after completion
        # this will let us set the name to the database row ID to link runs
        # with their video

        if self.opts.capture_path:
            capture_path = self.opts.capture_path
        else:
            filename = "{0}_{1}_{2}.mp4".format(
                self._scenario,
                self._agent,
                self.randomseed
            )
            print "Storing video in {0}".format(filename)
            capture_path = os.path.join("videos", filename)

        approx_framerate = int(1 / self.opts.timestep)
        return ffmpeg_encode.Video(path=capture_path,
                                   frame_rate=approx_framerate,
                                   frame_size=self._scenario.world.size)

    def _setup_scenario(self):
        # TODO: change to using once randomizes instance per Simluation

        # as to not be affected by external calls
        # seed needs to be set before the scenario is setup
        random.seed(self.randomseed)
        ScenarioClass = ScenarioRegistrar.register[self.opts.scenario]
        AgentClass = AgentRegistrar.register[self.opts.agent]

        self._agent = AgentClass(self.opts.agentparameter)
        self._scenario = ScenarioClass(
            self.opts.scenarioparameter,
            self._agent,
            random_seed=self.randomseed + 1
        )
        self._scenario.world.set_timestep(self.opts.timestep)
        self._scenario.world.set_show_fps(self.opts.show_fps)
        self._agent.init(View(self._scenario.world.get_obstacles(), []))

    def _save_results(self):
        r = models.Record()
        r.date = datetime.now()
        r.revision = self.git.commit_id()
        r.scenario = self.opts.scenario
        r.scenario_parameter = self._scenario.parameter
        r.seed = self.randomseed
        r.agent = self.opts.agent
        r.agent_parameter = self._agent.parameter
        r.view_range = self._agent.view_range
        r.timestep = self.opts.timestep
        r.collisions = self._agent.collisions
        r.avg_iteration_time = self._agent.iterations.get_avg_iterationtime()
        r.max_iteration_time = self._agent.iterations.get_max_iterationtime()
        r.min_iteration_time = self._agent.iterations.get_min_iterationtime()
        r.completion_time = self._scenario.world.get_time()
        r.save()


def run():
    git = keiro.git.Git()

    opts = get_cli_options()

    if ':' in opts.seed:
        startseed, numseeds = map(int, opts.seed.split(':'))
    else:
        startseed = int(opts.seed)
        numseeds = 1

    for currentseed in xrange(startseed, startseed + numseeds):
        simulation = Simulation(git, opts, currentseed)
        simulation.run()


if __name__ == "__main__":
    run()
