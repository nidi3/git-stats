# git-stats

Charts how often regexes match, or how many files exist, over a git repository's history.

```
poetry install
poetry run git-stats <repo> [-a AFTER] [-b BEFORE] [-p {commit,day,week,month}] -f SEARCH ... [-x PATH ...] [-o FILE]
```

`-f` picks a group of regexes from `SEARCHES` in `git_stats/searches.py`, each regex becoming one line on the chart; `-f files` charts the number of files, `-f commits` the number of commits per period. Charts are written to `build/`. See `-h` for all options.

```
poetry run git-stats ~/code/app -a 2025-01-01 -x vendor -f types
```
