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

    # overall based on tracking mode
    trackingMode = configMap.get("trackingMode", "both")
    if trackingMode == "vocab":
        overallPct = vocabPct
    elif trackingMode == "grammar":
        overallPct = grammarPct
    else:
        overallPct = (vocabPct + grammarPct) / 2.0
    
    # History
    progress_utils.saveSnapshot(vocabCount, grammarCount, historyPath)
    historyList = progress_utils.getProgressHistory(historyPath)
    growthRate = progress_utils.calculateGrowthRate(historyList, trackingMode)

    # Estimate curr/target based on mode
    if trackingMode == "vocab":
        estCurr, estTarget = vocabCount, reqVocab
    elif trackingMode == "grammar":
        estCurr, estTarget = grammarCount, reqGrammar
    else:
        estCurr, estTarget = vocabCount + grammarCount, reqVocab + reqGrammar

    estString = progress_utils.estimateCompletionDate(estCurr, estTarget, growthRate)
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
    bgOpacity = configMap.get("backgroundOpacity", 1.0)

    dynamicCss = f"""
    :root {{ --jlpt-bg-opacity: {bgOpacity:.2f}; }}
    #jlpt-vocab-fill {{ width: {vocabPct:.1f}%; background-color: {vocabColor}; }}
    #jlpt-grammar-fill {{ width: {grammarPct:.1f}%; background-color: {grammarColor}; }}
    """

    # Conditional bar HTML for tracking mode
    vocabBarHtml = ""
    grammarBarHtml = ""
    if trackingMode in ("both", "vocab"):
        vocabBarHtml = (
            '<div class="jlpt-bar-row">'
            '<div class="jlpt-bar-meta">'
            f'<span>Vocab</span><span>{vocabCount} / {reqVocab}</span>'
            '</div>'
            '<div class="jlpt-track">'
            '<div id="jlpt-vocab-fill" class="jlpt-fill"></div>'
            '</div></div>'
        )
    if trackingMode in ("both", "grammar"):
        grammarBarHtml = (
            '<div class="jlpt-bar-row">'
            '<div class="jlpt-bar-meta">'
            f'<span>Grammar</span><span>{grammarCount} / {reqGrammar}</span>'
            '</div>'
            '<div class="jlpt-track">'
            '<div id="jlpt-grammar-fill" class="jlpt-fill"></div>'
            '</div></div>'
        )

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
        "grammarReq": reqGrammar,
        "vocabBarHtml": vocabBarHtml,
        "grammarBarHtml": grammarBarHtml
    }
    
    if htmlBody:
        htmlBody = htmlBody.format(**renderMap)
    else:
        htmlBody = "<div>Error loading template</div>"
        
    return "<style>" + staticCss + "\n" + dynamicCss + "</style>" + htmlBody