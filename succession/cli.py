#!/usr/bin/python3

import argparse
import asyncio
import pathlib
import runpy
from succession.registry import resolve_all, find_target


def get_parser():
    parser = argparse.ArgumentParser(description="Resolve dependency and run tasks")
    parser.add_argument('--file','-f', type=str, default="Sucessfile")
    parser.add_argument('initialjob', metavar="TARGET", type=JobResolver,
                         default= JobResolver(None), nargs='?', )
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
    ## Fix me this should be imported
    jobs = runpy.run_path(fname, init_globals =  prelude.__dict__,)

def run(opts):
    execute_successfile(opts.file)
    resolve_all()
    asyncio.run(opts.initialjob())

def main(args):
    parser = get_parser()
    opts = parser.parse_args(args)
    run(opts)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
