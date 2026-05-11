import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile
import io
import re
import os
import json
from itertools import combinations
from collections import Counter

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="1821GBFR · Greek Revolution Press Corpus",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# 🌍 MULTILINGUAL UI
# ==========================================
LANG_UI = {
    "EL": {
        "nav_title": "🏛️ 1821GBFR: Γαλλοβρετανικό Corpus Τύπου για την Ελληνική Επανάσταση, 1821–1832",
        "active_corpus": "Ενεργό Corpus",
        "filters_header": "🎛️ Φίλτρα",
        "filter_country": "Χώρες:",
        "filter_period": "Περίοδος:",
        "tab_overview": "📊 Επισκόπηση",
        "tab_press": "📰 Εκδοτικό Τοπίο",
        "tab_topics": "🧠 Θεματολογία",
        "tab_flows": "🌍 Ροές & Χάρτης",
        "tab_entities": "👥 Οντότητες",
        "tab_cooc": "🕸️ Συν-εμφάνιση",
        "tab_waves": "🌊 Κύματα Ειδήσεων",
        "tab_wavemap": "🗺️ Χρονική Κυκλοφορία",
        "tab_emotions": "🎭 Συναισθήματα",
        "tab_geo_emo": "🌍 Συναισθηματική Γεωγραφία",
        "metric_articles": "Συνολικά Άρθρα",
        "metric_papers": "Μοναδικοί Τίτλοι Εφημερίδων",
        "metric_total_corpus": "Σύνολο Corpus",
        "metric_directly_relevant": "Άμεσα Σχετικές Εγγραφές",
        "metric_active_dashboard": "Ενεργό Dataset Dashboard",
        "overview_caption": "Το dashboard αναλύει το directly relevant corpus. Η πίτα σχετικότητας παρουσιάζει την κατανομή του πλήρους αρχικού corpus.",
        "ov_sub": "### 🔭 Επισκόπηση του Corpus",
        "ov_relevance": "Αξιολόγηση Σχετικότητας (AI)",
        "ov_country": "Κατανομή ανά Χώρα (Ενεργό)",
        "ov_top_topics": "Top 5 Κυρίαρχα Θέματα",
        "ov_timeline": "📈 Εξέλιξη Όγκου Δημοσιεύσεων (1821–1832)",
        "press_sub": "📰 Πολιτική Γραμμή των 15 κυριότερων Εφημερίδων",
        "topics_sub": "🧠 Εξέλιξη Κυρίαρχων Θεμάτων",
        "flows_sub": "🌍 Ροές Ειδήσεων & Γεωχωρική Ανάλυση",
        "ent_sub": "👥 Ανάλυση Οντοτήτων",
        "ent_top_p": "Top 20 Πρόσωπα",
        "ent_top_l": "Top 20 Τοποθεσίες",
        "cooc_sub": "🕸️ Δίκτυο Συν-εμφάνισης Οντοτήτων",
        "cooc_note": "Κάθε κόμβος είναι μια οντότητα. Κάθε ακμή δείχνει πόσες φορές δύο οντότητες εμφανίζονται στο ίδιο άρθρο. Πάχος ακμής = συχνότητα συν-εμφάνισης.",
        "cooc_type": "Τύπος Οντοτήτων:",
        "cooc_top_n": "Αριθμός κορυφαίων οντοτήτων:",
        "cooc_min_edge": "Ελάχιστες συν-εμφανίσεις (φίλτρο ακμών):",
        "waves_sub": "🌊 Ανάλυση Ειδησεογραφικών Κυμάτων",
        "waves_note": "Η ανάλυση βασίζεται σε AI-assisted annotation εγγραφών με τεκμηριωμένο news_origin_norm. Τα αποτελέσματα είναι πειραματικά.",
        "waves_select": "Επιλογή συνόλου:",
        "waves_records": "Εγγραφές",
        "waves_newspapers": "Εφημερίδες",
        "waves_origins": "Προελεύσεις Ειδήσεων",
        "waves_rumor": "Κατάσταση Πληροφορίας",
        "waves_medium": "Μέσο Μετάδοσης",
        "waves_frame": "Ρητορικό Πλαίσιο",
        "waves_type": "Τύπος Γεγονότος",
        "waves_phase": "Φάση Ειδησεογραφικού Κύματος",
        "waves_sample": "Δείγμα εγγραφών",
        "wavemap_sub": "🗺️ Χρονική Κυκλοφορία Κυμάτων (1821–1832)",
        "wavemap_note": "Animation που δείχνει πώς αλλάζουν οι ειδησεογραφικές ροές χρόνο με χρόνο. Κάθε γραμμή είναι μια τεκμηριωμένη διαδρομή news_origin_norm → publication_place.",
        "wavemap_speed": "Ταχύτητα Animation:",
        "unknown": "Άγνωστο",
        "map_title": "Συνολικές Διαδρομές Ειδήσεων",
        "map_legend_fr": "Προς Γαλλία",
        "map_legend_gb": "Προς Βρετανία",
        "map_nodes": "Κόμβοι Πληροφορίας",
        "emo_sub": "🎭 Ανάλυση Συναισθηματικού Φορτίου",
        "emo_note": "Ανάλυση ρητορικής και συναισθηματικού φορτίου (1–10) με χρήση AI.",
        "emo_overall": "Γενικοί Μέσοι Όροι Συναισθημάτων",
        "emo_timeline": "Εξέλιξη Συναισθημάτων στον Χρόνο (1821–1832)",
        "emo_country": "Σύγκριση Συναισθημάτων: Βρετανία vs Γαλλία",
        "emo_select": "Επιλογή Συναισθήματος για Σύγκριση:",
        "geo_emo_sub": "🌍 Συναισθηματικό Αποτύπωμα Κόμβων",
        "geo_emo_note": "Σύγκριση του συναισθηματικού τόνου ανάμεσα σε κόμβους προέλευσης ειδήσεων, με πραγματικά scores από το corpus.",
    },
    "EN": {
        "nav_title": "🏛️ 1821GBFR: Franco-British Press Corpus on the Greek Revolution, 1821–1832",
        "active_corpus": "Active Corpus", "filters_header": "🎛️ Filters", "filter_country": "Countries:", "filter_period": "Period:",
        "tab_overview": "📊 Overview", "tab_press": "📰 Publishing Landscape", "tab_topics": "🧠 Topics",
        "tab_flows": "🌍 Flows & Map", "tab_entities": "👥 Entities", "tab_cooc": "🕸️ Co-occurrence",
        "tab_waves": "🌊 News Waves", "tab_wavemap": "🗺️ Temporal Circulation", "tab_emotions": "🎭 Emotions",
        "tab_geo_emo": "🌍 Emotional Geography", "metric_articles": "Total Articles", "metric_papers": "Unique Newspaper Titles",
        "metric_total_corpus": "Total Corpus", "metric_directly_relevant": "Directly Relevant Records",
        "metric_active_dashboard": "Active Dashboard Dataset",
        "overview_caption": "The dashboard analyzes the directly relevant corpus. The relevance pie chart shows the distribution of the full initial corpus.",
        "ov_sub": "### 🔭 Corpus Overview", "ov_relevance": "Relevance Assessment (AI)", "ov_country": "Distribution by Country (Active)",
        "ov_top_topics": "Top 5 Dominant Topics", "ov_timeline": "📈 Publication Volume Evolution (1821–1832)",
        "press_sub": "📰 Editorial Stance of Top 15 Newspapers", "topics_sub": "🧠 Dominant Topics Evolution",
        "flows_sub": "🌍 News Flows & Geospatial Map", "ent_sub": "👥 Entity Analysis", "ent_top_p": "Top 20 Persons",
        "ent_top_l": "Top 20 Locations", "cooc_sub": "🕸️ Entity Co-occurrence Network",
        "cooc_note": "Each node is an entity. Each edge shows how many times two entities appear in the same article.",
        "cooc_type": "Entity Type:", "cooc_top_n": "Number of top entities:", "cooc_min_edge": "Minimum co-occurrences:",
        "waves_sub": "🌊 News-Wave Analysis", "waves_note": "Analysis based on AI-assisted annotation. Results are experimental.",
        "waves_select": "Select dataset:", "waves_rumor": "Information Status", "waves_medium": "Transmission Medium",
        "waves_frame": "Rhetorical Frame", "waves_type": "Event Type", "waves_sample": "Sample records",
        "wavemap_sub": "🗺️ Temporal Circulation of News Waves (1821–1832)", "wavemap_note": "Animation showing how news flows change year by year.",
        "map_title": "Overall News Routes", "map_legend_fr": "To France", "map_legend_gb": "To Britain", "map_nodes": "Information Nodes",
        "emo_sub": "🎭 Emotional Charge Analysis", "emo_note": "Analysis of rhetorical and emotional charge (1–10) using AI.",
        "emo_overall": "Overall Emotion Means", "emo_timeline": "Evolution of Emotions over Time (1821–1832)",
        "emo_country": "Emotion Comparison: Britain vs France", "emo_select": "Select Emotion for Comparison:",
        "geo_emo_sub": "🌍 Emotional Footprint of Nodes", "geo_emo_note": "Comparison of the emotional tone between news-origin nodes, using real scores from the corpus.",
    },
    "FR": {
        "nav_title": "🏛️ 1821GBFR : Corpus franco-britannique de presse sur la Révolution grecque, 1821–1832",
        "active_corpus": "Corpus Actif", "filters_header": "🎛️ Filtres", "filter_country": "Pays:", "filter_period": "Période:",
        "tab_overview": "📊 Aperçu", "tab_press": "📰 Paysage éditorial", "tab_topics": "🧠 Thématiques",
        "tab_flows": "🌍 Flux et Carte", "tab_entities": "👥 Entités", "tab_cooc": "🕸️ Co-occurrence",
        "tab_waves": "🌊 Vagues d'information", "tab_wavemap": "🗺️ Circulation Temporelle", "tab_emotions": "🎭 Émotions",
        "tab_geo_emo": "🌍 Géographie Émotionnelle", "metric_articles": "Total des articles", "metric_papers": "Titres de journaux uniques",
        "metric_total_corpus": "Corpus total", "metric_directly_relevant": "Entrées directement pertinentes",
        "metric_active_dashboard": "Dataset actif du tableau de bord",
        "overview_caption": "Le tableau de bord analyse le corpus directement pertinent. Le graphique de pertinence présente la répartition du corpus initial complet.",
        "ov_sub": "### 🔭 Aperçu du Corpus", "ov_relevance": "Évaluation de la pertinence (IA)", "ov_country": "Répartition par pays (Actif)",
        "ov_top_topics": "Top 5 des thèmes dominants", "ov_timeline": "📈 Évolution du volume des publications (1821–1832)",
        "press_sub": "📰 Ligne politique des 15 principaux journaux", "topics_sub": "🧠 Évolution des thèmes dominants",
        "flows_sub": "🌍 Flux d'informations et Carte Géospatiale", "ent_sub": "👥 Analyse des entités", "ent_top_p": "Top 20 Personnes",
        "ent_top_l": "Top 20 Lieux", "cooc_sub": "🕸️ Réseau de co-occurrence des entités",
        "cooc_note": "Chaque nœud est une entité. Chaque arête indique combien de fois deux entités apparaissent dans le même article.",
        "cooc_type": "Type d'entité:", "cooc_top_n": "Nombre d'entités principales:", "cooc_min_edge": "Co-occurrences minimales:",
        "waves_sub": "🌊 Analyse des vagues d'information", "waves_note": "Analyse basée sur une annotation assistée par IA. Résultats expérimentaux.",
        "waves_select": "Choisir un ensemble:", "waves_rumor": "Statut de l'information", "waves_medium": "Moyen de transmission",
        "waves_frame": "Cadre rhétorique", "waves_type": "Type d'événement", "waves_sample": "Exemples d'entrées",
        "wavemap_sub": "🗺️ Circulation Temporelle des Vagues (1821–1832)", "wavemap_note": "Animation montrant comment les flux d'information évoluent d'année en année.",
        "map_title": "Itinéraires Globaux des Informations", "map_legend_fr": "Vers la France", "map_legend_gb": "Vers la Grande-Bretagne",
        "map_nodes": "Nœuds d'Information", "emo_sub": "🎭 Analyse de la Charge Émotionnelle", "emo_note": "Analyse de la charge émotionnelle (1–10) avec l'IA.",
        "emo_overall": "Moyennes Générales des Émotions", "emo_timeline": "Évolution des Émotions (1821–1832)",
        "emo_country": "Comparaison : Grande-Bretagne vs France", "emo_select": "Sélectionnez une émotion:",
        "geo_emo_sub": "🌍 Empreinte Émotionnelle des Nœuds", "geo_emo_note": "Comparaison du ton émotionnel entre différents nœuds d'origine de l'information.",
    },
}

