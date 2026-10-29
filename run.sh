#!/usr/bin/env bash
# SIDUMKM — jalankan server di port 3000
cd "$(dirname "$0")"
[ -f sidumkm.db ] || python3 seed.py
exec python3 app.py
