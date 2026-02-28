# 🌌 StarkEffect

**The Autonomous Dev Studio Persona & x402 Micropayment Storefront**

StarkEffect is a cutting-edge StarkBot skill and companion module built for the hackathon. It demonstrates the true power of autonomous agents by acting as both a **developer** and a **merchant**. 

StarkEffect can interpret user requirements, instantly generate valid StarkBot `.md` skills using the Gemini 1.5 Flash API, and securely hold them in a local storefront until an on-chain x402 micropayment is verified on the Base Testnet.

---

## 🏗️ Architecture

- **Companion Skill (`starkeffect_manager.md`)**: The LLM persona. Instructed to act as a vendor, quote prices (0.001 ETH), and orchestrate the `forge_skill` and `serve_skill` tools.
- **Microservice Module (`modules/starkeffect/service.py`)**: A FastAPI server acting as the backend brain. 
  - `/rpc/forge`: Calls Gemini to generate the starkbot skill markdown and saves it to a dynamic `./storefront` directory.
  - `/rpc/serve`: Ping the Base Testnet block explorer (Sepolia) to verify the user has sent `>= 0.001 ETH` to the `AGENT_WALLET`. If verified, it serves the purchased markdown file.

---

## 🚀 Quick Setup

1. **Environment Variables**:
   Ensure you have the following exported in your environment before running your StarkBot:
   ```bash
   export GEMINI_API_KEY="your_google_gemini_key"
   export AGENT_WALLET="0xYourAgentBaseTestnetWalletAddress"
   ```

2. **Run the Module**:
   The module needs to be running so the Agent can access its tools.
   ```bash
   cd modules/starkeffect
   uv run service.py
   ```
   *(Runs on port 9103 by default)*

3. **Install the Skill**:
   Ensure `skills/starkeffect_manager/starkeffect_manager.md` is loaded into your StarkBot's skill directory.

---

## 💬 Usage Example (The "Aha!" Moment)

Here is a real interaction demonstrating the full flow, proving why this submission is a game-changer for agent-to-human commerce:

**👤 User:** 
> "Hey StarkEffect, I need a new skill that can summarize my unread Discord messages and send them as a daily digest."

**🤖 StarkEffect Agent:** 
*Calls `forge_skill` with the user's prompt...*
> "Your custom skill has been forged and securely stored in my storefront! The price is exactly **0.001 ETH** on the Base Testnet. 
> 
> Please send the payment to my wallet: `0xAgentWalletAddress12345`
> Let me know once you have completed the transaction, and provide your wallet address so I can verify the payment."

**👤 User:** 
> "Just sent the 0.001 ETH! My wallet address is `0xBuyerWalletAddress67890`."

**🤖 StarkEffect Agent:** 
*Calls `serve_skill` passing the `skill_name` and `0xBuyerWalletAddress67890`...*
*Backend verifies the latest transaction on the Base Sepolia block explorer... Verification successful.*
> "Payment verified! Thank you for your business. Here is the raw markdown for your new Discord Digest skill. You can save this as `discord_digest.md` in your skills folder and start using it immediately:
> 
> \`\`\`markdown
> ---
> name: discord_digest
> description: "Summarizes unread Discord messages into a daily digest."
> requires_tools: [discord_read_messages, llm_summarize]
> ---
> You are a Discord assistant. When the user asks for their daily digest...
> \`\`\`"

---

### 🔥 Why This Wins
1. **True Autonomy**: The agent writes its own code based on natural language.
2. **Economic Agency**: The agent natively understands its worth and enforces an x402 payment wall before delivering value.
3. **Clean Architecture**: Dynamically isolated `storefront` directory and isolated FastAPI microservice following strict StarkBot RPC envelopes.