PERSON_ALIASES = {
    'Ibrahim Pasha': ['ibrahim-pacha', 'ibrahim', 'ibrahim pacha', 'pacha of egypt', 'ibrahim pasha', 'ibrahim pascha'],
    'Ioannis Kapodistrias': ["count capo d'istria", "capo d'istria", "comte capo-d'istria", 'president of greece', 'kapodistrias'],
    'Lord Cochrane': ['lord cochrane', 'cochrane', 'thomas cochrane'],
    'Sultan Mahmud II': ['sultan', 'mahmoud', 'le sultan', 'grand-seigneur', 'mahmud', 'mahmud ii'],
    'Lord Byron': ['lord byron', 'byron'],
    'Andreas Miaoulis': ['miaulis', 'amiral miaulis', 'admiral miaulis', 'miaoulis'],
    'Theodoros Kolokotronis': ['colocotroni', 'kolokotronis', 'kolokotroni', 'colocotronis'],
    'Alexander / Demetrios Ypsilantis': ['ypsilanti', 'prince ypsilanti', 'ypsilantis'],
    'General Richard Church': ['general church', 'général church', 'church', 'richard church'],
    'Jean-Gabriel Eynard': ['m. eynard', 'eynard'],
    'Reshid Pasha': ['reschid-pacha', 'reshid', 'kiutahi'],
    'Charles Fabvier': ['colonel fabvier', 'fabvier', 'général fabvier'],
    'Duke of Wellington': ['duke of wellington', 'wellington'],
    'George Canning': ['canning', 'mr. canning', 'm. canning'],
    'Georgios Karaiskakis': ['karaiskaki', 'karaiskakis', 'goaras'],
    'Alexandros Mavrokordatos': ['maurocordato', 'mavrocordato', 'prince mavrocordato', 'condurietti'],
    'Constantine Kanaris': ['canaris', 'kanaris']
}
LOC_ALIASES = {
    'Greece': ['greece', 'grèce', 'western greece', 'eastern greece', 'grecs', 'greeks', 'greek'],
    'Ottoman Empire': ['turkey', 'turquie', 'porte', 'ottoman empire'],
    'Peloponnese (Morea)': ['morée', 'morea', 'peloponnesus', 'peloponnese', 'moree'],
    'Russia': ['russia', 'russie'],
    'Great Britain': ['london', 'londres', 'england', 'angleterre', 'great britain'],
    'France': ['france', 'paris', 'marseille', 'marseilles', 'toulon'],
    'Missolonghi': ['missolonghi', 'mesolongi', 'missolongi'],
    'Navarino': ['navarin', 'navarino'],
    'Constantinople': ['constantinople', 'istanbul'],
    'Egypt': ['egypt', 'égypte', 'egypte', 'alexandrie', 'alexandria'],
    'Nafplion': ['napoli', 'napoli de romanie', 'napoli di romania', 'nafplion'],
    'Crete': ['candie', 'candia', 'crete'],
    'Smyrna': ['smyrne', 'smyrna', 'izmir'],
    'Athens': ['athens', 'athènes']
}
CITY_COORDS = {
    "London": [51.5074, -0.1278], "Dublin": [53.3498, -6.2603], "Yorkshire": [53.9599, -1.0872],
    "Midlothian": [55.9533, -3.1883], "Lancashire": [53.7632, -2.7044], "Hampshire": [51.0577, -1.3080],
    "Durham": [54.7753, -1.5849], "Antrim": [54.7167, -6.2000], "Warwickshire": [52.2823, -1.5849],
    "Inverness-shire": [57.4778, -4.2247], "Bristol": [51.4545, -2.5879], "Edinburgh": [55.9533, -3.1883],
    "Paris": [48.8566, 2.3522], "Bordeaux": [44.8378, -0.5792], "Strasbourg": [48.5734, 7.7521],
    "Toulouse": [43.6047, 1.4442], "Montpellier": [43.6108, 3.8767], "Marseille": [43.2965, 5.3698],
    "Vienna": [48.2082, 16.3738], "Trieste": [45.6495, 13.7768], "Augsburg": [48.3705, 10.8978],
    "Odessa": [46.4825, 30.7233], "St. Petersburg": [59.9311, 30.3609], "Geneva": [46.2044, 6.1432],
    "Naples": [40.8518, 14.2681], "Livorno": [43.5485, 10.3106], "Ancona": [43.6158, 13.5189],
    "Constantinople": [41.0082, 28.9784], "Smyrna": [38.4237, 27.1428], "Alexandria": [31.2001, 29.9187],
    "Thessaloniki": [40.6401, 22.9444], "Malta": [35.9375, 14.3978],
    "Greece": [38.5, 23.5], "Morea": [37.5, 22.5], "Athens": [37.9838, 23.7275],
    "Nafplio": [37.5672, 22.7984], "Nafplion": [37.5672, 22.7984], "Missolonghi": [38.3687, 21.4286],
    "Patras": [38.2466, 21.7346], "Navarino": [36.9110, 21.6924], "Tripolitsa": [37.5108, 22.3768],
    "Corfu": [39.6243, 19.9217], "Zante": [37.7870, 20.8999], "Kefalonia": [38.2598, 20.5750],
    "Syros": [37.4415, 24.9425], "Hydra": [37.3496, 23.4682], "Chios": [38.3678, 26.1361],
}
FR_CITIES = {"Paris", "Bordeaux", "Strasbourg", "Toulouse", "Montpellier", "Marseille"}
BAD_VALUES = {'unknown', 'nan', 'none', 'άγνωστο', 'άγνωστη', 'inconnu', '[]', '', 'skipped', 'skip'}
EMOTION_ORDER = ['Fear', 'Pity', 'Heroism', 'Barbarity', 'Hope']
EMOTION_RENAME = {
    'emotion_fear': 'Fear', 'emotion_pity': 'Pity', 'emotion_heroism': 'Heroism',
    'emotion_barbarity': 'Barbarity', 'emotion_hope': 'Hope',
    'fear': 'Fear', 'pity': 'Pity', 'heroism': 'Heroism', 'barbarity': 'Barbarity', 'hope': 'Hope'
}

