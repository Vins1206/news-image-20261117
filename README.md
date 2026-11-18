[![make.fun](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/c/news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/Vins1206/news-image-20261117/rank.svg)](https://make.fun/c/news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/Vins1206/news-image-20261117/reward.svg)](https://make.fun/c/news-image-20261117)

# World News in One Picture — Tuesday 17 November 2026

A single 1024x1024 newspaper front page that sums up the world's news of
Tuesday 17 November 2026, drawn entirely by `main.py` (Python 3.13,
standard library only — no Pillow, no network, no fonts on disk).

## The day, in one image

- **Kerch Bridge falls** — a Ukrainian strike collapses a road span of the
  bridge to Crimea, the second day in a row; Russia hits two bridges in
  Kyiv.
- **Tankers hit by mines** — two tankers catch fire off the Strait of
  Hormuz.
- **Trump lands in Manila** — for ASEAN; Xi, Trump and Putin meet Thursday
  in Shenzhen.
- **Vulcan rocket fails** — 40 Amazon Leo satellites lost.
- Also today: JPMorgan blames a software bug for its banking outage,
  Nvidia reports after the close, Estonia shuts its Russia border.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` — a valid PNG, 1024x1024, well under 1 MiB.
The drawing is fully deterministic: two runs produce byte-identical files.

## How it is drawn

`main.py` renders the page into an RGB buffer with its own tiny
5x7 bitmap font and a pure-stdlib PNG encoder (`zlib` + `struct`):
masthead, a hero illustration of the broken Kerch Bridge, three story
panels (tanker, summit flags, rocket), and a footer news ticker.
