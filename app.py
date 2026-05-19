
import hashlib
import json
import random
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

st.set_page_config(page_title='Pathway DB2 Mega Demo', page_icon='DB2', layout='wide')

# ============================================================
# PATHWAY DB2 MEGA DEMO
# No-source-change retrofit concept:
# User -> Edge Pathway Gateway -> Existing App -> DB2 Boundary Proxy -> DB2
# ============================================================

st.markdown('''
<style>
.block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1700px; }
.hero { padding: 2.2rem 2.5rem; border-radius: 30px; background: linear-gradient(135deg,#020617 0%,#172554 50%,#581c87 100%); color: white; margin-bottom: 1rem; box-shadow: 0 24px 60px rgba(15,23,42,.28); }
.hero h1 { margin: 0; font-size: 3rem; line-height: 1; letter-spacing: -0.05em; }
.hero p { margin: 1rem 0 0 0; color: rgba(255,255,255,.84); font-size: 1.1rem; line-height: 1.55; max-width: 1250px; }
.tag { display: inline-block; padding: .34rem .72rem; border-radius: 999px; background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.2); margin-right: .45rem; margin-bottom: .55rem; font-size: .82rem; font-weight: 850; }
.card { padding: 1.1rem 1.15rem; border-radius: 24px; background: white; border: 1px solid #e2e8f0; box-shadow: 0 13px 28px rgba(15,23,42,.08); margin-bottom: 1rem; }
.card h3 { margin: 0 0 .5rem 0; }
.green { border-top: 7px solid #22c55e; }
.purple { border-top: 7px solid #a855f7; }
.blue { border-top: 7px solid #3b82f6; }
.red { border-top: 7px solid #ef4444; }
.amber { border-top: 7px solid #f59e0b; }
.muted { color: #64748b; font-size: .96rem; line-height: 1.5; }
.callout { padding: 1rem 1.15rem; border-radius: 22px; background: #f8fafc; border: 1px solid #e2e8f0; color: #334155; line-height: 1.55; margin: .8rem 0 1rem 0; }
.metric { padding: .95rem 1rem; border-radius: 20px; text-align: center; min-height: 105px; display:flex; flex-direction:column; justify-content:center; border: 1px solid #e2e8f0; margin-bottom: .8rem; }
.metric-label { text-transform: uppercase; letter-spacing: .08em; font-weight: 850; color: #64748b; font-size: .74rem; }
.metric-value { margin-top: .3rem; font-size: 1.22rem; font-weight: 950; letter-spacing: -.03em; }
.metric-green { background:#dcfce7; border-color:#86efac; color:#14532d; }
.metric-purple { background:#f3e8ff; border-color:#d8b4fe; color:#581c87; }
.metric-red { background:#fee2e2; border-color:#fca5a5; color:#7f1d1d; }
.metric-blue { background:#dbeafe; border-color:#93c5fd; color:#1e3a8a; }
.metric-slate { background:#f1f5f9; border-color:#cbd5e1; color:#334155; }
.metric-amber { background:#fef3c7; border-color:#fcd34d; color:#78350f; }
.roomline { padding: 1rem; border-radius: 20px; background: #f8fafc; border: 1px solid #e2e8f0; margin: .8rem 0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; line-height: 2.35; overflow-wrap: anywhere; }
.room { display:inline-block; padding:.34rem .58rem; border-radius:999px; border:1px solid #93c5fd; background:#dbeafe; color:#1e3a8a; font-weight:850; font-size:.78rem; margin:.12rem; }
.room-safe { background:#dcfce7; border-color:#86efac; color:#14532d; }
.room-fake { background:#f3e8ff; border-color:#d8b4fe; color:#581c87; }
.room-boundary { background:#dbeafe; border-color:#93c5fd; color:#1e3a8a; }
.room-db { background:#fee2e2; border-color:#fca5a5; color:#7f1d1d; }
.room-edge { background:#ffedd5; border-color:#fdba74; color:#7c2d12; }
.room-existing { background:#f1f5f9; border-color:#cbd5e1; color:#334155; }
.screen { padding: 1.1rem 1.15rem; border-radius: 24px; background:#0f172a; color:white; box-shadow:0 18px 38px rgba(15,23,42,.22); margin-bottom:1rem; }
.screen-row { display:flex; justify-content:space-between; border-bottom:1px solid rgba(148,163,184,.28); padding:.65rem 0; gap:1rem; }
.screen-label { color:#94a3b8; font-weight:760; }
.screen-value { font-weight:920; text-align:right; }
.badge { padding:.35rem .7rem; border-radius:999px; font-weight:900; font-size:.82rem; display:inline-block; }
.badge-green { background:#22c55e; color:white; }
.badge-purple { background:#a855f7; color:white; }
.badge-red { background:#ef4444; color:white; }
.proof { padding:.95rem 1rem; border-radius:18px; background:#0f172a; color:#dbeafe; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size:.82rem; line-height:1.6; overflow-wrap:anywhere; margin:.8rem 0; }
.stButton > button { border-radius:16px !important; font-weight:850 !important; min-height:3rem; }
.primary-button button { min-height:4.2rem !important; font-size:1rem !important; }
</style>
''', unsafe_allow_html=True)

