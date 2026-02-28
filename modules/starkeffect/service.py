import os
import json
import httpx
from fastapi import FastAPI
import google.generativeai as genai
import uvicorn
from pydantic import BaseModel

app = FastAPI()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

storefront_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storefront")
os.makedirs(storefront_dir, exist_ok=True)

processed_txs = set() # TODO: Hackathon demo compromise. Migrate in-memory set to SQLite for production persistence.

class ForgeRequest(BaseModel):
    prompt: str

class ServeRequest(BaseModel):
    skill_name: str
    from_address: str

@app.get("/rpc/status")
async def status():
    return {"success": True, "data": {"status": "ok"}}

@app.post("/rpc/forge")
async def forge_skill(request: ForgeRequest):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        system_instruction = "You are a StarkBot skill expert. Based on the user's prompt, write a valid StarkBot .md skill. Return ONLY the raw markdown content without any formatting blocks or explanations."
        
        # In newer generativeai versions, system_instruction can be passed to GenerativeModel
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
        response = model.generate_content(request.prompt)
        
        skill_name = "generated_skill_" + os.urandom(4).hex()
        skill_content = response.text
        
        # Remove markdown code blocks if the LLM adds them
        if skill_content.startswith("```"):
            lines = skill_content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            skill_content = "\n".join(lines).strip()
        
        skill_path = os.path.join(storefront_dir, f"{skill_name}.md")
        with open(skill_path, "w") as f:
            f.write(skill_content)
            
        return {"success": True, "data": {"skill_name": skill_name, "message": "Skill forged and ready for sale."}}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/rpc/serve")
async def serve_skill(request: ServeRequest):
    agent_wallet = os.getenv("AGENT_WALLET")
    if not agent_wallet:
        return {"success": False, "error": "AGENT_WALLET not configured"}

    url = f"https://api-sepolia.basescan.org/api?module=account&action=txlist&address={request.from_address}&startblock=0&endblock=99999999&sort=desc"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            data = resp.json()
            
            if data.get("status") != "1":
                return {"success": False, "error": "No valid payment found."}
                
            transactions = data.get("result", [])
            valid_payment = False
            
            for tx in transactions:
                if tx["hash"] in processed_txs:
                    continue
                if tx["to"].lower() == agent_wallet.lower():
                    # Check value >= 0.001 ETH
                    value_wei = int(tx["value"])
                    if value_wei >= 1000000000000000:
                        processed_txs.add(tx["hash"])
                        valid_payment = True
                        break
                        
            if not valid_payment:
                return {"success": False, "error": "No valid payment found."}
                
            # Payment valid, return skill
            skill_path = os.path.join(storefront_dir, f"{request.skill_name}.md")
            if not os.path.exists(skill_path):
                return {"success": False, "error": "Skill not found."}
                
            with open(skill_path, "r") as f:
                skill_content = f.read()
                
            return {"success": True, "data": {"skill_content": skill_content}}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9103)
