#!/usr/bin/env python3
"""每日更新工具：给「橘子FM · 每日晨播」静态站新增一期。

用法：
    python3 add_episode.py --date 2026-11-19 \
        --one-liner "今日一句话摘要" \
        --full-text-file /path/to/full_text.md \
        --mp3 /path/to/2026-11-19.mp3 \
        [--sentiment 偏冷] [--duration 269.4]

行为：
    - 把 mp3 复制到 ../audio/<date>.mp3
    - 未给 --duration 时用 ffprobe 自动读取时长（读不到则为 null）
    - 插入 episodes.json，按日期升序自动重算 VOL（有音频期数从 1 编号）
    - 同日期已存在时覆盖该期（幂等，可重跑修正）
    - episodes.json 按日期降序保存（最新在前），与站点读取约定一致

完成后在 invest/ 目录里 git add/commit/push 即可上线。
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)  # invest/
EPISODES_JSON = os.path.join(SITE, "episodes.json")
AUDIO_DIR = os.path.join(SITE, "audio")


def probe_duration(mp3_path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", mp3_path],
            capture_output=True, text=True, timeout=30,
        )
        return round(float(out.stdout.strip()), 1)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description="新增一期每日晨播")
    ap.add_argument("--date", required=True, help="日期 YYYY-MM-DD")
    ap.add_argument("--one-liner", required=True, help="一句话摘要")
    ap.add_argument("--full-text-file", required=True, help="全文 Markdown 文件路径")
    ap.add_argument("--mp3", required=True, help="音频 mp3 路径")
    ap.add_argument("--sentiment", default="", help="情绪判断，如：偏冷")
    ap.add_argument("--duration", type=float, default=None, help="时长（秒），缺省用 ffprobe 读")
    args = ap.parse_args()

    if not os.path.exists(args.mp3):
        sys.exit(f"mp3 不存在：{args.mp3}")
    if not os.path.exists(args.full_text_file):
        sys.exit(f"全文文件不存在：{args.full_text_file}")

    with open(args.full_text_file, encoding="utf-8") as f:
        full_text = f.read()

    duration = args.duration if args.duration is not None else probe_duration(args.mp3)

    os.makedirs(AUDIO_DIR, exist_ok=True)
    dst_name = f"{args.date}.mp3"
    shutil.copyfile(args.mp3, os.path.join(AUDIO_DIR, dst_name))

    data = {"episodes": []}
    if os.path.exists(EPISODES_JSON):
        with open(EPISODES_JSON, encoding="utf-8") as f:
            data = json.load(f)

    episodes = [e for e in data.get("episodes", []) if e["date"] != args.date]
    episodes.append({
        "vol": 0,  # 下面统一重算
        "date": args.date,
        "one_liner": args.one_liner,
        "sentiment": args.sentiment,
        "full_text": full_text,
        "audio": f"audio/{dst_name}",
        "duration": duration,
    })
    episodes.sort(key=lambda e: e["date"])  # 升序编号 VOL
    for i, e in enumerate(episodes, start=1):
        e["vol"] = i
    episodes_desc = list(reversed(episodes))

    with open(EPISODES_JSON, "w", encoding="utf-8") as f:
        json.dump({"episodes": episodes_desc}, f, ensure_ascii=False, indent=1)

    new_ep = episodes_desc[0] if episodes_desc and episodes_desc[0]["date"] == args.date else None
    vol = next(e["vol"] for e in episodes if e["date"] == args.date)
    print(f"已添加 {args.date}（VOL.{vol}），音频 audio/{dst_name}，时长 {duration}s")
    print(f"episodes.json 现共 {len(episodes)} 期，最新 {episodes[-1]['date']} = VOL.{episodes[-1]['vol']}")


if __name__ == "__main__":
    main()
