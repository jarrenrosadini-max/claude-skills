#!/usr/bin/env python3
"""Find the main colors in one or more images, as hex codes and Roblox Color3 values.

Uses only ffmpeg + the Python standard library (no extra installs).

Usage:
  python3 palette.py image1.jpg [image2.png ...] [--top 8] [--crop x,y,w,h]

--crop takes fractions of the image (0-1), e.g. --crop 0,0.8,1,0.2 = bottom 20%,
useful for looking only at a HUD or button bar.
"""
import argparse
import subprocess
import sys
from collections import Counter

W = H = 96  # sample size; small = fast and cheap


def pixels(path, crop):
    vf = []
    if crop:
        x, y, w, h = crop
        vf.append(f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y}")
    vf.append(f"scale={W}:{H}")
    cmd = ["ffmpeg", "-loglevel", "error", "-i", path, "-vf", ",".join(vf),
           "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return [tuple(raw[i:i + 3]) for i in range(0, len(raw) - 2, 3)]


def bucket(c, step=24):
    return tuple(min(255, (v // step) * step + step // 2) for v in c)


def close(a, b, tol=40):
    return sum(abs(x - y) for x, y in zip(a, b)) < tol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--crop", type=lambda s: [float(v) for v in s.split(",")])
    a = ap.parse_args()

    counts, sums = Counter(), {}
    for img in a.images:
        try:
            for p in pixels(img, a.crop):
                k = bucket(p)
                counts[k] += 1
                s = sums.setdefault(k, [0, 0, 0])
                for i in range(3):
                    s[i] += p[i]
        except subprocess.CalledProcessError as e:
            print(f"skip {img}: {e.stderr.decode().strip()[:120]}", file=sys.stderr)
    total = sum(counts.values()) or 1

    picked = []  # [bucket, count, rgb sums]; merge near-duplicate colors
    for k, n in counts.most_common():
        for item in picked:
            if close(k, item[0]):
                item[1] += n
                item[2] = [x + y for x, y in zip(item[2], sums[k])]
                break
        else:
            picked.append([k, n, list(sums[k])])
    picked.sort(key=lambda t: -t[1])

    for _, n, s in picked[:a.top]:
        r, g, b = (round(v / n) for v in s)
        print(f"#{r:02X}{g:02X}{b:02X}  Color3.fromRGB({r}, {g}, {b})  {100 * n / total:4.1f}%")


if __name__ == "__main__":
    main()
