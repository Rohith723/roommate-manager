import streamlit as st
from database import get_connection
from streamlit_extras.switch_page_button import switch_page


st.title("➕ Add / ❌ Remove Roommate")

# Add Roommate Section
st.subheader("Add a Roommate")
name = st.text_input("Roommate Name")
mobile = st.text_input("Mobile Number")

if st.button("Add Roommate"):
    if name.strip() == "":
        st.warning("Roommate name cannot be empty.")
    else:
        conn = get_connection()
        conn.execute("INSERT INTO roommates (name, mobile) VALUES (?, ?)", (name, mobile))
        conn.commit()
        conn.close()
        st.success(f"{name} added successfully!")

# Remove Roommate Section
st.subheader("Remove a Roommate")

conn = get_connection()
roommates = conn.execute("SELECT id, name FROM roommates").fetchall()

if not roommates:
    st.info("No roommates available to remove.")
else:
    roommate_dict = {f"{r[1]} (ID: {r[0]})": r[0] for r in roommates}
    selected = st.selectbox("Select Roommate to Remove", list(roommate_dict.keys()))
    if st.button("Remove Roommate"):
        roommate_id = roommate_dict[selected]

        # Optional: Check if the roommate has paid any expenses before deleting
        expenses_check = conn.execute("SELECT COUNT(*) FROM expenses WHERE paid_by = (SELECT name FROM roommates WHERE id=?)", (roommate_id,)).fetchone()[0]
        if expenses_check > 0:
            st.error("Cannot remove roommate with existing expense records. Please delete their expenses first.")
        else:
            conn.execute("DELETE FROM roommates WHERE id=?", (roommate_id,))
            conn.commit()
            st.success("Roommate removed successfully.")

conn.close()
