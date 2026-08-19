import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------
# 1. Configuration de la page Streamlit & Style Montserrat
# ---------------------------------------------------------
st.set_page_config(
    page_title="Crypto Analyst AI — Rapport Pédagogique",
    page_icon="⚡",
    layout="wide"
)

# Chargement de la police Montserrat et application du style
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&display=swap');

    html, body, [class*="css"], .stMarkdown {
        font-family: 'Montserrat', sans-serif !important;
    }

    .main { 
        background-color: #0d0e12; 
        color: #e2e8f0; 
    }
    
    h1 { 
        color: #ffd700; 
        text-align: center; 
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 900 !important; 
        text-transform: uppercase;
    }

    h2, h3, h4 {
        color: #ffd700 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
    }

    .stButton>button { 
        background-color: #ffd700; 
        color: #0d0e12; 
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 900 !important; 
        width: 100%; 
        border-radius: 6px; 
        height: 50px;
        font-size: 16px;
    }
    .stButton>button:hover { 
        background-color: #ffe866; 
        color: #0d0e12; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Crypto Analyst AI")
st.caption("Entrez le nom d'un actif crypto pour obtenir un rapport clair, compréhensible et facile à lire.")

# ---------------------------------------------------------
# 2. Le Prompt Maître (Pédagogique pour débutants)
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un expert en analyse financière et vulgarisation de projets cryptos. Ton objectif est de rendre chaque analyse **facilement compréhensible par un débutant complet**, tout en restant rigoureux et précis.

Règles de rédaction :
- Utilise des mots simples. Si tu emploies un terme technique (ex: Tokenomics, Layer 2, Staking, Burn, Market Cap), explique-le immédiatement avec une analogie simple de la vie courante.
- Structure le contenu clairement avec du gras et des puces.
- Adopte un ton pédagogique, bienveillant et direct.

Structure de l'analyse à suivre rigoureusement :

1. 📌 C'EST QUOI CE PROJET ? (RÉSUMÉ SIMPLE)
- Explique ce que fait le projet comme si tu l'expliquais à un ami qui n'y connaît rien.
- Quelle est sa catégorie (ex: monnaie, banque décentralisée, réseau rapide, etc.) ?
- Ton verdict rapide : Intéressant, Moyen ou Risqué ?

2. 📊 LES CHIFFRES CLÉS (EXPLIQUÉS SIMPLEMENT)
- Prix actuel & Valeur totale du projet (Market Cap).
- Plus haut prix historique (ATH) et plus bas (ATL).
- La quantité de jetons disponibles (expliquer s'il y en aura d'autres créés ou si l'offre diminue).

3. 🚀 POURQUOI CE PROJET PEUT PRENDRE DE LA VALEUR ?
- Quel problème réel essaie-t-il de résoudre ?
- Comment le jeton gagne-t-il de la valeur quand le projet est utilisé ?

4. ⚠️ LES RISQUES À CONNAÎTRE (AVANT D'INVESTIR)
- Quels sont les pièges ou les dangers (concurrence, régulation, jetons bloqués) ?

5. ⚔️ COMPARATIVE AVEC LES CONCURRENTS
- Un petit tableau ou comparatif simple avec 2 à 3 projets connus du même domaine.

6. 🎯 VERDICT ET CONSEIL SIMPLE
- Une note sur 10 basée sur la solidité du projet.
- Une recommandation prudente pour un débutant.
"""

# ---------------------------------------------------------
# 3. Initialisation de l'API Gemini
# ---------------------------------------------------------
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_api_key)
except Exception:
    st.error("⚠️ Clé API Gemini manquante. Veuillez vérifier votre fichier secrets.toml.")
    st.stop()

# ---------------------------------------------------------
# 4. Interface Utilisateur
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
# 5. Traitement avec la version 'gemini-3.6-flash'
# ---------------------------------------------------------
if submit_button and crypto_input:
    with st.spinner(f"Analyse simplifiée de **{crypto_input}** en cours..."):
        # Liste avec le modèle gemini-3.6-flash exigé par l'API
        candidate_models = ["gemini-3.6-flash", "gemini-1.5-flash-latest"]
        
        response_text = None
        last_error = None

        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_INSTRUCTION
                )
                prompt_utilisateur = f"Effectue une analyse simple, pédagogique et complète de l'actif crypto : {crypto_input}"
                response = model.generate_content(prompt_utilisateur)
                response_text = response.text
                break
            except Exception as e:
                last_error = e
                continue

        if response_text:
            st.markdown("---")
            st.markdown(response_text)
            
            st.markdown("---")
            st.subheader("📋 Copier le résultat")
            st.caption("Survolez le bloc ci-dessous et cliquez sur l'icône de copie en haut à droite :")
            st.code(response_text, language="markdown")
        else:
            st.error(f"Erreur lors de la génération : {last_error}")