def fmt_int(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return str(n)

def clean_missing_series(s):
    return (
        s.fillna("").astype(str).str.strip()
        .replace({"nan": "", "NaN": "", "None": "", "none": "", "<NA>": "", "NULL": "", "null": ""})
    )

def normalize_entities(entity_str, alias_dict):
    if pd.isna(entity_str) or not isinstance(entity_str, str) or entity_str.strip() == "":
        return ""
    e_clean = re.sub(r'["\[\]]', '', entity_str)
    entities = [e.strip() for e in e_clean.split(',')]
    cleaned = []
    for e in entities:
        val = re.sub(r'\s+', ' ', e).strip()
        val_lower = val.lower().replace('\u2019', "'").replace('`', "'")
        matched = False
        for main_name, aliases in alias_dict.items():
            if val_lower in aliases:
                cleaned.append(main_name)
                matched = True
                break
        if not matched and val:
            cleaned.append(val.title())
    return ", ".join(sorted(list(set(cleaned))))

def standardize_emotion_columns(df):
    out = df.copy()
    out = out.rename(columns={c: EMOTION_RENAME.get(str(c).lower().strip(), c) for c in out.columns})
    return out

def find_sheet(xls, candidates):
    existing = {s.lower().strip(): s for s in xls.sheet_names}
    for cand in candidates:
        key = cand.lower().strip()
        if key in existing:
            return existing[key]
    for s in xls.sheet_names:
        low = s.lower().strip()
        if any(c.lower().strip() in low for c in candidates):
            return s
    return None

@st.cache_data
def load_thesis_data_v4():
    try:
        csv_path = os.path.join(BASE_DIR, "THESIS_STREAMLIT_SLIM.csv")
        df = pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)
        df.columns = df.columns.str.lower().str.strip()

        if 'newspaper_title' not in df.columns:
            possible = [c for c in df.columns if 'news' in c or 'title' in c or 'pub' in c]
            if possible:
                df = df.rename(columns={possible[0]: 'newspaper_title'})

        raw_relevance = df['ai_relevance'].value_counts() if 'ai_relevance' in df.columns else pd.Series(dtype="int64")

        if 'is_directly_relevant' in df.columns:
            df = df[df['is_directly_relevant'].astype(str).str.lower().isin(['true', '1', 'yes'])].copy()
        elif 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()

        for col in ['ai_stance', 'ai_topic']:
            if col in df.columns:
                df[col] = clean_missing_series(df[col]).replace({"": "Unknown", "unknown": "Unknown"})

        if 'country' in df.columns:
            df['country'] = df['country'].astype(str).str.strip().str.upper().replace(
                {'UK': 'GB', 'UNITED KINGDOM': 'GB', 'FRANCE': 'FR'}
            )

        if 'year_val' in df.columns:
            df['year_val'] = pd.to_numeric(df['year_val'], errors='coerce').fillna(0)
        elif 'year' in df.columns:
            df['year_val'] = pd.to_numeric(df['year'], errors='coerce').fillna(0)
        else:
            df['year_val'] = 0

        if 'date' in df.columns:
            mask = df['year_val'] == 0
            df.loc[mask, 'year_val'] = pd.to_numeric(
                df.loc[mask, 'date'].astype(str).str.extract(r'(18[23]\d)')[0],
                errors='coerce'
            ).fillna(0)

        df = df[(df['year_val'] >= 1821) & (df['year_val'] <= 1832)].copy()

        if 'entities_persons' in df.columns:
            df['entities_persons'] = df['entities_persons'].apply(lambda x: normalize_entities(x, PERSON_ALIASES))
        if 'entities_locations' in df.columns:
            df['entities_locations'] = df['entities_locations'].apply(lambda x: normalize_entities(x, LOC_ALIASES))

        for col in ['news_origin_norm', 'publication_place', 'rumor_status', 'transmission_medium',
                    'rhetorical_frame_primary', 'canonical_event_type', 'event_phase', 'story_cluster_id']:
            if col in df.columns:
                df[col] = clean_missing_series(df[col])

        for col in ['emotion_fear', 'emotion_pity', 'emotion_heroism', 'emotion_barbarity', 'emotion_hope']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df, raw_relevance
    except Exception as e:
        st.error(f"Error loading main data: {e}")
        return pd.DataFrame(), pd.Series(dtype="int64")

