import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import os
import base64

# ---------------------------------------------------------
# 1. Configuration et Style CSS (Base de Référence)
# ---------------------------------------------------------
st.set_page_config(page_title="Cryptos Analyst IA", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    stApp, .main, [data-testid="stAppViewContainer"] { background-color: #0d0e12 !important; color: #ffffff !important; }
    .block-container { max-width: 850px !important; padding-top: 2rem !important; margin: 0 auto !important; }
    .avatar-wrapper { display: flex; justify-content: center; margin-bottom: 15px; }
    .avatar-wrapper img { width: 120px !important; height: 120px !important; border-radius: 50% !important; border: 3px solid #ffd700 !important; }
    h1 { color: #ffd700 !important; text-align: center; font-weight: 800 !important; }
    .welcome-msg { text-align: center; color: #ffffff !important; font-size: 1.15rem; font-weight: 600; margin-bottom: 2rem; }
    .stMarkdown code { background-color: transparent !important; color: #ffd700 !important; font-weight: bold !important; font-size: 1.1em !important; }
    blockquote { border-left: 3px solid #ffd700 !important; background-color: #161b22 !important; color: #ffd700 !important; padding: 10px 15px !important; }
    /* Bouton Jaune texte Noir */
    .stButton>button { background-color: #ffd700 !important; color: #000000 !important; font-weight: bold !important; width: 100% !important; border-radius: 8px !important; border: none !important; }
    .stButton>button:hover { background-color: #e6c200 !important; color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Avatar et Limites
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

# ---------------------------------------------------------
# Cache & API CoinGecko (Données chiffrées officielles)
# ---------------------------------------------------------
@st.cache_data(ttl=3600) # Réduit à 1h pour garantir la fraîcheur des données de marché
def get_coingecko_data(query):
    try:
        search_res = requests.get(f"https://api.coingecko.com/api/v3/search?query={query}", timeout=10).json()
        coins = search_res.get("coins", [])
        if not coins: return None, None
        coin_id = coins[0]["id"]
        
        data = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false", timeout=10).json()
        market = data.get("market_data", {})
        
        return {
            "name": data.get("name"), 
            "symbol": data.get("symbol", "").upper(), 
            "rank": data.get("market_cap_rank"),
            "current_price_usd": market.get("current_price", {}).get("usd"), 
            "market_cap_usd": market.get("market_cap", {}).get("usd"),
            "total_volume_24h": market.get("total_volume", {}).get("usd"),
            "price_change_24h": market.get("price_change_percentage_24h"),
            "price_change_7d": market.get("price_change_percentage_7d"),
            "platforms": data.get("platforms", {})
        }, None
    except Exception as e: return None, f"Erreur API: {str(e)}"

def generate_content_with_key_failover(prompt_text, system_instruction):
    gemini_keys = [st.secrets[k] for k in st.secrets if "GEMINI_API_KEY" in k]
    if not gemini_keys: return None, "Aucune clé API trouvée dans secrets.toml"
    
    last_error = ""
    for api_key in gemini_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
            response = model.generate_content(prompt_text)
            if response and response.text: return response.text, None
        except Exception as e:
            last_error = str(e)
            continue
    return None, last_error

# ---------------------------------------------------------
# Prompt Système Strict & Actualités 24H
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un analyste financier crypto. Ton ton est familier, chaleureux et enthousiaste.

RÈGLES ABSOLUES :
1. Tu ne dois générer QUE le rapport final en Markdown (aucun brouillon, aucune introduction).
2. SECTION CHIFFRES EN DIRECT : Tu DOIS utiliser STRICTEMENT et UNIQUEMENT les chiffres exacts fournis par l'API CoinGecko dans le prompt (Prix, Market Cap, Volume 24h, Variations). N'invente ni n'estime aucun chiffre.
3. ACTUALITÉS & MOTORS : Intègre les dernières actualités et dynamiques des DERNIÈRES 24 HEURES concernant le projet.

Structure stricte :
1. 📌 C'EST QUOI CE PROJET ? (Verdict à chaud)
2. 📊 LES CHIFFRES EN DIRECT (Utilise obligatoirement les chiffres précis de CoinGecko : Prix, Market Cap, Volume 24h, Variation 24h/7j, Rang)
> 🎓 Minute Pédago - Explique une notion simple.
3. 🔗 INFOS TECHNIQUES (RÉSEAUX & CONTRATS)
4. 🚀 GROS MOTEURS DE HAUSSE & ACTUALITÉS (Mets en avant les infos fraîches des dernières 24h)
5. ⚠️ RISQUES À NE PAS IGNORER
6. ⚔️ COMPARATIF CONCURRENCE
7. 🎯 MON VERDICT & CONSEIL DE POTE (Note sur 10 selon le barème : 0-3.5=Danger, 4-5.5=Moyen, 6-7.5=Solide, 8-10=Pilier).
"""

# ---------------------------------------------------------
# Interface
# ---------------------------------------------------------
crypto_input = st.text_input("Quelle crypto veux-tu décortiquer ?", placeholder="ex: BGB, SUI...")
if requests_left > 0: st.caption(f"⚡ Crédits restants : **{requests_left} / 2**")
else: st.warning("⚠️ Limite atteinte.")

if st.button("🚀 LANCER L'ANALYSE", disabled=(requests_left <= 0)):
    cg_data, err = get_coingecko_data(crypto_input)
    if err: st.error(err)
    elif not cg_data: st.warning("😔 Crypto introuvable sur CoinGecko.")
    else:
        platforms = "\n".join([f"- {n.upper()}: `{a}`" for n, a in cg_data['platforms'].items() if a])
        
        # Injection stricte des données CoinGecko pour bloquer toute estimation erronée
        coingecko_context = f"""
DONNÉES OFFICIELLES COINGECKO EN DIRECT :
- Nom : {cg_data['name']} ({cg_data['symbol']})
- Prix actuel USD : `${cg_data['current_price_usd']}`
- Capitalisation boursière (Market Cap) : `${cg_data['market_cap_usd']:,}` USD
- Volume d'échange 24h : `${cg_data['total_volume_24h']:,}` USD
- Variation sur 24h : `{cg_data['price_change_24h']}%`
- Variation sur 7 jours : `{cg_data['price_change_7d']}%`
- Classement Market Cap : #{cg_data['rank']}
- Adresses de contrats / Réseaux :
{platforms}
"""
        prompt = f"{coingecko_context}\n\nRédige l'analyse complète de ce projet en incluant ses actualités les plus récentes des dernières 24 heures et en respectant la structure exigée."
        
        with st.spinner("Récupération des données CoinGecko et rédaction du rapport..."):
            res, gen_err = generate_content_with_key_failover(prompt, SYSTEM_INSTRUCTION)
            if res:
                st.session_state.daily_request_count += 1
                st.markdown(res)
                st.code(res, language="markdown")
            else: st.error(f"Erreur de génération : {gen_err}")
