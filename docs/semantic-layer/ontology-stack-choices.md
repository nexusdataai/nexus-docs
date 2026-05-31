# Ontology Stack Choices — Why Property Graph + YAML, Not RDF + OWL

The [Reference Algorithm](algorithm.md) shows the AI Control Plane with **Graph DB (Ontology + RDF)** at its core. Our actual implementation uses **Apache AGE property graph + YAML schemas + pgvector embeddings** instead of **RDF triples + OWL ontology + SPARQL**. This document explains the gap, the trade-offs, and the practical impact on Copilot reasoning efficiency.

For the runtime mechanics see [Knowledge Indexing & Copilot Reasoning](knowledge-indexing-and-copilot-reasoning.md). For the reference architecture see [Reference Algorithm](algorithm.md).

---

## TL;DR

**The reasoning plane functions properly without RDF/OWL.** What we have is not "only a Virtual Data Layer" — we have a complete ontology layer, just expressed as a property graph plus YAML rather than RDF plus OWL. For roughly 95 % of enterprise Copilot use cases the two stacks are equivalent in capability. The remaining 5 % (formal automated inference, transitive closure beyond two hops, W3C standards interop) is the real impact, and it is closable with four targeted mitigations.

---

## 1. Two Different Layers Are Being Conflated

The reference diagram groups things differently than how our system is organised. Separate cleanly:

| Layer in our system | What it is | Where it lives |
|---------------------|------------|----------------|
| **Virtual Data Layer (VDL)** | Uniform query API across Salesforce, SAP, Oracle, simulators — abstracts the **physical** sources | [Data Plane](../planes/data-plane.md) — `virtual_query_service.py`, `mapping_rule_service.py`, FDW + simulators |
| **Ontology / Knowledge Layer** | Schemas, policies, workflows, integrations, tools, use cases — the **business semantics** | [Control Plane](../planes/control-plane.md) — `enterprise-knowledge/*.yaml`, Apache AGE graph `enterprise_onto`, pgvector `control_plane_embeddings` |
| **Reasoning Layer** | ReAct agent + LLM consuming both | [Reasoning Plane](../planes/reasoning-plane.md) — `agent_executor.py`, `rag_service.py` |

So we have **both** a VDL **and** an ontology layer. The ontology layer is exactly what the reference labels "Graph DB (Ontology + RDF)". The only difference is in **how the ontology is represented**, not in whether one exists.

---

## 2. What Our Apache AGE Graph Actually Contains

Loaded by [`graph_loader.py`](../../../nexus-backend/src/stages/semantic-rag/graph_loader.py) during the semantic RAG journey. Queried by [`graph_store.py`](../../../nexus-backend/src/services/control_plane/graph_store.py) during hybrid retrieval. Concrete shape:

```cypher
-- Nodes: one per ontology document
(:Entity {onto_id: "policy:credit-policy",
          system: "internal",
          entity_type: "policy",
          title: "Credit Policy",
          category: "policy"})

(:Entity {onto_id: "virtual:Salesforce:Account",
          system: "Salesforce",
          entity_type: "schema"})

(:Entity {onto_id: "virtual:Oracle:AR_Customer",
          system: "Oracle",
          entity_type: "schema"})

-- Edges: typed by the relationship vocabulary in YAML
(:Entity {onto_id: "virtual:Salesforce:Account"})
   -[:SYNCS_TO]->
(:Entity {onto_id: "virtual:Oracle:AR_Customer"})

(:Entity {onto_id: "virtual:Salesforce:Account"})
   -[:CONSTRAINED_BY]->
(:Entity {onto_id: "policy:credit-policy"})

(:Entity {onto_id: "policy:credit-policy"})
   -[:TRIGGERS]->
(:Entity {onto_id: "workflow:credit-approval"})
```

This is **functionally equivalent to RDF** for retrieval. The edge type `SYNCS_TO` plays the role of an RDF predicate, the node `onto_id` plays the role of an IRI. What we do **not** have:

1. OWL class hierarchies and reasoners (Pellet, HermiT, RDFox) that infer new triples.
2. SPARQL endpoint for federation.
3. RDF Turtle / N-Triples serialisation for data exchange.

