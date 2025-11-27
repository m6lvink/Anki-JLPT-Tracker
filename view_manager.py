import os
from datetime import datetime, date
from . import progress_utils

def loadResourceText(webDir, fileName):
    fullPath = os.path.join(webDir, fileName)
    if os.path.exists(fullPath):
        try:
            with open(fullPath, 'r', encoding='utf-8') as fileObj:
                return fileObj.read()
        except:
            pass
    return ""

def generateDashboardHtml(configMap, levelDataMap, statsTuple, pathsMap):
    (vocabCount, grammarCount) = statsTuple
    webDir = pathsMap['webDir']
    historyPath = pathsMap['historyPath']
    
    targetLevel = configMap.get("targetLevel", "N3")
    
    if targetLevel not in levelDataMap:
        targetLevel = "N3"
        
    levelReqs = levelDataMap[targetLevel]
    reqVocab = levelReqs['vocab']
    reqGrammar = levelReqs['grammar']
    
    # Percentages
    vocabPct = 0.0
    if reqVocab > 0:
        rawPct = (vocabCount / reqVocab) * 100
        vocabPct = float(min(100, rawPct))
        
    grammarPct = 0.0
    if reqGrammar > 0:
        rawPct = (grammarCount / reqGrammar) * 100
        grammarPct = float(min(100, rawPct))
        
    overallPct = (vocabPct + grammarPct) / 2.0
    
    # History
    progress_utils.saveSnapshot(vocabCount, grammarCount, historyPath)
    historyList = progress_utils.getProgressHistory(historyPath)
    growthRate = progress_utils.calculateGrowthRate(historyList)
    
    estString = progress_utils.estimateCompletionDate(vocabCount+grammarCount, reqVocab+reqGrammar, growthRate)
    timeStr = f"Est: {estString}"
    
    # Deadline
    deadlineStr = configMap.get("deadline", "")
    if deadlineStr != "":
        try:
            deadlineDate = datetime.strptime(deadlineStr, "%Y-%m-%d").date()
            daysLeft = (deadlineDate - date.today()).days
            
            if daysLeft > 0:
                timeStr = f"{daysLeft} days left"
            elif daysLeft == 0:
                timeStr = "Exam Today!"
            else:
                timeStr = "Exam passed"
        except:
            timeStr = "Invalid Date"

    # Load Static CSS
    staticCss = loadResourceText(webDir, "style.css")
    
    # Dynamic CSS
    vocabColor = configMap.get("vocabColor", "#4CAF50")
    grammarColor = configMap.get("grammarColor", "#2196F3")
    
    dynamicCss = f"""
    #jlpt-vocab-fill {{ width: {vocabPct:.1f}%; background-color: {vocabColor}; }}
    #jlpt-grammar-fill {{ width: {grammarPct:.1f}%; background-color: {grammarColor}; }}
    """
    
    # HTML Body
    isMinimized = configMap.get("minimized", False)
    templateName = "pill.html" if isMinimized else "dashboard.html"
    
    htmlBody = loadResourceText(webDir, templateName)
    
    renderMap = {
        "level": targetLevel,
        "overallPct": overallPct,
        "timeStr": timeStr,
        "vocabCurr": vocabCount,
        "vocabReq": reqVocab,
        "grammarCurr": grammarCount,
        "grammarReq": reqGrammar
    }
    
    if htmlBody:
        htmlBody = htmlBody.format(**renderMap)
    else:
        htmlBody = "<div>Error loading template</div>"
        
    return "<style>" + staticCss + "\n" + dynamicCss + "</style>" + htmlBody