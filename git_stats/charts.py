import matplotlib.pyplot as plt


def draw_find_chart(filename: str, title: str, commits: dict[str, dict], names):
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    plt.title(title)
    dates = [commit["date"] for commit in commits.values()]
    for name in names:
        plt.plot(dates, [commit.get(name, 0) for commit in commits.values()], label=name)

    plt.legend()
    plt.ylabel('Count')
    plt.grid(axis="y", linestyle='--', alpha=0.5)
    # plt.show()
    fig.savefig(filename)
    plt.close()


def draw_files_chart(filename: str, title: str, commits: dict[str, dict]):
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    plt.title(title)
    dates = [commit["date"] for commit in commits.values()]
    plt.plot(dates, [len(commit["files"]) for commit in commits.values()])
    plt.ylabel('Count')
    # plt.show()
    fig.savefig(filename)
    plt.close()


def draw_size_chart(filename: str, title: str, commits: dict[str, dict]):
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    plt.title(title)
    dates = [commit["date"] for commit in commits.values()]
    plt.plot(dates, [sum(file["size"] for file in commit["files"]) / max(len(commit["files"]), 1) for commit in commits.values()])
    plt.ylabel('Bytes')
    fig.savefig(filename)
    plt.close()
