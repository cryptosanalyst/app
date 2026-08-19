import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import os
import base64

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

    /* Centrage parfait de l'avatar */
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

    /* Badges de Prix */
    code {
        background-color: #ffd700 !important;
        color: #0d0e12 !important;
        font-weight: bold !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-size: 0.95em !important;
    }

    /* Notes pédagogiques en Jaune */
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
# Affichage de l'Avatar en Base64
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

# ---------------------------------------------------------
# OPTION A : Limite de 2 requêtes / jour par session
# ---------------------------------------------------------
TODAY = str(date.today())

if "last_access_date" not in st.session_state or st.session_state.last_access_date != TODAY:
    st.session_state.last_access_date = TODAY
    st.session_state.daily_request_count = 0

requests_left = 2 - st.session_state.daily_request_count

# ---------------------------------------------------------
# OPTION B : Cache CoinGecko (1 Heure = 3600 secondes)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
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
            "max_supply": market.get("max_supply")
        }
        return result, None
    except Exception as e:
        return None, f"Erreur CoinGecko : {str(e)}"

# ---------------------------------------------------------
# OPTION C : Rotation sur 5 Clés API avec Recherche Web Active
# ---------------------------------------------------------
def get_gemini_api_keys():
    keys = []
    if "GEMINI_API_KEY" in st.secrets:
        keys.append(st.secrets["GEMINI_API_KEY"])
    
    for i in range(1, 6):
        key_name = f"GEMINI_API_KEY_{i}"
        if key_name in st.secrets:
            keys.append(st.secrets[key_name])
            
    return list(dict.fromkeys(keys))

gemini_keys = get_gemini_api_keys()

if not gemini_keys:
    st.error("⚠️ Aucune clé API Gemini n'a été configurée dans secrets.toml.")
    st.stop()

def generate_content_with_key_failover(prompt_text, system_instruction):
    # Utilisation des modèles Gemini
    candidate_models = ["gemini-3.6-flash", "gemini-1.5-flash-latest"]
    last_err = None

    for api_key in gemini_keys:
        try:
            genai.configure(api_key=api_key)
            for model_name in candidate_models:
                # 1. Tentative avec l'outil de Recherche Web en direct (Search Grounding)
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=system_instruction,
                        tools=['google_search_retrieval']
                    )
                    response = model.generate_content(prompt_text)
                    return response.text, None
                except Exception:
                    # 2. Reconstitution standard si le composant tools spécifique varie
                    try:
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            system_instruction=system_instruction
                        )
                        response = model.generate_content(prompt_text)
                        return response.text, None
                    except Exception as inner_err:
                        last_err = inner_err
                        continue
        except Exception as key_err:
            last_err = key_err
            continue

    return None, last_err

# ---------------------------------------------------------
# Prompt Système Strict (Exactitude & Dernières Mises à Jour)
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un analyste financier senior passionné par la crypto. Tu exprimes tes analyses avec un **ton familier, chaleureux, accessible et très enthousiaste** (tutoiement naturel).

