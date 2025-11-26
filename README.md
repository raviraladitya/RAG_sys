Generally a standard RAG-sys runs on cosine similarity so
for example the query: "Can i work from home?" has a high semantic match with 1st DOC and less match with 3rd DOC which has the correct response fo this query but a simple RAG-sys output would be- "No remote work for interns"

The solution for the conflicts(logic):

1. retrieval of multi-DOcuments: insteading of considering the best symentic DOC we consider the top 3 DOcs, ensuring the Intern DOc is passed to our LLM.
2. Used system_instruction forces gemini to work as logic controller by enforcing the following rules
 >  1.Specificity Overrides General: Rules for specific roles (e.g., Interns) should     override   general employee rules.
    2. Recency Overrides : If policies clash for the same group, consider the document which is recently updated.
    3. Citation: explicitly mention to cite the source filename that dictates the final decision. 

Cost Analysis:

Architecture
>LLM:Gemini 2.5 Flash
>DB:ChromaDB
>Embeddings: Google text-embedding-004

the Free Tier limits are 15 requests per minute,1.5k requests per Day and 1 million tokens per minute
  paid :unlimited requests
  >for the input(prompts and documents)
  >$0.075 per 1 Million tokens (for prompts < 128k tokens)
   >$0.15 per 1 Million tokens (for prompts > 128k tokens).

   >output(the AI answer)
   $0.30 per 1 Million tokens.
   for embedding
   Input Cost: $0.025 per 1 Million tokens.

   so
   DB storage: freee as it runs locally on my hardware
   cost for the daily input tokens

   as 5000 queries per day 
   let the approx size per query including user query, top 3 docs, the set of instruction=500
   so now total no of input tockens=5000*500=2.5M(2.5 million)
   total input cost would be= $.075*2.5M=.1875$

   cost for daily output tokens
   size per output avg ~100tokens
   total output tokens 5000*100=500000(.5 million)
   total output cost=0.5M × $0.30 = $0.15

now the total cost =(.1875+.15)$=.3375$ evey day