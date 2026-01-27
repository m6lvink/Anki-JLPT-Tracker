# SQL Query for counting cards
SQL_CARD_COUNTS = """
    SELECT notes.mid, COUNT(DISTINCT notes.id) 
    FROM cards 
    JOIN notes ON cards.nid = notes.id 
    WHERE cards.did IN ({}) AND cards.reps > 0
    GROUP BY notes.mid
"""

# Default level requirements
DEFAULT_LEVELS = {
    "N5": {"vocab": 800, "grammar": 100},
    "N4": {"vocab": 1500, "grammar": 200},
    "N3": {"vocab": 3750, "grammar": 350},
    "N2": {"vocab": 6000, "grammar": 500},
    "N1": {"vocab": 10000, "grammar": 700}
}

# Default user settings
DEFAULT_USER_CONFIG = {
    "noteTypes": {}, 
    "targetLevel": "N3", 
    "deadline": "",
    "vocabColor": "#4CAF50", 
    "grammarColor": "#2196F3",
    "trackedDeckIds": [], 
    "minimized": False
}