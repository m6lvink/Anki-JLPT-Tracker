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
        try:
            # Default to current color if parsing fail
            initialColor = QColor(self.currentColor)
            if not initialColor.isValid():
                initialColor = QColor("#FFFFFF")
                
            pickedColor = QColorDialog.getColor(initialColor, self)
            
            if pickedColor.isValid():
                self.updateButtonAppearance(pickedColor.name())
        except Exception:
            pass

class ConfigDialog(QDialog):
    def __init__(self, userConfigPath, parentWidget=None):
        super().__init__(parentWidget)
        self.setWindowTitle("JLPT Settings")
        self.resize(450, 600)
        self.configPath = userConfigPath
        self.userConfig = config_manager.loadUserConfig(userConfigPath)
        self.initInterface()
    
    def initInterface(self):
        mainLayout = QVBoxLayout()
        
        # Level select
        levelLayout = QHBoxLayout()
        levelLayout.addWidget(QLabel("Target Level:"))
        self.levelCombo = QComboBox()
        self.levelCombo.addItems(["N5", "N4", "N3", "N2", "N1"])
        self.levelCombo.setCurrentText(self.userConfig.get("targetLevel", "N3"))
        levelLayout.addWidget(self.levelCombo)
        mainLayout.addLayout(levelLayout)

        # Deck selection 
        deckGroup = QGroupBox("Tracked Decks")
        deckLayout = QVBoxLayout()
        
        self.deckListWidget = QListWidget()
        self.deckListWidget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        
        # Load Decks from Anki
        allDecks = mw.col.decks.all()
        
        # Get current IDs
        currentIds = self.userConfig.get("trackedDeckIds", [])
        
        # If list is empty --> check for legacy string and convert
        if not currentIds:
            legacyName = self.userConfig.get("trackedDeck", "")
            if legacyName:
                legacyId = mw.col.decks.id(legacyName)
                if legacyId:
                    currentIds = [legacyId]

        # Adds lists of decks
        for deck in allDecks:
            deckName = deck['name']
            deckId = deck['id']
            
            item = QListWidgetItem(deckName)
            # Store ID in hidden dat
            item.setData(Qt.ItemDataRole.UserRole, deckId)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            # Check if ID is in list
            if deckId in currentIds:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                
            self.deckListWidget.addItem(item)
            
        deckLayout.addWidget(self.deckListWidget)
        deckGroup.setLayout(deckLayout)
        mainLayout.addWidget(deckGroup)

        # Date Input
        dateLayout = QHBoxLayout()
        dateLayout.addWidget(QLabel("Exam Date (YYYY-MM-DD):"))
        self.dateInput = QLineEdit()
        self.dateInput.setText(self.userConfig.get("deadline", ""))
        dateLayout.addWidget(self.dateInput)
        mainLayout.addLayout(dateLayout)
        
        # Color select
        colorLayout = QHBoxLayout()
        self.vocabBtn = ColorButton(self.userConfig.get("vocabColor", "#4CAF50"))
        self.grammarBtn = ColorButton(self.userConfig.get("grammarColor", "#2196F3"))
        colorLayout.addWidget(QLabel("Vocab Color:"))
        colorLayout.addWidget(self.vocabBtn)
        colorLayout.addWidget(QLabel("Grammar Color:"))
        colorLayout.addWidget(self.grammarBtn)
        mainLayout.addLayout(colorLayout)

        # Note Types
        groupSettings = QGroupBox("Note Type Mapping")
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

        # Save Button
        saveBtn = QPushButton("Save Configuration")
        saveBtn.clicked.connect(self.saveSettings)
        mainLayout.addWidget(saveBtn)
        self.setLayout(mainLayout)

    def saveSettings(self):
        selectedLevel = self.levelCombo.currentText()
        
        # Gather Selected Deck IDs
        selectedDeckIds = []
        for i in range(self.deckListWidget.count()):
            item = self.deckListWidget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                deckId = item.data(Qt.ItemDataRole.UserRole)
                selectedDeckIds.append(deckId)

        # Gather Note Types
        newNoteTypes = {}
        for (name, widget) in self.comboMap.items():
            newNoteTypes[name] = widget.currentText()
            
        # Update Config Object
        self.userConfig.update({
            "targetLevel": selectedLevel,
            "trackedDeckIds": selectedDeckIds,
            "deadline": self.dateInput.text(),
            "vocabColor": self.vocabBtn.currentColor,
            "grammarColor": self.grammarBtn.currentColor,
            "noteTypes": newNoteTypes
        })
        
        # Cleanups older settings
        self.userConfig.pop("trackedDeck", None)
        
        # Disk save
        config_manager.saveUserConfig(self.configPath, self.userConfig)
        self.accept()
        
        # Refresh UI
        if hasattr(mw, 'deckBrowser'):
            mw.deckBrowser.refresh()