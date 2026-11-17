# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lockstep as mod  # noqa: E402
lockstep = mod

def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_hex(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def test_step_advances():
    w = lockstep.World()
    lockstep.step(w, {"a": 1})
    assert w.frame == 1


def test_checksum_stable():
    w = lockstep.World()
    c1 = lockstep.checksum(w)
    c2 = lockstep.checksum(w)
    assert c1 == c2
