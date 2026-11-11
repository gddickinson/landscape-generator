// Static-site data layer: answers api('/...') from the JSON files exported by scripts/build_static.py
// (every GET in STATIC_ENDPOINTS of terrain/web/app.py). Landscapes are generated in the browser by
// terrain_engine.js; only the Python run for arbitrary parameters (POST /generate) needs the local app.
const files = new Map();

export async function staticApi(path, body) {
  if (body) throw new Error('This needs the local app (Python server): see the README, "Run the web app".');
  const rel = path.split('?')[0].replace(/^\/+/, '');
  if (!files.has(rel)) {
    files.set(rel, fetch('api/' + rel + '.json').then(r => {
      if (!r.ok) throw new Error(`${r.status} ${rel}`);
      return r.json();
    }));
  }
  return files.get(rel);
}
