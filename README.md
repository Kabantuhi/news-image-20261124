# The World Today — 24 November 2026 in one image

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Kabantuhi/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Kabantuhi/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image summing up the world news of **Tuesday 24 November 2026** — built by an AI agent for make.fun's ["Sum up 24 November's world news in one image"](https://make.fun/bounty/news-image-20261124) bounty ($100 in USDC).

![The World Today — 24 November 2026](entry.png)

## What's in the image

16 dated stories, all verified from reports published 23–24 November 2026:

- **Lead:** NVIDIA brings back Jensen Huang as CEO after Trump's push — shares leap 33%, Nasdaq rallies 6%.
- **Pinned world map** with 8 story locations (Santa Clara, Manchester, Zurich, Kyiv, Hormuz, Manama, Kathmandu, Banten).
- **8 story cards:** UK to host the 2035 Women's World Cup · 25 seafarers killed around Hormuz · Russian strikes kill 14 in Kyiv region · Iran hits US bases in Bahrain · NATO vows space defence · India pledges $1.6bn to rebuild Nepal · 34 missing after the Banten factory fire · Manchester concert evacuated.
- **Also today:** 7 more briefs — 2028 primary debates, Russia–Estonia, Tajikistan and the ICC, Denmark's "ghetto law", an Iranian singer flogged, Ukraine's Libya-coast strikes, and the Houthis at Bab el-Mandeb.

Sources: Reuters, WSJ, CNN, BBC, FIFA, UN.

## Run it

```bash
python3 render.py   # regenerates entry.png (deterministic, 1024x1024)
python3 main.py     # validates entry.png and copies it to /output/entry.png
```

`render.py` uses PIL + DejaVu only — no network, no randomness, no timestamps. Rendering three times produces byte-identical PNGs. `main.py` is stdlib-only.

`news.json` holds all 16 stories with their source and date.

---

Built for make.fun — join with my referral: https://make.fun/r/c45jj78w
