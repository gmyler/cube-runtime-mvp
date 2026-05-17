
import hashlib
import json
import random
from datetime import datetime
from typing import Dict, List, Any

import streamlit as st


# ============================================================
# Cube Runtime MVP
# ------------------------------------------------------------
# Demonstrates two different mechanisms:
#
# 1. Valid witness:
#    - Real boundary is allowed.
#    - There are multiple valid room orders.
#    - One active chain is selected per request.
#    - Public user sees only normal app response.
#
# 2. Missing witness:
#    - Real boundary is absent.
#    - A generated synthetic maze starts.
#    - Each follow-up action extends the maze.
#    - Public user sees normal-looking synthetic app state.
#    - Operator view proves crown jewel was not reached.
# ============================================================


st.set_page_config(
    page_title="Cube Runtime MVP",
    page_icon="🧊",
    layout="wide",
)


# ============================================================
# Fake production data
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

USERS = ["alice", "bob", "carla"]


# ============================================================
# Valid witness pathway options
# ============================================================

VALID_PATHWAYS = [
    {
        "name": "Pathway A",
        "description": "Classic ownership-first path",
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
        "name": "Pathway B",
        "description": "Audit and cache before real boundary",
        "rooms": [
            "AuthRoom",
            "AuditRoom",
            "OwnershipWitnessRoom_v2",
            "CacheRoom",
            "InvoiceReadRoom_v2",
            "BoundaryBroker",
            "RealInvoiceBoundary",
        ],
    },
    {
        "name": "Pathway C",
        "description": "Risk and lineage enriched path",
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
        "name": "Pathway D",
        "description": "Replica read with post-boundary audit",
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


# ============================================================
# Missing witness synthetic room options
# ============================================================

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
# Session state
# ============================================================

def init_state() -> None:
    defaults = {
        "run_counter": 0,
        "latest_event": None,
        "evidence_log": [],
        "maze_state": None,
        "public_history": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ============================================================
# Helpers
# ============================================================

def stable_hash(*parts: Any, length: int = 16) -> str:
    raw = "||".join(str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:length]


def seeded_rng(*parts: Any) -> random.Random:
    seed = stable_hash(*parts, length=24)
    return random.Random(seed)


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ownership_witness(user: str, invoice_id: str) -> bool:
    invoice = REAL_INVOICE_DB.get(invoice_id)
    if not invoice:
        return False
    return invoice["owner"] == user


def choose_valid_pathway(user: str, invoice_id: str, run_counter: int) -> Dict[str, Any]:
    rng = seeded_rng("valid_pathway", user, invoice_id, run_counter)
    return rng.choice(VALID_PATHWAYS)


def make_real_invoice_response(user: str, invoice_id: str) -> Dict[str, Any]:
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


def start_generated_maze(user: str, invoice_id: str, run_counter: int) -> Dict[str, Any]:
    rng = seeded_rng("maze_start", user, invoice_id, run_counter)

    first_room = rng.choice(list(SYNTHETIC_ROOM_CATALOG.keys()))

    return {
        "maze_id": "maze_" + stable_hash(user, invoice_id, run_counter, length=10),
        "user": user,
        "invoice_id": invoice_id,
        "created_at": utc_now(),
        "rooms": ["AuthRoom", "InvoiceIntentRoom", first_room],
        "choices": [],
        "depth": 1,
        "max_depth": 12,
    }


def extend_generated_maze(maze: Dict[str, Any], choice: str) -> Dict[str, Any]:
    current_depth = maze["depth"]
    rng = seeded_rng("maze_extend", maze["maze_id"], choice, current_depth)

    room_names = list(SYNTHETIC_ROOM_CATALOG.keys())

    # Make it feel like rooms move by selecting from the catalogue each step,
    # but avoid repeating the immediately previous room where possible.
    previous = maze["rooms"][-1]
    candidates = [r for r in room_names if r != previous]
    next_room = rng.choice(candidates)

    updated = dict(maze)
    updated["rooms"] = list(maze["rooms"]) + [next_room]
    updated["choices"] = list(maze["choices"]) + [choice]
    updated["depth"] = current_depth + 1

    return updated


def generate_synthetic_response(maze: Dict[str, Any]) -> Dict[str, Any]:
    current_room = maze["rooms"][-1]
    room_meta = SYNTHETIC_ROOM_CATALOG.get(current_room, {})

    rng = seeded_rng("synthetic_response", maze["maze_id"], current_room, maze["depth"])

    statuses = [
        "processing",
        "reconciling",
        "under_review",
        "queued",
        "export_pending",
        "policy_review",
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

    lures = room_meta.get("lures", ["status", "continue", "details"])

    links = {}
    for lure in lures:
        cursor = stable_hash(maze["maze_id"], current_room, lure, maze["depth"], length=8)
        links[lure] = f"/invoice/{maze['invoice_id']}/{lure}?cursor={cursor}"

    if maze["depth"] >= maze["max_depth"]:
        links = {
            "status": f"/invoice/{maze['invoice_id']}/status?cursor=terminal"
        }

    return {
        "invoice_id": maze["invoice_id"],
        "view": room_meta.get("public_label", "generated state"),
        "customer": rng.choice(fake_customers),
        "amount": rng.randint(500, 25000),
        "status": rng.choice(statuses),
        "synthetic": True,
        "message": "Your request is being processed.",
        "links": links,
    }


def behavioural_signature(maze: Dict[str, Any]) -> Dict[str, Any]:
    choices = maze.get("choices", [])
    rooms = maze.get("rooms", [])

    choice_text = " ".join(choices).lower()
    room_text = " ".join(rooms).lower()

    preferred_lure = "status/orbit"
    for lure in ["download", "export", "audit", "payment", "approval", "hash"]:
        if lure in choice_text or lure in room_text:
            preferred_lure = lure
            break

    return {
        "risk_pattern": "missing_witness_object_probe",
        "preferred_lure": preferred_lure,
        "generated_rooms_visited": len(rooms),
        "choices_made": choices,
        "attempted_resource": maze["invoice_id"],
        "real_boundary_reached": False,
    }


def create_valid_event(user: str, invoice_id: str, run_counter: int) -> Dict[str, Any]:
    pathway = choose_valid_pathway(user, invoice_id, run_counter)
    response = make_real_invoice_response(user, invoice_id)

    inactive = [
        p for p in VALID_PATHWAYS
        if p["name"] != pathway["name"]
    ]

    return {
        "timestamp": utc_now(),
        "mode": "VALID_WITNESS_MOVING_REAL_PATHWAY",
        "user": user,
        "invoice_id": invoice_id,
        "witness_present": True,
        "real_boundary_reached": True,
        "crown_jewel": "RealInvoiceBoundary",
        "active_pathway_name": pathway["name"],
        "active_pathway_description": pathway["description"],
        "active_chain": pathway["rooms"],
        "inactive_valid_pathways": inactive,
        "synthetic_maze_active": False,
        "response": response,
        "public_user_knows_internal_room": False,
        "operator_can_inspect_chain": True,
    }


def create_missing_event(user: str, invoice_id: str, run_counter: int) -> Dict[str, Any]:
    maze = start_generated_maze(user, invoice_id, run_counter)
    st.session_state.maze_state = maze

    response = generate_synthetic_response(maze)

    return {
        "timestamp": utc_now(),
        "mode": "MISSING_WITNESS_GENERATED_MAZE",
        "user": user,
        "invoice_id": invoice_id,
        "witness_present": False,
        "real_boundary_reached": False,
        "crown_jewel": "RealInvoiceBoundary",
        "active_pathway_name": "Generated synthetic maze",
        "active_pathway_description": "No real boundary is available for this flow.",
        "active_chain": maze["rooms"],
        "inactive_valid_pathways": [],
        "synthetic_maze_active": True,
        "maze": maze,
        "behavioural_signature": behavioural_signature(maze),
        "response": response,
        "public_user_knows_internal_room": False,
        "operator_can_inspect_chain": True,
    }


def run_request(user: str, invoice_id: str) -> Dict[str, Any]:
    st.session_state.run_counter += 1
    run_counter = st.session_state.run_counter

    witness = ownership_witness(user, invoice_id)

    if witness:
        st.session_state.maze_state = None
        event = create_valid_event(user, invoice_id, run_counter)
    else:
        event = create_missing_event(user, invoice_id, run_counter)

    st.session_state.latest_event = event
    st.session_state.evidence_log.insert(0, event)
    st.session_state.public_history.insert(0, {
        "timestamp": event["timestamp"],
        "response": event["response"],
    })

    return event


def follow_generated_link(choice: str) -> Dict[str, Any]:
    maze = st.session_state.maze_state

    if not maze:
        raise RuntimeError("No generated maze is active.")

    updated_maze = extend_generated_maze(maze, choice)
    st.session_state.maze_state = updated_maze

    response = generate_synthetic_response(updated_maze)

    event = {
        "timestamp": utc_now(),
        "mode": "MISSING_WITNESS_GENERATED_MAZE_EXTENDED",
        "user": updated_maze["user"],
        "invoice_id": updated_maze["invoice_id"],
        "witness_present": False,
        "real_boundary_reached": False,
        "crown_jewel": "RealInvoiceBoundary",
        "active_pathway_name": "Extended generated synthetic maze",
        "active_pathway_description": "The next synthetic room was generated from the user's choice.",
        "active_chain": updated_maze["rooms"],
        "inactive_valid_pathways": [],
        "synthetic_maze_active": True,
        "maze": updated_maze,
        "behavioural_signature": behavioural_signature(updated_maze),
        "response": response,
        "public_user_knows_internal_room": False,
        "operator_can_inspect_chain": True,
    }

    st.session_state.latest_event = event
    st.session_state.evidence_log.insert(0, event)
    st.session_state.public_history.insert(0, {
        "timestamp": event["timestamp"],
        "response": event["response"],
    })

    return event


def graphviz_for_event(event: Dict[str, Any]) -> str:
    rooms = event.get("active_chain", [])
    witness = event.get("witness_present", False)

    lines = [
        "digraph G {",
        "rankdir=LR;",
        'graph [bgcolor="transparent"];',
        'node [shape=box, style="rounded,filled", fontname="Arial"];',
        'edge [fontname="Arial"];',
    ]

    for i, room in enumerate(rooms):
        fill = "#DCFCE7" if witness else "#F3E8FF"
        color = "#16A34A" if witness else "#7E22CE"
        font = "#111827"

        if room == "RealInvoiceBoundary":
            fill = "#FEE2E2"
            color = "#DC2626"
            label = f"{room}\\nCROWN JEWEL"
        elif room in {"BoundaryBroker"}:
            fill = "#DBEAFE"
            color = "#2563EB"
            label = room
        elif "Synthetic" in room or "Fake" in room or "Orbit" in room or "Evidence" in room or "Generated" in room:
            fill = "#F3E8FF"
            color = "#7E22CE"
            label = room
        else:
            label = room

        lines.append(
            f'"{room}_{i}" [label="{label}", fillcolor="{fill}", color="{color}", fontcolor="{font}", penwidth=2];'
        )

        if i > 0:
            lines.append(f'"{rooms[i-1]}_{i-1}" -> "{room}_{i}";')

    lines.append("}")
    return "\n".join(lines)


def reset_demo() -> None:
    st.session_state.run_counter = 0
    st.session_state.latest_event = None
    st.session_state.evidence_log = []
    st.session_state.maze_state = None
    st.session_state.public_history = []


# ============================================================
# UI
# ============================================================

st.title("Cube Runtime MVP")
st.caption(
    "Valid witness: one active real pathway is selected from many valid room orders. "
    "Missing witness: the real boundary is absent and a generated maze extends as the user follows links."
)

with st.sidebar:
    st.header("Request")

    user = st.selectbox("Authenticated user", USERS, index=0)
    invoice_id = st.text_input("Requested invoice ID", value="INV-100")

    st.markdown("### Try")
    st.code(
        "alice + INV-100 = valid witness\n"
        "alice + INV-200 = missing witness\n"
        "bob + INV-200 = valid witness\n"
        "carla + INV-300 = valid witness",
        language="text",
    )

    if st.button("Run request", type="primary", use_container_width=True):
        run_request(user, invoice_id)

    if st.button("Run same request again", use_container_width=True):
        run_request(user, invoice_id)

    st.divider()

    if st.button("Reset demo", use_container_width=True):
        reset_demo()

event = st.session_state.latest_event

if not event:
    st.info("Run a request from the sidebar.")
    st.stop()


# Top metrics
m1, m2, m3, m4 = st.columns(4)

m1.metric("Witness", "VALID" if event["witness_present"] else "MISSING")
m2.metric("Real boundary reached", "YES" if event["real_boundary_reached"] else "NO")
m3.metric("Synthetic maze", "YES" if event["synthetic_maze_active"] else "NO")
m4.metric("Public knows room?", "NO")


# Main views
public_col, operator_col = st.columns([1, 1.4], gap="large")

with public_col:
    st.subheader("Public app response")
    st.caption("This is what the outside user would see. It does not reveal the internal room or chain.")
    st.json(event["response"])

    if event.get("synthetic_maze_active"):
        links = event["response"].get("links", {})
        st.markdown("### Follow a generated link")

        if not links:
            st.warning("The generated maze reached its configured max depth.")
        else:
            link_cols = st.columns(max(1, min(3, len(links))))
            for i, choice in enumerate(links.keys()):
                with link_cols[i % len(link_cols)]:
                    if st.button(f"Follow {choice}", key=f"follow_{choice}_{event['timestamp']}"):
                        follow_generated_link(choice)
                        st.rerun()

    st.markdown("### Public response history")
    for item in st.session_state.public_history[:5]:
        with st.expander(item["timestamp"]):
            st.json(item["response"])


with operator_col:
    st.subheader("Operator/security view")
    st.caption("This view proves which internal chain was active and whether the crown jewel was touched.")

    st.markdown("### Active chain")
    st.graphviz_chart(graphviz_for_event(event))

    st.markdown("### Active chain details")
    st.json({
        "mode": event["mode"],
        "active_pathway": event["active_pathway_name"],
        "description": event["active_pathway_description"],
        "active_chain": event["active_chain"],
        "crown_jewel": event["crown_jewel"],
        "real_boundary_reached": event["real_boundary_reached"],
    })

    if event["witness_present"]:
        st.markdown("### Other valid room orders not active this run")
        st.caption("The valid flow has several safe equivalent room orders, but only one is active per request.")

        for pathway in event["inactive_valid_pathways"]:
            with st.expander(pathway["name"] + " — " + pathway["description"]):
                st.write(" → ".join(pathway["rooms"]))

    else:
        st.markdown("### Behavioural traversal signature")
        st.caption("This is not identity proof. It is a behavioural signature of the current missing-witness flow.")
        st.json(event.get("behavioural_signature", {}))

        st.markdown("### Maze state")
        st.json(event.get("maze", {}))


st.divider()

st.subheader("Evidence log")
st.caption("Every event records whether the crown jewel was reached. Missing-witness events should always show false.")

for item in st.session_state.evidence_log[:10]:
    title = (
        f"{item['timestamp']} | {item['mode']} | "
        f"{item['user']} → {item['invoice_id']} | "
        f"boundary_reached={item['real_boundary_reached']}"
    )
    with st.expander(title):
        st.json(item)
