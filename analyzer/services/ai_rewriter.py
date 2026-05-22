# analyzer/services/ai_rewriter.py
import requests

class AIRewriter:
    def __init__(self):
        self.api_key = "your_groq_api_key"  # Get from console.groq.com
    
    def improve_bullet_point(self, original_text, job_title):
        prompt = f"""Improve this resume bullet point for a {job_title} position. 
        Make it more action-oriented and metric-driven. Add numbers if possible.
        
        Original: {original_text}
        
        Improved version:"""
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]}
        )
        return response.json()["choices"][0]["message"]["content"]