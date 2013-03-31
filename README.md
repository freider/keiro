### Introduction - What is Keiro?
Keiro is a framework for trying out path finding algorithms. 
It allows the creation of 2-dimensional "scenarios" with static and moving objects and lets you run simulations of different navigation strategies. Statistics about each simulation is recorded in a database for later review and videos of each simulation can be recorded. Included are a bunch of algorithms and libraries that simplify working with path finding.

### Project status
Keiro was developed as part of Elias Freider's thesis project in 2009. The code isn't in the best shape everywhere and is undergoing some major refactorisations at the time of writing (2013-03-31)

### Dependencies
Keiro was written for Python 2.6-2.7
It depends on pygame and pil, django and Gnuplot.py which can be conveniently installed using pip:

    $ pip install pygame PIL Django gnuplot-py

For video recording, you need to have ffmpeg on your `PATH`:

    $ brew install ffmpeg  # using homebrew on OSX

### Building
Keiro makes use of some C++ Python extensions to speed up the "physics" engine and standard graph algorithms. These extensions needs to be built to run keiro:
    
    $ cd keiro/fast
    $ make

You also need to set up the sqlite (or other rdbms) for storing statistics of each run:
    
    $ cd keiro/stats
    $ python2.6 manage.py syncdb

### Running
Default simulation:

    $ python keiro.py

A simulation using the Arty algorithm

    $ python keiro.py -a Arty

Different scenarios (Try one of: {MarketSquare | CrowdedMarketSquare | TheFlood | Crossing})
    
    $ python keiro.py -s MarketSquare
  
Recording a video
    
    $ python keiro.py -c videos/testrun.mp4

Check stats

    $ cd stats
    $ python manage.py runserver
    # browse to localhost:8000
