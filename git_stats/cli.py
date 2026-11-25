import argparse
import os
import re
from argparse import Namespace
from collections.abc import Callable
from os.path import expanduser, realpath, join, dirname, basename

from git_stats.charts import draw_find_chart
from git_stats.history import find_commits, find_text, find_files
from git_stats.searches import SEARCHES, TEST_FILE


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
        find_files(commits, args.include, args.exclude)
        measure_files(commits, len)
        draw_find_chart(output, f"{project}: Files", commits, ["Total", "Prod", "Test"])
    elif find == "size":
        find_files(commits, args.include, args.exclude)
        measure_files(commits, average_size)
        draw_find_chart(output, f"{project}: Average file size", commits, ["Total", "Prod", "Test"], "Bytes")
    elif find == "commits":
        draw_find_chart(output, f"{project}: Commits per {args.period}", commits, ["commits"])
    else:
        search = SEARCHES[find]
        find_text(commits, search.regexes, search.files, args.include, args.exclude)
        draw_find_chart(output, f"{project}: {search.description}", commits, list(search.regexes))


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser("git-stats", description="Chart how often regexes match, or how many files exist, over a repo's history.")
    parser.add_argument("directory", help="The git dir to analyze.", type=str)
    parser.add_argument("-a", "--after", help="From date", type=str)
    parser.add_argument("-b", "--before", help="To date", type=str)
    parser.add_argument("-p", "--period", help="Sampling period", choices=["commit", "day", "week", "month"], default="week")
    parser.add_argument("-f", "--find", help="Predefined regexes to count, or files, size or commits; one chart each",
                        choices=[*SEARCHES, "files", "size", "commits"], action="extend", nargs="+", required=True)
    parser.add_argument("-i", "--include", help="Path included in --find, all if none; repeatable.", action="append", default=[])
    parser.add_argument("-x", "--exclude", help="Path excluded from --find; repeatable.", action="append", default=[])
    parser.add_argument("-o", "--output", help="Chart file in build/ (default: DIRECTORY-FIND.png)", type=str)
    args = parser.parse_args()
    if args.output and len(args.find) > 1:
        parser.error("--output needs a single --find")
    return args


def measure_files(commits: dict[str, dict], measure: Callable[[list[dict]], float]):
    test_file = re.compile(TEST_FILE)
    for commit in commits.values():
        test = [file for file in commit["files"] if test_file.search(file["name"])]
        prod = [file for file in commit["files"] if not test_file.search(file["name"])]
        commit.update(Total=measure(commit["files"]), Prod=measure(prod), Test=measure(test))


def average_size(files: list[dict]) -> float:
    return sum(file["size"] for file in files) / max(len(files), 1)
