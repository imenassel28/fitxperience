# FitXperience PRO
Entrenador IA + NutriMatch + Gamificación. Landing + App + PWA + IA real (OpenAI).

## 1) Ejecutar local
```bash
pip install -r requirements.txt
# Windows: setx OPENAI_API_KEY "TU_API_KEY"
# macOS/Linux: export OPENAI_API_KEY="TU_API_KEY"
python -m uvicorn main:app --host 127.0.0.1 --port 8090
# Landing:  http://localhost:8090/
# App:      http://localhost:8090/client/index.html
```

## 2) Publicar en Render (gratis)
1. Sube el repo a GitHub.
2. En Render.com → New + Web Service → conecta tu repo.
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5. En **Env Vars** añade: `OPENAI_API_KEY=...`
6. Deploy. Obtendrás `https://tuapp.onrender.com` (con HTTPS).

## 3) PWA
- Manifest y service worker ya incluidos. En móvil → "Añadir a pantalla de inicio".

## 4) Estructura
- `client/landing.html` → Página de presentación (root `/`).
- `client/index.html` → App SPA.
- `client/styles.css`, `client/app.js` → UI/UX.
- `client/manifest.json`, `client/service-worker.js` → PWA.
- `data/catalog.json` → ejercicios y comidas.
- `main.py` → FastAPI + IA (OpenAI con fallback).

## 5) Notas
- Si no configuras `OPENAI_API_KEY`, la app usa un **fallback** local (mock).
- Para producción, migra `profiles.json` a una DB (SQLite/Supabase).
