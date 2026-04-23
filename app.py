import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile
import io
import re

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Thesis Dashboard - 1821 Info Flows", page_icon="🏛️", layout="wide")

# ==========================================
# 📚 ΛΕΞΙΚΑ ΚΑΝΟΝΙΚΟΠΟΙΗΣΗΣ ΟΝΤΟΤΗΤΩΝ (NER)
# ==========================================
PERSON_ALIASES = {
    'Ibrahim Pasha': ['ibrahim', 'ibrahim pacha', 'ibrahim pasha', 'ibrahim pascha', 'pacha of egypt'],
    'Theodoros Kolokotronis': ['kolokotronis', 'colocotroni', 'colocotronis', 'kolokotroni'],
    'Sultan Mahmud II': ['mahmud', 'mahmoud', 'sultan', 'grand signior', 'mahmud ii'],
    'Lord Byron': ['byron', 'lord byron'],
    'Ioannis Kapodistrias': ['capodistrias', 'capo d\'istria', 'kapodistrias', 'count capodistrias'],
    'Admiral Codrington': ['codrington', 'edward codrington', 'admiral codrington'],
    'Reshid Pasha (Kiutahi)': ['reshid', 'kiutahi', 'redschid', 'redschid pacha'],
    'Alexander Ypsilantis': ['ypsilanti', 'ypsilantis', 'hypsilantes']
}

LOC_ALIASES = {
    'Missolonghi': ['missolonghi', 'mesolongi', 'missolongi', 'micsolonghi'],
    'Navarino': ['navarino', 'navarin'],
    'Constantinople': ['constantinople', 'istanbul', 'stamboul'],
    'Athens': ['athens', 'athènes'],
    'Peloponnese': ['peloponnese', 'morea', 'morée', 'peloponnesus'],
    'Smyrna': ['smyrna', 'izmir'],
    'London': ['london', 'londres']
}

