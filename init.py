from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo
from anki.hooks import addHook
import json
import os

# JLPT level requirements
jlptLevels = {
    "N5": {"vocab": 800, "grammar": 100},
    "N4": {"vocab": 1500, "grammar": 200},
    "N3": {"vocab": 3750, "grammar": 350},
    "N2": {"vocab": 6000, "grammar": 500},
    "N1": {"vocab": 10000, "grammar": 700}
}

# Simple data storage
addonPath = os.path.dirname(__file__)
dataFile = os.path.join(addonPath, "progress_data.json")

def loadProgressData():
    if os.path.exists(dataFile):
        with open(dataFile, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def saveProgressData(data):
    with open(dataFile, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def analyzeCards():
    # Get all cards from deck
    deckName = mw.col.decks.current()['name']
    cardIds = mw.col.find_cards(f'deck:"{deckName}"')
    
    vocabCount = 0
    grammarCount = 0
    
    # Count cards by type
    for cid in cardIds:
        card = mw.col.get_card(cid)
        note = card.note()
        
        # Simple classification based on tags or note type
        tags = note.tags
        noteType = note.note_type()['name'].lower()
        
        if 'grammar' in tags or 'grammar' in noteType:
            grammarCount += 1
        else:
            vocabCount += 1
    
    return vocabCount, grammarCount

def calculateProgress(vocabCount, grammarCount):
    progress = {}
    
    for level, requirements in jlptLevels.items():
        vocabPercent = min(100, (vocabCount / requirements['vocab']) * 100)
        grammarPercent = min(100, (grammarCount / requirements['grammar']) * 100)
        
        progress[level] = {
            'vocab': vocabPercent,
            'grammar': grammarPercent,
            'vocabCount': vocabCount,
            'grammarCount': grammarCount,
            'vocabNeeded': requirements['vocab'],
            'grammarNeeded': requirements['grammar']
        }
    
    return progress

class ProgressBar(QWidget):
    def __init__(self, level, progress, parent=None):
        super().__init__(parent)
        self.level = level
        self.progress = progress
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Level label
        levelLabel = QLabel(self.level)
        levelLabel.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(levelLabel)
        
        # Vocab progress bar
        vocabBar = QProgressBar()
        vocabBar.setValue(int(self.progress['vocab']))
        vocabBar.setFormat(f"Vocab: {self.progress['vocabCount']}/{self.progress['vocabNeeded']}")
        vocabBar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        layout.addWidget(vocabBar)
        
        # Grammar progress bar
        grammarBar = QProgressBar()
        grammarBar.setValue(int(self.progress['grammar']))
        grammarBar.setFormat(f"Grammar: {self.progress['grammarCount']}/{self.progress['grammarNeeded']}")
        grammarBar.setStyleSheet("QProgressBar::chunk { background-color: #2196F3; }")
        layout.addWidget(grammarBar)
        
        # Click for details
        self.setLayout(layout)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event):
        showDetails(self.level, self.progress)

def showDetails(level, progress):
    # Show detailed info
    vocabNeeded = progress['vocabNeeded'] - progress['vocabCount']
    grammarNeeded = progress['grammarNeeded'] - progress['grammarCount']
    
    msg = f"{level} Progress Details\n\n"
    msg += f"Vocabulary: {progress['vocabCount']}/{progress['vocabNeeded']}\n"
    msg += f"Need {max(0, vocabNeeded)} more vocab cards\n\n"
    msg += f"Grammar: {progress['grammarCount']}/{progress['grammarNeeded']}\n"
    msg += f"Need {max(0, grammarNeeded)} more grammar cards\n"
    
    showInfo(msg)

class JLPTDashboard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JLPT Progress Dashboard")
        self.setMinimumWidth(500)
        self.setupUI()
    
    def setupUI(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("JLPT Progress Tracker")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Analyze current deck
        vocabCount, grammarCount = analyzeCards()
        progress = calculateProgress(vocabCount, grammarCount)
        
        # Summary
        summary = QLabel(f"Total Cards: {vocabCount + grammarCount} (Vocab: {vocabCount}, Grammar: {grammarCount})")
        summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(summary)
        
        layout.addSpacing(20)
        
        # Progress bars for each level
        for level in ['N5', 'N4', 'N3', 'N2', 'N1']:
            progressBar = ProgressBar(level, progress[level])
            layout.addWidget(progressBar)
            layout.addSpacing(10)
        
        # Refresh button
        refreshBtn = QPushButton("Refresh")
        refreshBtn.clicked.connect(self.refresh)
        layout.addWidget(refreshBtn)
        
        self.setLayout(layout)
    
    def refresh(self):
        self.close()
        showDashboard()

def showDashboard():
    dashboard = JLPTDashboard(mw)
    dashboard.exec()

# Add menu item
action = QAction("JLPT Progress", mw)
action.triggered.connect(showDashboard)
mw.form.menuTools.addAction(action)