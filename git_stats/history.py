import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from os.path import expanduser, realpath


def find_commits(dir: str, after: str, before: str, period: str) -> dict[str, dict]:
    os.chdir(realpath(expanduser(dir)))
    options = []
    if after: options.append(f"--after={after}")
    if before: options.append(f"--before={before}")
    lines = git("--no-pager", "log", "--no-merges", "--all", "--format=%ct %H", *options).splitlines()
    commits = {}
    current = 0
    for line in lines:
        time, commit = line.split(" ")
        date = datetime.fromtimestamp(int(time))
        if period == "day":
            time = date.year * 400 + date.month * 40 + date.day
        elif period == "week":
            time = date.isocalendar()[1]
        elif period == "month":
            time = date.year * 100 + date.month
        elif period == "commit":
            time = date
        else:
            raise Exception("Invalid period " + period)
        if time != current:
            current = time
            sample = commits[commit] = {"date": date, "commits": 0}
        sample["commits"] += 1
    return commits


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def find_text(commits: dict[str, dict], find: dict[str, str], files: dict[str, str], excludes: list[str]):
    excluded = [f":!{exclude}" for exclude in excludes]
    counts: dict[str, dict[str, int]] = {regex: {} for regex in find.values()}
    previous = None
    with ThreadPoolExecutor() as pool:
        for id, commit in reversed(commits.items()):
            if previous is None:
                literal, paths = False, excluded
            else:
                literal, paths = True, changed_files(previous, id, excluded)
                for file_counts in counts.values():
                    for path in paths:
                        file_counts.pop(path, None)
            if previous is None or paths:
                matches = pool.map(lambda regex: count_matches(id, regex, paths, literal), counts)
                for file_counts, new_counts in zip(counts.values(), matches):
                    file_counts.update(new_counts)
            for name, regex in find.items():
                file = re.compile(files.get(name, ""))
                commit[name] = sum(count for path, count in counts[regex].items() if file.search(path))
            previous = id

            print(commit["date"])  # , end='\r')


def changed_files(old: str, new: str, excluded: list[str]) -> list[str]:
    return git("diff", "--name-only", "--no-renames", "-z", old, new, "--", *excluded).split("\0")[:-1]


def count_matches(id: str, regex: str, paths: list[str], literal: bool) -> dict[str, int]:
    options = ["--literal-pathspecs"] if literal else []
    output = subprocess.run(["git", *options, "--no-pager", "grep", "-c", "-z", "-I", "-E", regex, id, "--", *paths],
                            capture_output=True, text=True).stdout
    return {location.split(":", 1)[1]: int(count) for location, count in (line.split("\0") for line in output.splitlines())}


def find_files(commits: dict[str, dict]):
    for id, commit in commits.items():
        lines = git("ls-tree", "-r", "-l", id).splitlines()
        lines_parts = [line.split(maxsplit=5) for line in lines]
        commit["files"] = [{"size": int(parts[3]), "name": parts[4]} for parts in lines_parts]

        print(commit["date"])  # , end='\r')
