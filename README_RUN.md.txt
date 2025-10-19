Multi-Agent Stock Research Assistant - Quick Run

1) Create project folder and paste files into it.
2) Create a Python virtual environment and install dependencies:
   python -m venv venv
   source venv/bin/activate   # venv\\Scripts\\activate on Windows
   pip install -r requirements.txt

3) Copy .env.example -> .env and set keys. If you don't have API keys, the system uses safe fallbacks.

4) Run demo:
   python main.py AAPL

5) Output:
 - Prints a synthesized report to the terminal
 - Saves JSON report to output/<TICKER>_report.json
 - Caches AlphaV JSON responses (if used) under data/cache/
