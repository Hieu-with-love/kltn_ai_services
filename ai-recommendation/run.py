import uvicorn
import os
import sys

if __name__ == "__main__":
    # Add src to the system path to ensure modules are found
    sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
    
    # Run Uvicorn
    # Now that we have src/ai_recommendation/main.py, the module path is ai_recommendation.main
    uvicorn.run("ai_recommendation.main:app", host="0.0.0.0", port=8002, reload=True)
