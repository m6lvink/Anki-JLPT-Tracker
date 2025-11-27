import json
import os
from datetime import datetime

def getTimestamp():
    # Return YYYY-MM-DD
    return datetime.now().strftime("%Y-%m-%d")

def saveSnapshot(vocabCount, grammarCount, dataFilePath):
    # Append stats to history
    historyList = []
    directoryPath = os.path.dirname(dataFilePath)
    
    os.makedirs(directoryPath, exist_ok=True)
    
    isFilePresent = os.path.exists(dataFilePath)
    if isFilePresent:
        try:
            with open(dataFilePath, 'r', encoding='utf-8') as fileObj:
                dataMap = json.load(fileObj)
                historyList = dataMap.get('history', [])
        except:
            historyList = []
    
    currentDate = getTimestamp()
    hasEntryForToday = False
    
    if len(historyList) > 0:
        lastEntry = historyList[-1]
        if lastEntry['date'] == currentDate:
            hasEntryForToday = True
            
    if hasEntryForToday:
        historyList[-1]['vocab'] = vocabCount
        historyList[-1]['grammar'] = grammarCount
    else:
        newEntry = {
            'date': currentDate,
            'vocab': vocabCount,
            'grammar': grammarCount
        }
        historyList.append(newEntry)
    
    # Cap size
    if len(historyList) > 365:
        historyList = historyList[-365:]

    with open(dataFilePath, 'w', encoding='utf-8') as fileObj:
        json.dump({'history': historyList}, fileObj, indent=2)

def getProgressHistory(dataFilePath):
    # Read history safely
    if not os.path.exists(dataFilePath):
        return []
        
    try:
        with open(dataFilePath, 'r', encoding='utf-8') as fileObj:
            dataMap = json.load(fileObj)
            return dataMap.get('history', [])
    except:
        return []

def calculateGrowthRate(historyList):
    # Average daily increase over 2 weeks
    if len(historyList) < 2:
        return 0
    
    subsetList = historyList[-14:]
    firstEntry = subsetList[0]
    lastEntry = subsetList[-1]
    
    totalStart = firstEntry['vocab'] + firstEntry['grammar']
    totalEnd = lastEntry['vocab'] + lastEntry['grammar']
    diff = totalEnd - totalStart
    
    dStart = datetime.strptime(firstEntry['date'], "%Y-%m-%d")
    dEnd = datetime.strptime(lastEntry['date'], "%Y-%m-%d")
    days = (dEnd - dStart).days
    
    if days > 0:
        return diff / days
    return 0

def estimateCompletionDate(curr, target, rate):
    # String estimation
    if rate <= 0: return "Unknown"
    
    remaining = target - curr
    if remaining <= 0: return "Complete!"
    
    days = remaining / rate
    if days > 365: return "> 1 year"
    
    return f"{int(days)} days"