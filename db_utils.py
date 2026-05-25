from aqt import mw
from . import consts

def getAllNoteTypes():
    modelList = mw.col.models.all()
    nameList = [model['name'] for model in modelList]
    return sorted(nameList)

def getCardCounts(configMap):
    # Get IDs
    trackedIds = configMap.get("trackedDeckIds", [])
    
    # Fallback for legacy
    if not trackedIds:
        legacyName = configMap.get("trackedDeck", "")
        if legacyName:
            legacyId = mw.col.decks.id(legacyName)
            if legacyId:
                trackedIds = [legacyId]

    # If still no decks --> return zero
    if not trackedIds:
        return (0, 0)
        
    allDecks = mw.col.decks.all()
    uniqueDeckIds = set()
    
    # ID/Children resolution
    for deckId in trackedIds:
        # Check if deck still exists 
        deckObj = mw.col.decks.get(deckId)
        if deckObj is None:
            continue
            
        uniqueDeckIds.add(deckId)
        parentName = deckObj['name']
        
        # Add all subdecks of parent
        for d in allDecks:
            if d['name'].startswith(parentName + "::"):
                uniqueDeckIds.add(d['id'])
                
    if not uniqueDeckIds:
        return (0, 0)
    
    deckIdList = list(uniqueDeckIds)
    
    # SQL Query
    idPlaceholder = ','.join('?' * len(deckIdList))
    formattedQuery = consts.SQL_CARD_COUNTS.format(idPlaceholder)
    
    try:
        queryResults = mw.col.db.all(formattedQuery, *deckIdList)
    except Exception as e:
        # Log error to console --> avoid crash
        print(f"JLPT Tracker DB Error: {e}")
        return (0, 0)
    
    # Count
    noteTypeMap = configMap.get("noteTypes", {})
    vocabTotal = 0
    grammarTotal = 0
    
    for (modelId, cardCount) in queryResults:
        modelData = mw.col.models.get(modelId)
        if modelData:
            categoryType = noteTypeMap.get(modelData['name'], "vocab")
            
            isGrammar = (categoryType == "grammar")
            isVocab = (categoryType == "vocab")
            
            if isGrammar:
                grammarTotal += cardCount
            elif isVocab:
                vocabTotal += cardCount
                
    return (vocabTotal, grammarTotal)