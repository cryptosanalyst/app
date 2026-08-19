import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import os
import base64
import streamlit.components.v1 as components
import re

# ---------------------------------------------------------
# 1. Configuration & Style (CSS)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cryptos Analyst IA",
    page_icon="🤖",
    layout="wide"
)

# CSS : Centrage absolu, responsive, thèmes et contrastes
st.markdown("""
    <style>
    /* Fond noir pur et visibilité générale */
    stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #0d0e12 !important;
        color: #ffffff !important;
    }
    
    /* Conteneur principal centré sans débordement */
    .block-container {
        max-width: 850px !important;
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        margin: 0 auto !important;
    }

    /* Avatar centré et rond */
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

    /* Titre responsive grand format (jusqu'à 1000px max) */
    h1 { 
        color: #ffd700 !important; 
        text-align: center; 
        font-weight: 800 !important;
        font-size: min(1000px, 10vw) !important;
        line-height: 1.1 !important;
        margin-bottom: 0.5rem !important;
    }

    /* Message d'accueil */
    .welcome-msg {
        text-align: center;
        color: #ffffff !important;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 2rem;
        line-height: 1.5;
    }

    /* Champ de saisie */
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
        font-size: 16px !important;
    }

    .stTextInput input::placeholder {
        color: #cbd5e1 !important;
        opacity: 0.8;
    }

    /* Bouton Jaune / Texte Noir */
    .stButton>button { 
        background-color: #ffd700 !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        width: 100% !important; 
        border-radius: 8px !important; 
        height: 50px !important;
        font-size: 16px !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover { 
        background-color: #e6c200 !important; 
        color: #000000 !important;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.5) !important;
    }

    /* Badges de Prix & Code */
    code {
        background-color: transparent !important;
        color: #ffd700 !important;
        font-weight: bold !important;
        font-size: 1.05em !important;
    }

    /* Citations / Notes Pédagogiques en Jaune */
    blockquote {
        border-left: 3px solid #ffd700 !important;
        background-color: #161b22 !important;
        color: #ffd700 !important;
        padding: 10px 15px !important;
        margin: 10px 0 !important;
        border-radius: 0 8px 8px 0 !important;
    }

    blockquote p, blockquote em, blockquote i, blockquote span {
        color: #ffd700 !important;
        font-weight: 500 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. En-tête : Avatar & Titres
# ---------------------------------------------------------
def get_image_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

avatar_filename = next((f for f in ["avatar.jpg", "avatar.jpeg", "avatar.png"] if os.path.exists(f)), None)
if avatar_filename:
    st.markdown(f'<div class="avatar-wrapper"><img src="data:image/jpeg;base64,{get_image_base64(avatar_filename)}" alt="Avatar"></div>', unsafe_allow_html=True)

st.markdown("<h1>Cryptos Analyst IA</h1>", unsafe_allow_html=True)
st.markdown("<div class='welcome-msg'>Bienvenue je suis l'agent IA de cryptos analyst je vous aide à analyser rapidement vos projets crypto</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Limite de 2 requêtes / jour par session + Sync LocalStorage
# ---------------------------------------------------------
TODAY = str(date.today())

if "daily_request_count" not in st.session_state:
    st.session_state.daily_request_count = 0

requests_left = max(0, 2 - st.session_state.daily_request_count)

components.html(f"""
<script>
    const today = "{TODAY}";
    let storedDate = localStorage.getItem("crypto_analyst_date");
    if (storedDate !== today) {{
        localStorage.setItem("crypto_analyst_date", today);
        localStorage.setItem("crypto_analyst_count", "0");
    }}
</script>
""", height=0)

# ---------------------------------------------------------
# 4. Données CoinGecko (Cache de 12 heures = 43200s)
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
            "platforms": platforms
        }
        return result, None
    except Exception as e:
        return None, f"Erreur CoinGecko : {str(e)}"

# ---------------------------------------------------------
# 5. API Gemini : Rotation Clés, Détection Modèles & Anti-Brouillon
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

def generate_clean_report(prompt_text, system_instruction):
    gemini_keys = get_gemini_api_keys()
    if not gemini_keys:
        return None, "Aucune clé API Gemini n'a été configurée."

    last_err = "Erreur de connexion."

    for api_key in gemini_keys:
        try:
            genai.configure(api_key=api_key)
            
            # Détection dynamique des modèles valides sur la clé
            valid_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        valid_models.append(m.name)
            except Exception:
                pass
            
            candidate_models = valid_models if valid_models else ["models/gemini-2.5-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash"]

            for model_name in candidate_models:
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=system_instruction
                    )
                    response = model.generate_content(prompt_text)
                    if response and response.text:
                        raw_text = response.text.strip()
                        # Filtre strict : supprime physiquement tout ce qui précède la section 1
                        start_match = re.search(r"1\.\s?📌", raw_text)
                        if start_match:
                            raw_text = raw_text[start_match.start():]
                        return raw_text, None
                except Exception as m_err:
                    last_err = str(m_err)
                    continue
        except Exception as k_err:
            last_err = str(k_err)
            continue

    return None, last_err

# ---------------------------------------------------------
# 6. Prompt Système (Ton, Exactitude, Barème & Format)
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un analyste financier senior passionné par la crypto. Tu exprimes tes analyses avec un ton familier, chaleureux, accessible et très enthousiaste (tutoiement naturel).

CONSIGNE STRICTE - SANS BROUILLON :
Ne génère AUCUN plan de réflexion, AUCUN brouillon, AUCUNE phrase d'introduction.
COMMENCE DIRECTEMENT PAR LE TITRE : "1. 📌 C'EST QUOI CE PROJET CONCRÈTEMENT ?".

BARÈME DE NOTATION OBLIGATOIRE (POUR PROTÉGER LES DÉBUTANTS) :
- 0/10 à 3.5/10 (RISQUE TRÈS ÉLEVÉ / DANGER) : Projet spéculatif, memecoin sans utilité, projet suspect. Si un projet est jugé très risqué, sa note NE PEUT PAS dépasser 3.5/10.
- 4/10 à 5.5/10 (RISQUE MOYEN À ÉLEVÉ) : Projet moyen, forte concurrence, utilité incertaine.
- 6/10 à 7.5/10 (SOLIDE) : Bon projet, utilité réelle, adoption en hausse.
- 8/10 à 10/10 (PILIER SÉCURISÉ) : Bitcoin, Ethereum, etc.

Directives de formatage :
- Entoure les prix de backticks (ex: `$0.60`).
- Les explications "Minute Pédago" doivent TOUJOURS être sous forme de citation avec `>` pour s'afficher en jaune.

Structure du rapport :
1. 📌 C'EST QUOI CE PROJET CONCRÈTEMENT ? (Verdict à chaud)
2. 📊 LES CHIFFRES EN DIRECT (Prix, Market Cap, Rang)
> 🎓 Minute Pédago - Explique simplement une notion (ex: Market Cap).
3. 🔗 INFOS TECHNIQUES (RÉSEAUX & CONTRATS)
- Liste clairement les réseaux et adresses de contrat transmises.
4. 🚀 GROS MOTEURS DE HAUSSE & ACTUALITÉS
5. ⚠️ RISQUES À NE PAS IGNORER
6. ⚔️ COMPARATIF AVEC LA CONCURRENCE
7. 🎯 MON VERDICT & MON CONSEIL DE POTE (Note sur 10 stricte).
"""

# ---------------------------------------------------------
# 7. Interface Utilisateur & Traitement
# ---------------------------------------------------------
crypto_input = st.text_input(
    "Quelle crypto veux-tu décortiquer aujourd'hui ?", 
    placeholder="Tape un ticker ou un nom (ex: BGB, Solana, ONDO, SUI, Bitcoin...)"
)

if requests_left > 0:
    st.caption(f"⚡ Crédits gratuits restants pour aujourd'hui : **{requests_left} / 2**")
else:
    st.warning("⚠️ Tu as atteint ta limite de 2 analyses quotidiennes. Reviens demain !")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
submit_button = st.button("🚀 LANCER L'ANALYSE D'EXPERT", disabled=(requests_left <= 0))

if submit_button and crypto_input:
    if requests_left <= 0:
        st.error("Limite quotidienne atteinte.")
    else:
        with st.spinner(f"Vérification de l'existence de **{crypto_input}** sur CoinGecko..."):
            cg_data, error = get_coingecko_data(crypto_input)
            
            # Étape : si la crypto n'existe pas, on bloque tout ici sans consommer de crédit
            if not cg_data:
                st.warning(
                    f"😔 **Désolé !** Je n'ai trouvé aucune crypto correspondant à **« {crypto_input} »** sur CoinGecko.\n\n"
                    "Vérifie l'orthographe du nom ou du ticker (ex: *BTC, BGB, SUI, Solana*) puis réessaye."
                )
            else:
                platforms_info = "\n".join([f"- {net.upper()}: `{addr}`" for net, addr in cg_data['platforms'].items() if addr]) if cg_data['platforms'] else "Réseau natif ou données de contrat non applicables."
                
                data_context = f"""
Données CoinGecko vérifiées pour {cg_data['name']} ({cg_data['symbol']}) :
- Prix actuel: `${cg_data['current_price_usd']}`
- Capitalisation Boursière: `${cg_data['market_cap_usd']:,}` USD
- Rang Market Cap: #{cg_data['rank']}
- Volume 24h: `${cg_data['total_volume_24h']:,}` USD
- Variations: 24h = {cg_data['price_change_24h_pct']}%, 7j = {cg_data['price_change_7d_pct']}%
- ATH: `${cg_data['ath_usd']}`, ATL: `${cg_data['atl_usd']}`
- RÉSEAUX & ADRESSES CONTRAT:
{platforms_info}
"""
                prompt_final = f"{data_context}\n\nEffectue la vérification des dernières actualités et rédige l'analyse complète de : {cg_data['name']} ({cg_data['symbol']})"

                with st.spinner(f"Rédaction du rapport d'expert pour **{cg_data['name']}**..."):
                    response_text, gen_error = generate_clean_report(prompt_final, SYSTEM_INSTRUCTION)

                if response_text:
                    st.session_state.daily_request_count += 1
                    components.html(f"<script>localStorage.setItem('crypto_analyst_count', '{st.session_state.daily_request_count}');</script>", height=0)
                    
                    st.markdown("<hr style='border-color: #30363d; margin: 2rem 0;'>", unsafe_allow_html=True)
                    st.markdown(response_text)
                    
                    st.markdown("---")
                    st.markdown("### 📋 Copier le rapport")
                    st.code(response_text, language="markdown")
                else:
                    st.error(f"Désolé, l'agent IA rencontre un souci : {gen_error}")
