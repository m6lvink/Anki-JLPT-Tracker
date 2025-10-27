import json
import os
from datetime import datetime

# Helper functions for progress tracking

def getTimestamp():
    return datetime.now().strftime("%Y-%m-%d")

def saveSnapshot(vocabCount, grammarCount, dataFile):
    # Load existing history
    history = []
    if os.path.exists(dataFile):
        with open(dataFile, 'r') as f:
            data = json.load(f)
            history = data.get('history', [])
    
    # Add new snapshot
    snapshot = {
        'date': getTimestamp(),
        'vocab': vocabCount,
        'grammar': grammarCount
    }
    history.append(snapshot)
    
    # Save updated history
    with open(dataFile, 'w') as f:
        json.dump({'history': history}, f, indent=2)

def getProgressHistory(dataFile):
    if not os.path.exists(dataFile):
        return []
    
    with open(dataFile, 'r') as f:
        data = json.load(f)
        return data.get('history', [])

def calculateGrowthRate(history):
    # Calculate cards added per day
    if len(history) < 2:
        return 0
    
    first = history[0]
    last = history[-1]
    
    totalCards = (last['vocab'] + last['grammar']) - (first['vocab'] + first['grammar'])
    
    # Simple days calculation
    days = len(history)
    
    return totalCards / days if days > 0 else 0

def estimateCompletionDate(currentCount, targetCount, dailyRate):
    # Estimate days to reach target
    if dailyRate <= 0:
        return "Unknown"
    
    remaining = targetCount - currentCount
    if remaining <= 0:
        return "Complete"
    
    days = remaining / dailyRate
    return f"{int(days)} days"

def categorizeByFrequency(notes):
    # Placeholder for frequency-based categorization
    # Future: use JLPT word lists to categorize
    categories = {
        'N5': 0,
        'N4': 0,
        'N3': 0,
        'N2': 0,
        'N1': 0,
        'unknown': 0
    }
    
    for note in notes:
        # Simple categorization based on tags
        tags = note.tags
        foundLevel = False
        
        for level in ['N5', 'N4', 'N3', 'N2', 'N1']:
            if level.lower() in [t.lower() for t in tags]:
                categories[level] += 1
                foundLevel = True
                break
        
        if not foundLevel:
            categories['unknown'] += 1
    
    return categories