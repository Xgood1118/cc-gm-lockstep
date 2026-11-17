# 帧同步确定性

一个保证同输入同结果、并支持回滚重放的帧同步核心

## 保留签名

- `World`
- `step(world, inputs)`
- `checksum(world)`
- `rollback(world, frame)`

## 自测

```
python -m pytest tests -q
python -m lockstep.cli data/inputs.json --frames 30 --out checksums.json
```
