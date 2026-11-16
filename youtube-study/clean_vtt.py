#!/usr/bin/env python3
"""Turn a YouTube .vtt caption file into compact plain text.

Removes timing lines, styling tags and the repeated lines that
auto-captions produce. Adds a [mm:ss] marker about once a minute.

Usage: python3 clean_vtt.py input.vtt output.txt
"""
import re
import sys

TIME = re.compile(r"(?:(\d+):)?(\d\d):(\d\d)\.\d+\s+-->")
TAG = re.compile(r"<[^>]+>")


def main(src, dst, every=60):
    out, last_line, next_mark, cur = [], None, 0, 0
    with open(src, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            m = TIME.match(line)
            if m:
                h, mi, s = (int(g or 0) for g in m.groups())
                cur = h * 3600 + mi * 60 + s
                continue
            if (not line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE"))
                    or line.isdigit()):
                continue
            text = TAG.sub("", line).strip()
            if not text or text == last_line:
                continue
            last_line = text
            if cur >= next_mark:
                out.append(f"\n[{cur // 60:02d}:{cur % 60:02d}]")
                next_mark = cur - cur % every + every
            out.append(text)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(" ".join(out).replace(" \n", "\n").strip() + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 clean_vtt.py input.vtt output.txt")
    main(sys.argv[1], sys.argv[2])