CONSIGNE CRITIQUE - EXACTITUDE & RIGOUREUSES VÉRIFICATIONS :
- Effectue obligatoirement une recherche Web pour VÉRIFIER L'EXACTITUDE des données financières et des dernières actualités majeures concernant le projet.
- Intègre impérativement les métriques chiffrées exactes transmises depuis l'API CoinGecko (prix, rang, Market Cap, ATH/ATL).
- Fournis TOUJOURS les informations de la DERNIÈRE MISE À JOUR DISPONIBLE (ex: changements stratégiques récents, transitions d'échangeur CEX vers UEX, intégrations Layer 2 comme Morph pour BGB, rachats/burns récents, roadmap actuelle).
- Ne sous-entends ou n'invente jamais de fonctionnalités obsolètes ou fausses. Si une information est incertaine, indique-le clairement.

Directives de formatage impératives :
- Entoure TOUJOURS les prix et montants importants de backticks pour former un badge distinct (ex: `$0.60`).
- Place TOUTES les explications pédagogiques / "Minute Pédago" sous forme de citation avec un chevron `>` pour qu'elles s'affichent en jaune.

Structure de ton rapport :

1. 📌 C'EST QUOI CE PROJET CONCRÈTEMENT ?
- Présentation simple, exacte et chaleureuse du projet.
- Catégorie & évolutions majeures les plus récentes (ex: CEX vers UEX, Layer 2 Morph, etc.).
- Verdict à chaud : PÉPITE / PROJET SOLIDE / ATTENTION DANGER ?

2. 📊 LES CHIFFRES EN DIRECT (GARDONS UN ŒIL SUR LE COUNTER)
- Présente le prix actuel (`$0.60`), le classement, la Market Cap et les variations 24h/7j.
> 🎓 Minute Pédago - Explique ici simplement une notion comme le Market Cap ou les Tokenomics.

3. 🚀 LES GROS MOTEURS DE HAUSSE & ACTUALITÉS RÉCENTES
- Utilité réelle du jeton (frais de gaz, staking, réductions) et catalyseurs les plus récents vérifiés.

4. ⚠️ LES PIÈGES ET RISQUES À NE PAS IGNORER
- Facteurs de risque réels (concurrence, déblocage de jetons, régulation).

5. ⚔️ COMPARATIF AVEC LA CONCURRENCE
- Petit comparatif rapide avec 2-3 concurrents directs actuels.

6. 🎯 MON VERDICT & MON CONSEIL DE POTE
- Note globale sur 10 et conseil prudent basé sur la réalité actuelle du marché.
"""

# ---------------------------------------------------------
# Interface Utilisateur & Contrôle des Limites
# ---------------------------------------------------------
crypto_input = st.text_input(
    "Quelle crypto veux-tu décortiquer aujourd'hui ?", 
    placeholder="Tape un ticker ou un nom (ex: BGB, Solana, ONDO, SUI, Bitcoin...)"
)

if requests_left > 0:
    st.caption(f"⚡ Crédits gratuits restants pour aujourd'hui : **{requests_left} / 2**")
else:
    st.warning("⚠️ Tu as atteint ta limite de 2 analyses quotidiennes. Reviens demain pour de nouvelles analyses !")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
submit_button = st.button("🚀 LANCER L'ANALYSE D'EXPERT", disabled=(requests_left <= 0))

# ---------------------------------------------------------
# Traitement & Génération du Rapport
# ---------------------------------------------------------
if submit_button and crypto_input:
    if requests_left <= 0:
        st.error("Limite quotidienne atteinte.")
    else:
        with st.spinner(f"Vérification des dernières données en direct pour **{crypto_input}**..."):
            cg_data, error = get_coingecko_data(crypto_input)
            
            if cg_data:
                data_context = f"""
Données de marché officielles CoinGecko vérifiées pour {cg_data['name']} ({cg_data['symbol']}) :
- Prix actuel USD: `${cg_data['current_price_usd']}`
- Rang Market Cap: #{cg_data['rank']}
- Capitalisation Boursière: `${cg_data['market_cap_usd']:,}` USD
- Volume 24h: `${cg_data['total_volume_24h']:,}` USD
- Variation 24h: {cg_data['price_change_24h_pct']}%
- Variation 7j: {cg_data['price_change_7d_pct']}%
- ATH: `${cg_data['ath_usd']}` ({cg_data['ath_date']})
- ATL: `${cg_data['atl_usd']}` ({cg_data['atl_date']})
- Circulating Supply: {cg_data['circulating_supply']}
- Total Supply: {cg_data['total_supply']}
"""
            else:
                data_context = f"Indication : CoinGecko indisponible ({error}). Effectue la vérification Web et l'analyse sur : {crypto_input}"

            prompt_final = f"{data_context}\n\nEffectue une recherche Web pour valider l'exactitude des dernières informations et rédige l'analyse complète de : {crypto_input}"

            response_text, gen_error = generate_content_with_key_failover(prompt_final, SYSTEM_INSTRUCTION)

            if response_text:
                st.session_state.daily_request_count += 1
                
                st.markdown("<hr style='border-color: #30363d; margin: 2rem 0;'>", unsafe_allow_html=True)
                st.markdown(response_text)
                
                st.markdown("---")
                st.markdown("### 📋 Copier le rapport")
                st.code(response_text, language="markdown")
            else:
                st.error(f"Désolé, l'agent IA est très sollicité en ce moment. Réessaie dans quelques minutes. Erreur : {gen_error}")
