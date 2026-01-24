import sys
import os
import asyncio
from pathlib import Path
import types
from dotenv import load_dotenv

load_dotenv()

# 1. SETUP PATHS
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"
shared_lib_src = current_dir.parent / "shared-ai-lib" / "src"

sys.path.append(str(src_dir))
sys.path.append(str(shared_lib_src))

# 2. FIX IMPORTS (Hack for project structure)
try:
    # Import the top-level packages from 'src'
    import api
    import application
    
    # Create the fake 'ai_recommendation' package
    ai_rec = types.ModuleType("ai_recommendation")
    sys.modules["ai_recommendation"] = ai_rec
    
    # Link subpackages BEFORE importing their contents that might rely on the full name
    sys.modules["ai_recommendation.api"] = api
    sys.modules["ai_recommendation.application"] = application
    ai_rec.api = api
    ai_rec.application = application
    
    # Now it is safe to import submodules that might follow absolute imports
    import api.schemas
    sys.modules["ai_recommendation.api.schemas"] = api.schemas
    
    import api.routes
    sys.modules["ai_recommendation.api.routes"] = api.routes
    
    import application.service
    sys.modules["ai_recommendation.application.service"] = application.service

except ImportError as e:
    print(f"Import Error during setup: {e}")
    sys.exit(1)

# 3. IMPORT SERVICE
try:
    from ai_recommendation.application.service import RecommendationService
    from ai_recommendation.api.schemas import RecommendationRequest, UserProfile, CourseCandidate
except ImportError as e:
    print(f"Failed to import service after path setup: {e}")
    sys.exit(1)

# 4. TEST FUNCTION
async def test_recommendation():
    print("Testing RecommendationService...")
    
    # Mock Data
    user = UserProfile(
        user_id="u123", 
        interests=["Python", "Data Science"], 
        history=["Intro to Python"]
    )
    
    candidates = [
        CourseCandidate(id="c1", title="Advanced Python", description="Deep dive into Python internals"),
        CourseCandidate(id="c2", title="Machine Learning 101", description="Basic ML concepts"),
        CourseCandidate(id="c3", title="Web Dev with React", description="Frontend development")
    ]
    
    req = RecommendationRequest(
        user_profile=user,
        candidates=candidates,
        top_k=2
    )
    
    # Init Service
    try:
        service = RecommendationService()
        print("Service initialized.")
        
        print("Sending request to LLM (this may take a few seconds)...")
        response = await service.recommend(req)
        
        print("\nSUCCESS! Recommendation received:")
        print(f"Top Recommendations: {[c.title for c in response.recommendations]}")
        print(f"Reasoning: {response.reasoning}")
        
    except Exception as e:
        print(f"\nFAILED! Error: {e}")
        print("\nPossible reasons: Missing Google API Key, Network issue, or Library mismatch.")

if __name__ == "__main__":
    asyncio.run(test_recommendation())
