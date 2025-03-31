# -*- encoding: utf-8 -*-
# ======================================================================================
# Copyright and other protections apply. Please see the accompanying LICENSE file for
# rights and restrictions governing use of this software. All rights not expressly
# waived or licensed are reserved. If that file is missing or appears to be modified
# from its original, then please contact the author before viewing or using this
# software in any capacity.
# ======================================================================================

from __future__ import annotations

from graph import COLORS, Dot, digraph, graphviz_walk

from dyce import H, R
from dyce.r import ValueRoller
from tests.patches import patch_roll


def do_it(style: str) -> Dot:
    g = digraph(style)
    d6 = H(6)
    d8 = H(8)

    r_d6 = ValueRoller(
        d6,
        annotation={
            "node": dict(
                color=COLORS[style]["blue"],
                fontcolor=COLORS[style]["blue"],
                style="dashed",
            ),
            "edge": dict(
                color=COLORS[style]["blue"],
                fontcolor=COLORS[style]["blue"],
                style="dashed",
            ),
        },
    )
    r_d8 = ValueRoller(
        d8,
        annotation={
            "node": dict(
                color=COLORS[style]["red"],
                fontcolor=COLORS[style]["red"],
                style="dashed",
            ),
            "edge": dict(
                color=COLORS[style]["red"],
                fontcolor=COLORS[style]["red"],
                style="dashed",
            ),
        },
    )

    # ---- BEGIN MONKEY PATCH ----
    # For deterministic outcomes
    d6 = patch_roll(d6, 6, 1, 1)
    r_d6._value = d6
    d8 = patch_roll(d8, 5)
    r_d8._value = d8
    # ----- END MONKEY PATCH -----

    r_3d6 = (3 @ r_d6).annotate(r_d6.annotation)
    r_best_3_of_3d6_d8 = R.select_from_rs((slice(1, None),), r_3d6, r_d8)
    graphviz_walk(g, r_best_3_of_3d6_d8.roll())

    return g
