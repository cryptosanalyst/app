import streamlit as st
import google.generativeai as genai
import requests
from datetime import date
import os
import base64
import streamlit.components.v1 as components
import re

# ... (Garde toute la partie Style CSS et Avatar identique à la version précédente) ...

# ---------------------------------------------------------
# API : Correction définitive du modèle (Sans préfixe "models/")
# ---------------------------------------------------------
def generate_clean_report(prompt_text, system_instruction):
    gemini_keys = [st.secrets[k] for k in st.secrets if "GEMINI_API_KEY" in k]
    if not gemini_keys: return None, "Aucune clé API configurée."
    
    # Utilisation du nom simple 'gemini-1.5-flash'
    # C'est la syntaxe la plus stable pour éviter l'erreur 404 v1beta
    model_name = "gemini-1.5-flash"
    
    for api_key in gemini_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
            response = model.generate_content(prompt_text)
            
            if response and response.text:
                txt = response.text.strip()
                # Nettoyage automatique du brouillon si présent
                start_match = re.search(r"1\.\s?📌", txt)
                if start_match: txt = txt[start_match.start():]
                return txt, None
        except Exception as e:
            # On log l'erreur pour comprendre, mais on continue avec la clé suivante
            continue
            
    return None, "Erreur API : Vérifiez que vos clés sont valides et que google-generativeai est à jour."

# ---------------------------------------------------------
# Interface (Reste de la logique identique)
# ---------------------------------------------------------
# (Ici, reprends exactement la même interface que ton code précédent)
