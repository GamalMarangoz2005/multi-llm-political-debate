import os
import time
import gradio as gr
from google import genai
from groq import Groq

# 1. Initialize API Clients safely
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

gemini_client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# Active verified models
GEMINI_MODEL = "gemini-3.5-flash-lite"
GROQ_MODEL = "qwen/qwen3.8-27b"  # High speed & high rate-limit ceiling on Groq

def generate_gemini_safe(prompt, max_retries=4):
    """Helper with automatic retries for rate limits or server spikes."""
    for attempt in range(1, max_retries + 1):
        try:
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            err = str(e)
            if "429" in err or "503" in err or "RESOURCE_EXHAUSTED" in err or "UNAVAILABLE" in err:
                if attempt < max_retries:
                    time.sleep(attempt * 3)  # Wait 3s, 6s, 9s between retries
                    continue
            raise e
    return "[Gemini API exhausted quota]"

def format_recent_context(chat_display, max_messages=4):
    """Keeps context light (last 4 messages) to stay within Free Tier TPM limits."""
    recent = chat_display[-max_messages:] if len(chat_display) > max_messages else chat_display
    formatted = ""
    for msg in recent:
        content = msg.get("content", "")
        formatted += f"{content}\n\n"
    return formatted

def run_full_debate(country):
    if not country or not country.strip():
        yield [], "⚠️ Please enter a country name."
        return

    if not gemini_client or not groq_client:
        yield [], "⚠️ Missing API keys! Set GEMINI_API_KEY and GROQ_API_KEY."
        return

    chat_display = []
    max_rounds = 10

    gov_sys_prompt = (
        f"You are the official Spokesperson for the Government of {country}. "
        f"Defend policy, growth, and social programs using valid facts/data. Keep response under 90 words."
    )

    opp_sys_prompt = (
        f"You are the Leader of the Opposition party in {country}. "
        f"Critique government policy and economy using valid counter-statistics. Keep response under 90 words."
    )

    # Clean continuous generator loop across all 10 rounds
    for current_round in range(1, max_rounds + 1):

        # -------------------------------------------------------------
        # STEP 1: Government Turn (Gemini)
        # -------------------------------------------------------------
        recent_context = format_recent_context(chat_display)
        
        if current_round == 1:
            gov_prompt = f"{gov_sys_prompt}\n\nOpening Statement: Present a strong defense of {country}."
        else:
            gov_prompt = (
                f"{gov_sys_prompt}\n\n"
                f"Recent Debate Context:\n{recent_context}\n"
                f"Round {current_round}: Directly counter the Opposition's point."
            )

        try:
            gov_text = generate_gemini_safe(gov_prompt)
        except Exception as e:
            gov_text = f"[Gemini Quota Error: {str(e)}]"

        chat_display.append({"role": "user", "content": f"**[Round {current_round}/10] Government (Gemini):**\n{gov_text}"})
        yield chat_display, f"⏳ Round {current_round}/10 in progress (Opposition is thinking...)"

        if "[Gemini Quota Error" in gov_text:
            yield chat_display, f"❌ Stopped at Round {current_round} due to Gemini API limits."
            return

        # Pause 3 seconds to clear API rate-limit windows
        time.sleep(3)

        # -------------------------------------------------------------
        # STEP 2: Opposition Turn (Groq)
        # -------------------------------------------------------------
        recent_context_updated = format_recent_context(chat_display)
        opp_prompt = (
            f"Recent Debate Context:\n{recent_context_updated}\n"
            f"Round {current_round}: Counter the Government's claims with alternative statistics."
        )

        try:
            opp_response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": opp_sys_prompt},
                    {"role": "user", "content": opp_prompt}
                ],
                max_tokens=180,
            )
            opp_text = opp_response.choices[0].message.content.strip()
        except Exception as e:
            opp_text = f"[Groq Error: {str(e)}]"

        chat_display.append({"role": "assistant", "content": f"**[Round {current_round}/10] Opposition (Groq):**\n{opp_text}"})
        yield chat_display, f"✅ Round {current_round}/10 completed."

        if "[Groq Error" in opp_text:
            yield chat_display, f"❌ Stopped at Round {current_round} due to Groq API limits."
            return

        # Pause 3 seconds before starting next round
        time.sleep(3)

    yield chat_display, "🎉 Debate Finished! (Completed 10/10 Rounds)"

# --- Gradio UI Layout ---
with gr.Blocks(title="Multi-LLM Political Debate") as demo:
    gr.Markdown("# 🏛️ Multi-LLM Political Debate Application")
    gr.Markdown("**Government (Gemini Flash)** vs. **Opposition (Groq / Qwen 27B)**")

    with gr.Row():
        country_input = gr.Textbox(label="Target Country", placeholder="e.g. Germany, Egypt, Singapore, Japan...")
        start_btn = gr.Button("Start Debate", variant="primary")

    status_output = gr.Markdown("Status: Ready to start.")
    chatbot = gr.Chatbot(height=600)

    # Direct connection triggering the full generator loop
    start_btn.click(
        fn=run_full_debate,
        inputs=[country_input],
        outputs=[chatbot, status_output]
    )

if __name__ == "__main__":
    demo.launch()