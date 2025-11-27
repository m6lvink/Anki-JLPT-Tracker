from aqt.qt import *
from aqt import mw
from . import db_utils, config_manager

class ColorButton(QPushButton):
    def __init__(self, colorString, parentWidget=None):
        super().__init__(parentWidget)
        self.currentColor = colorString
        self.setMaximumWidth(80)
        self.updateButtonAppearance(colorString)
        self.clicked.connect(self.pickNewColor)
        
    def updateButtonAppearance(self, colorString):
        self.currentColor = colorString
        self.setStyleSheet(f"background:{colorString};border:1px solid #666;border-radius:3px;")
        self.setText("")
        
    def pickNewColor(self):
        pickedColor = QColorDialog.getColor(QColor(self.currentColor), self)
        if pickedColor.isValid():
            self.updateButtonAppearance(pickedColor.name())

class ConfigDialog(QDialog):
    def __init__(self, userConfigPath, parentWidget=None):
        super().__init__(parentWidget)
        self.setWindowTitle("JLPT Settings")
        self.resize(400, 500)
        self.configPath = userConfigPath
        self.userConfig = config_manager.loadUserConfig(userConfigPath)
        self.initInterface()
    
    def initInterface(self):
        mainLayout = QVBoxLayout()
        
        # Level
        levelLayout = QHBoxLayout()
        levelLayout.addWidget(QLabel("Level:"))
        self.levelCombo = QComboBox()
        self.levelCombo.addItems(["N5", "N4", "N3", "N2", "N1"])
        self.levelCombo.setCurrentText(self.userConfig.get("targetLevel", "N3"))
        levelLayout.addWidget(self.levelCombo)
        mainLayout.addLayout(levelLayout)

        # Deck
        deckLayout = QHBoxLayout()
        deckLayout.addWidget(QLabel("Deck:"))
        self.deckCombo = QComboBox()
        self.deckCombo.addItem("(Current deck)")
        
        allDecks = mw.col.decks.all()
        deckNames = [d['name'] for d in allDecks]
        self.deckCombo.addItems(deckNames)
        
        savedDeck = self.userConfig.get("trackedDeck", "")
        if savedDeck != "":
            self.deckCombo.setCurrentText(savedDeck)
            
        deckLayout.addWidget(self.deckCombo)
        mainLayout.addLayout(deckLayout)

        # Date
        dateLayout = QHBoxLayout()
        dateLayout.addWidget(QLabel("Date (YYYY-MM-DD):"))
        self.dateInput = QLineEdit()
        self.dateInput.setText(self.userConfig.get("deadline", ""))
        dateLayout.addWidget(self.dateInput)
        mainLayout.addLayout(dateLayout)
        
        # Colors
        colorLayout = QHBoxLayout()
        self.vocabBtn = ColorButton(self.userConfig.get("vocabColor", "#4CAF50"))
        self.grammarBtn = ColorButton(self.userConfig.get("grammarColor", "#2196F3"))
        colorLayout.addWidget(QLabel("Vocab:"))
        colorLayout.addWidget(self.vocabBtn)
        colorLayout.addWidget(QLabel("Grammar:"))
        colorLayout.addWidget(self.grammarBtn)
        mainLayout.addLayout(colorLayout)

        # Note Types
        groupSettings = QGroupBox("Note Types")
        scrollLayout = QVBoxLayout()
        scrollArea = QScrollArea()
        scrollWidget = QWidget()
        listLayout = QVBoxLayout()
        
        self.comboMap = {}
        noteTypes = db_utils.getAllNoteTypes()
        currentNoteSettings = self.userConfig.get("noteTypes", {})
        
        for noteName in noteTypes:
            rowLayout = QHBoxLayout()
            rowLayout.addWidget(QLabel(noteName))
            typeSelector = QComboBox()
            typeSelector.addItems(["vocab", "grammar", "ignore"])
            savedType = currentNoteSettings.get(noteName, "vocab")
            typeSelector.setCurrentText(savedType)
            self.comboMap[noteName] = typeSelector
            rowLayout.addWidget(typeSelector)
            listLayout.addLayout(rowLayout)
            
        scrollWidget.setLayout(listLayout)
        scrollArea.setWidget(scrollWidget)
        scrollArea.setWidgetResizable(True)
        scrollLayout.addWidget(scrollArea)
        groupSettings.setLayout(scrollLayout)
        mainLayout.addWidget(groupSettings)

        # Save
        saveBtn = QPushButton("Save")
        saveBtn.clicked.connect(self.saveSettings)
        mainLayout.addWidget(saveBtn)
        self.setLayout(mainLayout)

    def saveSettings(self):
        # Gather Data
        selectedLevel = self.levelCombo.currentText()
        selectedDeck = self.deckCombo.currentText()
        deckValue = ""
        
        if selectedDeck != "(Current deck)":
            deckValue = selectedDeck
            
        newNoteTypes = {}
        for (name, widget) in self.comboMap.items():
            newNoteTypes[name] = widget.currentText()
            
        self.userConfig.update({
            "targetLevel": selectedLevel,
            "trackedDeck": deckValue,
            "deadline": self.dateInput.text(),
            "vocabColor": self.vocabBtn.currentColor,
            "grammarColor": self.grammarBtn.currentColor,
            "noteTypes": newNoteTypes
        })
        
        config_manager.saveUserConfig(self.configPath, self.userConfig)
        self.accept()
        
        if hasattr(mw, 'deckBrowser'):
            mw.deckBrowser.refresh()