@st.cache_data
def load_relevance_counts():
    path = os.path.join(BASE_DIR, "relevance_counts.csv")
    if not os.path.exists(path):
        return pd.Series(dtype="int64")
    try:
        rel = pd.read_csv(path, encoding="utf-8-sig")
        rel.columns = rel.columns.str.lower().str.strip()
        if "ai_relevance" in rel.columns and "count" in rel.columns:
            return pd.Series(rel["count"].values, index=rel["ai_relevance"].astype(str))
        return pd.Series(dtype="int64")
    except Exception as e:
        st.warning(f"Could not load relevance_counts.csv: {e}")
        return pd.Series(dtype="int64")

def get_relevance_metric(raw_relevance, key):
    if raw_relevance is None or raw_relevance.empty:
        return 0
    s = raw_relevance.copy()
    s.index = s.index.astype(str).str.lower().str.strip()
    return int(s.get(key.lower().strip(), 0))

@st.cache_data
def load_waves_data():
    try:
        path = os.path.join(BASE_DIR, "news_wave_streamlit_slim.csv")
        if not os.path.exists(path):
            return pd.DataFrame()
        df = pd.read_csv(path, low_memory=False)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_waves_cards():
    try:
        with open(os.path.join(BASE_DIR, "streamlit_news_wave_cards.json"), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

@st.cache_data
def load_emotions_data():
    candidates = [
        os.path.join(BASE_DIR, "EMOTION_ANALYSIS_SUMMARY.xlsx"),
        os.path.join(BASE_DIR, "EMOTION_ANALYSIS_SUMMARY_v2.xlsx"),
    ]
    file_path = next((p for p in candidates if os.path.exists(p)), None)
    if not file_path:
        return None
    try:
        xls = pd.ExcelFile(file_path)
        sheet_overall = find_sheet(xls, ['emotion_means_overall', 'overall_means', 'means_overall'])
        sheet_by_year = find_sheet(xls, ['emotion_by_year', 'emotion_by_year_full', 'emotion_by_year_full_dr'])
        sheet_by_year_country = find_sheet(xls, ['emotion_by_year_country', 'emotion_by_country_year'])
        sheet_dom_year = find_sheet(xls, ['dominant_emotion_by_year', 'dominant_emotion_by_year_full'])
        result = {}

        if sheet_overall:
            overall = pd.read_excel(xls, sheet_overall)
            overall.columns = overall.columns.str.lower().str.strip()
            if 'emotion' not in overall.columns:
                overall = overall.rename(columns={overall.columns[0]: 'emotion'})
            if 'mean' not in overall.columns:
                numeric_cols = [c for c in overall.columns if c != 'emotion' and pd.api.types.is_numeric_dtype(overall[c])]
                if numeric_cols:
                    overall = overall.rename(columns={numeric_cols[0]: 'mean'})
            result['overall'] = overall

        if sheet_by_year:
            by_year = pd.read_excel(xls, sheet_by_year)
            by_year.columns = by_year.columns.str.strip()
            if 'year' in by_year.columns and 'year_val' not in by_year.columns:
                by_year = by_year.rename(columns={'year': 'year_val'})
            result['by_year'] = standardize_emotion_columns(by_year)

        if sheet_by_year_country:
            by_year_country = pd.read_excel(xls, sheet_by_year_country)
            by_year_country.columns = by_year_country.columns.str.strip()
            if 'year' in by_year_country.columns and 'year_val' not in by_year_country.columns:
                by_year_country = by_year_country.rename(columns={'year': 'year_val'})
            result['by_year_country'] = standardize_emotion_columns(by_year_country)

        if sheet_dom_year:
            dominant = pd.read_excel(xls, sheet_dom_year)
            dominant.columns = dominant.columns.str.strip()
            result['dominant_by_year'] = dominant

        return result if result else None
    except Exception as e:
        st.error(f"Excel read error: {e}")
        return None

@st.cache_data
def build_cooc_network(df, col, top_n=30, min_edge=3):
    if col not in df.columns:
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    pair_counts = Counter()
    for val in df[col].dropna():
        entities = [e.strip() for e in str(val).split(',') if e.strip()]
        if len(entities) >= 2:
            for a, b in combinations(sorted(set(entities)), 2):
                pair_counts[(a, b)] += 1
    if not pair_counts:
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    edges = pd.DataFrame([(a, b, w) for (a, b), w in pair_counts.items()],
                         columns=['source', 'target', 'weight'])
    all_entities = pd.concat([edges['source'], edges['target']])
    top_entities = set(all_entities.value_counts().head(top_n).index)
    edges = edges[edges['source'].isin(top_entities) & edges['target'].isin(top_entities) & (edges['weight'] >= min_edge)]
    return edges.sort_values('weight', ascending=False)

def make_cooc_figure(edges_df, title="Co-occurrence Network"):
    if edges_df.empty:
        return None
    import math
    nodes = list(set(edges_df['source'].tolist() + edges_df['target'].tolist()))
    n = len(nodes)
    angles = [2 * math.pi * i / n for i in range(n)]
    pos = {node: (math.cos(a), math.sin(a)) for node, a in zip(nodes, angles)}
    degree = {node: 0 for node in nodes}
    for _, row in edges_df.iterrows():
        degree[row['source']] += row['weight']
        degree[row['target']] += row['weight']
    max_w = edges_df['weight'].max()
    max_degree = max(degree.values()) if degree else 1
    fig = go.Figure()
    for _, row in edges_df.iterrows():
        x0, y0 = pos[row['source']]
        x1, y1 = pos[row['target']]
        width = 1 + 6 * (row['weight'] / max_w)
        opacity = 0.3 + 0.6 * (row['weight'] / max_w)
        fig.add_trace(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None], mode='lines',
            line=dict(width=width, color=f'rgba(180,140,80,{opacity:.2f})'),
            hoverinfo='skip', showlegend=False
        ))
    fig.add_trace(go.Scatter(
        x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes],
        mode='markers+text',
        marker=dict(size=[8 + 22 * (degree[n] / max_degree) for n in nodes],
                    color=[degree[n] for n in nodes], colorscale='YlOrRd',
                    showscale=True, colorbar=dict(title="Degree", thickness=12),
                    line=dict(width=1.5, color='white')),
        text=nodes, textposition='top center', textfont=dict(size=10, color='white'),
        hovertext=[f"<b>{n}</b><br>Degree: {degree[n]}" for n in nodes],
        hoverinfo='text', showlegend=False
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(color='white', size=16)),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(15,15,20,1)', paper_bgcolor='rgba(15,15,20,1)',
        height=700, margin=dict(l=20, r=20, t=60, b=20), font=dict(color='white')
    )
    return fig

