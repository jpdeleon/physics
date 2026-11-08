# Physics Video Notes

This book contains AI-generated summaries of physics and science videos.

Each chapter covers one video and is organized into three tabs:

- **Abstract** — a concise 1–2 paragraph overview
- **Key Insights** — 4–8 bullet points capturing the most important ideas
- **Deep Dive** — core concepts, equations in LaTeX, and concrete examples

---

To regenerate this book from a new list of videos, edit `settings.yml` and run:

```bash
uv run python -m pipeline.main
uv run jupyter-book build book/
```
