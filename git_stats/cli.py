import argparse
import os
from argparse import Namespace
from os.path import expanduser, realpath, join, dirname, basename

from git_stats.charts import draw_find_chart, draw_files_chart
from git_stats.history import find_commits, find_text, find_files
from git_stats.searches import SEARCHES


def main():
    args = parse_args()
    project = basename(realpath(expanduser(args.directory)))
    outputs = {find: realpath(join("build", args.output or f"{project}-{find}.png")) for find in args.find}
    commits = find_commits(args.directory, args.after, args.before, args.period)
    for find, output in outputs.items():
        os.makedirs(dirname(output), exist_ok=True)
        draw(find, output, project, commits, args)
        print(f"Wrote {output}")


def draw(find: str, output: str, project: str, commits: dict[str, dict], args: Namespace):
    if find == "files":
        find_files(commits)
        draw_files_chart(output, f"{project}: Files", commits)
    elif find == "commits":
        draw_find_chart(output, f"{project}: Commits per {args.period}", commits, ["commits"])
    else:
        search = SEARCHES[find]
        find_text(commits, search.regexes, search.files, args.exclude)
        draw_find_chart(output, f"{project}: {search.description}", commits, list(search.regexes))


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser("git-stats", description="Chart how often regexes match, or how many files exist, over a repo's history.")
    parser.add_argument("directory", help="The git dir to analyze.", type=str)
    parser.add_argument("-a", "--after", help="From date", type=str)
    parser.add_argument("-b", "--before", help="To date", type=str)
    parser.add_argument("-p", "--period", help="Sampling period", choices=["commit", "day", "week", "month"], default="week")
    parser.add_argument("-f", "--find", help="Predefined regexes to count, or files or commits; one chart each",
                        choices=[*SEARCHES, "files", "commits"], action="extend", nargs="+", required=True)
    parser.add_argument("-x", "--exclude", help="Path excluded from --find; repeatable.", action="append", default=[])
    parser.add_argument("-o", "--output", help="Chart file in build/ (default: DIRECTORY-FIND.png)", type=str)
    args = parser.parse_args()
    if args.output and len(args.find) > 1:
        parser.error("--output needs a single --find")
    return args