@st.cache_data
def build_animated_map_data(df, c_src, c_dst):
    rows = []
    for year in range(1821, 1833):
        df_y = df[df['year_val'] == year].copy()
        df_y = df_y.dropna(subset=[c_src, c_dst])
        df_y = df_y[(~df_y[c_src].astype(str).str.lower().str.strip().isin(BAD_VALUES)) &
                    (~df_y[c_dst].astype(str).str.lower().str.strip().isin(BAD_VALUES))]
        grp = df_y.groupby([c_src, c_dst]).size().reset_index(name='weight')
        grp['year'] = year
        rows.append(grp)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()

def make_animated_map(flow_df, c_src, c_dst, ui):
    years = sorted(flow_df['year'].unique())
    frames = []
    all_lons_fr, all_lats_fr, all_lons_gb, all_lats_gb, all_node_sets = {}, {}, {}, {}, {}
    for year in years:
        df_y = flow_df[flow_df['year'] == year]
        fr_lon, fr_lat, uk_lon, uk_lat = [], [], [], []
        nodes = set()
        for _, row in df_y.iterrows():
            src, dst = str(row[c_src]).strip(), str(row[c_dst]).strip()
            if src in CITY_COORDS and dst in CITY_COORDS:
                s_lat, s_lon = CITY_COORDS[src]
                d_lat, d_lon = CITY_COORDS[dst]
                nodes.update([src, dst])
                repeats = max(1, int(row['weight'] / 5))
                if dst in FR_CITIES:
                    fr_lon.extend([s_lon, d_lon, None] * repeats)
                    fr_lat.extend([s_lat, d_lat, None] * repeats)
                else:
                    uk_lon.extend([s_lon, d_lon, None] * repeats)
                    uk_lat.extend([s_lat, d_lat, None] * repeats)
        all_lons_fr[year], all_lats_fr[year] = fr_lon, fr_lat
        all_lons_gb[year], all_lats_gb[year] = uk_lon, uk_lat
        all_node_sets[year] = nodes

    def make_traces(year):
        traces = []
        if all_lons_fr.get(year):
            traces.append(go.Scattergeo(lon=all_lons_fr[year], lat=all_lats_fr[year], mode='lines',
                                        line=dict(width=1.5, color='#ff6b6b'), opacity=0.6,
                                        name=ui['map_legend_fr'], hoverinfo='skip'))
        if all_lons_gb.get(year):
            traces.append(go.Scattergeo(lon=all_lons_gb[year], lat=all_lats_gb[year], mode='lines',
                                        line=dict(width=1.5, color='#4ecdc4'), opacity=0.6,
                                        name=ui['map_legend_gb'], hoverinfo='skip'))
        nodes = sorted(all_node_sets.get(year, set()))
        if nodes:
            traces.append(go.Scattergeo(lon=[CITY_COORDS[c][1] for c in nodes], lat=[CITY_COORDS[c][0] for c in nodes],
                                        mode='markers+text',
                                        marker=dict(size=7, color='#ffe66d', symbol='circle', line=dict(width=1, color='black')),
                                        text=nodes, textfont=dict(color='white', size=9),
                                        textposition="top center", hoverinfo='text', name=ui['map_nodes']))
        return traces

    first_year = years[0] if years else 1821
    fig = go.Figure(data=make_traces(first_year))
    fig.frames = [go.Frame(data=make_traces(year), name=str(year),
                           layout=go.Layout(title_text=f"{ui['wavemap_sub']} — {year}")) for year in years]
    steps = [dict(args=[[str(y)], {"frame": {"duration": 800, "redraw": True}, "mode": "immediate"}],
                  label=str(y), method="animate") for y in years]
    fig.update_layout(
        title=dict(text=f"{ui['wavemap_sub']} — {first_year}", font=dict(color='white', size=15)),
        showlegend=True, legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
        geo=dict(scope='world', projection_type='natural earth', showland=True, landcolor='rgb(35,35,35)',
                 showocean=True, oceancolor='rgb(15,15,30)', showcountries=True, countrycolor='rgb(70,70,70)',
                 showcoastlines=True, coastlinecolor='rgb(80,80,80)', showlakes=False,
                 bgcolor='rgba(0,0,0,0)', center=dict(lat=40, lon=20),
                 lonaxis=dict(range=[-15, 60]), lataxis=dict(range=[20, 65])),
        dragmode='zoom', paper_bgcolor='rgba(15,15,20,1)', plot_bgcolor='rgba(15,15,20,1)',
        height=650, margin=dict(l=0, r=0, t=50, b=0), font=dict(color='white'),
        updatemenus=[dict(type="buttons", showactive=False, y=0.02, x=0.5, xanchor="center",
                          buttons=[dict(label="▶ Play", method="animate",
                                        args=[None, {"frame": {"duration": 900, "redraw": True},
                                                     "fromcurrent": True, "mode": "immediate"}]),
                                   dict(label="⏸ Pause", method="animate",
                                        args=[[None], {"frame": {"duration": 0, "redraw": False},
                                                       "mode": "immediate"}])],
                          bgcolor='rgba(40,40,50,0.9)', font=dict(color='white'))],
        sliders=[dict(active=0, steps=steps, x=0.05, y=0, len=0.9,
                      currentvalue=dict(prefix="Έτος: ", font=dict(color='white')),
                      font=dict(color='white'), bgcolor='rgba(40,40,50,0.7)')]
    )
    return fig

@st.cache_data
def build_node_emotions(df):
    required = ['news_origin_norm', 'emotion_fear', 'emotion_pity', 'emotion_heroism', 'emotion_barbarity', 'emotion_hope']
    if not all(c in df.columns for c in required):
        return pd.DataFrame()
    sub = df.copy()
    sub['news_origin_norm'] = clean_missing_series(sub['news_origin_norm'])
    sub = sub[~sub['news_origin_norm'].str.lower().isin(BAD_VALUES)].copy()
    for c in required[1:]:
        sub[c] = pd.to_numeric(sub[c], errors='coerce')
    agg = sub.groupby('news_origin_norm').agg(
        records=('news_origin_norm', 'size'),
        Fear=('emotion_fear', 'mean'),
        Pity=('emotion_pity', 'mean'),
        Heroism=('emotion_heroism', 'mean'),
        Barbarity=('emotion_barbarity', 'mean'),
        Hope=('emotion_hope', 'mean')
    ).reset_index().rename(columns={'news_origin_norm': 'Node'})
    agg = agg[agg['records'] >= 20].copy()
    for c in EMOTION_ORDER:
        agg[c] = agg[c].round(3)
    return agg.sort_values('records', ascending=False)

df_main, raw_relevance = load_thesis_data_v4()
raw_relevance_full = load_relevance_counts()
if not raw_relevance_full.empty:
    raw_relevance = raw_relevance_full
df_waves = load_waves_data()
wave_cards = load_waves_cards()
dict_emotions = load_emotions_data()

if df_main.empty:
    st.error("Δεν βρέθηκε το THESIS_STREAMLIT_SLIM.csv.")
    st.stop()

