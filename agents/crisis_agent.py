def check_crisis(text):
    text = text.lower()

    keywords = [
        "suicide", "kill myself", "end my life",
        "die", "hopeless"
    ]

    return any(k in text for k in keywords)