# Ref: https://zetcode.com/python/markitdown/

from markitdown import MarkItDown
from groq import Groq

md = MarkItDown(enable_plugins=False) # Set to True to enable plugins
# md = MarkItDown(docintel_endpoint="<document_intelligence_endpoint>")
# md = MarkItDown(llm_client= Groq(api_key=os.environ.get("GROQ_API_KEY")),
                # llm_model="llama-3.2-11b-vision-preview")

result = md.convert("data/YogeshKulkarniLinkedInProfile.pdf")
print(result.text_content)