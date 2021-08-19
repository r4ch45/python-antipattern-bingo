import os
import random
import pandas as pd
import textwrap

themes = [
    "correctness",
    "maintainability",
    "performance",
    "readability",
    "security",
]

theme_colors = {
    "None" : "grey",
    "correctness": "thistle",
    "maintainability": "plum",
    "performance": "lightsteelblue",
    "readability": "lightpink",
    "security": "lightblue",
}


def customwrap(s, width=15):
    return "<br>".join(textwrap.wrap(s, width=width))


def get_antipatterns_df(anti_pattern_src_path="../python-anti-patterns/src/"):

    df = pd.DataFrame()

    for theme in themes:
        patterns = []
        for root, dirs, files in os.walk(
            os.path.join(anti_pattern_src_path, theme), topdown=False
        ):
            for name in files:
                if not name == "index.rst":
                    patterns.append(name)

        df_theme = pd.DataFrame({"pattern": patterns})
        df_theme["theme"] = theme

        df = df.append(df_theme)

    return df


def get_antipattern_internet_path(pattern, theme):
    return (
        f"https://quantifiedcode.github.io/python-anti-patterns/{theme}/{pattern}.html"
    )


def wrangle_antipatterns_df(df):
    df["pattern"] = df["pattern"].str.replace(".rst", "", regex=False)

    df["internet_path"] = df.apply(
        lambda row: get_antipattern_internet_path(row["pattern"], row["theme"]), axis=1
    )
    df["readable_pattern"] = (
        df["pattern"].str.replace("_", " ", regex=False).apply(lambda x: customwrap(x))
    )

    df["color"] = df["theme"].map(theme_colors)

    return df
