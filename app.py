import streamlit as st
import google.generativeai as genai
import requests

# ---------------------------------------------------------
# 1. Configuration de la page Streamlit (Interface par Défaut)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cryptos Analyst IA",
    page_icon="⚡",
    layout="wide"
)

# Style sombre épuré par défaut
st.markdown("""
    <style>
    .main { background-color: #0d0e12; color: #e2e8f0; }
    h1 { color: #ffd700; text-align: center; font-weight: bold; }
    .stButton>button { 
        background-color: #ffd700; 
        color: #0d0e12; 
        font-weight: bold; 
        width: 100%; 
        border-radius: 6px; 
        height: 50px;
        font-size: 16px;
    }
    .stButton>button:hover { background-color: #ffe866; color: #0d0e12; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Cryptos Analyst IA")
st.caption("Entrez le nom d'un actif crypto pour obtenir un rapport clair, mis à jour en direct avec CoinGecko et généré par Gemini AI.")

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
col1, col2 = st.columns([3, 1])

with col1:
    crypto_input = st.text_input(
        "Actif à analyser :", 
        placeholder="ex: BGB, Solana, ONDO, SUI, Bitcoin..."
    )

with col2:
    st.write(" ")
    st.write(" ")
    submit_button = st.button("🚀 Lancer l'Analyse")

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
            st.markdown("---")
            st.markdown(response_text)
            
            st.markdown("---")
            st.subheader("📋 Copier le rapport")
            st.caption("Survolez le bloc ci-dessous et cliquez sur l'icône de copie en haut à droite :")
            st.code(response_text, language="markdown")
        else:
            st.error(f"Erreur lors de la génération : {last_error}")
