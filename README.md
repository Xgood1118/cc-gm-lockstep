# 帧同步确定性

一个保证同输入同结果、并支持回滚重放的帧同步核心。仅使用 Python 标准库。

## 保留签名

- `World`
- `step(world, inputs)`
- `checksum(world)`
- `rollback(world, frame)`

## 设计要点

- **确定性**：输入按键排序后应用，与字典遍历顺序无关；数值一律定点化为整数（浮点 ×1000 取整），不做任何浮点累加；状态用排序键的规范 JSON 序列化，校验和为 SHA-256，同状态必同值。
- **回滚**：`rollback(world, n)` 丢弃第 n 帧之后的输入日志与历史，从零重放前 n 帧，返回重放帧数 n；回滚后不保留任何未来帧状态，连续回滚同一帧结果相同。
- **分叉定位**：`first_divergence(a, b)` 返回两条校验和序列第一条不一致的帧号（0 起），一致返回 `None`。

## 自测

```
python -m pytest tests -q          # 12 passed
python -m lockstep.cli data/inputs.json --frames 30 --out checksums.json
```

## 运行结果（data/inputs.json，30 帧）

- 重放帧数：30
- 分叉帧号：无（重放与首跑逐位一致）
- 状态字节数：34
- 两次完整运行校验和序列：逐位一致（diff 为空）

每帧校验和：

| 帧 | 校验和 |
|---|---|
| 1 | 36d052e1bd4eb67a437a9c0e2959944d4803e18346c115cdcc01f3e311cb6682 |
| 2 | dca196e293d001682e75e2c7edf31de9009b8c94ac6099f619aa7f2e5387b63c |
| 3 | 09c962492d6ba0ee8938220b731498ea339f8ca6b5508ccd5c63ed8249eff588 |
| 4 | 399806822abf8506267b4b2b85cb5d2a6068b5a592b6efe1996e973226837382 |
| 5 | dbb79487a8855cd5ae5de7ec8d0b30e705be10785a25da94f99d82221e1e24c5 |
| 6 | caa889f8e27040e98087d1389c98cd6f2dfc4d0a6db13cac8ca78f39e4abc618 |
| 7 | ef9fb478930bff9f315d811dbf9d6f798c04d9c26bf34ae40a6ccaa9bf66a332 |
| 8 | 0730e5592ddef6c3ea4aa6e5ea3012c61d833b031684602a40d0fb588189fb9f |
| 9 | 205b5ae0cf859bef2109eaaf85075a344d0e7c43116b754ec0c2e11d1a558071 |
| 10 | 598e545ceeac080f3038bdc6b5b0e652141a54e3370ed0322ad0392e7caf03d8 |
| 11 | 7a0784f62e8cff0cc5c209d48727f6a0596119ec0bd2d07c20cf68c2e6e5a966 |
| 12 | 5411e748dfa1ad50361d169dc8ed5c67dab9764bb609ac5acbc3c96568b5e719 |
| 13 | 50c57d42638ef6dcce6589d9b3476dc61e18a21dc5b9d88b387dd93e05a08f27 |
| 14 | d6ab3ff9db7193f908a1d99c4b9e22c77201ea12cadcd870d74d3df56587303d |
| 15 | bf1342c54cfba1184f30e1dcb62046bf30242519373974e7a63adbe6dd95ef69 |
| 16 | 981b3caa9aa66012f38c047b08876359dc3fb0a5d05f84f4d4ebafa554fe8465 |
| 17 | 8e4bda8f69be340e564f709115e7661dcfd26f7b524c2f1d3b236ae22a50f39c |
| 18 | ef37ba89a82ffe71cbbda4274cfba4faf185b02e3462b6d585a9a5b68c1fe15e |
| 19 | 19ee2e77ff0859d5503807b5c8f173ca1d4d6e6a66f503d826a3219b0789ebfc |
| 20 | f880186893270511116e2e6125ea0a12c9de0c7542a0b9b809e7f8f8d30d277a |
| 21 | dd21fbdc2c327ec5f970f03714bee43b219a37782110454fc87bfa6d0eb9517d |
| 22 | ca9d3b3547e8aa48a7cf6c37a5f5266e113fe1829154b3fe53bde17eaf79f284 |
| 23 | d664addade7413e7273b9f5876b94667a019432c8ba2755e1715c07bf5dbabcf |
| 24 | 0e0b562e38f6cb4c5beaf9c9bf6f8f77fa54c38bd9b2c84920959459cab0a633 |
| 25 | ed9e709fcd03aa701dd2b9882b5cf5d84dd15929e4b4e3d3aaae89d4da9c5cfb |
| 26 | 3d234c5dbe8c1f873eef8dd641d64aa8cc4c27aaf279d118373015506c7fdd73 |
| 27 | 4592b74d793aa7d78ec32e471c2c853fd68650913d6846039f48844668cf646d |
| 28 | 80686cb5e6f4807e01a7c1114fcf1dfa42cbfc1329e2894a5cd7bc36e189fa5f |
| 29 | 558cf1230583a0ef231b9828ca29a63cd253b9f3f14a5783b540964810c03cbd |
| 30 | a3b6aa2ad383358026063ffdba681d9860cbf596a8c6a019026ad38b01524076 |

最终校验和：`a3b6aa2ad383358026063ffdba681d9860cbf596a8c6a019026ad38b01524076`（机器可读结果见 `checksums.json`）
