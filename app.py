
import hashlib
import random
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st


# ============================================================
# CUBE RUNTIME SHOWCASE V2
# ============================================================
# Added:
#   1. Crown-jewel safety meter
#   2. Valid witness replay: same public result, moving internal room order
#   3. Missing-witness live attack mode: attacker actions generate synthetic rooms
# ============================================================


st.set_page_config(
    page_title="Cube Runtime Showcase V2",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.1rem;
        padding-bottom: 3rem;
        max-width: 1650px;
    }

    div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }

    .hero {
        padding: 2.2rem 2.45rem;
        border-radius: 30px;
        background:
          radial-gradient(circle at 12% 20%, rgba(59,130,246,0.35) 0%, transparent 28%),
          radial-gradient(circle at 85% 15%, rgba(236,72,153,0.42) 0%, transparent 30%),
          linear-gradient(135deg, #020617 0%, #1e1b4b 48%, #701a75 100%);
        color: white;
        margin-bottom: 1.1rem;
        box-shadow: 0 22px 60px rgba(15, 23, 42, 0.28);
    }

    .hero h1 {
        margin: 0;
        font-size: 3.35rem;
        line-height: 1;
        letter-spacing: -0.06em;
    }

    .hero p {
        margin: 0.95rem 0 0 0;
        max-width: 1180px;
        color: rgba(255,255,255,0.84);
        font-size: 1.13rem;
        line-height: 1.55;
    }

    .tag {
        display: inline-block;
        padding: 0.34rem 0.74rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        color: rgba(255,255,255,0.88);
        margin-right: 0.45rem;
        margin-bottom: 0.55rem;
        font-size: 0.82rem;
        font-weight: 800;
    }

    .section-title {
        margin-top: 1.25rem;
        margin-bottom: 0.8rem;
    }

    .meter {
        padding: 1rem 1.1rem;
        border-radius: 24px;
        background: #0f172a;
        color: white;
        box-shadow: 0 16px 36px rgba(15, 23, 42, 0.16);
        border: 1px solid rgba(255,255,255,0.08);
        min-height: 148px;
    }

    .meter h3 {
        margin: 0 0 0.45rem 0;
        font-size: 1.35rem;
    }

    .meter .small {
        color: rgba(255,255,255,0.68);
        font-size: 0.92rem;
        line-height: 1.45;
    }

    .meter-state {
        margin-top: 0.9rem;
        padding: 0.8rem 0.9rem;
        border-radius: 18px;
        font-size: 1.15rem;
        font-weight: 950;
        text-align: center;
        letter-spacing: -0.02em;
    }

    .meter-granted {
        background: #dcfce7;
        color: #14532d;
        border: 1px solid #86efac;
    }

    .meter-sealed {
        background: #fee2e2;
        color: #7f1d1d;
        border: 1px solid #fca5a5;
    }

    .meter-neutral {
        background: #f8fafc;
        color: #334155;
        border: 1px solid #cbd5e1;
    }

    .story-card {
        padding: 1.2rem 1.25rem;
        border-radius: 24px;
        background: white;
        border: 1px solid #e2e8f0;
        box-shadow: 0 13px 28px rgba(15, 23, 42, 0.08);
        margin-bottom: 1rem;
        min-height: 138px;
    }

    .story-card h3 {
        margin: 0 0 0.55rem 0;
        font-size: 1.45rem;
    }

    .valid-card {
        border-top: 7px solid #22c55e;
    }

    .missing-card {
        border-top: 7px solid #a855f7;
    }

    .muted {
        color: #64748b;
        font-size: 0.96rem;
        line-height: 1.5;
    }

    .metric-card {
        padding: 1rem 1.1rem;
        border-radius: 22px;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
        text-align: center;
        height: 118px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 0.85rem;
    }

    .metric-label {
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 850;
        color: #64748b;
        font-size: 0.76rem;
    }

    .metric-value {
        margin-top: 0.3rem;
        font-size: 1.36rem;
        font-weight: 950;
        letter-spacing: -0.035em;
    }

    .metric-green { background: #dcfce7; border-color: #86efac; color: #14532d; }
    .metric-purple { background: #f3e8ff; border-color: #d8b4fe; color: #581c87; }
    .metric-red { background: #fee2e2; border-color: #fca5a5; color: #7f1d1d; }
    .metric-yellow { background: #fef9c3; border-color: #fde047; color: #713f12; }
    .metric-blue { background: #dbeafe; border-color: #93c5fd; color: #1e3a8a; }

    .roomline {
        padding: 1rem 1rem;
        border-radius: 20px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        margin: 0.8rem 0;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        line-height: 2.3;
        overflow-wrap: anywhere;
    }

    .room {
        display: inline-block;
        padding: 0.34rem 0.58rem;
        border-radius: 999px;
        border: 1px solid #93c5fd;
        background: #dbeafe;
        color: #1e3a8a;
        font-weight: 850;
        font-size: 0.78rem;
        margin: 0.12rem;
    }

    .room-safe { background: #dcfce7; border-color: #86efac; color: #14532d; }
    .room-fake { background: #f3e8ff; border-color: #d8b4fe; color: #581c87; }
    .room-crown { background: #fee2e2; border-color: #fca5a5; color: #7f1d1d; }
    .room-broker { background: #dbeafe; border-color: #93c5fd; color: #1e3a8a; }
    .room-attack { background: #ffedd5; border-color: #fdba74; color: #7c2d12; }

    .app-screen {
        padding: 1.2rem 1.25rem;
        border-radius: 26px;
        background: #0f172a;
        color: white;
        box-shadow: 0 18px 38px rgba(15,23,42,0.22);
        margin-bottom: 1rem;
    }

    .fake-ui-row {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid rgba(148,163,184,0.28);
        padding: 0.7rem 0;
        gap: 1rem;
    }

    .fake-ui-label {
        color: #94a3b8;
        font-weight: 750;
    }

    .fake-ui-value {
        font-weight: 900;
        text-align: right;
    }

    .claim {
        padding: 1rem 1.1rem;
        border-radius: 20px;
        background: #f8fafc;
        border-left: 7px solid #6366f1;
        color: #334155;
        font-size: 1rem;
        line-height: 1.55;
        margin-top: 0.9rem;
    }

    .attack-panel {
        padding: 1rem 1.1rem;
        border-radius: 24px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
        box-shadow: 0 10px 24px rgba(124,45,18,0.08);
        margin: 0.8rem 0 1rem 0;
    }

    .attack-panel h4 {
        margin: 0 0 0.6rem 0;
        color: #7c2d12;
        font-size: 1.15rem;
    }

    .footer {
        padding: 1rem 1.2rem;
        border-radius: 22px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #475569;
        line-height: 1.55;
    }

    .stButton > button {
        border-radius: 16px !important;
        font-weight: 850 !important;
        min-height: 3.1rem;
    }

    .primary-button button {
        min-height: 4.45rem !important;
        font-size: 1.03rem !important;
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
        "customer": "Acme Ltd",
        "amount": 1200,
        "status": "paid",
        "line_items": ["support renewal", "priority support"],
    },
    "INV-200": {
        "owner": "bob",
        "customer": "Black Mesa",
        "amount": 9800,
        "status": "overdue",
        "line_items": ["enterprise support", "migration services"],
    },
}

VALID_PATHWAYS = [
    {
        "name": "Verified Chain A",
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
        "name": "Verified Chain B",
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
        "name": "Verified Chain C",
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
        "name": "Verified Chain D",
        "rooms": [
            "AuthRoom",
            "OwnershipWitnessRoom_v3",
            "InvoiceReplicaReadRoom",
            "BoundaryBroker",
            "RealInvoiceBoundary",
            "PostReadAuditRoom",
        ],
    },
    {
        "name": "Verified Chain E",
        "rooms": [
            "AuthRoom",
            "DevicePostureRoom",
            "OwnershipWitnessRoom",
            "LeastPrivilegeRoom",
            "InvoiceReadRoom",
            "BoundaryBroker",
            "RealInvoiceBoundary",
        ],
    },
]

ATTACK_ACTIONS = {
    "View invoice": {
        "intent": "object_probe",
        "rooms": ["SyntheticInvoiceRoom", "FakeAuditRoom", "OrbitRoom"],
        "lures": ["audit", "status", "download"],
    },
    "Download PDF": {
        "intent": "exfiltration_probe",
        "rooms": ["FakeDownloadRoom", "HashPreparationRoom", "GeneratedExportRoom"],
        "lures": ["hash", "retry", "export"],
    },
    "Export audit trail": {
        "intent": "audit_exfiltration_probe",
        "rooms": ["FakeAuditRoom", "GeneratedExportRoom", "EvidenceRoom"],
        "lures": ["events", "download", "continue"],
    },
    "Change payment status": {
        "intent": "state_change_probe",
        "rooms": ["FakePaymentStatusRoom", "SyntheticWorkflowRoom", "ApprovalShadowRoom"],
        "lures": ["approval", "review", "receipt"],
    },
    "Try admin route": {
        "intent": "privilege_probe",
        "rooms": ["AdminMirageRoom", "PolicyEchoRoom", "OrbitRoom"],
        "lures": ["continue", "status", "review"],
    },
    "Replay old token": {
        "intent": "token_replay_probe",
        "rooms": ["TokenEchoRoom", "SessionShadowRoom", "FakeAuditRoom"],
        "lures": ["events", "status", "retry"],
    },
}

SYNTHETIC_FALLBACK_ROOMS = [
    "SyntheticInvoiceRoom",
    "FakeAuditRoom",
    "FakeDownloadRoom",
    "GeneratedExportRoom",
    "SyntheticWorkflowRoom",
    "OrbitRoom",
    "EvidenceRoom",
    "HashPreparationRoom",
    "ApprovalShadowRoom",
    "AdminMirageRoom",
    "PolicyEchoRoom",
    "TokenEchoRoom",
    "SessionShadowRoom",
]


# ============================================================
# STATE
# ============================================================

def init() -> None:
    defaults = {
        "run_counter": 0,
        "valid_event": None,
        "valid_replays": [],
        "missing_event": None,
        "maze": None,
        "evidence_log": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init()


# ============================================================
# LOGIC
# ============================================================

def stable_hash(*parts: Any, length: int = 16) -> str:
    raw = "||".join(str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:length]


def rng_for(*parts: Any) -> random.Random:
    return random.Random(stable_hash(*parts, length=24))


def now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def choose_valid_chain() -> Dict[str, Any]:
    st.session_state.run_counter += 1
    rng = rng_for("valid", st.session_state.run_counter)
    return rng.choice(VALID_PATHWAYS)


def make_valid_event() -> Dict[str, Any]:
    user = "alice"
    invoice_id = "INV-100"
    invoice = REAL_INVOICE_DB[invoice_id]
    chain = choose_valid_chain()

    event = {
        "timestamp": now(),
        "type": "valid_witness",
        "user": user,
        "invoice_id": invoice_id,
        "witness": "VALID",
        "real_boundary_reached": True,
        "crown_jewel_state": "ACCESS GRANTED THROUGH VERIFIED PATH",
        "active_chain_name": chain["name"],
        "active_chain": chain["rooms"],
        "valid_pathway_count": len(VALID_PATHWAYS),
        "inactive_chains": [p for p in VALID_PATHWAYS if p["name"] != chain["name"]],
        "public_response": {
            "invoice_id": invoice_id,
            "customer": invoice["customer"],
            "amount": invoice["amount"],
            "status": invoice["status"],
            "line_items": invoice["line_items"],
            "synthetic": False,
        },
        "security_claim": "The real boundary is reached, but the route/order is not fixed.",
    }

    st.session_state.valid_event = event
    st.session_state.valid_replays.insert(0, event)
    st.session_state.valid_replays = st.session_state.valid_replays[:5]
    st.session_state.evidence_log.insert(0, event)
    return event


def start_maze(action_name: str) -> Dict[str, Any]:
    st.session_state.run_counter += 1

    action = ATTACK_ACTIONS[action_name]
    rng = rng_for("maze_start", action_name, st.session_state.run_counter)

    action_rooms = list(action["rooms"])
    rng.shuffle(action_rooms)

    maze = {
        "maze_id": "maze_" + stable_hash("maze", action_name, st.session_state.run_counter, length=10),
        "user": "alice",
        "invoice_id": "INV-200",
        "rooms": ["AuthRoom", "InvoiceIntentRoom"] + action_rooms[:2],
        "choices": [action_name],
        "actions": [action_name],
        "depth": 1,
        "max_depth": 30,
        "last_action": action_name,
        "intent_counts": {action["intent"]: 1},
    }

    st.session_state.maze = maze
    return maze


def extend_maze(action_name: str) -> Dict[str, Any]:
    if st.session_state.maze is None:
        return start_maze(action_name)

    maze = dict(st.session_state.maze)
    action = ATTACK_ACTIONS[action_name]
    rng = rng_for("maze_extend", maze["maze_id"], action_name, maze["depth"], len(maze["rooms"]))

    action_rooms = list(action["rooms"])
    rng.shuffle(action_rooms)

    previous = maze["rooms"][-1]
    candidates = [r for r in action_rooms + SYNTHETIC_FALLBACK_ROOMS if r != previous]
    new_room_count = 2 if action_name in {"Download PDF", "Export audit trail", "Try admin route"} else 1
    new_rooms = []

    for _ in range(new_room_count):
        room = rng.choice(candidates)
        if room not in new_rooms:
            new_rooms.append(room)

    maze["rooms"] = list(maze["rooms"]) + new_rooms
    maze["choices"] = list(maze["choices"]) + [action_name]
    maze["actions"] = list(maze["actions"]) + [action_name]
    maze["depth"] += 1
    maze["last_action"] = action_name

    counts = dict(maze.get("intent_counts", {}))
    counts[action["intent"]] = counts.get(action["intent"], 0) + 1
    maze["intent_counts"] = counts

    st.session_state.maze = maze
    return maze


def synthetic_public_response(maze: Dict[str, Any]) -> Dict[str, Any]:
    current = maze["rooms"][-1]
    rng = rng_for("synthetic", maze["maze_id"], current, maze["depth"])

    statuses = [
        "processing",
        "queued",
        "under review",
        "audit sync pending",
        "export pending",
        "policy review",
        "reconciling",
    ]
    fake_customers = [
        "Northstar Systems",
        "Helios Group",
        "Orchid Finance",
        "Meridian Works",
        "Blue River Holdings",
    ]

    # Lures are based on the current attack profile, not the real app.
    last_action = maze.get("last_action", "View invoice")
    lures = ATTACK_ACTIONS.get(last_action, {}).get("lures", ["status", "continue", "details"])

    links = {}
    if maze["depth"] < maze["max_depth"]:
        for lure in lures:
            links[lure] = f"/invoice/{maze['invoice_id']}/{lure}?cursor={stable_hash(maze['maze_id'], lure, maze['depth'], length=8)}"

    return {
        "invoice_id": maze["invoice_id"],
        "customer": rng.choice(fake_customers),
        "amount": rng.randint(900, 24000),
        "status": rng.choice(statuses),
        "screen": current,
        "synthetic": True,
        "links": links,
    }


def behavioural_signature(maze: Dict[str, Any]) -> Dict[str, Any]:
    intent_counts = maze.get("intent_counts", {})
    if intent_counts:
        dominant = max(intent_counts.items(), key=lambda kv: kv[1])[0]
    else:
        dominant = "unknown_probe"

    return {
        "pattern": "missing_witness_object_probe",
        "dominant_intent": dominant,
        "actions_seen": maze.get("actions", []),
        "generated_rooms": len(maze.get("rooms", [])),
        "maze_depth": maze.get("depth", 0),
        "attempted_resource": maze.get("invoice_id"),
        "crown_jewel_touched": False,
        "real_boundary_reached": False,
    }


def make_missing_event(action_name: str = "View invoice") -> Dict[str, Any]:
    if st.session_state.maze is None:
        maze = start_maze(action_name)
        action = "maze_started"
    else:
        maze = extend_maze(action_name)
        action = f"attacker_action::{action_name}"

    event = {
        "timestamp": now(),
        "type": "missing_witness",
        "action": action,
        "user": maze["user"],
        "invoice_id": maze["invoice_id"],
        "witness": "MISSING",
        "real_boundary_reached": False,
        "crown_jewel_state": "SEALED / NOT IN TOPOLOGY",
        "active_chain_name": "Generated Synthetic Maze",
        "active_chain": maze["rooms"],
        "public_response": synthetic_public_response(maze),
        "signature": behavioural_signature(maze),
        "security_claim": "No real chain to the crown jewel exists for this flow.",
        "maze": maze,
    }

    st.session_state.missing_event = event
    st.session_state.evidence_log.insert(0, event)
    return event


def reset() -> None:
    st.session_state.run_counter = 0
    st.session_state.valid_event = None
    st.session_state.valid_replays = []
    st.session_state.missing_event = None
    st.session_state.maze = None
    st.session_state.evidence_log = []


# ============================================================
# VISUAL HELPERS
# ============================================================

def room_class(room: str) -> str:
    if room == "RealInvoiceBoundary":
        return "room-crown"
    if room == "BoundaryBroker":
        return "room-broker"
    if any(x in room for x in ["Synthetic", "Fake", "Generated", "Orbit", "Evidence", "Shadow", "Mirage", "Echo", "Hash", "Approval"]):
        return "room-fake"
    if "Intent" in room:
        return "room-attack"
    return "room-safe"


def roomline(rooms: List[str]) -> str:
    out = []
    for i, r in enumerate(rooms):
        out.append(f'<span class="room {room_class(r)}">{r}</span>')
        if i < len(rooms) - 1:
            out.append(" → ")
    return "".join(out)


def metric(label: str, value: str, kind: str) -> None:
    cls = f"metric-card metric-{kind}"
    st.markdown(
        f"""
        <div class="{cls}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def meter(title: str, state: str, subtitle: str, kind: str) -> None:
    cls = {
        "granted": "meter-granted",
        "sealed": "meter-sealed",
        "neutral": "meter-neutral",
    }.get(kind, "meter-neutral")

    st.markdown(
        f"""
        <div class="meter">
            <h3>{title}</h3>
            <div class="small">{subtitle}</div>
            <div class="meter-state {cls}">{state}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def public_invoice_card(resp: Dict[str, Any], title: str) -> None:
    synthetic = resp.get("synthetic", False)
    synth_label = "Synthetic app state" if synthetic else "Real invoice result"
    synth_color = "#a855f7" if synthetic else "#22c55e"

    st.markdown(
        f"""
        <div class="app-screen">
            <div style="display:flex;justify-content:space-between;gap:1rem;align-items:center;">
                <div>
                    <div style="font-size:0.82rem;color:#94a3b8;font-weight:850;text-transform:uppercase;letter-spacing:0.08em;">{title}</div>
                    <div style="font-size:1.55rem;font-weight:950;margin-top:0.15rem;">Invoice Portal</div>
                </div>
                <div style="padding:0.35rem 0.7rem;border-radius:999px;background:{synth_color};font-weight:900;">{synth_label}</div>
            </div>
            <div style="margin-top:1rem;">
                <div class="fake-ui-row"><span class="fake-ui-label">Invoice</span><span class="fake-ui-value">{resp.get('invoice_id')}</span></div>
                <div class="fake-ui-row"><span class="fake-ui-label">Customer</span><span class="fake-ui-value">{resp.get('customer')}</span></div>
                <div class="fake-ui-row"><span class="fake-ui-label">Amount</span><span class="fake-ui-value">€{resp.get('amount')}</span></div>
                <div class="fake-ui-row"><span class="fake-ui-label">Status</span><span class="fake-ui-value">{resp.get('status')}</span></div>
                <div class="fake-ui-row"><span class="fake-ui-label">Screen</span><span class="fake-ui-value">{resp.get('screen', 'invoice detail')}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def graphviz(rooms: List[str]) -> str:
    lines = [
        "digraph G {",
        "rankdir=LR;",
        'graph [bgcolor="transparent"];',
        'node [shape=box, style="rounded,filled", fontname="Arial"];',
        'edge [fontname="Arial", color="#64748b"];',
    ]
    for i, r in enumerate(rooms):
        fill = "#DCFCE7"
        color = "#16A34A"
        label = r
        if r == "RealInvoiceBoundary":
            fill = "#FEE2E2"
            color = "#DC2626"
            label = f"{r}\\nCROWN JEWEL"
        elif r == "BoundaryBroker":
            fill = "#DBEAFE"
            color = "#2563EB"
        elif any(x in r for x in ["Synthetic", "Fake", "Generated", "Orbit", "Evidence", "Shadow", "Mirage", "Echo", "Hash", "Approval"]):
            fill = "#F3E8FF"
            color = "#7E22CE"
        elif "Intent" in r:
            fill = "#FFEDD5"
            color = "#EA580C"
        lines.append(f'"{r}_{i}" [label="{label}", fillcolor="{fill}", color="{color}", penwidth=2];')
        if i:
            lines.append(f'"{rooms[i-1]}_{i-1}" -> "{r}_{i}";')
    lines.append("}")
    return "\n".join(lines)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <span class="tag">Crown-jewel safety meter</span>
        <span class="tag">Moving valid pathways</span>
        <span class="tag">Live synthetic maze</span>
        <span class="tag">Attacker behaviour signature</span>
        <h1>Cube Runtime Showcase V2</h1>
        <p>
        A cyber-conference demo of witness-controlled topology:
        valid flows reach the crown jewel through a moving verified path;
        missing-witness flows enter a generated maze where the real boundary is not in the topology.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONTROLS
# ============================================================

st.markdown("## Run the demonstration")

b1, b2, b3, b4, b5 = st.columns([1.05, 1.05, 1.05, 1.05, 0.65])

with b1:
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    if st.button("Run valid witness\nAlice → INV-100", use_container_width=True):
        make_valid_event()
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    if st.button("Replay valid request\nsame output, new path", use_container_width=True):
        make_valid_event()
    st.markdown("</div>", unsafe_allow_html=True)

with b3:
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    if st.button("Run missing witness\nAlice → INV-200", use_container_width=True):
        make_missing_event("View invoice")
    st.markdown("</div>", unsafe_allow_html=True)

with b4:
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    if st.button("Run both stories", use_container_width=True):
        make_valid_event()
        make_missing_event("View invoice")
    st.markdown("</div>", unsafe_allow_html=True)

with b5:
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    if st.button("Reset", use_container_width=True):
        reset()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


valid = st.session_state.valid_event
missing = st.session_state.missing_event

if not valid and not missing:
    st.markdown(
        """
        <div class="footer">
        <b>Fast demo:</b> click <b>Run both stories</b>. Then use <b>Replay valid request</b>
        to show the same legitimate output moving through different real room orders. Use the attacker buttons
        on the missing-witness side to show the synthetic maze extending.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# SAFETY METERS
# ============================================================

st.markdown('<div class="section-title"><h2>Crown-jewel safety meter</h2></div>', unsafe_allow_html=True)

m_left, m_right = st.columns(2, gap="large")

with m_left:
    if valid:
        meter(
            "Valid witness flow",
            "ACCESS GRANTED THROUGH VERIFIED PATH",
            "The witness exists, so the real boundary may be reached. The internal room order can still move.",
            "granted",
        )
    else:
        meter(
            "Valid witness flow",
            "NOT RUN YET",
            "Run the valid witness story to show the moving real pathway.",
            "neutral",
        )

with m_right:
    if missing:
        meter(
            "Missing witness flow",
            "SEALED / NOT IN TOPOLOGY",
            "The witness is missing, so the real crown-jewel boundary is absent for this flow.",
            "sealed",
        )
    else:
        meter(
            "Missing witness flow",
            "NOT RUN YET",
            "Run the missing witness story to show the generated maze.",
            "neutral",
        )


# ============================================================
# SIDE-BY-SIDE STORIES
# ============================================================

st.markdown('<div class="section-title"><h2>Valid witness vs missing witness</h2></div>', unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

# ---------------- VALID ----------------
with left:
    st.markdown(
        """
        <div class="story-card valid-card">
            <h3>Valid witness: moving real pathway</h3>
            <div class="muted">
            The user owns the resource. The system reaches the real boundary, but the room order is not fixed.
            Replaying the same valid request can select a different verified chain while the public result stays the same.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if valid:
        c1, c2, c3 = st.columns(3)
        with c1:
            metric("Witness", "VALID", "green")
        with c2:
            metric("Boundary", "REACHED", "green")
        with c3:
            metric("Active path", valid["active_chain_name"].replace("Verified ", ""), "blue")

        public_invoice_card(valid["public_response"], "Public user view")

        st.markdown("### Operator view: selected real chain")
        st.graphviz_chart(graphviz(valid["active_chain"]))
        st.markdown(f'<div class="roomline">{roomline(valid["active_chain"])}</div>', unsafe_allow_html=True)

        st.markdown("### Replay history")
        if len(st.session_state.valid_replays) <= 1:
            st.caption("Click Replay valid request to show the same public result using a different internal room order.")
        for idx, e in enumerate(st.session_state.valid_replays[:5], start=1):
            with st.expander(f"Replay {idx}: {e['active_chain_name']} | public invoice still {e['public_response']['invoice_id']}", expanded=(idx == 1)):
                st.markdown(f'<div class="roomline">{roomline(e["active_chain"])}</div>', unsafe_allow_html=True)

        with st.expander("Show full verified pathway set"):
            for p in VALID_PATHWAYS:
                prefix = "ACTIVE" if valid["active_chain_name"] == p["name"] else "inactive"
                st.markdown(f"**{prefix}: {p['name']}**")
                st.markdown(f'<div class="roomline">{roomline(p["rooms"])}</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="claim">
            <b>Key claim:</b> valid access is real, but the internal path is not a fixed map.
            The public user gets the same invoice while the operator sees the room order move.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Run the valid witness demo.")

# ---------------- MISSING ----------------
with right:
    st.markdown(
        """
        <div class="story-card missing-card">
            <h3>Missing witness: live synthetic maze</h3>
            <div class="muted">
            The user is authenticated but lacks the ownership witness. The real boundary is not hidden;
            it is absent. Attacker actions generate more synthetic rooms and leave a behavioural signature.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if missing:
        c1, c2, c3 = st.columns(3)
        with c1:
            metric("Witness", "MISSING", "purple")
        with c2:
            metric("Boundary", "SEALED", "red")
        with c3:
            metric("Maze depth", str(len(missing["active_chain"])), "purple")

        public_invoice_card(missing["public_response"], "Public user view")

        st.markdown(
            """
            <div class="attack-panel">
                <h4>Live attack mode</h4>
                <div class="muted">
                Choose what the attacker tries next. Each action generates new synthetic topology.
                The real crown jewel remains unreachable.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        attack_cols = st.columns(3)
        for i, action_name in enumerate(ATTACK_ACTIONS.keys()):
            with attack_cols[i % 3]:
                if st.button(action_name, key=f"attack_{action_name}_{missing['timestamp']}", use_container_width=True):
                    make_missing_event(action_name)
                    st.rerun()

        links = missing["public_response"].get("links", {})
        if links:
            st.markdown("### Public links generated by the fake room")
            link_cols = st.columns(min(3, len(links)))
            for i, lure in enumerate(links.keys()):
                with link_cols[i % len(link_cols)]:
                    if st.button(f"Follow generated {lure}", key=f"lure_{lure}_{missing['timestamp']}", use_container_width=True):
                        # Map lure to nearest attack behaviour.
                        action_map = {
                            "download": "Download PDF",
                            "export": "Export audit trail",
                            "events": "Export audit trail",
                            "audit": "Export audit trail",
                            "approval": "Change payment status",
                            "review": "Change payment status",
                            "hash": "Download PDF",
                            "retry": "Replay old token",
                            "status": "View invoice",
                            "continue": "Try admin route",
                        }
                        make_missing_event(action_map.get(lure, "View invoice"))
                        st.rerun()

        st.markdown("### Operator view: generated topology")
        st.graphviz_chart(graphviz(missing["active_chain"]))
        st.markdown(f'<div class="roomline">{roomline(missing["active_chain"])}</div>', unsafe_allow_html=True)

        st.markdown("### Behavioural traversal signature")
        st.json(missing["signature"])

        st.markdown(
            """
            <div class="claim">
            <b>Key claim:</b> this is not just detecting bad traffic. The runtime changes what topology exists.
            Without the witness, the real boundary is not in the path; synthetic rooms absorb and profile the behaviour.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Run the missing witness demo.")


# ============================================================
# SPEAKER SCRIPT + EVIDENCE
# ============================================================

st.markdown('<div class="section-title"><h2>Speaker script</h2></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer">
    <b>Thirty-second version:</b>
    On the left, Alice has the witness for her own invoice. The app returns the real invoice, but the internal route
    is selected from a verified set of safe room orders, so the map is not stable. On the right, Alice tries Bob's
    invoice. She is authenticated, but the ownership witness is missing. The real boundary is not merely hidden;
    it is absent from her topology. Her actions generate synthetic rooms, and the operator learns the behavioural
    signature without touching the crown jewel.
    <br><br>
    <b>What to click live:</b>
    hit <b>Replay valid request</b> two or three times, then hit <b>Download PDF</b>, <b>Export audit trail</b>,
    and <b>Try admin route</b> on the missing-witness side.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Evidence log / operator audit trail"):
    for e in st.session_state.evidence_log[:25]:
        st.json(e)
