#!/usr/bin/python3

import argparse
import asyncio
import pathlib
import runpy
from succession.registry import resolve_all, find_target
import logging
import sys
from colorlog import ColoredFormatter

def get_parser():
    parser = argparse.ArgumentParser(description="Resolve dependency and run tasks")
    parser.add_argument('--file','-f', type=str, default="Sucessfile")
    verbgroup = parser.add_mutually_exclusive_group()
    verbgroup.add_argument('--verbose', '-v', action='count', default=0, help="Increase verbosity")
    verbgroup.add_argument('--quiet', '-q', action='store_true', help="Silences all but critical errors")
    colourgroup = parser.add_mutually_exclusive_group()
    colourgroup.add_argument('--colour', action='store_true', help="Enables colour output on terminals which support it")
    colourgroup.add_argument('--no-colour', dest = "colour", action='store_false' ,help="Disables colour output")
       
    parser.add_argument('initialjob', metavar="TARGET", type=JobResolver,
                         default= JobResolver(None), nargs='?', )
    parser.set_defaults(**{
        'colour': sys.stdin.isatty()
    })
    return parser


class JobResolver:
    def __init__(self, jobname):
        self.jobname = jobname

    def __str__(self,):
        return f"JobResolver<{self.jobname}>"


    def find_job(self,):

        ## Create a serach order list
        jobnames =[self.jobname]
        try:
            jobnames.append(pathlib.Path(self.jobname))
        except TypeError:pass

        jobnames.append('default')

        ## Search each into turn until we find one
        for j in  jobnames:
            if not j:continue
            try:
                return find_target(j)
            except KeyError:continue

        raise RuntimeError("No initial target found")

    def __call__(self,*args,**kwargs):
        return self.find_job().Run()

def execute_successfile(fname):
    from succession import prelude
    runpy.run_path(fname, init_globals =  prelude.__dict__,)


def setup_logging(opts):
    rootlogger = logging.getLogger('')
    if opts.quiet:
        level = logging.CRITICAL
    else:
        level = logging.INFO

    # Lower lvel by verbosity setting
    level -= (opts.verbose * 10)
    rootlogger.setLevel(level)
    handler = logging.StreamHandler()
    if opts.colour:
        formatter = ColoredFormatter(
           "%(log_color)s%(message)s",
           datefmt=None,
           reset=True,
           log_colors={
              'DEBUG':    'green',
              'INFO':     'white',
              'WARNING':  'yellow',
              'ERROR':    'red',
              'CRITICAL': 'red,bg_white',
           },
           secondary_log_colors={},
           style='%'
        ) 
        handler.setFormatter(formatter)
    rootlogger.addHandler(handler)

def run(opts):
    setup_logging(opts)
    execute_successfile(opts.file)
    resolve_all()
    asyncio.run(opts.initialjob())

def main(args):
    parser = get_parser()
    opts = parser.parse_args(args)
    run(opts)

def start():
    main(sys.argv[1:])

if __name__ == "__main__":
    start()

