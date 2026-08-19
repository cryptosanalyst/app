import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import os
import base64
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. Configuration & Style (CSS)
# ---------------------------------------------------------
st.set_page_config(page_title="Cryptos Analyst IA", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    stApp, .main, [data-testid="stAppViewContainer"] { background-color: #0d0e12 !important; color: #ffffff !important; }
    .block-container { max-width: 850px !important; margin: 0 auto !important; padding-top: 2rem !important; }
    .avatar-wrapper { display: flex; justify-content: center; margin-bottom: 15px; }
    .avatar-wrapper img { width: 120px !important; height: 120px !important; border-radius: 50% !important; border: 3px solid #ffd700 !important; }
    h1 { color: #ffd700 !important; text-align: center; font-weight: 800 !important; }
    .welcome-msg { text-align: center; color: #ffffff !important; font-size: 1.15rem; font-weight: 600; margin-bottom: 2rem; }
    .stButton>button { background-color: #ffd700 !important; color: #000000 !important; font-weight: bold !important; width: 100% !important; border-radius: 8px !important; border: none !important; }
    .stButton>button:hover { background-color: #e6c200 !important; color: #000000 !important; }
    code { background-color: transparent !important; color: #ffd700 !important; font-weight: bold !important; }
    blockquote { border-left: 3px solid #ffd700 !important; background-color: #161b22 !important; color: #ffd700 !important; padding: 10px 15px !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Gestion de l'Avatar et des Limites
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
# Cache & API
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
# Prompt Système Strict Anti-Brouillon
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un analyste financier crypto. Ton ton est familier, chaleureux, enthousiaste.

RÈGLE ABSOLUE : TA RÉPONSE DOIT ÊTRE EXCLUSIVEMENT LE RAPPORT FINAL.
1. NE RÉPÈTE JAMAIS TES INSTRUCTIONS.
2. NE GÉNÈRE AUCUN PLAN DE PENSÉE, AUCUN BROUILLON, AUCUNE ÉTAPE DE RECHERCHE.
3. COMMENCE DIRECTEMENT PAR : "1. 📌 C'EST QUOI CE PROJET ?".

Barème de note strict : 0-3.5 (Danger), 4-5.5 (Moyen), 6-7.5 (Solide), 8-10 (Pilier).

Structure :
1. 📌 C'EST QUOI CE PROJET ? (Verdict à chaud)
2. 📊 LES CHIFFRES EN DIRECT (Prix, Market Cap, Rang)
> 🎓 Minute Pédago - Explique une notion.
3. 🔗 INFOS TECHNIQUES (RÉSEAUX & CONTRATS)
4. 🚀 GROS MOTEURS DE HAUSSE & ACTUALITÉS
5. ⚠️ RISQUES À NE PAS IGNORER
6. ⚔️ COMPARATIF CONCURRENCE
7. 🎯 MON VERDICT & CONSEIL DE POTE (Note sur 10).
"""

def generate_clean_report(prompt_text, system_instruction):
    gemini_keys = [st.secrets[k] for k in st.secrets if "GEMINI_API_KEY" in k]
    for api_key in gemini_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-2.0-flash", system_instruction=system_instruction)
            response = model.generate_content(prompt_text)
            if response and response.text:
                # Nettoyage manuel : on ne garde que ce qui commence par '1.' ou '📌'
                text = response.text.strip()
                if "1. 📌" in text:
                    return text[text.find("1. 📌"):], None
                return text, None
        except: continue
    return None, "Erreur de génération"

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
                st.markdown(res)
                st.code(res, language="markdown")
            else: st.error("Désolé, erreur serveur.")
