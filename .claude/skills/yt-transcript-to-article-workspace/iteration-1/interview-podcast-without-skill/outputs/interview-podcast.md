# Most Companies Are Over-Engineering Their Data Pipelines

*An interview with Marcus Rivera, CTO of DataFlow Labs*

Marcus Rivera has been building data infrastructure for fifteen years. As CTO of DataFlow Labs, he has consulted with companies of all sizes on their data architecture -- and he has a controversial claim: most companies are over-engineering their data pipelines.

In a conversation on the AI Engineering podcast, Rivera laid out his case for radical simplicity, both in traditional data infrastructure and in the emerging world of AI applications.

## The Netflix Effect

The pattern Rivera sees repeating is familiar to anyone in the data engineering world. A company starts with a simple ETL pipeline -- maybe using Airflow -- and it works fine. Then someone reads a blog post about how Netflix handles real-time streaming with Kafka, and suddenly everyone wants to rebuild everything to be real-time and event-driven.

"Netflix has 200 million subscribers generating massive amounts of data in real time. They actually need that infrastructure," Rivera said. "But if you're a B2B SaaS company with ten thousand customers, you probably don't. You're adding enormous complexity for no real benefit."

His advice is deliberately unglamorous: start with batch processing. Run pipelines once a day or once an hour. For 90 percent of use cases, that is perfectly fine. Dashboards update hourly instead of in real time, and nobody actually notices.

That is not to say real-time processing never has a place. Fraud detection, recommendation engines, and monitoring and alerting are legitimate real-time use cases. But even in those scenarios, Rivera advocates a hybrid approach: keep most of the pipeline in batch mode and maintain only a thin real-time layer for the things that genuinely require it.

## The Complexity Tax

Rivera frames the hidden costs of over-engineering as what he calls the "complexity tax" -- all the costs that people fail to account for when making architecture decisions.

Take Kafka as an example. Once you adopt it, you need someone who understands Kafka. You need to manage partitions and consumer groups, handle rebalancing, deal with schema evolution, and monitor lag. If something goes wrong at 3 AM, someone has to understand all of it to fix it.

"I've consulted with companies that have five-person data teams spending 80 percent of their time just keeping Kafka and Flink running," Rivera said. "They're like, 'We can't do any actual data science because all our time goes to infrastructure.' That's the complexity tax right there."

## Applying the Philosophy to AI

The same principles extend to the current wave of AI application development, where a whole new category of pipeline complexity has emerged: embedding pipelines, vector databases, RAG systems, fine-tuning pipelines, and evaluation frameworks. The temptation is to build an elaborate system with all of these components from day one.

Rivera pushes back against that impulse. His recommendations for getting started:

- **Skip the vector database on day one.** Just use a simple prompt with context included directly.
- **Skip fine-tuning.** Start with few-shot prompting.
- **Skip complex evaluation frameworks.** Start with what Rivera calls "vibes-based evaluation" -- a term he credits to Hamel Husain -- where you simply use the product and see if it feels right.

"For early-stage products, that's the right approach because you don't even know what 'good' looks like yet," he explained. "Building elaborate benchmarks is premature optimization."

The key insight is that you will know when you need to scale, because you will hit a specific, identifiable problem. Your context window is too small for all your documents -- now you actually need RAG. Latency is too high -- now you need to cache embeddings. Prompt engineering is hitting a ceiling -- now fine-tuning might make sense. Each of those is a clear signal, and you add exactly the component you need, nothing more.

## The Starter Stack

For anyone starting a new AI project, Rivera's recommended stack is almost aggressively minimal:

- **Database:** PostgreSQL with pgvector
- **LLM:** OpenAI or Anthropic API calls
- **Pipeline:** A simple Python script
- **Deployment:** A single server

"I know that sounds almost irresponsibly simple," Rivera admitted, "but you would be amazed at how far that gets you. And when you need more complexity, you'll know -- and you can add it then."

## The Bottom Line

Rivera's message cuts against the grain of an industry obsessed with adopting every new tool -- a stance he acknowledges is unusual for someone who is himself a vendor in the data infrastructure space.

"I genuinely believe that simpler is better," he said. "The companies that win are the ones that ship products, not the ones with the most sophisticated infrastructure."

---

*Marcus Rivera can be found on Twitter at @marcus\_rivera or on the DataFlow Labs blog at dataflowlabs.io/blog.*
