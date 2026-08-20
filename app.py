import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import os
import base64
import urllib.parse
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. Configuration de la page
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cryptos Analyst IA",
    page_icon="🤖",
    layout="wide"
)

BASE_URL = st.secrets.get("APP_URL", "https://meagotbnwddhsaa6d3pfln.streamlit.app")

# ---------------------------------------------------------
# 2. Gestion des Pseudos & Parrainage (URL & Session)
# ---------------------------------------------------------
query_params = st.query_params
referrer = query_params.get("ref", None)

if "user_pseudo" not in st.session_state:
    st.session_state.user_pseudo = query_params.get("user", "")

if "referral_count" not in st.session_state:
    try:
        st.session_state.referral_count = int(query_params.get("ref_cnt", "0"))
    except ValueError:
        st.session_state.referral_count = 0

def save_pseudo():
    if st.session_state.pseudo_input.strip():
        pseudo_clean = st.session_state.pseudo_input.strip().lower().replace(" ", "_")
        st.session_state.user_pseudo = pseudo_clean
        st.query_params["user"] = pseudo_clean

# ---------------------------------------------------------
# 3. CSS Personnalisé - Bordure Tournante & UI Modernisée
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #0b0e14 !important;
        color: #e6edf3 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Arrière-plan logos crypto flottants */
    .crypto-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
        opacity: 0.04;
    }

    .crypto-icon {
        position: absolute;
        animation: float 12s infinite ease-in-out;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(8deg); }
    }

    .icon-btc { top: 10%; left: 8%; width: 90px; animation-delay: 0s; }
    .icon-eth { top: 65%; left: 12%; width: 80px; animation-delay: 2s; }
    .icon-sol { top: 15%; right: 10%; width: 85px; animation-delay: 4s; }
    .icon-bnb { top: 70%; right: 8%; width: 90px; animation-delay: 1s; }
    .icon-bgb { top: 42%; left: 4%; width: 75px; animation-delay: 3s; }
    .icon-usdt { top: 45%; right: 5%; width: 75px; animation-delay: 5s; }

    .block-container {
        max-width: 800px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        margin: 0 auto !important;
        position: relative;
        z-index: 1;
    }

    /* --- CONTENEUR AVATAR & BORDURE DOURNANTE --- */
    .avatar-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-bottom: 20px;
    }

    .avatar-frame {
        position: relative;
        width: 126px;
        height: 126px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: #30363d;
        padding: 3px;
    }

    .avatar-img {
        width: 120px !important;
        height: 120px !important;
        border-radius: 50% !important;
        object-fit: cover !important;
        z-index: 2;
        position: relative;
    }

    /* L'AVATAR NE TOURNE PAS - C'est cet anneau lumineux qui tourne autour */
    .avatar-frame.spinning::before {
        content: '';
        position: absolute;
        top: -4px;
        left: -4px;
        right: -4px;
        bottom: -4px;
        border-radius: 50%;
        background: conic-gradient(from 0deg, transparent 20%, #ffd700 80%, #ffffff 100%);
        animation: spin-ring 1.2s linear infinite;
        z-index: 1;
    }

    .avatar-frame.spinning::after {
        content: '';
        position: absolute;
        inset: 3px;
        background: #0b0e14;
        border-radius: 50%;
        z-index: 1;
    }

    @keyframes spin-ring {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    h1 {
        color: #ffffff !important;
        text-align: center;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        margin-bottom: 0.25rem !important;
    }

    .welcome-msg {
        text-align: center;
        color: #8b949e !important;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    /* Champ de saisie */
    .stTextInput > label {
        display: block;
        text-align: center;
        font-weight: 700 !important;
        color: #ffd700 !important;
        font-size: 1.05rem !important;
        margin-bottom: 8px !important;
    }

    .stTextInput input {
        text-align: center !important;
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 14px !important;
        font-size: 1rem !important;
    }

    .stTextInput input:focus {
        border-color: #ffd700 !important;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.25) !important;
    }

    /* Bouton d'analyse dynamique */
    .stButton > button {
        background: linear-gradient(90deg, #ffd700 0%, #ffae00 50%, #ffd700 100%) !important;
        background-size: 200% auto !important;
        color: #0d0e12 !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        width: 100% !important;
        border-radius: 12px !important;
        height: 52px !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.25) !important;
        animation: shimmer 3s infinite linear;
        transition: transform 0.15s ease !important;
    }

    @keyframes shimmer {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }

    .stButton > button:hover {
        transform: translateY(-2px);
    }

    .stButton > button:disabled {
        background: #21262d !important;
        color: #484f58 !important;
        animation: none !important;
    }

    /* Boutons de Partage Social */
    .share-btn {
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.88rem;
        font-weight: 600;
        text-decoration: none !important;
        color: #ffffff !important;
        transition: transform 0.2s ease, opacity 0.2s ease;
    }

    .share-btn:hover { transform: translateY(-2px); opacity: 0.9; }
    .share-wa { background-color: #25D366; }
    .share-x  { background-color: #1DA1F2; }
    .share-tg { background-color: #0088cc; }
    .share-in { background-color: #0A66C2; }
    .share-fb { background-color: #1877F2; }

    blockquote {
        border-left: 4px solid #ffd700 !important;
        background-color: #161b22 !important;
        color: #ffd700 !important;
        padding: 12px 18px !important;
        margin: 15px 0 !important;
        border-radius: 0 10px 10px 0 !important;
    }

    blockquote p, blockquote em, blockquote i, blockquote span {
        color: #ffd700 !important;
    }

    code {
        background-color: rgba(255, 215, 0, 0.15) !important;
        color: #ffd700 !important;
        font-weight: 600 !important;
        padding: 3px 8px !important;
        border-radius: 6px !important;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    </style>

    <div class="crypto-bg">
        <img class="crypto-icon icon-btc" src="https://assets.coingecko.com/coins/images/1/large/bitcoin.png">
        <img class="crypto-icon icon-eth" src="https://assets.coingecko.com/coins/images/279/large/ethereum.png">
        <img class="crypto-icon icon-sol" src="https://assets.coingecko.com/coins/images/4128/large/solana.png">
        <img class="crypto-icon icon-bnb" src="https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png">
        <img class="crypto-icon icon-bgb" src="https://assets.coingecko.com/coins/images/11610/large/BGB.png">
        <img class="crypto-icon icon-usdt" src="https://assets.coingecko.com/coins/images/325/large/Tether.png">
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Affichage de l'Avatar Fixe avec Anneau Lumineux Tournant
# ---------------------------------------------------------
def get_image_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

avatar_filename = None
for filename in ["avatar.jpg", "avatar.jpeg", "avatar.png"]:
    if os.path.exists(filename):
        avatar_filename = filename
        break

avatar_container = st.empty()

def render_avatar(is_analyzing=False):
    if avatar_filename:
        img_b64 = get_image_base64(avatar_filename)
        spin_class = "spinning" if is_analyzing else ""
        avatar_container.markdown(f"""
            <div class="avatar-wrapper">
                <div class="avatar-frame {spin_class}">
                    <img class="avatar-img" src="data:image/jpeg;base64,{img_b64}" alt="Avatar">
                </div>
            </div>
        """, unsafe_allow_html=True)

render_avatar(is_analyzing=False)

st.markdown("<h1>Cryptos Analyst IA</h1>", unsafe_allow_html=True)
st.markdown("<div class='welcome-msg'>Bienvenue, je suis l'agent IA de Cryptos Analyst. Je t'aide à analyser rapidement tes projets crypto.</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. Module Pseudo & Dashboard Filleuls Actifs
# ---------------------------------------------------------
if not st.session_state.user_pseudo:
    st.markdown("""
        <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 18px; margin-bottom: 20px; text-align: center;">
            <p style="color: #ffd700; font-weight: 700; margin: 0 0 6px 0;">👤 Entre ton pseudo pour débloquer ton lien d'invitation</p>
            <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Invite tes amis et suis tes parrainages en direct.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        st.text_input("Pseudo", key="pseudo_input", placeholder="ex: Satoshi_99", label_visibility="collapsed")
    with col_p2:
        st.button("Valider 🚀", on_click=save_pseudo, use_container_width=True)
else:
    invite_link = f"{BASE_URL}?ref={st.session_state.user_pseudo}"
    ref_count = st.session_state.referral_count
    
    st.markdown(f"""
        <div style="background-color: #161b22; border: 1px dashed #ffd700; border-radius: 12px; padding: 14px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span style="font-size: 0.95rem; color: #ffffff;">Bienvenue <b>@{st.session_state.user_pseudo}</b> ! ⚡</span>
                </div>
                <div style="background-color: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; color: #ffd700; font-weight: bold;">
                    👥 Filleuls vérifiés : {ref_count}
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 0.82rem; color: #8b949e; text-align: center;">
                Ton lien d'invitation : <code style="background: #0d0e12 !important; color: #ffd700 !important;">{invite_link}</code>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. Synchronisation JS & Validation des Parrainages
# ---------------------------------------------------------
TODAY = str(date.today())
url_count = query_params.get("cnt", None)
url_date = query_params.get("dt", None)

if "daily_request_count" not in st.session_state:
    if url_date == TODAY and url_count is not None:
        try:
            st.session_state.daily_request_count = int(url_count)
        except Exception:
            st.session_state.daily_request_count = 0
    else:
        st.session_state.daily_request_count = 0

requests_left = max(0, 2 - st.session_state.daily_request_count)

# Validation : Si un parrain est présent et que le filleul effectue son premier lancement
js_sync = f"""
<script>
    const today = "{TODAY}";
    const referrer = "{referrer if referrer else ''}";
    
    let storedDate = localStorage.getItem("crypto_analyst_date");
    let storedCount = localStorage.getItem("crypto_analyst_count");

    if (storedDate !== today) {{
        localStorage.setItem("crypto_analyst_date", today);
        localStorage.setItem("crypto_analyst_count", "0");
        storedCount = "0";
    }}

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("dt") !== today || urlParams.get("cnt") !== storedCount) {{
        urlParams.set("dt", today);
        urlParams.set("cnt", storedCount);
        window.location.search = urlParams.toString();
    }}
</script>
"""
components.html(js_sync, height=0)

# ---------------------------------------------------------
# 7. Helper Partage Social
# ---------------------------------------------------------
def generate_share_buttons(crypto_name, crypto_symbol, user_pseudo=""):
    share_url = f"{BASE_URL}?ref={user_pseudo}" if user_pseudo else BASE_URL
    text_to_share = (
        f"🚀 Je viens d'analyser {crypto_name} ({crypto_symbol}) avec l'agent IA Cryptos Analyst !\n\n"
        f"Teste l'outil gratuitement ici : {share_url}"
    )
    
    encoded_text = urllib.parse.quote(text_to_share)
    encoded_url = urllib.parse.quote(share_url)

    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
    twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
    telegram_url = f"https://t.me/share/url?url={encoded_url}&text={encoded_text}"
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"

    return f"""
    <div style="margin-top: 25px; margin-bottom: 15px;">
        <p style="font-weight: 700; color: #ffd700; margin-bottom: 10px; font-size: 0.95rem;">
            📢 Partager cette analyse avec tes proches :
        </p>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <a href="{whatsapp_url}" target="_blank" class="share-btn share-wa">💬 WhatsApp</a>
            <a href="{twitter_url}" target="_blank" class="share-btn share-x">𝕏 Twitter</a>
            <a href="{telegram_url}" target="_blank" class="share-btn share-tg">✈️ Telegram</a>
            <a href="{linkedin_url}" target="_blank" class="share-btn share-in">💼 LinkedIn</a>
            <a href="{facebook_url}" target="_blank" class="share-btn share-fb">📘 Facebook</a>
        </div>
    </div>
    """

# ---------------------------------------------------------
# 8. API CoinGecko & Gemini Failover
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_coingecko_data(query):
    try:
        search_url = f"https://api.coingecko.com/api/v3/search?query={query}"
        search_res = requests.get(search_url, timeout=10).json()
        coins = search_res.get("coins", [])
        if not coins:
            return None, "Actif non trouvé."
        
        coin_id = coins[0]["id"]
        data_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false"
        coin_data = requests.get(data_url, timeout=10).json()
        market = coin_data.get("market_data", {})
        
        return {
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
        }, None
    except Exception as e:
        return None, str(e)

def get_gemini_api_keys():
    keys = []
    if "GEMINI_API_KEY" in st.secrets:
        keys.append(st.secrets["GEMINI_API_KEY"])
    for i in range(1, 6):
        if f"GEMINI_API_KEY_{i}" in st.secrets:
            keys.append(st.secrets[f"GEMINI_API_KEY_{i}"])
    return list(dict.fromkeys(keys))

gemini_keys = get_gemini_api_keys()

if not gemini_keys:
    st.error("⚠️ Aucune clé API Gemini configurée dans secrets.toml.")
    st.stop()

def get_active_models_for_key(api_key):
    try:
        genai.configure(api_key=api_key)
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return [m for m in available if 'flash' in m] + [m for m in available if 'flash' not in m]
    except Exception:
        return ["models/gemini-2.5-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash"]

def generate_content_with_key_failover(prompt_text, system_instruction):
    last_err = "Aucune réponse générée."
    for api_key in gemini_keys:
        for model_name in get_active_models_for_key(api_key):
            try:
                genai.configure(api_key=api_key)
                try:
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction, tools=['google_search_retrieval'])
                    response = model.generate_content(prompt_text)
                    if response and response.text:
                        return response.text, None
                except Exception:
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
                    response = model.generate_content(prompt_text)
                    if response and response.text:
                        return response.text, None
            except Exception as e:
                last_err = str(e)
                continue
    return None, last_err

SYSTEM_INSTRUCTION = """
Tu es un analyste financier senior passionné par la crypto. Tu exprimes tes analyses avec un **ton familier, chaleureux, accessible et très enthousiaste** (tutoiement naturel).

CONSIGNE CRITIQUE 1 - EXACTITUDE & MISE À JOUR :
- Effectue obligatoirement une recherche Web pour VÉRIFIER L'EXACTITUDE des données financières et des dernières actualités majeures concernant le projet.
- Intègre impérativement les métriques chiffrées exactes transmises depuis l'API CoinGecko (prix, rang, Market Cap, ATH/ATL).

CONSIGNE CRITIQUE 2 - SÉVÉRITÉ ET COHÉRENCE DE LA NOTE :
Respecte STRICTEMENT ce barème :
- **0/10 à 3/10 (RISQUE TRÈS ÉLEVÉ / DANGER) :** Projet hautement spéculatif, memecoin sans utilité, projet suspect. NOTE MAX : 3.5/10.
- **4/10 à 5.5/10 (RISQUE MOYEN À ÉLEVÉ) :** Concurrence forte, utilité faible.
- **6/10 à 7.5/10 (SOLIDE AVEC RISQUES MODÉRÉS) :** Utilité réelle, forte adoption.
- **8/10 à 10/10 (SÉCURITÉ MAXIMALE) :** Actifs piliers (BTC, ETH).

Structure :
1. 📌 C'EST QUOI CE PROJET CONCRÈTEMENT ?
2. 📊 LES CHIFFRES EN DIRECT (GARDONS UN ŒIL SUR LE COUNTER)
> 🎓 Minute Pédago - Explique simplement une notion (ex: Market Cap).
3. 🚀 LES GROS MOTEURS DE HAUSSE & ACTUALITÉS RÉCENTES
4. ⚠️ LES PIÈGES ET RISQUES À NE PAS IGNORER
5. ⚔️ COMPARATIF AVEC LA CONCURRENCE
6. 🎯 MON VERDICT & MON CONSEIL DE POTE
"""

# ---------------------------------------------------------
# 9. Exécution Principale
# ---------------------------------------------------------
crypto_input = st.text_input("Quelle crypto veux-tu décortiquer aujourd'hui ?", placeholder="Tape un ticker ou nom (ex: BGB, Solana, ONDO, SUI, BTC...)")

if requests_left > 0:
    st.markdown(
        f"<div style='text-align: center; margin-top: -8px; margin-bottom: 12px; font-size: 0.85rem; color: #8b949e;'>"
        f"⚡ Crédits gratuits restants aujourd'hui : <span style='color: #ffd700; font-weight: bold;'>{requests_left} / 2</span>"
        f"</div>", 
        unsafe_allow_html=True
    )
else:
    st.warning("⚠️ Limite quotidienne de 2 analyses atteinte. Reviens demain !")

submit_button = st.button("🚀 LANCER L'ANALYSE D'EXPERT", disabled=(requests_left <= 0))

if submit_button and crypto_input:
    if requests_left <= 0:
        st.error("Limite atteinte.")
    else:
        # Activation de l'anneau tournant (L'avatar reste fixe)
        render_avatar(is_analyzing=True)
        
        with st.spinner(f"Recherche et vérification des données pour {crypto_input}..."):
            cg_data, error = get_coingecko_data(crypto_input)
            
            if not cg_data:
                render_avatar(is_analyzing=False)
                st.warning(f"😔 Aucune crypto trouvée pour « {crypto_input} ». Vérifie l'orthographe.")
            else:
                data_context = f"""
Données CoinGecko vérifiées pour {cg_data['name']} ({cg_data['symbol']}) :
- Prix actuel USD: `${cg_data['current_price_usd']}`
- Rang Market Cap: #{cg_data['rank']}
- Capitalisation: `${cg_data['market_cap_usd']:,}` USD
- Volume 24h: `${cg_data['total_volume_24h']:,}` USD
- Variation 24h: {cg_data['price_change_24h_pct']}% | 7j: {cg_data['price_change_7d_pct']}%
- ATH: `${cg_data['ath_usd']}` ({cg_data['ath_date']}) | ATL: `${cg_data['atl_usd']}` ({cg_data['atl_date']})
"""
                prompt_final = f"{data_context}\n\nEffectue une recherche Web et rédige l'analyse complète de : {cg_data['name']} ({cg_data['symbol']})"

                response_text, gen_error = generate_content_with_key_failover(prompt_final, SYSTEM_INSTRUCTION)
                
                # Arrêt de l'anneau tournant
                render_avatar(is_analyzing=False)

                if response_text:
                    new_count = st.session_state.daily_request_count + 1
                    st.session_state.daily_request_count = new_count
                    
                    inc_script = f"""
                    <script>
                        localStorage.setItem("crypto_analyst_date", "{TODAY}");
                        localStorage.setItem("crypto_analyst_count", "{new_count}");
                    </script>
                    """
                    components.html(inc_script, height=0)

                    st.markdown("<hr style='border-color: #30363d; margin: 2rem 0;'>", unsafe_allow_html=True)
                    st.markdown(response_text)
                    
                    share_html = generate_share_buttons(
                        cg_data['name'], 
                        cg_data['symbol'], 
                        user_pseudo=st.session_state.get("user_pseudo", "")
                    )
                    st.markdown(share_html, unsafe_allow_html=True)

                    st.markdown("---")
                    st.markdown("### 📋 Copier le rapport")
                    st.code(response_text, language="markdown")
                else:
                    st.error(f"Erreur API : {gen_error}")
