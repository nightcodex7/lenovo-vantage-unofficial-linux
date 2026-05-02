# UI/UX Issues — Screenshot Audit (All Pages)

| # | Page | Severity | Issue |
|---|------|----------|-------|
| A1 | All Pages | 🔴 Critical | Enabled card RowTitle/RowSubtitle still appear dimmed — Qt disabled-state cascade overrides QSS on all pages |
| A2 | All Pages | 🟡 Medium | Subtitle text wraps to 2–3 lines on every settings card (word wrap on, fixed card height) |
| A3 | Dashboard | 🟡 Medium | GPU Utilization bar invisible at 0% despite min-width fix (8px bar too thin for 6px chunk) |
| A4 | Power & System | 🟡 Medium | Section label says "GPU Section" — should say "GPU" |
| A5 | Power & System | 🟡 Medium | Multi-line subtitles on Power Mode, USB, Instant Boot, Flip To Start cards |
| A6 | Power & System | 🟢 Low | TDP labels use setProperty("class") not setObjectName — QSS selector won't match |
| A7 | Battery | 🟡 Medium | "Health %" stat label rendered in amber/yellow — inheriting bar chunk color from QProgressBar |
| A8 | Battery | 🟢 Low | Battery Conservation Mode subtitle too long, wraps to 2 lines |
| A9 | Settings | 🟡 Medium | Autorun card text is dimmed despite having an active blue combo |
| A10 | Settings | 🟢 Low | "Display Section" and "System Controls" section headers are visible but all rows disabled — confusing layout |
z