st.sidebar.header("🌐 Language / Γλώσσα")
lang_choice = st.sidebar.selectbox("Select Language:", ["EL", "EN", "FR"])
ui = LANG_UI[lang_choice]

st.sidebar.divider()
st.sidebar.header(ui['filters_header'])
countries = sorted(df_main['country'].dropna().unique()) if 'country' in df_main.columns else []
sel_countries = st.sidebar.multiselect(ui['filter_country'], countries, default=countries)
v_years = df_main['year_val']
sel_years = st.sidebar.slider(ui['filter_period'], int(v_years.min()), int(v_years.max()), (int(v_years.min()), int(v_years.max())))

df_filt = df_main[(df_main['country'].isin(sel_countries)) &
                  (df_main['year_val'] >= sel_years[0]) &
                  (df_main['year_val'] <= sel_years[1])].copy()

st.sidebar.divider()
st.sidebar.markdown(f"**{ui['active_corpus']}:** `{fmt_int(len(df_filt))}` {ui['metric_articles']}")
st.sidebar.markdown(f"**Χώρες:** {', '.join(sel_countries)}")
st.sidebar.markdown(f"**Περίοδος:** {sel_years[0]}–{sel_years[1]}")

st.title(ui['nav_title'])
st.divider()

tabs = st.tabs([
    ui['tab_overview'], ui['tab_press'], ui['tab_topics'], ui['tab_flows'], ui['tab_entities'],
    ui['tab_cooc'], ui['tab_waves'], ui['tab_wavemap'], ui['tab_emotions'], ui['tab_geo_emo'],
])
t1, t2, t3, t4, t5, t6, t7, t8, t9, t10 = tabs

with t1:
    st.markdown(ui['ov_sub'])
    total_corpus = int(raw_relevance.sum()) if raw_relevance is not None and not raw_relevance.empty else len(df_main)
    directly_relevant_total = get_relevance_metric(raw_relevance, "directly_relevant")
    active_dashboard_total = len(df_filt)
    num_papers = df_filt['newspaper_title'].nunique() if 'newspaper_title' in df_filt.columns else 0
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    c_m1.metric(ui['metric_total_corpus'], fmt_int(total_corpus))
    c_m2.metric(ui['metric_directly_relevant'], fmt_int(directly_relevant_total))
    c_m3.metric(ui['metric_active_dashboard'], fmt_int(active_dashboard_total))
    c_m4.metric(ui['metric_papers'], fmt_int(num_papers))
    st.caption(ui['overview_caption'])
    st.divider()

    c_pie1, c_pie2, c_bar = st.columns(3)
    with c_pie1:
        st.markdown(f"**{ui['ov_relevance']}**")
        if raw_relevance is not None and not raw_relevance.empty:
            fig_p = px.pie(values=raw_relevance.values, names=raw_relevance.index, hole=0.4,
                           color_discrete_sequence=['#2ecc71', '#f39c12', '#e74c3c', '#95a5a6'])
            fig_p.update_traces(textposition='inside', textinfo='percent+label')
            fig_p.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10), height=320)
            st.plotly_chart(fig_p, use_container_width=True)
    with c_pie2:
        st.markdown(f"**{ui['ov_country']}**")
        if 'country' in df_filt.columns:
            df_c = df_filt['country'].value_counts().reset_index()
            df_c.columns = ['Country', 'Count']
            fig_c = px.pie(df_c, values='Count', names='Country', hole=0.4,
                           color='Country', color_discrete_map={'GB': '#1f77b4', 'FR': '#d62728'})
            fig_c.update_layout(showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=300)
            st.plotly_chart(fig_c, use_container_width=True)
    with c_bar:
        st.markdown(f"**{ui['ov_top_topics']}**")
        if 'ai_topic' in df_filt.columns:
            vt = df_filt[~df_filt['ai_topic'].str.lower().isin(['unknown', 'άγνωστο', 'inconnu', ''])]
            df_top = vt['ai_topic'].value_counts().head(5).reset_index()
            df_top.columns = ['Topic', 'Count']
            if not df_top.empty:
                fig_t = px.bar(df_top, x='Count', y='Topic', orientation='h', color_discrete_sequence=['#9b59b6'])
                fig_t.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=10,b=10,l=10,r=10), height=300)
                st.plotly_chart(fig_t, use_container_width=True)
    st.divider()
    st.markdown(f"**{ui['ov_timeline']}**")
    df_v = df_filt.groupby(['year_val', 'country']).size().reset_index(name='count')
    fig_v = px.line(df_v, x='year_val', y='count', color='country', markers=True,
                    color_discrete_map={'GB': '#1f77b4', 'FR': '#d62728'})
    fig_v.update_layout(height=400)
    st.plotly_chart(fig_v, use_container_width=True)

with t2:
    st.subheader(ui['press_sub'])
    if {'newspaper_title', 'ai_stance'}.issubset(df_filt.columns):
        df_temp = df_filt[df_filt['newspaper_title'].notna() & (df_filt['newspaper_title'] != '')]
        top_np = df_temp['newspaper_title'].value_counts().nlargest(15).index
        df_np = df_temp[df_temp['newspaper_title'].isin(top_np)].groupby(['newspaper_title', 'ai_stance']).size().reset_index(name='count')
        fig_np = px.bar(df_np, x='count', y='newspaper_title', color='ai_stance', orientation='h', height=600)
        st.plotly_chart(fig_np, use_container_width=True)

with t3:
    st.subheader(ui['topics_sub'])
    if 'ai_topic' in df_filt.columns:
        vt2 = df_filt[~df_filt['ai_topic'].str.lower().isin(['unknown', 'άγνωστο', 'inconnu', ''])]
        top_t = vt2['ai_topic'].value_counts().nlargest(10).index
        df_t = vt2[vt2['ai_topic'].isin(top_t)].groupby(['year_val', 'ai_topic']).size().reset_index(name='count')
        if not df_t.empty:
            st.plotly_chart(px.area(df_t, x='year_val', y='count', color='ai_topic', height=500), use_container_width=True)

