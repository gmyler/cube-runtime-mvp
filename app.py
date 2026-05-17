
import hashlib
import random
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st


# ============================================================
# CUBE RUNTIME — CONFERENCE DEMO
# ============================================================
# Two ideas:
#
# A) Valid witness:
#    The real boundary is allowed, but the internal room order moves.
#    There are many valid safe pathways; only one is active per request.
#
# B) Missing witness:
#    The real boundary does not exist for that flow.
#    The runtime generates an extendable synthetic maze.
#    The outside user sees plausible app behaviour.
#    The operator sees proof the crown jewel was never touched.
# ============================================================


st.set_page_config(
    page_title="Cube Runtime Conference Demo",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }

    .hero {
        padding: 2rem 2.2rem;
        border-radius: 28px;
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 45%, #701a75 100%);
        color: white;
        margin-bottom: 1.2rem;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.25);
    }

    .hero h1 {
        font-size: 3.1rem;
        margin: 0;
        line-height: 1.05;
        letter-spacing: -0.04em;
    }

    .hero p {
        margin-top: 0.9rem;
        font-size: 1.15rem;
        color: rgba(255, 255, 255, 0.84);
        max-width: 1050px;
    }

    .tag {
        display: inline-block;
        padding: 0.34rem 0.72rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.82rem;
        margin-right: 0.45rem;
        margin-bottom: 0.45rem;
    }

    .panel {
        padding: 1.15rem 1.2rem;
        border-radius: 22px;
        background: white;
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.07);
        margin-bottom: 1rem;
    }

    .panel-dark {
        padding: 1.15rem 1.2rem;
        border-radius: 22px;
        background: #0f172a;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.16);
        margin-bottom: 1rem;
    }

    .panel h3, .panel-dark h3 {
        margin-top: 0;
        margin-bottom: 0.6rem;
    }

    .mini-muted {
        color: #64748b;
        font-size: 0.94rem;
    }

    .mini-muted-dark {
        color: rgba(255, 255, 255, 0.72);
        font-size: 0.94rem;
    }

    .status-good {
        padding: 0.75rem 1rem;
        border-radius: 16px;
        background: #dcfce7;
        border: 1px solid #86efac;
        color: #14532d;
        font-weight: 700;
        text-align: center;
    }

    .status-warn {
        padding: 0.75rem 1rem;
        border-radius: 16px;
        background: #fef3c7;
        border: 1px solid #fcd34d;
        color: #78350f;
        font-weight: 700;
        text-align: center;
    }

    .status-bad {
        padding: 0.75rem 1rem;
        border-radius: 16px;
        background: #fee2e2;
        border: 1px solid #fca5a5;
        color: #7f1d1d;
        font-weight: 700;
        text-align: center;
    }

    .status-purple {
        padding: 0.75rem 1rem;
        border-radius: 16px;
        background: #f3e8ff;
        border: 1px solid #d8b4fe;
        color: #581c87;
        font-weight: 700;
        text-align: center;
    }

    .big-number {
        font-size: 2.2rem;
        line-height: 1;
        font-weight: 900;
        margin-bottom: 0.25rem;
        letter-spacing: -0.04em;
    }

    .chain-box {
        padding: 1rem;
        border-radius: 18px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.92rem;
        overflow-wrap: anywhere;
        margin-bottom: 0.7rem;
    }

    .room {
        display: inline-block;
        margin: 0.22rem 0.12rem;
        padding: 0.38rem 0.58rem;
        border-radius: 999px;
        background: #e0f2fe;
        border: 1px solid #7dd3fc;
        color: #0c4a6e;
        font-weight: 700;
        font-size: 0.8rem;
    }

    .room-real {
        background: #fee2e2;
        border-color: #fca5a5;
        color: #7f1d1d;
    }

    .room-fake {
        background: #f3e8ff;
        border-color: #d8b4fe;
        color: #581c87;
    }

    .room-broker {
        background: #dbeafe;
        border-color: #93c5fd;
        color: #1e3a8a;
    }

    .room-safe {
        background: #dcfce7;
        border-color: #86efac;
        color: #14532d;
    }

    .scenario-button button {
        height: 4.2rem !important;
        border-radius: 18px !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
    }

    .stButton > button {
        border-radius: 14px;
        font-weight: 700;
    }

    .footer-note {
        padding: 1rem 1.2rem;
        border-radius: 18px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #475569;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA
# ============================================================

REAL_INVOICE_DB = {
    "INV-100": {
        "owner": "alice",
        "amount": 1200,
        "status": "paid",
        "customer": "Acme Ltd",
        "line_items": ["support renewal", "priority support"],
    },
    "INV-200": {
        "owner": "bob",
        "amount": 9800,
        "status": "overdue",
        "customer": "Black Mesa",
        "line_items": ["enterprise support", "migration services"],
    },
    "INV-300": {
        "owner": "carla",
        "amount": 4200,
        "status": "pending",
        "customer": "Tyrell Systems",
        "line_items": ["platform advisory", "technical onboarding"],
    },
}

VALID_PATHWAYS = [
    {
        "name": "Valid Chain A",
        "description": "Ownership first, then audit, then boundary.",
        "rooms": [
            "AuthRoom",
            "OwnershipWitnessRoom",
            "AuditRoom",
            "InvoiceReadRoom",
            "BoundaryBroker",
            "RealInvoiceBoundary",
        ],
    },
    {
        "name": "Valid Chain B",
        "description": "Audit and cache first, then ownership witness.",
        "rooms": [
            "AuthRoom",
            "AuditRoom",
            "CacheRoom",
            "OwnershipWitnessRoom_v2",
            "InvoiceReadRoom_v2",
            "BoundaryBroker",
            "RealInvoiceBoundary",
        ],
    },
    {
        "name": "Valid Chain C",
        "description": "Risk and lineage enriched route.",
        "rooms": [
            "AuthRoom",
            "RiskContextRoom",
            "OwnershipWitnessRoom",
            "LineageRoom",
            "InvoiceReplicaReadRoom",
            "BoundaryBroker",
            "RealInvoiceBoundary",
        ],
    },
    {
        "name": "Valid Chain D",
        "description": "Replica read with post-boundary audit.",
        "rooms": [
            "AuthRoom",
            "OwnershipWitnessRoom_v3",
            "InvoiceReplicaReadRoom",
            "BoundaryBroker",
            "RealInvoiceBoundary",
            "PostReadAuditRoom",
        ],
    },
]

SYNTHETIC_ROOM_CATALOG = {
    "SyntheticInvoiceRoom": {
        "public_label": "invoice summary",
        "lures": ["audit", "download", "status"],
    },
    "FakeAuditRoom": {
        "public_label": "audit history",
        "lures": ["events", "export", "status"],
    },
    "FakeDownloadRoom": {
        "public_label": "download preparation",
        "lures": ["status", "hash", "retry"],
    },
    "FakePaymentStatusRoom": {
        "public_label": "payment status",
        "lures": ["history", "receipt", "status"],
    },
    "GeneratedExportRoom": {
        "public_label": "export queue",
        "lures": ["download", "events", "retry"],
    },
    "SyntheticWorkflowRoom": {
        "public_label": "workflow state",
        "lures": ["approval", "review", "status"],
    },
    "OrbitRoom": {
        "public_label": "processing state",
        "lures": ["status", "continue", "details"],
    },
    "EvidenceRoom": {
        "public_label": "review record",
        "lures": ["audit", "status", "continue"],
    },
}


# ============================================================
# STATE
# ============================================================

def init_state() -> None:
    defaults = {
        "run_counter": 0,
        "latest_event": None,
        "maze_state": None,
        "evidence_log": [],
        "active_demo": "none",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ============================================================
# CORE LOGIC
# ============================================================

def stable_hash(*parts: Any, length: int = 16) -> str:
    raw = "||".join(str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:length]


def rng_for(*parts: Any) -> random.Random:
    return random.Random(stable_hash(*parts, length=24))


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ownership_witness(user: str, invoice_id: str) -> bool:
    invoice = REAL_INVOICE_DB.get(invoice_id)
    return bool(invoice and invoice["owner"] == user)


def choose_valid_pathway(user: str, invoice_id: str, run_counter: int) -> Dict[str, Any]:
    rng = rng_for("valid", user, invoice_id, run_counter)
    return rng.choice(VALID_PATHWAYS)


def real_invoice_response(user: str, invoice_id: str) -> Dict[str, Any]:
    invoice = REAL_INVOICE_DB[invoice_id]
    return {
        "invoice_id": invoice_id,
        "customer": invoice["customer"],
        "amount": invoice["amount"],
        "status": invoice["status"],
        "line_items": invoice["line_items"],
        "viewer": user,
        "synthetic": False,
    }


def start_maze(user: str, invoice_id: str, run_counter: int) -> Dict[str, Any]:
    rng = rng_for("maze_start", user, invoice_id, run_counter)
    first_room = rng.choice(list(SYNTHETIC_ROOM_CATALOG.keys()))

    return {
        "maze_id": "maze_" + stable_hash(user, invoice_id, run_counter, length=10),
        "user": user,
        "invoice_id": invoice_id,
        "rooms": ["AuthRoom", "InvoiceIntentRoom", first_room],
        "choices": [],
        "depth": 1,
        "max_depth": 15,
        "created_at": utc_now(),
    }


def extend_maze(choice: str) -> Dict[str, Any]:
    maze = st.session_state.maze_state
    if not maze:
        raise RuntimeError("No generated maze is active.")

    rng = rng_for("maze_extend", maze["maze_id"], choice, maze["depth"])
    previous = maze["rooms"][-1]
    candidates = [r for r in SYNTHETIC_ROOM_CATALOG.keys() if r != previous]
    next_room = rng.choice(candidates)

    updated = dict(maze)
    updated["rooms"] = list(maze["rooms"]) + [next_room]
    updated["choices"] = list(maze["choices"]) + [choice]
    updated["depth"] = maze["depth"] + 1
    st.session_state.maze_state = updated
    return updated


def synthetic_response(maze: Dict[str, Any]) -> Dict[str, Any]:
    current_room = maze["rooms"][-1]
    meta = SYNTHETIC_ROOM_CATALOG.get(current_room, {})
    rng = rng_for("synthetic_response", maze["maze_id"], current_room, maze["depth"])

    statuses = [
        "processing",
        "reconciling",
        "queued",
        "under_review",
        "policy_review",
        "export_pending",
        "audit_sync_pending",
    ]

    fake_customers = [
        "Northstar Systems",
        "Helios Group",
        "Redwood Labs",
        "Orchid Finance",
        "Meridian Works",
        "Blue River Holdings",
    ]

    links = {}
    if maze["depth"] < maze["max_depth"]:
        for lure in meta.get("lures", ["status", "continue", "details"]):
            cursor = stable_hash(maze["maze_id"], current_room, lure, maze["depth"], length=8)
            links[lure] = f"/invoice/{maze['invoice_id']}/{lure}?cursor={cursor}"

    return {
        "invoice_id": maze["invoice_id"],
        "view": meta.get("public_label", "generated state"),
        "customer": rng.choice(fake_customers),
        "amount": rng.randint(400, 26000),
        "status": rng.choice(statuses),
        "message": "Your request is being processed.",
        "synthetic": True,
        "links": links,
    }


def behavioural_signature(maze: Dict[str, Any]) -> Dict[str, Any]:
    choices = maze.get("choices", [])
    rooms = maze.get("rooms", [])

    text = " ".join(choices + rooms).lower()

    preferred = "status/orbit"
    for lure in ["download", "export", "audit", "payment", "approval", "hash", "events"]:
        if lure in text:
            preferred = lure
            break

    return {
        "risk_pattern": "missing_witness_object_probe",
        "preferred_lure": preferred,
        "generated_rooms_visited": len(rooms),
        "choices_made": choices,
        "attempted_resource": maze["invoice_id"],
        "real_boundary_reached": False,
    }


def event_for_valid(user: str, invoice_id: str) -> Dict[str, Any]:
    st.session_state.run_counter += 1
    run_counter = st.session_state.run_counter

    pathway = choose_valid_pathway(user, invoice_id, run_counter)
    inactive = [p for p in VALID_PATHWAYS if p["name"] != pathway["name"]]

    return {
        "timestamp": utc_now(),
        "demo_type": "valid_witness",
        "headline": "Valid witness: moving real pathway",
        "user": user,
        "invoice_id": invoice_id,
        "witness_present": True,
        "real_boundary_reached": True,
        "synthetic_maze_active": False,
        "crown_jewel": "RealInvoiceBoundary",
        "active_pathway_name": pathway["name"],
        "active_pathway_description": pathway["description"],
        "active_chain": pathway["rooms"],
        "inactive_valid_pathways": inactive,
        "response": real_invoice_response(user, invoice_id),
        "operator_claim": "One real chain is active, but the room order can change between valid requests.",
        "outsider_claim": "The outside user sees only a normal invoice response, not the room map.",
    }


def event_for_missing(user: str, invoice_id: str) -> Dict[str, Any]:
    st.session_state.run_counter += 1
    run_counter = st.session_state.run_counter

    maze = start_maze(user, invoice_id, run_counter)
    st.session_state.maze_state = maze

    return {
        "timestamp": utc_now(),
        "demo_type": "missing_witness",
        "headline": "Missing witness: generated synthetic maze",
        "user": user,
        "invoice_id": invoice_id,
        "witness_present": False,
        "real_boundary_reached": False,
        "synthetic_maze_active": True,
        "crown_jewel": "RealInvoiceBoundary",
        "active_pathway_name": "Generated maze",
        "active_pathway_description": "No real chain to the crown jewel exists for this flow.",
        "active_chain": maze["rooms"],
        "inactive_valid_pathways": [],
        "maze": maze,
        "response": synthetic_response(maze),
        "behavioural_signature": behavioural_signature(maze),
        "operator_claim": "The generated path can extend, but the real boundary is absent.",
        "outsider_claim": "The outside user sees plausible app states and links, not the true room map.",
    }


def event_for_maze_follow(choice: str) -> Dict[str, Any]:
    maze = extend_maze(choice)

    return {
        "timestamp": utc_now(),
        "demo_type": "missing_witness",
        "headline": "Missing witness: generated maze extended",
        "user": maze["user"],
        "invoice_id": maze["invoice_id"],
        "witness_present": False,
        "real_boundary_reached": False,
        "synthetic_maze_active": True,
        "crown_jewel": "RealInvoiceBoundary",
        "active_pathway_name": "Generated maze extension",
        "active_pathway_description": f"The user followed '{choice}', so another synthetic room was generated.",
        "active_chain": maze["rooms"],
        "inactive_valid_pathways": [],
        "maze": maze,
        "response": synthetic_response(maze),
        "behavioural_signature": behavioural_signature(maze),
        "operator_claim": "Each follow-up choice extends the maze without opening the crown jewel.",
        "outsider_claim": "The outside user sees plausible next steps, not the internal synthetic labels.",
    }


def set_event(event: Dict[str, Any]) -> None:
    st.session_state.latest_event = event
    st.session_state.evidence_log.insert(0, event)


def reset_demo() -> None:
    st.session_state.run_counter = 0
    st.session_state.latest_event = None
    st.session_state.maze_state = None
    st.session_state.evidence_log = []
    st.session_state.active_demo = "none"


# ============================================================
# VISUAL HELPERS
# ============================================================

def room_badge(room: str) -> str:
    cls = "room-safe"
    if room == "RealInvoiceBoundary":
        cls = "room-real"
    elif room == "BoundaryBroker":
        cls = "room-broker"
    elif any(x in room for x in ["Synthetic", "Fake", "Orbit", "Evidence", "Generated"]):
        cls = "room-fake"

    return f'<span class="room {cls}">{room}</span>'


def room_chain_html(rooms: List[str]) -> str:
    bits = []
    for i, room in enumerate(rooms):
        bits.append(room_badge(room))
        if i < len(rooms) - 1:
            bits.append(" → ")
    return "".join(bits)


def graphviz(event: Dict[str, Any]) -> str:
    rooms = event.get("active_chain", [])
    lines = [
        "digraph G {",
        "rankdir=LR;",
        'graph [bgcolor="transparent"];',
        'node [shape=box, style="rounded,filled", fontname="Arial"];',
        'edge [fontname="Arial", color="#64748b"];',
    ]

    for i, room in enumerate(rooms):
        fill = "#DCFCE7"
        color = "#16A34A"
        label = room

        if room == "RealInvoiceBoundary":
            fill = "#FEE2E2"
            color = "#DC2626"
            label = f"{room}\\nCROWN JEWEL"
        elif room == "BoundaryBroker":
            fill = "#DBEAFE"
            color = "#2563EB"
        elif any(x in room for x in ["Synthetic", "Fake", "Orbit", "Evidence", "Generated"]):
            fill = "#F3E8FF"
            color = "#7E22CE"

        lines.append(
            f'"{room}_{i}" [label="{label}", fillcolor="{fill}", color="{color}", penwidth=2];'
        )

        if i > 0:
            lines.append(f'"{rooms[i-1]}_{i-1}" -> "{room}_{i}";')

    lines.append("}")
    return "\n".join(lines)


def status_box(label: str, status: str, kind: str = "good") -> None:
    cls = {
        "good": "status-good",
        "bad": "status-bad",
        "warn": "status-warn",
        "purple": "status-purple",
    }.get(kind, "status-good")

    st.markdown(
        f"""
        <div class="{cls}">
            <div style="font-size:0.76rem; text-transform:uppercase; letter-spacing:0.08em; opacity:0.75;">{label}</div>
            <div style="font-size:1.15rem;">{status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div>
            <span class="tag">Witness-based boundary access</span>
            <span class="tag">Moving valid pathways</span>
            <span class="tag">Generated missing-witness maze</span>
        </div>
        <h1>Cube Runtime Demo</h1>
        <p>
        A live app pathway demonstration: with a valid witness, one authorised chain is active while room order can move.
        With a missing witness, the real boundary is absent and an extendable synthetic maze is generated.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SCENARIO CONTROLS
# ============================================================

st.markdown("## 1. Pick the demonstration")

c1, c2, c3 = st.columns([1, 1, 0.75])

with c1:
    st.markdown('<div class="scenario-button">', unsafe_allow_html=True)
    if st.button("Run VALID witness demo\nAlice → INV-100", use_container_width=True):
        st.session_state.active_demo = "valid"
        set_event(event_for_valid("alice", "INV-100"))
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Shows many valid room orders, one active chain, real boundary reached.")

with c2:
    st.markdown('<div class="scenario-button">', unsafe_allow_html=True)
    if st.button("Run MISSING witness demo\nAlice → INV-200", use_container_width=True):
        st.session_state.active_demo = "missing"
        set_event(event_for_missing("alice", "INV-200"))
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Shows generated maze, synthetic data, no crown-jewel access.")

with c3:
    st.markdown('<div class="scenario-button">', unsafe_allow_html=True)
    if st.button("Reset", use_container_width=True):
        reset_demo()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Clear the demo state.")


event = st.session_state.latest_event

if not event:
    st.markdown(
        """
        <div class="footer-note">
        Start with the left button for the valid-witness story, then run the missing-witness story.
        The point is to show the two mechanisms separately.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# STATUS SUMMARY
# ============================================================

st.markdown("## 2. What happened?")

s1, s2, s3, s4 = st.columns(4)

with s1:
    status_box("Witness", "VALID" if event["witness_present"] else "MISSING", "good" if event["witness_present"] else "purple")

with s2:
    status_box("Real boundary", "REACHED" if event["real_boundary_reached"] else "NOT REACHED", "good" if event["real_boundary_reached"] else "bad")

with s3:
    status_box("Active chain", "REAL PATHWAY" if event["witness_present"] else "SYNTHETIC MAZE", "good" if event["witness_present"] else "purple")

with s4:
    outsider = "NO MAP LEAKED"
    status_box("Outsider view", outsider, "warn")


# ============================================================
# MAIN DEMO AREA
# ============================================================

st.markdown("## 3. Public view vs operator view")

public, operator = st.columns([0.9, 1.35], gap="large")

with public:
    st.markdown(
        """
        <div class="panel">
            <h3>Public app response</h3>
            <div class="mini-muted">
            This is what the outside user sees. They do not see internal room names or the active pathway.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.json(event["response"])

    if event.get("synthetic_maze_active"):
        links = event["response"].get("links", {})
        st.markdown("### Follow generated link")

        if not links:
            st.warning("Synthetic maze reached its configured max depth.")
        else:
            cols = st.columns(max(1, min(3, len(links))))
            for i, choice in enumerate(links.keys()):
                with cols[i % len(cols)]:
                    if st.button(f"Follow: {choice}", key=f"follow_{choice}_{event['timestamp']}"):
                        set_event(event_for_maze_follow(choice))
                        st.rerun()

    st.markdown(
        f"""
        <div class="panel">
            <h3>Public claim</h3>
            <div class="mini-muted">{event['outsider_claim']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with operator:
    st.markdown(
        f"""
        <div class="panel-dark">
            <h3>Operator / security control room</h3>
            <div class="mini-muted-dark">{event['operator_claim']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.graphviz_chart(graphviz(event))

    st.markdown("### Active chain")
    st.markdown(
        f'<div class="chain-box">{room_chain_html(event["active_chain"])}</div>',
        unsafe_allow_html=True,
    )

    if event["witness_present"]:
        st.markdown("### Valid pathway set")
        st.caption("Several valid room orders are allowed. Only one is active in this request.")

        active = event["active_pathway_name"]
        for p in VALID_PATHWAYS:
            prefix = "ACTIVE: " if p["name"] == active else "inactive: "
            with st.expander(prefix + p["name"] + " — " + p["description"], expanded=p["name"] == active):
                st.markdown(
                    f'<div class="chain-box">{room_chain_html(p["rooms"])}</div>',
                    unsafe_allow_html=True,
                )

    else:
        st.markdown("### Missing-witness behavioural signature")
        st.json(event.get("behavioural_signature", {}))

        st.markdown("### Maze state")
        st.json(event.get("maze", {}))


# ============================================================
# EXPLANATION STRIP
# ============================================================

st.markdown("## 4. Speaker explanation")

if event["witness_present"]:
    st.markdown(
        """
        <div class="footer-note">
        <b>Valid witness story:</b> the user is authorised for this resource. The real boundary is allowed, but the
        internal room order is not fixed. The runtime chooses one chain from a verified set of safe valid pathways.
        The user receives the correct invoice, but the outside observer does not learn the active internal route.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="footer-note">
        <b>Missing witness story:</b> the user is authenticated but not authorised for this resource. The real
        boundary is not merely hidden; it is absent for this flow. The runtime generates a synthetic pathway with
        plausible app states and links. Following those links extends the maze, while the crown jewel remains untouched.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# EVIDENCE LOG
# ============================================================

st.markdown("## 5. Evidence log")

for item in st.session_state.evidence_log[:12]:
    title = (
        f"{item['timestamp']} | {item['headline']} | "
        f"{item['user']} → {item['invoice_id']} | "
        f"boundary_reached={item['real_boundary_reached']}"
    )

    with st.expander(title):
        st.json(item)
