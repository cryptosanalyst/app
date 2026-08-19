import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import os
import base64
import streamlit.components.v1 as components
import re

# ---------------------------------------------------------
# 1. Configuration & Style (CSS) - Tout centré et responsive
# ---------------------------------------------------------
st.set_page_config(page_title="Cryptos Analyst IA", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    stApp, .main, [data-testid="stAppViewContainer"] { background-color: #0d0e12 !important; color: #ffffff !important; }
    .block-container { max-width: 850px !important; margin: 0 auto !important; padding-top: 2rem !important; }
    
    /* Avatar centré et rond */
    .avatar-wrapper { display: flex; justify-content: center; margin-bottom: 15px; }
    .avatar-wrapper img { width: 120px !important; height: 120px !important; border-radius: 50% !important; border: 3px solid #ffd700 !important; box-shadow: 0 0 15px rgba(255, 215, 0, 0.4) !important; object-fit: cover !important; }
    
    /* Titre 1000px max, centré */
    h1 { color: #ffd700 !important; text-align: center; font-weight: 800 !important; font-size: min(1000px, 10vw) !important; margin-bottom: 0.5rem !important; }
    .welcome-msg { text-align: center; color: #ffffff !important; font-size: 1.15rem; font-weight: 600; margin-bottom: 2rem; }
    
    /* Bouton Jaune / Texte Noir */
    .stButton>button { background-color: #ffd700 !important; color: #000000 !important; font-weight: bold !important; width: 100% !important; border-radius: 8px !important; border: none !important; }
    .stButton>button:hover { background-color: #e6c200 !important; color: #000000 !important; }
    
    /* Prix et Notes */
    code { background-color: transparent !important; color: #ffd700 !important; font-weight: bold !important; font-size: 1.1em !important; }
    blockquote { border-left: 3px solid #ffd700 !important; background-color: #161b22 !important; color: #ffd700 !important; padding: 10px 15px !important; }
    
    /* Input */
    .stTextInput > label { display: block; text-align: center; font-weight: 700 !important; color: #ffd700 !important; font-size: 1.1rem !important; }
    .stTextInput input { text-align: center !important; background-color: #1e222d !important; color: #ffffff !important; border: 1px solid #ffd700 !important; border-radius: 8px !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Avatar et Persistance (Limite 2/jour)
# ---------------------------------------------------------
def get_image_base64(file_path):
    with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()

avatar_filename = next((f for f in ["avatar.jpg", "avatar.jpeg", "avatar.png"] if os.path.exists(f)), None)
if avatar_filename:
    st.markdown(f'<div class="avatar-wrapper"><img src="data:image/jpeg;base64,{get_image_base64(avatar_filename)}"></div>', unsafe_allow_html=True)

st.markdown("<h1>Cryptos Analyst IA</h1>", unsafe_allow_html=True)
st.markdown("<div class='welcome-msg'>Bienvenue je suis l'agent IA de cryptos analyst je vous aide à analyser rapidement vos projets crypto</div>", unsafe_allow_html=True)

TODAY = str(date.today())
if "daily_request_count" not in st.session_state: st.session_state.daily_request_count = 0
requests_left = max(0, 2 - st.session_state.daily_request_count)

components.html(f"""<script>
    if (localStorage.getItem("d") !== "{TODAY}") {{ localStorage.setItem("d", "{TODAY}"); localStorage.setItem("c", "0"); }}
</script>""", height=0)

# ---------------------------------------------------------
# Cache 12H et Vérification CoinGecko
# ---------------------------------------------------------
@st.cache_data(ttl=43200)
def get_coingecko_data(query):
    try:
        search_res = requests.get(f"https://api.coingecko.com/api/v3/search?query={query}", timeout=10).json()
        if not search_res.get("coins"): return None, None
        coin_id = search_res["coins"][0]["id"]
        data = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false", timeout=10).json()
        market = data.get("market_data", {})
        return {
            "name": data.get("name"), "symbol": data.get("symbol", "").upper(), "rank": data.get("market_cap_rank"),
            "current_price_usd": market.get("current_price", {}).get("usd"), "market_cap_usd": market.get("market_cap", {}).get("usd"),
            "platforms": data.get("platforms", {})
        }, None
    except: return None, "Erreur API"

# ---------------------------------------------------------
# IA : Rotation Clés, Détection Modèles & Nettoyage Réponse
# ---------------------------------------------------------
def generate_clean_report(prompt_text, system_instruction):
    gemini_keys = [st.secrets[k] for k in st.secrets if "GEMINI_API_KEY" in k]
    for api_key in gemini_keys:
        try:
            genai.configure(api_key=api_key)
            # Détection auto
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            for model_name in ["models/gemini-2.5-flash", "models/gemini-2.0-flash"] + models:
                try:
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
                    response = model.generate_content(prompt_text)
                    if response and response.text:
                        # Nettoyage radical : on coupe tout ce qui précède le titre 1
                        txt = response.text
                        start_match = re.search(r"1\.\s?📌", txt)
                        if start_match: txt = txt[start_match.start():]
                        return txt, None
                except: continue
        except: continue
    return None, "Erreur de génération"

# ---------------------------------------------------------
# Prompt Système Strict
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un analyste financier crypto. Ton ton est familier, chaleureux, enthousiaste.

RÈGLE ABSOLUE : TA RÉPONSE DOIT ÊTRE EXCLUSIVEMENT LE RAPPORT FINAL.
NE GÉNÈRE PAS DE PLAN DE PENSÉE, DE BROUILLON, NI DE PHRASES D'INTRODUCTION (ex: "Voici mon analyse").
COMMENCE DIRECTEMENT PAR LE TITRE DE LA SECTION 1.

Barème strict :
- 0-3.5/10 (RISQUE TRÈS ÉLEVÉ) : Danger, memecoin suspect.
- 4-5.5/10 (MOYEN) : Spéculatif, concurrence forte.
- 6-7.5/10 (SOLIDE) : Utility réelle.
- 8-10/10 (PILIER) : Bitcoin/ETH.

Structure :
1. 📌 C'EST QUOI CE PROJET ? (Verdict à chaud)
2. 📊 LES CHIFFRES EN DIRECT (Prix, Market Cap, Rang)
> 🎓 Minute Pédago - Explique une notion simple.
3. 🔗 INFOS TECHNIQUES (RÉSEAUX & CONTRATS)
4. 🚀 GROS MOTEURS DE HAUSSE & ACTUALITÉS
5. ⚠️ RISQUES À NE PAS IGNORER
6. ⚔️ COMPARATIF CONCURRENCE
7. 🎯 MON VERDICT & CONSEIL DE POTE (Note sur 10).
"""

# ---------------------------------------------------------
# Interface
# ---------------------------------------------------------
crypto_input = st.text_input("Quelle crypto veux-tu décortiquer ?", placeholder="ex: BGB, SUI...")
if requests_left > 0: st.caption(f"⚡ Crédits restants : **{requests_left} / 2**")
else: st.warning("⚠️ Limite atteinte.")

if st.button("🚀 LANCER L'ANALYSE", disabled=(requests_left <= 0)):
    cg_data, err = get_coingecko_data(crypto_input)
    if not cg_data: st.warning("😔 Crypto introuvable.")
    else:
        platforms = "\n".join([f"- {n.upper()}: `{a}`" for n, a in cg_data['platforms'].items() if a])
        prompt = f"Data: {cg_data}. Analyse: {cg_data['name']}. Adresses: {platforms}. Effectue la vérification Web et rédige le rapport."
        
        with st.spinner("Analyse en cours..."):
            res, gen_err = generate_clean_report(prompt, SYSTEM_INSTRUCTION)
            if res:
                st.session_state.daily_request_count += 1
                components.html(f"<script>localStorage.setItem('c', '{st.session_state.daily_request_count}');</script>", height=0)
                st.markdown(res)
                st.code(res, language="markdown")
            else: st.error("Désolé, erreur serveur.")