def normalize_entities(entity_str, alias_dict):
    """Μετατρέπει τις παραλλαγές στο κεντρικό, επίσημο όνομα."""
    if pd.isna(entity_str) or not isinstance(entity_str, str):
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
        with zipfile.ZipFile("THESIS_WITH_ORIENTATION.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and not name.startswith('._') and name.endswith('.csv')]
            if not csv_files:
                return pd.DataFrame(), pd.Series()
                
            real_file_name = csv_files[0]
            with z.open(real_file_name) as f:
                content_bytes = f.read()
        
        text_content = content_bytes.decode('utf-8', errors='replace')
        df = pd.read_csv(io.StringIO(text_content), sep=',', low_memory=False, on_bad_lines='skip')
        if len(df.columns) < 3:
            df = pd.read_csv(io.StringIO(text_content), sep=';', low_memory=False, on_bad_lines='skip')
        
        df.columns = df.columns.str.lower().str.strip()
        
        # Υπολογισμός συνολικών στατιστικών ΠΡΙΝ το φιλτράρισμα
        if 'ai_relevance' in df.columns:
            raw_relevance = df['ai_relevance'].astype(str).str.lower().str.strip().value_counts()
        else:
            raw_relevance = pd.Series()
        
        # 1. Φιλτράρισμα Directly Relevant (ΤΟ FIX: == αντί για contains)
        if 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()
            
        # 2. ΣΚΟΥΠΑ ΓΙΑ "ΠΑΡΑΙΣΘΗΣΕΙΣ" ΤΟΥ AI 
        if 'ai_stance' in df.columns:
            df['ai_stance'] = df['ai_stance'].astype(str).fillna('Άγνωστη Στάση')
            df.loc[df['ai_stance'].str.lower().str.contains('relevant|irrelevant|unknown'), 'ai_stance'] = 'Άγνωστη Στάση'
        if 'ai_topic' in df.columns:
            df['ai_topic'] = df['ai_topic'].astype(str).fillna('Άγνωστο Θέμα')
            df.loc[df['ai_topic'].str.lower().str.contains('relevant|irrelevant|unknown'), 'ai_topic'] = 'Άγνωστο Θέμα'

        # 3. Καθαρισμός Χώρας
        if 'country' in df.columns:
            df['country'] = df['country'].astype(str).str.strip().str.upper()
            country_map = {
                'UK': 'GB', 'GBR': 'GB', 'UNITED KINGDOM': 'GB', 'GREAT BRITAIN': 'GB',
                'FR': 'FR', 'FRA': 'FR', 'FRANCE': 'FR', 'NAN': 'ΑΓΝΩΣΤΗ', 'NONE': 'ΑΓΝΩΣΤΗ'
            }
            df['country'] = df['country'].replace(country_map)
            
        # 4. Καθαρισμός Έτους
        df['year_val'] = 0
        if 'year' in df.columns:
            df['year_val'] = pd.to_numeric(df['year'], errors='coerce').fillna(0)
        if 'date' in df.columns:
            mask_zero = df['year_val'] == 0
            if mask_zero.any():
                extracted = df.loc[mask_zero, 'date'].astype(str).str.extract(r'(18[23]\d)')[0]
                df.loc[mask_zero, 'year_val'] = pd.to_numeric(extracted, errors='coerce').fillna(0)
        df.loc[(df['year_val'] < 1821) | (df['year_val'] > 1832), 'year_val'] = 0
        
        # 5. ΚΑΝΟΝΙΚΟΠΟΙΗΣΗ ΟΝΤΟΤΗΤΩΝ (NER NORMALIZATION)
        if 'entities_persons' in df.columns:
            df['entities_persons'] = df['entities_persons'].apply(lambda x: normalize_entities(x, PERSON_ALIASES))
        else:
            df['entities_persons'] = ''
            
        if 'entities_locations' in df.columns:
            df['entities_locations'] = df['entities_locations'].apply(lambda x: normalize_entities(x, LOC_ALIASES))
        else:
            df['entities_locations'] = ''
            
        return df, raw_relevance
    except Exception as e:
        st.error(f"Σφάλμα: {e}")
        return pd.DataFrame(), pd.Series()

df_main, raw_relevance = load_main_data()

if df_main.empty:
    st.warning("Αναμονή για φόρτωση δεδομένων ή το αρχείο είναι άδειο...")
    st.stop()

# --- ΠΛΑΪΝΗ ΜΠΑΡΑ (SIDEBAR) ΦΙΛΤΡΩΝ ---
st.sidebar.header("🎛️ Φίλτρα Ανάλυσης")

valid_countries = sorted([c for c in df_main['country'].unique() if c != 'ΑΓΝΩΣΤΗ'])
if 'ΑΓΝΩΣΤΗ' in df_main['country'].unique(): valid_countries.append('ΑΓΝΩΣΤΗ')
sel_countries = st.sidebar.multiselect("Χώρες:", valid_countries, default=[c for c in valid_countries if c != 'ΑΓΝΩΣΤΗ'])

v_years = df_main[df_main['year_val'] > 0]['year_val']
min_y, max_y = int(v_years.min()), int(v_years.max())
sel_years = st.sidebar.slider("Περίοδος:", min_y, max_y, (min_y, max_y))

sel_stances = st.sidebar.multiselect("Στάση (Stance):", sorted(df_main['ai_stance'].unique()), default=sorted(df_main['ai_stance'].unique()))
sel_topics = st.sidebar.multiselect("Θέμα (Topic):", sorted(df_main['ai_topic'].unique()), default=[])

y_filt = (df_main['year_val'] >= sel_years[0]) & (df_main['year_val'] <= sel_years[1])
if sel_years[0] == min_y and sel_years[1] == max_y: y_filt = y_filt | (df_main['year_val'] == 0)

df_filt = df_main[(df_main['country'].isin(sel_countries)) & y_filt & (df_main['ai_stance'].isin(sel_stances))]
if sel_topics: df_filt = df_filt[df_filt['ai_topic'].isin(sel_topics)]

st.sidebar.divider()
st.sidebar.download_button("💾 Λήψη Δεδομένων", df_filt.to_csv(index=False, encoding='utf-8-sig'), "Filtered_Data.csv")

# --- UI ΕΠΙΚΕΦΑΛΙΔΑ ---
st.title("🏛️ Ψηφιακό Παράρτημα: Διακρατικές Ροές Πληροφορίας")
st.markdown(f"**Ενεργό Corpus:** {len(df_filt):,} / {len(df_main):,} Άρθρα | **Περίοδος:** {sel_years[0]} - {sel_years[1]}")
st.divider()

color_map = {'GB': '#1f77b4', 'FR': '#d62728', 'ΑΓΝΩΣΤΗ': '#7f7f7f'}

# --- ΚΑΡΤΕΛΕΣ ---
t1, t2, t3, t4, t5, t6 = st.tabs(["📊 Επισκόπηση", "📰 Εκδοτικό Τοπίο", "🧠 Θεματολογία", "🌍 Ροές", "👥 Οντότητες", "🔍 Αρχείο"])

with t1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Άρθρα", f"{len(df_filt):,}")
    c2.metric("Εφημερίδες", df_filt['newspaper_title'].nunique() if 'newspaper_title' in df_filt.columns else 0)
    c3.metric("Αναφορές Προσώπων", sum(df_filt['entities_persons'].str.count(',') + 1) if 'entities_persons' in df_filt.columns else 0)
    c4.metric("Αναφορές Τόπων", sum(df_filt['entities_locations'].str.count(',') + 1) if 'entities_locations' in df_filt.columns else 0)
    
    st.divider()
    
    c_pie, c_line = st.columns([1, 2])
    with c_pie:
        st.subheader("📊 Κατανομή Σχετικότητας")
        st.caption("Από το σύνολο του αρχικού αρχείου")
        if not raw_relevance.empty:
            fig_stats = px.pie(values=raw_relevance.values, names=raw_relevance.index, hole=0.4, 
                               color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig_stats, use_container_width=True)
            
    with c_line:
        st.subheader("📈 Όγκος Δημοσιεύσεων ανά Έτος")
        st.caption("Μόνο για το Ενεργό Corpus (Directly Relevant)")
        if not df_filt.empty:
            df_v = df_filt[df_filt['year_val'] > 0].groupby(['year_val', 'country']).size().reset_index(name='c')
            fig_v = px.line(df_v, x='year_val', y='c', color='country', markers=True, color_discrete_map=color_map)
            st.plotly_chart(fig_v, use_container_width=True)
    
    st.divider()
    
    c5, c6 = st.columns(2)
    with c5:
        st.subheader("⚖️ Πολιτική Στάση ανά Χώρα")
        fig_s = px.sunburst(df_filt, path=['country', 'ai_stance'], color='country', color_discrete_map=color_map)
        st.plotly_chart(fig_s, use_container_width=True)
    with c6:
        st.subheader("⏳ Εξέλιξη Στάσης")
        df_ts = df_filt[df_filt['year_val'] > 0].groupby(['year_val', 'ai_stance']).size().reset_index(name='c')
        fig_ts = px.line(df_ts, x='year_val', y='c', color='ai_stance', markers=True)
        st.plotly_chart(fig_ts, use_container_width=True)

with t2:
    st.subheader("📰 Πολιτική Γραμμή Κορυφαίων Εφημερίδων")
    if 'newspaper_title' in df_filt.columns and not df_filt.empty:
        top_np = df_filt['newspaper_title'].value_counts().nlargest(20).index
        df_np = df_filt[df_filt['newspaper_title'].isin(top_np)].groupby(['newspaper_title', 'ai_stance']).size().reset_index(name='count')
        fig_np = px.bar(df_np, x='count', y='newspaper_title', color='ai_stance', orientation='h')
        fig_np.update_layout(yaxis={'categoryorder':'total ascending'}, barmode='stack')
        st.plotly_chart(fig_np, use_container_width=True, height=600)

with t3:
    st.subheader("🌊 Εξέλιξη Κυρίαρχων Θεμάτων")
    if 'ai_topic' in df_filt.columns and not df_filt.empty:
        top_t = df_filt['ai_topic'].value_counts().nlargest(10).index
        df_t_time = df_filt[(df_filt['year_val'] > 0) & (df_filt['ai_topic'].isin(top_t))].groupby(['year_val', 'ai_topic']).size().reset_index(name='c')
        if not df_t_time.empty:
            fig_a = px.area(df_t_time, x='year_val', y='c', color='ai_topic')
            st.plotly_chart(fig_a, use_container_width=True)

with t4:
    st.subheader("🌍 Χαρτογράφηση Ροής (Origin ➔ Publication)")
    if 'news_origin' in df_filt.columns and 'publication_place' in df_filt.columns and not df_filt.empty:
        f_df = df_filt.dropna(subset=['news_origin', 'publication_place'])
        f_grp = f_df.groupby(['news_origin', 'publication_place']).size().reset_index(name='c')
        f_top = f_grp.sort_values('c', ascending=False).head(80)
        
        if not f_top.empty:
            nds = list(pd.concat([f_top['news_origin'], f_top['publication_place']]).unique())
            n_m = {n: i for i, n in enumerate(nds)}
            fig_sk = go.Figure(go.Sankey(
                node=dict(pad=15, thickness=20, label=nds, color="#1f77b4"),
                link=dict(source=f_top['news_origin'].map(n_m), target=f_top['publication_place'].map(n_m), value=f_top['c'], color="rgba(100,100,255,0.3)")
            ))
            fig_sk.update_layout(height=700)
            st.plotly_chart(fig_sk, use_container_width=True)

with t5:
    st.markdown("Τα ονόματα έχουν κανονικοποιηθεί (π.χ. Ibrahim Pacha -> Ibrahim Pasha).")
    c7, c8 = st.columns(2)
    def plot_ner(column, color_scale):
        if column in df_filt.columns and not df_filt.empty:
            items = df_filt[column].dropna().astype(str).str.split(',').explode().str.strip()
            items = items[(items != '') & (~items.str.lower().isin(['nan', 'none', 'unknown']))]
            if not items.empty:
                t_items = items.value_counts().head(20).reset_index()
                t_items.columns = ['Οντότητα', 'Αναφορές']
                f = px.bar(t_items, x='Αναφορές', y='Οντότητα', orientation='h', color='Αναφορές', color_continuous_scale=color_scale)
                f.update_layout(yaxis={'categoryorder':'total ascending'})
                return f
        return None

    with c7:
        st.subheader("👤 Top 20 Πρόσωπα")
        f_p = plot_ner('entities_persons', 'Teal')
        if f_p: st.plotly_chart(f_p, use_container_width=True)
    with c8:
        st.subheader("📍 Top 20 Τοποθεσίες")
        f_l = plot_ner('entities_locations', 'Oranges')
        if f_l: st.plotly_chart(f_l, use_container_width=True)

with t6:
    st.subheader("🔍 Αναζήτηση στο Κείμενο")
    if 'content' in df_filt.columns:
        sq = st.text_input("Λέξη-κλειδί:")
        if sq:
            r = df_filt[df_filt['content'].astype(str).str.contains(sq, case=False, na=False)]
            st.write(f"**Βρέθηκαν {len(r)} άρθρα.**")
            if not r.empty:
                st.dataframe(r[['newspaper_title', 'date', 'country', 'ai_topic', 'ai_stance']].head(100), use_container_width=True)
                sel_a = st.selectbox("Επίλεξε άρθρο:", r['newspaper_title'].astype(str) + " (" + r['date'].astype(str) + ")")
                if sel_a:
                    st.info(r[r['newspaper_title'].astype(str) + " (" + r['date'].astype(str) + ")" == sel_a]['content'].values[0])
