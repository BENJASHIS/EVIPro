import streamlit as st
import pandas as pd
import sqlite3, os, urllib.parse, hashlib
from datetime import date, datetime, timedelta
from diagnosticos_db import buscar_diagnostico, formato_opcion, DIAGNOSTICOS

# ══════════════════════════════════════════════════════════════
#  BASE DE DATOS SQLite
# ══════════════════════════════════════════════════════════════
DB_PATH = "evipro.db"

def _conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha       TEXT,
            hora        TEXT,
            nombres     TEXT,
            dni         TEXT,
            edad        INTEGER,
            sexo        TEXT,
            ocupacion   TEXT,
            ciudad      TEXT,
            altitud     INTEGER,
            motivo      TEXT,
            cie10       TEXT,
            cie11       TEXT,
            dx_nombre   TEXT,
            gad7        INTEGER,
            phq9        INTEGER,
            mejoria     INTEGER,
            cbd_mg_ml   REAL,
            volumen_ml  REAL,
            gotas_dia   INTEGER,
            ratio       TEXT,
            notas       TEXT,
            creado_en   TEXT DEFAULT (datetime('now','localtime'))
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente    TEXT,
            fecha       TEXT,
            hora        TEXT,
            especialidad TEXT,
            estado      TEXT DEFAULT 'Pendiente',
            notas       TEXT,
            creado_en   TEXT DEFAULT (datetime('now','localtime'))
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS farmacos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            medicamento TEXT,
            dosis       TEXT,
            frecuencia  TEXT,
            tiempo_uso  TEXT,
            FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
        )""")
        c.commit()

init_db()

def guardar_paciente(d: dict) -> int:
    with _conn() as c:
        cur = c.execute("""
        INSERT INTO pacientes
            (fecha,hora,nombres,dni,edad,sexo,ocupacion,ciudad,altitud,
             motivo,cie10,cie11,dx_nombre,gad7,phq9,mejoria,
             cbd_mg_ml,volumen_ml,gotas_dia,ratio,notas)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            d.get("fecha",""), d.get("hora",""),
            d.get("nombres",""), d.get("dni",""), d.get("edad",0),
            d.get("sexo",""), d.get("ocupacion",""), d.get("ciudad",""), d.get("altitud",0),
            d.get("motivo",""), d.get("cie10",""), d.get("cie11",""),
            d.get("dx_nombre",""), d.get("gad7",0), d.get("phq9",0), d.get("mejoria",0),
            d.get("cbd_mg_ml",0), d.get("volumen_ml",0), d.get("gotas_dia",0),
            d.get("ratio",""), d.get("notas","")
        ))
        c.commit()
        return cur.lastrowid

def guardar_farmacos(paciente_id: int, farmacos: list):
    with _conn() as c:
        for f in farmacos:
            c.execute("""
            INSERT INTO farmacos (paciente_id,medicamento,dosis,frecuencia,tiempo_uso)
            VALUES (?,?,?,?,?)
            """, (paciente_id, f.get("Medicamento",""), f.get("Dosis",""),
                  f.get("Frecuencia",""), f.get("Tiempo","")))
        c.commit()

def guardar_cita(d: dict):
    with _conn() as c:
        c.execute("""
        INSERT INTO citas (paciente,fecha,hora,especialidad,notas)
        VALUES (?,?,?,?,?)
        """, (d.get("paciente",""), d.get("fecha",""), d.get("hora",""),
              d.get("especialidad",""), d.get("notas","")))
        c.commit()

def actualizar_estado_cita(cita_id: int, estado: str):
    with _conn() as c:
        c.execute("UPDATE citas SET estado=? WHERE id=?", (estado, cita_id))
        c.commit()

def eliminar_cita(cita_id: int):
    with _conn() as c:
        c.execute("DELETE FROM citas WHERE id=?", (cita_id,))
        c.commit()

def leer_pacientes(busqueda: str = "") -> pd.DataFrame:
    q = f"%{busqueda}%" if busqueda else "%"
    with _conn() as c:
        df = pd.read_sql_query("""
        SELECT id, fecha, nombres, dni, edad, sexo, ciudad, motivo,
               cie10, cie11, dx_nombre, gad7, phq9, cbd_mg_ml, volumen_ml,
               gotas_dia, ratio, mejoria, creado_en
        FROM pacientes
        WHERE nombres LIKE ? OR dni LIKE ? OR cie10 LIKE ? OR motivo LIKE ?
        ORDER BY id DESC
        """, c, params=(q, q, q, q))
    return df

def leer_paciente_id(pid: int) -> dict:
    with _conn() as c:
        row = c.execute("SELECT * FROM pacientes WHERE id=?", (pid,)).fetchone()
        cols = [d[0] for d in c.execute("SELECT * FROM pacientes WHERE id=?", (pid,)).description] if row else []
    return dict(zip(cols, row)) if row else {}

def leer_citas(solo_pendientes: bool = False) -> pd.DataFrame:
    with _conn() as c:
        filtro = "WHERE estado='Pendiente'" if solo_pendientes else ""
        df = pd.read_sql_query(
            f"SELECT * FROM citas {filtro} ORDER BY fecha, hora", c)
    return df

def stats_db() -> dict:
    with _conn() as c:
        total   = c.execute("SELECT COUNT(*) FROM pacientes").fetchone()[0]
        hoy     = c.execute("SELECT COUNT(*) FROM pacientes WHERE fecha=?",
                            (datetime.now().strftime("%d/%m/%Y"),)).fetchone()[0]
        gad_avg = c.execute("SELECT AVG(gad7) FROM pacientes").fetchone()[0] or 0
        phq_avg = c.execute("SELECT AVG(phq9) FROM pacientes").fetchone()[0] or 0
        ultima  = c.execute("SELECT fecha,nombres FROM pacientes ORDER BY id DESC LIMIT 1").fetchone()
        citas_p = c.execute("SELECT COUNT(*) FROM citas WHERE estado='Pendiente'").fetchone()[0]
    return {"total":total,"hoy":hoy,"gad_avg":gad_avg,"phq_avg":phq_avg,
            "ultima":ultima,"citas_p":citas_p}

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EVIPro · Estación Vital Pro",
    layout="wide", page_icon="⚕",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
#  AUTENTICACIÓN
# ══════════════════════════════════════════════════════════════
def _hash(p): return hashlib.sha256(p.encode()).hexdigest()

def _usuarios():
    try:
        return {
            "medico":    {"pwd": _hash(st.secrets["usuarios"]["medico"]["pwd"]),    "rol": "medico"},
            "auditor":   {"pwd": _hash(st.secrets["usuarios"]["auditor"]["pwd"]),   "rol": "auditor"},
            "asistente": {"pwd": _hash(st.secrets["usuarios"]["asistente"]["pwd"]), "rol": "asistente"},
        }
    except:
        return {
            "medico":    {"pwd": _hash("nebula2025"),    "rol": "medico"},
            "auditor":   {"pwd": _hash("auditor2025"),   "rol": "auditor"},
            "asistente": {"pwd": _hash("asistente2025"), "rol": "asistente"},
        }

USUARIOS = _usuarios()
PERMISOS = {
    "medico":    ["📋 Historia Clínica", "⚡ Dashboard", "👥 Pacientes", "🌿 Emergencia Cannábica"],
    "auditor":   ["⚡ Dashboard", "👥 Pacientes", "📊 Auditoría"],
    "asistente": ["📅 Citas y Agenda", "👥 Pacientes"],
}
ROL_LABELS = {"medico": ("⚕ Médico","#00FFCC"), "auditor": ("📋 Auditor","#FFB300"), "asistente": ("🗂 Asistente","#BF00FF")}

for k,v in {"autenticado":False,"usuario":None,"rol":None,"intentos":0,"log":[]}.items():
    if k not in st.session_state: st.session_state[k] = v

def login(u, p):
    if st.session_state.intentos >= 5:
        st.error("🔒 Demasiados intentos. Recarga la página."); return
    usr = USUARIOS.get(u.lower().strip())
    if usr and usr["pwd"] == _hash(p):
        st.session_state.autenticado = True
        st.session_state.usuario = u.lower().strip()
        st.session_state.rol = usr["rol"]
        st.session_state.intentos = 0
        st.session_state.log.append({"u":u,"r":usr["rol"],"h":datetime.now().strftime("%d/%m %H:%M"),"a":"LOGIN"})
        st.rerun()
    else:
        st.session_state.intentos += 1
        st.error(f"❌ Incorrecto. Intentos restantes: {5 - st.session_state.intentos}")

def logout():
    st.session_state.log.append({"u":st.session_state.usuario,"r":st.session_state.rol,"h":datetime.now().strftime("%d/%m %H:%M"),"a":"LOGOUT"})
    for k in ["autenticado","usuario","rol"]: st.session_state[k] = False if k=="autenticado" else None
    st.rerun()

