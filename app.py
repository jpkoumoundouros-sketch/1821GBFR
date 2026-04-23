@st.cache_data
def load_main_data():
    try:
        with zipfile.ZipFile("THESIS_WITH_ORIENTATION.csv.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and not name.startswith('._') and name.endswith('.csv')]
            if not csv_files:
                return pd.DataFrame()
                
            real_file_name = csv_files[0]
            
            # Δοκιμάζουμε πρώτα με το standard κόμμα (,)
            with z.open(real_file_name) as f:
                df = pd.read_csv(f, sep=',', low_memory=False, encoding='utf-8-sig', on_bad_lines='skip')
                
                # Αν απέτυχε να βρει στήλες (έφτιαξε κάτω από 3), σημαίνει ότι το Excel σου έβαλε ερωτηματικά (;)
                if len(df.columns) < 3:
                    f.seek(0) # Πάμε το αρχείο πάλι στην αρχή
                    df = pd.read_csv(f, sep=';', low_memory=False, encoding='utf-8-sig', on_bad_lines='skip')
        
        # Καθαρισμός ονομάτων στηλών
        df.columns = df.columns.str.lower().str.strip()
        
        # Φιλτράρισμα για το Τελικό Corpus (Directly Relevant) -> ΕΔΩ ΠΡΕΠΕΙ ΝΑ ΔΟΥΜΕ ΤΑ ~55.000
        if 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης: {e}")
        return pd.DataFrame()
