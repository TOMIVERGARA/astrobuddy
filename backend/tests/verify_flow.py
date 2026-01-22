import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)

def test_generate_plan():
    print("Testing /generate-plan endpoint...")
    
    # Mock request data
    payload = {
        "lat": -34.6037, # Buenos Aires
        "lon": -58.3816,
        "date": datetime.now().isoformat(),
        "telescope": "8 inch Dobsonian"
    }
    
    response = client.post("/generate-plan", json=payload)
    
    if response.status_code == 200:
        print("[SUCCESS] Endpoint returned 200 OK")
        
        # Verify content type
        content_type = response.headers["content-type"]
        print(f"Content-Type: {content_type}")
        if "application/pdf" in content_type:
            print("[SUCCESS] Returned PDF content type")
        else:
            print(f"[FAIL] Expected application/pdf, got {content_type}")
        
        # Save to verify file size
        with open("test_output.pdf", "wb") as f:
            f.write(response.content)
            
        size = os.path.getsize("test_output.pdf")
        print(f"Generated PDF size: {size} bytes")
        if size > 1000:
            print("[SUCCESS] PDF file looks valid (size > 1KB)")
        else:
            print("[WARN] PDF file is remarkably small")
            
    else:
        print(f"[FAIL] Endpoint returned {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    # Ensure env is setup or mock libraries? 
    # The services use requests, so in TestClient they will really make requests.
    # OpenMeteo is real. Skyfield is real (requires data).
    # We rely on previous steps having downloaded data.
    test_generate_plan()
