# The World, 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/chiidaichii1-boop/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/chiidaichii1-boop/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A newspaper front page summing up the world's news of Wednesday 25 November 2026 in one image.

Bounty page: https://make.fun/bounty/news-image-20261125

## Stories in the image

- **Ukraine sinks Russian warship off Libya** — Kyiv confirms drone strikes on Russian vessels in the Gulf of Finland and off Benghazi; Moscow calls the attacks terrorism.
- **COP31 collapses without a deal** — the Antalya climate summit ends in deadlock as oil and gas producers block fossil-fuel phaseout.
- **CIA hit by cyberattack** — the US spy agency's classified systems breached, CNN reports.
- **Huawei guilty of stealing trade secrets** — a US jury convicts the Chinese telecom giant on 10 of 12 counts.
- **Nvidia surges 31% as Huang returns** — the chipmaker regains nearly $1 trillion in value in a day.
- **5.6 quake shakes Nepal** — a tremor strikes Koshi Province near the China border.

## How to run

```sh
python3 main.py
```

The program draws the front page with the Python standard library only (it encodes the PNG by hand with `zlib` and `struct` — no PIL, no network) and writes `entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output`). Two runs produce byte-identical output.

Referral code: `7g64vnx0`
