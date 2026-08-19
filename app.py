import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import base64
import os
import streamlit.components.v1 as components

# [Garde ton style CSS intact ici...]

# ---------------------------------------------------------
# Fonction API ultra-simplifiée (Force la version stable)
# ---------------------------------------------------------
def generate_report_v1(prompt_text, system_instruction):
    # Récupérer toutes les clés
    keys = [st.secrets[k] for k in st.secrets if "GEMINI_API_KEY" in k]
    
    for api_key in keys:
        try:
            # Configurer le SDK
            genai.configure(api_key=api_key)
            
            # Utiliser le modèle stable sans préfixe "models/"
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            
            response = model.generate_content(prompt_text)
            
            if response and response.text:
                return response.text, None
            else:
                return None, "Réponse vide reçue"
                
        except Exception as e:
            # On continue sur la prochaine clé si celle-ci échoue
            continue
            
    return None, "Toutes les clés ont échoué. Vérifiez vos quotas ou vos clés."

# ---------------------------------------------------------
# Interface (Exemple de bouton)
# ---------------------------------------------------------
if st.button("🚀 LANCER L'ANALYSE"):
    # ... (ton code de vérification coingecko reste ici) ...
    
    # Appel de la fonction simplifiée
    res, gen_err = generate_report_v1(prompt, SYSTEM_INSTRUCTION)
    
    if res:
        st.markdown(res)
    else:
        st.error(f"Erreur API : {gen_err}")
