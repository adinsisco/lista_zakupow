import streamlit as st
import sqlite3
import pandas as pd
from time import sleep
import streamlit.components.v1 as components
import os

def is_local():
    host = os.getenv('HOSTNAME', 'localhost')
    return host in ['localhost', '127.0.0.1', '::1']

def get_db_connection():
    conn = sqlite3.connect("lista_zakupow.db")
    conn.row_factory = sqlite3.Row
    return conn

def view_all_records():
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM zakupy ORDER BY nazwa_towaru").fetchall()
    conn.close()

    df = pd.DataFrame(records, columns=records[0].keys()) if records else pd.DataFrame()
    st.write("Wszystkie Rekordy")
    st.dataframe(df)

    if not df.empty:
        record_id = st.selectbox("Wybierz ID rekordu, aby oznaczyć jako do kupienia", df['id'])
        if st.button("Oznacz jako do kupienia"):
            conn = get_db_connection()
            conn.execute("UPDATE zakupy SET kupic = 'tak' WHERE id = ?", (record_id,))
            conn.commit()
            conn.close()
            st.success(f"Rekord o ID {record_id} został oznaczony jako do kupienia")
            sleep(1)
            st.rerun()

def view_buy_records_with_buttons2():
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM zakupy WHERE kupic = 'tak' ORDER BY numer_grupy").fetchall()
    conn.close()

    st.write("Do Kupienia")

    for record in records:
        button_label = f"{record['nazwa_towaru']} - {record['ilosc_towaru']} {record['jednostka']}"
        if st.button(button_label):
            conn = get_db_connection()
            conn.execute("UPDATE zakupy SET kupic = 'nie' WHERE id = ?", (record["id"],))
            conn.commit()
            conn.close()
            st.success(f"{record['nazwa_towaru']} został oznaczony jako kupiony")
            sleep(1)
            st.rerun()

def view_not_bought_records():
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM zakupy WHERE kupic = 'nie' ORDER BY nazwa_towaru").fetchall()
    conn.close()

    st.write("Do Zakupu")

    for record in records:
        button_label = f"{record['nazwa_towaru']} - {record['ilosc_towaru']} {record['jednostka']}"
        if st.button(button_label):
            conn = get_db_connection()
            conn.execute("UPDATE zakupy SET kupic = 'tak' WHERE id = ?", (record["id"],))
            conn.commit()
            conn.close()
            st.success(f"{record['nazwa_towaru']} został oznaczony jako do kupienia")
            sleep(1)
            st.rerun()

def view_buy_records_with_buttons():
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM zakupy WHERE kupic = 'tak' ORDER BY numer_grupy").fetchall()
    conn.close()

    st.write("Zmień ilość")

    if records:
        df = pd.DataFrame(records, columns=records[0].keys())
        for index, row in df.iterrows():
            col1, col2, col3, _ = st.columns([3, 2, 1, 1])
            with col1:
                st.text(f"{row['nazwa_towaru']} ({row['jednostka']})")
            with col2:
                new_quantity = st.number_input(
                    f"Ilość dla {row['nazwa_towaru']}",
                    min_value=0,
                    value=row['ilosc_towaru'],
                    key=f"qty_{row['id']}"
                )
            with col3:
                if st.button(f"Zaktualizuj ilość", key=f"update_{row['id']}"):
                    conn = get_db_connection()
                    conn.execute("UPDATE zakupy SET ilosc_towaru = ? WHERE id = ?",
                                 (new_quantity, row['id']))
                    conn.commit()
                    conn.close()
                    st.success(f"Ilość dla {row['nazwa_towaru']} została zaktualizowana")
                    st.rerun()

        for index, row in df.iterrows():
            if st.button(f"Oznacz jako kupiony: {row['nazwa_towaru']}", key=f"bought_{row['id']}"):
                conn = get_db_connection()
                conn.execute("UPDATE zakupy SET kupic = 'nie' WHERE id = ?", (row['id'],))
                conn.commit()
                conn.close()
                st.success(f"{row['nazwa_towaru']} został oznaczony jako kupiony")
                st.rerun()

