import streamlit as st
import google.generativeai as genai
import requests

# ---------------------------------------------------------
# 1. Configuration de la page Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cryptos Analyst IA",
    page_icon="⚡",
    layout="wide"
)

# Correction CSS pour les prix et les notes pédagogiques
st.markdown("""
    <style>
    /* Forcer le fond sombre général */
    stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #0d0e12 !important;
        color: #ffffff !important;
    }
    
    .block-container {
        max-width: 850px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
        margin: 0 auto !important;
    }

    /* Titres */
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

    /* FIX 1 : Affichage des prix en badge jaune texte noir */
    code {
        background-color: #ffd700 !important;
        color: #0d0e12 !important;
        font-weight: bold !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-size: 0.95em !important;
    }

    /* FIX 2 : Notes pédagogiques (Citations / Blockquotes) en Jaune */
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

    /* Champ de saisie & Bouton */
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

# En-tête
st.markdown("<h1>⚡ Cryptos Analyst IA</h1>", unsafe_allow_html=True)
st.markdown("<div class='welcome-msg'>Bienvenue je suis l'agent IA de cryptos analyst je vous aide à analyser rapidement vos projets crypto</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Récupération des Données CoinGecko
# ---------------------------------------------------------
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
# 3. Instruction Système Gemini
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un analyste financier senior passionné par la crypto. Tu exprimes tes analyses avec un **ton familier, chaleureux, accessible et très enthousiaste** (tutoiement naturel).

Directives de formatage impératives :
- Entoure TOUJOURS les prix et montants importants de backticks pour former un badge distinct (ex: `$0.60`).
- Place TOUTES les explications pédagogiques / "Minute Pédago" sous forme de citation avec un chevron `>` pour qu'elles s'affichent en jaune.

Structure de ton rapport :

1. 📌 C'EST QUOI CE PROJET CONCRÈTEMENT ?
- Présentation simple et chaleureuse du projet.
- Catégorie & évolutions récentes (ex: CEX vers UEX, intégration Layer 2 Morph, etc.).
- Verdict à chaud : PÉPITE / PROJET SOLIDE / ATTENTION DANGER ?

2. 📊 LES CHIFFRES EN DIRECT (GARDONS UN ŒIL SUR LE COUNTER)
- Présente le prix actuel (`$0.60`), le classement, la Market Cap et les variations 24h/7j.
> 🎓 Minute Pédago - Explique ici simplement une notion comme le Market Cap ou les Tokenomics.

3. 🚀 LES GROS MOTEURS DE HAUSSE
- Utilité réelle du jeton (gaz, staking, réductions) et catalyseurs récents.

4. ⚠️ LES PIÈGES ET RISQUES À NE PAS IGNORER
- Facteurs de risque (concurrence, déblocage de jetons, régulation).

5. ⚔️ COMPARATIF AVEC LA CONCURRENCE
- Petit comparatif rapide avec 2-3 concurrents.

6. 🎯 MON VERDICT & MON CONSEIL DE POTE
- Note globale sur 10 et conseil prudent.
"""

# ---------------------------------------------------------
# 4. Connexion API Gemini
# ---------------------------------------------------------
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_api_key)
except Exception:
    st.error("⚠️ Clé API Gemini manquante dans secrets.toml.")
    st.stop()

# ---------------------------------------------------------
# 5. Interface Utilisateur
# ---------------------------------------------------------
crypto_input = st.text_input(
    "Quelle crypto veux-tu décortiquer aujourd'hui ?", 
    placeholder="Tape un ticker ou un nom (ex: BGB, Solana, ONDO, SUI, Bitcoin...)"
)

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
submit_button = st.button("🚀 LANCER L'ANALYSE D'EXPERT")

# ---------------------------------------------------------
# 6. Traitement & Génération
# ---------------------------------------------------------
if submit_button and crypto_input:
    with st.spinner(f"Récupération des données en direct pour **{crypto_input}**..."):
        cg_data, error = get_coingecko_data(crypto_input)
        
        if cg_data:
            data_context = f"""
Données de marché officielles CoinGecko pour {cg_data['name']} ({cg_data['symbol']}) :
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
            data_context = f"Indication : CoinGecko indisponible ({error}). Effectue l'analyse sur : {crypto_input}"

        prompt_final = f"{data_context}\n\nEffectue l'analyse complète de la crypto : {crypto_input}"

        candidate_models = ["gemini-3.6-flash", "gemini-1.5-flash-latest"]
        response_text = None
        last_error = None

        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_INSTRUCTION
                )
                response = model.generate_content(prompt_final)
                response_text = response.text
                break
            except Exception as e:
                last_error = e
                continue

        if response_text:
            st.markdown("<hr style='border-color: #30363d; margin: 2rem 0;'>", unsafe_allow_html=True)
            st.markdown(response_text)
            
            st.markdown("---")
            st.markdown("### 📋 Copier le rapport")
            st.code(response_text, language="markdown")
        else:
            st.error(f"Erreur lors de la génération : {last_error}")