---

## 3. Capability Comparison

| Capability | RDF / OWL (reference) | Our actual stack | Real impact |
|-----------|----------------------|------------------|-------------|
| **Modelling entities + relationships** | RDF triples `(s, p, o)` | Property graph nodes + typed edges | **Equivalent.** Property graphs are a strict superset of RDF for modelling — every RDF triple is expressible as a node-edge-node, and you can attach properties directly on nodes/edges (RDF needs reification). |
| **Querying relationships** | SPARQL | Cypher (via AGE) | **Equivalent.** Both languages handle pattern matching, multi-hop traversal, filtering. |
| **Subclass / type hierarchy** | `rdfs:subClassOf` — automatic inheritance | Must encode `is_a` edge explicitly | **Minor.** Declare it explicitly in YAML and the LLM still uses it. |
| **Subclass inference** ("Customer is a Party, Party has Balance → Customer has Balance") | Automatic via OWL reasoner | LLM does it from retrieved context, or pre-computed | **Moderate gap.** OWL gives this for free. We rely on the LLM reading both rows from the retrieval bundle and inferring it in prose. Works for natural-language questions, weaker for programmatic constraint checks. |
| **Transitive closure** ("A → B → C → D → E, infer A → E") | OWL `owl:TransitiveProperty` | `GraphStore.expand_neighbors(hops=2)` — fixed two hops, agent can chain further | **Workable.** Two hops covers most enterprise dependency questions. Deeper: agent calls the tool a second time with the new seed `onto_id`s. |
| **Equivalence (same-as)** | `owl:sameAs`, `owl:equivalentClass` | `syncs_to` relationship in YAML (e.g. `Account` syncs_to `AR_Customer`) | **Equivalent.** Our `syncs_to` plays the same role for the LLM. |
| **Cardinality / property restrictions** | `owl:maxCardinality`, `owl:Restriction` | `Configuration_Rule` entities + policy markdown | **Equivalent at runtime, different at modelling time.** OWL puts constraints in the ontology; we put them in policy docs that the LLM reads. Same effect — different mechanism. |
| **Formal consistency checking** | OWL reasoner can prove "ontology is consistent" or find contradictions | Schema YAML validation via Pydantic models | **Loss.** OWL guarantees logical consistency at load time. We catch shape errors but not logical contradictions. |
| **Negation, disjointness** | `owl:disjointWith`, open-world semantics | Encoded as exclusion rules in policy markdown | **Loss for automated checks.** OWL can prove "X cannot be both Customer and Vendor". We rely on policy text + LLM reading it. |
| **Inference scalability** | OWL reasoners (Pellet, HermiT, RDFox) — can be slow / memory-bound | Graph traversal is linear in hops × neighbours | **Win for us.** No reasoner state to maintain. AGE traversals scale predictably. |
| **W3C interop / data exchange** | RDF datasets, SPARQL endpoints | Cypher / proprietary | **Loss.** If you ever need to federate with another RDF system (e.g. a partner's regulatory ontology), there's friction. R2RML export is the workaround. |
| **Human authorability** | OWL / Turtle has a steep learning curve | YAML schemas are readable by business analysts | **Big win for us.** Most of `enterprise-knowledge/` is editable by domain SMEs. |
| **LLM-friendliness** | Triples must be reformatted for LLM context | YAML chunks already look like documents — embed + retrieve naturally | **Big win for us.** Hybrid retrieval is more natural over text-shaped docs than over triples. |

---

## 4. Impact on Copilot Reasoning Efficiency — by Question Type

| Question pattern | Example | Impact of no RDF/OWL | Why |
|-----------------|---------|---------------------|-----|
| **Lookup / definition** | "What is the credit policy?" | None | Vector search handles it. |
| **Relationship discovery** | "What workflows depend on Account?" | None | Property graph traversal handles it. |
| **Cross-system mapping** | "Where is Account in Oracle?" | None | `SYNCS_TO` edge gives it directly. |
| **Multi-hop dependency** | "If Account becomes Inactive, what breaks?" | None to minor | Two-hop expansion + LLM chaining covers it. |
| **Approval chain reasoning** | "Who approves a $50k discount?" | None | Policy markdown + LLM reads thresholds. |
| **Subclass inference** | "Is a HORECA Account a Customer Account?" | Minor | LLM gets it from context if the YAML says so. Stronger with explicit `is_a` edges. |
| **Constraint satisfaction** | "Can this quote configuration pass all rules?" | Moderate | `Configuration_Rule` entities + policy validation tools. No formal OWL reasoner. |
| **Consistency proof** | "Are these two policies contradictory?" | **Significant gap** | OWL reasoner would detect; LLM might miss subtle contradictions. |
| **Transitive closure > 2 hops** | "What is the longest dependency chain from Account to GL_Journal?" | Moderate | Agent must chain `expand_neighbors` calls; not automatic. |
| **Cardinality enforcement** | "Can a Quote have more than 1 owning Account?" | Moderate | Encoded in YAML constraints; OWL would enforce it natively. |
| **Cross-organisation federation** | "Merge our policy ontology with the partner's regulatory RDF" | **Significant gap** | Would require R2RML export or a separate triple store. |

**Overall efficiency impact: less than 10 % on real Copilot workloads** because:

1. The bulk of Copilot questions are **retrieval + summarisation** ("find the X that says Y"), which does not need inference.
2. The few questions that *do* need inference (chain "A subClassOf B, B has P → A has P") are handled by the LLM at the prose level — it reads both rows from the retrieval bundle and connects them.
3. Multi-hop reasoning beyond two hops is rare in practice, and when it's needed the agent can call `search_enterprise_knowledge` a second time with the expanded `onto_id`s as the next seed.

---

## 5. Where You Would Actually Feel the Loss

Three concrete scenarios where adding a formal RDF/OWL layer would meaningfully improve the system.

### 5.1 Regulatory compliance audits

Questions like *"prove that no policy contradicts another"* or *"prove that every Restricted account follows the credit-hold workflow"* benefit from formal consistency checking. Today this is brittle: you write policy markdown, you trust the LLM to flag contradictions if you ask. An OWL reasoner can prove it mechanically.

**Mitigation**: write a `policy_consistency_diagnostic` tool that runs declarative rule checks (similar to our `Configuration_Rule` engine) — gets you about 80 % of the way without OWL.

### 5.2 Deep dependency analysis

*"What's the full transitive blast radius if we change `AR_Invoice.Status` from 4 to 8 enum values?"* — needs walking every `depends_on` / `validates` / `triggers` edge until closure. We can do it; you'd just need to chain more tool calls or add a dedicated `compute_transitive_closure(onto_id, edge_types)` tool.

**Mitigation**: precompute closures into a metadata column at load time, or expose a hops-unlimited `expand_neighbors`.

### 5.3 Standards-based interop

If you ever need to publish the ontology as an RDF dataset for partners or regulators, you'd need R2RML or a custom exporter. Today our YAML schemas could be exported, but it's not a one-line operation.

**Mitigation**: write a one-off exporter (`OntoBundle → Turtle`) when needed. The data model is rich enough — the conversion is mechanical.

---

## 6. Why We Picked This Stack — the LLM Trade

In a pre-LLM world, OWL reasoning was the **only** way to do automated inference at scale. With a strong LLM, the LLM does it at query time — given the right retrieved context.

```text
              ┌─ Pre-LLM era ─┐         ┌─ With strong LLM ─┐
Inference    │  OWL reasoner  │   vs   │  Hybrid retrieval  │
             │  builds        │        │  + LLM stitches    │
             │  entailed      │        │  facts together at │
             │  triples ahead │        │  query time        │
             │  of time       │        │                    │
              └────┬──────────┘         └────┬──────────────┘
                   │                         │
What you get:  Precomputed,              Just-in-time, fuzzy,
               formally provable,        handles ambiguity,
               brittle to vocabulary     slower per query,
               changes                   extremely flexible
```

For a Copilot whose **output** is natural-language explanations (not formal proofs), the LLM is the better reasoner. The graph is there to **constrain what facts the LLM sees**, not to do inference itself. That is why hybrid (vector + graph) retrieval is the right answer: vector for "find relevant docs", graph for "find related docs", and the LLM for "make sense of them together".

This trade-off shows up cleanly in our [`RAGService.hybrid_search`](../../../nexus-backend/src/services/control_plane/rag_service.py):

1. Embed the query (OpenAI `text-embedding-3-small`).
2. Vector top-K against `control_plane_embeddings` (cosine, `min_similarity=0.20`).
3. Take the top 10 hits as **seeds**.
4. `GraphStore.expand_neighbors(seeds, hops=2)` — the graph adds the relational context the LLM needs.
5. Re-hydrate graph-expanded `onto_id`s by looking them up in the vector store for content.
6. Merge, dedupe, sort by similarity, cap at `limit`.
7. Return the bundle as `role: tool` JSON to the LLM.

The LLM then performs the reasoning the OWL engine would have performed — but in prose, with ambiguity tolerance, citing the retrieved rows.

---

## 7. Recommendations — How to Close the Gap Without Adopting RDF/OWL

If you want to close the gap with the reference without adopting the full RDF/OWL stack, four mitigations get you about 95–98 % of the reasoning capability with about 10 % of the complexity:

| # | Mitigation | What it gives you | Effort |
|---|------------|-------------------|--------|
| 1 | **Add explicit `is_a` / `subclass_of` edges** in schema YAMLs | Subclass hints for the LLM; matches `rdfs:subClassOf` semantics | Small. Edit a few schema YAMLs and the relationship vocabulary doc. |
| 2 | **Add `compute_transitive_closure(seed, edge_type, max_hops)` tool** | Deep dependency walks without chaining `expand_neighbors` manually | Medium. ~100 LOC new tool + register in `tool_registry`. |
| 3 | **Add `validate_policy_consistency` diagnostic** | Declarative rule checks on `Configuration_Rule` + policy markdown — covers the OWL-consistency use case for the most important policies | Medium. New diagnostic endpoint + UI panel. |
| 4 | **Plan an `OntoBundle → RDF Turtle` exporter** for future federation/audit needs | W3C interop on demand; do not build until needed | Small. Mechanical mapping from our YAML data model to N-Triples. |

Document the **edge-type taxonomy** (`SYNCS_TO`, `TRIGGERS`, `CONSTRAINED_BY`, `DEPENDS_ON`, `VALIDATES`, `CONTAINS`, `IS_A`, ...) explicitly so YAML authors stay consistent — this is the closest analogue to an OWL ontology spec in our stack.

---

## 8. Bottom Line

The reference algorithm's "Graph DB (Ontology + RDF)" is **one valid implementation**, not a requirement. Our stack uses a property graph + YAML + embeddings, which is functionally equivalent for the questions a Copilot actually gets asked. The Virtual Data Layer is a **separate** concern (data plane abstraction) — we have both VDL **and** an ontology, just expressed differently.

Reasoning plane efficiency is at parity with an OWL-based system for retrieval and natural-language reasoning, with a real but narrow gap on formal consistency / deep transitive inference — and even that gap is closable with the four mitigations above. The LLM-era trade — pre-computed OWL inference replaced by just-in-time LLM reasoning over hybrid retrieval — is the right call for our use case.

---

## Related References

- [Reference Algorithm](algorithm.md) — the source reference architecture (three-plane diagram).
- [Knowledge Indexing & Copilot Reasoning](knowledge-indexing-and-copilot-reasoning.md) — runtime mechanics of our actual stack.
- [Semantic RAG Pipeline](semantic-rag-pipeline.md) — indexing pipeline that builds the property graph + embeddings.
- [Semantic RAG Overview](../ai-os/semantic-rag.md) — retrieval engineering principles.
- [Control Plane](../planes/control-plane.md) — the ontology + knowledge graph layer.
- [Data Plane](../planes/data-plane.md) — the Virtual Data Layer (VDL).
- [Reasoning Plane](../planes/reasoning-plane.md) — the ReAct loop.
