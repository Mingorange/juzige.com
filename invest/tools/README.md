# 橘子FM · 每日晨播（invest/）维护说明

静态站，部署于 juzige.com/invest/。页面版式为定型版（方案四「Apple 经典极简白」），不要改设计。

## 目录

- `index.html` — 单页应用（原生 JS），首页=最新一期，含历史日历/列表/搜索、全文折叠、常驻播放条、播完自动接下一期。
- `episodes.json` — 全部有音频期数数据（vol、date、one_liner、sentiment、full_text、audio、duration），按日期降序。
- `audio/<date>.mp3` — 各期音频，按日期命名。
- `tools/add_episode.py` — 每日新增一期工具。

## 数据规则

- 只收录有音频的期数；无音频期数不出现、不标注。
- VOL = 有音频期数按日期升序编号（最早一期为 VOL.1）。
- 口播稿（script_text）永不进 episodes.json、永不展示；不放倍速按钮。

## 每日新增一期

```bash
python3 tools/add_episode.py \
  --date 2026-11-19 \
  --one-liner "今日一句话摘要" \
  --full-text-file /path/to/full_text.md \
  --mp3 /path/to/2026-11-19.mp3 \
  --sentiment 偏冷
```

`--duration` 可省略（自动 ffprobe 读取）。同日期重跑会覆盖该期。然后在仓库根目录提交推送 `invest/` 的变更即可上线。
