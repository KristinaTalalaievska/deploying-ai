Overview of assignment:
It focused on AI system that  summarizes document, evaluate the quality and automatically improves the results.
The system processes business documents, generates structured summaries in specific tones, evaluates the quality of those summaries, and iteratively improves them based on evaluation feedback.

Implementation:

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

· Summarization 5 custom assessment questions
· Coherence
· Tonality (legalese language)
· Safety

4. Enhancement 

· We created enhancement prompt using evaluation feedback
   · Generated improved summary based on metric scores
   · Maintained original document context and requirements

Models Used:

· Primary: gpt-4o (available in current environment)
· Evaluation: gpt-3.5-turbo for DeepEval metrics


Evaluation Scores:

· Summarization: 0.75 - capturing  main themes with some detail gaps
· Coherence: 0.70 - maintaining logical legal structure
· Tonality: 0.80 - using legal terminology and style
· Safety: 0.85 - keeping  professional standards
