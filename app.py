import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile
import io

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Thesis Dashboard - 1821 Info Flows", page_icon="🏛️", layout="wide")

# ==========================================
# 📚 ΛΕΞΙΚΑ ΚΑΝΟΝΙΚΟΠΟΙΗΣΗΣ ΟΝΤΟΤΗΤΩΝ (NER)
# ==========================================
PERSON_ALIASES = {
    'Ibrahim Pasha': ['ibrahim-pacha', 'ibrahim', 'ibrahim pacha', 'pacha of egypt', 'pacha', 'ibrahim pasha', 'ibrahim pascha'],
    'Ioannis Kapodistrias': ["count capo d'istria", "capo d'istria", "comte capo-d'istria", 'president of greece', 'kapodistrias'],
    'Lord Cochrane': ['lord cochrane', 'cochrane', 'thomas cochrane'],
    'Sultan Mahmud II': ['sultan', 'mahmoud', 'le sultan', 'grand-seigneur', 'mahmud'],
    'Lord Byron': ['lord byron', 'byron'],
    'Theodoros Kolokotronis': ['kolokotronis', 'colocotroni', 'kolokotroni', 'colocotronis'],
    'Andreas Miaoulis': ['miaulis', 'amiral miaulis', 'admiral miaulis'],
    'Alexander Ypsilantis': ['ypsilanti', 'prince ypsilanti', 'ypsilantis'],
    'General Richard Church': ['general church', 'général church', 'church'],
    'Reshid Pasha': ['reschid-pacha', 'reshid', 'kiutahi'],
    'Alexandros Mavrokordatos': ['maurocordato', 'mavrocordato', 'prince mavrocordato']
}

LOC_ALIASES = {
    'Peloponnese (Morea)': ['morée', 'morea', 'péloponnèse', 'peloponnese'],
    'Missolonghi': ['missolonghi', 'mesolongi', 'missolongi'],
    'Navarino': ['navarin', 'navarino'],
    'Constantinople': ['constantinople', 'istanbul'],
    'Great Britain': ['london', 'londres', 'england', 'angleterre', 'great britain'],
    'France': ['france', 'paris', 'marseille', 'marseilles'],
    'Egypt': ['egypt', 'égypte', 'alexandria'],
    'Greece': ['greece', 'grèce', 'western greece', 'eastern greece']
}

