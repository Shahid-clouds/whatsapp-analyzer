import pandas as pd
from collections import Counter
import emoji
import re

def get_basic_stats(df):
    """Returns total messages, words, media, and links."""
    total_messages = len(df)
    total_words = df['message'].apply(lambda x: len(str(x).split())).sum()
    media_count = df['message'].str.contains('<Media omitted>', na=False).sum()
    link_count = df['message'].str.contains(r'http[s]?://', na=False, regex=True).sum()
    total_members = df['author'].nunique()

    return {
        "Total Messages": total_messages,
        "Total Words": int(total_words),
        "Media Shared": int(media_count),
        "Links Shared": int(link_count),
        "Total Members": total_members
    }

def get_most_active_users(df, top_n=5):
    """Returns message count per user."""
    return df['author'].value_counts().head(top_n).reset_index()

def get_busiest_days(df):
    """Returns message count by day of week."""
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = df['day_name'].value_counts().reindex(order).fillna(0).astype(int)
    return day_counts

def get_hourly_activity(df):
    """Returns message count by hour of day."""
    return df['hour'].value_counts().sort_index()

def get_monthly_timeline(df):
    """Returns message count per month."""
    return df.groupby('month').size().reset_index(name='messages')

def get_most_common_words(df, top_n=20):
    """Returns most common words excluding stopwords."""
    stopwords = set([
        'the', 'a', 'an', 'is', 'it', 'in', 'on', 'at', 'to', 'for',
        'and', 'or', 'but', 'of', 'with', 'this', 'that', 'was', 'are',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'shall', 'can',
        'i', 'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us',
        'them', 'my', 'your', 'his', 'our', 'their', 'its', 'what', 'how',
        'when', 'where', 'who', 'which', 'not', 'no', 'so', 'if', 'as',
        'media', 'omitted', 'message', 'deleted', 'null', 'ok', 'okay',
        'ha', 'haha', 'lol', 'ya', 'na', 'ka', 'la', 'da', 'ah'
    ])

    all_words = []
    for msg in df['message']:
        msg = str(msg).lower()
        msg = re.sub(r'http\S+', '', msg)  # remove links
        words = re.findall(r'\b[a-z]{3,}\b', msg)
        all_words.extend([w for w in words if w not in stopwords])

    word_freq = Counter(all_words).most_common(top_n)
    return pd.DataFrame(word_freq, columns=['word', 'count'])

def get_emoji_stats(df, top_n=10):
    """Returns most used emojis."""
    all_emojis = []
    for msg in df['message']:
        all_emojis.extend([c for c in str(msg) if c in emoji.EMOJI_DATA])

    if not all_emojis:
        return pd.DataFrame(columns=['emoji', 'count'])

    emoji_freq = Counter(all_emojis).most_common(top_n)
    return pd.DataFrame(emoji_freq, columns=['emoji', 'count'])

def get_user_word_count(df):
    """Average words per message per user."""
    df = df.copy()
    df['word_count'] = df['message'].apply(lambda x: len(str(x).split()))
    return df.groupby('author')['word_count'].mean().round(1).sort_values(ascending=False).head(8)
