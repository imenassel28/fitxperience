const $=s=>document.querySelector(s); const $$=s=>document.querySelectorAll(s);
$$('.nav a').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();const v=a.dataset.view;navigate(v);}));
function navigate(v){$$('.nav a').forEach(x=>x.classList.remove('active'));$(`.nav a[data-view="${v}"]`).classList.add('active');$$('.view').forEach(vw=>vw.classList.add('hidden'));$(`#view-${v}`).classList.remove('hidden'); if(v==='leaderboard') loadLeaders(); if(v==='nutrition') loadMeals(); if(v==='quests') renderQuests(); }
window.addEventListener('load',()=>navigate('home'));
$('#themeBtn')?.addEventListener('click',()=> document.documentElement.setAttribute('data-theme', document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark'));
$('[data-goto="coach"]')?.addEventListener('click',()=> navigate('coach'));

$('#btnPlan').addEventListener('click', async ()=>{
  const fd=new FormData();
  fd.set('goal',$('#goal').value||'definición');
  fd.set('level',$('#level').value);
  fd.set('minutes',$('#minutes').value||'24');
  fd.set('equipment',$('#equip').value);
  fd.set('injuries',$('#injuries').value);
  fd.set('focus',$('#focus').value);
  const r=await fetch('/api/ai/plan',{method:'POST',body:fd}); const data=await r.json();
  const box=$('#planBox'); box.innerHTML=''; let total=0;
  data.plan.blocks.forEach(b=>{ total+=b.duration; const div=document.createElement('div'); div.className='block'; div.innerHTML=`<div><b>${b.name}</b><div class="muted">${b.category} • ${b.duration} min</div></div><a class="btn ghost" target="_blank" href="${b.video}">▶</a>`; box.appendChild(div); });
  const meals = data.plan.meals.map(m=> `<li>${m.name} — ${m.cal} kcal • P ${m.protein}g • C ${m.carbs}g • G ${m.fat}g</li>`).join('');
  box.innerHTML += `<div class="card" style="margin-top:10px"><b>Macros por kg/día</b><div>Prot: ${data.plan.macros_perkg.protein_g} g • Carbs: ${data.plan.macros_perkg.carbs_g} g • Grasas: ${data.plan.macros_perkg.fat_g} g</div><b>Sugerencias</b><ul>${meals}</ul></div>`;
  await addPoints(Math.round(total/2));
});

$('#btnChat').addEventListener('click', async ()=>{
  const msg=$('#chatMsg').value.trim(); if(!msg) return; addMsg(msg,true);
  const fd=new FormData(); fd.set('message', msg); const r=await fetch('/api/ai/chat',{method:'POST',body:fd}); const data=await r.json(); addMsg(data.reply,false); $('#chatMsg').value='';
});
function addMsg(t,user){ const box=$('#chatBox'); const div=document.createElement('div'); div.className='msg '+(user?'user':'ai'); div.textContent=t; box.appendChild(div); box.scrollTop=box.scrollHeight; }

async function loadMeals(){ const r=await fetch('/client/manifest.json'); /* just to wait; replace if needed */ const r2=await fetch('/client/manifest.json'); const r3=await fetch('/api/ai/plan',{method:'POST',body:new FormData(Object.assign(document.createElement('form'),{goal:'definición',level:'Intermedio',minutes:18,equipment:'bodyweight'}))}); }
const QUESTS=[{id:'q1',title:'3 sesiones esta semana',points:50},{id:'q2',title:'2 entrenos de core',points:30},{id:'q3',title:'1 sesión HIIT',points:25}];
function renderQuests(){ const box=$('#questsBox'); box.innerHTML=''; QUESTS.forEach(q=>{ const div=document.createElement('div'); div.className='card'; div.innerHTML=`<b>${q.title}</b><div class="muted">+${q.points} pts</div><button class="btn" data-q="${q.id}">Completar</button>`; div.querySelector('button').onclick=async ()=>{ await addPoints(q.points); div.querySelector('button').textContent='¡Hecho!'; div.querySelector('button').disabled=true; loadLeaders(); }; box.appendChild(div); }); }

$('#saveNick').addEventListener('click',()=> localStorage.setItem('nick',$('#nick').value||'anon'));
async function addPoints(pts){ const nick=localStorage.getItem('nick')||'anon'; const fd=new FormData(); fd.set('nick',nick); fd.set('points',String(pts)); await fetch('/api/progress',{method:'POST',body:fd}); }
async function loadLeaders(){ const r=await fetch('/api/leaderboard'); const data=await r.json(); const box=$('#leaders'); box.innerHTML=''; data.leaders.forEach((u,i)=>{ const row=document.createElement('div'); row.className='plan block'; row.innerHTML=`<div><b>#${i+1} ${u.nick}</b></div><div>${u.points} pts</div>`; box.appendChild(row); }); }
