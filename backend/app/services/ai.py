from openai import OpenAI
import os
import json
from typing import List

class AIService:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def generate_observation_plan(self, objects: List[dict], weather: dict, location: dict, telescope_specs: dict) -> dict:
        """
        Generates a narrative plan using OpenAI.
        """
        if not self.client:
            print("   [AI] No OPENAI_API_KEY found. Returning fallback response.")
            return self._fallback_response(objects)

        print(f"   [AI] Requesting observations for {len(objects)} objects from OpenAI...")
        
        prompt = f"""
        Act as an expert astronomer writing a technical yet passionate observation report.
        Location: {{location}}
        Weather: {{weather}}
        Telescope: {{telescope_specs}}
        
        Available Objects (Filtered):
        {json.dumps(objects, indent=2)}
        
        Select the top 5 objects that are best for tonight's conditions and this telescope.
        For each object, provide:
        1. "id": The exact object ID from the input list.
        2. "ranking": 1-5.
        3. "description": A single, rich, exhaustive paragraph combining technical details (structure, distance, composition) with visual description ("what it looks like in the eyepiece"). Be passionate but technical.
        4. "tips": Specific technical advice for observing this object (filters, magnification, technique).
        5. "fact": A truly obscure or scientifically interesting fact about this object.
        
        Also provide a "Night Overview" summary that is technical and sets the mood for the session, mentioning the specific weather/moon conditions.
        
        Return JSON format:
        {{
            "overview": "...",
            "objects": [
                {{ "id": "...", "ranking": 1, "description": "...", "tips": "...", "fact": "..." }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert astronomer writing technical observation reports."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            print("   [AI] Response received.")
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"   [AI] Error calling OpenAI: {e}")
            return self._fallback_response(objects)

    def _fallback_response(self, objects: List[dict]) -> dict:
        """
        Fallback if AI is unavailable.
        """
        selected = objects[:5] if objects else []
        return {
            "overview": "AI service unavailable. Showing raw object data.",
            "objects": [
                {
                    "id": obj.get("id", "unknown"),
                    "ranking": 0,
                    "description": "No description available.",
                    "tips": "No tips available.",
                    "fact": "No fact available."
                }
                for obj in selected
            ]
        }
