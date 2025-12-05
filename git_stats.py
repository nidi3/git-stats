import argparse
import os
from argparse import Namespace
from datetime import datetime
from os.path import expanduser, dirname, realpath

import matplotlib.pyplot as plt


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser("git_stats")
    parser.add_argument("directory", help="The git dir to analyze.", type=str)
    parser.add_argument("-a", "--after", help="From date", type=str)
    parser.add_argument("-b", "--before", help="To date", type=str)
    parser.add_argument("-p", "--period", help="Sampling period", choices=["commit", "day", "week"], default="week")
    # parser.print_help()
    return parser.parse_args()


def find_commits(dir: str, after: str, before: str, period: str) -> dict[str, dict]:
    os.chdir(realpath(expanduser(dir)))
    options = ""
    if after: options = options + f"--after={after} "
    if before: options = options + f"--before={before} "
    lines = os.popen(f'git --no-pager log --no-merges --all --format="%ct %H" {options}').readlines()
    commits = {}
    current = 0
    for line in lines:
        time, commit = line[:-1].split(" ")
        date = datetime.fromtimestamp(int(time))
        if period == "day":
            time = date.year * 400 + date.month * 40 + date.day
        elif period == "week":
            time = date.isocalendar()[1]
        elif period == "commit":
            time = date
        else:
            raise Exception("Invalid period " + period)
        if time != current:
            current = time
            commits[commit] = {"date": date}
    return commits


def find_text(commits: dict[str, dict], find: dict[str, str]):
    batch_size = 10
    commit_list = list(commits.keys())
    for i in range(0, len(commits), batch_size):
        batch = commit_list[i:i + batch_size]
        for name, text in find.items():
            lines = os.popen(f"git --no-pager grep -c '{text}' {" ".join(batch)}").readlines()
            for line in lines:
                parts = line[:-1].split(":")
                commit = commits[parts[0]]
                commit[name] = commit.get(name, 0) + int(parts[-1])

        print(commits[batch[0]]["date"])  # , end='\r')


def find_files(commits: dict[str, dict]):
    for id, commit in commits.items():
        lines = os.popen(f"git ls-tree -r -l {id}").readlines()
        lines_parts = [line.split(maxsplit=5) for line in lines]
        commit["files"] = [{"size": int(parts[3]), "name": parts[4]} for parts in lines_parts]

        print(commit["date"])  # , end='\r')


def draw_find_chart(commits: dict[str, dict], names):
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    dates = [commit["date"] for commit in commits.values()]
    for name in names:
        plt.plot(dates, [commit.get(name, 0) for commit in commits.values()], label=name)

    plt.legend()
    plt.ylabel('Count')
    # plt.show()
    os.chdir(dirname(realpath(__file__)))
    fig.savefig('find-counts.png')
    plt.close()


def draw_files_chart(commits: dict[str, dict]):
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    dates = [commit["date"] for commit in commits.values()]
    plt.plot(dates, [len(commit["files"]) for commit in commits.values()])
    plt.ylabel('Count')
    # plt.show()
    os.chdir(dirname(realpath(__file__)))
    fig.savefig('file-counts.png')
    plt.close()


def main():
    args = parse_args()
    commits = find_commits(args.directory, args.after, args.before, args.period)
    # find_files(commits)
    # draw_files_chart(commits)

    find = {"Old simple": "extends Vue", "Old mixin": "extends mixins", "New": "<script .*setup"}
    # find={"link":"link_created","link2":"linkCreated"}
    find_text(commits, find)
    for commit in commits.values():
        commit["Old total"] = commit.get("Old simple", 0) + commit.get("Old mixin", 0)
        commit["Total"] = commit["Old total"] + commit.get("New", 0)
    draw_find_chart(commits, ["Old simple", "Old mixin", "Old total", "New", "Total"])
    # draw_chart(commits, ["link","link2"])


main()
