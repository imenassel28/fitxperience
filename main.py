import os, json, random, time
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

APP_DIR = os.path.dirname(__file__)
CLIENT_DIR = os.path.join(APP_DIR, "client")
DATA_DIR = os.path.join(APP_DIR, "data")

app = FastAPI(title="FitXperience — Fitness + IA + Gamificación")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/client", StaticFiles(directory=CLIENT_DIR), name="client")

def load_json(name):
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)

# Initialize OpenAI client (ensure OPENAI_API_KEY is set)
def get_openai():
    key = os.getenv("OPENAI_API_KEY", "")
    return OpenAI(api_key=key) if key else None

@app.get("/")
def root():
    # Serve landing by default
    return FileResponse(os.path.join(CLIENT_DIR, "landing.html"))

# ============== IA: PLAN ENTRENAMIENTO + NUTRICIÓN ==============
@app.post("/api/ai/plan")
async def ai_plan(
    goal: str = Form(...),
    level: str = Form(...),
    minutes: int = Form(...),
    equipment: str = Form("bodyweight"),
    injuries: str = Form(""),
    focus: str = Form("balanced")
):
    client = get_openai()
    if client:
        system = (
            "Eres un entrenador personal certificado y nutricionista. "
            "Genera planes seguros, progresivos y basados en evidencia. "
            "Nunca des consejos médicos; si hay dolor agudo, indica consultar a un profesional."
        )
        user = f"""Quiero un plan:
- Meta: {goal}
- Nivel: {level}
- Minutos: {minutes}
- Material: {equipment}
- Lesiones: {injuries or 'ninguna'}
- Foco: {focus}

Formato de salida EXACTAMENTE este JSON (sin texto extra):
{{
  "blocks": [
     {{"name":"...", "category":"hiit|strength|core|mobility|cardio", "duration":8, "video":"https://..."}}
  ],
  "macros_perkg": {{"protein_g":1.8, "carbs_g":3.5, "fat_g":0.9}},
  "meals": [
     {{"name":"...", "cal":500, "protein":35, "carbs":55, "fat":14}}
  ]
}}

- Los bloques deben sumar aproximadamente {minutes} minutos.
- Si hay lesiones, prioriza movilidad y core isométrico.
- Asegúrate de que el JSON sea válido.
"""
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                messages=[{"role":"system","content":system},{"role":"user","content":user}],
                response_format={"type":"json_object"}
            )
            data = json.loads(resp.choices[0].message.content)
            data.setdefault("blocks", [])
            data.setdefault("macros_perkg", {"protein_g":1.6,"carbs_g":3.0,"fat_g":0.9})
            data.setdefault("meals", [])
            if not data["blocks"]:
                data["blocks"] = [{"name":"Movilidad general","category":"mobility","duration":minutes,"video":""}]
            if not data["meals"]:
                data["meals"] = [{"name":"Yogur griego + frutos rojos + nueces","cal":380,"protein":23,"carbs":28,"fat":16}]
            return {"plan": data}
        except Exception as e:
            # Will fallback to mock below
            pass

    # Fallback (mock with local data) when no API key or error
    catalog = load_json("catalog.json")
    m = minutes
    blocks = []
    while m > 0:
        ex = random.choice(catalog["exercises"])
        dur = min(ex.get("suggested", 8), m)
        blocks.append({"name": ex["name"], "category": ",".join(ex["tags"]), "duration": dur, "video": ex.get("video","")})
        m -= dur
    return {"plan": {
        "blocks": blocks,
        "macros_perkg": {"protein_g":1.6,"carbs_g":3.0,"fat_g":0.9},
        "meals": random.sample(catalog["meals"], k=min(3, len(catalog["meals"])))
    }}

# ============== IA: CHAT ENTRENADOR ==============
@app.post("/api/ai/chat")
async def ai_chat(message: str = Form(...), goal: str = Form(""), level: str = Form("")):
    client = get_openai()
    if client:
        system = (
            "Eres un entrenador personal y nutricionista responsable. "
            "Responde con mensajes breves, accionables y seguros. "
            "No des diagnósticos médicos; si hay dolor agudo/lesión -> recomendar profesional."
        )
        user = f"Contexto -> Meta: {goal or 'no especificada'}, Nivel: {level or 'no especificado'}.\nUsuario: {message}"
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.6,
                messages=[{"role":"system","content":system},{"role":"user","content":user}]
            )
            reply = resp.choices[0].message.content.strip()
            return {"reply": reply}
        except Exception:
            pass
    # fallback simple
    lower = message.lower()
    if "dieta" in lower or "prote" in lower or "comer" in lower:
        return {"reply":"Apunta a 1.6–2.0 g/kg de proteína, hidratos alrededor del entreno y grasas saludables. ¿Generamos un plan y menú ahora?"}
    if "dolor" in lower or "lesión" in lower or "injur" in lower:
        return {"reply":"⚠️ Si hay dolor agudo o lesión, reduce intensidad y consulta a un profesional. Puedo ajustar tu plan a movilidad + core suave."}
    return {"reply":"Puedo crear tu plan por minutos y material. Dime tu objetivo (definición/masa/movilidad) y el tiempo disponible."}

# ============== Gamificación (demo JSON) ==============
PROFILES = os.path.join(DATA_DIR, "profiles.json")
if not os.path.exists(PROFILES):
    with open(PROFILES, "w", encoding="utf-8") as f:
        json.dump([], f)

@app.post("/api/progress")
async def progress(nick: str = Form(...), points: int = Form(...), mode: str = Form("workout")):
    data = json.load(open(PROFILES, "r", encoding="utf-8"))
    found = False
    for p in data:
        if p["nick"] == nick:
            p["points"] = p.get("points", 0) + int(points)
            p["last"] = int(time.time())
            found = True
            break
    if not found:
        data.append({"nick": nick, "points": int(points), "last": int(time.time())})
    json.dump(data, open(PROFILES, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return {"ok": True}

@app.get("/api/leaderboard")
def leaderboard():
    data = json.load(open(PROFILES, "r", encoding="utf-8"))
    data.sort(key=lambda x: (-x.get("points",0), -x.get("last",0)))
    return {"leaders": data[:50]}
