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
    'Ibrahim Pasha': ['ibrahim-pacha', 'ibrahim', 'ibrahim pacha', 'pacha of egypt', 'pacha', 'ibrahim pasha', 'ibrahim pascha', 'i-brahim pacha', 'ibrahian-pacha', 'ibrahim-packa'],
    'Ioannis Kapodistrias': ["count capo d'istria", "count capo d'istrias", "capo d'istria", "capo d'istrias", "comte capo-d'istria", "comte capo-d'istrias", 'president of greece', 'president', 'kapodistrias'],
    'Lord Cochrane': ['lord cochrane', 'cochrane', 'thomas cochrane', 'lords cochrane'],
    'Sultan Mahmud II': ['sultan', 'mahmoud', 'le sultan', 'grand-seigneur', 'mahmud', 'mahmud ii'],
    'Lord Byron': ['lord byron', 'byron'],
    'Capitan Pasha': ['capitan-pacha', 'capitan pacha'],
    'Andreas Miaoulis': ['miaulis', 'amiral miaulis', 'admiral miaulis'],
    'Theodoros Kolokotronis': ['colocotroni', 'kolokotronis', 'kolokotroni', 'colocotronis'],
    'Alexander / Demetrios Ypsilantis': ['ypsilanti', 'prince ypsilanti', 'démétrius ypsilanti', 'ypsilantis', 'démétrius-ipsilanty'],
    'General Richard Church': ['general church', 'général church', 'church', 'richard church'],
    'Jean-Gabriel Eynard': ['m. eynard', 'eynard'],
    'Reshid Pasha': ['reschid-pacha', 'reshid', 'kiutahi', 'teschid-pacha'],
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
    'Peloponnese (Morea)': ['morée', 'morea', 'péloponnèse', 'peloponnesus', 'peloponnese'],
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

