import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import os
import base64
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. Configuration de la page Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cryptos Analyst IA",
    page_icon="🤖",
    layout="wide"
)

# Style CSS : Centrage absolu & thème sombre
st.markdown("""
    <style>
    stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #0d0e12 !important;
        color: #ffffff !important;
    }
    
    .block-container {
        max-width: 850px !important;
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        margin: 0 auto !important;
    }

    .avatar-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-bottom: 15px;
    }

    .avatar-wrapper img {
        width: 120px !important;
        height: 120px !important;
        border-radius: 50% !important;
        border: 3px solid #ffd700 !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.4) !important;
        object-fit: cover !important;
    }

    h1 { 
        color: #ffd700 !important; 
        text-align: center; 
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }

    .welcome-msg {
        text-align: center;
        color: #ffffff !important;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 2rem;
    }

    code {
        background-color: #ffd700 !important;
        color: #0d0e12 !important;
        font-weight: bold !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-size: 0.95em !important;
    }

    blockquote {
        border-left: 3px solid #ffd700 !important;
        background-color: #161b22 !important;
        color: #ffd700 !important;
        padding: 8px 15px !important;
        margin: 10px 0 !important;
        border-radius: 0 8px 8px 0 !important;
    }

    blockquote p, blockquote em, blockquote i, blockquote span {
        color: #ffd700 !important;
        font-weight: 500 !important;
    }

    .stTextInput > label {
        display: block;
        text-align: center;
        font-weight: 700 !important;
        color: #ffd700 !important;
        font-size: 1.1rem !important;
    }

    .stTextInput input {
        text-align: center !important;
        background-color: #1e222d !important;
        color: #ffffff !important;
        border: 1px solid #ffd700 !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }

    .stButton>button { 
        background-color: #ffd700 !important; 
        color: #0d0e12 !important; 
        font-weight: bold !important; 
        width: 100% !important; 
        border-radius: 8px !important; 
        height: 50px !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Avatar & Sync Limite
# ---------------------------------------------------------
def get_image_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

avatar_filename = None
for filename in ["avatar.jpg", "avatar.jpeg", "avatar.png"]:
    if os.path.exists(filename):
        avatar_filename = filename
        break

if avatar_filename:
    img_b64 = get_image_base64(avatar_filename)
    st.markdown(f"""
        <div class="avatar-wrapper">
            <img src="data:image/jpeg;base64,{img_b64}" alt="Avatar">
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1>Cryptos Analyst IA</h1>", unsafe_allow_html=True)
st.markdown("<div class='welcome-msg'>Bienvenue je suis l'agent IA de cryptos analyst je vous aide à analyser rapidement vos projets crypto</div>", unsafe_allow_html=True)

TODAY = str(date.today())
if "daily_request_count" not in st.session_state: st.session_state.daily_request_count = 0
requests_left = max(0, 2 - st.session_state.daily_request_count)

js_sync = f"""<script>
    const today = "{TODAY}";
    if (localStorage.getItem("crypto_analyst_date") !== today) {{
        localStorage.setItem("crypto_analyst_date", today);
        localStorage.setItem("crypto_analyst_count", "0");
    }}
</script>"""
components.html(js_sync, height=0)

# ---------------------------------------------------------
# Cache CoinGecko (12H = 43200s)
# ---------------------------------------------------------
@st.cache_data(ttl=43200)
def get_coingecko_data(query):
    try:
        search_url = f"https://api.coingecko.com/api/v3/search?query={query}"
        search_res = requests.get(search_url, timeout=10).json()
        
        coins = search_res.get("coins", [])
        if not coins:
            return None, "Actif non trouvé sur CoinGecko."
        
        coin_id = coins[0]["id"]
        
        data_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false"
        coin_data = requests.get(data_url, timeout=10).json()
        
        market = coin_data.get("market_data", {})
        platforms = coin_data.get("platforms", {})
        
        result = {
            "name": coin_data.get("name"),
            "symbol": coin_data.get("symbol", "").upper(),
            "rank": coin_data.get("market_cap_rank"),
            "current_price_usd": market.get("current_price", {}).get("usd"),
            "market_cap_usd": market.get("market_cap", {}).get("usd"),
            "total_volume_24h": market.get("total_volume", {}).get("usd"),
            "price_change_24h_pct": market.get("price_change_percentage_24h"),
            "price_change_7d_pct": market.get("price_change_percentage_7d"),
            "ath_usd": market.get("ath", {}).get("usd"),
            "ath_date": market.get("ath_date", {}).get("usd"),
            "atl_usd": market.get("atl", {}).get("usd"),
            "atl_date": market.get("atl_date", {}).get("usd"),
            "circulating_supply": market.get("circulating_supply"),
            "total_supply": market.get("total_supply"),
            "max_supply": market.get("max_supply"),
            "platforms": platforms
        }
        return result, None
    except Exception as e:
        return None, f"Erreur CoinGecko : {str(e)}"

# ---------------------------------------------------------
# Rotation Clés API avec Modèles Mis à Jour
# ---------------------------------------------------------
def get_gemini_api_keys():
    keys = []
    if "GEMINI_API_KEY" in st.secrets: keys.append(st.secrets["GEMINI_API_KEY"])
    for i in range(1, 6):
        key_name = f"GEMINI_API_KEY_{i}"
        if key_name in st.secrets: keys.append(st.secrets[key_name])
    return list(dict.fromkeys(keys))

def generate_content_with_key_failover(prompt_text, system_instruction):
    gemini_keys = get_gemini_api_keys()
    candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-latest"]
    last_err = "Aucune réponse générée."

    for api_key in gemini_keys:
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
            except Exception as e:
                last_err = str(e)
                continue
    return None, last_err

# ---------------------------------------------------------
# Prompt Système
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un analyste financier senior passionné par la crypto. Tu exprimes tes analyses avec un ton familier, chaleureux, accessible et enthousiaste (tutoiement naturel).

CONSIGNE CRITIQUE - EXACTITUDE & RIGOUREUSES VÉRIFICATIONS :
- Intègre les métriques chiffrées de CoinGecko fournies (Prix, Market Cap, ATH/ATL, Réseaux/Contrats).
- Fournis les informations de la DERNIÈRE MISE À JOUR DISPONIBLE.

CONSIGNE CRITIQUE - SÉVÉRITÉ ET COHÉRENCE DE LA NOTE :
- 0/10 à 3.5/10 (RISQUE TRÈS ÉLEVÉ) : Memecoin, projet suspect, sans utilité.
- 4/10 à 5.5/10 (RISQUE MOYEN/ÉLEVÉ) : Projet spéculatif, forte concurrence.
- 6/10 à 7.5/10 (SOLIDE) : Bon projet, utility réelle, risques modérés.
- 8/10 à 10/10 (PILIER) : Bitcoin, Ethereum, etc.

Structure du rapport :
1. 📌 C'EST QUOI CE PROJET ? (Verdict à chaud)
2. 📊 LES CHIFFRES EN DIRECT
> 🎓 Minute Pédago - Explique simplement une notion (ex: Market Cap).
3. 🔗 INFOS TECHNIQUES (RÉSEAUX & CONTRATS)
- Liste clairement tous les réseaux blockchain et les adresses de contrat correspondantes fournies.
4. 🚀 GROS MOTEURS DE HAUSSE & ACTUALITÉS
5. ⚠️ RISQUES À NE PAS IGNORER
6. ⚔️ COMPARATIF CONCURRENCE
7. 🎯 MON VERDICT & CONSEIL DE POTE (Note sur 10 selon le barème strict).
"""

# ---------------------------------------------------------
# Interface
# ---------------------------------------------------------
crypto_input = st.text_input("Quelle crypto veux-tu décortiquer aujourd'hui ?", placeholder="Tape un ticker (ex: BGB, SUI...)")

if requests_left > 0: st.caption(f"⚡ Crédits restants : **{requests_left} / 2**")
else: st.warning("⚠️ Limite atteinte. Reviens demain !")

submit_button = st.button("🚀 LANCER L'ANALYSE D'EXPERT", disabled=(requests_left <= 0))

if submit_button and crypto_input:
    if requests_left <= 0: st.error("Limite quotidienne atteinte.")
    else:
        cg_data, error = get_coingecko_data(crypto_input)
        if not cg_data: st.warning(f"😔 Désolé ! Crypto « {crypto_input} » introuvable sur CoinGecko.")
        else:
            platforms_info = "\n".join([f"- {net.upper()}: `{addr}`" for net, addr in cg_data['platforms'].items() if addr]) if cg_data['platforms'] else "Réseau natif ou données de contrat non applicables."
            data_context = f"""
Données CoinGecko pour {cg_data['name']} ({cg_data['symbol']}) :
- Prix actuel: `${cg_data['current_price_usd']}`
- Market Cap: `${cg_data['market_cap_usd']:,}` USD
- Rang: #{cg_data['rank']}
- RÉSEAUX & ADRESSES CONTRAT: 
{platforms_info}
"""
            prompt_final = f"{data_context}\n\nEffectue l'analyse complète de : {cg_data['name']} ({cg_data['symbol']})"
            
            with st.spinner(f"Rédaction du rapport d'expert pour **{cg_data['name']}**..."):
                response_text, gen_error = generate_content_with_key_failover(prompt_final, SYSTEM_INSTRUCTION)

            if response_text:
                st.session_state.daily_request_count += 1
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown(response_text)
                st.markdown("---")
                st.markdown("### 📋 Copier le rapport")
                st.code(response_text, language="markdown")
            else: st.error(f"Désolé, l'agent IA rencontre un souci : {gen_error}")
