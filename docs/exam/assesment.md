Aperture Architecture Assessment

Step 1: Read the Aperture Baseline
Review the Aperture system description. This is a post-MVP image-processing SaaS serving ~1,000 organizations, with synchronous processing and a simple serverless architecture.
Aperture: The MVP Baseline

Step 2: Complete Both Scenarios
For each scenario, provide:
Important Facts: Key constraints, limitations, and technical context that inform your decisions. Facts are important if knowing them changes what you decide. What matters about the current system? What limitations or capabilities of the technologies drive architectural choices?
Important Technical Decisions: Important means it's core to the system's function, shapes the architecture, or involves meaningful tradeoffs; obvious or trivial choices don't count. Technical means the considerations are about implementation (complexity, performance, scalability, maintainability), not cost or business constraints. Decision means you evaluated alternatives and chose with a clear rationale. Good decisions optimize what matters most by accepting tradeoffs on what matters less (e.g., accepting eventual consistency to maximize throughput). For each significant decision, document:
The problem (why is this decision important?)
Alternatives you considered
Your decision
Rationale (why you chose this over the alternatives)
Keep it concise. We want to see your reasoning, not exhaustive documentation.

This is not a purely theoretical exercise. Imagine you're actually building this system and will be responsible for operating it in production. We're evaluating how you think about real-world tradeoffs:
Simplicity: A theoretically elegant solution that's a nightmare to operate is worse than a simple solution that works.
Operational reality: Think about what happens after deployment. How do you debug issues? What happens when things fail?
Incrementalism: Aperture already has a working architecture. Rebuilding everything from scratch needs strong justification.
The best architectures are often (but not always) the ones that solve the problem with the least new machinery. If you find yourself proposing complex infrastructure, ask yourself: Is there a simpler way?

Step 3: Submitting Your Work
Copy the submission template: Aperture Architecture Assessment - Submission Template
Complete both scenarios in your copy of the template.
Set sharing permissions: Click "Share" → "Anyone with the link" → "Viewer"
Submit the link in the Crossover application form.



Scenario A: Bulk Processing Pipeline
Context: An enterprise customer wants to apply a custom, multi-step filter pipeline to hundreds of photos at once. Today, Aperture processes one image with one filter synchronously, with a 4.5MB file limit and 30-second timeout.

Question: How would you evolve the architecture to support this use case?

Consider:
How do users upload hundreds of large images?
How do you handle processing that takes minutes or hours?
How do you model "filter pipelines" (apply filter A, then B, then C)?
What happens if processing fails partway through?



Scenario B: Third-Party Filter Marketplace
Context: We want to open Aperture as a platform. Third-party developers should be able to create custom filters, publish them to a marketplace, and Aperture customers can purchase and use these filters on their images.

Question: How would you design this platform extension?

Consider:
How do third-party developers submit and deploy their filters?
How do you isolate third-party code from your core system?
What does the API contract look like between Aperture and third-party filters?
How do you handle versioning, deprecation, and breaking changes?
What does the billing/revenue share model require technically?

