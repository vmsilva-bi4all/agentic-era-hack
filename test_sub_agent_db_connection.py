from app.sub_agents.candidate_manager.tools import candidate_manager_tools

try:
    conn = candidate_manager_tools._get_connection()
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")