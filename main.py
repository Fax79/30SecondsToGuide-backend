import os
import re
import urllib.parse
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from weasyprint import HTML
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# ==========================================
# CONSTANTS & AFFILIATE LINKS (DAL TUO FILE)
# ==========================================
GUIDE_APP_URL = "https://www.30secondstoguide.it" 
FLIGHT_LINK = "https://kiwi.tpx.lt/k6iWGXOK"
LUGGAGE_LINK = "https://radicalstorage.tpx.lt/fpjMovNW"
REIMB_LINK = "https://airhelp.tpx.lt/YS9ciIsW"
ESIM_LINK = "https://go.saily.site/aff_c?offer_id=101&aff_id=13541&source=WIZARD"
RENTAL_LINK = "https://clk.tradedoubler.com/click?p=284745&a=3480952"
TRANSF_LINK = "https://tpx.lt/O5I4OrpX"
TAXI_LINK = "https://kiwitaxi.tpx.lt/KCeVs32Q"
TIQETS_LINK = "https://www.tiqets.com/?partner=30secondstoguide.it-185728"
INSURANCE_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=WIZARD&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"
TRAIN_LINK = "https://clk.tradedoubler.com/click?a(3480952)p(376991)ttid(13)url(https://www.thetrainline.com/it/porta-un-amico?situation=td-it&utm_source=td-it)"
GYG_LINK = "https://gyg.me/YAGbtbpK"
HOTEL_LINK = "https://www.expedia.com"
TOUR_LINK = "https://www.getyourguide.com"

