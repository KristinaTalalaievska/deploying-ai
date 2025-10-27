Overview of assignment:

Overview of assignment:

It focused on AI system that  summarizes document, evaluate the quality and automatically improves the results.

Implementation

1. Document Loading

For document loading "The GenAI Divide: State of AI in Business 2025" PDF we've chosen LangChain PyPDFLoader for document processing


2. Structured Summary Generation

·As per guidance we've used  Model: GPT-4 Turbo, not GPT-5 family.
· Output: Pydantic BaseModel with:
  · Author, Title, Relevance statement
  · Summary (≤1000 tokens) in Legalese tone
  · Input/Output token counts
· Tone: Legalese with formal legal language and Latin phrases
· Prompts: Separate developer instructions and dynamic user prompts

3. Evaluation

We used DeepEval Framework with Custom Questions focused around:

· Summarization
· Coherence
· Tonality (legalese language)
· Safety

4. Enhancement 

· We used evaluation feedback to improve summary, maintaining Legalese tone 
· Meanwhile we revaluated  enhanced version and compare by score results before and after