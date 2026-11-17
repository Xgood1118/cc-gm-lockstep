# -*- coding: utf-8 -*-
"""帧同步确定性核心：同输入同结果，支持回滚重放。

确定性保证：
- 输入按键排序后应用，与字典遍历顺序无关；
- 数值一律定点化为整数，杜绝浮点累加顺序依赖；
- 状态序列化使用排序键的规范 JSON，校验和逐位一致。
"""

import copy
import hashlib
import json
from dataclasses import dataclass, field

__all__ = [
    "World",
    "step",
    "checksum",
    "rollback",
    "replay",
    "first_divergence",
    "state_bytes",
    "FIXED_POINT_SCALE",
]

# 浮点输入定点化比例：float 先乘 1000 再取整，之后全程整数运算
FIXED_POINT_SCALE = 1000


def _to_fixed(value):
    """把输入数值定点化为整数，避免任何浮点累加。"""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value * FIXED_POINT_SCALE))
    raise TypeError("不支持的输入数值类型: %r" % (type(value),))


def _normalize_inputs(inputs):
    """统一一帧的输入为 dict 列表；空输入（None/{} /[]）归一为可处理形态。"""
    if inputs is None:
        return []
    if isinstance(inputs, dict):
        return [inputs]
    return list(inputs)


@dataclass
class World:
    """帧同步世界状态。"""

    frame: int = 0
    positions: list = field(default_factory=list)      # [[name, x], ...] 始终按 name 排序
    history: list = field(default_factory=list)        # 每帧结束后的校验和
    inputs_log: list = field(default_factory=list)     # 每帧的规范化输入，用于重放/回滚


def state_bytes(world):
    """状态的规范序列化字节：排序键 JSON，逐位确定。"""
    state = {
        "frame": world.frame,
        "positions": [list(p) for p in world.positions],
    }
    return json.dumps(
        state, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def checksum(world):
    """状态校验和：对规范状态字节做 SHA-256，同状态必同值。"""
    return hashlib.sha256(state_bytes(world)).hexdigest()


def step(world, inputs):
    """推进一帧。

    inputs 可以是单个 dict、dict 列表或空（None/[]/{}）。
    同一帧内多个 dict 的同名按键按整数加法合并，应用时按键排序，
    因此结果与字典构造/遍历顺序无关。
    """
    frame_inputs = _normalize_inputs(inputs)
    deltas = {}
    for d in frame_inputs:
        for k, v in d.items():
            deltas[k] = deltas.get(k, 0) + _to_fixed(v)

    pos = {name: x for name, x in world.positions}
    for name in sorted(deltas):
        pos[name] = pos.get(name, 0) + deltas[name]

    world.positions = [[name, pos[name]] for name in sorted(pos)]
    world.frame += 1
    world.inputs_log.append(copy.deepcopy(frame_inputs))
    world.history.append(checksum(world))
    return world


def replay(inputs_log):
    """用一段输入日志从零重放，返回重放后的新世界。"""
    w = World()
    for frame_inputs in inputs_log:
        step(w, frame_inputs)
    return w


def rollback(world, frame):
    """回滚到第 frame 帧：丢弃未来帧，从零重放前 frame 帧。

    返回重放的帧数。回滚后 inputs_log 与 history 都被截断到第 frame 帧，
    不会泄漏未来帧的状态；连续回滚同一帧结果相同。
    """
    if not isinstance(frame, int) or not 0 <= frame <= world.frame:
        raise ValueError(
            "回滚目标帧 %r 越界（当前帧 %d）" % (frame, world.frame)
        )
    kept = copy.deepcopy(world.inputs_log[:frame])

    world.frame = 0
    world.positions = []
    world.history = []
    world.inputs_log = []

    for frame_inputs in kept:
        step(world, frame_inputs)
    return frame


def first_divergence(checksums_a, checksums_b):
    """返回两条校验和序列第一条分叉的帧号（0 起），完全一致返回 None。"""
    for i, (a, b) in enumerate(zip(checksums_a, checksums_b)):
        if a != b:
            return i
    if len(checksums_a) != len(checksums_b):
        return min(len(checksums_a), len(checksums_b))
    return None
