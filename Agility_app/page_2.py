import pandas as pd
import streamlit as st
import time

def add_c(df: pd.DataFrame) -> pd.DataFrame:
    try:
        total_seconds = df['Minuten'] * 60 + df['Sekunden'] + df['Millisekunden'] / 1000

        # Calculate exceeded seconds
        exceeded_seconds = total_seconds - st.session_state.standardzeit_sec

        # Ensure that exceeded_seconds is non-negative (using .clip(lower=0))
        exceeded_seconds = exceeded_seconds.clip(lower=0)

        # Calculate points for exceeded seconds
        exceeded_points = exceeded_seconds.astype(int)
        df["Punkte"] = (df["Fehler"] * 5) + (df["Verweigerung"] * 5) + exceeded_points

    except KeyError as e:
        st.write("")
    return df


def upload_file_2():
    uploaded_file_2 = st.file_uploader("Datei hochladen", type=["csv"])
    if uploaded_file_2:
        st.success("Datei erfolgreich hochgeladen!")
        with st.spinner('Starterliste wird aufbereitet - Sie können gleich mit der Dateneingabe beginnen...'):
                time.sleep(3)
        return uploaded_file_2
    return None


def display():
    uploaded_file = upload_file_2()

    if uploaded_file and "uploaded" not in st.session_state:
        st.session_state.uploaded = True
        st.session_state.df = pd.read_csv(uploaded_file, sep=';')
        st.session_state.df = st.session_state.df.drop(columns=['Prüfung', 'Cup'], errors='ignore')

    if "df" in st.session_state:
        # Aktualisieren Sie den Dataframe vor der Anzeige
        st.session_state.df = add_c(st.session_state.df)

        # Zeigen Sie den aktualisierten Dataframe an
        editable_df = st.data_editor(st.session_state["df"], key="data", num_rows="dynamic")

        # Überprüfen Sie, ob Änderungen vorgenommen wurden
        if not editable_df.equals(st.session_state["df"]):
            st.session_state.df = editable_df
            st.experimental_rerun()


def save_finale_table():
    if "df" in st.session_state:
        sorted_df = st.session_state.df.sort_values(by=['Punkte', 'Minuten', 'Sekunden', 'Millisekunden'],
                                                    ascending=[True, True, True, True])
        file_name = st.text_input("Geben Sie einen Namen für die Ergebnisliste ein")
        if file_name:
            csv = sorted_df.to_csv(index=False, sep=";")
            st.download_button(
                label= "Ergebnisliste herunterladen",
                data = csv,
                file_name=f"{file_name}.csv",
                mime="text/csv",
            )


def main():
    if 'standardzeit_sec' in st.session_state:
        total_seconds = st.session_state['standardzeit_sec']
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        st.info(f"Die Standardzeit beträgt: {minutes} Minuten und {seconds} Sekunden")
    else:
            st.error("Standardzeit wurde nicht gespeichert.")
    #functions above
    display()
    save_finale_table()


if __name__ == "__main__":
    main()


