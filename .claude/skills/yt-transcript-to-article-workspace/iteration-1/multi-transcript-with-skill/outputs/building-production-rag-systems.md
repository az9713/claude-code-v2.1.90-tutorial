# Building Production RAG Systems: A Complete Guide to Retrieval, Generation, and Evaluation

> **TL;DR:** Retrieval-Augmented Generation (RAG) dramatically improves LLM answers by retrieving relevant documents from your own knowledge base and injecting them into the prompt. Building a production-quality RAG system requires careful attention across the full pipeline: chunking strategy, embedding model selection, retrieval enhancements like query expansion and reranking, structured prompt construction, hallucination detection, and rigorous evaluation with metrics like recall@k, MRR, and faithfulness. Each component can be added incrementally, but skipping evaluation and monitoring is the most common mistake teams make.

**Source:** Building Production RAG Systems (Parts 1 & 2)

---

## What RAG Is and Why It Matters

RAG — retrieval-augmented generation — is a pattern where, instead of relying solely on an LLM's training data, you retrieve relevant documents from your own knowledge base and insert them into the context window alongside the user's question. The model then generates an answer grounded in your specific data, producing much better and more accurate results than a standalone LLM can deliver.

The full pipeline spans two phases: **retrieval** (finding the right documents) and **generation** (producing a faithful, well-structured answer from those documents). Getting both right, and monitoring them in production, is what separates a prototype from a system you can actually trust.

## Document Ingestion and Chunking

The first component of any RAG system is the document ingestion pipeline. Raw documents — PDFs, web pages, and other formats — need to be broken into smaller chunks before they can be embedded and searched.

Chunking is one of the most important and underrated parts of RAG. The tradeoffs are straightforward:

- **Chunks that are too large** dilute the relevant information with surrounding noise.
- **Chunks that are too small** lose the context needed to make sense of the content.
- **The sweet spot** for most applications falls between 200 and 500 tokens, with roughly 50 tokens of overlap between adjacent chunks.

There is also a newer approach called **semantic chunking**, which uses embeddings to identify natural breakpoints in the text — splitting where the topic changes rather than at arbitrary token boundaries. This produces more coherent chunks that better preserve meaning.

## Embedding and Vector Storage

After chunking, each chunk must be embedded using an embedding model. OpenAI's Ada model is the common default, but newer models from **Cohere** and **Voyage AI** outperform it for retrieval tasks specifically, because they were trained with retrieval objectives in mind.

These embeddings are stored in a vector database — Pinecone, Weaviate, pgvector, or similar. At query time, the user's question is embedded with the same model, and a similarity search identifies the most relevant chunks.

## Advanced Retrieval Techniques

The basic embed-and-search approach works, but several techniques make it work substantially better.

### Query Expansion

Instead of embedding only the raw user query, an LLM generates multiple variations of the question, and all variations are used for search. This addresses a fundamental problem: users often phrase their questions differently from how the answer is stated in the source documents.

### Reranking with Cross-Encoders

After retrieving the top 20 or so results from vector search, a **cross-encoder** model reranks them. Cross-encoders are far more accurate than embedding similarity for judging relevance, but they are too slow to run over an entire corpus. Using them as a second pass on a candidate set gives the best of both worlds. Cohere offers a dedicated reranking API for this purpose.

### Metadata Filtering

When documents are indexed, metadata such as date, source, and document type can be attached. At query time, filtering on this metadata *before* vector search narrows the results. This is especially important for **multi-tenant applications** where each user should only see their own documents.

## Constructing Effective Prompts

Once the top-k chunks are retrieved, they need to be assembled into a prompt — and this is where many teams stumble. The most common mistake is simply concatenating all chunks without structure and hoping for the best.

Three practices dramatically improve generation quality:

1. **Order chunks by relevance.** Place the most relevant chunks first in the prompt. LLMs tend to pay more attention to the beginning of the context — a phenomenon documented in the "lost in the middle" paper from Stanford.

2. **Add source citations to each chunk.** Instead of providing raw text, include the source document name, page number, date, and other available metadata. Instruct the model to cite its sources in the answer. This anchors the model to specific documents and dramatically reduces hallucinations.

3. **Set a clear system prompt.** Tell the model to answer only based on the provided context and to respond with "I don't know" when the context does not contain the answer. For production systems, preventing the model from inventing information is critical.

## Hallucination Detection

Even with all of these guardrails, models will still occasionally hallucinate. Catching this requires a dedicated verification step.

The technique is called **grounded generation** or **faithfulness checking**: take the model's response and verify that each claim is actually supported by the retrieved context. This can be done with an additional LLM call or with **NLI (natural language inference) models** purpose-built for this kind of entailment checking.

## Evaluation: The Hardest and Most Neglected Part

Most teams do not evaluate their RAG systems at all — they "vibe check" the output and move on. That is acceptable for prototyping, but production systems require metrics.

### Retrieval Metrics

- **Recall@k** — Measures whether the relevant documents appear anywhere in the top-k results.
- **MRR (Mean Reciprocal Rank)** — Measures how highly the relevant document is ranked; a relevant document at position 1 scores much higher than one at position 10.

### Generation Metrics

- **Faithfulness** — Measures whether the generated answer is actually supported by the retrieved context.
- **Answer relevance** — Measures whether the answer addresses the user's question.

The **RAGAS** framework (Retrieval-Augmented Generation Assessment) automates much of this evaluation, providing these metrics out of the box against a test set of question-answer pairs.

## Production Monitoring and Cost Management

Beyond offline evaluation, production systems need ongoing monitoring:

- **Average retrieval score** — How similar are the retrieved chunks to the query on average?
- **Answer latency** — How long does the full pipeline take end to end?
- **User feedback** — Thumbs-up/thumbs-down signals from actual users.

Cost is also a practical concern. RAG can get expensive, especially when using models like GPT-4 or Claude for generation and high-quality embedding models for retrieval. Strategies to manage costs include **caching common queries**, **routing simple questions to cheaper models**, and **batching embedding calls**.

## Key Takeaways

- RAG retrieves your own documents and injects them into the LLM's context, producing answers grounded in your specific data rather than general training knowledge.
- Chunking strategy matters enormously — aim for 200-500 tokens with overlap, or use semantic chunking for more coherent segments.
- Newer embedding models from Cohere and Voyage AI outperform OpenAI Ada for retrieval-specific tasks.
- Query expansion, cross-encoder reranking, and metadata filtering each substantially improve retrieval quality beyond basic vector search.
- Structure your prompts deliberately: order by relevance, include source citations, and instruct the model to say "I don't know" when context is insufficient.
- Implement faithfulness checking to catch hallucinations, even after applying all other guardrails.
- Evaluate with real metrics (recall@k, MRR, faithfulness, answer relevance) — "vibe checking" is not enough for production.
- Monitor retrieval scores, latency, and user feedback continuously in production.
- The pipeline has many components, but they can be added incrementally — you do not need everything on day one.

---

*Sources: Building Production RAG Systems — Part 1: Retrieval; Building Production RAG Systems — Part 2: Generation and Evaluation*
