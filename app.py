import streamlit as st
import google.generativeai as genai
import requests

# ---------------------------------------------------------
# 1. Configuration & Design Personnalisé
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cryptos Analyst IA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injection CSS (Lisibilité maximale sur fond noir)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&display=swap');

    /* Fond noir pur et police Montserrat */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Montserrat', sans-serif !important;
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    .stApp {
        background-color: #000000 !important;
    }

    /* Titre Principal à 1000px max (Responsive pour s'adapter à la largeur) */
    h1 { 
        color: rgb(3, 239, 252) !important; 
        text-align: center; 
        font-weight: 900 !important; 
        text-transform: uppercase;
        font-size: min(1000px, 12vw) !important;
        line-height: 1 !important;
        letter-spacing: 1px;
        margin-bottom: 0.5rem !important;
    }

    /* Tous les sous-titres en couleur Cyan Néon */
    h2, h3, h4, h5, h6 {
        color: rgb(3, 239, 252) !important;
        font-weight: 700 !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.6rem !important;
    }

    /* Visibilité totale : Tout le texte explicatif, puces, divs et labels en BLANC PUR */
    p, li, span, div, label, caption, .stCaption {
        color: #FFFFFF !important;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Étiquette du champ de texte en blanc */
    .stTextInput label {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Champ de saisie : fond sombre, texte BLANC et bordure Cyan */
    .stTextInput input {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid rgb(3, 239, 252) !important;
        border-radius: 8px !important;
        padding: 12px 15px !important;
        font-size: 16px !important;
    }

    /* Texte d'exemple (placeholder) en jaune clair très lisible */
    .stTextInput input::placeholder {
        color: #FFE866 !important;
        opacity: 0.8;
    }

    /* Bouton Jaune avec Texte STRICTEMENT NOIR */
    .stButton>button { 
        background-color: #FFD700 !important; 
        color: #000000 !important; 
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 900 !important; 
        width: 100%; 
        border-radius: 8px !important; 
        height: 50px;
        font-size: 16px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        cursor: pointer;
    }

    .stButton>button p, .stButton>button div, .stButton>button span {
        color: #000000 !important;
        font-weight: 900 !important;
    }

    .stButton>button:hover { 
        background-color: #FFE866 !important; 
        color: #000000 !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.8) !important;
    }

    .stButton>button:hover p, .stButton>button:hover div, .stButton>button:hover span {
        color: #000000 !important;
    }

    /* Carte de résultat lisible */
    .crypto-card {
        background: #111111;
        border: 1px solid rgba(3, 239, 252, 0.4);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        color: #FFFFFF !important;
    }

    /* Bloc de code pour la copie avec contour Cyan */
    .stCodeBlock {
        border: 1px solid rgba(3, 239, 252, 0.3) !important;
        border-radius: 8px !important;
        background-color: #080808 !important;
    }

    /* Masquage des menus système Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# En-tête
st.markdown("<h1>Cryptos Analyst IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FFFFFF !important; margin-bottom: 2rem;'>Rapports d'analyse fondamentale en direct alimentés par CoinGecko & Gemini AI.</p>", unsafe_allow_html=True)

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
Tu es un expert senior en analyse financière et vulgarisation de projets cryptos. Ton objectif est de rendre chaque analyse **facilement compréhensible par un débutant complet**, tout en fournissant une analyse fondamentale ultra-précise.

Règles importantes :
- Utilise en priorité les métriques chiffrées exactes transmises depuis l'API CoinGecko.
- Mentionne les évolutions stratégiques récentes du projet (ex: pour BGB/Bitget, mentionne l'évolution vers un Universal Exchange UEX, l'intégration de la Layer 2 Morph où BGB sert de jeton de gaz, etc.).
- Utilise des mots simples. Explique tout terme technique (Tokenomics, Layer 2, Staking, Burn, Market Cap, UEX) avec une analogie simple de la vie courante.
- Ton pédagogique, bienveillant et structuré avec des puces.

Structure de l'analyse :

1. 📌 C'EST QUOI CE PROJET ? (RÉSUMÉ SIMPLE & ÉVOLUTION RÉCENTE)
- Description simple comme pour un ami novice.
- Catégorie & évolutions récentes importantes (ex: CEX vers UEX, intégration Layer 2, etc.).
- Verdict rapide : Intéressant, Moyen ou Risqué.

2. 📊 CHIFFRES CLÉS COINGECKO (DONNÉES EN DIRECT)
- Présente le prix actuel, le classement, le Market Cap et les variations récentes.
- Mentionne les ATH/ATL historiques et la situation de l'offre (Circulating vs Max Supply, burn).

3. 🚀 CATALYSEURS & DERNIÈRES ACTUALITÉS (MOTEURS DE HAUSSE)
- Pourquoi le projet peut-il prendre de la valeur ?
- Les cas d'utilisation concrets du jeton (frais de gaz, réductions, staking, etc.).

4. ⚠️ RISQUES ET FREINS À SURVEILLER
- Concurrence, régulation, calendrier de déblocage (vesting), ou dépendance à une entreprise centralisée.

5. ⚔️ COMPARATIF SIMPLIFIÉ
- Comparaison rapide avec 2 ou 3 concurrents directs.

6. 🎯 VERDICT ET RECOMMANDATION
- Note globale sur 10.
- Conseil prudent pour un débutant et métriques clés à surveiller.
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
col1, col2 = st.columns([3, 1], gap="medium")

with col1:
    crypto_input = st.text_input(
        "Actif crypto à analyser :", 
        placeholder="Saisissez un nom ou ticker (ex: BGB, Solana, ONDO, SUI, Bitcoin...)"
    )

with col2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    submit_button = st.button("🚀 LANCER L'ANALYSE")

# ---------------------------------------------------------
# 6. Traitement & Génération du Rapport
# ---------------------------------------------------------
if submit_button and crypto_input:
    with st.spinner(f"Récupération des métriques et analyse en cours pour **{crypto_input}**..."):
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

        prompt_final = f"{data_context}\n\nEffectue l'analyse complète et pédagogique de l'actif crypto : {crypto_input}"

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
            st.markdown("<hr style='border-color: rgba(3, 239, 252, 0.3); margin: 2rem 0;'>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='crypto-card'>{response_text}</div>", unsafe_allow_html=True)
            
            st.markdown("### 📋 Copier le rapport")
            st.markdown("<p style='color: #FFFFFF !important;'>Survolez le bloc ci-dessous et cliquez sur l'icône de copie en haut à droite :</p>", unsafe_allow_html=True)
            st.code(response_text, language="markdown")
        else:
            st.error(f"Erreur lors de la génération : {last_error}")
