import argparse
from os import path, mkdir
import base
import yaml

rootDir = base.rootPath
yamlPath = path.join(rootDir, "input.yaml")

# parse input arguments: a path to the yaml config file and an output dir
parser = argparse.ArgumentParser()
parser.add_argument("output", nargs='?',
                    help='The root directory for the new application',
                    action='store',
                    default=path.expanduser("~"))
parser.add_argument("config", nargs='?',
                    help="YAML file with app configuration values",
                    action='store',
                    default=yamlPath)
args = parser.parse_args()

# make sure the output path makes sense
assert (path.isdir(args.output))
# read in the YAML, if present.
with open(yamlPath) as _:
    configDict = yaml.load(_)

# Make a folder whose name is the app.
appBasePath = path.join(args.output, configDict['appname'])
mkdir(appBasePath)