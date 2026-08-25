import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import os
import base64
import urllib.parse
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. Configuration et Style CSS (Avatar Animé & Background Z-Index)
# ---------------------------------------------------------
st.set_page_config(page_title="Cryptos Analyst IA", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
 /* Importation de la famille de polices Montserrat depuis Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap');

    /* Application universelle de Montserrat sur tous les textes de l'application */
    html, body, [class*="css"], stApp, .main, [data-testid="stAppViewContainer"], p, span, label, input, button, h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif !important;
    }

    /* Fond sombre général */
    stApp, .main, [data-testid="stAppViewContainer"] { 
        background-color: #0d0e12 !important; 
        color: #ffffff !important; 
    }
    
    .block-container { 
        max-width: 850px !important; 
        padding-top: 2rem !important; 
        margin: 0 auto !important; 
        position: relative;
        z-index: 10 !important;
    }

    /* --- BACKGROUND DYNAMIQUE EN ARRIÈRE-PLAN STRICT --- */
    .crypto-bubbles-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        z-index: 0 !important;
        pointer-events: none;
        opacity: 0.75;
    
    }

    .crypto-bubble {
        position: absolute;
        bottom: -100px;
        background: rgba(22, 27, 34, 0.6);
        border: 2px solid #ffd700;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
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
        10% { opacity: 0.5; }
        90% { opacity: 0.5; }
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

    /* --- AVATAR AVEC CERCLAGE DE ROTATION DYNAMIQUE --- */
    .avatar-wrapper { 
        display: flex; 
        justify-content: center; 
        margin-bottom: 15px; 
    }
    
    .avatar-container {
        position: relative;
        width: 130px;
        height: 130px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .avatar-img { 
        width: 115px !important; 
        height: 115px !important; 
        border-radius: 50% !important; 
        object-fit: cover;
        z-index: 2;
    }

    .avatar-ring {
        position: absolute;
        width: 130px;
        height: 130px;
        border-radius: 50%;
        border: 3px solid transparent;
        border-top: 3px solid #ffd700;
        border-right: 3px solid #ffd700;
        z-index: 1;
        transition: all 0.3s ease;
    }

    /* Animation activée pendant l'analyse */
    .avatar-ring.loading {
        animation: spinRing 1s linear infinite;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.6);
    }

    @keyframes spinRing {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    h1 { color: #ffd700 !important; text-align: center; font-weight: 800 !important; }
    .welcome-msg { text-align: center; color: #ffffff !important; font-size: 1.15rem; font-weight: 600; margin-bottom: 2rem; }
    
    .stMarkdown code { background-color: transparent !important; color: #ffd700 !important; font-weight: bold !important; font-size: 1.1em !important; }
    blockquote { border-left: 3px solid #ffd700 !important; background-color: #161b22 !important; color: #ffd700 !important; padding: 10px 15px !important; }
    
    .stButton>button { background-color: #ffd700 !important; color: #000000 !important; font-weight: bold !important; width: 100% !important; border-radius: 8px !important; border: none !important; height: 50px !important; }
    .stButton>button:hover { background-color: #e6c200 !important; color: #000000 !important; }

    /* Boutons de partage sociaux */
    .share-container {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 15px;
    }
    .share-btn {
        padding: 8px 16px;
        border-radius: 6px;
        color: #ffffff !important;
        font-weight: bold;
        text-decoration: none !important;
        font-size: 0.9em;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .share-wa { background-color: #25D366; }
    .share-tg { background-color: #0088cc; }
    .share-fb { background-color: #1877F2; }
    .share-tw { background-color: #1DA1F2; }
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
# 2. Persistance Navigateur (Limite 2/jour Inviolable)
# ---------------------------------------------------------
TODAY = str(date.today())

# Synchronisation du quota avec le LocalStorage du navigateur
js_limiter = f"""
<script>
    const today = "{TODAY}";
    const storedDate = localStorage.getItem("ca_date");
    let count = parseInt(localStorage.getItem("ca_count") || "0");

    if (storedDate !== today) {{
        localStorage.setItem("ca_date", today);
        localStorage.setItem("ca_count", "0");
        count = 0;
    }}
    
    // Transmission vers la session Streamlit
    const queryParams = new URLSearchParams(window.location.search);
    if (!queryParams.has('user_count')) {{
        queryParams.set('user_count', count);
        window.location.search = queryParams.toString();
    }}
</script>
"""
components.html(js_limiter, height=0)

user_count_param = st.query_params.get("user_count", "0")
try:
    current_user_count = int(user_count_param)
except ValueError:
    current_user_count = 0

requests_left = max(0, 2 - current_user_count)

# ---------------------------------------------------------
# 3. Affichage Avatar (Statique vs Dynamique)
# ---------------------------------------------------------
def render_avatar(is_loading=False):
    def get_image_base64(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()

    avatar_filename = next((f for f in ["avatar.jpg", "avatar.jpeg", "avatar.png"] if os.path.exists(f)), None)
    ring_class = "avatar-ring loading" if is_loading else "avatar-ring"
    
    if avatar_filename:
        st.markdown(f'''
            <div class="avatar-wrapper">
                <div class="avatar-container">
                    <div class="{ring_class}"></div>
                    <img class="avatar-img" src="data:image/jpeg;base64,{get_image_base64(avatar_filename)}">
                </div>
            </div>
        ''', unsafe_allow_html=True)

avatar_placeholder = st.empty()
with avatar_placeholder.container():
    render_avatar(is_loading=False)

st.markdown("<h1>Cryptos Analyst IA</h1>", unsafe_allow_html=True)
st.markdown("<div class='welcome-msg'>Bienvenue je suis l'agent IA de cryptos analyst je vous aide à analyser rapidement vos projets crypto</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Cache & APIs
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
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
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
# 5. Instructions Système
# ---------------------------------------------------------
# ---------------------------------------------------------
# Prompt Système Strict (Focus Actualités 48h & Exactitude)
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un analyste financier crypto intransigeant et ultra-informé. Ton ton est familier, chaleureux et enthousiaste, mais extrêmement rigoureux sur l'évaluation des faits et des risques.

CONSIGNE CRITIQUE - FRAÎCHEUR DES INFORMATIONS (DERNIÈRES 48H) :
- Les informations présentées dans TOUT le rapport, et SPÉCIFIQUEMENT dans la section "1. 📌 C'EST QUOI CE PROJET ?", doivent être rigoureusement À JOUR jusqu'aux dernières 48 heures.
- Vérifie scrupuleusement l'état actuel du projet : rebranding récents, migrations de contrat, annonces officielles majeures, faillites, piratages ou mises à jour fondamentales des 48 dernières heures.
- Si un événement majeur a eu lieu très récemment, mentionne-le d'entrée de jeu dans le verdict à chaud.

RÈGLES ABSOLUES :
1. Tu ne dois générer QUE le rapport final en Markdown.
2. NE GÉNÈRE AUCUN plan de pensée, aucune étape de recherche interne, aucun brouillon. 
3. COMMENCE DIRECTEMENT par le titre de la section 1 ("1. 📌 C'EST QUOI CE PROJET ?").
4. SECTION CHIFFRES EN DIRECT : Utilise STRICTEMENT et UNIQUEMENT les chiffres exacts de CoinGecko transmis dans le prompt.

BARÈME DE NOTATION STRICT ET OBLIGATOIRE :
Interdiction d'attribuer une note supérieure à 5/10 si l'analyse relève des risques majeurs, un manque de transparence ou une utilité faible.
- 0/10 à 3.5/10 (DANGER / TRÈS RISQUÉ)
- 4/10 à 5/10 (MOYEN / INCERTAIN)
- 5.5/10 à 7/10 (SOLIDE AVEC RÉSERVES)
- 7.5/10 à 10/10 (VALEUR SÛRE / PILIER)

Structure stricte :
1. 📌 C'EST QUOI CE PROJET ? (Présentation complète, statut exact et événements majeurs des 48 dernières heures)
2. 📊 LES CHIFFRES EN DIRECT (Chiffres précis de CoinGecko : Prix, Market Cap, Volume 24h, Variation 24h/7j, Rang)
> 🎓 Minute Pédago - Explique une notion simple.
3. 🔗 INFOS TECHNIQUES (RÉSEAUX & CONTRATS)
4. 🚀 GROS MOTEURS DE HAUSSE & ACTUALITÉS (Annonces et catalyseurs des 48h)
5. ⚠️ RISQUES À NE PAS IGNORER
6. ⚔️ COMPARATIF CONCURRENCE
7. 🎯 MON VERDICT & CONSEIL DE POTE (Note sur 10 selon le barème).
"""

# ---------------------------------------------------------
# 6. Interface Utilisateur & Exécution
# ---------------------------------------------------------
crypto_input = st.text_input("Quelle crypto veux-tu décortiquer ?", placeholder="ex: BGB, SUI...")
if requests_left > 0: st.caption(f"⚡ Crédits restants : **{requests_left} / 2**")
else: st.warning("⚠️ Tu as atteint ta limite de 2 analyses quotidiennes. Reviens demain !")

if st.button("🚀 LANCER L'ANALYSE", disabled=(requests_left <= 0)):
    # Activation du cerclage dynamique autour de l'avatar
    with avatar_placeholder.container():
        render_avatar(is_loading=True)

    cg_data, err = get_coingecko_data(crypto_input)
    if err: 
        st.error(err)
        with avatar_placeholder.container(): render_avatar(is_loading=False)
    elif not cg_data: 
        st.warning("😔 Crypto introuvable sur CoinGecko.")
        with avatar_placeholder.container(): render_avatar(is_loading=False)
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
prompt = f"""
{coingecko_context}

DATE DU JOUR : {TODAY}

Consigne spéciale : Rédige l'analyse de ce projet en t'assurant que la présentation ("1. 📌 C'EST QUOI CE PROJET ?") et les actualités intègrent les derniers développements survenus jusqu'aux dernières 48 heures.
"""
        
with st.spinner("Récupération des données et rédaction du rapport..."):
            res, gen_err = generate_content_with_key_failover(prompt, SYSTEM_INSTRUCTION)
            
            # Arrêt de la rotation autour de l'avatar
            with avatar_placeholder.container():
                render_avatar(is_loading=False)

            if res:
                # Incrémentation et sauvegarde locale de la limite
                new_count = current_user_count + 1
                components.html(f"<script>localStorage.setItem('ca_count', '{new_count}');</script>", height=0)
                st.query_params["user_count"] = str(new_count)
                
                st.markdown(res)
                st.markdown("---")
                
                # --- BOUTONS DE PARTAGE SOCIAUX ---
                st.markdown("### 📢 Partager ce rapport d'analyse")
                
                share_text = f"🤖 Découvre l'analyse complète de {cg_data['name']} ({cg_data['symbol']}) générée par Cryptos Analyst IA !"
                encoded_text = urllib.parse.quote(share_text)
                encoded_url = urllib.parse.quote("https://meagotbnwddhsaa6d3pfln.streamlit.app")
                
                wa_url = f"https://api.whatsapp.com/send?text={encoded_text}%20{encoded_url}"
                tg_url = f"https://t.me/share/url?url={encoded_url}&text={encoded_text}"
                fb_url = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"
                tw_url = f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}"

                st.markdown(f"""
                <div class="share-container">
                    <a class="share-btn share-wa" href="{wa_url}" target="_blank">📱 WhatsApp</a>
                    <a class="share-btn share-tg" href="{tg_url}" target="_blank">✈️ Telegram</a>
                    <a class="share-btn share-fb" href="{fb_url}" target="_blank">📘 Facebook</a>
                    <a class="share-btn share-tw" href="{tw_url}" target="_blank">🐦 X (Twitter)</a>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### 📋 Copier le rapport texte")
                st.code(res, language="markdown")
            else: 
                st.error(f"Erreur de génération : {gen_err}")
