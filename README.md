# reaperml
Python scripts for musicking with [Reaper](https://www.reaper.fm/) and machine learning.

This is mainly for personal use, but I imagine some people could be interested. Like most things I do, this is essentially a wrapper for other talented people's work - notably [James Bradbury](https://github.com/jamesb93), the [FluCoMa](https://www.flucoma.org/) team and the [scikit-learn](https://scikit-learn.org/stable/) team.

These scripts are an environment for me to do musicking in Reaper using various machine learning algorithms, signal decomposition, algorithmic composition techniques etc.

## Main Features

- Programatically create and modify reaper projects (_.rpp_ files). This is using my modified version of James Bradbury's [reathon](https://github.com/jamesb93/reathon).
- Control audio corpora: create and manipulate collections of sounds and notably their audio descriptions. This is my own, much simpler version of a wrapper around the [FluCoMa](https://www.flucoma.org/) tools, again inspired by James Bradbury's [work](https://github.com/jamesb93/ftis) (honestly, check that guy out).
- Coupling of these elements with my own scikit-learn wrapper. This isn't essential, but I like to think as little as possible about what I'm doing, so look forward to simple functions like `cluster(num_clusters = 4)` or `reduce(method = 'umap', dimensions = 2`.

## Getting Started & Installation

There is no installation because I'm a savage. However, I do recommend you use a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html), and install the [FluCoMa CLI tools](https://github.com/flucoma/flucoma-cli) in this environment's bin.

Then you will need to `pip install` the following dependencies:
- scikit-learn
- soundfile
- numpy
- matplotlib

Oh yeah, and I imagine this will only work in Python 3.7+. I also recommend using something like [Visual Studio Code](https://code.visualstudio.com/) to run this from.