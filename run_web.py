"""Start the Landscape Generator web app on http://127.0.0.1:8162 (local only).

    pip install -r requirements-web.txt
    python run_web.py [--port 8162]
"""
import argparse

import uvicorn

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8162)
    a = ap.parse_args()
    print(f"Landscape Generator web app: http://127.0.0.1:{a.port}")
    uvicorn.run("terrain.web.app:app", host="127.0.0.1", port=a.port)
