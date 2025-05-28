import streamlit as st
import random
import json
import os
from fpdf import FPDF
import requests
from PIL import Image
from io import BytesIO

# Bestand voor opslag
DATA_FILE = "oefeningen_data.json"

# Laad oefeningen uit bestand of gebruik standaard
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        oefeningen_db = json.load(f)
else:
    oefeningen_db = [
        {"id": 1, "sport": "hockey", "leeftijdscategorie": "U12", "categorie": "techniek",
         "instructie": "Dribbel met bal in slalom tussen pionnen.", "materiaal": "6 pylonen, 1 bal per speler",
         "afbeelding_url": "https://example.com/slalom.png", "duur_minuten": 10},
        {"id": 2, "sport": "voetbal", "leeftijdscategorie": "U10", "categorie": "conditie",
         "instructie": "Sprint afstanden van 10, 20 en 30 meter.", "materiaal": "Pionnen, stopwatch",
         "afbeelding_url": "https://example.com/sprint.png", "duur_minuten": 8},
        {"id": 3, "sport": "hockey", "leeftijdscategorie": "U12", "categorie": "passing",
         "instructie": "Oefen push-passes met tweetallen op 10 meter afstand.", "materiaal": "2 ballen, 4 pylonen",
         "afbeelding_url": "https://example.com/pushpass.png", "duur_minuten": 10},
    ]

# Zoek oefeningen op basis van leeftijd en sport
def zoek_oefeningen(leeftijd, sport):
    return [o for o in oefeningen_db if o["leeftijdscategorie"] == leeftijd and o["sport"] == sport]

# Selecteer willekeurige oefeningen
def selecteer_gevarieerd(oefeningen, aantal):
    random.shuffle(oefeningen)
    return oefeningen[:aantal]

# Genereer schema voor één week
def genereer_schema_voor_week(leeftijd, sport, oef_count, tijd_per_oefening, aantal_trainingen):
    oefeningen = zoek_oefeningen(leeftijd, sport)
    schema_per_week = {}
    for training_nr in range(1, aantal_trainingen + 1):
        gekozen = selecteer_gevarieerd(oefeningen, oef_count)
        schema = []
        for i, oef in enumerate(gekozen, 1):
            schema.append({
                "training": f"Training {training_nr} - Oefening {i}",
                "instructie": oef["instructie"],
                "materiaal": oef["materiaal"],
                "duur": tijd_per_oefening,
                "afbeelding": oef["afbeelding_url"]
            })
        schema_per_week[f"Training {training_nr}"] = schema
    return schema_per_week

# Genereer PDF inclusief afbeeldingen
def genereer_pdf(schema):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Trainingsschema", ln=True, align='C')
    pdf.set_font("Arial", size=12)

    for training, oefeningen in schema.items():
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=training, ln=True)
        for oef in oefeningen:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 8, txt=oef['training'], ln=True)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 8, txt=f"Instructie: {oef['instructie']}\nMateriaal: {oef['materiaal']}\nDuur: {oef['duur']} minuten")
            # Voeg afbeelding toe
            try:
                response = requests.get(oef['afbeelding'])
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    image_path = f"temp_{oef['training'].replace(' ', '_')}.jpg"
                    image.save(image_path)
                    pdf.image(image_path, w=80)
                    os.remove(image_path)
            except:
                pass
            pdf.ln(2)
    output_file = "trainingsschema_week.pdf"
    pdf.output(output_file)
    return output_file

# Streamlit Webinterface
st.title("Dynamische Trainingsschema Generator")

st.header("Trainingsparameters")
sport = st.selectbox("Kies sport", ["hockey", "voetbal"])
leeftijd = st.selectbox("Kies leeftijdscategorie", ["U10", "U12"])
aantal_trainingen = st.slider("Aantal trainingen per week", 1, 5, 2)
aantal_oefeningen = st.slider("Aantal oefeningen per training", 1, 5, 2)
tijd_per_oef = st.slider("Tijd per oefening (min)", 5, 20, 10)

if st.button("Genereer schema voor deze week"):
    schema = genereer_schema_voor_week(leeftijd, sport, aantal_oefeningen, tijd_per_oef, aantal_trainingen)
    st.subheader("Trainingsschema voor deze week")
    for training, oefeningen in schema.items():
        st.markdown(f"## {training}")
        for oef in oefeningen:
            st.markdown(f"**{oef['training']}**")
            st.image(oef['afbeelding'], width=300)
            st.markdown(f"📋 Instructie: {oef['instructie']}")
            st.markdown(f"🧰 Materiaal: {oef['materiaal']}")
            st.markdown(f"⏱️ Duur: {oef['duur']} minuten")
            st.markdown("---")
    pdf_bestand = genereer_pdf(schema)
    with open(pdf_bestand, "rb") as f:
        st.download_button("📄 Download PDF", f, file_name=pdf_bestand)

# Oefening Editor
st.header("Voeg een nieuwe oefening toe")
with st.form("oefening_form"):
    nieuwe_id = max([o["id"] for o in oefeningen_db]) + 1 if oefeningen_db else 1
    nieuwe_sport = st.selectbox("Sport", ["hockey", "voetbal"], key="sport")
    nieuwe_leeftijd = st.selectbox("Leeftijdscategorie", ["U10", "U12"], key="leeftijd")
    nieuwe_categorie = st.text_input("Categorie (bv. techniek, conditie)")
    nieuwe_instructie = st.text_area("Instructie")
    nieuwe_materiaal = st.text_area("Materiaal")
    nieuwe_afbeelding = st.text_input("Afbeelding URL")
    nieuwe_duur = st.slider("Duur (minuten)", 5, 20, 10, key="duur")
    submitted = st.form_submit_button("Voeg oefening toe")
    if submitted:
        nieuwe_oefening = {
            "id": nieuwe_id,
            "sport": nieuwe_sport,
            "leeftijdscategorie": nieuwe_leeftijd,
            "categorie": nieuwe_categorie,
            "instructie": nieuwe_instructie,
            "materiaal": nieuwe_materiaal,
            "afbeelding_url": nieuwe_afbeelding,
            "duur_minuten": nieuwe_duur
        }
        oefeningen_db.append(nieuwe_oefening)
        with open(DATA_FILE, "w") as f:
            json.dump(oefeningen_db, f, indent=2)
        st.success(f"Oefening {nieuwe_id} toegevoegd!")
<gebruik de huidige code uit het canvas hier>
