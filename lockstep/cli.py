# -*- coding: utf-8 -*-
"""命令行：跑 N 帧，做完整重放校验，输出每帧校验和。"""

import argparse
import json

import lockstep as m


def main():
    ap = argparse.ArgumentParser(description="帧同步确定性")
    ap.add_argument("inputs", help="输入 JSON：每帧一个输入列表")
    ap.add_argument("--frames", type=int, default=30)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    with open(a.inputs, encoding="utf-8") as f:
        frames_data = json.load(f)

    # 第一次完整运行
    world = m.World()
    for i in range(a.frames):
        frame_inputs = frames_data[i] if i < len(frames_data) else []
        m.step(world, frame_inputs)

    # 第二次完整运行（重放校验）：同输入必须逐位一致
    world2 = m.replay(world.inputs_log)
    divergence = m.first_divergence(world.history, world2.history)

    result = {
        "frames": a.frames,
        "checksums": list(world.history),
        "replayed_frames": a.frames,
        "divergence_frame": divergence,
        "state_bytes": len(m.state_bytes(world)),
        "final_checksum": m.checksum(world),
        "replay_matches": divergence is None,
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("帧数: %d" % result["frames"])
    print("重放帧数: %d" % result["replayed_frames"])
    print("分叉帧号: %s" % ("无" if divergence is None else divergence))
    print("状态字节数: %d" % result["state_bytes"])
    print("最终校验和: %s" % result["final_checksum"])
    print("重放一致: %s" % result["replay_matches"])


if __name__ == "__main__":
    main()
