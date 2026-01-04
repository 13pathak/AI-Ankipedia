import json
import urllib.request
import urllib.error

class AIService:
    def __init__(self, config):
        self.config = config

    def update_config(self, config):
        self.config = config

    def get_definition(self, word):
        models = self.config.get('models', [])
        default_id = self.config.get('defaultModelId')
        
        model = next((m for m in models if m['id'] == default_id), None)
        if not model:
            if models:
                model = models[0]
            else:
                return {"error": "No AI models configured. Please check settings."}

        # Select Prompt
        prompts = self.config.get('prompts', [])
        default_prompt_id = self.config.get('defaultPromptId')
        prompt_content = "Explain the following word or concept in a concise paragraph: {word}" # Fallback
        
        if default_prompt_id:
            p = next((x for x in prompts if x['id'] == default_prompt_id), None)
            if p:
                prompt_content = p['content']
                
        final_prompt = prompt_content.replace("{word}", word)
        
        # Determine API Type (Google vs OpenAI/Ollama)
        # For simplicity, we assume OpenAI-compatible format for now as per Chrome extension logic
        # But user config might use Google endpoint.
        
        api_key = model.get('apiKey', '')
        endpoint = model.get('endpoint', '')
        model_name = model.get('modelName', 'gpt-3.5-turbo')
        
        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": final_prompt}
            ],
            "stream": False
        }
        
        try:
            req = urllib.request.Request(
                endpoint, 
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req) as response:
                data = json.load(response)
                # Parse OpenAI-style response
                try:
                    definition = data['choices'][0]['message']['content']
                    return {
                        "definition": definition,
                        "model": model_name,
                        "word": word
                    }
                except (KeyError, IndexError):
                    return {"error": "Invalid API response format", "raw": data}
                    
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP Error {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"URL Error: {e.reason}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
