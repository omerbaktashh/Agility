import streamlit as st
import pandas as pd
import numpy as np
import os
import time


def shuffle_dataframe(df):
    shuffled_df = df.sample(frac=1, random_state=42)
    return shuffled_df.reset_index(drop=True)


def upload_file():
    st.title("Laden Sie die Teilnehmerliste hoch - Die Startnummern werden automatisiert erstellt und weiter unten angezeigt.")
    uploaded_file = st.file_uploader("Datei hochladen", type=["csv", "xlsx"])
    if uploaded_file:
        st.success("Datei erfolgreich hochgeladen!")
        return uploaded_file


def init_session_state():
    uploaded_file = upload_file()
    if uploaded_file is not None:

        file_extension = uploaded_file.name.split(".")[-1]
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file, sep=';')
        elif file_extension == "xlsx":
            df = pd.read_excel(uploaded_file)

        # anzeige für Auswahl mini oder maxi
        if 'df' not in st.session_state and df is not None:
            st.session_state['df'] = df
        if 'current_row' not in st.session_state:
            st.session_state['current_row'] = 0

        st.subheader("Wählen Sie aus, mit welchem Lauf gestartet werden soll.")
        selected_runs = st.multiselect("Lauf auswählen", ["Mini-Lauf", "Maxi-Lauf", "A1", "A2", "Cup"])

        # Generierung des Standard-Dateinamens basierend auf der Auswahl der Läufe
        if selected_runs:
            dateiname = "_".join(selected_runs)
            st.session_state['file_name'] = f"Starterliste_{dateiname}"
        
        if 'df' in st.session_state:
            filtered_df = st.session_state['df'].copy()

            if "Mini-Lauf" in selected_runs:
                filtered_df = filtered_df[filtered_df["Mini_Maxi"] == "Mini"]

            if "Maxi-Lauf" in selected_runs:
                filtered_df = filtered_df[filtered_df["Mini_Maxi"] == "Maxi"]

            if "A1" in selected_runs:
                filtered_df = filtered_df[filtered_df["Prüfung"] == "A1"]

            if "A2" in selected_runs:
                filtered_df = filtered_df[filtered_df["Prüfung"] == "A2"]

            if "Cup" in selected_runs:
                filtered_df = filtered_df[filtered_df["Cup"] == "Cup"]

            # Entfernen Sie doppelte Einträge, falls es welche gibt
            st.session_state.filtered_df = filtered_df.drop_duplicates()

            st.subheader("hochgeladene & gefilterte Teilnehmerliste")
            st.dataframe(filtered_df)
            
            # Standard-Dateiname zuweisen
            if 'file_name' in st.session_state:
                st.session_state['download_name'] = f"{st.session_state['file_name']}.csv"


            # shuffle_dataframe
            shuffled_df = shuffle_dataframe(st.session_state['filtered_df'])
            for col in ['Minuten', 'Sekunden', 'Millisekunden', 'Fehler', 'Verweigerung']:
                shuffled_df[col] = 0

            columns_to_convert = ['Minuten', 'Sekunden', 'Millisekunden', 'Fehler', 'Verweigerung']
            for col in columns_to_convert:
                shuffled_df[col] = shuffled_df[col].astype(int)
            
            # Store shuffled_df in session state
            shuffled_df["Startnummer"] = np.arange(1, len(shuffled_df) + 1)
            columns_order = [shuffled_df.columns[-1]] + list(shuffled_df.columns[:-1])
            shuffled_df = shuffled_df[columns_order]
            st.session_state['shuffled_df'] = shuffled_df
        
        if 'shuffled_df' in st.session_state:
            st.info("automatisierte Starterliste", icon="ℹ️")
            st.write(st.session_state['shuffled_df'])


def agility_run():
    if 'df' in st.session_state:
        button_run = st.button("Agility-Lauf Starten!")
        if button_run:
            with st.spinner('Starterliste wird aufbereitet...'):
                time.sleep(3)
            st.session_state.current_page = "page_2"
            st.experimental_rerun()


def starter_list_to_csv():
    if "shuffled_df" in st.session_state and "download_name" in st.session_state:
            csv = st.session_state.shuffled_df.to_csv(index=False, sep=";")
            st.download_button(
                label="Starterliste herunterladen",
                data=csv,
                file_name=st.session_state['download_name'],
                mime="text/csv",
            )
    with st.sidebar:
        # Navigationstasten in der Sidebar
        if st.button("🏠 Startseite"):
            st.session_state.current_page = "main"
            st.experimental_rerun()
        
        if st.button("🏃‍♂️ Agility Lauf"):
            st.session_state.current_page = "page_2"
            st.experimental_rerun()
def main():
    init_session_state()
    starter_list_to_csv()
    #agility_run()


if __name__ == "__main__":
    main()