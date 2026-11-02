# AI Ankipedia

**AI Ankipedia** adds AI-generated definitions and explanations to Anki review sessions. Select a word or short phrase on a card to request an explanation from your configured model.

## ✨ Features

-   **Instant Definitions**: Select any text (up to 6 words) in the Reviewer to trigger a popup.
-   **Configurable Models**: Uses OpenAI-compatible chat-completion endpoints, including compatible Gemini, OpenAI, and Ollama configurations.
-   **Rich Formatting**: Supports Markdown rendering (headers, bold, lists) for readable explanations.
-   **History & Saving**: Saves definitions to `user_files/history.json` in the add-on directory.
-   **Anki Integrated**: Displays explanations in the Reviewer webview.

## 📥 Installation

1.  Download the `.ankiaddon` file from the [Releases](https://github.com/13pathak/AI-Ankipedia/releases) page.
2.  Open Anki and go to **Tools** > **Add-ons**.
3.  Click **Install from file...**.
4.  Select the downloaded file.
5.  Restart Anki.

## ⚙️ Configuration

1.  After installation, go to **Tools** > **Add-ons**.
2.  Select **AI Ankipedia** and click **Config**.
3.  In the **AI Models** tab, edit the JSON array of models. Set the endpoint, model ID, and API key for your provider, then click **OK**.

**Example Configuration:**
```json
[
  {
    "id": "gemini",
    "name": "Gemini",
    "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "modelName": "YOUR_MODEL_ID",
    "apiKey": "YOUR_API_KEY"
  }
]
```

Replace `YOUR_MODEL_ID` and `YOUR_API_KEY` with values from your provider. The endpoint must accept OpenAI-compatible chat-completion requests.

## 🛠️ Development

To modify this add-on or build it from source:

1.  Clone this repository and open its directory:
    ```bash
    git clone https://github.com/13pathak/AI-Ankipedia.git
    cd AI-Ankipedia
    ```
2.  Edit the Python files or web assets in `web_assets/`.
3.  Use Python 3 to package the add-on from the repository root:
    ```bash
    python -m zipfile -c AI.Ankipedia.ankiaddon __init__.py ai_service.py settings_dialog.py config.json manifest.json web_assets
    ```
4.  Install `AI.Ankipedia.ankiaddon` in Anki using **Install from file...**, then restart Anki to test.

## 📄 License

MIT License
