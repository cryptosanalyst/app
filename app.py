import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------
# 1. Configuration de la page Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="Crypto Analyst AI — Rapport Institutionnel",
    page_icon="⚡",
    layout="wide"
)

# Style sombre personnalisé
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

st.title("⚡ Crypto Analyst AI")
st.caption("Entrez le nom d'un actif crypto pour obtenir une analyse fondamentale complète.")

# ---------------------------------------------------------
# 2. Le Prompt Maître (Instructions Système)
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Tu es un expert senior en analyse financière et stratégies d'investissement dans le secteur des actifs numériques (Cryptomonnaies, Web3, DeFi & Infrastructure).

Lorsqu'un utilisateur te fournit le nom d'un actif crypto, tu dois effectuer une évaluation financière, fondamentale et stratégique ultra-détaillée.

Applique rigoureusement la structure suivante :

1. SYNTHÈSE EXÉCUTIVE & AVIS D'EXPERT
- Positionnement, catégorie de l'actif, profil risque/rendement et horizon d'évaluation.
- Thèse principale en 2-3 piliers majeurs.
- Verdict d'Expert (Positif / Neutre / Prudent).

2. FICHE TECHNIQUE & MÉTRIQUES CLÉS
- Prix actuel & Market Cap
- ATH (All-Time High) & ATL (All-Time Low) avec dates
- Lancement & Premier Listing
- Tokenomics (Supply circulante, Max supply, émission, mécanismes déflationnistes/burn).

3. THÈSE D'INVESTISSEMENT & MOTEURS D'ASYMÉTRIE
- Marché Adressable (TAM) & Écosystème
- Mécanisme d'Accumulation de Valeur (Gas, Staking, Real Yield, Burn)
- Synergies & Effets de Réseau

4. ANALYSE CRITIQUE DES RISQUES & LIMITES
- Risque de Tokenomics / Vesting / Unlocks
- Concurrence & Moat
- Risque Réglementaire & Dépendance Corporate

5. ANATOMIE COMPARATIVE DU SECTEUR
Intègre un tableau comparatif opposant l'actif étudié à 3 ou 4 de ses concurrents directs.

6. SCÉNARIOS D'ÉVOLUTION (Horizon 12 - 24 mois)
- Bull Case / Base Case / Bear Case

7. GRILLE D'ÉVALUATION FINALE & RECOMMANDATION TACTIQUE
- Grille de Notation sur 10 (5 critères)
- Score Global / 10
- Recommandation Tactique & 2-3 métriques clés à surveiller chaque trimestre.

Directives : Ton financier, direct, professionnel. Utilise le Markdown pour la lisibilité.
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
        placeholder="ex: BGB, Solana, ONDO, SUI, Bittensor..."
    )

with col2:
    st.write(" ")
    st.write(" ")
    submit_button = st.button("🚀 Lancer l'Analyse")

# ---------------------------------------------------------
# 5. Traitement & Génération du Rapport
# ---------------------------------------------------------
if submit_button and crypto_input:
    with st.spinner(f"Génération du rapport d'analyse pour **{crypto_input}**..."):
        # Modèles cibles par ordre de compatibilité recommandée par Google
        candidate_models = ["gemini-3.6-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        
        response_text = None
        last_error = None

        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_INSTRUCTION
                )
                prompt_utilisateur = f"Effectue l'analyse fondamentale complète et à jour de l'actif crypto : {crypto_input}"
                response = model.generate_content(prompt_utilisateur)
                response_text = response.text
                break  # Si la génération réussit, on sort de la boucle
            except Exception as e:
                last_error = e
                continue

        if response_text:
            st.markdown("---")
            st.markdown(response_text)
        else:
            st.error(f"Erreur lors de la génération : {last_error}")