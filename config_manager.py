import json
import os
from . import consts

def loadBaseConfig(basePath):
    # Load read-only defaults
    isFilePresent = os.path.exists(basePath)
    
    if isFilePresent:
        try:
            with open(basePath, 'r', encoding='utf-8') as fileObj:
                dataMap = json.load(fileObj)
                return dataMap.get("jlptLevels", {})
        except:
            pass
            
    return consts.DEFAULT_LEVELS.copy()

def loadUserConfig(userPath):
    # Load user settings with fallback
    configMap = consts.DEFAULT_USER_CONFIG.copy()
    
    isFilePresent = os.path.exists(userPath)
    if isFilePresent:
        try:
            with open(userPath, 'r', encoding='utf-8') as fileObj:
                loadedData = json.load(fileObj)
                isDict = isinstance(loadedData, dict)
                if isDict:
                    configMap.update(loadedData)
        except:
            pass
            
    return configMap

def saveUserConfig(userPath, configMap):
    # Save settings to disk
    try:
        with open(userPath, 'w', encoding='utf-8') as fileObj:
            json.dump(configMap, fileObj, ensure_ascii=False, indent=2)
    except:
        pass