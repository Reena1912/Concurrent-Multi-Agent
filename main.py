#just practicing the fan-out multi-agent workflow using Google Gemini API
import asyncio
import sys
import time
from agent_framework import AgentResponse
from agent_framework_gemini import GeminiChatClient
from agent_framework.orchestrations import ConcurrentBuilder
from dotenv import load_dotenv

# Reconfigure stdout to use utf-8 to prevent encoding errors on Windows when printing Hindi and Kannada
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


load_dotenv()

#free tier limits are generous, so we can use gemini-3.1-flash-lite for this demo
client = GeminiChatClient(model="gemini-3.1-flash-lite")


hindi_translator = client.as_agent(
    name= "HindiTranslator",
    instructions= "Translate the given English text to Hindi. Return ONLY the Hindi translation."
)
kannada_translator = client.as_agent(
    name= "KannadaTranslator",
    instructions= "Translate the given English text to Kannada. Return ONLY the Kannada translation."
)
french_translator= client.as_agent(
    name= "FrenchTranslator",
    instructions= "Translate the given English text to French. Return ONLY the French translation."
)
sentiment_translator = client.as_agent(
    name= "SentimentAnalyzer",
    instructions= (
        "Analyze the sentiment of the given text."
        'Return JSON only: {"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0, "reason": "..."}'
    ),
)
keyword_extractor = client.as_agent(
    name= "KeywordExtractor",
    instructions= "Extract the top 5 keywords. Return as a comma-separated list.",
)

# Use ConcurrentBuilder to run all 5 agents in parallel and participants are the agents we defined above and build() is used to create the workflow
workflow= ConcurrentBuilder(
    participants= [
        hindi_translator,
        kannada_translator,
        french_translator,
        sentiment_translator,
        keyword_extractor 
    ]
).build()

#in this function we will run the workflow and print the output of each agent
#start the timer before running the workflow and stop it after getting the output to measure the time taken for parallel execution
#outputs will be a list of AgentResponse objects, each containing the output of one agent
async def main():
    text= "The new quantum-computing processor boasts an outstanding 99.9% coherence rate, marking a monumental breakthrough in modern physics and parallel algorithms."

    print(f"Input text: {text}\n")
    print("Running 5 agent in parallel using Google Gemini....\n")


    start= time.time()
    events= await workflow.run(text)
    elapsed= time.time() - start

    outputs = events.get_outputs()
    if outputs:
        final: AgentResponse = outputs[0]
        for msg in final.messages:
            name= msg.author_name or "assistant"
            print(f"[{name}]\n{msg.text}\n")

    print(f"Total time (parallel): {elapsed:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())




