import google.generativeai as genai
import os

class GeminiClient:
    def __init__(self, api_key):
        if api_key:
            api_key = api_key.strip()
        genai.configure(api_key=api_key)
        
        self.model = None
        self._configure_model()

    def _configure_model(self):
        """Dynamically find a working model availability."""
        try:
            print("Searching for available Gemini models...")
            # List all models available to this API key
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            print(f"Found models: {available_models}")

            # clear model names (remove 'models/' prefix if present)
            clean_models = [m.replace('models/', '') for m in available_models]

            # Priority list
            priorities = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
            
            selected_model_name = None
            
            # Check for priority match
            for p in priorities:
                if p in clean_models:
                    selected_model_name = p
                    break
            
            # Fallback to first available if no priority match
            if not selected_model_name and clean_models:
                selected_model_name = clean_models[0]

            if selected_model_name:
                print(f"Selected model: {selected_model_name}")
                self.model = genai.GenerativeModel(selected_model_name)
            else:
                print("CRITICAL: No text generation models found for this API Key.")
                
        except Exception as e:
            print(f"Error configuring models: {e}")

    def get_full_response(self, prompt, file_data=None):
        """Generates response and emotion in a single call, supporting optional file attachments."""
        if not self.model:
            self._configure_model()
            if not self.model:
                return {"response": "Error: No AI model available.", "emotion": "Neutral"}

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
        
        try:
            content_parts = [f"{system_instruction}\n\nUser: {prompt}"]
            
            if file_data and file_data.get('data'):
                file_type = file_data.get('type', '')
                
                if file_data.get('isText'):
                    # It's a text file, append content as context
                    content_parts[0] += f"\n\n[Context from attached file '{file_data.get('name')}']:\n{file_data.get('data')}"
                elif file_type.startswith('image/'):
                    # It's an image, decode base64
                    base64_data = file_data.get('data').split(',')[-1]
                    import base64
                    image_bytes = base64.b64decode(base64_data)
                    content_parts.append({
                        "mime_type": file_type,
                        "data": image_bytes
                    })
                else:
                    # Generic fallback
                    content_parts[0] += f"\n[Attached File: {file_data.get('name')}]"

            response = self.model.generate_content(content_parts)
            
            # Simple parsing if AI follows instructions
            text = response.text
            import json
            try:
                # Use regex or simple split to find JSON if AI adds extra text
                if "{" in text and "}" in text:
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    data = json.loads(text[start:end])
                    return {
                        "response": data.get("response", "I'm here to help."),
                        "emotion": data.get("emotion", "Neutral")
                    }
            except:
                pass
            
            return {"response": text, "emotion": "Neutral"}

        except Exception as e:
            error_str = str(e)
            print(f"Error in Gemini response: {error_str}")
            
            if "429" in error_str:
                return {
                    "response": "⚠️ **Rate Limit Reached**: The free version of Gemini allows only a few requests per minute. Please wait 30 seconds and try again.",
                    "emotion": "Neutral"
                }
            
            return {
                "response": f"I'm having trouble connecting to my brain. Error: {error_str}",
                "emotion": "Neutral"
            }

    def get_response(self, prompt):
        # Kept for compatibility but recommended to use get_full_response
        res = self.get_full_response(prompt)
        return res["response"]

    def analyze_emotion(self, text):
        # Kept for compatibility but recommended to use get_full_response
        return "Neutral"
