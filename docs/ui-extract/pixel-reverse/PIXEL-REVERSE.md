# 天使☆嚣嚣 RE-BOOT — 像素级 UI 反推

> 生成：2026-07-17T01:16:55.366062+00:00

## 方法

1. 静态强解已完成：`filtered-cn-jp/uipsd/*.pbd` + `*.tlg`
2. 复用 LimeLight `pbd_ns_parse.py` 提取图层几何 / 绑定
3. TLG5 解码为 PNG 精灵图（按钮烤字 / chrome）

## 统计

- PBD 解析：{'ok': 53, 'total': 53, 'hotspots': 3398}
- TLG 解码：{'ok': 71, 'total': 71}

## 分界面

### `title`
- `title.pbd` — layers=76 hotspots=37 bindings=6
- `title_locale_cn.pbd` — layers=28 hotspots=9 bindings=0

### `option`
- `option.pbd` — layers=104 hotspots=42 bindings=1
- `option_0simple.pbd` — layers=253 hotspots=121 bindings=24
- `option_1display.pbd` — layers=204 hotspots=84 bindings=34
- `option_2game1.pbd` — layers=187 hotspots=73 bindings=33
- `option_3game2.pbd` — layers=175 hotspots=65 bindings=30
- `option_4text.pbd` — layers=197 hotspots=78 bindings=26
- `option_5sound1.pbd` — layers=385 hotspots=204 bindings=30
- `option_5sound2.pbd` — layers=273 hotspots=200 bindings=38
- `option_6dialog.pbd` — layers=228 hotspots=138 bindings=3
- `option_7mouse.pbd` — layers=240 hotspots=154 bindings=10
- `option_8keyboard1.pbd` — layers=214 hotspots=120 bindings=3
- `option_9gamepad.pbd` — layers=269 hotspots=177 bindings=14
- `option_9gamepad2_assign.pbd` — layers=70 hotspots=40 bindings=0
- `option_cmds.pbd` — layers=56 hotspots=42 bindings=0
- `option_keyinput.pbd` — layers=297 hotspots=143 bindings=0

### `file`
- `file.pbd` — layers=123 hotspots=75 bindings=0
- `file_load.pbd` — layers=140 hotspots=88 bindings=8
- `file_quick.pbd` — layers=133 hotspots=87 bindings=4
- `file_save.pbd` — layers=140 hotspots=88 bindings=8

### `qconf`
- `qconf.pbd` — layers=68 hotspots=47 bindings=0
- `qconf_load.pbd` — layers=66 hotspots=47 bindings=1
- `qconf_qload.pbd` — layers=33 hotspots=19 bindings=0
- `qconf_qvsave.pbd` — layers=44 hotspots=31 bindings=4
- `qconf_save.pbd` — layers=95 hotspots=66 bindings=5
- `qconf_text.pbd` — layers=66 hotspots=34 bindings=5
- `qconf_volume.pbd` — layers=124 hotspots=68 bindings=11
- `qlpopup.pbd` — layers=31 hotspots=18 bindings=0
- `qvpopup.pbd` — layers=29 hotspots=15 bindings=0

### `window`
- `backlog.pbd` — layers=70 hotspots=36 bindings=5
- `dialog.pbd` — layers=107 hotspots=37 bindings=0
- `select.pbd` — layers=61 hotspots=47 bindings=0
- `window.pbd` — layers=37 hotspots=22 bindings=0
- `window_h.pbd` — layers=35 hotspots=22 bindings=0

### `extra`
- `bgmtitle.pbd` — layers=16 hotspots=10 bindings=0
- `chapter.pbd` — layers=16 hotspots=11 bindings=0
- `extra.pbd` — layers=33 hotspots=21 bindings=0
- `extra_cg.pbd` — layers=155 hotspots=79 bindings=5
- `extra_cgview.pbd` — layers=71 hotspots=50 bindings=0
- `extra_locale_cn.pbd` — layers=28 hotspots=16 bindings=0
- `extra_voice.pbd` — layers=195 hotspots=124 bindings=15
- `scnchart.pbd` — layers=119 hotspots=66 bindings=5

### `hud`
- `autoskipmark_img.pbd` — layers=45 hotspots=31 bindings=0
- `autoskipmark_pos.pbd` — layers=10 hotspots=7 bindings=0
- `btncustom.pbd` — layers=212 hotspots=139 bindings=0
- `clickglyph_img.pbd` — layers=31 hotspots=21 bindings=0
- `gesture_help.pbd` — layers=59 hotspots=55 bindings=0
- `phonechat.pbd` — layers=45 hotspots=19 bindings=0
- `quickmenu.pbd` — layers=79 hotspots=50 bindings=0
- `touchuibar.pbd` — layers=96 hotspots=78 bindings=0
- `touchvolume.pbd` — layers=45 hotspots=22 bindings=0
- `voicebar.pbd` — layers=28 hotspots=25 bindings=0

## 坐标可信度

- PBD 几何为启发式提取（与 LimeLight 相同限制）：部分 `cx/cy/cw/ch` 可能噪声
- **优先**使用 `*.hotspots.json` 中已过滤（宽高 1–1920、坐标 -100–2000）的条目
- 绑定字符串 `Current.cmd(...)` 用于语义映射（设置项 key）
- 精灵图见 `tlg-png/`，可与热区叠图校验

## 产物

| 路径 | 说明 |
|---|---|
| `pixel-reverse/pbd-layers/*.hotspots.json` | 每屏热区 |
| `pixel-reverse/pbd-layers/*.json` | 全量图层 |
| `pixel-reverse/tlg-png/` | TLG→PNG |
| `pixel-reverse/PIXEL-REVERSE.md` | 本说明 |
