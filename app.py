df.columns = df.columns.str.lower().str.strip()

        # DEBUG: δες τι τιμές έχει το ai_relevance ΠΡΙΝ το φιλτράρισμα
        if 'ai_relevance' in df.columns:
            st.write("Μοναδικές τιμές ai_relevance:", 
                     df['ai_relevance'].value_counts().to_dict())
        else:
            st.write("Στήλες που βρέθηκαν:", list(df.columns))