DB2_INITIAL = {
    'PAY-100': {'owner': 'alice', 'account': 'ACME-01', 'status': 'pending', 'amount': 1200, 'last_write': 'initial'},
    'PAY-200': {'owner': 'bob', 'account': 'BLACKMESA-01', 'status': 'pending', 'amount': 9800, 'last_write': 'initial'},
    'PAY-300': {'owner': 'carol', 'account': 'ORCHID-01', 'status': 'held', 'amount': 4500, 'last_write': 'initial'},
}

VALID_ROOMS = [
    'AuthContextRoom', 'ActionScopeRoom', 'SQLShapeRoom', 'TableScopeRoom',
    'RowWitnessRoom', 'PayloadSchemaRoom', 'BusinessRuleRoom', 'IdempotencyRoom',
    'RiskPostureRoom', 'AuditLineageRoom',
]
ROOM_CONSTRAINTS = [
    ('AuthContextRoom', 'ActionScopeRoom'),
    ('AuthContextRoom', 'RowWitnessRoom'),
    ('ActionScopeRoom', 'TableScopeRoom'),
    ('SQLShapeRoom', 'BusinessRuleRoom'),
    ('PayloadSchemaRoom', 'BusinessRuleRoom'),
    ('RowWitnessRoom', 'BusinessRuleRoom'),
    ('BusinessRuleRoom', 'IdempotencyRoom'),
    ('IdempotencyRoom', 'DB2WriteBroker'),
    ('AuditLineageRoom', 'DB2WriteBroker'),
    ('TableScopeRoom', 'DB2WriteBroker'),
]
FAKE_ROOMS = [
    'SyntheticDb2Console', 'FakeCommitQueue', 'GeneratedAuditTrail', 'ShadowExportRoom',
    'PolicyEchoRoom', 'RollbackPreviewRoom', 'StatementHashRoom', 'PhantomCursorRoom',
    'ApprovalPendingRoom', 'SyntheticLockWaitRoom', 'ArchiveVersionRoom', 'DiagnosticTraceRoom',
]
ATTACK_ACTIONS = {
    'Submit normal payment update': 'normal_update_probe',
    'Replay stolen witness': 'stolen_witness_replay',
    'Try direct DB2 write': 'direct_db2_probe',
    'Export audit trail': 'audit_exfiltration_probe',
    'Change Bob payment': 'row_ownership_bypass_probe',
    'Force admin override': 'privilege_probe',
    'Retry same write': 'replay_probe',
    'Probe rollback logs': 'diagnostic_exfiltration_probe',
}