def normalize_entities(entity_str, alias_dict):
    if pd.isna(entity_str) or not isinstance(entity_str, str) or entity_str.strip() == "":
        return ""
    entities = [e.strip() for e in entity_str.split(',')]
    cleaned = []
    for e in entities:
        e_lower = e.lower().replace('"', '').replace('[', '').replace(']', '').strip()
        matched = False
        for main_name, aliases in alias_dict.items():
            if e_lower in aliases:
                cleaned.append(main_name)
                matched = True
                break
        if not matched and e_lower != '':
            cleaned.append(e.strip().title())
    return ", ".join(sorted(list(set(cleaned))))

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΦΟΡΤΩΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
@st.cache_data
def load_main_data():
    try:
        with zipfile.ZipFile("THESIS_RECLASSIFIED_FINAL.csv.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and name.endswith('.csv')]
            if not csv_files:
                return pd.DataFrame(), pd.Series()
            with z.open(csv_files[0]) as f:
                content = f.read().decode('utf-8', errors='replace')
                # Χρήση sep=None για αυτόματη αναγνώριση διαχωριστικού χωρίς low_memory conflict
                df = pd.read_csv(io.StringIO(content), sep=None, engine='python', on_bad_lines='skip')
        
        df.columns = df.columns.str.lower().str.strip()
        
        # 1. Στατιστικά Σχετικότητας & Φιλτράρισμα
        raw_relevance = pd.Series()
        if 'ai_relevance' in df.columns:
            raw_relevance = df['ai_relevance'].astype(str).str.lower().str.strip().value_counts()
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()

        # 2. Καθαρισμός Στάσης / Θεμάτων (Σκούπα για λάθη του AI)
        for col in ['ai_stance', 'ai_topic']:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna('Άγνωστο').replace(['nan', 'unknown', 'None'], 'Άγνωστο')
                df.loc[df[col].str.contains('relevant', case=False, na=False), col] = 'Άγνωστο'

        # 3. Καθαρισμός Χώρας
        if 'country' in df.columns:
            df['country'] = df['country'].astype(str).str.strip().str.upper()
            df['country'] = df['country'].replace({'UK': 'GB', 'GBR': 'GB', 'UNITED KINGDOM': 'GB', 'FRANCE': 'FR'})
            
        # 4. Καθαρισμός Έτους
        df['year_val'] = 0
        if 'year' in df.columns:
            df['year_val'] = pd.to_numeric(df['year'], errors='coerce').fillna(0)
        if 'date' in df.columns:
            mask = df['year_val'] == 0
            extracted = df.loc[mask, 'date'].astype(str).str.extract(r'(18[23]\d)')[0]
            df.loc[mask, 'year_val'] = pd.to_numeric(extracted, errors='coerce').fillna(0)
            
        df = df[(df['year_val'] >= 1821) & (df['year_val'] <= 1832)].copy()
        
        # 5. Κανονικοποίηση (On-the-fly)
        if 'entities_persons' in df.columns:
            df['entities_persons'] = df['entities_persons'].apply(lambda x: normalize_entities(x, PERSON_ALIASES))
        if 'entities_locations' in df.columns:
            df['entities_locations'] = df['entities_locations'].apply(lambda x: normalize_entities(x, LOC_ALIASES))
            
        return df, raw_relevance
    except Exception as e:
        st.error(f"Σφάλμα κατά τη φόρτωση: {e}")
        return pd.DataFrame(), pd.Series()

df_main, raw_relevance = load_main_data()

# --- SIDEBAR ---
if not df_main.empty:
    st.sidebar.header("🎛️ Φίλτρα Ανάλυσης")
    countries = sorted(df_main['country'].unique())
    sel_countries = st.sidebar.multiselect("Χώρες:", countries, default=countries)
    min_y, max_y = int(df_main['year_val'].min()), int(df_main['year_val'].max())
    sel_years = st.sidebar.slider("Περίοδος:", min_y, max_y, (min_y, max_y))
    
    df_filt = df_main[
        (df_main['country'].isin(sel_countries)) & 
        (df_main['year_val'] >= sel_years[0]) & 
        (df_main['year_val'] <= sel_years[1])
    ]
else:
    st.stop()

# --- ΚΥΡΙΩΣ ΕΦΑΡΜΟΓΗ ---
st.title("🏛️ Ψηφιακό Παράρτημα: Διακρατικές Ροές Πληροφορίας")
st.markdown(f"**Ενεργό Corpus:** {len(df_filt):,} Άρθρα (Directly Relevant)")
st.divider()

t1, t2, t3, t4, t5 = st.tabs(["📊 Επισκόπηση", "📰 Εκδοτικό Τοπίο", "🧠 Θεματολογία", "🌍 Ροές", "👥 Οντότητες"])

with t1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Άρθρα", f"{len(df_filt):,}")
    c2.metric("Εφημερίδες", df_filt['newspaper_title'].nunique() if 'newspaper_title' in df_filt.columns else 0)
    
    u_pers = df_filt['entities_persons'].str.split(',').explode().str.strip().replace('', pd.NA).dropna().nunique()
    u_locs = df_filt['entities_locations'].str.split(',').explode().str.strip().replace('', pd.NA).dropna().nunique()
    c3.metric("Μοναδικά Πρόσωπα", f"{u_pers:,}")
    c4.metric("Μοναδικοί Τόποι", f"{u_locs:,}")
    
    st.subheader("📈 Όγκος Δημοσιεύσεων ανά Έτος")
    df_v = df_filt.groupby(['year_val', 'country']).size().reset_index(name='c')
    st.plotly_chart(px.line(df_v, x='year_val', y='c', color='country', markers=True), use_container_width=True)

with t2:
    st.subheader("📰 Πολιτική Γραμμή των κυριότερων Εφημερίδων")
    if 'newspaper_title' in df_filt.columns:
        top_np = df_filt['newspaper_title'].value_counts().nlargest(15).index
        df_np = df_filt[df_filt['newspaper_title'].isin(top_np)].groupby(['newspaper_title', 'ai_stance']).size().reset_index(name='count')
        st.plotly_chart(px.bar(df_np, x='count', y='newspaper_title', color='ai_stance', orientation='h'), use_container_width=True)

with t3:
    st.subheader("🧠 Εξέλιξη Κυρίαρχων Θεμάτων")
    if 'ai_topic' in df_filt.columns:
        top_t = df_filt['ai_topic'].value_counts().nlargest(10).index
        df_t = df_filt[df_filt['ai_topic'].isin(top_t)].groupby(['year_val', 'ai_topic']).size().reset_index(name='c')
        st.plotly_chart(px.area(df_t, x='year_val', y='c', color='ai_topic'), use_container_width=True)

with t4:
    st.subheader("🌍 Διακρατικές Ροές Ειδήσεων (Top 50)")
    c_src = next((c for c in df_filt.columns if 'origin' in c), None)
    c_dst = next((c for c in df_filt.columns if 'pub' in c or 'place' in c), None)
    if c_src and c_dst:
        f_df = df_filt.dropna(subset=[c_src, c_dst])
        f_grp = f_df.groupby([c_src, c_dst]).size().reset_index(name='c').sort_values('c', ascending=False).head(50)
        if not f_grp.empty:
            nds = list(pd.concat([f_grp[c_src], f_grp[c_dst]]).unique())
            mapping = {n: i for i, n in enumerate(nds)}
            fig = go.Figure(go.Sankey(node=dict(label=nds, pad=15, thickness=20), link=dict(source=f_grp[c_src].map(mapping), target=f_grp[c_dst].map(mapping), value=f_grp['c'])))
            st.plotly_chart(fig, use_container_width=True)

with t5:
    st.subheader("👥 Ανάλυση Οντοτήτων (Κανονικοποιημένες)")
    ca, cb = st.columns(2)
    def make_ner(col, title, color):
        data = df_filt[col].str.split(',').explode().str.strip().replace('', pd.NA).dropna()
        if not data.empty:
            cnt = data.value_counts().head(20).reset_index()
            cnt.columns = ['Οντότητα', 'Αναφορές']
            return px.bar(cnt, x='Αναφορές', y='Οντότητα', orientation='h', title=title, color_discrete_sequence=[color])
    
    chart_p = make_ner('entities_persons', "Top 20 Πρόσωπα", "#1f77b4")
    chart_l = make_ner('entities_locations', "Top 20 Τοποθεσίες", "#ff7f0e")
    if chart_p: ca.plotly_chart(chart_p, use_container_width=True)
    if chart_l: cb.plotly_chart(chart_l, use_container_width=True)