with t4:
    st.subheader(ui['flows_sub'])
    c_src = 'news_origin_norm' if 'news_origin_norm' in df_filt.columns else None
    c_dst = 'publication_place' if 'publication_place' in df_filt.columns else None
    if c_src and c_dst:
        f_df = df_filt.dropna(subset=[c_src, c_dst])
        f_df = f_df[(~f_df[c_src].astype(str).str.lower().str.strip().isin(BAD_VALUES)) &
                    (~f_df[c_dst].astype(str).str.lower().str.strip().isin(BAD_VALUES))]
        if not f_df.empty:
            st.markdown("**1. Sankey Flow**")
            f_grp = f_df.groupby([c_src, c_dst]).size().reset_index(name='c').sort_values('c', ascending=False).head(40)
            nds = list(pd.concat([f_grp[c_src], f_grp[c_dst]]).unique())
            mapping = {n: i for i, n in enumerate(nds)}
            fig_s = go.Figure(go.Sankey(node=dict(label=nds, pad=15, thickness=20),
                                         link=dict(source=f_grp[c_src].map(mapping), target=f_grp[c_dst].map(mapping), value=f_grp['c'])))
            fig_s.update_layout(height=500)
            st.plotly_chart(fig_s, use_container_width=True)

            st.divider()
            st.markdown(f"**2. {ui['map_title']}**")
            map_data = f_df.groupby([c_src, c_dst]).size().reset_index(name='weight')
            uk_lon, uk_lat, fr_lon, fr_lat, nodes_to_plot = [], [], [], [], set()
            for _, row in map_data.iterrows():
                src, dst = str(row[c_src]).strip(), str(row[c_dst]).strip()
                if src in CITY_COORDS and dst in CITY_COORDS:
                    s_lat, s_lon = CITY_COORDS[src]; d_lat, d_lon = CITY_COORDS[dst]
                    nodes_to_plot.update([src, dst])
                    if dst in FR_CITIES:
                        fr_lon.extend([s_lon, d_lon, None]); fr_lat.extend([s_lat, d_lat, None])
                    else:
                        uk_lon.extend([s_lon, d_lon, None]); uk_lat.extend([s_lat, d_lat, None])
            fig_map = go.Figure()
            if fr_lon:
                fig_map.add_trace(go.Scattergeo(lon=fr_lon, lat=fr_lat, mode='lines', line=dict(width=1.5, color='#ff4d4d'), opacity=0.5, name=ui['map_legend_fr'], hoverinfo='skip'))
            if uk_lon:
                fig_map.add_trace(go.Scattergeo(lon=uk_lon, lat=uk_lat, mode='lines', line=dict(width=1.5, color='#3498db'), opacity=0.5, name=ui['map_legend_gb'], hoverinfo='skip'))
            if nodes_to_plot:
                nodes_sorted = sorted(nodes_to_plot)
                fig_map.add_trace(go.Scattergeo(lon=[CITY_COORDS[c][1] for c in nodes_sorted], lat=[CITY_COORDS[c][0] for c in nodes_sorted],
                                                mode='markers+text', marker=dict(size=7, color='white', symbol='circle', line=dict(width=1, color='black')),
                                                text=nodes_sorted, textfont=dict(color='white'), textposition="top center", hoverinfo='text', name=ui['map_nodes']))
            fig_map.update_layout(title_text=ui['map_title'], title_font=dict(color='white'), showlegend=True,
                                  legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                                  geo=dict(scope='world', showland=True, landcolor='rgb(35,35,35)', showocean=True, oceancolor='rgb(15,15,15)',
                                           showcountries=True, countrycolor='rgb(70,70,70)', showcoastlines=True, coastlinecolor='rgb(70,70,70)',
                                           bgcolor='rgba(0,0,0,0)'),
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=650, margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
        else:
            st.warning("No flow data after filtering unknown values.")
    else:
        st.warning("Columns news_origin_norm / publication_place not found.")

with t5:
    st.subheader(ui['ent_sub'])
    col_a, col_b = st.columns(2)
    def make_ner_chart(col_name, color, title):
        if col_name in df_filt.columns:
            data = df_filt[col_name].str.split(',').explode().str.strip().replace('', pd.NA).dropna()
            if not data.empty:
                counts = data.value_counts().head(20).reset_index()
                counts.columns = ['Entity', 'Count']
                fig = px.bar(counts, x='Count', y='Entity', orientation='h', color_discrete_sequence=[color], height=700)
                fig.update_layout(title=title, yaxis={'categoryorder': 'total ascending'})
                return fig
        return None
    chart_p = make_ner_chart('entities_persons', "#1f77b4", ui['ent_top_p'])
    chart_l = make_ner_chart('entities_locations', "#ff7f0e", ui['ent_top_l'])
    if chart_p: col_a.plotly_chart(chart_p, use_container_width=True)
    if chart_l: col_b.plotly_chart(chart_l, use_container_width=True)
    st.download_button("📥 Export filtered CSV", df_filt.to_csv(index=False).encode('utf-8'), "filtered_corpus.csv", "text/csv")

with t6:
    st.subheader(ui['cooc_sub'])
    st.info(ui['cooc_note'])
    cooc_col1, cooc_col2, cooc_col3 = st.columns(3)
    with cooc_col1:
        cooc_type = st.selectbox(ui['cooc_type'], ["Persons", "Locations"], format_func=lambda x: ui['ent_top_p'] if x == "Persons" else ui['ent_top_l'])
    with cooc_col2:
        cooc_top_n = st.slider(ui['cooc_top_n'], 10, 60, 25, 5)
    with cooc_col3:
        cooc_min_edge = st.slider(ui['cooc_min_edge'], 1, 20, 3)
    cooc_col_name = 'entities_persons' if cooc_type == "Persons" else 'entities_locations'
    with st.spinner("Building network..."):
        edges_df = build_cooc_network(df_filt, cooc_col_name, top_n=cooc_top_n, min_edge=cooc_min_edge)
    if edges_df.empty:
        st.warning("No co-occurrence data found. Try lowering the minimum edge filter or selecting more data.")
    else:
        fig_cooc = make_cooc_figure(edges_df, title=f"Co-occurrence: {cooc_type} (top {cooc_top_n}, min edges={cooc_min_edge})")
        if fig_cooc:
            st.plotly_chart(fig_cooc, use_container_width=True)
        st.markdown("**Top Co-occurring Pairs**")
        st.dataframe(edges_df.head(30).rename(columns={'source': 'Entity A', 'target': 'Entity B', 'weight': 'Co-occurrences'}),
                     use_container_width=True, hide_index=True)

with t7:
    st.subheader(ui['waves_sub'])
    st.info(ui['waves_note'])
    if df_waves.empty or not wave_cards:
        st.error("⚠️ Missing 'news_wave_streamlit_slim.csv' or 'streamlit_news_wave_cards.json'.")
    else:
        all_event_types = sorted(set(c.get('dominant_event_type', 'Unknown') for c in wave_cards))
        sel_event_type = st.selectbox("Filter by event type:", ["All"] + all_event_types)
        filtered_cards = wave_cards if sel_event_type == "All" else [c for c in wave_cards if c.get('dominant_event_type') == sel_event_type]
        event_options = [c.get('canonical_event_label', 'Unknown') for c in filtered_cards]
        if not event_options:
            st.warning("No events match this filter.")
        else:
            selected_event = st.selectbox(ui['waves_select'], event_options)
            card_data = next((c for c in filtered_cards if c.get('canonical_event_label') == selected_event), None)
            if card_data:
                cluster_id = card_data.get('canonical_story_cluster_id', '')
                summary_text = card_data.get(f"dashboard_card_{lang_choice.lower()}", card_data.get('dashboard_card_en', '—'))
                st.info(f"**AI Summary:** {summary_text}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Volume", card_data.get('count', 0))
                c2.metric("Dom. Frame", card_data.get('dominant_frame', '—'))
                c3.metric("Event Type", card_data.get('dominant_event_type', '—'))
                c4.metric("Medium", card_data.get('dominant_transmission_medium', '—'))
                st.markdown(f"**Certainty profile:** {card_data.get('certainty_profile', '—')}")
                st.markdown(f"**Transmission profile:** {card_data.get('transmission_profile', '—')}")
                st.divider()
                id_col = "canonical_story_cluster_id" if "canonical_story_cluster_id" in df_waves.columns else "story_cluster_id" if "story_cluster_id" in df_waves.columns else None
                df_w = df_waves[df_waves[id_col].astype(str) == str(cluster_id)].copy() if id_col else pd.DataFrame()
                def simple_bar(dataframe, column, title, color):
                    if column in dataframe.columns and not dataframe.empty:
                        temp = dataframe[column].fillna("Unknown").astype(str).str.strip().replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
                        counts = temp.value_counts().head(10).reset_index()
                        counts.columns = ["Category", "Count"]
                        fig = px.bar(counts, x="Count", y="Category", orientation="h", color_discrete_sequence=[color], title=title)
                        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=350, margin=dict(t=50,b=20,l=10,r=10))
                        return fig
                    return None
                col_w1, col_w2 = st.columns(2)
                with col_w1:
                    fig_r = simple_bar(df_w, "rumor_status", ui['waves_rumor'], "#3498db")
                    if fig_r: st.plotly_chart(fig_r, use_container_width=True)
                with col_w2:
                    fig_m = simple_bar(df_w, "transmission_medium", ui['waves_medium'], "#2ecc71")
                    if fig_m: st.plotly_chart(fig_m, use_container_width=True)
                col_w3, col_w4 = st.columns(2)
                with col_w3:
                    fig_f = simple_bar(df_w, "rhetorical_frame_primary", ui['waves_frame'], "#9b59b6")
                    if fig_f: st.plotly_chart(fig_f, use_container_width=True)
                with col_w4:
                    fig_t2 = simple_bar(df_w, "canonical_event_type", ui['waves_type'], "#e67e22")
                    if fig_t2: st.plotly_chart(fig_t2, use_container_width=True)
                st.divider()
                st.markdown(f"### {ui['waves_sample']} ({selected_event})")
                show_cols = ["newspaper_title", "date", "country", "publication_place", "news_origin_norm", "rumor_status", "transmission_medium", "rhetorical_frame_primary", "canonical_event_type"]
                show_cols = [c for c in show_cols if c in df_w.columns]
                if show_cols:
                    st.dataframe(df_w[show_cols].head(100), use_container_width=True, hide_index=True)
                st.download_button("📥 Export wave CSV", df_w.to_csv(index=False).encode('utf-8'),
                                   f"wave_{re.sub(r'[^A-Za-z0-9_]+', '_', selected_event)}.csv", "text/csv")

