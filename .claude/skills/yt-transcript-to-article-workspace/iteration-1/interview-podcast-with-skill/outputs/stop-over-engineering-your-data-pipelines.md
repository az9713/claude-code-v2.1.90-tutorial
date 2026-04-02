# Stop Over-Engineering Your Data Pipelines: A Case for Radical Simplicity

> **TL;DR:** Most companies are wasting engineering resources by copying the data infrastructure of tech giants like Netflix, when simple batch processing would serve them just as well. Marcus Rivera, CTO of DataFlow Labs, argues that the "complexity tax" — the hidden cost of maintaining sophisticated systems — is crippling small data teams, and that this pattern is now repeating itself in the AI tooling space. His prescription: start embarrassingly simple and add complexity only when you hit a specific, measurable limitation.

**Source:** AI Engineering Podcast
**Speakers:** Sarah Chen (Host, AI Engineering Podcast) and Marcus Rivera (CTO, DataFlow Labs)

---

## The Netflix Effect: Why Companies Copy Infrastructure They Don't Need

After fifteen years building data infrastructure, Marcus Rivera has seen the same pattern play out over and over: a company starts with a simple ETL pipeline — maybe Airflow-based — and it works fine. Then someone reads a blog post about how Netflix handles real-time streaming with Kafka, and suddenly the whole team wants to rebuild everything to be real-time and event-driven.

Rivera calls this "the Netflix effect," and he considers it one of the most damaging patterns in modern data engineering. The core issue is a mismatch of scale: Netflix has roughly 200 million subscribers generating massive amounts of data in real time — they genuinely need that infrastructure. A B2B SaaS company with ten thousand customers almost certainly does not.

As Rivera puts it, "You're adding enormous complexity for no real benefit."

## The Complexity Tax

Rivera has coined a concept he calls the "complexity tax" — the hidden costs of running sophisticated infrastructure that teams fail to account for when making architecture decisions. Take Kafka as an example: once you adopt it, you need engineers who understand Kafka, you need to manage partitions and consumer groups, handle rebalancing, deal with schema evolution, and monitor lag. When something breaks at 3 AM, someone has to understand all of these interlocking systems to fix it.

The real-world cost of this tax is staggering. Rivera has consulted with companies where five-person data teams spend 80 percent of their time just keeping Kafka and Flink running. As he describes it, "They're like, 'We can't do any actual data science because all our time goes to infrastructure.'" That, he argues, is the complexity tax made visible — engineering capacity consumed entirely by maintenance rather than value creation.

## Batch Processing: Boring, Powerful, and Underrated

Rivera's recommendation is straightforward and deliberately unglamorous: start with batch processing. Run pipelines once a day or once an hour. For 90 percent of use cases, that cadence is perfectly adequate — dashboards update hourly instead of in real time, and nobody actually notices the difference.

This is not to say real-time processing has no place. Rivera identifies several legitimate real-time use cases: fraud detection, recommendation engines, and monitoring and alerting systems. But even in those scenarios, he advocates for a hybrid approach — keep most of the pipeline batch-based and layer in a thin real-time component only for the specific operations that genuinely require it. The key is surgical precision rather than wholesale adoption.

## The Same Mistake, Repeated for AI

The over-engineering pattern is now repeating itself in the AI application space, with a whole new category of pipeline complexity: embedding pipelines, vector databases, RAG systems, fine-tuning pipelines, and evaluation frameworks. The temptation, Rivera observes, is to build an elaborate system incorporating all of these components from day one.

His advice for AI projects mirrors his advice for data pipelines: start simple. Specifically:

- **Skip the vector database on day one.** Just stuff your context directly into the prompt.
- **Skip fine-tuning.** Start with few-shot prompting.
- **Skip complex evaluation frameworks.** Start with what Rivera calls "vibes-based evaluation" — a term he credits to Hamel Husain — where you simply use the product and assess whether it feels right.

That last point is particularly counterintuitive, but Rivera argues it makes sense for early-stage products. "You don't even know what good looks like yet," he explains, "so building elaborate benchmarks is premature optimization."

## Knowing When to Scale

The natural follow-up question is: when do you add complexity? Rivera's answer is that the system itself will tell you through specific, identifiable signals:

- **Your context window is too small** for all your documents — now you actually need RAG.
- **Your latency is too high** — now you need to cache embeddings.
- **Your prompt engineering is hitting a ceiling** — now fine-tuning might make sense.

Each of these is a clear, concrete signal, and the response should be equally targeted: add exactly the component you need, nothing more. This stands in contrast to the common approach of pre-building for every conceivable future requirement.

## The Vendor Paradox

Rivera acknowledges an irony in his position: as the CTO of a data infrastructure company, he is literally a vendor himself. Yet he genuinely believes simpler is better. The tooling ecosystem is exploding, and every vendor is telling companies they need their product. Rivera pushes back against this pressure directly: "The companies that win are the ones that ship products, not the ones with the most sophisticated infrastructure."

## The Radically Simple AI Stack

When asked for a concrete stack recommendation for someone starting a new AI project, Rivera's answer is almost provocatively minimal:

- **Database:** Postgres with pgvector
- **LLM:** OpenAI or Anthropic API calls
- **Pipeline:** A simple Python script
- **Deployment:** A single server

As Rivera acknowledges, "I know that sounds almost irresponsibly simple, but you would be amazed at how far that gets you." The philosophy is consistent throughout: when you need more complexity, you will know, and you can add it then.

## Key Takeaways

- **The "Netflix effect" is real and damaging** — most companies copy infrastructure designed for problems they don't have.
- **The complexity tax is invisible but enormous** — account for the full cost of maintenance, hiring, and on-call burden before adopting complex tools.
- **Batch processing handles 90% of use cases** — hourly updates are sufficient for most business needs.
- **Use a hybrid approach for real-time needs** — keep most of the pipeline batch-based and add a thin real-time layer only where truly necessary.
- **AI tooling is repeating the same over-engineering pattern** — resist the urge to build elaborate AI infrastructure before you need it.
- **Start with vibes-based evaluation** — you can't build meaningful benchmarks until you understand what "good" looks like for your product.
- **Let specific bottlenecks drive architecture decisions** — add components like RAG, embedding caches, or fine-tuning only when you hit a measurable limitation.
- **A radically simple stack can take you further than you think** — Postgres, an LLM API, a Python script, and one server is a legitimate starting point.
- **Shipping products beats sophisticated infrastructure** — engineering time spent on infrastructure maintenance is time not spent creating value.

---

*Sources: AI Engineering Podcast — Sarah Chen interviews Marcus Rivera (CTO, DataFlow Labs)*
