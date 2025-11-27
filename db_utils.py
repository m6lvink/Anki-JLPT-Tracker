from aqt import mw
from . import consts

def getAllNoteTypes():
    # Return sorted model names
    modelList = mw.col.models.all()
    nameList = [model['name'] for model in modelList]
    return sorted(nameList)

def getCardCounts(configMap):
    # Query database for counts
    trackedDeckName = configMap.get("trackedDeck", "")
    allDecks = mw.col.decks.all()
    deckNames = [d['name'] for d in allDecks]
    
    isDeckValid = (trackedDeckName != "" and trackedDeckName in deckNames)
    targetDeckName = ""
    
    if isDeckValid:
        targetDeckName = trackedDeckName
    else:
        currentDeck = mw.col.decks.current()
        if currentDeck is None:
            return (0, 0)
        targetDeckName = currentDeck['name']
    
    # Gather subdecks
    targetDeckId = mw.col.decks.id(targetDeckName)
    deckIdList = [targetDeckId]
    
    for deck in allDecks:
        isSubDeck = deck['name'].startswith(targetDeckName + "::")
        if isSubDeck:
            deckIdList.append(deck['id'])
    
    # Execute SQL
    idPlaceholder = ','.join('?' * len(deckIdList))
    formattedQuery = consts.SQL_CARD_COUNTS.format(idPlaceholder)
    
    try:
        queryResults = mw.col.db.all(formattedQuery, *deckIdList)
    except:
        return (0, 0)
    
    # Process results
    noteTypeMap = configMap.get("noteTypes", {})
    vocabTotal = 0
    grammarTotal = 0
    
    for (modelId, cardCount) in queryResults:
        modelData = mw.col.models.get(modelId)
        if modelData is not None:
            categoryType = noteTypeMap.get(modelData['name'], "vocab")
            
            isGrammar = (categoryType == "grammar")
            isVocab = (categoryType == "vocab")
            
            if isGrammar:
                grammarTotal += cardCount
            elif isVocab:
                vocabTotal += cardCount
                
    return (vocabTotal, grammarTotal)