with t8:
    st.subheader(ui['wavemap_sub'])
    st.info(ui['wavemap_note'])
    c_src_anim = 'news_origin_norm' if 'news_origin_norm' in df_filt.columns else None
    c_dst_anim = 'publication_place' if 'publication_place' in df_filt.columns else None
    if not c_src_anim or not c_dst_anim:
        st.error("Columns news_origin_norm / publication_place not found.")
    else:
        with st.spinner("Building animated map..."):
            flow_df = build_animated_map_data(df_filt, c_src_anim, c_dst_anim)
        if flow_df.empty:
            st.warning("No flow data with known coordinates found.")
        else:
            fig_anim = make_animated_map(flow_df, c_src_anim, c_dst_anim, ui)
            st.plotly_chart(fig_anim, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
            st.divider()
            st.markdown("**Ετήσιος Όγκος Ροών (τεκμηριωμένες διαδρομές)**")
            year_summary = flow_df.groupby('year')['weight'].sum().reset_index().rename(columns={'year': 'Έτος', 'weight': 'Εγγραφές'})
            st.bar_chart(year_summary.set_index('Έτος'))

with t9:
    st.subheader(ui['emo_sub'])
    st.info(ui['emo_note'])
    if not dict_emotions:
        st.warning("⚠️ EMOTION_ANALYSIS_SUMMARY.xlsx not found or sheets could not be read.")
    else:
        st.markdown(f"**1. {ui['emo_overall']}**")
        df_ov = dict_emotions.get('overall', pd.DataFrame()).copy()
        if not df_ov.empty and {'emotion', 'mean'}.issubset(df_ov.columns):
            fig_ov = px.bar(df_ov, x='mean', y='emotion', color='emotion', orientation='h', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_ov.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400, showlegend=False)
            st.plotly_chart(fig_ov, use_container_width=True)
        else:
            st.warning("Overall emotion sheet not found in expected format.")
        st.divider()
        st.markdown(f"**2. {ui['emo_timeline']}**")
        df_y = dict_emotions.get('by_year', pd.DataFrame()).copy()
        if not df_y.empty and 'year_val' in df_y.columns:
            available_emo_cols = [c for c in EMOTION_ORDER if c in df_y.columns]
            if available_emo_cols:
                df_y_melt = df_y.melt(id_vars=['year_val'], value_vars=available_emo_cols, var_name='Emotion', value_name='Score')
                fig_y = px.line(df_y_melt, x='year_val', y='Score', color='Emotion', markers=True, color_discrete_sequence=px.colors.qualitative.Set1)
                fig_y.update_layout(height=450, xaxis_title="Έτος", yaxis_title="Ένταση (1–10)")
                st.plotly_chart(fig_y, use_container_width=True)
        st.divider()
        st.markdown(f"**3. {ui['emo_country']}**")
        df_yc = dict_emotions.get('by_year_country', pd.DataFrame()).copy()
        if not df_yc.empty and 'country_analysis' in df_yc.columns and 'year_val' in df_yc.columns:
            available_country_emo_cols = [c for c in EMOTION_ORDER if c in df_yc.columns]
            if available_country_emo_cols:
                selected_emo = st.selectbox(ui['emo_select'], available_country_emo_cols)
                fig_yc = px.line(df_yc, x='year_val', y=selected_emo, color='country_analysis', markers=True,
                                 color_discrete_map={'UK': '#1f77b4', 'France': '#d62728', 'GB': '#1f77b4', 'FR': '#d62728'})
                fig_yc.update_layout(height=450, xaxis_title="Έτος", yaxis_title=f"Ένταση ({selected_emo})")
                st.plotly_chart(fig_yc, use_container_width=True)
        else:
            st.warning("Emotion-by-year-country data not found.")

with t10:
    st.subheader(ui['geo_emo_sub'])
    st.info(ui['geo_emo_note'])
    node_emotions = build_node_emotions(df_filt)
    if node_emotions.empty:
        st.warning("No node-level emotion data found. Check news_origin_norm and emotion columns.")
    else:
        st.markdown("**Top emotional news-origin nodes**")
        st.dataframe(node_emotions.head(30), use_container_width=True, hide_index=True)
        nodes_available = node_emotions['Node'].tolist()
        if len(nodes_available) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                node1 = st.selectbox("1ος Κόμβος:", nodes_available, index=0)
            with col2:
                node2 = st.selectbox("2ος Κόμβος (Σύγκριση):", nodes_available, index=min(1, len(nodes_available)-1))
            data1 = node_emotions[node_emotions['Node'] == node1].iloc[0]
            data2 = node_emotions[node_emotions['Node'] == node2].iloc[0]
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=[data1[c] for c in EMOTION_ORDER], theta=EMOTION_ORDER,
                                                fill='toself', name=f"{node1} (n={int(data1['records'])})", line_color='#e74c3c'))
            fig_radar.add_trace(go.Scatterpolar(r=[data2[c] for c in EMOTION_ORDER], theta=EMOTION_ORDER,
                                                fill='toself', name=f"{node2} (n={int(data2['records'])})", line_color='#3498db'))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10], gridcolor='rgba(255,255,255,0.2)'),
                                               bgcolor='rgba(0,0,0,0)'),
                                    showlegend=True, title=f"Emotional profile: {node1} vs {node2}",
                                    title_font=dict(color='white'), legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=600)
            st.plotly_chart(fig_radar, use_container_width=True)
