# -*- coding: utf-8 -*-
"""帧同步确定性"""

from dataclasses import dataclass, field


@dataclass
class World:
    """帧同步世界状态。"""
    frame: int = 0
    positions: list = field(default_factory=list)
    history: list = field(default_factory=list)


def World:
    """class"""
    raise NotImplementedError("World 尚未实现")


def step(world, inputs):
    """推进一帧"""
    raise NotImplementedError("step 尚未实现")


def checksum(world):
    """状态校验和"""
    raise NotImplementedError("checksum 尚未实现")


def rollback(world, frame):
    """回滚并重放"""
    raise NotImplementedError("rollback 尚未实现")

