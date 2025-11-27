'''
JLPT Tracker Anki Add-on
Built to help track progress towards JLPT levels within Anki :D
Author: MK
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
    # Hook: Deck Browser (Main Screen)
    
    dashboardHtml = getDashboardContent()
    
    # Strict academic check for None
    if browserContent.stats is not None:
        browserContent.stats += dashboardHtml
    else:
        browserContent.stats = dashboardHtml

def onRenderOverview(overviewInstance, overviewContent):
    # Hook: Overview (Screen after clicking a deck)    
    dashboardHtml = getDashboardContent()
    
    if overviewContent.body is not None:
        # Prepend to body so it sits at the top
        overviewContent.body = dashboardHtml + overviewContent.body

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