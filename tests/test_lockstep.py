# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lockstep as mod  # noqa: E402
lockstep = mod

INPUTS = [[{"a": 1}], [{"a": 2, "b": 1}], [{"a": 1}], [{"b": 3}], []]


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_hex(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def run(frames):
    w = lockstep.World()
    for fi in frames:
        lockstep.step(w, fi)
    return w


def test_step_advances():
    w = lockstep.World()
    lockstep.step(w, {"a": 1})
    assert w.frame == 1


def test_checksum_stable():
    w = lockstep.World()
    c1 = lockstep.checksum(w)
    c2 = lockstep.checksum(w)
    assert c1 == c2


def test_bit_identical_runs():
    """两次完整运行：校验和序列与状态字节逐位一致。"""
    w1 = run(INPUTS)
    w2 = run(INPUTS)
    assert w1.history == w2.history
    assert lockstep.state_bytes(w1) == lockstep.state_bytes(w2)


def test_dict_order_irrelevant():
    """同输入不同字典顺序，结果逐位一致。"""
    w1 = run([[{"a": 1, "b": 2, "c": 3}]])
    w2 = run([[{"c": 3, "a": 1, "b": 2}]])
    assert lockstep.checksum(w1) == lockstep.checksum(w2)
    assert lockstep.state_bytes(w1) == lockstep.state_bytes(w2)


def test_float_inputs_deterministic():
    """浮点输入定点化，两次运行逐位一致且不依赖累加顺序。"""
    w1 = run([[{"a": 0.1}, {"a": 0.2}]])
    w2 = run([[{"a": 0.2}, {"a": 0.1}]])
    assert lockstep.checksum(w1) == lockstep.checksum(w2)


def test_first_divergence_located():
    """校验和分叉定位：返回第一条不一致的帧号。"""
    w1 = run(INPUTS)
    w2 = run(INPUTS)
    assert lockstep.first_divergence(w1.history, w2.history) is None

    w3 = run([[{"a": 1}], [{"a": 999}], [{"a": 1}], [{"b": 3}], []])
    assert lockstep.first_divergence(w1.history, w3.history) == 1

    assert lockstep.first_divergence([], []) is None
    assert lockstep.first_divergence(["x"], ["x", "y"]) == 1


def test_rollback_equivalent_to_direct_run():
    """回滚到第 N 帧后，状态与直接跑到第 N 帧逐位相同。"""
    w = run(INPUTS)
    for n in range(len(INPUTS) + 1):
        wn = run(INPUTS)
        replayed = lockstep.rollback(wn, n)
        direct = run(INPUTS[:n])
        assert replayed == n
        assert lockstep.state_bytes(wn) == lockstep.state_bytes(direct)
        assert lockstep.checksum(wn) == lockstep.checksum(direct)


def test_rollback_reports_and_no_future_leak():
    """回滚报告重放帧数，且不保留未来帧的输入与校验和。"""
    w = run(INPUTS)
    replayed = lockstep.rollback(w, 2)
    assert replayed == 2
    assert w.frame == 2
    assert len(w.inputs_log) == 2
    assert len(w.history) == 2
    # 回滚后继续推进，与从头跑同输入一致
    lockstep.step(w, INPUTS[2])
    direct = run(INPUTS[:3])
    assert lockstep.checksum(w) == lockstep.checksum(direct)


def test_consecutive_rollback_same_frame():
    """连续回滚同一帧：每次结果都相同。"""
    w = run(INPUTS)
    lockstep.rollback(w, 2)
    first = lockstep.state_bytes(w)
    replayed = lockstep.rollback(w, 2)
    assert replayed == 2
    assert lockstep.state_bytes(w) == first
    # 回滚到第 0 帧也确定
    assert lockstep.rollback(w, 0) == 0
    assert w.frame == 0 and w.positions == []


def test_empty_inputs():
    """空输入：帧照常推进，结果确定。"""
    w1 = run([[], [], []])
    w2 = run([[], [], []])
    assert w1.frame == 3
    assert w1.positions == []
    assert w1.history == w2.history
    assert len(set(w1.history)) == 3  # 帧号进入状态，校验和逐帧不同
    # 空输入单帧
    w = lockstep.World()
    lockstep.step(w, [])
    assert w.frame == 1
    # 空输入上的回滚
    assert lockstep.rollback(w1, 1) == 1
    assert w1.frame == 1


def test_single_frame():
    w = run([[{"a": 1}]])
    assert w.frame == 1
    assert w.positions == [["a", 1]]
    assert lockstep.rollback(w, 1) == 1
    assert w.positions == [["a", 1]]


def test_rollback_out_of_range():
    w = run(INPUTS)
    for bad in (-1, len(INPUTS) + 1):
        try:
            lockstep.rollback(w, bad)
        except ValueError:
            pass
        else:
            raise AssertionError("越界回滚应抛 ValueError")
