import pathlib, json, os
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
p = pathlib.Path(DATA_DIR) / 'data.json'
if not p.exists():
    p.write_text(json.dumps({'ok': True}))
