@st.cache_data
def load_main_data():
    try:
        with zipfile.ZipFile("THESIS_WITH_ORIENTATION.csv.zip", 'r') as z:
            csv_files = [
                name for name in z.namelist()
                if not name.startswith('__MACOSX')
                and not name.startswith('._')
                and name.endswith('.csv')
            ]
            if not csv_files:
                st.error("Δεν βρέθηκε CSV μέσα στο zip.")
                return pd.DataFrame()

            real_file_name = csv_files[0]

            # Διαβάζουμε τα bytes μία φορά για να μπορούμε να δοκιμάσουμε δύο separators
            with z.open(real_file_name) as f:
                raw_bytes = f.read()

        # Δοκιμή με κόμμα
        df = pd.read_csv(
            io.BytesIO(raw_bytes),
            sep=',',
            low_memory=False,
            encoding='utf-8-sig',
            on_bad_lines='skip'
        )

        # Αν έβγαλε <3 στήλες, δοκιμή με ερωτηματικό
        if len(df.columns) < 3:
            df = pd.read_csv(
                io.BytesIO(raw_bytes),
                sep=';',
                low_memory=False,
                encoding='utf-8-sig',
                on_bad_lines='skip'
            )

        # Καθαρισμός ονομάτων στηλών
        df.columns = df.columns.str.lower().str.strip()

        # Φιλτράρισμα directly_relevant
        if 'ai_relevance' in df.columns:
            df = df[
                df['ai_relevance'].astype(str).str.lower().str.strip()
                == 'directly_relevant'
            ].copy()

        # Ημερομηνία: "Monday 01 January 1821" → πρώτα εξάγουμε το year
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')

        # Για date: το format με weekday δεν παρσάρεται άμεσα
        # Εξάγουμε ημερομηνία αφαιρώντας το weekday prefix
        if 'date' in df.columns:
            # "Monday 01 January 1821" → "01 January 1821"
            df['date_clean'] = df['date'].astype(str).str.replace(
                r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+',
                '', regex=True
            )
            df['date_parsed'] = pd.to_datetime(
                df['date_clean'],
                format='%d %B %Y',
                errors='coerce'
            )
            # Fallback για εγγραφές που έχουν ήδη καθαρή μορφή
            mask_failed = df['date_parsed'].isna()
            df.loc[mask_failed, 'date_parsed'] = pd.to_datetime(
                df.loc[mask_failed, 'date'],
                errors='coerce'
            )
            df.drop(columns=['date_clean'], inplace=True)

        return df

    except FileNotFoundError:
        st.error("Το αρχείο THESIS_WITH_ORIENTATION.csv.zip δεν βρέθηκε.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης: {e}")
        return pd.DataFrame()
