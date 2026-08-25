import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import os
import base64

# ---------------------------------------------------------
# 1. Configuration et Style CSS (Avec Background Dynamique Top Cryptos)
# ---------------------------------------------------------
st.set_page_config(page_title="Cryptos Analyst IA", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    /* Fond sombre général */
    stApp, .main, [data-testid="stAppViewContainer"] { 
        background-color: #0d0e12 !important; 
        color: #ffffff !important; 
    }
    
    /* Conteneur principal au premier plan */
    .block-container { 
        max-width: 850px !important; 
        padding-top: 2rem !important; 
        margin: 0 auto !important; 
        position: relative;
        z-index: 10;
    }

    /* --- BACKGROUND DYNAMIQUE : BULLES FLOTTANTES CRYPTO --- */
    .crypto-bubbles-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        z-index: 1;
        pointer-events: none;
    }

    .crypto-bubble {
        position: absolute;
        bottom: -100px;
        background: rgba(22, 27, 34, 0.75);
        border: 2px solid #ffd700;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
        animation: floatUp 15s infinite linear;
    }

    .crypto-bubble img {
        width: 60%;
        height: 60%;
        object-fit: contain;
        border-radius: 50%;
    }

    @keyframes floatUp {
        0% { transform: translateY(0) rotate(0deg); opacity: 0; }
        10% { opacity: 0.6; }
        90% { opacity: 0.6; }
        100% { transform: translateY(-110vh) rotate(360deg); opacity: 0; }
    }

    .bubble-1 { left: 5%; width: 50px; height: 50px; animation-duration: 12s; animation-delay: 0s; }
    .bubble-2 { left: 15%; width: 70px; height: 70px; animation-duration: 18s; animation-delay: 2s; }
    .bubble-3 { left: 28%; width: 45px; height: 45px; animation-duration: 14s; animation-delay: 4s; }
    .bubble-4 { left: 40%; width: 65px; height: 65px; animation-duration: 16s; animation-delay: 1s; }
    .bubble-5 { left: 55%; width: 55px; height: 55px; animation-duration: 13s; animation-delay: 5s; }
    .bubble-6 { left: 70%; width: 75px; height: 75px; animation-duration: 20s; animation-delay: 3s; }
    .bubble-7 { left: 82%; width: 50px; height: 50px; animation-duration: 15s; animation-delay: 6s; }
    .bubble-8 { left: 92%; width: 60px; height: 60px; animation-duration: 17s; animation-delay: 2.5s; }

    /* --- DESIGN DES ELEMENTS --- */
    .avatar-wrapper { display: flex; justify-content: center; margin-bottom: 15px; }
    .avatar-wrapper img { width: 120px !important; height: 120px !important; border-radius: 50% !important; border: 3px solid #ffd700 !important; object-fit: cover; }
    
    h1 { color: #ffd700 !important; text-align: center; font-weight: 800 !important; }
    .welcome-msg { text-align: center; color: #ffffff !important; font-size: 1.15rem; font-weight: 600; margin-bottom: 2rem; }
    
    .stMarkdown code { background-color: transparent !important; color: #ffd700 !important; font-weight: bold !important; font-size: 1.1em !important; }
    blockquote { border-left: 3px solid #ffd700 !important; background-color: #161b22 !important; color: #ffd700 !important; padding: 10px 15px !important; }
    
    .stButton>button { background-color: #ffd700 !important; color: #000000 !important; font-weight: bold !important; width: 100% !important; border-radius: 8px !important; border: none !important; height: 50px !important; }
    .stButton>button:hover { background-color: #e6c200 !important; color: #000000 !important; }
    </style>

    <div class="crypto-bubbles-bg">
        <div class="crypto-bubble bubble-1"><img src="https://assets.coingecko.com/coins/images/1/large/bitcoin.png" alt="BTC"></div>
        <div class="crypto-bubble bubble-2"><img src="https://assets.coingecko.com/coins/images/279/large/ethereum.png" alt="ETH"></div>
        <div class="crypto-bubble bubble-3"><img src="https://assets.coingecko.com/coins/images/325/large/Tether.png" alt="USDT"></div>
        <div class="crypto-bubble bubble-4"><img src="https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png" alt="BNB"></div>
        <div class="crypto-bubble bubble-5"><img src="https://assets.coingecko.com/coins/images/4128/large/solana.png" alt="SOL"></div>
        <div class="crypto-bubble bubble-6"><img src="https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png" alt="XRP"></div>
        <div class="crypto-bubble bubble-7"><img src="https://assets.coingecko.com/coins/images/5/large/dogecoin.png" alt="DOGE"></div>
        <div class="crypto-bubble bubble-8"><img src="https://assets.coingecko.com/coins/images/975/large/cardano.png" alt="ADA"></div>
    </div>
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
# Cache & API CoinGecko
# ---------------------------------------------------------
@st.cache_data(ttl=43200)
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
    except Exception as e: return None, f"Erreur API CoinGecko : {str(e)}"

# ---------------------------------------------------------
# API Gemini : Modèles actuels (Gemini 3.6 Flash)
# ---------------------------------------------------------
def generate_content_with_key_failover(prompt_text, system_instruction):
    gemini_keys = [st.secrets[k] for k in st.secrets if "GEMINI_API_KEY" in k]
    if not gemini_keys: return None, "Aucune clé API trouvée dans secrets.toml"
    
    candidate_models = ["gemini-3.6-flash", "gemini-3.5-flash"]
    last_error = ""

    for api_key in gemini_keys:
        try:
            genai.configure(api_key=api_key)
            for model_name in candidate_models:
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=system_instruction
                    )
                    response = model.generate_content(prompt_text)
                    if response and response.text:
                        return response.text, None
                except Exception as m_err:
                    last_error = str(m_err)
                    continue
        except Exception as k_err:
            last_error = str(k_err)
            continue

    return None, f"Erreur de génération : {last_error}"

# ---------------------------------------------------------
# Prompt Système Strict & Barème de Notation Cohérent
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un analyste financier crypto intransigeant. Ton ton est familier, chaleureux et enthousiaste, mais extrêmement rigoureux sur l'évaluation des risques.

RÈGLES ABSOLUES :
1. Tu ne dois générer QUE le rapport final en Markdown.
2. NE GÉNÈRE AUCUN plan de pensée, aucune étape de recherche interne, aucun brouillon. 
3. COMMENCE DIRECTEMENT par le titre de la section 1 ("1. 📌 C'EST QUOI CE PROJET ?").
4. SECTION CHIFFRES EN DIRECT : Utilise STRICTEMENT et UNIQUEMENT les chiffres exacts de CoinGecko transmis dans le prompt.
5. ACTUALITÉS & MOTEURS : Intègre les actualités fraîches des dernières 24 heures.

BARÈME DE NOTATION STRICT ET OBLIGATOIRE (COHÉRENCE AVEC L'ANALYSE) :
La note finale doit refléter fidèlement le texte de ton analyse. Interdiction d'attribuer une note supérieure à 5/10 si l'analyse relève des risques majeurs, un manque de transparence, une utilité faible ou une forte probabilité de perte en capital.
- **0/10 à 3.5/10 (DANGER / TRÈS RISQUÉ) :** Projet hautement spéculatif, memecoin sans fond, arnaque potentielle, équipe douteuse ou tokenomics toxiques.
- **4/10 à 5/10 (MOYEN / INCERTAIN) :** Projet faible, concurrence trop rude, absence d'utilité concrète ou adoption en berne.
- **5.5/10 à 7/10 (SOLIDE AVEC RÉSERVES) :** Bon projet, équipe sérieuse, cas d'usage réel, mais présentant des risques de marché ou de régulation normaux.
- **7.5/10 à 10/10 (VALEUR SÛRE / PILIER) :** Actif majeur, ultra-solide, adopté mondialement (ex: Bitcoin, Ethereum).

Structure stricte :
1. 📌 C'EST QUOI CE PROJET ? (Verdict à chaud)
2. 📊 LES CHIFFRES EN DIRECT (Utilise obligatoirement les chiffres précis de CoinGecko : Prix, Market Cap, Volume 24h, Variation 24h/7j, Rang)
> 🎓 Minute Pédago - Explique une notion simple.
3. 🔗 INFOS TECHNIQUES (RÉSEAUX & CONTRATS)
4. 🚀 GROS MOTEURS DE HAUSSE & ACTUALITÉS (Infos fraîches des dernières 24h)
5. ⚠️ RISQUES À NE PAS IGNORER
6. ⚔️ COMPARATIF CONCURRENCE
7. 🎯 MON VERDICT & CONSEIL DE POTE (Note sur 10 respectant impérativement le barème strict ci-dessus).
"""

# ---------------------------------------------------------
# Interface Utilisateur & Exécution
# ---------------------------------------------------------
crypto_input = st.text_input("Quelle crypto veux-tu décortiquer ?", placeholder="ex: BGB, SUI...")
if requests_left > 0: st.caption(f"⚡ Crédits restants : **{requests_left} / 2**")
else: st.warning("⚠️ Limite atteinte.")

if st.button("🚀 LANCER L'ANALYSE", disabled=(requests_left <= 0)):
    cg_data, err = get_coingecko_data(crypto_input)
    if err: 
        st.error(err)
    elif not cg_data: 
        st.warning("😔 Crypto introuvable sur CoinGecko.")
    else:
        platforms = "\n".join([f"- {n.upper()}: `{a}`" for n, a in cg_data['platforms'].items() if a]) if cg_data['platforms'] else "Réseau natif ou non applicable."
        
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
        prompt = f"{coingecko_context}\n\nRédige l'analyse complète de ce projet en incluant ses actualités les plus récentes des dernières 24 heures, et attribue une note en accord parfait avec le niveau de risque réel du projet."
        
        with st.spinner("Récupération des données CoinGecko et rédaction du rapport..."):
            res, gen_err = generate_content_with_key_failover(prompt, SYSTEM_INSTRUCTION)
            if res:
                st.session_state.daily_request_count += 1
                st.markdown(res)
                st.markdown("---")
                st.markdown("### 📋 Copier le rapport")
                st.code(res, language="markdown")
            else: 
                st.error(f"Erreur de génération : {gen_err}")
