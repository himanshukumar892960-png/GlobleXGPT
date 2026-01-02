import requests
import json
import os

class OpenRouterClient:
    def __init__(self, api_key, model=None):
        self.api_key = api_key
        self.model = model or "deepseek/deepseek-chat"
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def get_full_response(self, prompt, file_data=None):
        """Generates response and emotion in a single call, supporting files."""
        system_instruction = (
            "You are GlobleXGPT, a powerful AI assistant with advanced multimodal capabilities. "
            "You CAN generate images, videos, and search YouTube. "
            "If a user asks for an image, tell them you are generating it. "
            "If a user asks for a video, tell them you are generating it. "
            "If a user asks to find a YouTube video or trending videos, tell them you are looking for them. "
            "You should also mention that you can animate images if they attach one. "
            "Return your response in JSON format with exactly two keys: "
            "'response' (your helpful text) and 'emotion' (one word describing user's mood, e.g., Happy, Neutral, Sad)."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "GlobleXGPT"
        }

        # Prepare content
        user_content = prompt
        if file_data and file_data.get('data'):
            file_type = file_data.get('type', '')
            if file_type.startswith('image/'):
                user_content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": file_data.get('data') # This is base64 data URL
                        }
                    }
                ]
            else:
                user_content = f"{prompt}\n[Attached File: {file_data.get('name')}]"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.base_url, headers=headers, data=json.dumps(payload))
            
            # log raw response if status not 200
            if response.status_code != 200:
                print(f"OpenRouter Error {response.status_code}: {response.text}")
                return {
                    "response": f"API Error {response.status_code}: {response.text}",
                    "emotion": "Neutral"
                }

            data = response.json()
            
            if 'choices' not in data or not data['choices']:
                return {"response": "I couldn't get a response. Please try again.", "emotion": "Neutral"}

            content = data['choices'][0]['message']['content']
            
            # Robust JSON parsing
            try:
                # Clean up markdown if present
                clean_content = content.strip()
                if clean_content.startswith("```json"):
                    clean_content = clean_content[7:-3].strip()
                elif clean_content.startswith("```"):
                    clean_content = clean_content[3:-3].strip()
                
                parsed_data = json.loads(clean_content)
                return {
                    "response": parsed_data.get("response", content),
                    "emotion": parsed_data.get("emotion", "Neutral")
                }
            except json.JSONDecodeError:
                # Fallback if AI didn't return valid JSON
                return {
                    "response": content,
                    "emotion": "Neutral"
                }
                
        except Exception as e:
            print(f"Error in OpenRouter response: {e}")
            return {
                "response": f"I'm having trouble connecting to my brain. Error: {str(e)}",
                "emotion": "Neutral"
            }

    def get_response(self, prompt):
        res = self.get_full_response(prompt)
        return res["response"]