def add_record():
    st.subheader("Dodaj Rekord")
    components.html(
        """
        <script>
        </script>
        """,
        height=0,
    )

    if is_local():
        st.write("Aplikacja działa lokalnie.")
    else:
        st.write("Aplikacja działa w hostingu.")

    # if is_local():
    numer_grupy = st.number_input("Numer Grupy", min_value=0)
    nazwa_grupy = st.text_input("Nazwa Grupy")
    nazwa_towaru = st.text_input("Nazwa Towaru")
    ilosc_towaru = st.number_input("Ilość Towaru", min_value=0)
    jednostka = st.selectbox("Jednostka", ["sztuka", "opakowanie", "litr", "kg"])
    kupic = st.selectbox("Kupić", ["tak", "nie"])

    if st.button("Dodaj"):
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO zakupy (numer_grupy, nazwa_grupy, nazwa_towaru, ilosc_towaru, jednostka, kupic) VALUES (?, ?, ?, ?, ?, ?)",
            (numer_grupy, nazwa_grupy, nazwa_towaru, ilosc_towaru, jednostka, kupic),
        )
        conn.commit()
        conn.close()
        st.success("Rekord został dodany")

def delete_record():
    st.subheader("Usuń Rekord")
    record_id = st.number_input("ID Rekordu", min_value=0)
    if st.button("Usuń"):
        conn = get_db_connection()
        conn.execute("DELETE FROM zakupy WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        st.success(f"Rekord z ID {record_id} został usunięty")

def edit_record():
    st.subheader("Edytuj Rekord")
    record_id = st.number_input("ID Rekordu do Edycji", min_value=0)

    conn = get_db_connection()
    record = conn.execute("SELECT * FROM zakupy WHERE id = ?", (record_id,)).fetchone()
    conn.close()

    if record:
        numer_grupy = st.number_input("Numer Grupy", min_value=0, value=record["numer_grupy"])
        nazwa_grupy = st.text_input("Nazwa Grupy", value=record["nazwa_grupy"])
        nazwa_towaru = st.text_input("Nazwa Towaru", value=record["nazwa_towaru"])
        ilosc_towaru = st.number_input("Ilość Towaru", min_value=0, value=record["ilosc_towaru"])
        jednostka = st.selectbox("Jednostka", ["sztuka", "opakowanie", "litr", "kg"], index=["sztuka", "opakowanie", "litr", "kg"].index(record["jednostka"]))
        kupic = st.selectbox("Kupić", ["tak", "nie"], index=["tak", "nie"].index(record["kupic"]))

        if st.button("Aktualizuj"):
            conn = get_db_connection()
            conn.execute(
                "UPDATE zakupy SET numer_grupy = ?, nazwa_grupy = ?, nazwa_towaru = ?, ilosc_towaru = ?, jednostka = ?, kupic = ? WHERE id = ?",
                (numer_grupy, nazwa_grupy, nazwa_towaru, ilosc_towaru, jednostka, kupic, record_id),
            )
            conn.commit()
            conn.close()
            st.success("Rekord został zaktualizowany")
    else:
        st.warning("Rekord nie istnieje")

def main():
    st.sidebar.title("Menu")
    choice = st.sidebar.selectbox("Wybierz opcję", ["Do kupienia", "Do Zakupu", "Zmień ilość", "Przeglądaj wszystkie", "Dodaj", "Usuń", "Edytuj"])

    if choice == "Do kupienia":
        view_buy_records_with_buttons2()
    elif choice == "Do Zakupu":
        view_not_bought_records()
    elif choice == "Zmień ilość":
        view_buy_records_with_buttons()    
    elif choice == "Przeglądaj wszystkie":
        view_all_records()
    elif choice == "Dodaj":
        add_record()
    elif choice == "Usuń":
        delete_record()
    elif choice == "Edytuj":
        edit_record()

if __name__ == "__main__":
    main()