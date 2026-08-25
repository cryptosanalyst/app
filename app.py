
# ---------------------------------------------------------
# API Gemini : Utilisation des modèles stables actuels
# ---------------------------------------------------------
def generate_content_with_key_failover(prompt_text, system_instruction):
    gemini_keys = [st.secrets[k] for k in st.secrets if "GEMINI_API_KEY" in k]
    if not gemini_keys:
        return None, "Aucune clé API trouvée dans secrets.toml"
    
    # Modèles actuels supportés sur l'API
    candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash"]
    last_error = ""

    for api_key in gemini_keys:
        try:
            genai.configure(api_key=api_key)
            
            for model_name in candidate_models:
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=system_instruction
                    )
                    response = model.generate_content(prompt_text)
                    if response and response.text:
                        return response.text, None
                except Exception as m_err:
                    last_error = str(m_err)
                    continue
        except Exception as e:
            last_error = str(e)
            continue

    return None, f"Toutes les clés/modèles ont échoué. Dernière erreur : {last_error}"
