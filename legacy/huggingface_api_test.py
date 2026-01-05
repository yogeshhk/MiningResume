# import os
# from langchain_huggingface import HuggingFaceEndpoint
# from langchain.prompts import PromptTemplate

# # 1. Check token
# token = os.environ.get("HUGGINGFACEHUB_API_TOKEN") or os.environ.get("HF_API_TOKEN")
# if not token:
#     print("❌ No Hugging Face API token found in environment.")
# else:
#     print(f"✅ Found HF token: {token[:10]}...")

# # 2. Pick a model that works with free inference API
# repo_id = "google/flan-t5-large"

# # 3. Create the endpoint
# try:
#     llm = HuggingFaceEndpoint(
#         repo_id=repo_id,
#         temperature=0.1,
#         huggingfacehub_api_token=token,
#     )

#     # 4. Simple prompt
#     prompt = PromptTemplate(
#         input_variables=["topic"],
#         template="Explain {topic} in one sentence."
#     )

#     chain = prompt | llm
#     result = chain.invoke({"topic": "machine learning"})

#     print("✅ Model responded:", result)

# except Exception as e:
#     print("❌ Error invoking model:", e)

from transformers import pipeline

# Load FLAN-T5 locally (no token required)
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-large",  # you can also try flan-t5-base for faster CPU
    tokenizer="google/flan-t5-large",
    token=False  # ✅ Correct and explicit way to force no token
)

# Simple test prompt
prompt = "Explain machine learning in one sentence."

result = generator(prompt, max_new_tokens=50)

print("✅ Model responded:", result[0]["generated_text"])
