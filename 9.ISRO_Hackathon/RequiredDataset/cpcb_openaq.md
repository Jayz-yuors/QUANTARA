Dataset: CPCB / OpenAQ (Air quality)

Official sources:

- OpenAQ API: https://openaq.org/
- CPCB (Central Pollution Control Board, India): https://cpcb.nic.in/

Notes / access:

- Air quality station data is typically accessed via APIs (OpenAQ) or national portals (CPCB). Download CSV/time-series and join to training samples by nearest station/time.
- For ingestion, fetch via API and store under `data/raw/air_quality/`.
