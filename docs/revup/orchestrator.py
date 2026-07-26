"""
Orchestrator agent for a revenue-acceleration multi-agent system.

Architecture:
    - Event-driven: agents don't call each other directly, they emit events
      onto a shared queue. The orchestrator is the only thing that reads
      the queue and decides what runs next.
    - Per-account state machine: each account has its own OrchestrationRun
      that tracks where it is in the pipeline. Multiple accounts run
      concurrently and independently.
    - Idempotent, restartable: state is persisted (here: in-memory store,
      swap for Redis/Postgres) so a crash doesn't lose in-flight work.

Run this file directly for a working simulation with mock agents:
    python orchestrator.py
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("orchestrator")


# --------------------------------------------------------------------------
# Domain types
# --------------------------------------------------------------------------

class EventType(str, Enum):
    USAGE_SPIKE = "usage_spike"
    RENEWAL_UPCOMING = "renewal_upcoming"
    SUPPORT_ESCALATION = "support_escalation"
    CHAMPION_LEFT = "champion_left"
    PRICING_PAGE_VISIT = "pricing_page_visit"
    EMAIL_OPENED = "email_opened"
    WEBINAR_ATTENDED = "webinar_attended"
    QUOTE_SENT = "quote_sent"          # emitted BY the pipeline, re-enters the queue


# Events that always imply "this account needs a concrete offer / intervention"
# regardless of what the fuzzy classifier says. Hardcoded because these are
# unambiguous business rules, not judgment calls.
HARD_BUYING_SIGNALS = {
    EventType.RENEWAL_UPCOMING,
    EventType.SUPPORT_ESCALATION,
    EventType.CHAMPION_LEFT,
    EventType.QUOTE_SENT,  # a sent quote always triggers a follow-up campaign, handled specially below
}


class RunState(str, Enum):
    RECEIVED = "received"
    PROFILING = "profiling"
    CLASSIFYING = "classifying"
    RECOMMENDING = "recommending"       # recommendation + pricing + CPQ validation
    CAMPAIGNING = "campaigning"         # targeting + content + channel orchestration
    DONE = "done"
    FAILED = "failed"


class EventClass(str, Enum):
    BUYING_OR_RISK = "buying_or_risk"
    ENGAGEMENT_ONLY = "engagement_only"
    FOLLOW_UP = "follow_up"  # special case: quote already sent, just needs nurture


@dataclass
class Event:
    account_id: str
    type: EventType
    payload: dict = field(default_factory=dict)
    received_at: float = field(default_factory=time.time)


@dataclass
class AccountProfile:
    account_id: str
    segment: str | None = None
    intent_score: float = 0.0
    health_score: float = 1.0
    last_profiled_at: float = 0.0

    def is_fresh(self, max_age_seconds: float = 24 * 3600) -> bool:
        return (time.time() - self.last_profiled_at) < max_age_seconds


@dataclass
class OrchestrationRun:
    """Tracks one event's journey through the pipeline for one account."""
    account_id: str
    event: Event
    state: RunState = RunState.RECEIVED
    attempts: int = 0
    error: str | None = None


# --------------------------------------------------------------------------
# Agent interfaces — swap these implementations for real model/API calls.
# Each is `async` so slow agents don't block the orchestrator loop.
# --------------------------------------------------------------------------

class ProfilingAgent(Protocol):
    async def refresh(self, account_id: str) -> AccountProfile: ...

class EventClassifier(Protocol):
    async def classify(self, profile: AccountProfile, event: Event) -> EventClass: ...

class RecommendationCpqAgent(Protocol):
    async def run(self, profile: AccountProfile, event: Event) -> dict: ...

class CampaignAgent(Protocol):
    async def run(self, profile: AccountProfile, event: Event, context: dict | None = None) -> dict: ...


# --------------------------------------------------------------------------
# Mock implementations (replace with real agents / model calls)
# --------------------------------------------------------------------------

class MockProfilingAgent:
    async def refresh(self, account_id: str) -> AccountProfile:
        await asyncio.sleep(0.05)  # simulate enrichment + scoring latency
        return AccountProfile(
            account_id=account_id,
            segment=random.choice(["enterprise", "mid_market", "smb"]),
            intent_score=round(random.uniform(0, 1), 2),
            health_score=round(random.uniform(0.4, 1), 2),
            last_profiled_at=time.time(),
        )


class RuleThenModelClassifier:
    """Hardcoded rules for unambiguous cases, falls back to a 'model' for fuzzy ones."""

    async def classify(self, profile: AccountProfile, event: Event) -> EventClass:
        if event.type == EventType.QUOTE_SENT:
            return EventClass.FOLLOW_UP
        if event.type in HARD_BUYING_SIGNALS:
            return EventClass.BUYING_OR_RISK

        # Fuzzy case: e.g. a pricing page visit means different things for a
        # brand-new trial account vs. an account three renewals deep.
        # This is where you'd call an actual classifier / LLM prompt.
        await asyncio.sleep(0.02)
        signal_strength = profile.intent_score * (1.2 if event.type == EventType.PRICING_PAGE_VISIT else 0.6)
        return EventClass.BUYING_OR_RISK if signal_strength > 0.5 else EventClass.ENGAGEMENT_ONLY


class MockRecommendationCpqAgent:
    async def run(self, profile: AccountProfile, event: Event) -> dict:
        await asyncio.sleep(0.05)
        return {
            "recommended_skus": ["sku_pro", "sku_addon_analytics"],
            "proposed_discount_pct": 12,
            "within_approval_limits": profile.segment != "enterprise",  # enterprise deals need deal desk
        }


