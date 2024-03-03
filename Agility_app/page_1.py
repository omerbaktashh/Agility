import streamlit as st
import pandas as pd
import numpy as np
import os
import time


def shuffle_dataframe(df):
    shuffled_df = df.sample(frac=1, random_state=42)
    return shuffled_df.reset_index(drop=True)


def Parcour_data_form():
    standardzeit_sec = 0

    with st.form("Parcour-Daten"):
        st.subheader("Parcour-Daten eingeben, um Standardzeit zu berechnen")
        laenge_meter = st.number_input("Länge in Meter")
        bewegung_sec = st.number_input("Bewegung in Sekunden")

        if (laenge_meter != 0) & (bewegung_sec != 0):
            standardzeit_sec = round(laenge_meter / bewegung_sec)
            st.session_state['standardzeit_sec'] = standardzeit_sec
            st.write("Die Standardzeit beträgt:", standardzeit_sec, "Sekunden")
        else:
            st.error("Die Länge in Meter und die Bewegung in Sekunden dürfen nicht null sein.")

        anzahl_hindernisse = st.number_input("Anzahl Hindernisse", min_value=0, step=1)
        submit_button = st.form_submit_button("Standardzeit ausgeben")
    return submit_button, standardzeit_sec


# Styling-Funktion definieren
def highlight_first_row(s):
    if s.name == 0:
        return ['background-color: yellow'] * len(s)
    else:
        return [''] * len(s)


def upload_file():
    st.title("Teilnehmerliste hochladen - Startnummern werden automatisch vergeben")
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

        st.subheader("Mit welchem Lauf soll gestartet werden?")
        selected_runs = st.multiselect("Lauf auswählen", ["Mini-Lauf", "Maxi-Lauf", "A1", "A2", "Cup"])

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
            filtered_df = filtered_df.drop_duplicates()

            st.subheader("hochgeladene Teilnehmerliste:")
            # filtered_df = filtered_df[filtered_df["Prüfung"].notnull()] # falls Prüfung leer ist, werden diese nicht angezeigt
            st.dataframe(filtered_df)

            submit_button_parcour, st.session_state.standardzeit_sec = Parcour_data_form()

            # shuffle_dataframe
            shuffled_df = shuffle_dataframe(st.session_state['df'])
            for col in ['Minuten', 'Sekunden', 'Millisekunden', 'Fehler', 'Verweigerung']:
                shuffled_df[col] = 0

            columns_to_convert = ['Minuten', 'Sekunden', 'Millisekunden', 'Fehler', 'Verweigerung']
            for col in columns_to_convert:
                shuffled_df[col] = shuffled_df[col].astype(int)
            
            # Store shuffled_df in session state
            st.session_state['shuffled_df'] = shuffled_df
        
        if 'shuffled_df' in st.session_state:
            st.info("Starterliste:", icon="ℹ️")
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
    if "shuffled_df" in st.session_state:
        file_name = st.text_input("Geben Sie einen Namen für die CSV-Datei ein")
        if file_name:
            csv = st.session_state.shuffled_df.to_csv(index=False, sep=";")
            st.download_button(
                label="Starterliste herunterladen",
                data=csv,
                file_name=f"{file_name}.csv",
                mime="text/csv",
            )

def main():
    init_session_state()
    starter_list_to_csv()
    agility_run()


if __name__ == "__main__":
    main()