import pandas as pd
import streamlit as st
import os


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


def init_session_state():
    submit_button_parcour, st.session_state.standardzeit_sec = Parcour_data_form()

# Funktion zum Berechnen der Punktzahlen
def add_c(df: pd.DataFrame) -> pd.DataFrame:
    try:
        total_seconds = df['Minuten'] * 60 + df['Sekunden'] + df['Millisekunden'] / 1000

        # Calculate exceeded seconds
        exceeded_seconds = total_seconds - st.session_state.standardzeit_sec
        exceeded_seconds = exceeded_seconds.fillna(0)  # Replace NaN with zero
        # Ensure that exceeded_seconds is non-negative (using .clip(lower=0))
        exceeded_seconds = exceeded_seconds.clip(lower=0)

        # Calculate points for exceeded seconds
        exceeded_points = exceeded_seconds.astype(int)
        df["Punkte"] = (df["Fehler"] * 5) + (df["Verweigerung"] * 5) + exceeded_points

    except KeyError:
        pass
    return df

# Funktion zum Hochladen der Datei
def upload_file_2():
    uploaded_file = st.file_uploader("", type=["csv"])
    if uploaded_file:
        st.success("Datei erfolgreich hochgeladen!")
        st.session_state['uploaded_filename'] = os.path.splitext(uploaded_file.name)[0]
        return uploaded_file
    else:
        st.warning("Bitte laden Sie eine CSV-Datei hoch.")  # Warnung hinzufügen, wenn keine Datei hochgeladen wurde
    return None

# Funktion zur Anzeige und Bearbeitung der Daten
def display():
    uploaded_file = upload_file_2()

    if uploaded_file and "uploaded" not in st.session_state:
        st.session_state.uploaded = True
        st.session_state.df = pd.read_csv(uploaded_file, sep=';')
        st.session_state.df = st.session_state.df.drop(columns=['Prüfung', 'Cup'], errors='ignore')
        st.session_state.df["Dis"] = False  # Add "Dis" if missing, defaulting to False

    if "df" in st.session_state:
        # Aktualisieren Sie den Dataframe vor der Anzeige
        st.session_state.df = add_c(st.session_state.df)

        # Zeigen Sie den aktualisierten Dataframe an
        editable_df = st.data_editor(st.session_state["df"], key="data", num_rows="dynamic", column_config={"Dis": {'editable':True, 'widget': 'toggle'}})

        # Überprüfen Sie, ob Änderungen vorgenommen wurden
        if not editable_df.equals(st.session_state["df"]):
            st.session_state.df = editable_df
            st.experimental_rerun()

# Funktion zum Speichern der finalen Tabelle
def save_finale_table():
    if "df" in st.session_state:
        transformed_df = st.session_state.df.copy()
        try:
            transformed_df["Dis"] = transformed_df["Dis"].apply(lambda x: "Disqualifiziert" if x else "")
        except KeyError:
            pass
        sorted_df = transformed_df.sort_values(
            by=['Punkte', 'Minuten', 'Sekunden', 'Millisekunden'],
            ascending=[True, True, True, True]
        )

        # Entfernen der Spalte "Startnummern" und Hinzufügen der neuen Spalte "Platzierung"
        sorted_df = sorted_df.drop(columns=["Startnummern"], errors='ignore')
        sorted_df["Platzierung"] = range(1, len(sorted_df) + 1)  # Vergibt fortlaufende Platzierungen

        # Zeilen mit "Dis" am Ende sortieren
        sorted_df = sorted_df.sort_values(
            by=['Dis', 'Platzierung'],
            ascending=[True, True]  # "Dis" zuerst sortieren, dann "Platzierung"
        )
        # Neue Spaltenreihenfolge: "Platzierung" zuerst
        columns = ["Platzierung"] + [col for col in sorted_df.columns if col != "Platzierung"]
        sorted_df = sorted_df[columns]
        
        # Basisinformationen in der CSV-Datei als Kommentar einfügen
        basis_info = [
            f"# Veranstalter: {st.session_state.get('organizer', '')}",
            f"# AG Richter: {st.session_state.get('ag_richter', '')}",
            f"# Jump Richter: {st.session_state.get('jump_richter', '')}",
            f"# Art der Veranstaltung: {st.session_state.get('art_der_veranstaltung', '')}",
            f"# Ort der Veranstaltung: {st.session_state.get('ort_der_veranstaltung', '')}",
            f"# Datum: {st.session_state.get('date', '')}",
        ]
        # Use the uploaded file name to derive the output file name
        default_filename = st.session_state.get('uploaded_filename', 'Ergebnisliste')
        result_filename = default_filename.replace("Starterliste", "Ergebnisliste")

        csv_data = "\n".join(basis_info) + "\n" + sorted_df.to_csv(index=False, sep=";")
        st.download_button(
            label="Ergebnisliste herunterladen",
            data=csv_data,
            file_name=f"{result_filename}.csv",
            mime="text/csv"
        )
    with st.sidebar:
        # Navigationstasten in der Sidebar
        if st.button("🏠 Startseite"):
            st.session_state.current_page = "main"
            st.experimental_rerun()
        
        if st.button("🏃‍♂️ Agility Lauf"):
            st.session_state.current_page = "page_2"
            st.experimental_rerun()
# Hauptfunktion
def main():
    init_session_state()
    
    if 'standardzeit_sec' in st.session_state:
        total_seconds = st.session_state['standardzeit_sec']
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        st.info(f"Die Standardzeit beträgt: {minutes} Minuten und {seconds} Sekunden")
    else:
            st.error("Standardzeit wurde nicht gespeichert.")
            
    display()  # Anzeige und Bearbeitung der Daten
    save_finale_table()  # Speichern der finalen Tabelle

if __name__ == "__main__":
    main()
