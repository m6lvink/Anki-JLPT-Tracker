'''
JLPT Tracker Anki Add-on
'''
from aqt import mw, gui_hooks
from aqt.qt import *
import json
import os

# Module Imports
from . import config_manager
from . import db_utils
from . import view_manager
from . import gui

# Global Paths
addonDir = os.path.dirname(__file__)
userConfigPath = os.path.join(addonDir, "user_config.json")
baseConfigPath = os.path.join(addonDir, "config.json")
historyPath = os.path.join(addonDir, "history.json")
webDir = os.path.join(addonDir, "web")

pathsMap = {
    'webDir': webDir,
    'historyPath': historyPath
}

def getDashboardContent():
    # Helper to generate the HTML string
    userConfig = config_manager.loadUserConfig(userConfigPath)
    levelData = config_manager.loadBaseConfig(baseConfigPath)
    
    # Analyze DB
    statsTuple = db_utils.getCardCounts(userConfig)
    
    # Create HTML
    finalHtml = view_manager.generateDashboardHtml(userConfig, levelData, statsTuple, pathsMap)
    
    return finalHtml

def onRenderDeckBrowser(deckBrowser, browserContent):
    # Hook: Deck Browser 
    
    try:
        dashboardHtml = getDashboardContent()
        
        # Check for attributes
        if hasattr(browserContent, "stats"):
            browserContent.stats = dashboardHtml + browserContent.stats
            
    except Exception as e:
        print(f"JLPT Tracker Error (DeckBrowser): {e}")

def onRenderOverview(overviewInstance, overviewContent):
    # Hook: Overview 
    
    try:
        dashboardHtml = getDashboardContent()
        
        # (Prevents crash if 'body' is missing)
        if hasattr(overviewContent, "body"):
            overviewContent.body = dashboardHtml + overviewContent.body
            
    except Exception as e:
        # Error log console (rather than crashing anki)
        print(f"JLPT Tracker Error (Overview): {e}")

def handleWebCommand(handledState, commandString, context):
    # Route JS Commands (Toggle/Settings)
    isSettings = (commandString == "jlptSettings")
    isToggle = (commandString == "jlptToggle")
    
    if isSettings:
        gui.ConfigDialog(userConfigPath, mw).exec()
        return (True, None)
        
    elif isToggle:
        currentConfig = config_manager.loadUserConfig(userConfigPath)
        prevState = currentConfig.get("minimized", False)
        
        # Toggle state
        currentConfig["minimized"] = not prevState
        config_manager.saveUserConfig(userConfigPath, currentConfig)
        
        # Refresh UI immediately
        if hasattr(mw, 'deckBrowser'):
            mw.deckBrowser.refresh()
            
        return (True, None)
        
    return handledState

def openSettings():
    gui.ConfigDialog(userConfigPath, mw).exec()

# Hook Wiring
gui_hooks.deck_browser_will_render_content.append(onRenderDeckBrowser)
gui_hooks.overview_will_render_content.append(onRenderOverview)
gui_hooks.webview_did_receive_js_message.append(handleWebCommand)

# Menu
mw.form.menuTools.addAction(QAction("JLPT Tracker Settings", mw, triggered=openSettings))