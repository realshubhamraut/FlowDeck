"""
Utility functions for fetching motivational quotes
"""
import requests
from functools import lru_cache
import random

# Fallback quotes in case API is unavailable
FALLBACK_QUOTES = [
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"text": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius"},
    {"text": "Everything you've ever wanted is on the other side of fear.", "author": "George Addair"},
    {"text": "Success is not how high you have climbed, but how you make a positive difference to the world.", "author": "Roy T. Bennett"},
    {"text": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
    {"text": "The only impossible journey is the one you never begin.", "author": "Tony Robbins"},
    {"text": "Your limitation—it's only your imagination.", "author": "Unknown"},
    {"text": "Great things never come from comfort zones.", "author": "Unknown"},
    {"text": "Dream it. Wish it. Do it.", "author": "Unknown"},
    {"text": "Success doesn't just find you. You have to go out and get it.", "author": "Unknown"},
    {"text": "The harder you work for something, the greater you'll feel when you achieve it.", "author": "Unknown"},
    {"text": "Dream bigger. Do bigger.", "author": "Unknown"},
    {"text": "Don't stop when you're tired. Stop when you're done.", "author": "Unknown"},
    {"text": "Wake up with determination. Go to bed with satisfaction.", "author": "Unknown"},
    {"text": "Do something today that your future self will thank you for.", "author": "Unknown"},
    {"text": "Little things make big days.", "author": "Unknown"},
    {"text": "It's going to be hard, but hard does not mean impossible.", "author": "Unknown"},
]


@lru_cache(maxsize=1)
def get_quote_from_api():
    """
    Fetch a random motivational quote from ZenQuotes API
    Cached to avoid hitting API repeatedly
    """
    try:
        # Using ZenQuotes API - free, no auth required
        response = requests.get('https://zenquotes.io/api/random', timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return {
                    'text': data[0].get('q', ''),
                    'author': data[0].get('a', 'Unknown')
                }
    except Exception as e:
        print(f"Error fetching quote from API: {e}")
    
    return None


def get_daily_quote():
    """
    Get a daily motivational quote
    Tries API first, falls back to local quotes
    """
    # Try to get from API
    quote = get_quote_from_api()
    
    # If API fails, use fallback
    if not quote:
        quote = random.choice(FALLBACK_QUOTES)
    
    return quote


def get_birthday_message(name, age=None):
    """
    Generate a personalized birthday message
    """
    messages = [
        f"🎉 Happy Birthday {name}! Wishing you a fantastic day filled with joy and success!",
        f"🎂 Happy Birthday {name}! May this year bring you closer to your dreams!",
        f"🎈 Cheers to {name}! Hope your special day is as amazing as you are!",
        f"🎊 Happy Birthday {name}! May your day be filled with laughter and happiness!",
        f"🌟 Wishing {name} a wonderful birthday! Here's to another year of great achievements!",
    ]
    
    if age:
        messages.extend([
            f"🎉 Happy {age}th Birthday {name}! Make this year count!",
            f"🎂 Celebrating {age} years of {name}! Here's to many more!",
        ])
    
    return random.choice(messages)
