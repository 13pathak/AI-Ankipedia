import os
import json
import base64
from aqt import mw
from aqt.gui_hooks import webview_will_set_content
from aqt.utils import showInfo, tooltip
from aqt.qt import *
import aqt

from .ai_service import AIService
from .settings_dialog import SettingsDialog

# Globals
ADDON_DIR = os.path.dirname(__file__)
CONFIG = mw.addonManager.getConfig(__name__)
ai_service = AIService(CONFIG)

# Debug: Confirm load
tooltip("AI Ankipedia: Python Module Loaded")

def get_web_content(filename):
    path = os.path.join(ADDON_DIR, "web_assets", filename)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def on_webview_init(web_content, context):
    """Injects JS and CSS into the reviewer webview."""
    # Only inject in reviewer (context is Reviewer instance) via the generic hook often used or specific reviewer hook
    # But reviewer_did_init_web_view passes (webview).
    # Easier to use webview_will_set_content to inject script tags if we want persistence or load js file.
    pass

def inject_assets(web_content, context):
    """Injects CSS and JS into the Reviewer."""
    # Strict check might be failing if Anki changed class names or context types
    # Let's try to inject if it looks like a reviewer or has 'card' in the content
    # For now, just logging context for debug if needed, but proceeding.
    
    # We will try to identify reviewer by existence of .reviewer property on mw or similar,
    # but the 'context' arg is usually the specific object (Reviewer, Editor, etc).
    # Let's trust it's the reviewer if it's hitting this hook with web_content.
    
    # Debug:
    # tooltip(f"Injecting assets. Context: {type(context)}")
    
    js = get_web_content("ankipedia.js")
    css = get_web_content("ankipedia.css")
    
    # Add JS and CSS to the head
    web_content.head += f"<style>{css}</style>"
    web_content.head += f"<script>{js}</script>"

# Hook into Anki's bridge mechanism
def on_bridge_cmd(handled, cmd, context):
    if not isinstance(context, aqt.reviewer.Reviewer):
        return handled

    if cmd.startswith("ankipedia_trigger:"):
        text = cmd.split(":", 1)[1]
        handle_popup_trigger(text)
        return (True, None) # handled
    
    if cmd.startswith("ankipedia_save:"):
        # Format: ankipedia_save:JSON_STRING
        try:
            data_str = cmd.split(":", 1)[1]
            data = json.loads(data_str) # Decode URL encoded if necessary? No, bridge sends string.
            handle_save(data)
        except Exception as e:
            tooltip(f"Error saving: {e}")
        return (True, None)

    return handled

def handle_popup_trigger(text):
    """Called when user selects text and triggers popup."""
    # 1. Notify JS that we received the request (optional, to show loading if not already shown)
    
    # 2. Call AI Service (async to avoid freezing UI)
    mw.taskman.run_in_background(
        lambda: ai_service.get_definition(text),
        lambda result: on_ai_result(result, text)
    )

def on_ai_result(future, original_text):
    """Callback when AI request finishes."""
    try:
        # run_in_background returns a Future in the callback
        result = future.result()
    except Exception as e:
        result = {"error": str(e)}

    if result.get("error"):
        content = f"Error: {result['error']}"
    else:
        content = result.get("definition", "No definition found.")
    
    # Send data back to JS
    # We need to escape content for JS string
    
    safe_content = json.dumps(content)
    safe_result = json.dumps(result)
    
    script = f"Ankipedia.updatePopup({safe_content}, {safe_result});"
    mw.reviewer.web.eval(script)

def handle_save(data):
    """Saves the item to a history file."""
    history_file = os.path.join(ADDON_DIR, "user_files", "history.json")
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            pass
    
    history.insert(0, data)
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)
    
    tooltip("Saved to Ankipedia History")

def on_settings():
    """Opens the configuration dialog."""
    # Reload config in case it changed
    global CONFIG
    CONFIG = mw.addonManager.getConfig(__name__)
    
    dlg = SettingsDialog(mw, CONFIG)
    if dlg.exec():
        # Save new config
        new_config = dlg.get_config()
        mw.addonManager.writeConfig(__name__, new_config)
        CONFIG = new_config
        ai_service.update_config(CONFIG)
        tooltip("Settings saved.")

# Hooks
webview_will_set_content.append(inject_assets)
aqt.gui_hooks.webview_did_receive_js_message.append(on_bridge_cmd)

# Menu
action = QAction("AI Ankipedia Settings", mw)
action.triggered.connect(on_settings)
mw.form.menuTools.addAction(action)

# Link "Config" button in Add-on Manager to our settings dialog
mw.addonManager.setConfigAction(__name__, on_settings)
