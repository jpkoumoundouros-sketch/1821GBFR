df.columns = df.columns.str.lower().str.strip()

        if 'ai_relevance' in df.columns:
            # Φιλτράρισμα ανεξάρτητο κεφαλαίων/κενών/παραλλαγών
            mask = (
                df['ai_relevance']
                .astype(str)
                .str.lower()
                .str.strip()
                .str.replace('_', '')   # καλύπτει "directlyrelevant" και "directly_relevant"
                == 'directlyrelevant'
            )
            df = df[mask].copy()
            
            if df.empty:
                st.warning("Το φιλτράρισμα επέστρεψε 0 εγγραφές. "
                           "Έλεγξε τις τιμές του ai_relevance.")
