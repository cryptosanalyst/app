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

# Style CSS pour une lisibilité maximale sur l'interface par défaut
st.markdown("""
    <style>
    .main { background-color: #0d0e12; color: #f0f6fc; }
    
    /* Conteneur principal centré */
    .block-container {
        max-width: 850px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
        margin: 0 auto !important;
    }

    h1 { 
        color: #ffd700; 
        text-align: center; 
        font-weight: bold;
        margin-bottom: 0.5rem !important;
    }

    .welcome-msg {
        text-align: center;
        color: #e2e8f0;
        font-size: 1.15rem;
        font-weight: 500;
        margin-bottom: 2rem;
        line-height: 1.5;
    }

    /* Champ de saisie */
    .stTextInput > label {
        display: block;
        text-align: center;
        font-weight: bold;
        color: #ffd700;
        font-size: 1.05rem;
    }

    .stTextInput > div > div > input {
        text-align: center;
        background-color: #161b22;
        color: #ffffff;
        border: 1px solid #30363d;
        border-radius: 8px;
        font-size: 16px;
    }

    /* Bouton d'action */
    .stButton>button { 
        background-color: #ffd700; 
        color: #0d0e12; 
        font-weight: bold; 
        width: 100%; 
        border-radius: 8px; 
        height: 50px;
        font-size: 16px;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton>button:hover { 
        background-color: #ffe866; 
        color: #0d0e12;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# En-tête & Message d'accueil
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
# 3. Instruction Système Gemini (Ton Familier, Chaleureux & Expert)
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un analyste financier senior passionné par la crypto, mais tu exprimes tes analyses avec un **ton familier, chaleureux, accessible et très enthousiaste** (tutoiement naturel, comme un pote expert qui explique un projet autour d'un café). 

Ton style est **ultra-pédagogique et informatif** : tu dois expliquer le fond du sujet avec la précision d'un analyste institutionnel, mais en utilisant des mots simples, des analogies de la vie courante et une touche d'humour bienveillante.

Règles impératives :
- Utilise le tutoiement ("tu", "ton", "tes").
- Intègre impérativement les métriques chiffrées exactes transmises par CoinGecko.
- Sois à jour sur l'écosystème récent (ex: si tu analyses BGB/Bitget, parle de l'évolution vers un Universal Exchange UEX, l'intégration du Layer 2 Morph où BGB sert de jeton de gaz, etc.).
- Explique immédiatement chaque notion complexe (Market Cap, Tokenomics, Layer 2, Staking, Burn, Vesting).

Structure de ton rapport :

1. 📌 C'EST QUOI CE PROJET CONCRÈTEMENT ?
- Présentation simple, directe et chaleureuse du projet.
- Catégorie & évolutions récentes majeures (ex: CEX vers UEX, intégration Layer 2, etc.).
- Ton petit verdict à chaud : PÉPITE / PROJET SOLIDE / ATTENTION DANGER ?

2. 📊 LES CHIFFRES EN DIRECT (GARDONS UN ŒIL SUR LE COUNTER)
- Présente le prix, le classement, la Market Cap et les mouvements récents (24h/7j).
- Un mot sur l'ATH/ATL et l'état des stocks de jetons (Supply circulante vs Max Supply, burn).

3. 🚀 LES GROS MOTEURS DE HAUSSE (POURQUOI ÇA PEUT IMPLOSER EN HAUSSE ?)
- À quoi sert vraiment le jeton dans la vie de tous les jours (frais de gaz, réductions, staking) ?
- Les vrais catalyseurs et actualités du moment.

4. ⚠️ LES PIÈGES ET RISQUES À NE PAS IGNORER
- Ce qui pourrait mal tourner (concurrence, régulation, jetons bloqués/vesting, centralisation).

5. ⚔️ COMPARATIF AVEC LA CONCURRENCE
- Petit comparatif rapide et pertinent avec 2-3 concurrents du secteur.

6. 🎯 MON VERDICT & MON CONSEIL DE POTE
- Ta note globale sur 10.
- Ton conseil tactique et prudent pour un débutant, avec 2-3 indicateurs clés à surveiller régulièrement.
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
# 6. Traitement & Génération du Rapport
# ---------------------------------------------------------
if submit_button and crypto_input:
    with st.spinner(f"Attends deux secondes, je récupère les données fraîches de **{crypto_input}** et je te prépare ça..."):
        cg_data, error = get_coingecko_data(crypto_input)
        
        if cg_data:
            data_context = f"""
Données de marché officielles en direct de CoinGecko pour {cg_data['name']} ({cg_data['symbol']}) :
- Prix actuel USD: ${cg_data['current_price_usd']}
- Rang Market Cap: #{cg_data['rank']}
- Capitalisation Boursière: ${cg_data['market_cap_usd']:,} USD
- Volume 24h: ${cg_data['total_volume_24h']:,} USD
- Variation 24h: {cg_data['price_change_24h_pct']}%
- Variation 7 jours: {cg_data['price_change_7d_pct']}%
- Plus haut historique (ATH): ${cg_data['ath_usd']} (Date: {cg_data['ath_date']})
- Plus bas historique (ATL): ${cg_data['atl_usd']} (Date: {cg_data['atl_date']})
- Offre en circulation: {cg_data['circulating_supply']}
- Total Supply: {cg_data['total_supply']}
- Max Supply: {cg_data['max_supply']}
"""
        else:
            data_context = f"Indication : CoinGecko indisponible ({error}). Effectue l'analyse avec tes données sur : {crypto_input}"

        prompt_final = f"{data_context}\n\nEffectue l'analyse complète, chaleureuse et pédagogique de la crypto : {crypto_input}"

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
            
            # Affichage du rapport
            st.markdown(response_text)
            
            st.markdown("---")
            st.markdown("### 📋 Copier le rapport")
            st.caption("Passe ta souris sur le bloc ci-dessous et clique sur le bouton de copie en haut à droite :")
            st.code(response_text, language="markdown")
        else:
            st.error(f"Oups ! Une erreur est survenue lors de la génération : {last_error}")