class MockCampaignAgent:
    async def run(self, profile: AccountProfile, event: Event, context: dict | None = None) -> dict:
        await asyncio.sleep(0.05)
        mode = "quote_follow_up" if context else "nurture"
        return {"campaign_mode": mode, "channel": "email"}


# --------------------------------------------------------------------------
# The orchestrator itself
# --------------------------------------------------------------------------

class Orchestrator:
    def __init__(
        self,
        profiling_agent: ProfilingAgent,
        classifier: EventClassifier,
        rec_cpq_agent: RecommendationCpqAgent,
        campaign_agent: CampaignAgent,
        max_retries: int = 2,
    ) -> None:
        self.profiling_agent = profiling_agent
        self.classifier = classifier
        self.rec_cpq_agent = rec_cpq_agent
        self.campaign_agent = campaign_agent
        self.max_retries = max_retries

        self.queue: asyncio.Queue[Event] = asyncio.Queue()
        self.profiles: dict[str, AccountProfile] = {}       # swap for a real DB
        self.runs: dict[str, OrchestrationRun] = {}          # keyed by f"{account_id}:{event.received_at}"

    def emit(self, event: Event) -> None:
        """Any agent (or an external webhook handler) calls this to enqueue work."""
        self.queue.put_nowait(event)

    async def start(self, num_workers: int = 4) -> list[asyncio.Task]:
        return [asyncio.create_task(self._worker(i)) for i in range(num_workers)]

    async def _worker(self, worker_id: int) -> None:
        while True:
            event = await self.queue.get()
            run_id = f"{event.account_id}:{event.received_at}"
            run = OrchestrationRun(account_id=event.account_id, event=event)
            self.runs[run_id] = run
            try:
                await self._advance(run)
            except Exception as exc:  # noqa: BLE001
                run.attempts += 1
                run.error = str(exc)
                log.exception("run %s failed on attempt %d", run_id, run.attempts)
                if run.attempts <= self.max_retries:
                    backoff = 0.2 * (2 ** run.attempts)
                    await asyncio.sleep(backoff)
                    self.queue.put_nowait(event)  # retry
                else:
                    run.state = RunState.FAILED
                    log.error("run %s permanently failed: %s", run_id, run.error)
            finally:
                self.queue.task_done()

    async def _advance(self, run: OrchestrationRun) -> None:
        """The actual state machine. One event, walked start to finish."""
        event = run.event
        account_id = run.account_id

        # --- Check 1: is the profile fresh? ---
        run.state = RunState.PROFILING
        profile = self.profiles.get(account_id)
        if profile is None or not profile.is_fresh():
            log.info("[%s] profile stale/missing, refreshing", account_id)
            profile = await self.profiling_agent.refresh(account_id)
            self.profiles[account_id] = profile
        else:
            log.info("[%s] profile fresh, skipping refresh", account_id)

        # --- Check 2: classify the event ---
        run.state = RunState.CLASSIFYING
        event_class = await self.classifier.classify(profile, event)
        log.info("[%s] event %s classified as %s", account_id, event.type.value, event_class.value)

        # --- Route ---
        if event_class == EventClass.BUYING_OR_RISK:
            run.state = RunState.RECOMMENDING
            result = await self.rec_cpq_agent.run(profile, event)
            log.info("[%s] rec+cpq result: %s", account_id, result)

            if not result["within_approval_limits"]:
                log.info("[%s] exceeds approval limits -> deal desk (not modeled here)", account_id)
                # In a real system: emit a DEAL_DESK_REVIEW event and stop here;
                # a human approval elsewhere emits QUOTE_SENT to resume the flow.
            else:
                # quote auto-finalized -> this itself becomes a new event
                self.emit(Event(account_id=account_id, type=EventType.QUOTE_SENT, payload=result))

        elif event_class == EventClass.FOLLOW_UP:
            run.state = RunState.CAMPAIGNING
            result = await self.campaign_agent.run(profile, event, context=event.payload)
            log.info("[%s] follow-up campaign queued: %s", account_id, result)

        else:  # ENGAGEMENT_ONLY
            run.state = RunState.CAMPAIGNING
            result = await self.campaign_agent.run(profile, event)
            log.info("[%s] nurture campaign queued: %s", account_id, result)

        run.state = RunState.DONE


# --------------------------------------------------------------------------
# Demo
# --------------------------------------------------------------------------

async def main() -> None:
    orchestrator = Orchestrator(
        profiling_agent=MockProfilingAgent(),
        classifier=RuleThenModelClassifier(),
        rec_cpq_agent=MockRecommendationCpqAgent(),
        campaign_agent=MockCampaignAgent(),
    )
    workers = await orchestrator.start(num_workers=4)

    sample_events = [
        Event(account_id="acct_1", type=EventType.RENEWAL_UPCOMING),
        Event(account_id="acct_2", type=EventType.EMAIL_OPENED),
        Event(account_id="acct_3", type=EventType.PRICING_PAGE_VISIT),
        Event(account_id="acct_1", type=EventType.SUPPORT_ESCALATION),  # same account, second event
    ]
    for evt in sample_events:
        orchestrator.emit(evt)

    await orchestrator.queue.join()
    for w in workers:
        w.cancel()

    log.info("Final run states: %s", {k: v.state.value for k, v in orchestrator.runs.items()})


if __name__ == "__main__":
    asyncio.run(main())
