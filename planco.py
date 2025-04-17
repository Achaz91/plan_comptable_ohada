import streamlit as st
import pandas as pd
import os

# --- Configuration ---
# Chemin relatif du fichier CSV (à modifier par le développeur)
CSV_FILE_PATH = "planco.csv"
CSV_SEPARATOR = ";" # Définition du séparateur
# --- Fin Configuration ---

# Fonction pour charger les données CSV
@st.cache_data
def load_data(file_path, separator):
    if not os.path.exists(file_path):
        st.error(f"Erreur: Le fichier CSV spécifié ('{file_path}') n'a pas été trouvé.")
        return None
    try:
        df = pd.read_csv(file_path, sep=separator)
        # Traiter les numéros de compte comme des chaînes et supprimer les séparateurs de milliers potentiels
        df['Numéro de compte'] = df['Numéro de compte'].astype(str).str.replace(r'[^\d]', '', regex=True)
        # Extraction de la classe basée sur le premier chiffre du 'Numéro de compte'
        df['Classe'] = df['Numéro de compte'].astype(str).str[0].astype(int)
        return df
    except pd.errors.ParserError as e:
        st.error(f"Erreur lors de la lecture du fichier CSV: {e}")
        return None

# Fonction pour filtrer les données par classe
def filter_by_class(df, selected_class):
    if selected_class == "Toutes":
        return df
    else:
        return df[df['Classe'] == int(selected_class)]

# Fonction pour filtrer les données par numéro de compte (début de chaîne)
def filter_by_numero(df, selected_numero_prefix):
    if not selected_numero_prefix:
        return df
    else:
        return df[df['Numéro de compte'].astype(str).str.startswith(selected_numero_prefix)]

# Fonction pour filtrer les données par mots-clés dans l'intitulé
def filter_by_keywords(df, keywords):
    if not keywords:
        return df
    else:
        keywords = keywords.lower().split()
        return df[df['Intitulé du compte'].str.lower().apply(lambda x: all(keyword in x for keyword in keywords))]

def main():
    st.title("Explorateur du Plan Comptable OHADA")
    st.subheader("Basé sur un fichier CSV fourni")

    # Charger les données (sans intervention de l'utilisateur)
    data = load_data(CSV_FILE_PATH, CSV_SEPARATOR)

    # Vérifier si les données ont été chargées correctement
    if data is None:
        return

    # Sidebar pour les filtres
    with st.sidebar:
        st.header("Filtres")
        # Sélection de la classe
        if 'Classe' in data.columns:
            classes_uniques = ["Toutes"] + sorted(data['Classe'].unique().astype(str).tolist())
            selected_class = st.selectbox("Sélectionner une Classe", classes_uniques)
        else:
            selected_class = "Toutes"
            st.warning("La colonne 'Classe' n'a pas été trouvée. Le filtrage par classe ne sera pas disponible.")

        # Filtre par numéro de compte
        numero_prefix = st.text_input("Filtrer par les premiers chiffres du Numéro de Compte")

        # Recherche par mots-clés
        keywords = st.text_input("Rechercher par mots-clés dans l'Intitulé")

    # Appliquer les filtres
    filtered_data = data
    if 'Classe' in data.columns:
        filtered_data = filter_by_class(filtered_data, selected_class)
    filtered_data = filter_by_numero(filtered_data, numero_prefix)
    filtered_data = filter_by_keywords(filtered_data, keywords)

    # Afficher les données filtrées
    st.subheader("Résultats Filtrés")
    st.dataframe(filtered_data)

    # Option pour télécharger les résultats filtrés
    st.download_button(
        label="Télécharger les résultats au format CSV",
        data=filtered_data.to_csv(index=False, sep=CSV_SEPARATOR).encode('utf-8'),
        file_name='plan_comptable_filtre.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()
