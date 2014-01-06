# Introduction - What is Keiro?
Keiro is a framework for trying out path finding algorithms. 
It allows the creation of 2-dimensional "scenarios" with static and moving objects and lets you run simulations of different navigation strategies. Statistics about each simulation is recorded in a database for later review and videos of each simulation can be recorded. Included are a bunch of algorithms and libraries that simplify working with path finding.

## Project status
Keiro was developed as part of Elias Freider's thesis project in 2009. The code isn't in the best shape everywhere and is undergoing some major refactorisations at the time of writing (2013-03-31)

## Dependencies
Installation instructions are for Mac OSX mountain lion since that's what I use, but Keior should work on any other system as long as the dependencies can be installed. I assume that you have the CLI developer tools installed (via XCode or developer.apple.com) as well as the homebrew package manager (http://mxcl.github.io/homebrew/). I also prefer to use pip instead of easy_install.

    $ sudo easy_install pip

### Python 2.6-2.7
Keiro was written for Python 2.6, but has only been tested on 2.7 as of late.

### Pygame
Keiro depends on pygame which itself depends on the SDL and numpy libraries. To install the latest version of pygame from the project repository, which you have to if you want to use the SDL installed by homebrew, you also need the mercurial/hg version control system.
When installing pygame you might get a popup dialog telling you that you need X11. You can safely press cancel since that isn't required for keiro.
    
    $ brew install mercurial  # if you don't have it on your system already
    $ brew install sdl
    $ pip install numpy
    $ pip install hg+http://bitbucket.org/pygame/pygame

### swig
Keiro uses swig for building optimized native Python plugins written in C++
    
    $ brew install swig

### Django
For statistics gathering/display

    $ pip install Django

### ffmpeg
For (optional) video recording, you need to have ffmpeg on your `PATH`:

    $ brew install ffmpeg  # using homebrew on OSX

### Gnuplot
Gnuplot is optional but needed for plotting (which currently is experimental at best)

    $ brew install gnuplot
    $ pip install gnuplot-py


## Building
Keiro makes use of some C++ Python extensions to speed up the "physics" engine and standard graph algorithms. These extensions needs to be built to run keiro:
    
    $ cd cpp
    $ make

You also need to set up the sqlite (or other rdbms) for storing statistics of each run:
    
    $ cd stats
    $ python2.6 manage.py syncdb

## Running
Default simulation:

    $ python run.py

A simulation using the Arty algorithm

    $ python run.py -a Arty

Different scenarios (Try one of: {MarketSquare | CrowdedMarketSquare | TheFlood | Crossing})
    
    $ python run.py -s MarketSquare
  
Videos will be automatically stored in the videos directory after each successful simulation (if ffmpeg is installed on your system and available on the $PATH)

Check stats

    $ cd stats
    $ python manage.py runserver
    # browse to localhost:8000
