import streamlit as st
import pandas as pd
import numpy as np
import csv
import page_1
import page_2


def main_page():
    st.title("Daten der Agility-Veranstaltung eingeben")

    organizer = st.text_input("Veranstalter")
    ag_richter = st.text_input("AG Richter")
    jump_richter = st.text_input("Jump Richter")
    art_der_veranstaltung = st.text_input("Art der Veranstaltung")
    ort_der_veranstaltung = st.text_input("Ort der Veranstaltung")
    date = st.date_input("Datum")

    button_pruefung = st.button("Weiter")
    if button_pruefung:
        st.session_state.current_page = "page_1"
        st.experimental_rerun()


    with st.sidebar:
        st.title("Anmelde-Bogen")
        form = st.form(key="Teilname", clear_on_submit=True)
        with form:
            name = st.text_input(label="Name")
            dog_name = st.text_input(label="Name des Hundes")
            dog_race = st.text_input(label="Hunderasse")
            group = st.text_input(label="Gruppe")
            mini_maxi = st.radio("Mini oder Maxi", ["Mini", "Maxi"])
            cup_name = st.radio("Cup-Teilnahme", ["", "Fun", "Cup"])
            pruefung = st.radio("Prüfung", ["", "A1", "A2"])
            submit_button = form.form_submit_button("Teilnahme absenden")

            if submit_button:
                st.write(f"Die Teilnahme von {name} und {dog_name} wurde versendet.")
                save_data(name, dog_name, dog_race, group, mini_maxi, cup_name, pruefung)


def save_data(first_name, last_name, dog_name, dog_race, cup_name, group, mini_maxi):
    # Speichern der Daten in einer CSV-Datei
    with open("teilnehmer.csv", "a", newline="") as file:
        writer = csv.writer(file)
        # Schreibe die Spaltennamen, wenn die Datei leer ist
        if file.tell() == 0:
            writer.writerow(
                ["Name", "Name des Hundes", "Hunderasse", "Gruppe", "Mini oder Maxi", "Cup-Teilnahme", "Prüfung"])
        writer.writerow([first_name, last_name, dog_name, dog_race, cup_name, group, mini_maxi])


def main():
    st.set_page_config(layout="wide")
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "main"

    if st.session_state.current_page == "main":
        main_page()
    elif st.session_state.current_page == "page_1":
        page_1.main()
    elif st.session_state.current_page == "page_2":
        page_2.main()

if __name__ == "__main__":
    main()





