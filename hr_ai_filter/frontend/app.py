import streamlit as st
import requests
import time
import json
import re
import os

API = os.getenv("API_URL", "http://127.0.0.1:8000")
API_LIST_JOBS = f"{API}/jobs/list"
API_CV_UPLOAD = f"{API}/cv/upload"
API_ANALYZE = f"{API}/jobs/analyze"

st.set_page_config(
    page_title="HR AI Filter",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { 
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
}

header[data-testid="stHeader"] { display: none !important; }
.block-container { padding-top: 1rem !important; max-width: 1400px !important; }

.stApp {
    background: linear-gradient(135deg, #F3F2F1 0%, #E1DFDD 100%);
}

.header-wrap {
    background: linear-gradient(90deg, #0078D4 0%, #005A9E 100%) !important;
    padding: 24px 32px;
    border-radius: 4px;
    margin-bottom: 30px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.15);
}
.header-title { 
    font-size: 30px; 
    font-weight: 700; 
    color: #FFFFFF !important; 
    margin: 0;
    letter-spacing: -0.5px;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
.header-sub { 
    font-size: 15px; 
    color: #FFFFFF !important; 
    margin-top: 6px; 
    opacity: 1;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0,0,0,0.15);
}

.process-flow {
    background: white;
    padding: 25px;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    margin-bottom: 20px;
    border-left: 4px solid #0078D4;
}

.step-container {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
}

.step-icon {
    background: #0078D4 !important;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
    font-weight: 700;
    flex-shrink: 0;
    box-shadow: 0 2px 6px rgba(0,120,212,0.4);
}

.step-icon,
.card .step-icon {
    color: #FFFFFF !important;
}
            
.step-icon.completed {
    background: #107C10 !important;
}

.step-icon.active {
    background: #0078D4 !important;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 2px 4px rgba(0,120,212,0.3); }
    50% { box-shadow: 0 2px 12px rgba(0,120,212,0.6); }
}

.step-label {
    font-size: 14px;
    font-weight: 600;
    color: #323130 !important;
}

.card {
    background: white;
    border: 1px solid #EDEBE9;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 1.6px 3.6px rgba(0,0,0,0.08);
    height: 100%;
}

.card-header {
    font-size: 16px;
    font-weight: 600;
    color: #323130 !important;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #0078D4;
}

.score-box {
    width: 100%;
    text-align: center;
    padding: 20px;
    border-radius: 4px;
    font-size: 48px;
    font-weight: 700;
    color: white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}

.divider-thick {
    height: 4px;
    background: linear-gradient(90deg, #0078D4 0%, #005A9E 100%);
    margin: 30px 0 25px 0;
    border-radius: 2px;
    box-shadow: 0 2px 4px rgba(0,120,212,0.3);
}

.results-section-header {
    background: white;
    padding: 15px 20px;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    margin-bottom: 20px;
    border-left: 4px solid #0078D4;
}

.results-title {
    font-size: 18px;
    font-weight: 600;
    color: #323130 !important;
    margin: 0;
}

.section-title {
    font-size: 14px;
    font-weight: 600;
    color: #0078D4 !important;
    margin: 0 0 12px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.result-item {
    background: #F3F2F1;
    padding: 8px 12px;
    border-radius: 3px;
    margin-bottom: 6px;
    border-left: 3px solid #0078D4;
    font-size: 13px;
    color: #323130 !important;
    line-height: 1.5;
}

.result-item.weakness {
    border-left-color: #D13438;
}

.result-text {
    padding: 12px;
    background: #F3F2F1;
    border-radius: 3px;
    font-size: 13px;
    color: #323130 !important;
    line-height: 1.6;
}

.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 5px;
}

.status-badge.success {
    background: #DFF6DD;
    color: #107C10 !important;
}

.status-badge.warning {
    background: #FFF4CE;
    color: #797775 !important;
}

.status-badge.info {
    background: #E1F5FE;
    color: #005A9E !important;
}

.stButton > button {
    background: #0078D4 !important;
    color: white !important;
    border: none !important;
    padding: 10px 24px !important;
    border-radius: 3px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
    width: 100%;
}

.stButton > button:hover {
    background: #005A9E !important;
    box-shadow: 0 4px 8px rgba(0,120,212,0.3) !important;
}

.stSelectbox > div > div {
    border: 1px solid #EDEBE9 !important;
    border-radius: 3px !important;
    background: white !important;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: white !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: white !important;
    border: 2px solid #C7C7C7 !important;
    color: #323130 !important;
}

.stSelectbox div[data-baseweb="select"] > div:hover {
    border-color: #0078D4 !important;
}

.stSelectbox label {
    color: #323130 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}

.stSelectbox input {
    color: #323130 !important;
    font-weight: 500 !important;
}

.stSelectbox [role="button"] {
    color: #323130 !important;
}

.stSelectbox [role="button"] span {
    color: #323130 !important;
}

.stSelectbox div[data-baseweb="select"] span {
    color: #323130 !important;
}

.stSelectbox [data-baseweb="popover"] {
    background: white !important;
}

.stSelectbox ul {
    background: white !important;
}

.stSelectbox li {
    color: #323130 !important;
    background: white !important;
}

.stSelectbox li:hover {
    background: #F3F2F1 !important;
    color: #323130 !important;
}

.stFileUploader {
    border: 2px dashed #C7C7C7 !important;
    border-radius: 3px !important;
    padding: 20px !important;
    background: white !important;
}

.stFileUploader:hover {
    border-color: #0078D4 !important;
}

.stFileUploader label {
    color: #323130 !important;
    font-weight: 600 !important;
}

.stFileUploader section {
    color: #323130 !important;
}

.stFileUploader section > div {
    color: #323130 !important;
}

.stFileUploader button {
    background-color: white !important;
    color: #323130 !important;
    border: 2px solid #0078D4 !important;
    font-weight: 600 !important;
}

.stFileUploader button:hover {
    background-color: #0078D4 !important;
    color: white !important;
    border: 2px solid #0078D4 !important;
}

.stFileUploader section button {
    background-color: white !important;
    color: #323130 !important;
    border: 2px solid #0078D4 !important;
}

.stFileUploader section button:hover {
    background-color: #0078D4 !important;
    color: white !important;
}

.stFileUploader section span {
    color: #323130 !important;
    font-weight: 500 !important;
}

.stFileUploader section small {
    color: #605E5C !important;
}

.stFileUploader [data-testid="stFileUploaderDropzone"] {
    background-color: white !important;
}

.stFileUploader [data-testid="stFileUploaderDropzone"] span {
    color: #323130 !important;
    font-weight: 500 !important;
}

.stFileUploader [data-testid="stFileUploaderDropzone"] small {
    color: #605E5C !important;
}

.stFileUploader [data-testid="stFileUploaderFile"] {
    background-color: #F3F2F1 !important;
    border: 1px solid #EDEBE9 !important;
}

.stFileUploader [data-testid="stFileUploaderFile"] span {
    color: #323130 !important;
    font-weight: 500 !important;
}

.stFileUploader [data-testid="stFileUploaderFile"] small {
    color: #605E5C !important;
}

.stFileUploader [data-testid="stFileUploaderFileName"] {
    color: #323130 !important;
    font-weight: 500 !important;
}

.stFileUploader [data-testid="stFileUploaderFileSize"] {
    color: #605E5C !important;
}

div[data-testid="stExpander"] {
    background: #F3F2F1;
    border: 1px solid #EDEBE9;
    border-radius: 3px;
}

div[data-testid="stExpander"] summary {
    color: #323130 !important;
}

div[data-testid="stExpander"] summary span {
    color: #323130 !important;
}

div[data-testid="stExpander"] p {
    color: #323130 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: white;
    padding: 8px;
    border-radius: 4px;
}

.stTabs [data-baseweb="tab"] {
    background: #F3F2F1;
    border-radius: 3px;
    color: #323130 !important;
    font-weight: 600;
    padding: 12px 32px !important;
    font-size: 15px !important;
}

.stTabs [aria-selected="true"] {
    background: #0078D4 !important;
    color: white !important;
}

.stSpinner > div {
    color: #0078D4 !important;
}

.card p, .card span, .card div {
    color: #323130 !important;
}

.stMarkdown {
    color: #323130 !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-wrap">
    <div class="header-title">🧠 HR AI Filter - Sistema de Evaluación de Candidatos</div>
    <div class="header-sub">Análisis automatizado mediante IA • Embeddings • LLM</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📋 Proceso de Evaluación", "📊 Dashboard & Métricas"])

with tab1:

    @st.cache_data(show_spinner=False, ttl=60)  # Refresh every 60 seconds
    def load_jobs():
        try:
            return requests.get(API_LIST_JOBS, timeout=5).json().get("jobs", [])
        except:
            return []

    jobs = load_jobs()
    if not jobs:
        st.error("❌ No hay convocatorias disponibles en el sistema.")
        st.stop()

    st.markdown("""
    <div class="process-flow">
        <div style="font-size: 18px; font-weight: 600; color: #323130; margin-bottom: 15px;">
            📋 Flujo del Proceso de Evaluación
        </div>
        <div style="font-size: 13px; color: #605E5C;">
            Complete cada paso del proceso para obtener la evaluación del candidato
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1.2], gap="medium")

    final_result = None
    exec_time = None

    with col1:
        st.markdown("""
        <div class="card">
            <div class="step-container">
                <div class="step-icon">1</div>
                <div class="step-label">Seleccionar Convocatoria</div>
            </div>
        """, unsafe_allow_html=True)

        job_names = [j["job_name"] for j in jobs]
        selected_job = st.selectbox("Puesto disponible", job_names, label_visibility="collapsed")

        job_ok = False
        job_text = ""

        if selected_job:
            j = next(item for item in jobs if item["job_name"] == selected_job)
            job_text = j.get("text", "")
            if job_text.strip():
                job_ok = True

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <div class="step-container">
                <div class="step-icon">2</div>
                <div class="step-label">Cargar Currículum</div>
            </div>
        """, unsafe_allow_html=True)

        cv_pdf = st.file_uploader("Cargar CV en PDF", type=["pdf"], label_visibility="collapsed")

        cv_ok = False
        emb_ok = False
        cv_text = ""

        if cv_pdf:
            with st.spinner("Procesando documento..."):
                files = {"file": (cv_pdf.name, cv_pdf, "application/pdf")}
                resp = requests.post(API_CV_UPLOAD, files=files)

            if resp.status_code == 200:
                data = resp.json()
                cv_text = data.get("text", "")
                if cv_text.strip():
                    cv_ok = True
                # FIX: usar embedding_dim en lugar de embeddings_path
                if data.get("embedding_dim", 0) > 0:
                    emb_ok = True

        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <div class="step-container">
                <div class="step-icon">3</div>
                <div class="step-label">Ejecutar Análisis</div>
            </div>
        """, unsafe_allow_html=True)

        ready = job_ok and cv_ok and emb_ok

        if not ready:
            st.markdown("<span class='status-badge warning'>⏳ Esperando datos</span>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:12px;color:#605E5C;margin-top:5px;'>Complete los pasos anteriores</p>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        run_eval = st.button("🚀 Iniciar Evaluación IA", type="primary", disabled=not ready)

        if run_eval and ready:
            start_time = time.time()

            payload = {
                "cv_text": cv_text,
                "job_text": job_text,
                "job_name": selected_job
            }

            with st.spinner("Analizando con modelo de lenguaje..."):
                r = requests.post(API_ANALYZE, json=payload)

            exec_time = time.time() - start_time

            if r.status_code == 200:
                final_result = r.json()

            st.markdown(f"<span class='status-badge info'>⏱ {exec_time:.2f}s</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="card">
            <div class="step-container">
                <div class="step-icon">4</div>
                <div class="step-label">Puntuación Final</div>
            </div>
        """, unsafe_allow_html=True)

        if final_result:
            score_value = int(final_result.get("score_final", 0))

            if score_value >= 75:
                color = "#107C10"
                label = "APTO"
            elif score_value >= 50:
                color = "#FFB900"
                label = "MODERADO"
            else:
                color = "#D13438"
                label = "NO APTO"

            st.markdown(
                f"<div class='score-box' style='background:{color};'>{score_value}<div style='font-size:16px;margin-top:5px;color:white!important;'>{label}</div></div>",
                unsafe_allow_html=True
            )
            
            with st.expander("🔍 Ver datos técnicos (JSON)"):
                st.json(final_result)
        else:
            st.markdown("<span class='status-badge info'>ℹ️ Sin resultados</span>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:12px;color:#605E5C;margin-top:5px;'>Ejecute la evaluación para ver la puntuación</p>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    if final_result:
        st.markdown("<div class='divider-thick'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="results-section-header">
            <div class="results-title">📊 Análisis Detallado del Candidato</div>
        </div>
        """, unsafe_allow_html=True)

        parsed = {
            "resumen": final_result.get("resumen", "No disponible"),
            "fortalezas": final_result.get("fortalezas", []),
            "debilidades": final_result.get("debilidades", [])
        }

        if parsed["resumen"] == "No disponible" and not parsed["fortalezas"] and not parsed["debilidades"]:
            raw = final_result.get("raw_output", "")

            def parse_llm_text(text):
                result = {
                    "resumen": "No disponible",
                    "fortalezas": [],
                    "debilidades": []
                }

                json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group(1))
                        result["resumen"] = json_data.get("resumen", "No disponible")
                        result["fortalezas"] = json_data.get("fortalezas", [])
                        result["debilidades"] = json_data.get("debilidades", [])
                        return result
                    except:
                        pass

                brace_match = re.search(r'(\{[\s\S]*?\})', text)
                if brace_match:
                    try:
                        json_data = json.loads(brace_match.group(1))
                        result["resumen"] = json_data.get("resumen", "No disponible")
                        result["fortalezas"] = json_data.get("fortalezas", [])
                        result["debilidades"] = json_data.get("debilidades", [])
                        return result
                    except:
                        pass

                m = re.search(r"\*\*Resumen:\*\*\s*(.+?)(\n\n|\Z)", text, re.DOTALL)
                if m:
                    result["resumen"] = m.group(1).strip()

                m = re.search(r"\*\*Fortalezas:\*\*\s*(.+?)(\n\n|\Z)", text, re.DOTALL)
                if m:
                    lines = m.group(1).strip().split("\n")
                    result["fortalezas"] = [l.strip("*•- ").strip() for l in lines if l.strip()]

                m = re.search(r"\*\*Debilidades:\*\*\s*(.+?)(\n\n|\Z)", text, re.DOTALL)
                if m:
                    lines = m.group(1).strip().split("\n")
                    result["debilidades"] = [l.strip("*•- ").strip() for l in lines if l.strip()]

                return result

            parsed = parse_llm_text(raw)

        result_col1, result_col2, result_col3 = st.columns(3, gap="medium")

        with result_col1:
            st.markdown("""
            <div class="card">
                <div class='section-title'>📝 Resumen Ejecutivo</div>
            """, unsafe_allow_html=True)
            st.markdown(f"<div class='result-text'>{parsed.get('resumen', 'No disponible')}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with result_col2:
            st.markdown("""
            <div class="card">
                <div class='section-title'>💪 Fortalezas Identificadas</div>
            """, unsafe_allow_html=True)

            if parsed.get("fortalezas"):
                for f in parsed.get("fortalezas"):
                    st.markdown(f"<div class='result-item'>{f}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='result-text' style='font-style:italic;color:#605E5C!important;'>No se identificaron fortalezas</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with result_col3:
            st.markdown("""
            <div class="card">
                <div class='section-title'>⚠️ Áreas de Mejora</div>
            """, unsafe_allow_html=True)

            if parsed.get("debilidades"):
                for d in parsed.get("debilidades"):
                    st.markdown(f"<div class='result-item weakness'>{d}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='result-text' style='font-style:italic;color:#605E5C!important;'>No se identificaron áreas de mejora</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="card" style="margin-top:20px;">
        <div class="card-header">📊 Dashboard de Métricas</div>
        <div style="padding:40px;text-align:center;color:#605E5C;">
            <div style="font-size:48px;margin-bottom:10px;">📈</div>
            <div style="font-size:18px;font-weight:600;color:#323130;margin-bottom:10px;">
                Dashboard en Desarrollo
            </div>
            <div style="font-size:14px;">
                Próximamente: Estadísticas de evaluaciones, métricas de rendimiento, análisis comparativo y reportes avanzados.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
