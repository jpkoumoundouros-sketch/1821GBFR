import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile
import io

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Thesis Dashboard - 1821 Info Flows", page_icon="🏛️", layout="wide")

# ==========================================
# 📚 ΛΕΞΙΚΑ ΚΑΝΟΝΙΚΟΠΟΙΗΣΗΣ ΟΝΤΟΤΗΤΩΝ
# ==========================================
PERSON_ALIASES = {'Ibrahim Pasha': ['ibrahim', 'ibrahim pacha', 'ibrahim pasha', 'ibrahim pascha', 'pacha of egypt'], 'Ioannis Kapodistrias': ["count capo d'istria", "capo d'istria", 'kapodistrias'], 'Lord Byron': ['byron', 'lord byron'], 'Theodoros Kolokotronis': ['kolokotronis', 'colocotroni']}
LOC_ALIASES = {'Peloponnese (Morea)': ['morée', 'morea', 'peloponnese'], 'Missolonghi': ['missolonghi', 'mesolongi'], 'Navarino': ['navarin', 'navarino']}

def normalize_entities(entity_str, alias_dict):
    if pd.isna(entity_str) or not isinstance(entity_str, str): return ""
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
        if not matched and e_lower != '': cleaned.append(e.title())
    return ", ".join(sorted(list(set(cleaned))))

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΦΟΡΤΩΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
@st.cache_data
def load_main_data():
    try:
        with zipfile.ZipFile("THESIS_WITH_ORIENTATION.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and name.endswith('.csv')]
            if not csv_files: return pd.DataFrame(), pd.Series()
            with z.open(csv_files[0]) as f:
                df = pd.read_csv(io.StringIO(f.read().decode('utf-8', errors='replace')), low_memory=False, sep=None, engine='python')
        
        df.columns = df.columns.str.lower().str.strip()
        
        # Στατιστικά Σχετικότητας
        raw_relevance = df['ai_relevance'].astype(str).str.lower().str.strip().value_counts() if 'ai_relevance' in df.columns else pd.Series()
        
        # Φιλτράρισμα (Πιο ανθεκτικό)
        if 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()
            
        # Καθαρισμός Στάσης/Θέματος
        for col, label in [('ai_stance', 'Άγνωστη Στάση'), ('ai_topic', 'Άγνωστο Θέμα')]:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna(label).replace(['nan', 'unknown', 'None'], label)
                # Διόρθωση αν το AI έγραψε κατά λάθος το relevance στη στάση
                df.loc[df[col].str.contains('relevant', case=False), col] = label

        # Καθαρισμός Χώρας
        if 'country' in df.columns:
            df['country'] = df['country'].astype(str).str.upper().str.strip().replace({'UK': 'GB', 'UNITED KINGDOM': 'GB', 'FRANCE': 'FR'})
            
        # Καθαρισμός Έτους
        df['year_val'] = 0
        if 'year' in df.columns: df['year_val'] = pd.to_numeric(df['year'], errors='coerce').fillna(0)
        if 'date' in df.columns:
            mask = df['year_val'] == 0
            df.loc[mask, 'year_val'] = pd.to_numeric(df.loc[mask, 'date'].astype(str).str.extract(r'(18[23]\d)')[0], errors='coerce').fillna(0)
        df.loc[(df['year_val'] < 1821) | (df['year_val'] > 1832), 'year_val'] = 0
        
        # Κανονικοποίηση
        if 'entities_persons' in df.columns: df['entities_persons'] = df['entities_persons'].apply(lambda x: normalize_entities(x, PERSON_ALIASES))
        if 'entities_locations' in df.columns: df['entities_locations'] = df['entities_locations'].apply(lambda x: normalize_entities(x, LOC_ALIASES))
            
        return df, raw_relevance
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης: {e}")
        return pd.DataFrame(), pd.Series()

df_main, raw_relevance = load_main_data()

# --- SIDEBAR ΦΙΛΤΡΑ ---
if not df_main.empty:
    st.sidebar.header("🎛️ Φίλτρα")
    
    countries = sorted(df_main['country'].unique())
    sel_countries = st.sidebar.multiselect("Χώρες:", countries, default=countries)
    
    v_years = df_main[df_main['year_val'] > 0]['year_val']
    sel_years = st.sidebar.slider("Περίοδος:", int(v_years.min()) if not v_years.empty else 1821, int(v_years.max()) if not v_years.empty else 1832, (int(v_years.min()) if not v_years.empty else 1821, int(v_years.max()) if not v_years.empty else 1832))
    
    stances = sorted(df_main['ai_stance'].unique())
    sel_stances = st.sidebar.multiselect("Στάση:", stances, default=stances)

    df_filt = df_main[(df_main['country'].isin(sel_countries)) & (df_main['year_val'] >= sel_years[0]) & (df_main['year_val'] <= sel_years[1]) & (df_main['ai_stance'].isin(sel_stances))]
else:
    df_filt = pd.DataFrame()

# --- MAIN UI ---
st.title("🏛️ Ψηφιακό Παράρτημα")
if df_filt.empty:
    st.warning("⚠️ Δεν βρέθηκαν δεδομένα. Ελέγξτε τα φίλτρα στην πλαϊνή μπάρα.")
else:
    t1, t2, t3, t4, t5 = st.tabs(["📊 Επισκόπηση", "📰 Εκδοτικό Τοπίο", "🧠 Θεματολογία", "🌍 Ροές", "👥 Οντότητες"])

    with t1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Άρθρα", f"{len(df_filt):,}")
        c2.metric("Εφημερίδες", df_filt['newspaper_title'].nunique() if 'newspaper_title' in df_filt.columns else 0)
        
        st.subheader("📈 Όγκος Δημοσιεύσεων")
        df_v = df_filt[df_filt['year_val'] > 0].groupby(['year_val', 'country']).size().reset_index(name='c')
        st.plotly_chart(px.line(df_v, x='year_val', y='c', color='country', markers=True), use_container_width=True)

    with t2:
        st.subheader("📰 Πολιτική Γραμμή Εφημερίδων")
        if 'newspaper_title' in df_filt.columns:
            top_np = df_filt['newspaper_title'].value_counts().nlargest(15).index
            df_np = df_filt[df_filt['newspaper_title'].isin(top_np)].groupby(['newspaper_title', 'ai_stance']).size().reset_index(name='count')
            st.plotly_chart(px.bar(df_np, x='count', y='newspaper_title', color='ai_stance', orientation='h'), use_container_width=True)
        else:
            st.info("Η στήλη 'newspaper_title' δεν βρέθηκε στο αρχείο.")

    with t3:
        st.subheader("🧠 Ανάλυση Θεματολογίας")
        if 'ai_topic' in df_filt.columns:
            top_t = df_filt['ai_topic'].value_counts().nlargest(10).index
            df_t = df_filt[df_filt['ai_topic'].isin(top_t)].groupby(['year_val', 'ai_topic']).size().reset_index(name='c')
            st.plotly_chart(px.area(df_t[df_t['year_val']>0], x='year_val', y='c', color='ai_topic'), use_container_width=True)
        else:
            st.info("Η στήλη 'ai_topic' δεν βρέθηκε στο αρχείο.")

    with t4:
        st.subheader("🌍 Διακρατικές Ροές Ειδήσεων")
        # ΕΔΩ ΕΙΝΑΙ Η ΔΙΟΡΘΩΣΗ: Ελέγχουμε αν υπάρχουν οι στήλες των ροών
        origin_col = next((c for c in df_filt.columns if 'origin' in c), None)
        dest_col = next((c for c in df_filt.columns if 'publication_place' in c or 'place' in c), None)
        
        if origin_col and dest_col:
            f_df = df_filt.dropna(subset=[origin_col, dest_col])
            if not f_df.empty:
                f_grp = f_df.groupby([origin_col, dest_col]).size().reset_index(name='c').sort_values('c', ascending=False).head(50)
                nds = list(pd.concat([f_grp[origin_col], f_grp[dest_col]]).unique())
                n_m = {n: i for i, n in enumerate(nds)}
                fig = go.Figure(go.Sankey(node=dict(label=nds), link=dict(source=f_grp[origin_col].map(n_m), target=f_grp[dest_col].map(n_m), value=f_grp['c'])))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Τα πεδία προέλευσης/έκδοσης είναι κενά για αυτά τα φίλτρα.")
        else:
            st.info("Δεν βρέθηκαν στήλες 'news_origin' ή 'publication_place'.")

    with t5:
        st.subheader("👥 Οντότητες")
        st.info("Ελέγξτε τις συχνότητες των κανονικοποιημένων προσώπων και τοποθεσιών.")
