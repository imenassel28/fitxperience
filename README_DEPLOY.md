# Deploy en dominio: fitxperience.app

## 1) Render (HTTPS automático)
1. Sube este proyecto a un repo de **GitHub**.
2. En **Render.com → New → Web Service** → conecta tu repo.
3. Usa estos comandos (ya vienen en render.yaml):
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. En **Environment** añade `OPENAI_API_KEY`.
5. Deploy. Render te dará una URL temporal `https://fitxperience.onrender.com`.

## 2) Conectar el dominio **fitxperience.app**
1. En Render → tu servicio → **Settings → Custom Domains** → Add `fitxperience.app` y `www.fitxperience.app`.
2. Render te mostrará **registros DNS**:
   - **CNAME** para `www`: apunta a tu subdominio de Render.
   - **ALIAS / ANAME / A** para el root (`fitxperience.app`). Render suele dar un registro tipo A/ALIAS.
3. Ve a tu proveedor de dominio (Google Domains, Namecheap, Cloudflare, etc.) y crea esos registros.
4. Espera la propagación (normalmente 5-30 min). Render emitirá **SSL** automáticamente (Let's Encrypt).

## 3) PWA
- El manifest ya apunta a `https://fitxperience.app/` y `start_url` en `/client/index.html`.
- En móvil, abre la web y selecciona “Agregar a pantalla de inicio”.

## 4) SEO
- `robots.txt` y `sitemap.xml` incluidos. En Search Console, verifica el dominio y envía el sitemap:
  https://search.google.com/search-console