# --- DIZIONARI LINGUA ---
LANGUAGES = {
    "IT": {
        "subtitle": "Il pianificatore di viaggi complessi con analisi del budget.",
        "info_box": "🧙‍♂️ Inserisci i dettagli per ricevere un Travel Plan completo.",
        "label_dest": "Destinazione (Città/Regione/Paese)",
        "place_dest": "Es. New York, Provenza, Giappone...",
        "label_budget": "Budget Totale (€)",
        "label_start": "Data Partenza",
        "label_end": "Data Ritorno",
        "label_adults": "Numero Adulti",
        "label_kids": "Numero Minorenni",
        "label_ages": "Età figlio",
        "label_desc": "Descrizione del viaggio (Opzionale)",
        "place_desc": "Es. Partenza da Milano, voglio fare scalo a Dubai. Mi interessano musei e trekking...",
        "help_desc": "Dettagli extra per l'AI.",
        "btn_generate": "✨ Crea il mio Travel Plan",
        "btn_download": "📥 SCARICA IL TRAVEL PLAN (PDF)",
        "msg_success": "✅ Travel Plan pronto!",
        "msg_warning_dest": "Inserisci una destinazione!",
        "msg_warning_long": "⚠️ Il viaggio è troppo lungo ({days} notti). Il limite massimo è di 40 notti.",
        "msg_warning_short": "⚠️ Hai scelto un periodo di una sola notte, verifica se è corretta la Data Ritorno.",
        "spinner": "🧙‍♂️ Sto elaborando il Travel Plan per {dest}...",
        "months": {1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile", 5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto", 9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"},
        "pax_adults": "Adults", # Preso dal tuo codice
        "pax_kids": "Ragazzi",
        "pdf_title": "Travel Plan Esclusivo",
        "pdf_generated": "GENERATO CON www.30secondstoguide.it",
        "pdf_promo": "Approfondisci la conoscenza delle città del tuo itinerario, crea le tue guide qui.",
        "pdf_travellers": "Viaggiatori",
        "pdf_date": "Date",
        "pdf_budget_target": "Budget Target",
        "pdf_page": "Pagina",
        "pdf_seen": "Già visti nella guida...",
        "pdf_others": "ALTRI SERVIZI INDISPENSABILI",
        "key_chapter": "CAPITOLO",
        "key_verdict": "VERDETTO",
        "key_day": "GIORNO",
        "ad_flight": "In {month} i prezzi aumentano? Inizia a monitorare ORA i migliori prezzi su Kiwi.com",
        "ad_esim": "eSim Saily: Internet immediato all'arrivo senza acquisto di SIM locali. 5$ di sconto con codice FABIOI3455",
        "ad_insur": "MAI senza Assicurazione Sanitaria: Clicca e sblocca il 10% DI SCONTO con Heymondo",
        "ad_hotel": "Stanze in Hotel quasi esaurite in {month}? Prenota ora su Expedia",
        "ad_transfer": "Transfer privati ad un prezzo WOW! da e per l'aeroporto",
        "ad_tiqets": "Non rischiare il tutto esaurito a {dest}. Assicurati il posto e le migliori offerte su Tiqets",
        "ad_car": "Viaggia in libertà e noleggia un auto: Tariffe esclusive con Sixt",
        "ad_train": "Treni: Prenota su Trainline",
        "ad_rest": "Esplora al miglior prezzo! Prenota su GetYourGuide",
        "sb_book": "✈️ PRENOTAZIONI",
        "sb_exp": "🎟️ ESPERIENZE & ALTRO",
        "sb_tools": "🛠️ SERVIZI UTILI",
        "footer_title": "Come funziona Itinerary Wizard?",
        "footer_text": "Strumento di <strong>30SecondsToGuide</strong> per pianificare viaggi complessi analizzando il budget. Gratuito al 100%."
    },
    "EN": {
        "subtitle": "The complex trip planner with budget analysis.",
        "info_box": "🧙‍♂️ Enter details to receive a full Travel Plan.",
        "label_dest": "Destination (City/Region/Country)",
        "place_dest": "E.g. New York, Provence, Japan...",
        "label_budget": "Total Budget (€)",
        "label_start": "Departure Date",
        "label_end": "Return Date",
        "label_adults": "Adults",
        "label_kids": "Minors",
        "label_ages": "Age child",
        "label_desc": "Trip Description (Optional)",
        "place_desc": "E.g. Departing from London, want a layover in Dubai. Interested in museums and hiking...",
        "help_desc": "Extra details for AI.",
        "btn_generate": "✨ Create my Travel Plan",
        "btn_download": "📥 DOWNLOAD TRAVEL PLAN (PDF)",
        "msg_success": "✅ Travel Plan ready!",
        "msg_warning_dest": "Please enter a destination!",
        "msg_warning_long": "⚠️ Trip is too long ({days} nights). Maximum limit is 40 nights.",
        "msg_warning_short": "⚠️ You chose a single night trip, check if Return Date is correct.",
        "spinner": "🧙‍♂️ Processing Travel Plan for {dest}...",
        "months": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"},
        "pax_adults": "Adults",
        "pax_kids": "Teens/Kids",
        "pdf_title": "Exclusive Travel Plan",
        "pdf_generated": "GENERATED WITH www.30secondstoguide.it",
        "pdf_promo": "Deepen your knowledge of the cities in your itinerary, create your guides here.",
        "pdf_travellers": "Travelers",
        "pdf_date": "Dates",
        "pdf_budget_target": "Target Budget",
        "pdf_page": "Page",
        "pdf_seen": "Featured in this guide...",
        "pdf_others": "ESSENTIAL SERVICES",
        "key_chapter": "CHAPTER",
        "key_verdict": "VERDICT",
        "key_day": "DAY",
        "ad_flight": "Prices rising in {month}? Book now on Kiwi.com",
        "ad_esim": "eSim Saily: Instant internet on arrival without buying local SIMs",
        "ad_insur": "NEVER without Health Insurance: Get 10% off HERE with Heymondo",
        "ad_hotel": "Hotel rooms almost sold out in {month}? Book now on Expedia",
        "ad_transfer": "Private transfers at WOW prices! to and from the airport",
        "ad_tiqets": "Don't risk sold out in {dest}. Secure spots and best deals on Tiqets",
        "ad_car": "Travel freely and rent a car: Exclusive rates with Sixt",
        "ad_train": "Trains: Book on Trainline",
        "ad_rest": "Discover at the best rate! Book on GetYourGuide",
        "sb_book": "✈️ BOOKINGS",
        "sb_exp": "🎟️ EXPERIENCES & MORE",
        "sb_tools": "🛠️ USEFUL SERVICES",
        "footer_title": "How does Itinerary Wizard work?",
        "footer_text": "Tool by <strong>30SecondsToGuide</strong> to plan complex trips analyzing the budget. 100% Free."
    }
}

def inject_gyg_links(text_line, dest_name):
    tour_matches = re.findall(r'\[TOUR:\s*(.*?)\]', text_line)
    for tour in tour_matches:
        query_string = f"{tour} {dest_name}"
        query_encoded = urllib.parse.quote(query_string)
        search_link = f"https://www.getyourguide.it/s?q={query_encoded}&partner_id=UR2ZJHB&utm_medium=online_publisher"
        html_link = f"<a href='{search_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>{tour}</a>"
        text_line = text_line.replace(f"[TOUR: {tour}]", html_link)
    return text_line

def create_complex_pdf(text, destination, meta_data, lang_code):
    ui = LANGUAGES[lang_code]

    def clean_text_for_pdf(text_input):
        if not text_input: return ""
        text_input = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text_input)
        return text_input

    dest_clean = clean_text_for_pdf(destination)
    month_clean = clean_text_for_pdf(meta_data.get('month_name', ''))

    city_upper = dest_clean.strip().upper()
    if len(city_upper) > 24:
        city_upper = city_upper[:21] + "..."
    if 12 < len(city_upper) <= 24 and " " in city_upper:
        words = city_upper.split()
        mid = len(words) // 2
        line1, line2 = " ".join(words[:mid]), " ".join(words[mid:])
        html_city = f"{line1}<br>{line2[:-1]}<span class='last-letter-dot'>{line2[-1]}.</span>"
    else:
        html_city = f"{city_upper[:-1]}<span class='last-letter-dot'>{city_upper[-1]}.</span>"

    formatted_body = ""
    lines = text.split('\n')
    inserted_ch1 = inserted_ch2 = inserted_ch3 = inserted_ch4 = False

    TRIGGER_CH = f"## {ui['key_chapter']}"
    TRIGGER_VERDICT = ui['key_verdict']

    def make_html_box(link, cta, sub):
        cta_html = f"{cta[:-1]}<span style='color: #1a1a1a;'>{cta[-1]}</span>"
        return f"""
        <div class="section-service-box">
            <span class="service-tag">LINK UTILI PER IL TUO VIAGGIO</span>
            <a href="{link}" target="_blank" class="service-cta">{cta_html}</a>
            <div class="service-sub">{sub}</div>
        </div>
        """

    for line in lines:
        clean_line = clean_text_for_pdf(line.strip())
        
        heymondo_link = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=WIZARDCONTEXT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"
        heymondo_html = f"<a href='{heymondo_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Heymondo</a>"
        clean_line = re.sub(r'\bHeymondo\b', heymondo_html, clean_line, flags=re.IGNORECASE)

        kiwi_link = "https://kiwi.tpx.lt/k6iWGXOK"
        kiwi_html = f"<a href='{kiwi_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Kiwi</a>"
        clean_line = re.sub(r'\bKiwi(?:\.com)?\b', kiwi_html, clean_line, flags=re.IGNORECASE)
        
        saily_link = "https://go.saily.site/aff_c?offer_id=101&aff_id=13541&source=WIZARDTEXT"
        saily_html = f"<a href='{saily_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Saily</a>"
        clean_line = re.sub(r'\bSaily\b', saily_html, clean_line, flags=re.IGNORECASE)

        treno_link = "https://clk.tradedoubler.com/click?a(3480952)p(376991)ttid(13)url(https://www.thetrainline.com/it/porta-un-amico?situation=td-it&utm_source=td-it)"
        treno_html = f"<a href='{treno_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>treno</a>"
        clean_line = re.sub(r'\btreno\b', treno_html, clean_line, flags=re.IGNORECASE)
        
        clean_line = inject_gyg_links(clean_line, destination)
        
        if not clean_line:
            continue
        line_upper = clean_line.upper()
        
        if f"{TRIGGER_CH} 2" in line_upper and not inserted_ch1:
            formatted_body += make_html_box(FLIGHT_LINK, "FLIGHTS", ui["ad_flight"].format(month=month_clean))
            formatted_body += make_html_box(ESIM_LINK, "INTERNET", ui["ad_esim"])
            formatted_body += make_html_box(INSURANCE_LINK, "INSURANCE", ui["ad_insur"])
            inserted_ch1 = True
        elif f"{TRIGGER_CH} 3" in line_upper and not inserted_ch2:
            formatted_body += make_html_box(HOTEL_LINK, "HOTEL", ui["ad_hotel"].format(month=month_clean))
            formatted_body += make_html_box(TRANSF_LINK, "TRANSFER", ui["ad_transfer"])
            inserted_ch2 = True
        elif f"{TRIGGER_CH} 4" in line_upper and not inserted_ch3:
            formatted_body += make_html_box(TIQETS_LINK, "TICKETS", ui["ad_tiqets"].format(dest=dest_clean))
            formatted_body += make_html_box(RENTAL_LINK, "RENTAL CAR", ui["ad_car"])
            formatted_body += make_html_box(TRAIN_LINK, "TRAIN", ui["ad_train"])
            inserted_ch3 = True
        elif f"{TRIGGER_CH} 5" in line_upper and not inserted_ch4:
            formatted_body += make_html_box(GYG_LINK, "TOURS", ui["ad_rest"])
            inserted_ch4 = True

        if clean_line.startswith('## '):
            formatted_body += f"<h2 class='h2-title'>{clean_line.replace('## ', '')}</h2>"
        elif clean_line.startswith('### '):
            formatted_body += f"<h3 class='h3-title'>{clean_line.replace('### ', '')}</h3>"
        elif TRIGGER_VERDICT in line_upper:
            verdict_text = clean_line.replace('#', '').strip()
            formatted_body += f"<div class='verdict-box'>{verdict_text}</div>"
        elif clean_line.startswith('* ') or clean_line.startswith('- '):
            formatted_body += f"<li>{clean_line[2:]}</li>"
        elif re.match(r'^\d+\.', clean_line):
            formatted_body += f"<p><strong>{clean_line}</strong></p>"
        elif clean_line.startswith('# '):
            continue 
        else:
            formatted_body += f"<p>{clean_line}</p>"

    html_template = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 25mm 20mm 30mm 20mm;
                background-color: #faf9f6;
                background-image: 
                    linear-gradient(rgba(26, 26, 26, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(26, 26, 26, 0.03) 1px, transparent 1px);
                background-size: 40px 40px;

                @bottom-left {{
                    content: "30SecondsToGuide";
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 14px;
                    font-weight: 800;
                    color: #e67e22;
                    padding-bottom: 5mm;
                }}
                @bottom-right {{
                    content: "{ui['pdf_generated']}";
                    font-family: monospace;
                    font-size: 11px;
                    color: #1a1a1a;
                    opacity: 0.8;
                    padding-bottom: 5mm;
                }}
            }}

            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #1a1a1a;
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }}

            .cover-container {{
                page-break-after: always;
                position: relative;
                padding-top: 80px;
            }}
            .design-accent-l {{
                position: absolute;
                top: 40px; left: -15px;
                width: 120px; height: 200px;
                border-top: 12px solid #1a1a1a;
                border-left: 12px solid #1a1a1a;
                z-index: -1;
            }}
            .category-label {{
                font-size: 13px; font-weight: 800; letter-spacing: 5px;
                text-transform: uppercase; margin-bottom: 12px;
                background: #faf9f6; display: inline-block; padding-right: 10px;
            }}
            .city-name {{
                font-size: 65px; font-weight: 900; text-transform: uppercase;
                margin: 0; line-height: 0.95; letter-spacing: -2px;
                color: #e67e22;
            }}
            .last-letter-dot {{ color: #1a1a1a; }}
            
            .description-box {{
                margin-top: 145px; padding: 25px; background-color: #ffffff;
                border-left: 4px solid #1a1a1a; max-width: 460px; font-size: 14px;
                color: #555; box-shadow: 8px 8px 0px rgba(26, 26, 26, 0.05);
            }}

            .content-container {{
                page-break-after: always;
            }}
            .h2-title {{
                text-transform: uppercase; font-weight: 900; letter-spacing: -1px;
                color: #e67e22; margin-top: 40px; margin-bottom: 15px; border-bottom: 2px solid #1a1a1a; display: inline-block;
                page-break-after: avoid; 
            }}
            .h3-title {{ 
                font-weight: 800; color: #1a1a1a; margin-top: 30px; margin-bottom: 10px; 
                page-break-after: avoid; 
            }}
            p, li {{ font-size: 14px; color: #333; margin-bottom: 10px; text-align: justify; }}
            li {{ margin-left: 20px; }}
            strong {{ color: #000000; font-weight: bold; }}

            .verdict-box {{
                margin: 30px 0; padding: 15px; background-color: #f8f9fa; 
                border-left: 5px solid #e67e22; font-weight: bold; color: #2c3e50;
            }}

            .section-service-box {{
                margin: 40px 0px; padding: 25px; position: relative;
                background-color: #ffffff;
                border: 1px solid rgba(26, 26, 26, 0.08);
                box-shadow: 8px 8px 0px rgba(26, 26, 26, 0.05);
                page-break-inside: avoid;
            }}
            .section-service-box::before {{
                content: ""; position: absolute; top: -6px; left: -6px;
                width: 40px; height: 40px;
                border-top: 8px solid #1a1a1a; border-left: 8px solid #1a1a1a;
            }}
            .service-tag {{
                font-size: 11px; font-weight: 800; letter-spacing: 4px;
                text-transform: uppercase; color: #1a1a1a; display: block; margin-bottom: 10px;
            }}
            .service-cta {{
                font-size: 30px; font-weight: 900; text-transform: uppercase;
                color: #e67e22; text-decoration: none; letter-spacing: -1.5px; line-height: 1; display: block;
            }}
            .service-cta::after {{ content: "."; color: #1a1a1a; }}
            .service-sub {{ font-size: 13px; color: #7f8c8d; margin-top: 8px; font-weight: 400; }}

        </style>
    </head>
    <body>

        <div class="cover-container">
            <div class="design-accent-l"></div>
            <div class="category-label">{ui['pdf_title']}</div>
            <h1 class="city-name">{html_city}</h1>
            <div class="description-box">
                <strong>{ui['pdf_date']}:</strong> {meta_data['dates']}<br>
                <strong>{ui['pdf_travellers']}:</strong> {meta_data['pax']}<br>
                <strong>{ui['pdf_budget_target']}:</strong> {meta_data['budget']}
            </div>
            
            <div style="margin-top: 60px; text-align: center;">
                <a href="{GUIDE_APP_URL}" style="display:inline-block; padding:15px 25px; background-color:#e67e22; color:white; text-decoration:none; font-weight:bold; border-radius:5px;">
                    {ui['pdf_promo']}
                </a>
            </div>
        </div>

        <div class="content-container">
            {formatted_body}
        </div>

    </body>
    </html>
    """
    return HTML(string=html_template).write_pdf()

# ==========================================
# FASTAPI ENGINE
# ==========================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

class TravelData(BaseModel):
    origin: str
    destination: str
    startDate: str
    endDate: str
    adults: int
    kids: int
    kidsAges: list[int]
    description: str
    budget: int
    lang_code: str = "IT" # Predisposto per il Multi-Lingua se dovesse servire

@app.post("/genera-pdf")
async def generate_pdf(data: TravelData):
    try:
        # Calcolo date e durata
        start_date = datetime.datetime.strptime(data.startDate, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(data.endDate, "%Y-%m-%d").date()
        duration_check = (end_date - start_date).days

        ui = LANGUAGES.get(data.lang_code, LANGUAGES["IT"])
        current_months = ui["months"]
        mese_partenza = current_months[start_date.month]

        pax_desc = f"{data.adults} {ui['pax_adults']}"
        if data.kids > 0: 
            kids_ages_str = ', '.join(map(str, data.kidsAges))
            pax_desc += f", {data.kids} {ui['pax_kids']} ({kids_ages_str})"

        model = genai.GenerativeModel("gemini-2.5-flash")

        if data.lang_code == "IT":
            sys_prompt = "Agisci come un Travel Planner Senior. Non pianifichi solo un viaggio, pianifichi un viaggio su misura che massimizza il valore del budget."
            rules_lang = "Usa SOLO l'alfabeto Latino/Italiano. Quando suggerisci un'escursione, un'attrazione, un tour o un museo specifico, SOLO E SOLTANTO SE SEI RAGIONEVOLMENTE CERTO CHE SI POSSA PRENOTARE TRAMITE GETYOURGUIDE ALLORA devi racchiudere il nome ESATTAMENTE in questo tag: [TOUR: Nome Attrazione]. Esempio: Ti consiglio di visitare il [TOUR: Colosseo]."
            structure = f"""
            # {data.destination.upper()}: [Sottotitolo]
            **IL VERDETTO SUL BUDGET: € {data.budget}** (Stato: Lusso/Più che adeguato/Sufficiente/Stretto/Impossibile)
            ## CAPITOLO 1: LA PREPARAZIONE (Voli, eSim, Assicurazione)
            [Info trasporti ottimizza orari dei voli consultando dove possibile google flights se hai informazioni sulla città di partenza, reperisci gli ultimi prezzi da google flight se hai date precise e suggerisci Kiwi per la prenotazione sfruttando i travel hack. ATTENZIONE ALLA COERENZA CON LA DATA ODIERNA RISPETTO AI SUGGERIMENTI CHE DAI (es. se il volo è tra un mese non sugggerire di prenotare 6 mesi prima). Utilizza il mezzo di trasporto più razionale in linea con la durata del viaggio, il budget e se ci sono possiblità concrete di utilizzare mezzi alternativi all'aereo. Come eSim consiglia sempre Saily (NON per Italia/UE dove esiste roaming as at home), per l'assicurazione Heymondo con sconto 10%]
            ## CAPITOLO 2: DOVE DORMIRE (Strategie alloggio)
            ## CAPITOLO 3: L'ITINERARIO GIORNO PER GIORNO (Dettagliato)
            [Itinerario ottimizzato, razionalizza gli spostamenti in base alla distanza, a seconda del mezzo di trasporto massimizza le tappe con il tempo a disposizione. Prediligi attrazioni su Tiqets e Getyourguide. Scoperta del territorio]
            ## CAPITOLO 4: COSA MANGIARE
            [Piatti tipici, ristoranti (verifica su Tripadvisor i migliori per la fascia di prezzo compatibile con il budget e dai riferimenti puntuali), suggerisci i posti migliori per lo street food]
            ## CAPITOLO 5: CALENDARIO CULTURALE
            [Festival e ricorrenze]
            ## CAPITOLO 6: CONTO ECONOMICO FINALE [includi sempre Voli internazionali se il viaggio li necessita per la stima del budget]
            ## CAPITOLO 7: INFORMAZIONI PRATICHE
            ## CAPITOLO 8: CONCLUSIONE
            """
        else:
            sys_prompt = "Act as a Senior Travel Planner. You don't just plan a trip, you plan a tailor-made trip that maximizes budget value."
            rules_lang = "Use ONLY Latin/English alphabet. When you suggest a specific excursion, attraction, tour, or museum, you MUST enclose the name EXACTLY in this tag: [TOUR: Attraction Name]. Example: I recommend visiting the [TOUR: Colosseum]."
            structure = f"""
            # {data.destination.upper()}: [Subtitle]
            **THE VERDICT ON BUDGET: € {data.budget}** (Status: Luxury/More than adequate/Sufficient/Tight/Impossible)
            ## CHAPTER 1: PREPARATION (Flights, eSim, Insurance)
            [Transport info, Saily eSim, Heymondo insurance 10% off]
            ## CHAPTER 2: WHERE TO SLEEP (Accommodation strategies)
            ## CHAPTER 3: DAY BY DAY ITINERARY (Detailed)
            ## CHAPTER 4: WHAT TO EAT
            ## CHAPTER 5: CULTURAL CALENDAR
            ## CHAPTER 6: FINAL FINANCIAL BREAKDOWN
            ## CHAPTER 7: PRACTICAL INFORMATION
            ## CHAPTER 8: CONCLUSION
            """

        prompt = f"""
        {sys_prompt}
        Razionalizza il tempo, visita quanti più posti possibili con {duration_check} notti a disposizione.
        Valuta la densità degli impegni giornalieri perché siano fattibili. Presta attenzione ad essere razionale negli spostamenti per massimizzare il tempo a disposizione.
        Tieni conto delle NOTE UTENTE per personalizzare l'esperienza, ma NON ripeterle esplicitamente.
        Crea un "Travel Plan" esclusivo per: {data.destination}.
        
        DATI:
        - Durata: {duration_check} notti ({start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')})
        - Gruppo: {pax_desc}
        - Budget: € {data.budget}
        - NOTE UTENTE: {data.description if data.description else "Nessuna nota"}
        
        REGOLE TASSATIVE:
        1. {rules_lang} 2. TRASLITTERA i nomi locali. 3. Simboli Valute: EUR, USD.
        4. USA intelligentemente il grassetto markdown (**) per evidenziare i giorni (es. **Giorno 1:**), i nomi dei luoghi, degli hotel, delle attrazioni e dei ristoranti, per rendere la lettura del documento molto più facile e scansionabile.
        5. VIETATO USARE LISTE ANNIDATE. 6. PREZZI IN EURO CON SEPARATORE MIGLIAIA.
        7. USA DURATA {duration_check}, non ricalcolare. 8. NON SCRIVERE I TUOI PENSIERI INTERNI.
        
        STRUTTURA TITOLI (Usa ESATTAMENTE questi):
        {structure}
        """

        response = model.generate_content(prompt)
        
        meta_data = {
            "dates": f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m/%Y')}", 
            "pax": pax_desc, 
            "budget": f"EUR {data.budget}", 
            "month_name": mese_partenza
        }

        pdf_bytes = create_complex_pdf(response.text, data.destination, meta_data, data.lang_code)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Itinerary_{data.destination.replace(' ', '_')}.pdf"
            }
        )

    except Exception as e:
        print(f"Errore: {e}")
        raise HTTPException(status_code=500, detail=str(e))