def normalize_entities(entity_str, alias_dict):
    if pd.isna(entity_str) or not isinstance(entity_str, str) or entity_str.strip() == "":
        return ""
    entities = [e.strip() for e in entity_str.split(',')]
    cleaned = []
    for e in entities:
        e_lower = e.lower()
        matched = False
        for main_name, aliases in alias_dict.items():
            if e_lower in aliases:
                cleaned.append(main_name)
                matched = True
                break
        if not matched and e_lower != '':
            cleaned.append(e.title())
    return ", ".join(sorted(list(set(cleaned))))

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΦΟΡΤΩΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
@st.cache_data
def load_main_data():
    try:
        # Έλεγχος αν υπάρχει το αρχείο ZIP
        with zipfile.ZipFile("THESIS_RECLASSIFIED_FINAL.csv.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and name.endswith('.csv')]
            if not csv_files:
                st.error("Το ZIP δεν περιέχει αρχείο CSV.")
                return pd.DataFrame(), pd.Series()
            
            with z.open(csv_files[0]) as f:
                content = f.read().decode('utf-8', errors='replace')
                # Δοκιμή διαφορετικών διαχωριστικών (CSV/Excel)
                df = pd.read_csv(io.StringIO(content), low_memory=False, sep=None, engine='python')
        
        # Καθαρισμός ονομάτων στηλών
        df.columns = df.columns.str.lower().str.strip()
        
        # Υπολογισμός στατιστικών πριν το φιλτράρισμα
        raw_relevance = pd.Series()
        if 'ai_relevance' in df.columns:
            raw_relevance = df['ai_relevance'].astype(str).str.lower().str.strip().value_counts()
            # Σωστό φιλτράρισμα μόνο για Directly Relevant
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()
        
        # Καθαρισμός Στάσης και Θεμάτων
        for col in ['ai_stance', 'ai_topic']:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna('Άγνωστο').replace(['nan', 'unknown', 'None'], 'Άγνωστο')
                # Αφαίρεση λέξεων 'relevant' που μπορεί να ξέμειναν
                df.loc[df[col].str.contains('relevant', case=False, na=False), col] = 'Άγνωστο'

        # Καθαρισμός Χώρας
        if 'country' in df.columns:
            df['country'] = df['country'].astype(str).str.upper().str.strip().replace({'UK': 'GB', 'UNITED KINGDOM': 'GB', 'FRANCE': 'FR'})
            
        # Καθαρισμός Έτους (Regex για 1821-1832)
        df['year_val'] = 0
        if 'year' in df.columns:
            df['year_val'] = pd.to_numeric(df['year'], errors='coerce').fillna(0)
        
        if 'date' in df.columns:
            mask = df['year_val'] == 0
            extracted = df.loc[mask, 'date'].astype(str).str.extract(r'(18[23]\d)')[0]
            df.loc[mask, 'year_val'] = pd.to_numeric(extracted, errors='coerce').fillna(0)
        
        # Περιορισμός στα έτη της διατριβής
        df = df[(df['year_val'] >= 1821) & (df['year_val'] <= 1832)].copy()
        
        # Κανονικοποίηση Οντοτήτων
        if 'entities_persons' in df.columns:
            df['entities_persons'] = df['entities_persons'].apply(lambda x: normalize_entities(x, PERSON_ALIASES))
        if 'entities_locations' in df.columns:
            df['entities_locations'] = df['entities_locations'].apply(lambda x: normalize_entities(x, LOC_ALIASES))
            
        return df, raw_relevance
    except Exception as e:
        st.error(f"Κρίσιμο σφάλμα κατά τη φόρτωση: {e}")
        return pd.DataFrame(), pd.Series()

# Φόρτωση
df_filt, raw_relevance = load_main_data()

# --- SIDEBAR ---
if not df_filt.empty:
    st.sidebar.header("🎛️ Φίλτρα")
    
    countries = sorted(df_filt['country'].unique())
    sel_countries = st.sidebar.multiselect("Χώρες:", countries, default=countries)
    
    min_y = int(df_filt['year_val'].min())
    max_y = int(df_filt['year_val'].max())
    sel_years = st.sidebar.slider("Περίοδος:", min_y, max_y, (min_y, max_y))
    
    # Εφαρμογή Φίλτρων Sidebar
    df_display = df_filt[
        (df_filt['country'].isin(sel_countries)) & 
        (df_filt['year_val'] >= sel_years[0]) & 
        (df_filt['year_val'] <= sel_years[1])
    ]
else:
    st.title("🏛️ Dashboard Διατριβής")
    st.warning("⚠️ Δεν ήταν δυνατή η φόρτωση των δεδομένων. Βεβαιωθείτε ότι το αρχείο THESIS_WITH_ORIENTATION.zip βρίσκεται στον φάκελο.")
    st.stop()

# --- ΚΥΡΙΩΣ ΕΦΑΡΜΟΓΗ ---
st.title("🏛️ Ψηφιακό Παράρτημα: Διακρατικές Ροές Πληροφορίας")
st.markdown(f"**Ενεργό Corpus:** {len(df_display):,} Άρθρα | **Περίοδος:** {sel_years[0]} - {sel_years[1]}")
st.divider()

t1, t2, t3, t4, t5 = st.tabs(["📊 Επισκόπηση", "📰 Εκδοτικό Τοπίο", "🧠 Θεματολογία", "🌍 Ροές", "👥 Οντότητες"])

with t1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Άρθρα", f"{len(df_display):,}")
    c2.metric("Εφημερίδες", df_display['newspaper_title'].nunique() if 'newspaper_title' in df_display.columns else 0)
    
    # Υπολογισμός μοναδικών οντοτήτων
    u_pers = df_display['entities_persons'].str.split(',').explode().str.strip().replace('', pd.NA).dropna().nunique()
    u_locs = df_display['entities_locations'].str.split(',').explode().str.strip().replace('', pd.NA).dropna().nunique()
    c3.metric("Μοναδικά Πρόσωπα", f"{u_pers:,}")
    c4.metric("Μοναδικοί Τόποι", f"{u_locs:,}")
    
    st.subheader("📈 Όγκος Δημοσιεύσεων ανά Έτος")
    df_v = df_display.groupby(['year_val', 'country']).size().reset_index(name='c')
    st.plotly_chart(px.line(df_v, x='year_val', y='c', color='country', markers=True), use_container_width=True)

with t2:
    st.subheader("📰 Πολιτική Γραμμή των 15 κυριότερων Εφημερίδων")
    if 'newspaper_title' in df_display.columns:
        top_np = df_display['newspaper_title'].value_counts().nlargest(15).index
        df_np = df_display[df_display['newspaper_title'].isin(top_np)].groupby(['newspaper_title', 'ai_stance']).size().reset_index(name='count')
        st.plotly_chart(px.bar(df_np, x='count', y='newspaper_title', color='ai_stance', orientation='h'), use_container_width=True)

with t3:
    st.subheader("🧠 Κυρίαρχα Θέματα στον Χρόνο")
    if 'ai_topic' in df_display.columns:
        top_t = df_display['ai_topic'].value_counts().nlargest(10).index
        df_t = df_display[df_display['ai_topic'].isin(top_t)].groupby(['year_val', 'ai_topic']).size().reset_index(name='c')
        st.plotly_chart(px.area(df_t, x='year_val', y='c', color='ai_topic'), use_container_width=True)

with t4:
    st.subheader("🌍 Ροές Ειδήσεων (Προέλευση ➔ Έκδοση)")
    # Αναζήτηση στηλών για ροές
    col_src = next((c for c in df_display.columns if 'origin' in c), None)
    col_dst = next((c for c in df_display.columns if 'publication_place' in c or 'place' in c), None)
    
    if col_src and col_dst:
        f_df = df_display.dropna(subset=[col_src, col_dst])
        f_grp = f_df.groupby([col_src, col_dst]).size().reset_index(name='c').sort_values('c', ascending=False).head(40)
        if not f_grp.empty:
            nodes = list(pd.concat([f_grp[col_src], f_grp[col_dst]]).unique())
            mapping = {n: i for i, n in enumerate(nodes)}
            fig = go.Figure(go.Sankey(node=dict(label=nodes, pad=15, thickness=20), 
                                     link=dict(source=f_grp[col_src].map(mapping), target=f_grp[dst_col if 'dst_col' in locals() else col_dst].map(mapping), value=f_grp['c'])))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Δεν υπάρχουν επαρκή δεδομένα για τις ροές.")
    else:
        st.info("Δεν βρέθηκαν οι απαραίτητες στήλες για το διάγραμμα ροών.")

with t5:
    st.subheader("👥 Ανάλυση Οντοτήτων")
    col_a, col_b = st.columns(2)
    def make_ner_chart(col_name, title, color):
        data = df_display[col_name].str.split(',').explode().str.strip().replace('', pd.NA).dropna()
        if not data.empty:
            counts = data.value_counts().head(20).reset_index()
            counts.columns = ['Οντότητα', 'Αναφορές']
            return px.bar(counts, x='Αναφορές', y='Οντότητα', orientation='h', title=title, color_discrete_sequence=[color])
        return None

    chart_p = make_ner_chart('entities_persons', "Top 20 Πρόσωπα", "#1f77b4")
    chart_l = make_ner_chart('entities_locations', "Top 20 Τοποθεσίες", "#ff7f0e")
    
    if chart_p: col_a.plotly_chart(chart_p, use_container_width=True)
    if chart_l: col_b.plotly_chart(chart_l, use_container_width=True)

# --- ΔΙΑΓΝΩΣΤΙΚΟ TAB ---
with st.expander("🛠️ Διαγνωστικός Έλεγχος Αρχείου (Μόνο για εσένα)"):
    st.write("Στήλες που βρέθηκαν στο CSV:", list(df_display.columns))
    st.write("Δείγμα δεδομένων (πρώτες 5 γραμμές):")
    st.dataframe(df_display.head())