def init():
    defaults = {
        'db2': {k: dict(v) for k, v in DB2_INITIAL.items()},
        'run_id': 0,
        'last_valid': None,
        'last_missing': None,
        'last_attack': None,
        'valid_runs': [],
        'synthetic_maze': None,
        'db2_write_log': [],
        'gateway_log': [],
        'proxy_log': [],
        'latency_log': [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

def now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

def stable_hash(*parts: Any, length: int = 16) -> str:
    raw = '||'.join(str(p) for p in parts)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:length]

def rng_for(*parts: Any) -> random.Random:
    return random.Random(stable_hash(*parts, length=24))

def reset():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init()

def topo_sort_random(rooms: List[str], constraints: List[Tuple[str, str]], seed: str) -> List[str]:
    rng = rng_for('topo', seed)
    nodes = [n for n in rooms if n != 'DB2WriteBroker']
    incoming = {n: set() for n in nodes}
    outgoing = {n: set() for n in nodes}
    for a, b in constraints:
        if a in incoming and b in incoming:
            outgoing[a].add(b)
            incoming[b].add(a)
    available = [n for n in nodes if not incoming[n]]
    order = []
    while available:
        rng.shuffle(available)
        n = available.pop(0)
        order.append(n)
        for m in list(outgoing[n]):
            incoming[m].discard(n)
            if not incoming[m] and m not in order and m not in available:
                available.append(m)
    for n in nodes:
        if n not in order:
            order.append(n)
    return order + ['DB2WriteBroker']

def required_rooms_present(path: List[str]) -> bool:
    required = {'AuthContextRoom','ActionScopeRoom','SQLShapeRoom','TableScopeRoom','RowWitnessRoom','PayloadSchemaRoom','BusinessRuleRoom','IdempotencyRoom','AuditLineageRoom','DB2WriteBroker'}
    return required.issubset(set(path))

def constraints_satisfied(path: List[str]) -> bool:
    pos = {room: i for i, room in enumerate(path)}
    for a, b in ROOM_CONSTRAINTS:
        if a in pos and b in pos and pos[a] > pos[b]:
            return False
    return True

def generate_route_proof(ctx: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    leases = []
    prev = 'EDGE'
    for i, room in enumerate(path):
        leases.append({
            'from': prev,
            'to': room,
            'lease': stable_hash('lease', ctx['user'], ctx['resource_id'], ctx['action'], prev, room, ctx['request_nonce'], i, length=20),
            'one_step_only': True,
        })
        prev = room
    return {
        'proof': stable_hash('route_proof', ctx['user'], ctx['resource_id'], ctx['action'], ctx['request_nonce'], '|'.join(path), length=28),
        'request_nonce': ctx['request_nonce'],
        'path_hash': stable_hash('|'.join(path), length=20),
        'leases': leases,
        'fresh': True,
        'replay_seen': False,
    }

def room_class(r: str) -> str:
    if r == 'EdgePathwayGateway': return 'room-edge'
    if r == 'ExistingApp': return 'room-existing'
    if r == 'DB2WriteBroker': return 'room-boundary'
    if r == 'DB2': return 'room-db'
    if any(x in r for x in ['Synthetic','Fake','Generated','Shadow','Phantom','Echo','Preview','Trace','Archive']): return 'room-fake'
    return 'room-safe'

def roomline(rooms: List[str]) -> str:
    out = []
    for i, r in enumerate(rooms):
        out.append(f'<span class="room {room_class(r)}">{r}</span>')
        if i < len(rooms) - 1:
            out.append(' -> ')
    return ''.join(out)

def graphviz(rooms: List[str], title: str = '') -> str:
    lines = ['digraph G {','rankdir=LR;','graph [bgcolor="transparent"];','node [shape=box, style="rounded,filled", fontname="Arial"];','edge [fontname="Arial", color="#64748b"];']
    if title:
        lines.append(f'label="{title}"; labelloc="t"; fontsize=18; fontname="Arial";')
    for i, r in enumerate(rooms):
        fill, color, label = '#DCFCE7', '#16A34A', r
        if r == 'EdgePathwayGateway': fill, color = '#FFEDD5', '#EA580C'
        elif r == 'ExistingApp': fill, color = '#F1F5F9', '#64748B'
        elif r == 'DB2WriteBroker': fill, color, label = '#DBEAFE', '#2563EB', 'DB2WriteBroker\\nexternal proxy'
        elif r == 'DB2': fill, color, label = '#FEE2E2', '#DC2626', 'DB2\\nwrite target'
        elif any(x in r for x in ['Synthetic','Fake','Generated','Shadow','Phantom','Echo','Preview','Trace','Archive']): fill, color = '#F3E8FF', '#7E22CE'
        lines.append(f'"{r}_{i}" [label="{label}", fillcolor="{fill}", color="{color}", penwidth=2];')
        if i > 0:
            lines.append(f'"{rooms[i-1]}_{i-1}" -> "{r}_{i}";')
    lines.append('}')
    return '\n'.join(lines)

def metric(label: str, value: str, kind: str):
    st.markdown(f'<div class="metric metric-{kind}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

def proof_box(title: str, payload: Dict[str, Any]):
    st.markdown(f'**{title}**')
    st.markdown(f'<div class="proof">{json.dumps(payload, indent=2)}</div>', unsafe_allow_html=True)

def sql_box(sql: str, params: List[Any]):
    st.markdown(f'''
    <div class="screen">
      <div style="font-size:.82rem;color:#94a3b8;font-weight:850;text-transform:uppercase;letter-spacing:.08em;">Existing app still emits same DB2 write</div>
      <div style="font-size:1.15rem;font-weight:950;margin-top:.45rem;">{sql}</div>
      <div style="margin-top:.75rem;color:#dbeafe;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;">params = {params}</div>
    </div>
    ''', unsafe_allow_html=True)

def simulate_latency(valid: bool) -> int:
    rng = rng_for('latency', st.session_state.run_id, datetime.utcnow().isoformat())
    return int(rng.uniform(42, 96)) if valid else int(rng.uniform(35, 105))

def edge_gateway(user: str, payment_id: str, action: str, scenario: str) -> Dict[str, Any]:
    st.session_state.run_id += 1
    owns_row = st.session_state.db2.get(payment_id, {}).get('owner') == user
    valid_witness = owns_row and scenario == 'valid'
    ctx = {
        'timestamp': now(),
        'scenario': scenario,
        'user': user,
        'resource_id': payment_id,
        'action': action,
        'has_auth': True,
        'owns_row': owns_row,
        'witness_valid': valid_witness,
        'stolen_witness_present': scenario == 'stolen_witness',
        'direct_db2_attempt': scenario == 'direct_db2',
        'request_nonce': stable_hash('nonce', st.session_state.run_id, user, payment_id, action, length=14),
        'gateway_decision': 'forward_to_existing_app' if valid_witness else 'synthetic_topology',
    }
    st.session_state.gateway_log.insert(0, ctx)
    return ctx

def existing_app_attempt_db2_write(ctx: Dict[str, Any], new_status: str) -> Dict[str, Any]:
    return {
        'app': 'ExistingApp',
        'source_code_changed': False,
        'sql': 'UPDATE PAYMENTS SET STATUS = ? WHERE PAYMENT_ID = ?',
        'params': [new_status, ctx['resource_id']],
        'db2_connection_target': 'DB2BoundaryProxy',
    }

def db2_boundary_proxy(ctx: Dict[str, Any], write_attempt: Dict[str, Any]) -> Dict[str, Any]:
    seed = stable_hash('path', ctx['request_nonce'], ctx['user'], ctx['resource_id'], length=20)
    room_path = topo_sort_random(VALID_ROOMS, ROOM_CONSTRAINTS, seed)
    full_path = ['EdgePathwayGateway', 'ExistingApp'] + room_path + ['DB2']
    proof = generate_route_proof(ctx, room_path)
    valid = ctx['witness_valid'] and required_rooms_present(room_path) and constraints_satisfied(room_path) and not ctx.get('stolen_witness_present') and not ctx.get('direct_db2_attempt')
    latency_ms = simulate_latency(valid=True)
    decision = {
        'timestamp': now(),
        'proxy': 'DB2BoundaryProxy',
        'decision': 'ALLOW_DB2_WRITE' if valid else 'DENY_OR_DIVERT',
        'reason': 'valid witness + live moving route proof' if valid else 'missing/invalid witness or route proof',
        'room_path': room_path,
        'full_path': full_path,
        'route_proof': proof,
        'constraints_satisfied': constraints_satisfied(room_path),
        'required_rooms_present': required_rooms_present(room_path),
        'latency_ms': latency_ms,
        'write_attempt': write_attempt,
    }
    if valid:
        payment_id = ctx['resource_id']
        new_status = write_attempt['params'][0]
        if payment_id in st.session_state.db2:
            st.session_state.db2[payment_id]['status'] = new_status
            st.session_state.db2[payment_id]['last_write'] = 'proxy:' + proof['proof'][:10]
        st.session_state.db2_write_log.insert(0, {'timestamp': now(), 'payment_id': payment_id, 'new_status': new_status, 'proof': proof['proof'], 'path_hash': proof['path_hash'], 'room_count': len(room_path), 'latency_ms': latency_ms, 'source_code_changed': False})
    st.session_state.proxy_log.insert(0, decision)
    st.session_state.latency_log.insert(0, {'timestamp': now(), 'scenario': ctx['scenario'], 'stage': 'valid_proxy_path' if valid else 'proxy_denied_or_diverted', 'latency_ms': latency_ms})
    return decision

def synthetic_maze(ctx: Dict[str, Any], attack_action: str = 'Submit normal payment update') -> Dict[str, Any]:
    if st.session_state.synthetic_maze is None or ctx['scenario'] in {'missing','direct_db2','stolen_witness'}:
        st.session_state.synthetic_maze = {'maze_id': 'maze_' + stable_hash('maze', st.session_state.run_id, ctx['user'], ctx['resource_id'], length=10), 'rooms': ['EdgePathwayGateway', 'SyntheticDb2Console'], 'actions': [], 'depth': 0, 'intent_counts': {}}
    maze = st.session_state.synthetic_maze
    rng = rng_for('maze', maze['maze_id'], attack_action, maze['depth'], len(maze['rooms']))
    intent = ATTACK_ACTIONS.get(attack_action, 'unknown_probe')
    candidates = list(FAKE_ROOMS)
    rng.shuffle(candidates)
    new_rooms = candidates[:2] if attack_action in {'Export audit trail','Probe rollback logs','Try direct DB2 write'} else candidates[:1]
    for r in new_rooms:
        if not maze['rooms'] or maze['rooms'][-1] != r:
            maze['rooms'].append(r)
    maze['actions'].append(attack_action)
    maze['depth'] += 1
    maze['intent_counts'][intent] = maze['intent_counts'].get(intent, 0) + 1
    dominant = max(maze['intent_counts'].items(), key=lambda kv: kv[1])[0]
    latency_ms = simulate_latency(valid=False)
    st.session_state.latency_log.insert(0, {'timestamp': now(), 'scenario': ctx['scenario'], 'stage': 'synthetic_topology', 'latency_ms': latency_ms})
    event = {
        'timestamp': now(),
        'scenario': ctx['scenario'],
        'action': attack_action,
        'decision': 'SYNTHETIC_TOPOLOGY',
        'real_app_forwarded': False,
        'db2_touched': False,
        'db2_write_allowed': False,
        'rooms': list(maze['rooms']),
        'maze': dict(maze),
        'synthetic_response': {'payment_id': ctx['resource_id'], 'status': rng.choice(['queued','commit pending','lock wait','audit sync','rollback preview','policy review']), 'statement_hash': stable_hash('stmt', maze['maze_id'], maze['depth'], length=12), 'cursor': stable_hash('cursor', attack_action, maze['depth'], length=10), 'links': {'audit': '/db2/audit/' + stable_hash(maze['maze_id'], 'audit', maze['depth'], length=8), 'retry': '/db2/retry/' + stable_hash(maze['maze_id'], 'retry', maze['depth'], length=8), 'rollback': '/db2/rollback/' + stable_hash(maze['maze_id'], 'rollback', maze['depth'], length=8)}},
        'behaviour_signature': {'dominant_intent': dominant, 'actions_seen': list(maze['actions']), 'generated_room_count': len(maze['rooms']), 'real_db2_touched': False, 'live_route_proof_seen': False},
        'latency_ms': latency_ms,
    }
    st.session_state.last_missing = event
    st.session_state.last_attack = event
    return event

def run_valid_db2_write(new_status='approved'):
    ctx = edge_gateway('alice', 'PAY-100', 'payment.status.write', 'valid')
    write_attempt = existing_app_attempt_db2_write(ctx, new_status)
    proxy_result = db2_boundary_proxy(ctx, write_attempt)
    event = {'timestamp': now(), 'scenario': 'valid', 'ctx': ctx, 'write_attempt': write_attempt, 'proxy_result': proxy_result, 'real_app_forwarded': True, 'db2_touched': proxy_result['decision'] == 'ALLOW_DB2_WRITE', 'db2_write_allowed': proxy_result['decision'] == 'ALLOW_DB2_WRITE'}
    st.session_state.last_valid = event
    st.session_state.valid_runs.insert(0, event)
    st.session_state.valid_runs = st.session_state.valid_runs[:7]
    return event

def run_missing_witness(action='Submit normal payment update'):
    ctx = edge_gateway('alice', 'PAY-200', 'payment.status.write', 'missing')
    return synthetic_maze(ctx, action)

def run_stolen_witness():
    ctx = edge_gateway('alice', 'PAY-200', 'payment.status.write', 'stolen_witness')
    return synthetic_maze(ctx, 'Replay stolen witness')

def run_direct_db2_attempt():
    ctx = edge_gateway('unknown', 'PAY-200', 'raw.db2.update', 'direct_db2')
    return synthetic_maze(ctx, 'Try direct DB2 write')

# Header
st.markdown('''
<div class="hero">
  <span class="tag">No source-code change story</span>
  <span class="tag">Existing app stays intact</span>
  <span class="tag">DB2 Boundary Proxy</span>
  <span class="tag">Moving verification rooms</span>
  <span class="tag">Synthetic topology</span>
  <h1>Pathway DB2 Mega Demo</h1>
  <p>A practical retrofit demonstration: keep the existing DB2-backed app unchanged, insert an edge gateway and a DB2 boundary proxy, then make auth-to-DB2-write pass through a moving room order. If the witness or live route proof is missing, the request enters generated topology and DB2 is not touched.</p>
</div>
''', unsafe_allow_html=True)

st.markdown('''<div class="callout"><strong>Core demo claim:</strong> the existing app still emits the same DB2 write, but DB2 only receives it after an external proxy runs a fresh moving room chain and verifies the live route proof. Missing-witness traffic never reaches the real app write path.</div>''', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns([1.15, 1.15, 1.15, 1.15, .7])
with c1:
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    if st.button('Run valid DB2 write\nAlice -> PAY-100', use_container_width=True): run_valid_db2_write('approved')
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    if st.button('Replay same valid write\nnew room order', use_container_width=True): run_valid_db2_write('approved')
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    if st.button('Run missing witness\nAlice -> PAY-200', use_container_width=True): run_missing_witness('Submit normal payment update')
    st.markdown('</div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    if st.button('Run full mega story', use_container_width=True):
        run_valid_db2_write('approved'); run_missing_witness('Submit normal payment update'); run_stolen_witness()
    st.markdown('</div>', unsafe_allow_html=True)
with c5:
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    if st.button('Reset', use_container_width=True): reset(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.last_valid and not st.session_state.last_missing:
    st.info('Click Run full mega story to populate the whole demonstration.')
    st.stop()

tab_live, tab_arch, tab_proxy, tab_attack, tab_logs, tab_script = st.tabs(['Live demo','Architecture','DB2 proxy proof','Attack / maze mode','Logs & latency','Speaker script'])

with tab_live:
    st.markdown('## The two paths')
    left, right = st.columns(2, gap='large')
    with left:
        st.markdown('<div class="card green"><h3>Valid witness: existing app write allowed</h3><div class="muted">Alice owns PAY-100. The edge gateway forwards to the existing app. The app emits its normal DB2 write. The DB2 proxy runs a moving room order, verifies proof, then allows DB2.</div></div>', unsafe_allow_html=True)
        valid = st.session_state.last_valid
        if valid:
            proxy = valid['proxy_result']
            cols = st.columns(4)
            with cols[0]: metric('Source code','unchanged','slate')
            with cols[1]: metric('Gateway','forwarded','green')
            with cols[2]: metric('DB2 write','allowed','green')
            with cols[3]: metric('Latency', f"{proxy['latency_ms']}ms", 'blue')
            sql_box(valid['write_attempt']['sql'], valid['write_attempt']['params'])
            st.graphviz_chart(graphviz(proxy['full_path'], 'Valid flow: moving rooms before DB2 write'))
            st.markdown(f'<div class="roomline">{roomline(proxy["full_path"])}</div>', unsafe_allow_html=True)
            st.markdown('### Same write, different room orders')
            for i, event in enumerate(st.session_state.valid_runs[:5], start=1):
                proxy_i = event['proxy_result']
                with st.expander(f"Valid replay {i}: path_hash={proxy_i['route_proof']['path_hash']} | latency={proxy_i['latency_ms']}ms", expanded=(i==1)):
                    st.markdown(f'<div class="roomline">{roomline(proxy_i["full_path"])}</div>', unsafe_allow_html=True)
                    proof_box('Route proof', proxy_i['route_proof'])
    with right:
        st.markdown('<div class="card purple"><h3>Missing witness: generated topology</h3><div class="muted">Alice is authenticated but does not own PAY-200. The gateway does not forward to the app write path. Instead, it generates plausible DB2-like operational rooms. DB2 is not touched.</div></div>', unsafe_allow_html=True)
        missing = st.session_state.last_missing
        if missing:
            cols = st.columns(4)
            with cols[0]: metric('Witness','missing','purple')
            with cols[1]: metric('Real app','not forwarded','red')
            with cols[2]: metric('DB2 touched','false','red')
            with cols[3]: metric('Maze depth', str(len(missing['rooms'])), 'purple')
            sr = missing['synthetic_response']
            st.markdown(f'''<div class="screen"><div style="display:flex;justify-content:space-between;gap:1rem;align-items:center;"><div><div style="font-size:.82rem;color:#94a3b8;font-weight:850;text-transform:uppercase;letter-spacing:.08em;">Synthetic DB2 response</div><div style="font-size:1.35rem;font-weight:950;margin-top:.15rem;">Payment operation surface</div></div><span class="badge badge-purple">synthetic topology</span></div><div style="margin-top:1rem;"><div class="screen-row"><span class="screen-label">Payment</span><span class="screen-value">{sr['payment_id']}</span></div><div class="screen-row"><span class="screen-label">Status</span><span class="screen-value">{sr['status']}</span></div><div class="screen-row"><span class="screen-label">Statement hash</span><span class="screen-value">{sr['statement_hash']}</span></div><div class="screen-row"><span class="screen-label">DB2 touched</span><span class="screen-value">false</span></div></div></div>''', unsafe_allow_html=True)
            st.graphviz_chart(graphviz(missing['rooms'], 'Missing witness: generated operational topology'))
            st.markdown(f'<div class="roomline">{roomline(missing["rooms"])}</div>', unsafe_allow_html=True)
            st.markdown('### Behaviour signature')
            st.json(missing['behaviour_signature'])

with tab_arch:
    st.markdown('## No-source-change retrofit architecture')
    st.graphviz_chart('''
    digraph G {
      rankdir=LR; graph [bgcolor="transparent"]; node [shape=box, style="rounded,filled", fontname="Arial"]; edge [fontname="Arial", color="#64748b"];
      User [fillcolor="#FFEDD5", color="#EA580C", penwidth=2];
      Edge [label="Edge Pathway Gateway\\nvalid witness -> forward\\nmissing witness -> synthetic topology", fillcolor="#FFEDD5", color="#EA580C", penwidth=2];
      App [label="Existing App\\nsource code unchanged", fillcolor="#F1F5F9", color="#64748B", penwidth=2];
      Proxy [label="DB2 Boundary Proxy\\nmoving rooms + route proof", fillcolor="#DBEAFE", color="#2563EB", penwidth=2];
      DB2 [label="DB2\\nprotected write target", fillcolor="#FEE2E2", color="#DC2626", penwidth=2];
      Maze [label="Generated operational topology\\nno app write\\nno DB2 touch", fillcolor="#F3E8FF", color="#7E22CE", penwidth=2];
      User -> Edge; Edge -> App [label="valid witness"]; App -> Proxy [label="normal DB2 write now routed here"]; Proxy -> DB2 [label="allow only after proof"]; Edge -> Maze [label="missing witness"];
    }
    ''')
    a,b,c = st.columns(3, gap='large')
    with a: st.markdown('<div class="card blue"><h3>1. Edge Pathway Gateway</h3><div class="muted">Sits before the existing app. Valid witness traffic is forwarded. Missing-witness traffic never reaches the real app write path.</div></div>', unsafe_allow_html=True)
    with b: st.markdown('<div class="card green"><h3>2. Existing app unchanged</h3><div class="muted">The app still attempts the same DB2 write. Deployment routes DB2 connection through the boundary proxy.</div></div>', unsafe_allow_html=True)
    with c: st.markdown('<div class="card red"><h3>3. DB2 Boundary Proxy</h3><div class="muted">External proxy runs a fresh moving room order, checks proof, validates write shape, then forwards DB2 write.</div></div>', unsafe_allow_html=True)
    st.markdown('## What changes in production?')
    checklist = pd.DataFrame([
        {'Change': 'Application source code', 'Required?': 'No', 'Reason': 'Existing app can keep emitting same DB2 write.'},
        {'Change': 'DB2 connection routing', 'Required?': 'Yes', 'Reason': 'App DB2 connection must point at DB2 Boundary Proxy.'},
        {'Change': 'Network rule blocking direct DB2', 'Required?': 'Yes', 'Reason': 'Otherwise old paths can bypass the proxy.'},
        {'Change': 'DB2 credentials split', 'Required?': 'Strongly recommended', 'Reason': 'Proxy should be the only writer for protected operations.'},
        {'Change': 'Pathfinder mapping', 'Required?': 'Recommended', 'Reason': 'Find current auth-to-DB2-write paths and bypass candidates.'},
        {'Change': 'Synthetic topology', 'Required?': 'For missing-witness story', 'Reason': 'Preserves safety while avoiding obvious hard-deny.'},
    ])
    st.dataframe(checklist, use_container_width=True, hide_index=True)

with tab_proxy:
    st.markdown('## DB2 Boundary Proxy proof')
    valid = st.session_state.last_valid
    if not valid:
        st.warning('Run a valid DB2 write first.')
    else:
        proxy = valid['proxy_result']
        p1,p2 = st.columns([1.1,.9], gap='large')
        with p1:
            st.markdown('### Moving room order')
            st.markdown(f'<div class="roomline">{roomline(proxy["room_path"])}</div>', unsafe_allow_html=True)
            checks = pd.DataFrame([
                {'Check':'Valid witness','Result':str(valid['ctx']['witness_valid']),'Meaning':'Alice owns PAY-100'},
                {'Check':'Required rooms present','Result':str(proxy['required_rooms_present']),'Meaning':'All policy rooms ran'},
                {'Check':'Constraints satisfied','Result':str(proxy['constraints_satisfied']),'Meaning':'Random order is still valid'},
                {'Check':'Fresh route proof','Result':str(proxy['route_proof']['fresh']),'Meaning':'Not stale'},
                {'Check':'Replay seen','Result':str(proxy['route_proof']['replay_seen']),'Meaning':'False means not replayed'},
                {'Check':'Source code changed','Result':'False','Meaning':'Retrofit uses routing/proxy layer'},
            ])
            st.dataframe(checks, use_container_width=True, hide_index=True)
        with p2:
            proof_box('Route proof object', proxy['route_proof'])
            proof_box('Proxy decision', {'decision':proxy['decision'], 'reason':proxy['reason'], 'latency_ms':proxy['latency_ms'], 'path_hash':proxy['route_proof']['path_hash']})
        st.markdown('### Current DB2-like table')
        db_df = pd.DataFrame([{'payment_id':k, **v} for k,v in st.session_state.db2.items()])
        st.dataframe(db_df, use_container_width=True, hide_index=True)

with tab_attack:
    st.markdown('## Attack / synthetic topology mode')
    st.markdown('<div class="callout"><strong>Demo point:</strong> stolen witness alone is not enough. Direct DB2 attempt is not enough. The boundary proxy requires the live moving route proof. If the valid pathway is absent, the system generates operational topology instead of touching DB2.</div>', unsafe_allow_html=True)
    row1 = st.columns(4)
    actions1 = [('Replay stolen witness', run_stolen_witness), ('Try direct DB2 write', run_direct_db2_attempt), ('Export audit trail', lambda: run_missing_witness('Export audit trail')), ('Force admin override', lambda: run_missing_witness('Force admin override'))]
    for col, (label, fn) in zip(row1, actions1):
        with col:
            if st.button(label, use_container_width=True): fn(); st.rerun()
    row2 = st.columns(4)
    actions2 = [('Change Bob payment', lambda: run_missing_witness('Change Bob payment')), ('Retry same write', lambda: run_missing_witness('Retry same write')), ('Probe rollback logs', lambda: run_missing_witness('Probe rollback logs')), ('Submit normal update', lambda: run_missing_witness('Submit normal payment update'))]
    for col, (label, fn) in zip(row2, actions2):
        with col:
            if st.button(label, use_container_width=True): fn(); st.rerun()
    attack = st.session_state.last_attack or st.session_state.last_missing
    if attack:
        l,r = st.columns([1.2,.8], gap='large')
        with l:
            st.markdown('### Generated path')
            st.graphviz_chart(graphviz(attack['rooms'], 'Synthetic topology grows while DB2 remains untouched'))
            st.markdown(f'<div class="roomline">{roomline(attack["rooms"])}</div>', unsafe_allow_html=True)
        with r:
            cc = st.columns(2)
            with cc[0]: metric('DB2 touched','false','red')
            with cc[1]: metric('Live proof','absent','purple')
            proof_box('Synthetic response', attack['synthetic_response'])
            proof_box('Behaviour signature', attack['behaviour_signature'])

with tab_logs:
    st.markdown('## Logs and latency')
    l1,l2,l3 = st.columns(3)
    with l1: metric('Gateway events', str(len(st.session_state.gateway_log)), 'blue')
    with l2: metric('Proxy events', str(len(st.session_state.proxy_log)), 'blue')
    with l3: metric('DB2 writes allowed', str(len(st.session_state.db2_write_log)), 'green')
    if st.session_state.latency_log:
        lat_df = pd.DataFrame(st.session_state.latency_log)
        st.markdown('### Latency log')
        st.dataframe(lat_df, use_container_width=True, hide_index=True)
        chart_df = lat_df.iloc[::-1].copy(); chart_df['event'] = range(1, len(chart_df)+1)
        st.line_chart(chart_df, x='event', y='latency_ms')
    with st.expander('Gateway log'):
        st.json(st.session_state.gateway_log[:20])
    with st.expander('Proxy log'):
        st.json(st.session_state.proxy_log[:20])
    with st.expander('DB2 write log', expanded=True):
        st.json(st.session_state.db2_write_log[:20])

with tab_script:
    st.markdown('## Conference speaker script')
    st.markdown('<div class="callout"><strong>Thirty-second version:</strong><br>This is a no-source-change retrofit for an existing DB2-backed application. The app stays as it is. We place an edge gateway before it and a DB2 boundary proxy after it. Valid witness requests are forwarded to the existing app, and the app emits its normal DB2 write. But DB2 only sees the write after the proxy runs a fresh moving room order and verifies the live route proof. Missing-witness requests never reach the real app write path. They enter generated operational topology and DB2 is not touched.</div>', unsafe_allow_html=True)
    st.markdown('### Click sequence')
    st.code('''1. Click Run full mega story.
2. Open Architecture: no source code changes, only gateway/proxy routing.
3. Return to Live demo.
4. Click Replay same valid write two or three times.
   - Same DB2 write.
   - Different room order / route proof.
5. Open Attack / maze mode.
6. Click Replay stolen witness and Try direct DB2 write.
   - DB2 touched = false.
   - Live route proof = absent.
   - Generated topology grows.
7. Finish with:
   The pathway is not a static map. For valid traffic, the route is generated and proved.
   Without the witness/live route proof, the DB2 write path does not exist for that flow.''')
    st.markdown('### Strong positioning')
    st.code('''This is not hiding DB2 behind obscurity.

The lock is the witness plus live route proof.
The moving path is execution-integrity control.
The synthetic topology is missing-witness containment.

The existing app can remain unchanged.
The protected DB2 write becomes reachable only through the external boundary proxy.''')
    st.markdown('### Honest limitation')
    st.code('''To enforce this in production, you need routing/security control:

- app DB2 connection points to the proxy
- direct app-to-DB2 writes are blocked
- protected DB2 writes are only accepted from the proxy
- ideally, DB2 credentials are split by function

Without that, the system can observe but not enforce.''')