# ══════════════════════════════════════════════════════════════
#  PANTALLA DE LOGIN
# ══════════════════════════════════════════════════════════════
if not st.session_state.autenticado:
    st.markdown("""
    <style>
    .stApp{background:#080c0f!important;color:#dde8f0;}
    section[data-testid="stSidebar"]{display:none!important;}
    .stTextInput input{background:#0d1b26!important;border:1px solid #1e3a50!important;color:#dde8f0!important;border-radius:6px!important;}
    .stSelectbox>div>div{background:#0d1b26!important;border:1px solid #1e3a50!important;color:#dde8f0!important;border-radius:6px!important;}
    .stButton>button{border-radius:6px!important;}
    button[data-testid="baseButton-primary"]{background:linear-gradient(90deg,#1a9e8c,#0d7a6a)!important;color:#ffffff!important;border:none!important;font-weight:600!important;}
    label{color:#a8c4d4!important;}
    p{color:#a8c4d4!important;}
    </style>
    """, unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center;margin-bottom:2.5rem;'>
          <div style='font-size:2.8rem;margin-bottom:0.75rem;'>⚕</div>
          <div style='font-family:"DM Mono",monospace;font-size:1.5rem;letter-spacing:8px;color:#4dc8b4;'>EVIPro</div>
          <div style='font-size:0.7rem;letter-spacing:3px;color:#3a5a70;margin-top:0.5rem;'>PLATAFORMA CLÍNICA PRIVADA - ESTACIÓN VITAL PRO</div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            usuario = st.selectbox("Perfil de acceso", ["medico","auditor","asistente"],
                format_func=lambda x:{"medico":"⚕  Médico","auditor":"📋  Auditor","asistente":"🗂  Asistente"}[x])
            pwd = st.text_input("Contraseña", type="password", placeholder="••••••••••")
            sub = st.form_submit_button("Ingresar →", use_container_width=True, type="primary")
        if sub: login(usuario, pwd)
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("🔒 Acceso restringido — Solo personal autorizado · Estación Vital Pro Cusco, Perú")
    st.stop()

# ══════════════════════════════════════════════════════════════
#  ESTILOS — solo se ejecutan si el usuario está autenticado
# ══════════════════════════════════════════════════════════════
CSS = """
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
.stApp{background:#060d14;color:#d8e8f0;font-family:'DM Sans',sans-serif;}
section[data-testid="stSidebar"]{background:#040a10!important;border-right:1px solid #112233;}
p,li,.stMarkdown{font-size:1rem!important;line-height:1.85!important;color:#a8c4d4!important;}
label,.stRadio label,.stCheckbox label{font-size:0.95rem!important;color:#90b0c4!important;line-height:1.7!important;}
h1{color:#4dc8b4!important;font-size:1.5rem!important;font-weight:500!important;letter-spacing:0.5px!important;}
h2{color:#4dc8b4!important;font-size:1.25rem!important;font-weight:500!important;}
h3{color:#6ab8a8!important;font-size:1.05rem!important;font-weight:500!important;}
h4,h5{color:#6ab8a8!important;font-size:0.95rem!important;}
.stTextInput input,.stNumberInput input,.stTextArea textarea{background:#0d1b26!important;border:1px solid #1e3a50!important;color:#d8e8f0!important;border-radius:6px!important;font-size:0.95rem!important;padding:0.55rem 0.75rem!important;}
.stTextInput input:focus,.stNumberInput input:focus{border-color:#4dc8b4!important;outline:none!important;}
.stSelectbox>div>div{background:#0d1b26!important;border:1px solid #1e3a50!important;color:#d8e8f0!important;border-radius:6px!important;}
.stRadio>div{gap:0.4rem!important;}
div[role="radiogroup"]{gap:0.5rem!important;}
.stTabs [data-baseweb="tab-list"]{background:#040a10!important;border-bottom:1px solid #1e3a50!important;gap:0!important;}
.stTabs [data-baseweb="tab"]{font-size:0.9rem!important;font-weight:500!important;color:#5a8090!important;padding:0.75rem 1.25rem!important;border-radius:0!important;}
.stTabs [aria-selected="true"]{color:#4dc8b4!important;border-bottom:2px solid #4dc8b4!important;background:transparent!important;}
.stButton>button{border-radius:6px;font-family:'DM Sans',sans-serif;font-weight:500;font-size:0.9rem!important;transition:0.2s;border:1px solid #1e3a50;background:#0d1b26;color:#90b0c4;padding:0.55rem 1.2rem!important;}
.stButton>button:hover{border-color:#4dc8b4!important;color:#4dc8b4!important;}
button[data-testid="baseButton-primary"]{background:linear-gradient(135deg,#1a9e8c,#0d7a6a)!important;color:#ffffff!important;border:none!important;font-weight:600!important;}
button[data-testid="baseButton-primary"]:hover{background:linear-gradient(135deg,#22b89e,#0f8f7a)!important;}
.stAlert{border-radius:8px!important;font-size:0.9rem!important;}
[data-testid="metric-container"]{background:#0d1b26!important;border:1px solid #1e3a50!important;border-radius:8px!important;padding:1rem!important;}
[data-testid="stMetricValue"]{color:#4dc8b4!important;font-size:1.4rem!important;}
[data-testid="stMetricLabel"]{color:#5a8090!important;font-size:0.75rem!important;letter-spacing:1px!important;}
hr{border-color:#1e3a50!important;margin:1.25rem 0!important;}
.wizard-progress{background:#0d1b26;border:1px solid #1e3a50;border-radius:12px;padding:1rem 1.5rem;margin-bottom:1.5rem;}
.wizard-steps{display:flex;gap:0;align-items:center;}
.wstep{display:flex;flex-direction:column;align-items:center;flex:1;position:relative;}
.wstep-circle{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:600;font-family:'DM Mono',monospace;z-index:1;}
.wstep-done .wstep-circle{background:#1a9e8c;color:#ffffff;}
.wstep-active .wstep-circle{background:#0d1b26;border:2px solid #4dc8b4;color:#4dc8b4;}
.wstep-pending .wstep-circle{background:#0d1b26;border:1px solid #1e3a50;color:#3a5a70;}
.wstep-label{font-size:0.6rem;margin-top:5px;letter-spacing:1px;text-transform:uppercase;}
.wstep-done .wstep-label{color:#4dc8b4;}
.wstep-active .wstep-label{color:#d8e8f0;}
.wstep-pending .wstep-label{color:#3a5a70;}
.wstep-line{flex:1;height:1px;background:#1e3a50;margin:0 -1px;margin-bottom:18px;}
.wstep-line-done{background:#1a9e8c;}
.section-card-title{font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:3px;text-transform:uppercase;color:#4dc8b4;margin-bottom:1rem;padding-bottom:0.5rem;border-bottom:1px solid #1e3a50;}
.receta-container{background:#fff;padding:28px;border:1px solid #ccc;border-radius:8px;color:#333;}
.tabla-medica{width:100%;border-collapse:collapse;margin:8px 0;}
.tabla-medica th,.tabla-medica td{border:1px solid #999;padding:5px 8px;text-align:center;font-size:11px;}
.tabla-medica th{background:#f0f0f0;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DATOS GLOBALES
# ══════════════════════════════════════════════════════════════
try: MI_NUMERO = st.secrets["TELEFONO"]
except: MI_NUMERO = "51942185939"

CIUDADES = {"Cusco, PE":3399,"Lima, PE":154,"Arequipa, PE":2335,"Bogotá, CO":2625,
            "CDMX, MX":2240,"La Paz, BO":3640,"Quito, EC":2850,"Madrid, ES":657,"Denver, US":1609}
DB_FARMACOS = [
    "Pregabalina","Gabapentina","Tramadol","Morfina","Oxicodona","Codeína","Fentanilo",
    "Sertralina","Fluoxetina","Escitalopram","Paroxetina","Venlafaxina","Duloxetina",
    "Amitriptilina","Nortriptilina","Mirtazapina","Clomipramina",
    "Alprazolam","Clonazepam","Diazepam","Lorazepam","Midazolam","Bromazepam",
    "Clobazam","Valproato","Carbamazepina","Lamotrigina","Fenitoína","Levetiracetam",
    "Warfarina","Rivaroxabán","Apixabán","Clopidogrel","Aspirin",
    "Haloperidol","Risperidona","Quetiapina","Olanzapina","Aripiprazol","Clozapina",
    "Litio","Topiramato","Bupropión","Metilfenidato","Atomoxetina",
    "Metformina","Insulina","Glibenclamida","Sitagliptina",
    "Atorvastatina","Simvastatina","Losartán","Enalapril","Amlodipino","Propranolol",
    "Omeprazol","Pantoprazol","Metoclopramida",
    "Dexametasona","Prednisona","Metilprednisolona",
    "Ciclosporina","Tacrolimus","Metotrexato",
    "Rifampicina","Isoniacida","Ketoconazol","Fluconazol",
    "Ibuprofeno","Naproxeno","Celecoxib","Diclofenaco",
]

# Base de interacciones cannabinoides — nivel, mecanismo, recomendación
INTERACCIONES_CBD = {
    "Warfarina":       ("CRITICA","CYP2C9 — CBD inhibe metabolismo, aumenta efecto anticoagulante. Riesgo hemorragia","Contraindicado sin monitoreo INR semanal. Reducir dosis warfarina 30-50%."),
    "Clobazam":        ("CRITICA","CYP2C19 — CBD eleva niveles de N-desmetilclobazam hasta 3x. Sedación excesiva","Reducir dosis clobazam 25-50%. Monitorear sedación."),
    "Valproato":       ("CRITICA","Sinergismo — riesgo hepatotoxicidad aditiva. Elevación LFTs","Monitorear LFTs mensualmente. Precaución en niños."),
    "Carbamazepina":   ("ALTA",   "Inductor CYP3A4 — reduce niveles de CBD hasta 40%. Efecto bidireccional","Ajustar dosis CBD. Monitorear niveles plasmáticos."),
    "Fenitoína":       ("ALTA",   "CYP2C9/CYP2C19 — interacción bidireccional. Toxicidad fenitoína posible","Monitorear niveles fenitoína. Ajuste de dosis."),
    "Rifampicina":     ("ALTA",   "Potente inductor CYP3A4 — reduce drasticamente niveles CBD","Evitar combinación o aumentar dosis CBD significativamente."),
    "Ketoconazol":     ("ALTA",   "Inhibidor CYP3A4 — puede aumentar niveles CBD y THC","Reducir dosis cannabinoide 30%. Monitoreo estrecho."),
    "Clonazepam":      ("MODERADA","Depresores SNC — potenciación sedante. Riesgo caídas en adultos mayores","Usar con precaución. Reducir BZD si es posible."),
    "Alprazolam":      ("MODERADA","Depresores SNC — potenciación sedante","Monitorear sedación. Preferir dosis nocturna."),
    "Diazepam":        ("MODERADA","Depresores SNC — potenciación sedante","Monitorear. Puede permitir reducción de BZD."),
    "Tramadol":        ("MODERADA","Opioide — sinergismo analgésico y sedante. Riesgo síndrome serotoninérgico con ISRS","Útil para reducción opioide. Vigilar depresión respiratoria."),
    "Morfina":         ("MODERADA","Opioide — sinergismo. CBD puede reducir necesidad de morfina","Potencial opioid-sparing. Monitorear función respiratoria."),
    "Sertralina":      ("LEVE",   "ISRS — posible síndrome serotoninérgico con THC a dosis altas","Vigilar síntomas serotoninérgicos. CBD generalmente seguro."),
    "Fluoxetina":      ("LEVE",   "ISRS — inhibidor CYP2D6. Puede elevar niveles THC","Preferir CBD puro. Vigilar estado de ánimo inicial."),
    "Escitalopram":    ("LEVE",   "ISRS — interacción leve. CBD puede potenciar efecto ansiolítico","Combinación generalmente bien tolerada."),
    "Amitriptilina":   ("MODERADA","ATC — depresores SNC aditivos. CBD inhibe CYP2D6","Reducir dosis ATC si es posible. Monitorear sedación y cardiotoxicidad."),
    "Haloperidol":     ("MODERADA","Antipsicótico — CBD puede reducir efectos extrapiramidales","Potencial beneficio. Monitorear PA ortostática."),
    "Risperidona":     ("LEVE",   "Antipsicótico — interacción farmacodinámica leve","Vigilar metabolismo glucídico y sedación."),
    "Quetiapina":      ("MODERADA","Antipsicótico — sedación aditiva. CYP3A4 compartido","Monitorear sedación excesiva y QT."),
    "Clozapina":       ("ALTA",   "Antipsicótico — riesgo convulsiones. CBD comparte vía CYP1A2","Monitoreo estrecho. Potencial interacción significativa."),
    "Litio":           ("LEVE",   "Estabilizador ánimo — interacción directa no documentada","Monitorear función renal y niveles séricos de litio."),
    "Metformina":      ("LEVE",   "Antidiabético — sin interacción directa significativa","CBD puede tener efecto hipoglucemiante leve. Monitorear glucemia."),
    "Insulina":        ("LEVE",   "Hipoglucemiante — CBD puede potenciar efecto. Vigilar hipoglucemia","Monitorear glucemia. Posible necesidad de ajuste insulina."),
    "Dexametasona":    ("MODERADA","Corticoide — CYP3A4 compartido. Corticoides reducen niveles CBD","Aumentar dosis CBD si es necesario durante tratamiento corticoide."),
    "Ciclosporina":    ("ALTA",   "Inmunosupresor — CYP3A4. CBD aumenta niveles ciclosporina. Nefrotoxicidad","Monitoreo frecuente niveles ciclosporina y función renal."),
    "Tacrolimus":      ("ALTA",   "Inmunosupresor — CYP3A4. Riesgo nefrotoxicidad","Monitoreo estricto. Ajuste de dosis inmunosupresor."),
    "Propranolol":     ("LEVE",   "Betabloqueante — CBD puede potenciar efecto bradicardizante","Monitorear FC y PA. Útil en ansiedad y temblor."),
    "Omeprazol":       ("LEVE",   "IBP — CYP2C19 compartido. Interacción farmacocinética leve","Generalmente seguro. Sin ajuste necesario."),
    "Ibuprofeno":      ("LEVE",   "AINE — sin interacción directa significativa. CBD antiinflamatorio complementario","Combinación frecuente en dolor. Generalmente segura."),
    "Metilfenidato":   ("MODERADA","Estimulante — THC puede antagonizar efecto. CBD puede ayudar en TDAH","Preferir CBD puro o ratio CBD:THC alto en TDAH."),
    "Levetiracetam":   ("LEVE",   "Antiepiléptico — CBD sinérgico en epilepsia refractaria","Combinación con evidencia en Dravet y LGS. Monitorear."),
    "Lamotrigina":     ("LEVE",   "Antiepiléptico — sin interacción farmacocinética significativa conocida","Combinación generalmente segura. Vigilar rash."),
    "Prednisona":      ("MODERADA","Corticoide — CYP3A4. Similar a dexametasona","Monitorear eficacia CBD. Posible reducción durante tratamiento."),
    "Atorvastatina":   ("LEVE",   "Estatina — CYP3A4 compartido. Interacción leve","Sin ajuste necesario en dosis habituales de CBD."),
    "Bupropión":       ("MODERADA","Antidepresivo — inhibidor CYP2D6. THC puede reducir umbral convulsivo","Usar con precaución. Preferir CBD puro."),
}

COLORES_INTERACCION = {
    "CRITICA":  ("#FF2222","#3d0000","🚨"),
    "ALTA":     ("#FF8800","#2d1a00","⚠️"),
    "MODERADA": ("#FFB300","#2d2200","⚡"),
    "LEVE":     ("#4dc8b4","#003328","ℹ️"),
}

OPCIONES_RATIO = ["1:0 (CBD puro)","20:1","10:1","5:1","3:1","2:1","1:1","1:2","1:3","1:5","1:10","0:1 (THC puro)"]

PROTOCOLOS_INICIO = {
    "🌿 Inicio Gradual — CBD 20:1 · 10mg/ml · 10ml":  {"ratio":"20:1","mg":10,"ml":10,"gotas":1},
    "🌿 Estándar CBD — 20:1 · 15mg/ml · 30ml":        {"ratio":"20:1","mg":15,"ml":30,"gotas":2},
    "⚖️ Balanceado — 10:1 · 10mg/ml · 20ml":          {"ratio":"10:1","mg":10,"ml":20,"gotas":2},
    "⚖️ Equilibrado — 5:1 · 10mg/ml · 30ml":          {"ratio":"5:1","mg":10,"ml":30,"gotas":2},
    "🔴 THC Predominante — 1:5 · 10mg/ml · 20ml":     {"ratio":"1:5","mg":10,"ml":20,"gotas":1},
    "💊 Alta Concentración — 20:1 · 50mg/ml · 10ml":  {"ratio":"20:1","mg":50,"ml":10,"gotas":1},
    "🌙 Nocturno (insomnio) — 1:1 · 10mg/ml · 15ml":  {"ratio":"1:1","mg":10,"ml":15,"gotas":2},
    "🧠 Neurológico — CBD puro · 25mg/ml · 30ml":      {"ratio":"1:0 (CBD puro)","mg":25,"ml":30,"gotas":1},
    "🤕 Dolor Crónico — 3:1 · 15mg/ml · 30ml":        {"ratio":"3:1","mg":15,"ml":30,"gotas":2},
    "👴 Adulto Mayor — 20:1 · 5mg/ml · 30ml":         {"ratio":"20:1","mg":5,"ml":30,"gotas":1},
}

_defs = {"vacunas_val":[],"rc_val":"","mac_val":"","g_val":0,"p_val":0,"a_val":0,"c_val":0,
         "r_ratio":"20:1","r_mg":10,"r_ml":10,"r_gotas":1,"farmacos":[],"paso_hc":0,
         "hc_data":{}}

# ── HTML Calculadora cannabinoide (constante) ──
_CALC_HTML = """
<style>
body{margin:0;padding:4px;background:#0d1b26;font-family:system-ui,sans-serif;}
.calc-body{display:block;margin-top:0;border:0.5px solid #1e3a50;border-radius:10px;overflow:hidden;}
.calc-body.open{display:block;}
.calc-tabs{display:flex;border-bottom:0.5px solid #1e3a50;}
.calc-tab{flex:1;padding:9px 4px;font-size:11px;font-weight:500;color:#5a8090;
  background:#0a1520;border:none;cursor:pointer;border-bottom:2px solid transparent;transition:all 0.15s;}
.calc-tab.active{color:#4dc8b4;border-bottom-color:#4dc8b4;background:#0d1b26;}
.calc-panel{display:none;padding:16px;background:#0d1b26;}
.calc-panel.active{display:block;}
.calc-row2{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;}
.calc-row3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px;}
.calc-lbl{display:block;font-size:10px;color:#5a8090;margin-bottom:4px;letter-spacing:0.5px;}
.calc-inp{width:100%;padding:6px 10px;background:#060d14;border:0.5px solid #1e3a50;
  border-radius:6px;font-size:13px;color:#d8e8f0;font-family:'DM Mono',monospace;}
.calc-inp:focus{outline:none;border-color:#4dc8b4;}
.calc-res{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px;}
.calc-card{background:#060d14;border-radius:6px;padding:10px 12px;text-align:center;border:0.5px solid #1e3a50;}
.calc-val{font-size:17px;font-weight:500;color:#4dc8b4;font-family:'DM Mono',monospace;}
.calc-lbl2{font-size:10px;color:#3a5a70;margin-top:2px;letter-spacing:0.5px;}
.calc-alert{padding:8px 12px;border-radius:6px;font-size:12px;margin-top:8px;}
.calc-warn{background:rgba(255,179,0,0.08);color:#FFB300;border:0.5px solid rgba(255,179,0,0.3);}
.calc-ok{background:rgba(57,255,20,0.06);color:#5dcb42;border:0.5px solid rgba(57,255,20,0.2);}
.calc-info{background:rgba(77,200,180,0.07);color:#4dc8b4;border:0.5px solid rgba(77,200,180,0.25);}
.calc-tit-hdr{display:flex;align-items:center;gap:8px;margin-bottom:12px;}
.calc-dot{width:5px;height:5px;border-radius:50%;background:#4dc8b4;flex-shrink:0;}
.calc-sect{font-size:11px;font-weight:500;color:#d8e8f0;letter-spacing:1px;}
.calc-div{height:0.5px;background:#1e3a50;margin:12px 0;}
.tit-tbl{width:100%;border-collapse:collapse;font-size:12px;margin-top:8px;}
.tit-tbl th{text-align:left;padding:6px 8px;font-size:10px;color:#5a8090;
  border-bottom:0.5px solid #1e3a50;letter-spacing:0.5px;}
.tit-tbl td{padding:6px 8px;color:#a8c4d4;font-family:'DM Mono',monospace;font-size:12px;
  border-bottom:0.5px solid #0f1e2a;}
.tit-badge{display:inline-block;font-size:10px;padding:2px 8px;border-radius:20px;font-weight:500;}
.tb-ind{background:rgba(77,200,180,0.1);color:#4dc8b4;}
.tb-aj{background:rgba(255,179,0,0.1);color:#FFB300;}
.tb-mant{background:rgba(57,255,20,0.08);color:#5dcb42;}
.calc-note{font-size:11px;color:#3a5a70;margin-top:8px;}
</style>

<div id="calc-root">
  <div class="calc-body" id="calc-body">
    <div class="calc-tabs">
      <button class="calc-tab active" onclick="cTab(0)">Aceite / Gotas</button>
      <button class="calc-tab" onclick="cTab(1)">Flor seca</button>
      <button class="calc-tab" onclick="cTab(2)">Vape / Cartucho</button>
      <button class="calc-tab" onclick="cTab(3)">Tópico</button>
      <button class="calc-tab" onclick="cTab(4)">Titulación</button>
    </div>

    <div class="calc-panel active" id="cp0">
      <div class="calc-tit-hdr"><div class="calc-dot"></div><div class="calc-sect">PARÁMETROS DE LA FÓRMULA</div></div>
      <div class="calc-row3">
        <div><label class="calc-lbl">RATIO CBD:THC</label>
          <select class="calc-inp" id="c_ratio" onchange="cAceite()">
            <option>1:1</option><option>2:1</option><option>5:1</option>
            <option selected>10:1</option><option>20:1</option><option>1:0 (CBD puro)</option>
          </select></div>
        <div><label class="calc-lbl">CONCENTRACIÓN (mg/ml)</label>
          <input class="calc-inp" type="number" id="c_conc" value="10" min="1" max="500" oninput="cAceite()"></div>
        <div><label class="calc-lbl">VOLUMEN TOTAL (ml)</label>
          <input class="calc-inp" type="number" id="c_vol" value="30" min="5" max="100" oninput="cAceite()"></div>
      </div>
      <div class="calc-div"></div>
      <div class="calc-tit-hdr"><div class="calc-dot"></div><div class="calc-sect">DOSIFICACIÓN</div></div>
      <div class="calc-row2">
        <div><label class="calc-lbl">DOSIS INICIAL (gotas/día)</label>
          <select class="calc-inp" id="c_gotas" onchange="cAceite()">
            <option>1</option><option selected>2</option><option>3</option><option>4</option>
            <option>5</option><option>6</option><option>7</option><option>8</option>
            <option>9</option><option>10</option><option>12</option><option>14</option>
            <option>16</option><option>18</option><option>20</option><option>25</option>
            <option>30</option><option>40</option><option>50</option><option>60</option>
          </select></div>
        <div><label class="calc-lbl">DOSIS OBJETIVO (mg/día)</label>
          <select class="calc-inp" id="c_obj" onchange="cAceite()">
            <option>5</option><option>10</option><option>15</option><option selected>20</option>
            <option>25</option><option>30</option><option>40</option><option>50</option>
            <option>60</option><option>75</option><option>100</option><option>150</option>
            <option>200</option><option>300</option><option>400</option><option>500</option>
          </select></div>
      </div>
      <div class="calc-res" id="cr0"></div>
      <div id="ca0"></div>
    </div>

    <div class="calc-panel" id="cp1">
      <div class="calc-tit-hdr"><div class="calc-dot"></div><div class="calc-sect">FLOR SECA / INHALADA</div></div>
      <div class="calc-row3">
        <div><label class="calc-lbl">CANTIDAD (g)</label>
          <input class="calc-inp" type="number" id="f_g" value="1" min="0.1" max="50" step="0.1" oninput="cFlor()"></div>
        <div><label class="calc-lbl">% CANNABINOIDE</label>
          <input class="calc-inp" type="number" id="f_pct" value="15" min="0.1" max="35" step="0.1" oninput="cFlor()"></div>
        <div><label class="calc-lbl">VÍA DE ADMINISTRACIÓN</label>
          <select class="calc-inp" id="f_via" onchange="cFlor()">
            <option value="25">Vaporización (~25%)</option>
            <option value="10">Combustión (~10%)</option>
            <option value="35">Nebulización (~35%)</option>
          </select></div>
      </div>
      <div class="calc-res" id="cr1"></div>
      <div id="ca1"></div>
    </div>

    <div class="calc-panel" id="cp2">
      <div class="calc-tit-hdr"><div class="calc-dot"></div><div class="calc-sect">CARTUCHO / VAPE</div></div>
      <div class="calc-row3">
        <div><label class="calc-lbl">CAPACIDAD</label>
          <select class="calc-inp" id="v_cap" onchange="cVape()">
            <option value="0.5">0.5 g</option>
            <option value="1.0" selected>1.0 g</option>
            <option value="2.0">2.0 g</option>
          </select></div>
        <div><label class="calc-lbl">PUREZA DESTILADO (%)</label>
          <input class="calc-inp" type="number" id="v_pur" value="85" min="50" max="99" oninput="cVape()"></div>
        <div><label class="calc-lbl">PUFFS / DÍA</label>
          <select class="calc-inp" id="v_puffs" onchange="cVape()">
            <option>1</option><option>2</option><option>3</option><option>4</option>
            <option selected>5</option><option>6</option><option>8</option><option>10</option>
            <option>12</option><option>15</option><option>20</option><option>25</option><option>30</option>
          </select></div>
      </div>
      <div class="calc-res" id="cr2"></div>
      <div id="ca2"></div>
    </div>

    <div class="calc-panel" id="cp3">
      <div class="calc-tit-hdr"><div class="calc-dot"></div><div class="calc-sect">TÓPICO / CREMA</div></div>
      <div class="calc-row3">
        <div><label class="calc-lbl">PESO ENVASE (g)</label>
          <input class="calc-inp" type="number" id="t_peso" value="60" min="10" max="500" oninput="cTopico()"></div>
        <div><label class="calc-lbl">CANNABINOIDE TOTAL (mg)</label>
          <input class="calc-inp" type="number" id="t_mg" value="500" min="50" max="10000" oninput="cTopico()"></div>
        <div><label class="calc-lbl">APLICACIONES / DÍA</label>
          <select class="calc-inp" id="t_app" onchange="cTopico()">
            <option>1</option><option selected>2</option><option>3</option>
            <option>4</option><option>5</option><option>6</option>
          </select></div>
      </div>
      <div class="calc-res" id="cr3"></div>
      <div id="ca3"></div>
    </div>

    <div class="calc-panel" id="cp4">
      <div class="calc-tit-hdr"><div class="calc-dot"></div><div class="calc-sect">PROTOCOLO DE TITULACIÓN</div></div>
      <div class="calc-row3">
        <div><label class="calc-lbl">DOSIS INICIO (gotas/día)</label>
          <select class="calc-inp" id="ti_ini" onchange="cTit()">
            <option selected>1</option><option>2</option><option>3</option><option>4</option><option>5</option>
          </select></div>
        <div><label class="calc-lbl">INCREMENTO CADA (días)</label>
          <select class="calc-inp" id="ti_int" onchange="cTit()">
            <option>1</option><option>2</option><option selected>3</option><option>4</option>
            <option>5</option><option>7</option><option>10</option><option>14</option>
          </select></div>
        <div><label class="calc-lbl">TECHO MÁXIMO (gotas/día)</label>
          <select class="calc-inp" id="ti_max" onchange="cTit()">
            <option>5</option><option>8</option><option>10</option><option>12</option>
            <option>15</option><option selected>20</option><option>25</option><option>30</option>
            <option>40</option><option>50</option>
          </select></div>
      </div>
      <div id="tit-tbl"></div>
    </div>
  </div>
</div>

<script>
var _cOpen=true;
function calcToggle(){
  _cOpen=!_cOpen;
  document.getElementById('calc-body').classList.toggle('open',_cOpen);
  document.getElementById('fab-pulse').style.display=_cOpen?'none':'block';
  var lbl=document.getElementById('fab-label');
  lbl.style.display=_cOpen?'inline':'none';
  lbl.textContent=_cOpen?'— clic para cerrar':'';
  if(_cOpen) cAceite();
  // Ajustar altura del iframe dinámicamente
  var h = _cOpen ? document.body.scrollHeight + 20 : 58;
  window.parent.postMessage({type:'streamlit:setFrameHeight', height:h}, '*');
}
function cTab(n){
  document.querySelectorAll('.calc-tab').forEach(function(t,i){t.classList.toggle('active',i===n);});
  document.querySelectorAll('.calc-panel').forEach(function(p,i){p.classList.toggle('active',i===n);});
  if(n===1)cFlor(); if(n===2)cVape(); if(n===3)cTopico(); if(n===4)cTit();
}
function cCards(id,items){
  document.getElementById(id).innerHTML=items.map(function(x){
    return '<div class="calc-card"><div class="calc-val">'+x[0]+'</div><div class="calc-lbl2">'+x[1]+'</div></div>';
  }).join('');
}
function cAlert(id,msg,t){
  document.getElementById(id).innerHTML=msg?'<div class="calc-alert calc-'+t+'">'+msg+'</div>':'';
}
function freqLbl(d){
  if(d<=2)return '1 vez/día';
  if(d<=6)return '2 veces/día';
  if(d<=12)return '3 veces/día';
  return '4 veces/día';
}
function cAceite(){
  var conc=+document.getElementById('c_conc').value||10;
  var vol=+document.getElementById('c_vol').value||30;
  var gotas=+document.getElementById('c_gotas').value||2;
  var obj=+document.getElementById('c_obj').value||20;
  var mgxg=conc/20;
  var dDia=gotas*mgxg;
  var dur=Math.round((vol*20)/gotas);
  var gObj=mgxg>0?Math.round(obj/mgxg*10)/10:0;
  var tot=vol*conc;
  cCards('cr0',[
    [mgxg.toFixed(2)+' mg','por gota'],
    [dDia.toFixed(1)+' mg','dosis / día actual'],
    [gObj+' gotas','para '+obj+' mg/día'],
    [tot+' mg','total frasco'],
    [dur+' días','duración estimada'],
    [conc+' mg/ml','concentración'],
  ]);
  var al='',at='info';
  if(dDia>50){al='Dosis alta (>50 mg/día) — verificar tolerancia y ajuste clínico.';at='warn';}
  else if(dDia>=10){al='Dosis terapéutica en rango habitual.';at='ok';}
  else{al='Dosis de inducción — monitorear respuesta inicial.';at='info';}
  cAlert('ca0',al,at);
}
function cFlor(){
  var g=+document.getElementById('f_g').value||1;
  var pct=+document.getElementById('f_pct').value||15;
  var bio=+document.getElementById('f_via').value||25;
  var tot=Math.round(g*1000*pct/100);
  var ef=Math.round(tot*(bio/100));
  var ses=Math.round(ef/3);
  cCards('cr1',[
    [tot+' mg','contenido teórico'],
    [bio+'%','biodisponibilidad'],
    [ef+' mg','activo estimado'],
    [ses+' mg','por sesión (3/día)'],
    [Math.round(ef/20)+' días','si 20 mg/día'],
    [g+' g','cantidad flor'],
  ]);
  cAlert('ca1','Biodisponibilidad variable ('+bio+'%). El calor destruye ~10% adicional. Valorar respuesta individual.','info');
}
function cVape(){
  var cap=+document.getElementById('v_cap').value||1;
  var pur=+document.getElementById('v_pur').value||85;
  var puffs=+document.getElementById('v_puffs').value||5;
  var tot=Math.round(cap*1000*pur/100);
  var pMg=Math.round(tot/175*10)/10;
  var dMg=Math.round(puffs*pMg*10)/10;
  var dur=Math.round(tot/(dMg||1));
  cCards('cr2',[
    [tot+' mg','cannabinoide total'],
    [pMg+' mg','por puff estimado'],
    [dMg+' mg','dosis / día'],
    [Math.round(cap*175)+' puffs','total estimado'],
    [dur+' días','duración'],
    [pur+'%','pureza destilado'],
  ]);
  cAlert('ca2','~175 puffs/g (referencia estándar). Variación según dispositivo y técnica de inhalación.','info');
}
function cTopico(){
  var peso=+document.getElementById('t_peso').value||60;
  var mg=+document.getElementById('t_mg').value||500;
  var app=+document.getElementById('t_app').value||2;
  var dens=Math.round(mg/peso*10)/10;
  var mgApp=Math.round(mg/peso*5*10)/10;
  var dias=Math.round(mg/(mgApp*app));
  cCards('cr3',[
    [dens+' mg/g','densidad'],
    [mgApp+' mg','por aplicación (~5 g)'],
    [Math.round(mgApp*app*10)/10+' mg','dosis / día'],
    [dias+' días','duración envase'],
    [mg+' mg','total formulación'],
    ['< 1%','absorción sistémica'],
  ]);
  cAlert('ca3','Absorción sistémica mínima (<1%). Acción principalmente local sobre receptores CB2 cutáneos.','info');
}
function cTit(){
  var ini=+document.getElementById('ti_ini').value||1;
  var int=+document.getElementById('ti_int').value||3;
  var max=+document.getElementById('ti_max').value||20;
  var rows='',dia=1,dosis=ini;
  while(dosis<=max){
    var fase=dosis<=3?'Inducción':dosis<=10?'Ajuste':'Mantenimiento';
    var bc=dosis<=3?'tb-ind':dosis<=10?'tb-aj':'tb-mant';
    rows+='<tr><td>Día '+dia+' – '+(dia+int-1)+'</td><td>'+dosis+' gotas</td><td>'+freqLbl(dosis)+'</td><td><span class="tit-badge '+bc+'">'+fase+'</span></td></tr>';
    dia+=int; dosis+=1;
  }
  document.getElementById('tit-tbl').innerHTML=
    '<table class="tit-tbl"><thead><tr><th>Período</th><th>Dosis / día</th><th>Frecuencia</th><th>Fase</th></tr></thead><tbody>'+rows+'</tbody></table>'+
    '<div class="calc-note" style="margin-top:8px;">Escalar solo si tolerancia adecuada. Suspender ante efectos adversos significativos.</div>';
}
</script>
"""

for k,v in _defs.items():
    if k not in st.session_state: st.session_state[k] = v

def wa_url(t): return f"https://wa.me/{MI_NUMERO}/?text={urllib.parse.quote(t)}"

def guardar_paciente(d):
    f = "bd_pacientes.csv"
    ex = os.path.isfile(f)
    with open(f,"a",newline="",encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=d.keys())
        if not ex: w.writeheader()
        w.writerow(d)

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    rl, rc = ROL_LABELS[st.session_state.rol]
    st.markdown(f"""
    <div style='text-align:center;padding:0.75rem 0 1.25rem;'>
      <div style='font-family:"DM Mono",monospace;font-size:0.95rem;letter-spacing:6px;color:#4dc8b4;'>⚕ EVIPRO</div>
      <div style='font-size:0.6rem;letter-spacing:2px;color:#3a5a70;margin-top:4px;'>ESTACIÓN VITAL PRO - v5.0</div>
    </div>
    <div style='background:rgba(0,255,204,0.04);border:1px solid rgba(0,255,204,0.15);
                border-radius:8px;padding:0.85rem;margin-bottom:1.25rem;'>
      <div style='font-size:0.6rem;letter-spacing:2px;color:#3a5a70;margin-bottom:5px;'>SESIÓN ACTIVA</div>
      <div style='font-size:1rem;font-weight:500;color:#dde8f0;'>{st.session_state.usuario.title()}</div>
      <div style='font-size:0.8rem;color:{rc};margin-top:3px;'>{rl}</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    modulo = st.radio("Nav", PERMISOS[st.session_state.rol], label_visibility="collapsed")
    st.divider()
    st.link_button("💬 WhatsApp", wa_url("Hola Dr., consulta desde EVIPro."), use_container_width=True)
    st.caption("Av. Infancia 410, Consultorio 2, Cusco")
    st.divider()
    if st.session_state.rol == "medico" and st.session_state.log:
        with st.expander("🔍 Accesos recientes"):
            for e in reversed(st.session_state.log[-8:]):
                st.caption(f"{'🟢' if e['a']=='LOGIN' else '🔴'} {e['h']} - {e['u']} - {e['r']}")
    if st.button("🚪 Cerrar sesión", use_container_width=True): logout()

# ══════════════════════════════════════════════════════════════
#  HELPER: barra de progreso wizard
# ══════════════════════════════════════════════════════════════
PASOS = [
    ("01","Filiación"),("02","Antecedentes"),("03","Enfermedad"),
    ("04","Psicometría"),("05","Seguimiento"),("06","Diagnóstico"),("07","Receta"),
]

def render_progress(paso_actual):
    circles = ""
    for i, (num, label) in enumerate(PASOS):
        if i < paso_actual:
            cls = "wstep-done"
            lbl = "✓"
        elif i == paso_actual:
            cls = "wstep-active"
            lbl = num
        else:
            cls = "wstep-pending"
            lbl = num
        line = f"<div class='wstep-line {'wstep-line-done' if i < paso_actual else ''}'></div>" if i < len(PASOS)-1 else ""
        circles += f"<div class='wstep {cls}'><div class='wstep-circle'>{lbl}</div><div class='wstep-label'>{label}</div></div>{line}"

    st.markdown(f"""
    <div class='wizard-progress'>
      <div class='wizard-steps'>{circles}</div>
    </div>
    """, unsafe_allow_html=True)

def nav_btns(paso, total=7):
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,3,1])
    with c1:
        if paso > 0 and st.button("← Anterior", use_container_width=True):
            st.session_state.paso_hc = paso - 1; st.rerun()
    with c2:
        pct = int((paso+1)/total*100)
        st.markdown(f"""
        <div style='text-align:center;font-size:0.75rem;color:#3a5a70;padding-top:0.6rem;'>
          Paso {paso+1} de {total} - {pct}% completado
        </div>""", unsafe_allow_html=True)
    with c3:
        if paso < total-1:
            if st.button("Siguiente →", use_container_width=True, type="primary"):
                st.session_state.paso_hc = paso + 1; st.rerun()

def card(titulo):
    st.markdown(f"<div class='section-card-title'>{titulo}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO HISTORIA CLÍNICA — WIZARD
# ══════════════════════════════════════════════════════════════
if modulo == "📋 Historia Clínica":

    paso = st.session_state.paso_hc
    render_progress(paso)

    # ── encabezado del paso ──
    titulos = [
        "👤 Datos de Filiación e Identidad",
        "📂 Antecedentes, Biometría e Inmunizaciones",
        "🤒 Enfermedad Actual y Farmacología",
        "🧠 Psicometría — GAD-7 y PHQ-9",
        "💊 Seguimiento y Farmacovigilancia",
        "🎯 Diagnóstico y Codificación",
        "📜 Receta Magistral y Dosificación",
    ]
    st.markdown(f"## {titulos[paso]}")
    st.divider()

    # ════════════════════════════════════════════════════════
    #  PASO 0 — FILIACIÓN
    # ════════════════════════════════════════════════════════
    if paso == 0:
        ahora = datetime.now()
        es_historico = st.toggle("📂 Modo Registro Histórico (fechas pasadas)")
        c1, c2, c3 = st.columns(3)
        if es_historico:
            fecha_hc = c1.date_input("📅 Fecha HC", value=ahora, format="DD/MM/YYYY")
            hora_hc  = c2.time_input("⏰ Hora HC", value=ahora.time())
            c3.warning("⚠️ Modo Histórico Activo")
        else:
            fecha_hc = c1.text_input("📅 Fecha", value=ahora.strftime("%d/%m/%Y"), disabled=True)
            hora_hc  = c2.text_input("⏰ Hora", value=ahora.strftime("%H:%M"), disabled=True)
            c3.success("🟢 Tiempo Real")

        st.markdown("<br>", unsafe_allow_html=True)
        card("IDENTIFICACIÓN DEL PACIENTE")
        f1, f2, f3 = st.columns(3)
        nombres  = f1.text_input("Nombres y Apellidos completos")
        dni      = f2.text_input("DNI / Pasaporte / CE")
        renpuc   = f3.text_input("Registro RENPUC / Licencia")

        f4, f5, f6 = st.columns(3)
        lugar_nac = f4.text_input("Lugar de Nacimiento")
        f_nac = f5.date_input("Fecha de Nacimiento", format="DD/MM/YYYY",
                              value=date(1990,1,1),
                              min_value=date(1900,1,1),
                              max_value=date.today())
        edad = (date.today() - f_nac).days // 365
        st.session_state.hc_data["f_nac_raw"] = f_nac
        # Guardar fecha raw para cálculo preciso en menores de 3 años
        st.session_state.hc_data["f_nac_raw"] = f_nac
        f6.markdown(f"""
        <div style='margin-top:28px;background:#0d1b26;border:1px solid #1e3a50;
                    border-radius:6px;padding:0.6rem;text-align:center;'>
            <div style='font-size:0.65rem;color:#3a5a70;letter-spacing:1px;'>EDAD CALCULADA</div>
            <div style='font-size:1.3rem;color:#4dc8b4;font-weight:600;'>{edad} años</div>
        </div>""", unsafe_allow_html=True)

        f7, f8, f9 = st.columns(3)
        sexo         = f7.selectbox("Sexo Biológico", ["Seleccione...","Femenino","Masculino","Otro"])
        estado_civil = f8.selectbox("Estado Civil", ["Soltero/a","Casado/a","Divorciado/a","Viudo/a","Conviviente"])
        religion     = f9.text_input("Religión / Creencias")

        st.markdown("<br>", unsafe_allow_html=True)
        card("DATOS DE CONTACTO")
        f10, f11, f12 = st.columns(3)
        ocupacion = f10.text_input("Ocupación / Profesión")
        telf      = f11.text_input("Teléfono o Celular")
        correo    = f12.text_input("Correo Electrónico")

        f13, f14, f15 = st.columns(3)
        dir_actual = f13.text_input("Dirección Actual")
        ciudad_sel = f14.selectbox("Ciudad de Residencia", ["Seleccione..."] + list(CIUDADES.keys()))
        altitud    = f15.number_input("Altitud (msnm)", value=CIUDADES.get(ciudad_sel, 0))
        if altitud > 2500:
            st.warning(f"⚠️ Paciente en altura: {altitud} msnm — considerar ajustes de dosificación.")

        st.markdown("<br>", unsafe_allow_html=True)
        card("PERFIL NUTRICIONAL BASAL")
        n1, n2, n3 = st.columns(3)
        dieta       = n1.selectbox("Tipo de Dieta", ["Omnívora","Vegetariana","Vegana","Keto","Paleo"])
        frec_comida = n2.number_input("Comidas / Día", 1, 10, 3)
        excesos     = n3.multiselect("Excesos en:", ["Azúcar","Carbohidratos","Proteínas","Grasas","Sodio"])

        st.markdown("<br>", unsafe_allow_html=True)
        if st.toggle("➕ Agregar Contactos de Emergencia"):
            card("CONTACTOS DE EMERGENCIA")
            e1,e2,e3 = st.columns(3)
            e1.text_input("Nombre (C1)"); e2.text_input("Parentesco (C1)"); e3.text_input("DNI (C1)")
            e4,e5,e6 = st.columns(3)
            e4.date_input("F. Nac (C1)", format="DD/MM/YYYY", key="fn1")
            e5.text_input("Correo (C1)"); e6.text_input("Celular (C1)")

        # Guardar en hc_data
        st.session_state.hc_data.update({
            "fecha_hc":fecha_hc,"nombres":nombres,"dni":dni,"edad":edad,
            "sexo":sexo,"altitud":altitud
        })
        nav_btns(paso)

    # ════════════════════════════════════════════════════════
    #  PASO 1 — ANTECEDENTES
    # ════════════════════════════════════════════════════════
    elif paso == 1:
        card("MOTIVO DE CONSULTA")
        motivo = st.text_area("Razón de la visita — relato del paciente", height=100,
                               placeholder="Describa brevemente el motivo de la consulta...")
        st.session_state.hc_data["motivo"] = motivo

        st.markdown("<br>", unsafe_allow_html=True)
        card("3.1 ANTROPOMETRÍA Y FUNCIONES VITALES")
        proto = st.radio("Protocolo:", ["Clínico Estándar","Deportivo Avanzado"], horizontal=True)
        b1,b2,b3,b4 = st.columns(4)
        peso  = b1.number_input("Peso (kg)", 0.0, 300.0, step=0.1)
        talla = b2.number_input("Talla (cm)", 0, 250)
        pa    = b3.text_input("P.A. (mmHg)", "120/80")
        fc    = b4.number_input("F.C. (lpm)", 40, 220, 75)
        b5,b6,b7 = st.columns(3)
        fr    = b5.number_input("F.R. (rpm)", 8, 40, 16)
        sat   = b6.number_input("Sat. O₂ (%)", 50, 100, 98)
        temp  = b7.number_input("Temp. (°C)", 30.0, 42.0, 36.5, step=0.1)

        altitud_p = st.session_state.hc_data.get("altitud", 0)
        if altitud_p > 2500 and sat < 90:
            st.warning(f"⚠️ Hipoxia detectada: {sat}% SpO₂ bajo para {altitud_p} msnm")
        elif altitud_p <= 2500 and sat < 95:
            st.error(f"🚨 Saturación crítica: {sat}% a nivel del mar")
        if temp >= 38.0:
            st.error(f"🔥 Fiebre: {temp} °C")

        imc = peso / ((talla/100)**2) if talla > 0 else 0
        # Guardar en hc_data para uso en componentes
        st.session_state.hc_data.update({"peso": peso, "talla": talla})
        if proto == "Deportivo Avanzado":
            d1,d2,_ = st.columns(3)
            cintura = d1.number_input("Cintura (cm)", 0.0)
            cadera  = d2.number_input("Cadera (cm)", 0.0)
            ict = cintura/talla if talla > 0 else 0
            st.metric("ICT", f"{ict:.2f}", delta="⚠ Riesgo" if ict > 0.5 else "✓ Normal")
        else:
            st.metric("IMC", f"{imc:.1f} kg/m²", delta="⚠ Sobrepeso/Obesidad" if imc >= 25 else "✓ Normal")

        st.markdown("<br>", unsafe_allow_html=True)
        card("3.2 HIDRATACIÓN Y NUTRICIÓN — PROTOCOLOS INTERNACIONALES")

        # ── Leer datos del paciente (del Paso 0 + lo recién capturado) ──
        edad_p     = int(st.session_state.hc_data.get("edad", 30))
        sexo_p     = st.session_state.hc_data.get("sexo", "Masculino")
        altitud_p  = int(st.session_state.hc_data.get("altitud", 0))
        peso_p     = float(st.session_state.hc_data.get("peso", peso if peso > 0 else 70))
        talla_p    = int(st.session_state.hc_data.get("talla", talla if talla > 0 else 170))
        embarazada = st.session_state.hc_data.get("embarazada", False)

        # ── Grupo etario automático ──
        if embarazada:             grupo_auto = "embarazada"
        elif edad_p < 1:           grupo_auto = "lactante"
        elif edad_p < 12:          grupo_auto = "pediatrico"
        elif edad_p < 18:          grupo_auto = "adolescente"
        elif edad_p < 60:          grupo_auto = "adulto"
        else:                      grupo_auto = "mayor"

        GRUPOS = {
            "lactante":    ("Lactante (<1 año)",     "#FF4444"),
            "pediatrico":  ("Pediátrico (1-11 años)","#FFB300"),
            "adolescente": ("Adolescente (12-17)",   "#4dc8b4"),
            "adulto":      ("Adulto (18-59 años)",   "#4dc8b4"),
            "mayor":       ("Adulto mayor (60+)",    "#6ab8a8"),
            "embarazada":  ("Embarazada",             "#bf7fff"),
        }
        g_label, g_color = GRUPOS[grupo_auto]

        # ── Protocolos activos según edad ──
        # Holliday-Segar: ideal para <18, válido hasta adulto
        # ACSM deportivo: adolescente y adulto
        # Rehidratación: todos
        # Nutrición: adolescente y adulto
        tab_hs    = edad_p < 60    # Holliday-Segar aplica más a pediatría/adulto joven
        tab_acsm  = edad_p >= 12   # Deportivo desde adolescentes
        tab_nutr  = edad_p >= 2    # Nutrición desde niños

        st.markdown(f"""<div style="background:#0d1b26;border:1px solid #1e3a50;border-radius:8px;
padding:0.65rem 1rem;margin-bottom:0.75rem;display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
<div style="font-size:0.6rem;color:#3a5a70;letter-spacing:1px;">DETECTADO</div>
<div style="font-size:1rem;font-weight:500;color:{g_color};">{g_label}</div>
<div style="font-size:0.8rem;color:#3a5a70;">{edad_p} años &nbsp;·&nbsp; {sexo_p} &nbsp;·&nbsp; {peso_p} kg &nbsp;·&nbsp; {talla_p} cm &nbsp;·&nbsp; {altitud_p} msnm</div>
</div>""", unsafe_allow_html=True)

        import streamlit.components.v1 as components
        _hn_html = """
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#0d1b26;font-family:system-ui,sans-serif;color:#a8c4d4;padding:6px;}
.hn-tabs{display:flex;border-bottom:1px solid #1e3a50;margin-bottom:0;}
.hn-tab{flex:1;padding:10px 4px;font-size:11px;font-weight:500;color:#5a8090;
  background:#0a1520;border:none;cursor:pointer;border-bottom:2px solid transparent;transition:all 0.15s;}
.hn-tab.active{color:#4dc8b4;border-bottom-color:#4dc8b4;background:#0d1b26;}
.hn-tab.disabled{color:#2a3a48;cursor:not-allowed;background:#060d14;}
.hn-panel{display:none;padding:14px 2px;}
.hn-panel.active{display:block;}
.hn-row2{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;}
.hn-row3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px;}
.hn-lbl{display:block;font-size:10px;color:#5a8090;margin-bottom:4px;letter-spacing:0.5px;}
.hn-inp{width:100%;padding:6px 10px;background:#060d14;border:1px solid #1e3a50;
  border-radius:6px;font-size:13px;color:#d8e8f0;font-family:monospace;}
.hn-inp:focus{outline:none;border-color:#4dc8b4;}
.hn-res{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px;}
.hn-res4{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px;}
.hn-card{background:#060d14;border-radius:6px;padding:10px 12px;text-align:center;border:1px solid #1e3a50;}
.hn-val{font-size:16px;font-weight:500;color:#4dc8b4;font-family:monospace;}
.hn-sub{font-size:10px;color:#3a5a70;margin-top:2px;letter-spacing:0.5px;}
.hn-alert{padding:8px 12px;border-radius:6px;font-size:12px;margin-top:8px;}
.hn-info{background:rgba(77,200,180,0.07);color:#4dc8b4;border:1px solid rgba(77,200,180,0.25);}
.hn-warn{background:rgba(255,179,0,0.08);color:#FFB300;border:1px solid rgba(255,179,0,0.3);}
.hn-ok{background:rgba(57,255,20,0.06);color:#5dcb42;border:1px solid rgba(57,255,20,0.2);}
.hn-danger{background:rgba(255,68,68,0.08);color:#FF4444;border:1px solid rgba(255,68,68,0.3);}
.hn-hdr{display:flex;align-items:center;gap:8px;margin-bottom:10px;}
.hn-dot{width:5px;height:5px;border-radius:50%;background:#4dc8b4;flex-shrink:0;}
.hn-sect{font-size:11px;font-weight:500;color:#d8e8f0;letter-spacing:1px;}
.hn-div{height:1px;background:#1e3a50;margin:12px 0;}
.prot-tbl{width:100%;border-collapse:collapse;font-size:12px;margin-top:8px;}
.prot-tbl th{text-align:left;padding:6px 8px;font-size:10px;color:#5a8090;
  border-bottom:1px solid #1e3a50;letter-spacing:0.5px;}
.prot-tbl td{padding:6px 8px;color:#a8c4d4;font-size:12px;border-bottom:1px solid #0f1e2a;}
.prot-tbl td.mono{font-family:monospace;color:#4dc8b4;}
.badge-prot{display:inline-block;font-size:10px;padding:2px 8px;border-radius:20px;font-weight:500;}
.b-teal{background:rgba(77,200,180,0.12);color:#4dc8b4;}
.b-amber{background:rgba(255,179,0,0.12);color:#FFB300;}
.b-red{background:rgba(255,68,68,0.1);color:#FF4444;}
.b-green{background:rgba(57,255,20,0.08);color:#5dcb42;}
.prot-nota{font-size:10px;color:#3a5a70;margin-top:6px;font-style:italic;}
</style>

<div class="hn-tabs" id="tabs">
  <button class="hn-tab active" onclick="hnTab(0)" id="tab0">Hidratación</button>
  <button class="hn-tab __HS_CLASS__" onclick="hnTabG(1)" id="tab1">Holliday-Segar</button>
  <button class="hn-tab __ACSM_CLASS__" onclick="hnTabG(2)" id="tab2">Deportivo ACSM</button>
  <button class="hn-tab" onclick="hnTab(3)" id="tab3">Rehidratación</button>
  <button class="hn-tab __NUTR_CLASS__" onclick="hnTabG(4)" id="tab4">Nutrición</button>
</div>

<!-- PANEL 0: HIDRATACIÓN -->
<div class="hn-panel active" id="hp0">
  <div class="hn-hdr"><div class="hn-dot"></div><div class="hn-sect">HIDRATACIÓN DIARIA — OMS / EFSA</div></div>
  <div class="hn-row3">
    <div><label class="hn-lbl">PESO (kg)</label>
      <input class="hn-inp" type="number" id="h_peso" value="__PESO__" min="1" max="300" step="0.1" oninput="calcHid()"></div>
    <div><label class="hn-lbl">GRUPO ETARIO</label>
      <select class="hn-inp" id="h_grupo" onchange="calcHid()">
        <option value="lactante" __SEL_LACT__>Lactante (&lt;1 año) — 150 ml/kg</option>
        <option value="pediatrico" __SEL_PED__>Pediátrico (1-11) — 80+20/kg</option>
        <option value="adolescente" __SEL_ADO__>Adolescente (12-17) — 40 ml/kg</option>
        <option value="adulto" __SEL_ADU__>Adulto (18-59) — 35 ml/kg</option>
        <option value="mayor" __SEL_MAY__>Adulto mayor (60+) — 30 ml/kg</option>
        <option value="embarazada" __SEL_EMB__>Embarazada — 35+300 ml/kg</option>
        <option value="lactancia">Lactancia — 35+500 ml/kg</option>
      </select></div>
    <div><label class="hn-lbl">SEXO</label>
      <select class="hn-inp" id="h_sexo" onchange="calcHid()">
        <option value="M" __SEL_M__>Masculino (EFSA 2500 ml)</option>
        <option value="F" __SEL_F__>Femenino (EFSA 2000 ml)</option>
      </select></div>
  </div>
  <div class="hn-row3">
    <div><label class="hn-lbl">KCAL/DIA estimado</label>
      <input class="hn-inp" type="number" id="h_kcal" value="2000" min="500" max="5000" oninput="calcHid()"></div>
    <div><label class="hn-lbl">ALTITUD (msnm)</label>
      <input class="hn-inp" type="number" id="h_alt" value="__ALT__" min="0" max="5000" oninput="calcHid()"></div>
    <div><label class="hn-lbl">TEMPERATURA AMBIENTAL</label>
      <select class="hn-inp" id="h_temp" onchange="calcHid()">
        <option value="1.0">Fría (&lt;15 C)</option>
        <option value="1.1" selected>Templada (15-25 C)</option>
        <option value="1.2">Calida (25-35 C)</option>
        <option value="1.35">Muy calurosa (&gt;35 C)</option>
      </select></div>
  </div>
  <div class="hn-res4" id="hr0"></div>
  <div class="hn-div"></div>
  <div class="hn-hdr"><div class="hn-dot"></div><div class="hn-sect">APORTE HIDRICO DE ALIMENTOS</div></div>
  <div class="hn-row3">
    <div><label class="hn-lbl">FRUTAS Y VERDURAS (porciones/dia)</label>
      <select class="hn-inp" id="h_fruta" onchange="calcHid()">
        <option value="0">0 porciones</option>
        <option value="150">1 porcion</option>
        <option value="300" selected>2-3 porciones</option>
        <option value="500">4-5 porciones</option>
        <option value="700">6+ porciones</option>
      </select></div>
    <div><label class="hn-lbl">SOPAS / LIQUIDOS EN COMIDAS</label>
      <select class="hn-inp" id="h_sopa" onchange="calcHid()">
        <option value="0">Sin sopas</option>
        <option value="200" selected>1 porcion</option>
        <option value="400">2 porciones</option>
        <option value="600">3+ porciones</option>
      </select></div>
    <div><label class="hn-lbl">AGUA LIBRE NECESARIA</label>
      <div class="hn-card" style="margin-top:0;"><div class="hn-val" id="h_neto">---</div>
        <div class="hn-sub">ml/dia neto</div></div></div>
  </div>
  <div id="ha0"></div>
</div>

<!-- PANEL 1: HOLLIDAY-SEGAR -->
<div class="hn-panel" id="hp1">
  <div class="hn-hdr"><div class="hn-dot"></div><div class="hn-sect">REGLA DE HOLLIDAY-SEGAR (1957) — MANTENIMIENTO 24h</div></div>
  <p style="font-size:11px;color:#5a8090;margin-bottom:10px;">
    Estandar de oro para calculo de liquidos de mantenimiento. <strong style="color:__AGECOLOR__">__AGELABEL__: __AGEREC__</strong>
  </p>
  <div class="hn-row2">
    <div><label class="hn-lbl">PESO (kg)</label>
      <input class="hn-inp" type="number" id="hs_peso" value="__PESO__" min="0.5" max="300" step="0.1" oninput="calcHS()"></div>
    <div><label class="hn-lbl">CONTEXTO CLINICO</label>
      <select class="hn-inp" id="hs_ctx" onchange="calcHS()">
        <option value="1.0">Mantenimiento estandar</option>
        <option value="1.12">Fiebre (+12% por cada C sobre 37.5)</option>
        <option value="0.8">Restriccion hidrica</option>
        <option value="1.3">Perdidas aumentadas (diarrea/vomito)</option>
        <option value="1.2">Postoperatorio</option>
      </select></div>
  </div>
  <div class="hn-res" id="hr1"></div>
  <div class="hn-div"></div>
  <div class="hn-hdr"><div class="hn-dot"></div><div class="hn-sect">REGLA 4-2-1 — HORARIO (ANESTESIOLOGIA)</div></div>
  <div id="hr1b"></div>
  <div id="ha1"></div>
</div>

<!-- PANEL 2: ACSM DEPORTIVO -->
<div class="hn-panel" id="hp2">
  <div class="hn-hdr"><div class="hn-dot"></div><div class="hn-sect">PROTOCOLO DEPORTIVO — ACSM</div></div>
  <p style="font-size:11px;color:#5a8090;margin-bottom:10px;">
    American College of Sports Medicine. <strong style="color:__AGECOLOR__">__AGELABEL__: __SPORTREC__</strong>
  </p>
  <div class="hn-row3">
    <div><label class="hn-lbl">PESO (kg)</label>
      <input class="hn-inp" type="number" id="d_peso" value="__PESO__" min="20" max="200" step="0.1" oninput="calcDep()"></div>
    <div><label class="hn-lbl">DURACION EJERCICIO</label>
      <select class="hn-inp" id="d_dur" onchange="calcDep()">
        <option value="30">30 min</option><option value="45">45 min</option>
        <option value="60" selected>60 min</option><option value="90">90 min</option>
        <option value="120">120 min</option><option value="180">180+ min</option>
      </select></div>
    <div><label class="hn-lbl">INTENSIDAD</label>
      <select class="hn-inp" id="d_int" onchange="calcDep()">
        <option value="0.5">Leve (caminar)</option>
        <option value="0.8" selected>Moderada (trotar)</option>
        <option value="1.2">Intensa (correr)</option>
        <option value="1.8">Alta competicion</option>
      </select></div>
  </div>
  <div class="hn-row2">
    <div><label class="hn-lbl">TEMPERATURA AMBIENTE</label>
      <select class="hn-inp" id="d_temp" onchange="calcDep()">
        <option value="0.8">Frio (&lt;15 C)</option>
        <option value="1.0" selected>Templado</option>
        <option value="1.3">Calor (&gt;25 C)</option>
        <option value="1.6">Calor extremo (&gt;35 C)</option>
      </select></div>
    <div><label class="hn-lbl">ALTITUD</label>
      <select class="hn-inp" id="d_alt" onchange="calcDep()">
        <option value="1.0">Nivel del mar</option>
        <option value="1.1">Media altura (1500-2500m)</option>
        <option value="1.25" __SEL_ALT__>Alta &gt;2500m (Cusco)</option>
      </select></div>
  </div>
  <div class="hn-res4" id="hr2"></div>
  <div id="ha2"></div>
</div>

<!-- PANEL 3: REHIDRATACION -->
<div class="hn-panel" id="hp3">
  <div class="hn-hdr"><div class="hn-dot"></div><div class="hn-sect">PROTOCOLO DE REHIDRATACION — OMS / OPS</div></div>
  <div class="hn-row3">
    <div><label class="hn-lbl">PESO (kg)</label>
      <input class="hn-inp" type="number" id="r_peso" value="__PESO__" min="3" max="200" step="0.1" oninput="calcReh()"></div>
    <div><label class="hn-lbl">GRADO DE DESHIDRATACION</label>
      <select class="hn-inp" id="r_grado" onchange="calcReh()">
        <option value="A">Plan A — Sin deshidratacion</option>
        <option value="B">Plan B — Moderada (3-9%)</option>
        <option value="C">Plan C — Severa (&gt;10%)</option>
        <option value="shock">Choque hipovolemico</option>
      </select></div>
    <div><label class="hn-lbl">VIA</label>
      <select class="hn-inp" id="r_via" onchange="calcReh()">
        <option value="oral">Oral / SRO</option>
        <option value="ev">Endovenosa</option>
        <option value="sng">SNG</option>
      </select></div>
  </div>
  <div class="hn-res" id="hr3"></div>
  <div id="hr3b" style="margin-top:10px;"></div>
  <div id="ha3"></div>
</div>

<!-- PANEL 4: NUTRICION -->
<div class="hn-panel" id="hp4">
  <div class="hn-hdr"><div class="hn-dot"></div><div class="hn-sect">REQUERIMIENTOS NUTRICIONALES — OMS / FAO / Harris-Benedict</div></div>
  <p style="font-size:11px;color:#5a8090;margin-bottom:10px;">
    <strong style="color:__AGECOLOR__">__AGELABEL__: __NUTREC__</strong>
  </p>
  <div class="hn-row3">
    <div><label class="hn-lbl">PESO (kg)</label>
      <input class="hn-inp" type="number" id="n_peso" value="__PESO__" min="5" max="300" step="0.1" oninput="calcNut()"></div>
    <div><label class="hn-lbl">TALLA (cm)</label>
      <input class="hn-inp" type="number" id="n_talla" value="__TALLA__" min="50" max="250" oninput="calcNut()"></div>
    <div><label class="hn-lbl">NIVEL DE ACTIVIDAD</label>
      <select class="hn-inp" id="n_act" onchange="calcNut()">
        <option value="1.2">Sedentario</option>
        <option value="1.375" selected>Ligero (1-3 dias/sem)</option>
        <option value="1.55">Moderado (3-5 dias/sem)</option>
        <option value="1.725">Activo (6-7 dias/sem)</option>
        <option value="1.9">Muy activo (atleta)</option>
      </select></div>
  </div>
  <div class="hn-row2">
    <div><label class="hn-lbl">OBJETIVO</label>
      <select class="hn-inp" id="n_obj" onchange="calcNut()">
        <option value="0.85">Deficit (perdida de peso)</option>
        <option value="1.0" selected>Mantenimiento</option>
        <option value="1.1">Superavit leve (ganancia)</option>
        <option value="1.3">Repleccion (desnutricion)</option>
        <option value="1.4">Post-cirugia / UCI</option>
      </select></div>
    <div><label class="hn-lbl">CONDICION ESPECIAL</label>
      <select class="hn-inp" id="n_cond" onchange="calcNut()">
        <option value="1.0">Ninguna</option>
        <option value="1.1">Embarazo 2do trim.</option>
        <option value="1.2">Embarazo 3er trim.</option>
        <option value="1.25">Lactancia materna</option>
        <option value="1.15">Patologia cronica</option>
        <option value="1.4">Quemaduras / trauma</option>
      </select></div>
  </div>
  <div class="hn-res4" id="hr4"></div>
  <div class="hn-div"></div>
  <div id="hr4b"></div>
  <div id="ha4"></div>
</div>

<script>
var _edad   = __EDAD__;
var _sexo   = "__SEXO__";
var _peso   = __PESO__;
var _grupo  = "__GRUPO__";
var _alt    = __ALT__;
var _hs_ok  = __HS_OK__;
var _acsm_ok= __ACSM_OK__;
var _nutr_ok= __NUTR_OK__;

// Recomendaciones por grupo etario
var REC = {
  lactante:   {age:"Lactante",color:"#FF4444",hs:"Referencia principal — 100-150 ml/kg/24h",sport:"No aplica en lactantes",nut:"110-120 kcal/kg (leche materna exclusiva)"},
  pediatrico: {age:"Pediatrico",color:"#FFB300",hs:"Referencia principal — formula clasica 100/50/20",sport:"Moderado: 400-600 ml extra por sesion",nut:"1200-1800 kcal/dia segun edad"},
  adolescente:{age:"Adolescente",color:"#4dc8b4",hs:"Valido — adulto joven",sport:"Igual que adulto; mayor cuidado con calor",nut:"2000-3200 kcal/dia segun sexo y actividad"},
  adulto:     {age:"Adulto",color:"#4dc8b4",hs:"Valido hasta 70 kg; NICE limita a 25-30 ml/kg",sport:"Protocolo estandar ACSM",nut:"Harris-Benedict + factor actividad"},
  mayor:      {age:"Adulto mayor",color:"#6ab8a8",hs:"Usar con precaucion — riesgo hipervolemia",sport:"Actividad fisica moderada recomendada",nut:"Proteina aumentada: 1.2-1.6 g/kg"},
  embarazada: {age:"Embarazada",color:"#bf7fff",hs:"Ajustar por ganancia de peso gestacional",sport:"Ejercicio moderado supervisado",nut:"+300 kcal/dia (2do-3er trim.), +500 kcal lactancia"},
};

function hnTab(n) {
  document.querySelectorAll('.hn-tab').forEach(function(t,i){t.classList.toggle('active',i===n);});
  document.querySelectorAll('.hn-panel').forEach(function(p,i){p.classList.toggle('active',i===n);});
  if(n===1)calcHS(); if(n===2)calcDep(); if(n===3)calcReh(); if(n===4)calcNut();
}

function hnTabG(n) {
  // Solo abre si la pestaña no esta deshabilitada
  var tab = document.getElementById('tab'+n);
  if(tab && tab.classList.contains('disabled')) return;
  hnTab(n);
}

function cards4(id,items){
  document.getElementById(id).innerHTML=items.map(function(x){
    return '<div class="hn-card"><div class="hn-val">'+x[0]+'</div><div class="hn-sub">'+x[1]+'</div></div>';
  }).join('');
}
function cards3(id,items){
  var el=document.getElementById(id);
  el.className='hn-res';
  el.innerHTML=items.map(function(x){
    return '<div class="hn-card"><div class="hn-val">'+x[0]+'</div><div class="hn-sub">'+x[1]+'</div></div>';
  }).join('');
}
function alert_(id,msg,t){
  document.getElementById(id).innerHTML=msg?'<div class="hn-alert hn-'+t+'">'+msg+'</div>':'';
}

function calcHid(){
  var p=+document.getElementById('h_peso').value||_peso;
  var gr=document.getElementById('h_grupo').value;
  var sx=document.getElementById('h_sexo').value;
  var kcal=+document.getElementById('h_kcal').value||2000;
  var alt=+document.getElementById('h_alt').value||0;
  var tF=+document.getElementById('h_temp').value||1.1;
  var fruta=+document.getElementById('h_fruta').value||300;
  var sopa=+document.getElementById('h_sopa').value||200;
  var altF=alt>3500?1.15:alt>2500?1.10:alt>1500?1.05:1.0;
  var factor=tF*altF;
  var base=0,efsa=0;
  if(gr==='lactante'){base=Math.round(p*150);efsa=800;}
  else if(gr==='pediatrico'){base=Math.round(80+p*20);efsa=p<5?1300:1600;}
  else if(gr==='adolescente'){base=Math.round(p*40);efsa=sx==='M'?2100:1900;}
  else if(gr==='adulto'){base=Math.round(p*35);efsa=sx==='M'?2500:2000;}
  else if(gr==='mayor'){base=Math.round(p*30);efsa=sx==='M'?2000:1600;}
  else if(gr==='embarazada'){base=Math.round(p*35+300);efsa=2300;}
  else{base=Math.round(p*35+500);efsa=2100;}
  var omsMl=Math.round(base*factor);
  var kcalMl=kcal;
  var recom=Math.max(omsMl,kcalMl);
  var neto=Math.max(0,recom-(fruta+sopa));
  document.getElementById('h_neto').textContent=Math.round(neto)+' ml';
  cards4('hr0',[
    [Math.round(omsMl)+' ml','OMS (peso x factor)'],
    [kcalMl+' ml','por kcal (1ml/kcal)'],
    [efsa+' ml','EFSA ingesta total'],
    [Math.round(recom)+' ml','RECOMENDADO/dia'],
  ]);
  var al='',at='info';
  if(alt>2500){al='Alta altitud '+alt+' msnm — +'+Math.round((altF-1)*100)+'% por hipoxia e hiperventilacion';at='warn';}
  else if(tF>1.1){al='Temperatura elevada — aumentar hidratacion en ambiente calido';at='warn';}
  else{al='Ingesta adecuada. Incluye aprox. 20% de agua proveniente de alimentos solidos.';at='ok';}
  alert_('ha0',al,at);
}

function calcHS(){
  var p=+document.getElementById('hs_peso').value||_peso;
  var ctx=+document.getElementById('hs_ctx').value||1.0;
  var ml24=0;
  if(p<=10)ml24=p*100;
  else if(p<=20)ml24=1000+(p-10)*50;
  else ml24=1500+(p-20)*20;
  ml24=Math.round(ml24*ctx);
  var mlh=0;
  if(p<=10)mlh=p*4;
  else if(p<=20)mlh=40+(p-10)*2;
  else mlh=60+(p-20)*1;
  mlh=Math.round(mlh);
  var gtt=Math.round(mlh*20/60);
  cards3('hr1',[
    [ml24+' ml','Holliday-Segar 24h'],
    [mlh+' ml/h','Regla 4-2-1 horario'],
    [gtt+' gtt/min','Goteo (20gtt/ml)'],
  ]);
  var det='<div class="hn-alert hn-info" style="font-size:11px;margin-top:8px;">';
  if(p<=10)det+=''+p+' kg x 100 ml = '+p*100+' ml';
  else if(p<=20)det+='10x100=1000 ml + '+(p-10).toFixed(1)+'x50='+(Math.round((p-10)*50))+' ml';
  else det+='10x100=1000 + 10x50=500 + '+(p-20).toFixed(1)+'x20='+Math.round((p-20)*20)+' ml';
  if(ctx!==1.0)det+=' — Factor x'+ctx+' = '+ml24+' ml';
  det+='</div>';
  document.getElementById('hr1b').innerHTML=det;
  var al='',at='ok';
  if(p>70){al='Adulto pesado — Holliday-Segar puede sobreestimar. Guia NICE recomienda maximo 25-30 ml/kg/dia en adultos hospitalizados.';at='warn';}
  if(al)alert_('ha1',al,at);
}

function calcDep(){
  var p=+document.getElementById('d_peso').value||_peso;
  var dur=+document.getElementById('d_dur').value||60;
  var intF=+document.getElementById('d_int').value||0.8;
  var tF=+document.getElementById('d_temp').value||1.0;
  var altF=+document.getElementById('d_alt').value||1.0;
  var preEj=Math.round(p*5);
  var sudH=Math.round(p*10*intF*tF*altF);
  var total=Math.round(sudH*(dur/60));
  var post=Math.round(total*1.5);
  cards4('hr2',[
    [preEj+' ml','pre-ejercicio (2h antes)'],
    [Math.round(sudH/60*15)+' ml','cada 15 min'],
    [total+' ml','total durante ejercicio'],
    [post+' ml','post-ejercicio'],
  ]);
  var al='',at='info';
  if(altF>1.2){al='Alta altitud — sudoracion basal aumentada. ACSM recomienda +25% sobre 2500 msnm.';at='warn';}
  else if(intF>=1.2){al='Ejercicio intenso — riesgo hiponatremia si solo agua. Considerar bebida con electrolitos.';at='warn';}
  else{al='Protocolo ACSM estandar. Ajustar segun diferencia de peso pre vs post ejercicio.';at='ok';}
  alert_('ha2',al,at);
}

function calcReh(){
  var p=+document.getElementById('r_peso').value||_peso;
  var g=document.getElementById('r_grado').value;
  var vol=0,tiempo=0,bolo=0;
  var plan='',sol='';
  if(g==='A'){vol=Math.round(p*5);plan='Plan A';sol='SRO preventivo, continuar alimentacion normal';}
  else if(g==='B'){vol=Math.round(p*75);tiempo=4;plan='Plan B';sol='SRO '+Math.round(p*75)+' ml en 4 horas';}
  else if(g==='C'){vol=Math.round(p*100);tiempo=3;bolo=20;plan='Plan C';sol='SSF 0.9% EV '+Math.round(p*100)+' ml en 3 horas';}
  else{bolo=20;vol=Math.round(p*20);plan='Choque';sol='Bolo SSF 20 ml/kg EV rapido — URGENCIA';}
  var ritmo=tiempo>0?Math.round(vol/tiempo):0;
  cards3('hr3',[
    [plan,'protocolo OMS'],
    [vol+' ml','volumen total'],
    [tiempo>0?ritmo+' ml/h':'Bolo rapido','ritmo'],
  ]);
  var rows='<table class="prot-tbl"><thead><tr><th>Parametro</th><th>Valor</th><th>Nota</th></tr></thead><tbody>';
  rows+='<tr><td>Solucion</td><td class="mono">'+plan+'</td><td>'+sol+'</td></tr>';
  if(tiempo>0)rows+='<tr><td>Duracion</td><td class="mono">'+tiempo+'h</td><td>'+Math.round(ritmo/4)+' ml cada 15 min</td></tr>';
  if(bolo>0)rows+='<tr><td>Bolo inicial</td><td class="mono">'+Math.round(p*bolo)+' ml</td><td>'+bolo+' ml/kg en 15-30 min</td></tr>';
  rows+='<tr><td>Reevaluar</td><td class="mono">c/1h</td><td>Signos de hidratacion y diuresis</td></tr>';
  rows+='</tbody></table>';
  document.getElementById('hr3b').innerHTML=rows;
  var msgs={A:'Sin deshidratacion. Mantener aporte oral y vigilar.',B:'Rehidratacion oral supervisada. Si no mejora en 4h pasar a Plan C.',C:'DESHIDRATACION GRAVE — acceso venoso inmediato. Monitoreo continuo.',shock:'EMERGENCIA HIPOVOLEMIA — acceso venoso x2. Valorar UCI.'};
  var tps={A:'info',B:'warn',C:'danger',shock:'danger'};
  alert_('ha3',msgs[g],tps[g]);
}

function calcNut(){
  var p=+document.getElementById('n_peso').value||_peso;
  var t=+document.getElementById('n_talla').value||170;
  var act=+document.getElementById('n_act').value||1.375;
  var obj=+document.getElementById('n_obj').value||1.0;
  var cond=+document.getElementById('n_cond').value||1.0;
  var tmb=_sexo==='M'?Math.round(66.5+13.75*p+5.003*t-6.75*_edad):Math.round(655.1+9.563*p+1.85*t-4.676*_edad);
  var tdee=Math.round(tmb*act*obj*cond);
  var prot=Math.round(p*(obj>=1.1?1.8:1.2));
  var grasas=Math.round(tdee*0.25/9);
  var cho=Math.round((tdee-prot*4-grasas*9)/4);
  cards4('hr4',[
    [tmb+' kcal','TMB (Harris-Benedict)'],
    [tdee+' kcal','TDEE recomendado/dia'],
    [prot+' g/dia','proteinas ('+Math.round(prot*4/tdee*100)+'%)'],
    [Math.round(tdee/1000*10)/10+' L/dia','agua (1ml/kcal)'],
  ]);
  var mac='<table class="prot-tbl"><thead><tr><th>Macronutriente</th><th>g/dia</th><th>kcal</th><th>%</th><th>Fuentes principales</th></tr></thead><tbody>';
  mac+='<tr><td>Proteinas</td><td class="mono">'+prot+'</td><td class="mono">'+prot*4+'</td><td class="mono">'+Math.round(prot*4/tdee*100)+'%</td><td>Carnes magras, huevos, legumbres</td></tr>';
  mac+='<tr><td>Carbohidratos</td><td class="mono">'+cho+'</td><td class="mono">'+cho*4+'</td><td class="mono">'+Math.round(cho*4/tdee*100)+'%</td><td>Cereales integrales, frutas, tuberculos</td></tr>';
  mac+='<tr><td>Grasas</td><td class="mono">'+grasas+'</td><td class="mono">'+grasas*9+'</td><td class="mono">'+Math.round(grasas*9/tdee*100)+'%</td><td>Aceite de oliva, aguacate, frutos secos</td></tr>';
  mac+='</tbody></table>';
  document.getElementById('hr4b').innerHTML=mac;
  var al='',at='ok';
  if(cond>1.1){al='Condicion especial activa — requerimientos aumentados. Considerar suplementacion dirigida.';at='warn';}
  else if(obj<1.0){al='Deficit calorico — mantener minimo '+tmb+' kcal/dia (TMB) para evitar catabolismo.';at='info';}
  else{al='Harris-Benedict revisado x factor actividad OMS/FAO 2004. Ajustar cada 4-8 semanas.';at='ok';}
  alert_('ha4',al,at);
}

// Deshabilitar pestanas segun edad
if(!_hs_ok)   document.getElementById('tab1').classList.add('disabled');
if(!_acsm_ok) document.getElementById('tab2').classList.add('disabled');
if(!_nutr_ok) document.getElementById('tab4').classList.add('disabled');

// Inicializar con el protocolo mas relevante para la edad
var initTab = _edad<18 ? 1 : (_edad>=12 ? 0 : 0);
hnTab(0);
calcHid();
if(_hs_ok) calcHS();
if(_acsm_ok) calcDep();
calcReh();
if(_nutr_ok) calcNut();
</script>
"""

        # Recomendaciones por grupo para insertar en el HTML
        _rec = {
            "lactante":    ("Lactante","#FF4444","100-150 ml/kg/24h","No aplica","110-120 kcal/kg"),
            "pediatrico":  ("Pediatrico","#FFB300","Formula 100/50/20 ml/kg","400-600 ml/sesion","1200-1800 kcal/dia"),
            "adolescente": ("Adolescente","#4dc8b4","Valido igual que adulto","Protocolo ACSM estandar","2000-3200 kcal/dia"),
            "adulto":      ("Adulto","#4dc8b4","Valido — NICE max 30 ml/kg","Protocolo ACSM estandar","Harris-Benedict + actividad"),
            "mayor":       ("Adulto mayor","#6ab8a8","Con precaucion — riesgo hipervolemia","Actividad moderada supervisada","Proteina 1.2-1.6 g/kg"),
            "embarazada":  ("Embarazada","#bf7fff","+300 ml/dia base","Ejercicio moderado supervisado","+300 kcal 2do-3er trim"),
        }
        _rl, _rc, _rhs, _rsport, _rnut = _rec.get(grupo_auto, _rec["adulto"])

        _hn_html = (_hn_html
            .replace("__PESO__",    str(round(peso_p, 1)))
            .replace("__TALLA__",   str(talla_p))
            .replace("__ALT__",     str(altitud_p))
            .replace("__EDAD__",    str(edad_p))
            .replace("__SEXO__",    "M" if "Masc" in sexo_p else "F")
            .replace("__GRUPO__",   grupo_auto)
            .replace("__HS_OK__",   "true" if tab_hs   else "false")
            .replace("__ACSM_OK__", "true" if tab_acsm else "false")
            .replace("__NUTR_OK__", "true" if tab_nutr else "false")
            .replace("__HS_CLASS__",   "" if tab_hs   else "disabled")
            .replace("__ACSM_CLASS__", "" if tab_acsm else "disabled")
            .replace("__NUTR_CLASS__", "" if tab_nutr else "disabled")
            .replace("__AGECOLOR__", _rc)
            .replace("__AGELABEL__", _rl)
            .replace("__AGEREC__",   _rhs)
            .replace("__SPORTREC__", _rsport)
            .replace("__NUTREC__",   _rnut)
            .replace("__SEL_LACT__", "selected" if grupo_auto=="lactante"    else "")
            .replace("__SEL_PED__",  "selected" if grupo_auto=="pediatrico"  else "")
            .replace("__SEL_ADO__",  "selected" if grupo_auto=="adolescente" else "")
            .replace("__SEL_ADU__",  "selected" if grupo_auto=="adulto"      else "")
            .replace("__SEL_MAY__",  "selected" if grupo_auto=="mayor"       else "")
            .replace("__SEL_EMB__",  "selected" if grupo_auto=="embarazada"  else "")
            .replace("__SEL_M__",    "selected" if "Masc" in sexo_p          else "")
            .replace("__SEL_F__",    "selected" if "Fem"  in sexo_p          else "")
            .replace("__SEL_ALT__",  "selected" if altitud_p > 2500          else "")
        )
        components.html(_hn_html, height=560, scrolling=True)


        st.markdown("<br>", unsafe_allow_html=True)
        card("3.3 INMUNIZACIONES — ESQUEMA NACIONAL PERÚ (NTS196-MINSA/DGIESP-2022)")

        edad_vac = st.session_state.hc_data.get("edad", edad if "edad" in dir() else 30)

        # ── Esquema completo por edad según MINSA Perú ──
        ESQUEMA_PERU = {
            "Recién nacido (0 días)": ["BCG","Hepatitis B (HvB) RN"],
            "2 meses": ["Pentavalente 1ra dosis","IPV (Polio inactivada) 1ra dosis","Neumococo conjugada 1ra dosis","Rotavirus 1ra dosis"],
            "4 meses": ["Pentavalente 2da dosis","IPV 2da dosis","Neumococo conjugada 2da dosis","Rotavirus 2da dosis"],
            "6 meses": ["Pentavalente 3ra dosis","IPV 3ra dosis","Neumococo conjugada 3ra dosis","Influenza pediátrica 1ra dosis"],
            "7 meses": ["Influenza pediátrica 2da dosis"],
            "12 meses": ["SPR (Sarampión-Parotiditis-Rubéola) 1ra dosis","Varicela 1ra dosis (prescripción médica)","Antiamarílica (zona selva)"],
            "15 meses": ["Neumococo conjugada 4ta dosis (refuerzo)"],
            "18 meses": ["IPV 4ta dosis (refuerzo 2024+)","DPT 1er refuerzo","APO (Antipolio oral) refuerzo"],
            "2 años": ["Influenza anual (continúa hasta 5 años)"],
            "4-5 años": ["DPT 2do refuerzo","APO 2do refuerzo","SPR 2da dosis"],
            "9-13 años": ["VPH — dosis única (niñas y niños desde 2023)"],
            "Adolescentes 10-19 años": ["Dt (Difteria-Tétanos) refuerzo","Influenza anual (grupos riesgo)"],
            "Adultos (20-59 años)": ["Influenza anual (riesgo/gestantes)","Dt cada 10 años","Hepatitis B (3 dosis si no vacunado)","COVID-19 según campaña vigente"],
            "Gestantes": ["Dt (2 dosis o 1 refuerzo)","Influenza (cualquier trimestre)","COVID-19 (recomendada)"],
            "Adultos mayores (60+ años)": ["Influenza anual","Neumococo 23v (PPSV23)","Dt cada 10 años","COVID-19 refuerzo"],
        }

        # Determinar vacunas esperadas según edad
        def vacunas_por_edad(e):
            esperadas = []
            if e <= 0: esperadas += ESQUEMA_PERU["Recién nacido (0 días)"]
            if e >= 0:
                for k,v in ESQUEMA_PERU.items():
                    if "2 meses" in k and e >= 0: esperadas += v
            if e >= 1:
                for k in ["4 meses","6 meses","7 meses","12 meses","15 meses","18 meses"]:
                    esperadas += ESQUEMA_PERU[k]
            if e >= 2: esperadas += ESQUEMA_PERU["2 años"]
            if e >= 4: esperadas += ESQUEMA_PERU["4-5 años"]
            if e >= 9: esperadas += ESQUEMA_PERU["9-13 años"]
            if e >= 10: esperadas += ESQUEMA_PERU["Adolescentes 10-19 años"]
            if e >= 20: esperadas += ESQUEMA_PERU["Adultos (20-59 años)"]
            if e >= 60: esperadas += ESQUEMA_PERU["Adultos mayores (60+ años)"]
            return list(dict.fromkeys(esperadas))  # dedup preservando orden

        vac_esperadas = vacunas_por_edad(edad_vac)
        nts_info = f"Esquema MINSA para {edad_vac} años — {len(vac_esperadas)} vacunas esperadas (NTS 196-MINSA/DGIESP-2022, mod. R.M. 218-2024)"
        st.info(nts_info)

        col_esq, col_priv = st.columns([3,1])

        with col_esq:
            st.markdown("**Vacunas del esquema MINSA esperadas para esta edad:**")
            if st.button("✅ Marcar todas como recibidas", key="vac_todas"):
                st.session_state.vacunas_val = vac_esperadas; st.rerun()
            vac_sel = st.multiselect(
                "Vacunas recibidas (MINSA):",
                options=vac_esperadas,
                default=[v for v in st.session_state.get("vacunas_val",[]) if v in vac_esperadas],
                key="vac_minsa"
            )
            faltantes = [v for v in vac_esperadas if v not in vac_sel]
            if faltantes:
                st.warning(f"⚠️ {len(faltantes)} vacuna(s) pendiente(s): {', '.join(faltantes[:4])}{'...' if len(faltantes)>4 else ''}")
            elif vac_sel:
                st.success("✅ Esquema MINSA completo para esta edad.")

        with col_priv:
            st.markdown("**Adicionales / Privadas:**")
            vac_extra = st.multiselect(
                "No incluidas en MINSA:",
                ["Varicela (universal)","Meningococo B","Meningococo ACWY",
                 "Hepatitis A","Neumococo 15v (PCV15)","Neumococo 20v (PCV20)",
                 "Dengue (Qdenga)","Herpes zóster (Shingrix)","Td acelular (Tdap)",
                 "Tifoidea","Rabia (pre-exposición)","Encefalitis japonesa"],
                key="vac_privadas"
            )

        with st.expander("📋 Ver esquema completo MINSA por etapa de vida"):
            for etapa, vacunas in ESQUEMA_PERU.items():
                st.markdown(f"**{etapa}**")
                for v in vacunas:
                    st.markdown(f"  - {v}")

        st.markdown("""
        <div style='font-size:0.75rem;color:#3a5a70;margin-top:0.5rem;'>
        Fuente: NTS196-MINSA/DGIESP-2022 - Modificada R.M.218-2024-MINSA - R.M.709-2025-MINSA<br>
        Nota: El esquema peruano sigue estándar OPS/OMS. Varicela universal y meningococo no están incluidos 
        en el esquema gratuito (disponibles en el sector privado).
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        card("3.4 SALUD REPRODUCTIVA Y GINECO-OBSTETRICIA")
        sexo_p = st.session_state.hc_data.get("sexo","")
        if sexo_p == "Femenino":
            cb1,cb2 = st.columns(2)
            if cb1.button("✅ Pack Nulípara (0-0-0-0)"):
                for k in ["g_val","p_val","a_val","c_val"]: st.session_state[k] = 0
                st.session_state.rc_val = "28/5 (Regular)"
                st.session_state.mac_val = "Ninguno"; st.rerun()
            if cb2.button("🚫 Niega Embarazo / MAC Barrera"):
                st.session_state.mac_val = "Preservativo / Barrera"; st.rerun()
            gc,pc,ac,cc = st.columns(4)
            gc.number_input("G (Gestas)",  0,20,value=st.session_state.g_val,key="g_input")
            pc.number_input("P (Partos)",  0,20,value=st.session_state.p_val,key="p_input")
            ac.number_input("A (Abortos)", 0,20,value=st.session_state.a_val,key="a_input")
            c_in = cc.number_input("C (Cesáreas)",0,20,value=st.session_state.c_val,key="c_input")
            if c_in >= 3: st.warning("⚠️ 3+ Cesáreas — Riesgo Quirúrgico Aumentado")
            g1,g2,g3 = st.columns(3)
            fur = g1.date_input("F.U.R.", format="DD/MM/YYYY")
            g2.text_input("Régimen Catamenial", value=st.session_state.rc_val)
            g3.text_input("M.A.C. Actual", value=st.session_state.mac_val)
            if st.toggle("🤰 Paciente actualmente gestante"):
                fpp = fur + timedelta(days=280)
                st.error(f"🚨 FPP estimada: {fpp.strftime('%d/%m/%Y')}")
        else:
            st.info("Sección gineco-obstétrica no aplica para el sexo biológico seleccionado.")

        card("3.5 ANTECEDENTES")

        with st.expander("🩺 Patológicos personales", expanded=True):
            ap1, ap2 = st.columns(2)
            ap1.text_area("Enfermedades previas y actuales", height=90,
                          placeholder="Ej: HTA desde 2018, DM2 diagnosticada 2020...",
                          key="ant_patologicos")
            ap2.text_area("Alergias (medicamentos, alimentos, ambiente)", height=90,
                          placeholder="Ej: Alergia a penicilina, alergia al polvo...",
                          key="ant_alergias")
            st.text_area("Antecedentes heredofamiliares (énfasis psiquiátrico y oncológico)", height=70,
                         placeholder="Ej: Padre con DM2, madre con depresión...",
                         key="ant_familiares")

        with st.expander("🔪 Cirugías e intervenciones"):
            cir1, cir2 = st.columns(2)
            cir1.text_area("Cirugías previas (tipo, año, complicaciones)", height=80,
                           placeholder="Ej: Apendicectomía 2015, sin complicaciones...",
                           key="ant_cirugias")
            cir2.text_area("Hospitalizaciones relevantes", height=80,
                           placeholder="Ej: Hospitalización por neumonía 2019...",
                           key="ant_hospitalizaciones")
            st.text_input("Implantes / prótesis / dispositivos",
                          placeholder="Ej: DIU, marcapasos, prótesis de rodilla...",
                          key="ant_implantes")

        with st.expander("🌿 Cannabis — Antecedentes de uso"):
            cv1, cv2, cv3 = st.columns(3)
            cons_prev2 = cv1.radio("¿Consumo previo de Cannabis?", ["No","Sí"],
                                   horizontal=True, key="cons_cannabis")
            if cons_prev2 == "Sí":
                edad_ini2 = cv2.number_input("Edad de inicio (años)", 0, 80, 18, key="cannabis_edad_ini")
                via_can   = cv3.selectbox("Vía de consumo", ["Fumado","Vaporizado","Oral/Comestible","Sublingual","Otros"], key="cannabis_via")
                cc1, cc2, cc3 = st.columns(3)
                freq_can  = cc1.selectbox("Frecuencia de uso", ["Ocasional","Semanal","Diario","Múltiple/día"], key="cannabis_freq")
                impacto2  = cc2.selectbox("Primer impacto subjetivo", ["Positivo","Negativo","Neutro"], key="cannabis_impacto")
                tiempo_can = cc3.text_input("Tiempo de uso total", placeholder="Ej: 3 años", key="cannabis_tiempo")
                if edad_ini2 < 18:
                    st.warning(f"⚠️ Inicio a los {edad_ini2} años — Consumo en adolescencia. Mayor riesgo de vulnerabilidad neurológica (receptor CB1 en desarrollo).")
                st.text_area("Motivo de uso y efectos reportados", height=60,
                             placeholder="Ej: Dolor crónico, ansiedad, insomnio. Refiere mejoría del sueño...",
                             key="cannabis_notas")

        with st.expander("🍺 Alcohol — Antecedentes de uso"):
            al_prev = st.radio("¿Consume alcohol actualmente?", ["No","Ocasional","Frecuente","Diario"],
                               horizontal=True, key="alcohol_uso")
            if al_prev != "No":
                alc1, alc2, alc3 = st.columns(3)
                tipo_beb  = alc1.multiselect("Tipo de bebida", ["Cerveza","Vino","Licor destilado","Chicha","Otros"], key="alcohol_tipo")
                anos_alc  = alc2.number_input("Años de consumo", 0, 60, 5, key="alcohol_anos")
                intentos  = alc3.radio("¿Ha intentado dejar?", ["No","Sí, sin éxito","Sí, actualmente abstinente"], horizontal=False, key="alcohol_intentos")
                st.text_area("Observaciones sobre consumo de alcohol", height=55,
                             placeholder="Ej: Consumo social, aumentó durante pandemia...",
                             key="alcohol_notas")

        with st.expander("💊 Drogas y otras sustancias"):
            dr1, dr2 = st.columns(2)
            drogas_uso = dr1.multiselect("Sustancias utilizadas",
                ["Tabaco/nicotina","Cocaína/pasta base","Opioides","Benzodiacepinas (automedicación)",
                 "Estimulantes (anfetaminas)","Alucinógenos","Solventes","Otras"],
                key="drogas_tipo")
            if drogas_uso:
                dr2.text_area("Frecuencia, tiempo de uso y última vez", height=80,
                              placeholder="Ej: Cocaína, uso ocasional, última vez hace 6 meses...",
                              key="drogas_detalle")
                if "Opioides" in drogas_uso:
                    st.error("🚨 Uso de opioides — evaluar tolerancia y posibles interacciones con cannabinoides (depresión SNC).")
                if "Benzodiacepinas (automedicación)" in drogas_uso:
                    st.warning("⚠️ Benzodiacepinas sin prescripción — riesgo de dependencia y potenciación sedante con CBD.")

        st.markdown("<br>", unsafe_allow_html=True)
        # Toxicológico cuantitativo (antes 3.2 ahora dentro de 3.4)
        with st.expander("📊 3.5.1 Riesgos toxicológicos cuantitativos", expanded=False):
            card("TABACO — ÍNDICE TABÁQUICO")
            t1,t2,t3 = st.columns(3)
            cig  = t1.number_input("Cigarros/día", 0, key="cig_dia")
            anos = t2.number_input("Años fumando", 0, key="cig_anos")
            it   = (cig * anos) / 20
            t3.metric("Índice Tabáquico", f"{it:.1f} paq/año")
            if cig > 0:
                if it >= 20:
                    st.error(f"🚨 IT {it:.1f} paq/año — Riesgo muy alto de EPOC y cáncer. Cesación tabáquica urgente.")
                elif it >= 10:
                    st.warning(f"⚠️ IT {it:.1f} paq/año — Riesgo alto. Considerar espirometría y consejería.")
                elif it >= 5:
                    st.warning(f"⚠️ IT {it:.1f} paq/año — Riesgo moderado. Intervención breve recomendada.")
                else:
                    st.info(f"ℹ️ IT {it:.1f} paq/año — Fumador activo. Registrar en historial.")
                if cig >= 20:
                    st.warning("⚠️ Interacción cannabis-tabaco: mayor riesgo de dependencia y efectos cardiovasculares.")

            st.markdown("---")
            card("ALCOHOL — ETANOL DIARIO")
            al1,al2,al3 = st.columns(3)
            pct_alc  = al1.number_input("% alcohol", 0.0, 100.0, 4.5, key="alc_pct")
            ml_alc   = al2.number_input("ml alcohol/día", 0, key="alc_ml")
            etanol_g = (pct_alc * ml_alc * 0.8) / 100
            al3.metric("Etanol diario", f"{etanol_g:.1f} g")
            if etanol_g > 0:
                if etanol_g >= 60:
                    st.error(f"🚨 {etanol_g:.1f} g etanol/día — ALTO RIESGO. Hepatotoxicidad severa. Interacción crítica con cannabinoides.")
                elif etanol_g >= 40:
                    st.error(f"🚨 {etanol_g:.1f} g etanol/día — Consumo perjudicial (OMS). Evaluar dependencia.")
                elif etanol_g >= 20:
                    st.warning(f"⚠️ {etanol_g:.1f} g etanol/día — Riesgo moderado. Potencia efectos sedantes del cannabis.")
                else:
                    st.info(f"ℹ️ {etanol_g:.1f} g etanol/día — Consumo bajo riesgo.")

        nav_btns(paso)

    # ════════════════════════════════════════════════════════
    #  PASO 2 — ENFERMEDAD ACTUAL
    # ════════════════════════════════════════════════════════
    elif paso == 2:
        card("4.1 CARACTERÍSTICAS DE LA ENFERMEDAD ACTUAL")
        e1,e2,e3 = st.columns(3)
        t_enf = e1.text_input("Tiempo de enfermedad", placeholder="Ej: 3 semanas")
        f_ini = e2.selectbox("Forma de inicio", ["Insidioso","Brusco"])
        c_enf = e3.selectbox("Curso clínico", ["Progresivo","Estacionario","Intermitente","Regresivo"])

        # ── Autocompletado 4.1 basado en datos previos ──
        d = st.session_state.hc_data
        _dx   = d.get("dx_nombre","")
        _cie  = d.get("cie10","")
        _mot  = d.get("motivo","")
        _gad  = d.get("gad7",0)
        _phq  = d.get("phq9",0)
        _edad = d.get("edad",0)
        _sexo = d.get("sexo","")

        # Generar texto sugerido según datos disponibles
        _sugerencia = ""
        if _mot or _dx:
            partes = []
            if _edad and _sexo and _sexo != "Seleccione...":
                partes.append(f"Paciente {_sexo.lower()} de {_edad} años")
            if _mot:
                partes.append(f"que consulta por {_mot.lower()}")
            if t_enf:
                partes.append(f"de {t_enf} de evolución")
            partes.append(f"de {f_ini.lower()}")
            partes.append(f"con curso {c_enf.lower()}")
            if _gad >= 10 or _phq >= 10:
                partes.append(f"con compromiso psicoemocional (GAD-7:{_gad}/PHQ-9:{_phq})")
            if _dx:
                partes.append(f"Diagnóstico: {_dx}")
            _sugerencia = ". ".join(partes) + "."

        col_desc, col_sug = st.columns([3,1])
        with col_desc:
            desc_enf = st.text_area("Descripción detallada de la enfermedad actual", height=120,
                         key="desc_enfermedad",
                         placeholder="Anamnesis completa, síntomas principales, cronología...")
        with col_sug:
            st.markdown("<br>", unsafe_allow_html=True)
            if _sugerencia:
                if st.button("✨ Autocompletar", use_container_width=True, help="Genera texto basado en datos del paciente"):
                    st.session_state["desc_enfermedad_auto"] = _sugerencia
                    st.rerun()
                st.caption("Basado en: motivo, edad, sexo, diagnóstico, psicometría")
            else:
                st.info("Completa el Paso 0 y Psicometría para autocompletar.")

        if st.session_state.get("desc_enfermedad_auto"):
            st.text_area("Texto sugerido (editar y copiar):", value=st.session_state["desc_enfermedad_auto"],
                         height=80, key="sugerencia_view")

        st.markdown("<br>", unsafe_allow_html=True)
        card("4.2 CONCILIACIÓN FARMACOLÓGICA Y ALERTAS DE INTERACCIÓN CANNABINOIDE")
        f1c,f2c,f3c,f4c = st.columns(4)
        f_nom   = f1c.selectbox("Fármaco", ["Otro..."] + sorted(DB_FARMACOS))
        f_input = f1c.text_input("Nombre libre", value="" if f_nom == "Otro..." else f_nom, key="f_input_libre")
        f_mg    = f2c.text_input("Dosis (mg)")
        f_h     = f3c.number_input("Cada (h)", 1, 24, 12)
        f_t     = f4c.text_input("Tiempo de uso")
        if st.button("➕ Agregar fármaco", use_container_width=True):
            nombre_real = f_input if f_input else f_nom
            if nombre_real and nombre_real != "Otro...":
                st.session_state.farmacos.append({
                    "Medicamento": nombre_real,
                    "Dosis": f"{f_mg}mg c/{f_h}h",
                    "Tiempo": f_t,
                    "Frecuencia": f"{f_h}h"
                })

        if st.session_state.farmacos:
            st.dataframe(pd.DataFrame(st.session_state.farmacos)[["Medicamento","Dosis","Tiempo"]],
                         use_container_width=True, hide_index=True)
            col_del = st.columns(len(st.session_state.farmacos))
            for i, f in enumerate(st.session_state.farmacos):
                if col_del[i].button(f"❌ {f['Medicamento'][:10]}", key=f"del_f_{i}"):
                    st.session_state.farmacos.pop(i); st.rerun()

            # ── Visualización de interacciones ──
            st.markdown("<br>", unsafe_allow_html=True)
            interacciones = [(f["Medicamento"], INTERACCIONES_CBD[f["Medicamento"]])
                             for f in st.session_state.farmacos
                             if f["Medicamento"] in INTERACCIONES_CBD]

            if interacciones:
                import streamlit.components.v1 as components_inter
                # Construir HTML de mapa de interacciones
                cards_html = ""
                resumen = {"CRITICA":0,"ALTA":0,"MODERADA":0,"LEVE":0}
                for med, (nivel, mecanismo, recomendacion) in interacciones:
                    color, bg, icon = COLORES_INTERACCION[nivel]
                    resumen[nivel] += 1
                    cards_html += f"""
<div style="background:{bg};border:1px solid {color}40;border-left:3px solid {color};
border-radius:8px;padding:10px 14px;margin-bottom:8px;">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
    <span style="font-size:14px;">{icon}</span>
    <span style="font-weight:600;color:{color};font-size:13px;">{med}</span>
    <span style="font-size:10px;padding:2px 8px;border-radius:12px;background:{color}22;
          color:{color};margin-left:auto;letter-spacing:1px;">{nivel}</span>
  </div>
  <div style="font-size:11px;color:#a8c4d4;margin-bottom:4px;">{mecanismo}</div>
  <div style="font-size:11px;color:#6ab8a8;font-style:italic;">{recomendacion}</div>
</div>"""

                # Resumen superior
                resumen_html = "<div style='display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;'>"
                for nivel, count in resumen.items():
                    if count > 0:
                        color, bg, icon = COLORES_INTERACCION[nivel]
                        resumen_html += f"""<div style="background:{bg};border:1px solid {color}50;
border-radius:20px;padding:4px 12px;font-size:11px;color:{color};font-weight:500;">
{icon} {count} {nivel}</div>"""
                resumen_html += "</div>"

                html_inter = f"""<style>
body{{margin:0;padding:4px;background:#060d14;font-family:system-ui,sans-serif;}}
</style>
<div style="padding:4px;">
<div style="font-size:10px;color:#3a5a70;letter-spacing:1.5px;margin-bottom:8px;">
INTERACCIONES CON CANNABINOIDES — {len(interacciones)} FÁRMACO(S) DETECTADO(S)</div>
{resumen_html}
{cards_html}
<div style="font-size:10px;color:#2a4a5a;margin-top:8px;font-style:italic;">
Fuente: Blesching 2020, McGregor 2021, Drugbank Cannabis Interactions DB.
Siempre verificar con ficha técnica actualizada.</div>
</div>"""
                components_inter.html(html_inter, height=min(120 + len(interacciones)*130, 600), scrolling=True)
            else:
                fármacos_sin_datos = [f["Medicamento"] for f in st.session_state.farmacos
                                       if f["Medicamento"] not in INTERACCIONES_CBD]
                if fármacos_sin_datos:
                    st.info(f"Sin datos de interacción cannábica para: {', '.join(fármacos_sin_datos)}. Verificar manualmente.")

        st.markdown("<br>", unsafe_allow_html=True)
        card("4.3 PROTOCOLO ALICIA — MAPA DE DOLOR")
        zonas = st.multiselect("Zonas de dolor:",
            ["Cervical","Lumbar","Dorsal","Hombro D/I","Rodilla D/I","Manos/Pies","Abdominal","Cefalea"],
            default=["Lumbar"])
        if zonas:
            st.markdown("**Intensidad EVA (0 = sin dolor - 10 = máximo dolor)**")
            evas = {}
            cols_z = st.columns(2)
            for i, z in enumerate(zonas):
                with cols_z[i % 2]:
                    v = st.select_slider(f"{z}", options=list(range(11)), value=5, key=f"eva_{z}")
                    color = "#FF4444" if v>=7 else "#FFB300" if v>=4 else "#39FF14"
                    nivel = "Severo" if v>=7 else "Moderado" if v>=4 else "Leve"
                    st.markdown(f"<div style='font-size:0.8rem;color:{color};margin-bottom:0.5rem;'>● {nivel} ({v}/10)</div>", unsafe_allow_html=True)
                    evas[z] = v
            mx = max(evas.values())
            st.metric("EVA máximo registrado", f"{mx}/10", delta="Alta prioridad" if mx > 6 else None)
        else:
            st.info("Seleccione zonas de dolor para evaluar intensidad.")

        nav_btns(paso)

    # ════════════════════════════════════════════════════════
    #  PASO 3 — PSICOMETRÍA
    # ════════════════════════════════════════════════════════
    elif paso == 3:
        OPCIONES_PSICO = {0:"0 — Nunca",1:"1 — Varios días",
                          2:"2 — Más de la mitad de los días",3:"3 — Casi todos los días"}
        fmt = lambda x: OPCIONES_PSICO[x]

        st.markdown("""
        <div style='background:rgba(0,255,204,0.05);border-left:3px solid #00FFCC;
                    padding:0.85rem 1.1rem;border-radius:0 8px 8px 0;margin-bottom:1.5rem;font-size:0.95rem;'>
            <strong>Instrucción al paciente:</strong> Durante las <u>últimas 2 semanas</u>,
            ¿con qué frecuencia le han molestado los siguientes problemas?
        </div>
        """, unsafe_allow_html=True)

        tg, tp = st.tabs(["📊 GAD-7 - Ansiedad Generalizada", "📊 PHQ-9 - Depresión Mayor"])

        # ── GAD-7 ──────────────────────────────
        with tg:
            st.markdown("""
            <div style='background:#0d1b26;border:1px solid #1e3a50;border-radius:8px;
                        padding:1rem 1.25rem;margin-bottom:1.5rem;'>
                <div style='font-size:0.95rem;font-weight:500;color:#dde8f0;margin-bottom:4px;'>
                    GAD-7 — Escala de Trastorno de Ansiedad Generalizada
                </div>
                <div style='font-size:0.8rem;color:#6a8a9a;line-height:1.6;'>
                    Spitzer RL, Kroenke K, Williams JBW, Löwe B (2006). <em>Arch Intern Med.</em><br>
                    Validado en español - Sensibilidad 89% - Especificidad 82% - Punto de corte ≥10
                </div>
            </div>
            """, unsafe_allow_html=True)

            GAD7 = [
                ("g1","1. Sentirse nervioso/a, ansioso/a o con los nervios de punta"),
                ("g2","2. No poder dejar de preocuparse o no poder controlar la preocupación"),
                ("g3","3. Preocuparse demasiado por diferentes cosas"),
                ("g4","4. Dificultad para relajarse"),
                ("g5","5. Estar tan intranquilo/a que es difícil permanecer sentado/a quieto/a"),
                ("g6","6. Molestarse o ponerse irritable con facilidad"),
                ("g7","7. Sentir miedo, como si algo terrible fuera a ocurrir"),
            ]
            g_scores = []
            for key, preg in GAD7:
                st.markdown(f"<div style='font-size:0.95rem;color:#dde8f0;font-weight:400;margin-bottom:4px;'>{preg}</div>", unsafe_allow_html=True)
                v = st.radio(preg,[0,1,2,3],format_func=fmt,horizontal=True,key=f"gad_{key}",label_visibility="collapsed")
                g_scores.append(v)
                st.markdown("<hr style='border-color:#0f2030;margin:0.75rem 0;'>", unsafe_allow_html=True)

            total_g = sum(g_scores)
            st.markdown("**¿Qué tan difícil le ha resultado hacer su trabajo, atender su hogar o relacionarse con otras personas?**")
            st.radio("Funcionalidad GAD",["Nada difícil","Algo difícil","Muy difícil","Sumamente difícil"],
                     horizontal=True, key="gad_func", label_visibility="collapsed")

            st.markdown("<br>", unsafe_allow_html=True)
            if   total_g <= 4:  nv,cl,rec = "Ansiedad mínima","#39FF14","Sin intervención. Reevaluar en próxima consulta."
            elif total_g <= 9:  nv,cl,rec = "Ansiedad leve","#FFB300","Psicoeducación y técnicas de relajación. Monitoreo activo."
            elif total_g <= 14: nv,cl,rec = "Ansiedad moderada","#FF6B00","Evaluar inicio de TCC. Considerar farmacoterapia."
            else:               nv,cl,rec = "Ansiedad severa","#FF4444","Intervención activa. Farmacoterapia recomendada."

            cg1,cg2 = st.columns(2)
            cg1.metric("Puntaje GAD-7", f"{total_g} / 21")
            cg2.markdown(f"""
            <div style='background:#0d1b26;border:1px solid #1e3a50;border-radius:8px;padding:0.85rem;margin-top:0.5rem;'>
              <div style='font-size:0.65rem;color:#3a5a70;letter-spacing:1px;margin-bottom:4px;'>NIVEL DE ANSIEDAD</div>
              <div style='font-size:1.05rem;font-weight:500;color:{cl};'>{nv}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='border-left:3px solid {cl};background:rgba(255,255,255,0.02);
                        padding:0.75rem 1rem;border-radius:0 6px 6px 0;margin-top:0.75rem;font-size:0.88rem;'>
              <strong>Recomendación:</strong> {rec}<br>
              <span style='color:#3a5a70;font-size:0.8rem;'>Corte: 0–4 mínima - 5–9 leve - 10–14 moderada - 15–21 severa</span>
            </div>""", unsafe_allow_html=True)
            st.session_state.hc_data["gad7"] = total_g

        # ── PHQ-9 ──────────────────────────────
        with tp:
            st.markdown("""
            <div style='background:#0d1b26;border:1px solid #1e3a50;border-radius:8px;
                        padding:1rem 1.25rem;margin-bottom:1.5rem;'>
                <div style='font-size:0.95rem;font-weight:500;color:#dde8f0;margin-bottom:4px;'>
                    PHQ-9 — Cuestionario sobre la Salud del Paciente
                </div>
                <div style='font-size:0.8rem;color:#6a8a9a;line-height:1.6;'>
                    Kroenke K, Spitzer RL, Williams JBW (2001). <em>J Gen Intern Med.</em><br>
                    Validado en español latinoamericano - Sensibilidad 88% - Especificidad 88% - Punto de corte ≥10
                </div>
            </div>
            """, unsafe_allow_html=True)

            PHQ9 = [
                ("p1","1. Poco interés o placer en hacer las cosas"),
                ("p2","2. Sentirse desanimado/a, deprimido/a o sin esperanza"),
                ("p3","3. Dificultad para quedarse o seguir dormido/a, o dormir demasiado"),
                ("p4","4. Sentirse cansado/a o tener poca energía"),
                ("p5","5. Tener poco apetito o comer en exceso"),
                ("p6","6. Sentirse mal consigo mismo/a o que es un fracaso, o que ha fallado a su familia"),
                ("p7","7. Dificultad para concentrarse en cosas como leer o ver televisión"),
                ("p8","8. Moverse o hablar tan despacio que otras personas lo han notado, o estar tan inquieto/a que se mueve más de lo usual"),
                ("p9","9. Pensamientos de que estaría mejor muerto/a o de hacerse daño de alguna manera"),
            ]
            p_scores = []
            for key, preg in PHQ9:
                if key == "p9":
                    st.markdown("""
                    <div style='background:rgba(255,68,68,0.07);border:1px solid rgba(255,68,68,0.3);
                                border-radius:6px;padding:0.5rem 0.85rem;margin-bottom:0.5rem;font-size:0.82rem;'>
                    ⚠️ <strong>Ítem de seguridad clínica</strong> — Cualquier respuesta mayor a "Nunca" requiere
                    evaluación de riesgo inmediata y activación de protocolo de seguridad.
                    </div>""", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:0.95rem;color:#dde8f0;font-weight:400;margin-bottom:4px;'>{preg}</div>", unsafe_allow_html=True)
                v = st.radio(preg,[0,1,2,3],format_func=fmt,horizontal=True,key=f"phq_{key}",label_visibility="collapsed")
                p_scores.append(v)
                st.markdown("<hr style='border-color:#0f2030;margin:0.75rem 0;'>", unsafe_allow_html=True)

            if p_scores[-1] > 0:
                st.error("🚨 ALERTA VITAL — Ítem 9 positivo. Activar protocolo de contención y evaluación de riesgo de inmediato.")

            total_p = sum(p_scores)
            st.markdown("**¿Qué tan difícil le ha resultado hacer su trabajo, atender su hogar o relacionarse con otras personas?**")
            funcional_p = st.radio("Funcionalidad PHQ",["Nada difícil","Algo difícil","Muy difícil","Sumamente difícil"],
                                   horizontal=True, key="phq_func", label_visibility="collapsed")

            st.markdown("<br>", unsafe_allow_html=True)
            if   total_p <= 4:  nvp,clp,recp,tipo = "Mínima o ausente","#39FF14","Sin intervención. Reevaluar en 3–6 meses.","—"
            elif total_p <= 9:  nvp,clp,recp,tipo = "Leve","#FFB300","Psicoeducación y activación conductual.","Episodio depresivo menor probable"
            elif total_p <= 14: nvp,clp,recp,tipo = "Moderada","#FF6B00","Psicoterapia y/o antidepresivo.","Episodio depresivo mayor probable"
            elif total_p <= 19: nvp,clp,recp,tipo = "Moderada-Severa","#FF4444","Farmacoterapia + psicoterapia urgente.","Episodio depresivo mayor"
            else:               nvp,clp,recp,tipo = "Severa","#FF0000","Derivación urgente. Evaluar hospitalización.","Episodio depresivo mayor severo"

            cp1,cp2 = st.columns(2)
            cp1.metric("Puntaje PHQ-9", f"{total_p} / 27")
            cp2.markdown(f"""
            <div style='background:#0d1b26;border:1px solid #1e3a50;border-radius:8px;padding:0.85rem;margin-top:0.5rem;'>
              <div style='font-size:0.65rem;color:#3a5a70;letter-spacing:1px;margin-bottom:4px;'>NIVEL DE DEPRESIÓN</div>
              <div style='font-size:1.05rem;font-weight:500;color:{clp};'>{nvp}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='border-left:3px solid {clp};background:rgba(255,255,255,0.02);
                        padding:0.75rem 1rem;border-radius:0 6px 6px 0;margin-top:0.75rem;font-size:0.88rem;'>
              <strong>Diagnóstico sugerido:</strong> {tipo}<br>
              <strong>Recomendación:</strong> {recp}<br>
              <span style='color:#3a5a70;font-size:0.8rem;'>Corte: 0–4 mínima - 5–9 leve - 10–14 moderada - 15–19 mod-severa - 20–27 severa</span>
            </div>""", unsafe_allow_html=True)
            st.session_state.hc_data["phq9"] = total_p

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🧠 Resumen Psicométrico")
        r1,r2,r3 = st.columns(3)
        r1.metric("GAD-7", f"{st.session_state.hc_data.get('gad7',0)} pts")
        r2.metric("PHQ-9", f"{st.session_state.hc_data.get('phq9',0)} pts")
        r3.metric("Funcionalidad", funcional_p if 'funcional_p' in dir() else "—")
        nav_btns(paso)

    # ════════════════════════════════════════════════════════
    #  PASO 4 — SEGUIMIENTO
    # ════════════════════════════════════════════════════════
    elif paso == 4:
        card("5.1 EVOLUCIÓN Y MEJORÍA GLOBAL")
        mejoria = st.slider("% Mejoría Global del paciente", 0, 100, 50,
                            format="%d%%", help="0% = sin mejoría - 100% = resolución completa")
        col_m1,col_m2,col_m3 = st.columns(3)
        color_m = "#39FF14" if mejoria>=70 else "#FFB300" if mejoria>=40 else "#FF4444"
        col_m1.markdown(f"<div style='background:#0d1b26;border:1px solid #1e3a50;border-radius:8px;padding:1rem;text-align:center;'><div style='font-size:0.65rem;color:#3a5a70;letter-spacing:1px;'>MEJORÍA</div><div style='font-size:1.8rem;font-weight:600;color:{color_m};'>{mejoria}%</div></div>", unsafe_allow_html=True)
        ram = col_m2.multiselect("RAM detectadas:", ["Boca seca","Mareo","Somnolencia","Náuseas","Ansiedad","Taquicardia","Cefalea"])
        col_m3.text_area("Observaciones de evolución", height=80)
        if "Mareo" in ram: st.warning("⚠️ Mareo reportado — evaluar ajuste de dosis.")

        st.markdown("<br>", unsafe_allow_html=True)
        card("5.2 MATRIZ DE SÍNTOMAS — 21 ÍTEMS (0 = ausente - 10 = máximo)")
        s_list = ["Agresividad","Ansiedad","Apetito","Cambios de humor","Cefaleas","Concentración",
                  "Convulsiones","Depresión","Diaforesis","Hiperactividad","Insomnio","Labilidad emocional",
                  "Mareos","Náuseas","Palpitaciones","Rigidez","Sed","Sialorrea","Somnolencia","Taquicardia","Vértigos"]
        cols_s = st.columns(3)
        for i,s in enumerate(s_list):
            with cols_s[i%3]:
                st.select_slider(s, options=list(range(11)), key=f"s_{s}")
        nav_btns(paso)

    # ════════════════════════════════════════════════════════
    #  PASO 5 — DIAGNÓSTICO
    # ════════════════════════════════════════════════════════
    elif paso == 5:
        from diagnosticos_db import capitulos_disponibles

        st.markdown("""
        <div style='background:#0d1b26;border-left:3px solid #4dc8b4;padding:0.75rem 1rem;
                    border-radius:0 6px 6px 0;margin-bottom:1.25rem;font-size:0.9rem;color:#a8c4d4;'>
            Escribe el <strong>código</strong> (F41, Z00, E11...) o el <strong>nombre</strong>
            del diagnóstico. Fuente: CIE-10 Vol.1 2018 (OPS) + CIE-11 (OMS).
        </div>
        """, unsafe_allow_html=True)

        def buscador_dx(label, key_q, key_sel, key_data_cie10, key_data_cie11, key_data_nombre):
            card(label)
            c_bus, c_cap = st.columns([2,1])
            query = c_bus.text_input("🔍 Buscar", placeholder="F32, ansiedad, diabetes, lumbalgia...", key=key_q)
            caps  = capitulos_disponibles()
            filtro = c_cap.selectbox("Capítulo", caps, key=f"cap_{key_q}")

            if query:
                res = buscar_diagnostico(query, limite=20)
                if filtro != "Todos":
                    res = [r for r in res if r.get("cap","") == filtro]
                if res:
                    opts = ["-- Seleccionar --"] + [formato_opcion(r) for r in res]
                    sel  = st.selectbox(f"{len(res)} resultado(s)", opts, key=key_sel)
                    if sel != "-- Seleccionar --":
                        dx = res[opts.index(sel)-1]
                        st.markdown(f"""
                        <div style='background:#0d1b26;border:1px solid #1e3a50;border-radius:8px;
                                    padding:0.9rem 1.1rem;margin:0.5rem 0;display:flex;gap:2rem;align-items:center;flex-wrap:wrap;'>
                            <div>
                                <div style='font-size:0.6rem;color:#3a5a70;letter-spacing:2px;'>CIE-10</div>
                                <div style='font-size:1.1rem;font-weight:600;color:#4dc8b4;font-family:monospace;'>{dx['cie10']}</div>
                            </div>
                            <div>
                                <div style='font-size:0.6rem;color:#3a5a70;letter-spacing:2px;'>CIE-11</div>
                                <div style='font-size:1.1rem;font-weight:600;color:#6ab8a8;font-family:monospace;'>{dx['cie11']}</div>
                            </div>
                            <div>
                                <div style='font-size:0.6rem;color:#3a5a70;letter-spacing:2px;'>CAPÍTULO</div>
                                <div style='font-size:0.8rem;color:#90b0c4;'>{dx.get('cap','')}</div>
                            </div>
                            <div style='flex:1;min-width:220px;'>
                                <div style='font-size:0.6rem;color:#3a5a70;letter-spacing:2px;'>DIAGNÓSTICO</div>
                                <div style='font-size:0.95rem;font-weight:500;color:#d8e8f0;'>{dx['nombre']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"✅ Confirmar", key=f"btn_{key_q}", type="primary"):
                            st.session_state.hc_data[key_data_cie10]   = dx["cie10"]
                            st.session_state.hc_data[key_data_cie11]   = dx["cie11"]
                            st.session_state.hc_data[key_data_nombre]  = dx["nombre"]
                            st.success(f"✅ {dx['cie10']} — {dx['nombre']}")
                else:
                    st.warning("Sin resultados. Prueba con otro término.")
            else:
                # Mostrar valor confirmado si ya existe
                v10 = st.session_state.hc_data.get(key_data_cie10,"")
                if v10:
                    st.markdown(f"""
                    <div style='background:#0d1b26;border:1px solid #1e3a50;border-radius:6px;
                                padding:0.6rem 1rem;font-size:0.9rem;color:#a8c4d4;'>
                        ✅ Confirmado: <code style='color:#4dc8b4;'>{v10}</code> — 
                        {st.session_state.hc_data.get(key_data_nombre,"")}
                    </div>""", unsafe_allow_html=True)

        # ── Diagnóstico Principal ──
        buscador_dx(
            "6.1 DIAGNÓSTICO PRINCIPAL",
            "q_dx_principal", "sel_dx_principal",
            "cie10", "cie11", "dx_nombre"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Diagnósticos Secundarios ──
        with st.expander("➕ Diagnósticos secundarios (opcional)", expanded=False):
            buscador_dx(
                "DIAGNÓSTICO SECUNDARIO 1",
                "q_dx_sec1", "sel_dx_sec1",
                "cie10_sec1", "cie11_sec1", "dx_nombre_sec1"
            )
            st.markdown("<br>", unsafe_allow_html=True)
            buscador_dx(
                "DIAGNÓSTICO SECUNDARIO 2",
                "q_dx_sec2", "sel_dx_sec2",
                "cie10_sec2", "cie11_sec2", "dx_nombre_sec2"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        card("6.2 PLAN TERAPÉUTICO")
        plan_tx = st.text_area("Plan de tratamiento", height=110,
                     placeholder="Indicaciones, metas terapéuticas, seguimiento programado...",
                     key="plan_tx")
        st.session_state.hc_data["plan_tx"] = plan_tx
        nav_btns(paso)

    # ════════════════════════════════════════════════════════
    #  PASO 6 — RECETA
    # ════════════════════════════════════════════════════════
    elif paso == 6:
        card("7.1 CONFIGURACIÓN DE LA FÓRMULA MAGISTRAL")

        # ── Autoselección por diagnóstico ──
        _dx_rec  = st.session_state.hc_data.get("dx_nombre","")
        _cie_rec = st.session_state.hc_data.get("cie10","")
        _sugg_prot = "🌿 Inicio Gradual — CBD 20:1 · 10mg/ml · 10ml"  # default
        if any(c in _cie_rec for c in ["F32","F33","F34"]):
            _sugg_prot = "🌿 Estándar CBD — 20:1 · 15mg/ml · 30ml"
        elif any(c in _cie_rec for c in ["F41","F40","F43"]):
            _sugg_prot = "🌙 Nocturno (insomnio) — 1:1 · 10mg/ml · 15ml"
        elif any(c in _cie_rec for c in ["G40","G41"]):
            _sugg_prot = "🧠 Neurológico — CBD puro · 25mg/ml · 30ml"
        elif any(c in _cie_rec for c in ["M54","M79","G43","R52"]):
            _sugg_prot = "🤕 Dolor Crónico — 3:1 · 15mg/ml · 30ml"
        elif st.session_state.hc_data.get("edad",0) >= 60:
            _sugg_prot = "👴 Adulto Mayor — 20:1 · 5mg/ml · 30ml"

        st.markdown(f"""<div style="background:#0a1a10;border:1px solid #1e4a2a;border-radius:8px;
padding:0.6rem 1rem;margin-bottom:0.75rem;font-size:0.85rem;color:#6ab8a8;">
Protocolo sugerido para <strong>{_dx_rec or 'diagnóstico pendiente'}</strong> ({_cie_rec}): 
<strong style="color:#4dc8b4;">{_sugg_prot.split(' · ')[0]}</strong>
</div>""", unsafe_allow_html=True)

        prot_sel = st.selectbox("Cargar protocolo de inicio:", ["— Seleccionar —"] + list(PROTOCOLOS_INICIO.keys()),
                                 index=1 + list(PROTOCOLOS_INICIO.keys()).index(_sugg_prot)
                                 if _sugg_prot in PROTOCOLOS_INICIO else 0)
        if prot_sel != "— Seleccionar —" and st.button("⚡ Aplicar protocolo", type="primary"):
            p = PROTOCOLOS_INICIO[prot_sel]
            st.session_state.r_ratio = p["ratio"]
            st.session_state.r_mg    = p["mg"]
            st.session_state.r_ml    = p["ml"]
            st.session_state.r_gotas = p["gotas"]
            st.rerun()

        st.divider()
        r1,r2,r3 = st.columns(3)
        ratio_idx = OPCIONES_RATIO.index(st.session_state.r_ratio) if st.session_state.r_ratio in OPCIONES_RATIO else 0
        ratio  = r1.selectbox("Ratio CBD:THC", OPCIONES_RATIO, index=ratio_idx)
        mg_ml  = r2.number_input("Concentración (mg/ml)", 1, 500, value=st.session_state.r_mg, key="mg_in")
        vol_ml = r3.selectbox("Volumen (ml)",
                              [5,10,15,20,25,30,50,60,100],
                              index=[5,10,15,20,25,30,50,60,100].index(st.session_state.r_ml)
                              if st.session_state.r_ml in [5,10,15,20,25,30,50,60,100] else 1,
                              key="ml_in")

        st.markdown("<br>", unsafe_allow_html=True)
        card("7.2 PLAN DE TITULACIÓN")
        d1r,d2r,d3r = st.columns(3)
        gtt_dia = d1r.number_input("Dosis inicial (gotas/día)", 1, 60, value=st.session_state.r_gotas, key="gtt_in")
        freq    = d2r.selectbox("Frecuencia", ["Cada 12h (AM/PM)","Cada 8h","Dosis única nocturna","Cada 24h"], key="sel_freq")
        st.session_state.hc_data["freq"] = freq
        mg_gota = mg_ml / 20
        dosis_d = gtt_dia * mg_gota
        with d3r:
            st.metric("Dosis diaria real", f"{dosis_d:.1f} mg")
            if dosis_d > 50: st.warning("⚠️ Dosis alta")
        dias = (vol_ml * 20) // gtt_dia if gtt_dia > 0 else 0
        st.info(f"💡 El frasco de {vol_ml}ml durará aproximadamente **{dias} días** con esta dosis.")

        t1r,t2r,t3r = st.columns(3)
        gtt_inicio = t1r.number_input("Dosis inicio (gotas/día)", 1, 30, gtt_dia, key="tit_inicio")
        t1r.caption("Inducción — semana 1")
        inc_dias_in = t2r.number_input("Incremento cada (días)", 1, 14, 3, key="tit_inc")
        t2r.caption("Ajuste por tolerancia")
        gtt_maximo = t3r.number_input("Máximo (gotas/día)", 1, 100, max(gtt_dia*3, 20), key="tit_max")
        t3r.caption("Techo terapéutico")
        # Guardar en hc_data para la receta
        st.session_state.hc_data.update({
            "gtt_inicio": gtt_inicio,
            "inc_dias":   inc_dias_in,
            "gtt_maximo": gtt_maximo,
            "freq":       freq,
        })

        st.markdown("<br>", unsafe_allow_html=True)
        card("7.3 PERFIL DE TERPENOS")
        terp_info = {
            "Mirceno":     "🍃 Sedante y analgésico. Facilita el paso de cannabinoides por la BHE.",
            "Limoneno":    "🍋 Ansiolítico y antidepresivo. Mejora estado de ánimo y absorción.",
            "Linalool":    "🌸 Calmante profundo y anticonvulsivo. Ideal para insomnio y ansiedad.",
            "Pineno":      "🌲 Broncodilatador. Ayuda a contrarrestar fallos de memoria a corto plazo.",
            "Cariofileno": "🌶️ Antiinflamatorio potente. Único terpeno que actúa sobre receptores CB2.",
        }
        sel = st.multiselect("Seleccionar terpenos:", list(terp_info.keys()))
        if sel:
            tc = st.columns(len(sel))
            for i,t in enumerate(sel):
                with tc[i]:
                    st.markdown(f"**{t}**")
                    st.caption(terp_info[t])
                    st.slider(f"% {t}", 0.0, 5.0, 1.0, 0.1, key=f"t_{t}")
        else:
            st.warning("Sin terpenos — fórmula Broad/Full Spectrum base.")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🧮 Calculadora cannabinoide — Dosificación y titulación", expanded=False):
            import streamlit.components.v1 as _cc
            _html = (
                "<html><head><meta charset=\"utf-8\"><style>"
                "body{margin:0;padding:6px;background:#0d1b26;font-family:system-ui,sans-serif;}"
                "</style></head><body>"
            )
            _html += _CALC_HTML
            _html += "</body></html>"
            _cc.html(_html, height=700, scrolling=True)

        st.text_area("Observaciones de la receta",
                     "Tomar con alimentos grasos para mejorar biodisponibilidad. No conducir si presenta mareos.",
                     key="obs_receta")

        st.markdown("<br>", unsafe_allow_html=True)
        card("7.5 VISTA PREVIA — RECETA MÉDICA MAGISTRAL")
        d      = st.session_state.hc_data
        gtt_p  = st.session_state.get("gtt_in", 1)
        mg_p   = st.session_state.get("mg_in", 10)
        vol_p  = st.session_state.get("ml_in", 10)
        cie_p  = d.get("cie10", "___")
        cie11_p= d.get("cie11", "")
        dx_p   = d.get("dx_nombre", "___")
        fecha_p= d.get("fecha_hc", datetime.now().strftime("%d/%m/%Y"))

        # Cálculo de edad en años y meses (hasta 2 años con meses)
        edad_num = d.get("edad", 0)
        f_nac_stored = st.session_state.hc_data.get("f_nac_raw", None)
        if f_nac_stored and isinstance(f_nac_stored, date) and edad_num < 3:
            meses_total = (date.today().year - f_nac_stored.year)*12 + (date.today().month - f_nac_stored.month)
            anos_e  = meses_total // 12
            meses_e = meses_total % 12
            edad_str = f"{anos_e} año{'s' if anos_e!=1 else ''} y {meses_e} mes{'es' if meses_e!=1 else ''}" if anos_e > 0 else f"{meses_e} mes{'es' if meses_e!=1 else ''}"
        else:
            edad_str = f"{edad_num} años"

        # Calcular mg/gota y dosis real
        mg_gota_p = mg_p / 20
        dosis_real = round(gtt_p * mg_gota_p, 1)
        dias_trat  = int((vol_p * 20) / gtt_p) if gtt_p > 0 else 0

        # Terpenos seleccionados
        terpenos_sel = [t for t in ["Mirceno","Limoneno","Linalool","Pineno","Cariofileno"]
                        if st.session_state.get(f"t_{t}", 0) > 0]
        terp_str = " + ".join(terpenos_sel) if terpenos_sel else "Broad Spectrum"

        # Observaciones de la receta
        obs_p = st.session_state.get("obs_receta",
                    "Tomar con alimentos grasos para mejorar biodisponibilidad. No conducir si presenta mareos.")

        # ── Indicaciones clínicas automáticas por diagnóstico CIE-10 + CIE-11 ──
        _cie10 = d.get("cie10","")
        _cie11 = d.get("cie11","")
        _gad   = d.get("gad7", 0)
        _phq   = d.get("phq9", 0)
        _alt   = d.get("altitud", 0)
        _edad_ind = d.get("edad", 30)
        _plan  = d.get("plan_tx","")

        # También leer diagnósticos secundarios
        _cie10_s1 = d.get("cie10_sec1","")
        _cie10_s2 = d.get("cie10_sec2","")
        _cie11_s1 = d.get("cie11_sec1","")
        _cie11_s2 = d.get("cie11_sec2","")

        # Función helper — busca prefijo en cualquier código presente
        def _match(*prefijos):
            todos = [_cie10, _cie11, _cie10_s1, _cie10_s2, _cie11_s1, _cie11_s2]
            return any(cod.startswith(p) for cod in todos for p in prefijos)

        _indicaciones = []

        # ── Mapa CIE-10 / CIE-11 combinado ──
        # Cada entrada: (función_match, texto_indicación)
        # CIE-11 equivalencias: 6A70-6A73=depresión, 6B00-6B05=ansiedad,
        # 8A60-8A62=epilepsia, FA90-FA95=dolor MSE, 8A80=migraña,
        # 7B01=insomnio, DA91-DA94=digestivo, 2A-2D=oncología, MG30=dolor crónico

        _proto_map = [
            # Depresión
            (lambda: _match("F32","F33","F34","F38","F39","6A70","6A71","6A72","6A73"),
             "Depresión — iniciar CBD predominante (ratio ≥10:1). Escalar c/2 semanas. "
             "Terpenos recomendados: Limoneno + Linalool. Control anímico semanal."),

            # Ansiedad / TEPT / TOC
            (lambda: _match("F40","F41","F42","F43","F44","6B00","6B01","6B02","6B03","6B04","6B05"),
             "Ansiedad — protocolo ansiolítico. Dosis nocturna prioritaria. "
             "Evitar THC las primeras 4 semanas. Terpenos: Linalool + Mirceno."),

            # Epilepsia
            (lambda: _match("G40","G41","8A60","8A61","8A62","8A63"),
             "Epilepsia — escalar MUY lento (1 gota cada 7 días). "
             "CBD puro o ratio ≥20:1. Interconsulta neurología obligatoria. "
             "No suspender antiepilépticos sin supervisión."),

            # Dolor músculo-esquelético
            (lambda: _match("M54","M79","M47","M48","M51","M50","FA90","FA91","FA92","FA93","FA94"),
             "Dolor MSE — ratio 5:1 a 10:1. Aplicar tópico cannabinoide en zona afectada "
             "si disponible. Terpeno prioritario: Cariofileno (antiinflamatorio CB2)."),

            # Migraña / cefalea
            (lambda: _match("G43","R51","8A80","8A81","8A82","MG31"),
             "Migraña — administrar al primer signo del episodio. "
             "Ratio 10:1 o 20:1. Terpeno: Pineno (broncodilatador y neuroprotector)."),

            # Insomnio / trastornos del sueño
            (lambda: _match("F51","G47","7B01","7B00","7B02"),
             "Insomnio — dosis única sublingual 30-45 min antes de dormir. "
             "Ratio 1:1 o 2:1. Terpenos: Mirceno (sedante) + Linalool (calmante profundo)."),

            # Patología digestiva / SII / EII
            (lambda: _match("K58","K57","K50","K51","K52","DA91","DA92","DA93","DA94"),
             "Patología digestiva — iniciar con dosis mínima (1-2 gotas). "
             "Monitorear motilidad intestinal. Ratio ≥10:1. Evitar THC en EII activa."),

            # Oncología / cuidados paliativos
            (lambda: _match("C","D0","D1","2A","2B","2C","2D","2E"),
             "Oncología / Paliativos — evaluación interdisciplinaria obligatoria. "
             "Protocolo individualizado según fase. Ratio según síntoma predominante. "
             "Considerar CBD para náuseas y THC para dolor oncológico refractario."),

            # Dolor crónico / fibromialgia
            (lambda: _match("R52","G89","M79.7","MG30","MG31"),
             "Dolor crónico / Fibromialgia — titulación gradual y sostenida. "
             "Ratio 3:1 a 10:1 según tolerancia. "
             "Terpenos: Cariofileno + Mirceno. Tópico complementario recomendado."),

            # TDAH
            (lambda: _match("F90","6A05"),
             "TDAH — CBD puro o ratio ≥20:1. Evitar THC. Administrar AM. "
             "Puede potenciar concentración. Monitorear si usa estimulantes."),

            # Espasticidad / EM / ELA
            (lambda: _match("G35","G12","G71","8A40","8A41"),
             "Espasticidad — ratio 1:1 a 2:1 (CBD:THC). Administrar noche. "
             "THC tiene efecto relajante muscular significativo."),

            # TEPT
            (lambda: _match("F43.1","6B40","6B41"),
             "TEPT — dosis nocturna para pesadillas. "
             "Ratio 2:1 a 5:1. Terpeno: Linalool. Psicoterapia complementaria obligatoria."),

            # Parkinson / Alzheimer / deterioro cognitivo
            (lambda: _match("G20","G30","F00","F01","F02","F03","8A00","8A20","6D80","6D81"),
             "Deterioro cognitivo / Parkinson — iniciar con dosis mínima (0.5 mg/día). "
             "CBD neuroprotector. Ratio ≥20:1. Monitorear cognición c/mes."),

            # Autismo
            (lambda: _match("F84","6A02"),
             "TEA — protocolo pediátrico si <18 años. CBD puro. "
             "Escalar muy lentamente. Consentimiento familiar informado. "
             "Monitorear conducta y sueño."),

            # Artritis / enfermedades autoinmunes
            (lambda: _match("M05","M06","M32","M34","FA20","FA21","FA22"),
             "Artritis / Autoinmune — efecto antiinflamatorio CB2. "
             "Ratio 10:1 a 20:1. Terpeno: Cariofileno. No suspender DMARD sin reumatología."),
        ]

        for fn_match, texto in _proto_map:
            if fn_match():
                _indicaciones.append(texto)
                break  # una indicación principal por diagnóstico primario

        # Diagnósticos secundarios — añadir nota adicional si difieren
        _ind_sec = []
        for fn_match, texto in _proto_map:
            if fn_match() and texto not in _indicaciones:
                _ind_sec.append(texto.split(" — ")[0])  # solo el nombre del protocolo
        if _ind_sec:
            _indicaciones.append(f"Dx secundario — considerar también: {'; '.join(_ind_sec[:2])}.")

        # Por psicometría
        if _gad >= 15:
            _indicaciones.append("GAD-7 severo — iniciar con dosis mínima, CBD puro. Reevaluar en 2 semanas.")
        elif _gad >= 10:
            _indicaciones.append("GAD-7 moderado — titular lentamente. Evitar THC las primeras 4 semanas.")
        if _phq >= 15:
            _indicaciones.append("PHQ-9 severo — interconsulta psiquiatría prioritaria. Cannabis como coadyuvante.")
        elif _phq >= 10:
            _indicaciones.append("PHQ-9 moderado — monitorear ánimo semanalmente. Potenciar con ejercicio.")

        # Por altitud
        if _alt >= 3000:
            _indicaciones.append(f"Alta altitud ({_alt} msnm) — biodisponibilidad aumentada. "
                "Reducir dosis inicial 20-30% respecto a nivel del mar.")

        # Por edad
        if _edad_ind >= 65:
            _indicaciones.append("Adulto mayor — iniciar con dosis mínima (0.5mg/día), "
                "escalar c/7 días. Vigilar interacciones y caídas.")
        elif _edad_ind < 18:
            _indicaciones.append("Paciente pediátrico/adolescente — supervisión médica estricta. "
                "CBD puro exclusivamente. Consentimiento informado obligatorio.")

        # Por fármacos (interacciones)
        _farmacos_nombres = [f["Medicamento"] for f in st.session_state.farmacos]
        _criticos = [f for f in _farmacos_nombres if f in ["Warfarina","Clobazam","Valproato","Ciclosporina","Tacrolimus"]]
        if _criticos:
            _indicaciones.append(f"ALERTA — interacción crítica con: {', '.join(_criticos)}. "
                "Monitoreo clínico estricto. Ver sección 4.2.")

        # Plan terapéutico del médico
        if _plan:
            _indicaciones.append(f"Plan médico: {_plan}")

        # Indicaciones generales siempre presentes
        _indicaciones_base = (
            "Hábitos saludables e hidratación adecuada (≥2 L/día). "
            "Estimular sistema endocannabinoide mediante ejercicio aeróbico moderado (30min/día). "
            "Evitar alcohol durante la titulación. "
            "Conservar el aceite en lugar fresco, oscuro y seco. "
            "No compartir la receta ni la medicación."
        )
        _ind_texto = " ".join(_indicaciones) if _indicaciones else ""

        # Titulación dinámica (desde 7.2)
        gtt_ini  = st.session_state.get("gtt_in", 1)
        inc_dias = d.get("inc_dias", st.session_state.get("tit_inc", 3))
        gtt_max  = d.get("gtt_maximo", st.session_state.get("tit_max", max(gtt_ini*3, 20)))
        freq_rec = d.get("freq", st.session_state.get("sel_freq", "Cada 12h (AM/PM)"))
        filas_tit = []
        dia_cur = 1
        g_cur   = gtt_ini
        while g_cur <= min(gtt_max, gtt_ini + 7) and len(filas_tit) < 10:
            if   g_cur <= gtt_ini + 1: fase = "Inducción"
            elif g_cur <= gtt_ini + 3: fase = "Ajuste"
            else:                      fase = "Mantenimiento"
            filas_tit.append((dia_cur, dia_cur+inc_dias-1, g_cur, freq_rec, fase))
            dia_cur += inc_dias
            g_cur   += 1

        # Construir filas HTML tabla titulación
        col_colors = {"Inducción":"#1a3a2a","Ajuste":"#1a2a3a","Mantenimiento":"#0d2010"}
        txt_colors = {"Inducción":"#4dc8b4","Ajuste":"#6ab8e8","Mantenimiento":"#39FF14"}
        rows_tit = ""
        for (d1,d2,g,fr,fase) in filas_tit:
            bg  = col_colors.get(fase,"#1a3a2a")
            clr = txt_colors.get(fase,"#4dc8b4")
            rows_tit += (
            f'<tr style="background:{bg}">'
            f'<td style="padding:5px 8px;border-bottom:1px solid #1e3a20;color:#a8d4b0">{d1}-{d2}</td>'
            f'<td style="padding:5px 8px;border-bottom:1px solid #1e3a20;color:#fff;font-weight:600;text-align:center">{g}</td>'
            f'<td style="padding:5px 8px;border-bottom:1px solid #1e3a20;color:#a8d4b0">{fr}</td>'
            f'<td style="padding:5px 8px;border-bottom:1px solid #1e3a20">'
            f'<span style="color:{clr};font-size:10px;padding:2px 6px;border-radius:10px;background:{clr}22">{fase}</span></td></tr>'
        )

        # ── Variables dinámicas para el HTML de la receta ──
        ratio_r      = ratio if "ratio" in dir() else d.get("ratio","20:1")
        inc_dias_txt = f"1 gota cada {inc_dias} días"

        # Datos biométricos
        _peso_p  = d.get("peso", 0)
        _talla_p = d.get("talla", 0)
        _imc_p   = round(_peso_p / (_talla_p/100)**2, 1) if _talla_p > 0 and _peso_p > 0 else 0
        _gad_p   = d.get("gad7", 0)
        _phq_p   = d.get("phq9", 0)
        _farmacos_r = [f["Medicamento"] for f in st.session_state.farmacos] if st.session_state.farmacos else []

        _gad_nivel = ("Mínima" if _gad_p<=4 else "Leve" if _gad_p<=9 else
                      "Moderada" if _gad_p<=14 else "Severa")
        _phq_nivel = ("Mínima" if _phq_p<=4 else "Leve" if _phq_p<=9 else
                      "Moderada" if _phq_p<=14 else "Mod-severa" if _phq_p<=19 else "Severa")

        _fila_peso = (
            f"<tr><td style='color:#4a7a4a;padding:2px 0'>Peso / Talla / IMC:</td>"
            f"<td style='color:#1a2a1a;padding:2px 0'>{_peso_p} kg · {_talla_p} cm"
            f"{f' · IMC {_imc_p}' if _imc_p else ''}</td></tr>"
        ) if _peso_p > 0 else ""

        _fila_gad = (
            f"<tr><td style='color:#4a7a4a;padding:2px 0'>GAD-7 / PHQ-9:</td>"
            f"<td style='color:#1a2a1a;padding:2px 0'>"
            f"{_gad_p}/21 <span style='color:#558b2f'>({_gad_nivel})</span> · "
            f"{_phq_p}/27 <span style='color:#558b2f'>({_phq_nivel})</span></td></tr>"
        ) if (_gad_p > 0 or _phq_p > 0) else ""

        _fila_farmacos = (
            f"<tr><td style='color:#4a7a4a;padding:2px 0;vertical-align:top'>Medicación actual:</td>"
            f"<td style='color:#1a2a1a;padding:2px 0;font-size:10px'>{', '.join(_farmacos_r)}</td></tr>"
        ) if _farmacos_r else ""

        receta_html = f"""
<div style="background:#ffffff;font-family:Georgia,serif;color:#1a2a1a;
            border:2px solid #2d5a27;border-radius:4px;
            max-width:900px;margin:0 auto;overflow:hidden;">

  <div style="background:#1a4a1a;
              padding:18px 28px;display:flex;justify-content:space-between;align-items:center;">
    <div>
      <div style="font-size:22px;font-weight:700;color:#ffffff;letter-spacing:2px;">RECETA MÉDICA MAGISTRAL</div>
      <div style="font-size:11px;color:#8fcc8f;margin-top:3px;letter-spacing:1px;">
        CANNABINOIDES MEDICINALES — FÓRMULA MAGISTRAL PERSONALIZADA
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:11px;color:#8fcc8f;">RNA: <strong style="color:#ffffff;">A10684</strong></div>
      <div style="font-size:11px;color:#8fcc8f;margin-top:2px;">CMP: <strong style="color:#ffffff;">82817</strong></div>
      <div style="font-size:10px;color:#6aa86a;margin-top:2px;">DIGEMID autorizado</div>
    </div>
  </div>

  <!-- FRANJA DORADA RNA -->
  <div style="background:#0d1f0d;padding:6px 28px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2d5a27;">
    <div style="font-size:11px;color:#4dc8b4;letter-spacing:1px;">
      FISIOIMPERIUM &nbsp;·&nbsp; Av. Infancia N° 410, Consultorio 2, Cusco
    </div>
    <div style="font-size:11px;color:#4dc8b4;">
      📞 924 074 152 / 942 185 939
    </div>
  </div>

  <!-- CUERPO PRINCIPAL -->
  <div style="display:flex;background:#f9fdf9;">

    <!-- COLUMNA IZQUIERDA -->
    <div style="width:52%;padding:20px 24px;border-right:1px solid #c8e6c8;">

      <!-- DATOS PACIENTE -->
      <div style="background:#e8f5e8;border:1px solid #4caf50;border-radius:6px;padding:12px 16px;margin-bottom:14px;">
        <div style="font-size:9px;color:#2d6b2d;letter-spacing:2px;font-weight:700;margin-bottom:8px;border-bottom:1px solid #81c784;padding-bottom:4px;">
          DATOS DEL PACIENTE
        </div>
        <table style="width:100%;font-size:12px;border-collapse:collapse;">
          <tr>
            <td style="color:#4a7a4a;padding:2px 0;width:40%;">Paciente:</td>
            <td style="color:#1a2a1a;font-weight:700;padding:2px 0;">{d.get('nombres','___').upper()}</td>
          </tr>
          <tr>
            <td style="color:#4a7a4a;padding:2px 0;">Documento:</td>
            <td style="color:#1a2a1a;padding:2px 0;">{d.get('dni','___')}</td>
          </tr>
          <tr>
            <td style="color:#4a7a4a;padding:2px 0;">Edad / Sexo:</td>
            <td style="color:#1a2a1a;padding:2px 0;">{edad_str} &nbsp;·&nbsp; {d.get('sexo','___')}</td>
          </tr>
          <tr>
            <td style="color:#4a7a4a;padding:2px 0;">Diagnóstico:</td>
            <td style="color:#1a3a1a;font-weight:600;padding:2px 0;">{dx_p}</td>
          </tr>
          <tr>
            <td style="color:#4a7a4a;padding:2px 0;">CIE-10 / CIE-11:</td>
            <td style="color:#2d6b2d;font-family:monospace;padding:2px 0;">{cie_p} / {cie11_p}</td>
          </tr>
          {(f"<tr><td style='color:#4a7a4a;padding:2px 0;font-size:10px'>Dx secundario:</td><td style='color:#558b2f;font-family:monospace;font-size:10px'>{d.get('cie10_sec1','')} {d.get('dx_nombre_sec1','')}</td></tr>") if d.get('cie10_sec1') else ""}
          {_fila_peso}
          {_fila_gad}
          {_fila_farmacos}
        </table>
      </div>

      <!-- FÓRMULA MAGISTRAL -->
      <div style="margin-bottom:14px;">
        <div style="font-size:9px;color:#2d6b2d;letter-spacing:2px;font-weight:700;margin-bottom:8px;
                    border-bottom:2px solid #2d6b2d;padding-bottom:4px;">
          FÓRMULA MAGISTRAL
        </div>
        <table style="width:100%;border-collapse:collapse;font-size:11px;">
          <thead>
            <tr style="background:#2d6b2d;">
              <th style="padding:6px 8px;color:#ffffff;text-align:left;font-weight:500;">Medicamento (DCI)</th>
              <th style="padding:6px 8px;color:#ffffff;text-align:center;">Concentración</th>
              <th style="padding:6px 8px;color:#ffffff;text-align:center;">Presentación</th>
              <th style="padding:6px 8px;color:#ffffff;text-align:center;">Cant.</th>
            </tr>
          </thead>
          <tbody>
            <tr style="background:#f1f8e9;">
              <td style="padding:8px;border-bottom:1px solid #c8e6c8;color:#1a2a1a;font-size:11px;line-height:1.4;">
                Extracto Estandarizado de Cannabidiol<br>
                <span style="font-size:9px;color:#558b2f;">Fórmula Magistral · Cannabis Sativa L.</span><br>
                <span style="font-size:9px;color:#558b2f;">Solución oral · Ratio {ratio if "ratio" in dir() else d.get("ratio","20:1")}</span>
              </td>
              <td style="padding:8px;border-bottom:1px solid #c8e6c8;text-align:center;color:#2d6b2d;font-weight:600;">
                {mg_p} mg/ml<br>
                <span style="font-size:9px;color:#558b2f;">{terp_str}</span>
              </td>
              <td style="padding:8px;border-bottom:1px solid #c8e6c8;text-align:center;color:#1a2a1a;">
                Frasco {vol_p} ml
              </td>
              <td style="padding:8px;border-bottom:1px solid #c8e6c8;text-align:center;font-weight:700;color:#2d6b2d;">
                02
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- INFO QUIMICO Y VALIDEZ -->
      <div style="background:#e8f5e8;border:1px solid #81c784;border-radius:4px;padding:8px 12px;margin-bottom:14px;font-size:11px;">
        <strong style="color:#2d6b2d;">Información para el Químico Farmacéutico:</strong>
        <span style="color:#4a7a4a;">Ninguna restricción adicional</span><br>
        <strong style="color:#2d6b2d;">Receta válida por:</strong>
        <span style="color:#4a7a4a;">30 días · Renovable con evaluación</span>
      </div>

      <!-- FIRMA -->
      <div style="text-align:center;margin-top:20px;padding-top:12px;border-top:1px dashed #81c784;">
        <div style="font-size:13px;font-weight:700;color:#1a3a1a;">MD. J. CARLOS JARA OVALLE</div>
        <div style="font-size:11px;color:#2d6b2d;margin-top:2px;">RNA A10684 &nbsp;·&nbsp; CMP 82817</div>
        <div style="font-size:10px;color:#4a7a4a;margin-top:2px;">Médico Cirujano · Especialista Cannabinología</div>
        <div style="font-size:10px;color:#558b2f;margin-top:4px;">Fecha: {fecha_p}</div>
      </div>
    </div>

    <!-- COLUMNA DERECHA -->
    <div style="width:48%;padding:20px 20px;">

      <!-- POSOLOGÍA -->
      <div style="margin-bottom:14px;">
        <div style="font-size:9px;color:#2d6b2d;letter-spacing:2px;font-weight:700;margin-bottom:8px;
                    border-bottom:2px solid #2d6b2d;padding-bottom:4px;">
          POSOLOGÍA E INDICACIONES
        </div>
        <div style="font-size:11px;color:#1a2a1a;line-height:1.7;background:#f9fdf9;
                    border-left:3px solid #4caf50;padding:10px 12px;border-radius:0 4px 4px 0;">
          <strong>Posología:</strong> Vía sublingual. Iniciar con <strong>{gtt_p} gota{'s' if gtt_p != 1 else ''}</strong>
          ({dosis_real} mg CBD) · <strong>{freq_rec}</strong>.<br>
          Incrementar {inc_dias_txt} según tolerancia hasta máximo {gtt_max} gotas/día
          ({round(gtt_max * mg_gota_p, 1)} mg/día).<br>
          {obs_p}<br><br>
          {('<strong>Protocolo clínico:</strong> ' + _ind_texto + '<br><br>') if _ind_texto else ''}
          <strong>Indicaciones:</strong> {_indicaciones_base}
        </div>
      </div>

      <!-- TABLA TITULACIÓN -->
      <div>
        <div style="font-size:9px;color:#2d6b2d;letter-spacing:2px;font-weight:700;margin-bottom:8px;
                    border-bottom:2px solid #2d6b2d;padding-bottom:4px;">
          CUADRO REFERENCIAL DE TITULACIÓN
        </div>
        <table style="width:100%;border-collapse:collapse;font-size:11px;">
          <thead>
            <tr style="background:#1a4a1a;">
              <th style="padding:6px 8px;color:#8fcc8f;text-align:left;font-weight:500;">Días</th>
              <th style="padding:6px 8px;color:#8fcc8f;text-align:center;">Gotas</th>
              <th style="padding:6px 8px;color:#8fcc8f;text-align:left;">Frecuencia</th>
              <th style="padding:6px 8px;color:#8fcc8f;text-align:center;">Fase</th>
            </tr>
          </thead>
          <tbody>
            {rows_tit}
          </tbody>
        </table>
        <div style="font-size:9px;color:#4a7a4a;margin-top:6px;padding:6px 8px;background:#e8f5e8;border-radius:4px;">
          * Reajuste de dosis cada {inc_dias} días según tolerancia. Máximo: {gtt_max} gotas/día.<br>
          * D: Desayuno &nbsp;·&nbsp; A: Almuerzo &nbsp;·&nbsp; C: Cena &nbsp;·&nbsp; AD: Antes de Dormir
        </div>
      </div>

      <!-- SEGUNDA FIRMA DERECHA -->
      <div style="text-align:center;margin-top:24px;padding-top:12px;border-top:1px dashed #81c784;">
        <div style="font-size:12px;font-weight:700;color:#1a3a1a;">MD. J. CARLOS JARA OVALLE</div>
        <div style="font-size:10px;color:#2d6b2d;">RNA A10684 &nbsp;·&nbsp; CMP 82817</div>
      </div>
    </div>
  </div>

  <!-- PIE DE PÁGINA -->
  <div style="background:#1a4a1a;padding:8px 28px;display:flex;justify-content:space-between;align-items:center;">
    <div style="font-size:10px;color:#6aa86a;">
      ESTACIÓN VITAL PRO &nbsp;·&nbsp; Sistema de Gestión Médica
    </div>
    <div style="font-size:10px;color:#6aa86a;">
      {datetime.now().strftime("%d/%m/%Y %H:%M")} &nbsp;·&nbsp; {d.get('ciudad','Cusco')}
    </div>
  </div>
</div>
"""
        import streamlit.components.v1 as _cr2
        _cr2.html(
            "<html><head><meta charset=\"utf-8\"><style>"
            ".pbtn{display:block;width:100%;padding:10px;margin-bottom:8px;"
            "background:#1a4a1a;color:#8fcc8f;border:1px solid #2d6b2d;"
            "border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;text-align:center}"
            ".pbtn:hover{background:#2d6b2d;color:#fff}"
            "@media print{.pbtn{display:none!important}body{background:#fff!important}"
            "@page{size:A4;margin:8mm 10mm}}</style></head>"
            "<body style=\"margin:0;padding:6px;background:#0d1b0d\">"
            "<button class=\"pbtn\" onclick=\"window.print()\">IMPRIMIR / GUARDAR PDF</button>"
            + receta_html + "</body></html>",
            height=920, scrolling=True
        )

        # ── BOTONES FINALES ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()
        st.markdown("#### 💾 Finalizar Historia Clínica")
        fc1,fc2,fc3 = st.columns(3)

        with fc1:
            if st.button("💾 Registrar en Base de Datos", use_container_width=True, type="primary"):
                reg = {
                    "fecha":      d.get("fecha_hc", datetime.now().strftime("%d/%m/%Y")),
                    "hora":       datetime.now().strftime("%H:%M"),
                    "nombres":    d.get("nombres",""),
                    "dni":        d.get("dni",""),
                    "edad":       d.get("edad",0),
                    "sexo":       d.get("sexo",""),
                    "ocupacion":  d.get("ocupacion",""),
                    "ciudad":     d.get("ciudad",""),
                    "altitud":    d.get("altitud",0),
                    "motivo":     d.get("motivo",""),
                    "cie10":      d.get("cie10","S/D"),
                    "cie11":      d.get("cie11",""),
                    "dx_nombre":  d.get("dx_nombre",""),
                    "gad7":       d.get("gad7",0),
                    "phq9":       d.get("phq9",0),
                    "mejoria":    0,
                    "cbd_mg_ml":  st.session_state.get("mg_in",0),
                    "volumen_ml": st.session_state.get("ml_in",0),
                    "gotas_dia":  st.session_state.get("gtt_in",0),
                    "ratio":      ratio if "ratio" in dir() else "",
                    "notas":      (f"Dx2: {d.get('cie10_sec1','')} {d.get('dx_nombre_sec1','')} | "
                                  f"Dx3: {d.get('cie10_sec2','')} {d.get('dx_nombre_sec2','')} | "
                                  f"Plan: {d.get('plan_tx','')}").strip(" |"),
                }
                pid = guardar_paciente(reg)
                if st.session_state.farmacos:
                    guardar_farmacos(pid, st.session_state.farmacos)
                st.success(f"✅ Historia de **{d.get('nombres','paciente')}** registrada - ID #{pid}")

        with fc2:
            if st.button("📩 Enviar resumen por WhatsApp", use_container_width=True):
                msg = (f"Consulta: {d.get('nombres','')} - DNI {d.get('dni','')} - {d.get('edad','')} años\n"
                       f"Motivo: {d.get('motivo','')}\n"
                       f"GAD-7: {d.get('gad7',0)} - PHQ-9: {d.get('phq9',0)}\n"
                       f"Receta: {mg_p}mg/ml - {vol_p}ml - {gtt_p} gotas/día - {ratio}")
                st.link_button("🔗 Abrir WhatsApp →", wa_url(msg), use_container_width=True)

        with fc3:
            if st.button("🔄 Nueva historia clínica", use_container_width=True):
                st.session_state.paso_hc = 0
                st.session_state.hc_data = {}
                st.session_state.farmacos = []
                st.rerun()

        nav_btns(paso)

# ══════════════════════════════════════════════════════════════
#  MÓDULO DASHBOARD
# ══════════════════════════════════════════════════════════════
elif modulo == "⚡ Dashboard":
    st.title("⚡ Dashboard")
    s = stats_db()
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total pacientes", s["total"])
    c2.metric("Consultas hoy", s["hoy"])
    c3.metric("GAD-7 promedio", f"{s['gad_avg']:.1f}")
    c4.metric("PHQ-9 promedio", f"{s['phq_avg']:.1f}")
    c5.metric("Citas pendientes", s["citas_p"])
    if s["ultima"]:
        st.caption(f"Última consulta: {s['ultima'][0]} - {s['ultima'][1]}")
    st.divider()

    df = leer_pacientes()
    if not df.empty:
        tab1, tab2, tab3 = st.tabs(["📋 Todos los registros","📊 Estadísticas","💊 Cannabis"])

        with tab1:
            busq = st.text_input("🔍 Buscar", placeholder="Nombre, DNI, diagnóstico...")
            if busq:
                df = leer_pacientes(busq)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("⬇ Exportar CSV",
                df.to_csv(index=False).encode("utf-8"),
                f"evipro_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv", use_container_width=True)

        with tab2:
            if len(df) > 0:
                col_a, col_b = st.columns(2)
                with col_a:
                    card("DISTRIBUCIÓN POR SEXO")
                    if "sexo" in df.columns:
                        vc = df["sexo"].value_counts()
                        for k,v in vc.items():
                            pct = v/len(df)*100
                            st.markdown(f"**{k}:** {v} ({pct:.0f}%)")
                    card("TOP DIAGNÓSTICOS CIE-10")
                    if "cie10" in df.columns:
                        top = df[df["cie10"]!=""]["cie10"].value_counts().head(8)
                        for k,v in top.items():
                            st.markdown(f"`{k}` — {v} caso{'s' if v>1 else ''}")
                with col_b:
                    card("PSICOMETRÍA")
                    if "gad7" in df.columns and "phq9" in df.columns:
                        gad_dist = {"Mínima (0-4)":0,"Leve (5-9)":0,"Moderada (10-14)":0,"Severa (15+)":0}
                        for v in df["gad7"].dropna():
                            if v<=4: gad_dist["Mínima (0-4)"]+=1
                            elif v<=9: gad_dist["Leve (5-9)"]+=1
                            elif v<=14: gad_dist["Moderada (10-14)"]+=1
                            else: gad_dist["Severa (15+)"]+=1
                        st.markdown("**GAD-7 distribución:**")
                        for k,v in gad_dist.items():
                            if v > 0: st.markdown(f"  {k}: {v}")

        with tab3:
            df_can = df[df["cie10"].str.startswith("F12", na=False) | df["ratio"].notna()]
            if not df_can.empty:
                card("PACIENTES CON PROTOCOLO CANNABIS")
                st.metric("Total", len(df_can))
                if "ratio" in df_can.columns:
                    top_ratio = df_can["ratio"].value_counts().head(5)
                    st.markdown("**Ratios más recetados:**")
                    for k,v in top_ratio.items():
                        if k: st.markdown(f"  `{k}` — {v} recetas")
                st.dataframe(
                    df_can[["fecha","nombres","cie10","ratio","cbd_mg_ml","volumen_ml","gotas_dia"]],
                    use_container_width=True, hide_index=True)
            else:
                st.info("Sin pacientes con protocolo cannabis registrados.")
    else:
        st.info("Sin pacientes registrados aún. Completa una Historia Clínica para comenzar.")

# ══════════════════════════════════════════════════════════════
#  MÓDULO PACIENTES
# ══════════════════════════════════════════════════════════════
elif modulo == "👥 Pacientes":
    st.title("👥 Pacientes")
    busq = st.text_input("🔍 Buscar por nombre, DNI o diagnóstico")
    df = leer_pacientes(busq)

    if not df.empty:
        st.caption(f"{len(df)} registro{'s' if len(df)>1 else ''} encontrado{'s' if len(df)>1 else ''}")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        card("VER EXPEDIENTE COMPLETO")
        ids = df["id"].tolist()
        sel_id = st.selectbox("Seleccionar paciente por ID",
                              ["Seleccione..."] + [f"#{i} — {r}" for i,r in zip(df["id"], df["nombres"])])
        if sel_id != "Seleccione...":
            pid = int(sel_id.split("—")[0].strip().replace("#",""))
            pac = leer_paciente_id(pid)
            if pac:
                c1,c2,c3 = st.columns(3)
                c1.metric("Nombre", pac.get("nombres",""))
                c2.metric("DNI", pac.get("dni",""))
                c3.metric("Edad", f"{pac.get('edad','')} años")
                c4,c5,c6 = st.columns(3)
                c4.metric("CIE-10", pac.get("cie10",""))
                c5.metric("GAD-7", pac.get("gad7",""))
                c6.metric("PHQ-9", pac.get("phq9",""))
                st.markdown(f"**Diagnóstico:** {pac.get('dx_nombre','—')}")
                st.markdown(f"**Motivo:** {pac.get('motivo','—')}")
                if pac.get("cbd_mg_ml"):
                    st.markdown(f"**Receta:** {pac.get('ratio','')} - {pac.get('cbd_mg_ml','')} mg/ml - {pac.get('volumen_ml','')} ml - {pac.get('gotas_dia','')} gotas/día")
    else:
        st.info("Sin pacientes registrados." if not busq else f"Sin resultados para '{busq}'.")

# ══════════════════════════════════════════════════════════════
#  MÓDULO EMERGENCIA CANNÁBICA
# ══════════════════════════════════════════════════════════════
elif modulo == "🌿 Emergencia Cannábica":
    st.title("🌿 Emergencia Cannábica")
    st.markdown("""
    <div style='background:#0d1b26;border-left:3px solid #FF4444;padding:0.85rem 1.1rem;
                border-radius:0 8px 8px 0;margin-bottom:1.5rem;'>
        Protocolo de respuesta inmediata ante reacciones adversas a cannabinoides.
        Marque los síntomas presentes para activar el protocolo.
    </div>
    """, unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    syms = [
        c1.checkbox("💓 Taquicardia (>100 lpm)"),
        c1.checkbox("🫁 Dificultad respiratoria"),
        c1.checkbox("🌀 Mareo / desequilibrio severo"),
        c2.checkbox("😰 Ansiedad / pánico intenso"),
        c2.checkbox("🧠 Confusión / neblina mental"),
        c2.checkbox("🔴 Psicosis transitoria / alucinaciones"),
    ]
    n_syms = sum(syms)
    if n_syms >= 3:
        st.error(f"🚨 {n_syms} síntomas activos — EMERGENCIA. Activar protocolo de inmediato.")
        st.link_button("🔥 Llamar Dr. Jara ahora", wa_url("EMERGENCIA CANNÁBICA: paciente con síntomas severos. Requiero asistencia INMEDIATA."), use_container_width=True)
    elif n_syms >= 1:
        st.warning(f"⚠️ {n_syms} síntoma(s) detectado(s) — Monitoreo activo recomendado.")
        st.link_button("📞 Consultar al médico", wa_url(f"Consulta Emergencia Cannabis: {n_syms} síntoma(s) activo(s). ¿Indicaciones?"), use_container_width=True)

    st.divider()
    card("PROTOCOLO ESTÁNDAR — REACCIÓN ADVERSA CANNABIS")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Pasos inmediatos:**
        1. Posición semi-sentada o decúbito lateral
        2. Ambiente tranquilo, silencioso, luz tenue
        3. Hidratación oral si tolera
        4. Oximetría de pulso — alertar si SpO₂ < 90%
        5. Evitar estimulación adicional (pantallas, ruido)
        """)
    with col2:
        st.markdown("""
        **No administrar:**
        - Benzodiacepinas sin indicación médica
        - Otros cannabinoides
        - Alcohol

        **Tiempo de resolución esperado:**
        - Intoxicación aguda: 2–6 horas
        - Psicosis transitoria: 12–48 horas
        """)

# ══════════════════════════════════════════════════════════════
#  MÓDULO AUDITORÍA
# ══════════════════════════════════════════════════════════════
elif modulo == "📊 Auditoría":
    st.title("📊 Auditoría — Solo Lectura")
    s = stats_db()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Expedientes totales", s["total"])
    c2.metric("Consultas hoy", s["hoy"])
    c3.metric("GAD-7 promedio", f"{s['gad_avg']:.1f}")
    c4.metric("PHQ-9 promedio", f"{s['phq_avg']:.1f}")
    st.divider()
    df = leer_pacientes()
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        col_exp1, col_exp2 = st.columns(2)
        col_exp1.download_button(
            "⬇ Exportar CSV completo",
            df.to_csv(index=False).encode("utf-8"),
            f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv", use_container_width=True)
        resumen = f"EVIPro - Reporte de Auditoría\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        resumen += f"Total expedientes: {s['total']}\nGAD-7 promedio: {s['gad_avg']:.1f}\nPHQ-9 promedio: {s['phq_avg']:.1f}\n"
        col_exp2.download_button(
            "⬇ Exportar resumen TXT",
            resumen.encode("utf-8"),
            f"resumen_{datetime.now().strftime('%Y%m%d')}.txt",
            "text/plain", use_container_width=True)
    else:
        st.warning("Sin expedientes registrados aún.")

# ══════════════════════════════════════════════════════════════
#  MÓDULO CITAS Y AGENDA
# ══════════════════════════════════════════════════════════════
elif modulo == "📅 Citas y Agenda":
    st.title("📅 Citas y Agenda")

    tab_nueva, tab_agenda = st.tabs(["➕ Nueva Cita", "📋 Agenda"])

    with tab_nueva:
        card("REGISTRAR NUEVA CITA")
        with st.form("form_cita", clear_on_submit=True):
            f1,f2 = st.columns(2)
            pac_nom = f1.text_input("Nombre del paciente")
            pac_tel = f2.text_input("Teléfono / WhatsApp")
            f3,f4,f5 = st.columns(3)
            esp = f3.selectbox("Especialidad", ["Medicina General","Cannabinología","Teleconsulta","Psicometría","Seguimiento","Urgencia"])
            fec = f4.date_input("Fecha", min_value=date.today(), format="DD/MM/YYYY")
            hor = f5.selectbox("Hora", ["07:00","08:00","09:00","10:00","11:00","12:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00"])
            notas_c = st.text_input("Notas adicionales (opcional)")
            if st.form_submit_button("✅ Registrar cita", use_container_width=True, type="primary") and pac_nom:
                guardar_cita({"paciente":pac_nom,"fecha":str(fec),"hora":hor,"especialidad":esp,"notas":notas_c})
                st.success(f"✅ Cita registrada para **{pac_nom}** el {fec.strftime('%d/%m/%Y')} a las {hor}")
                if pac_tel:
                    msg = f"Hola {pac_nom}, su cita en Estación Vital Pro es el {fec.strftime('%d/%m/%Y')} a las {hor} hs. Dr. Carlos Jara — CMP 82817."
                    st.link_button("📲 Enviar recordatorio WhatsApp", wa_url(msg))

    with tab_agenda:
        card("AGENDA DE CITAS")
        solo_pend = st.toggle("Mostrar solo pendientes", value=True)
        df_citas = leer_citas(solo_pend)
        if not df_citas.empty:
            st.caption(f"{len(df_citas)} cita(s)")
            for _, row in df_citas.iterrows():
                est_color = "#4dc8b4" if row["estado"]=="Pendiente" else "#39FF14" if row["estado"]=="Completada" else "#FF4444"
                with st.expander(f"📅 {row['fecha']} {row['hora']} - **{row['paciente']}** - {row['especialidad']}"):
                    cc1,cc2,cc3 = st.columns(3)
                    cc1.markdown(f"**Estado:** <span style='color:{est_color}'>{row['estado']}</span>", unsafe_allow_html=True)
                    cc2.markdown(f"**Especialidad:** {row['especialidad']}")
                    if row.get("notas"): cc3.markdown(f"**Notas:** {row['notas']}")
                    bc1,bc2,bc3 = st.columns(3)
                    if bc1.button("✅ Completada", key=f"comp_{row['id']}"):
                        actualizar_estado_cita(row["id"], "Completada"); st.rerun()
                    if bc2.button("❌ Cancelada", key=f"canc_{row['id']}"):
                        actualizar_estado_cita(row["id"], "Cancelada"); st.rerun()
                    if bc3.button("🗑 Eliminar", key=f"del_{row['id']}"):
                        eliminar_cita(row["id"]); st.rerun()
        else:
            st.info("Sin citas registradas." if not solo_pend else "Sin citas pendientes.")
