import os
import random


def get_antipatterns_per_theme(anti_pattern_src_path="../python-anti-patterns/src/"):
    themes = [
        "correctness",
        "maintainability",
        "performance",
        "readability",
        "security",
    ]

    patterns_per_theme = {}

    for theme in themes:
        patterns = []
        for root, dirs, files in os.walk(
            os.path.join(anti_pattern_src_path, theme), topdown=False
        ):
            for name in files:
                if not name == "index.rst":
                    patterns.append(name)

        patterns_per_theme[theme] = patterns

    return patterns_per_theme


def pick_random_antipatterns(patterns_per_theme, n=9):

    vals = sum(patterns_per_theme.values(), [])

    if len(vals) < n:
        print("Sample larger than population so returning entire population")
        return vals
    else:
        return random.sample(vals, k=n)
