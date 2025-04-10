# # Re-run due to kernel reset

# import json
# import pandas as pd
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans
# from sklearn.preprocessing import StandardScaler

# def preprocess_messages(messages):
#     if not messages:
#         return pd.DataFrame(columns=["sender", "text", "timestamp", "hour", "day"])

#     df = pd.DataFrame(messages)

#     if "text" not in df.columns or "timestamp" not in df.columns or "sender" not in df.columns:
#         raise ValueError("Expected fields missing in input messages.")

#     df = df.dropna(subset=["text", "timestamp", "sender"])
#     df["text"] = df["text"].astype(str).str.lower()
#     df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
#     df = df.dropna(subset=["timestamp"])
#     df["hour"] = df["timestamp"].dt.hour
#     df["day"] = df["timestamp"].dt.date.astype(str)

#     return df


# def extract_keywords(messages):
#     texts = [msg["text"].strip() for msg in messages if isinstance(msg, dict) and msg.get("text", "").strip()]

#     if not texts:
#         return []

#     tfidf = TfidfVectorizer(stop_words="english", max_features=10)
#     try:
#         tfidf_matrix = tfidf.fit_transform(texts)
#         keywords = tfidf.get_feature_names_out()
#         scores = tfidf_matrix.sum(axis=0).A1
#         keyword_score_pairs = sorted(zip(keywords, scores), key=lambda x: x[1], reverse=True)
#         return [kw for kw, _ in keyword_score_pairs]
#     except ValueError:
#         return []


# def cluster_users(messages):
#     df = preprocess_messages(messages)
#     if df.empty:
#         return []

#     user_activity = df.groupby("sender").agg({"text": "count", "hour": lambda x: x.mode()[0]})
#     user_activity.columns = ["message_count", "most_active_hour"]
#     scaler = StandardScaler()
#     X = scaler.fit_transform(user_activity)
#     kmeans = KMeans(n_clusters=min(3, len(user_activity)), random_state=42).fit(X)
#     user_activity["cluster"] = kmeans.labels_
#     return user_activity.reset_index().to_dict(orient="records")


# def chat_volume_by_hour(messages):
#     df = preprocess_messages(messages)
#     if df.empty:
#         return {}

#     volume = df.groupby(["day", "hour"]).size().unstack(fill_value=0)
#     return volume.to_dict(orient="index")


# def perform_ml_analysis(messages):
#     return {
#         "tfidf_keywords": extract_keywords(messages),
#         "user_clusters": cluster_users(messages),
#         "chat_heatmap": chat_volume_by_hour(messages)
#     }


# sample_messages = [
#     {"text": "Let's ship the product this week", "timestamp": "2024-04-01T13:45:00", "sender": "A"},
#     {"text": "Product page redesign looks great", "timestamp": "2024-04-01T14:10:00", "sender": "B"},
#     {"text": "Can we meet on Thursday?", "timestamp": "2024-04-02T10:00:00", "sender": "A"},
#     {"text": "Reminder: Submit your reports", "timestamp": "2024-04-02T16:30:00", "sender": "C"},
# ]

# analysis = perform_ml_analysis(sample_messages)
# analysis_json = json.dumps(analysis, indent=2, default=str)
# analysis_json[:1000]
