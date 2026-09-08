import requests

class ModelClient:
    """
    Unified AI client for GhostTrace.
    Supports LM Studio, OpenWebUI, Ollama, and cloud LLMs.
    """

    def __init__(self, base_url="http://localhost:11434/api/generate"):
        """
        Default base_url points to Ollama.
        You can change this to LM Studio or OpenWebUI easily.
        """
        self.base_url = base_url

    def ask(self, prompt: str, system: str = None):
        """
        Send a prompt to the model and return the response text.
        """
        try:
            payload = {
                "model": "llama3.1",   # Change to your installed model name
                "prompt": prompt
            }

            if system:
                payload["system"] = system

            response = requests.post(self.base_url, json=payload, timeout=30)

            if response.status_code != 200:
                return {
                    "error": f"Model returned {response.status_code}",
                    "details": response.text
                }

            data = response.json()

            # Ollama streams tokens; LM Studio returns full text
            if "response" in data:
                return {"text": data["response"]}
            if "output_text" in data:
                return {"text": data["output_text"]}

            return {"text": str(data)}

        except Exception as e:
            return {"error": str(e)}


# Global client instance
client = ModelClient()
