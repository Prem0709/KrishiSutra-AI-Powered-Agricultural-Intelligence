"""
Test script to verify the agriculture agent fix
"""
from agents.agriculture_agent import build_agriculture_agent

# Test building the agent
print("Building agriculture agent...")
try:
    qa_agent = build_agriculture_agent()
    print("✅ Agent built successfully!")
    
    # Test running a query
    print("\nTesting query: 'Which state had the highest rice production in 2020?'")
    result = qa_agent.run("Which state had the highest rice production in 2020?")
    print(f"\n✅ Query executed successfully!")
    print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
