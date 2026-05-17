
# Cube Runtime MVP

This is a small Streamlit proof-of-concept for a witness-based moving topology app.

It demonstrates two separate mechanisms:

1. **Valid witness**
   - The user has the required ownership witness.
   - The real boundary is allowed.
   - The runtime chooses one active chain from multiple valid room orders.
   - The public response stays normal.
   - The operator view shows which chain was active.

2. **Missing witness**
   - The user is authenticated but lacks the ownership witness.
   - The real boundary is absent.
   - A generated synthetic maze starts.
   - Each followed link extends the generated maze.
   - The crown jewel is never touched.
   - The operator view records a behavioural traversal signature.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Try these requests

```text
alice + INV-100 = valid witness
alice + INV-200 = missing witness
bob + INV-200 = valid witness
carla + INV-300 = valid witness
```

## What to look for

For valid witness:
- `Witness = VALID`
- `Real boundary reached = YES`
- one active chain is selected
- inactive valid room orders are shown

For missing witness:
- `Witness = MISSING`
- `Real boundary reached = NO`
- generated maze is active
- public response has generated links
- following links extends the maze
- evidence log proves crown jewel was never reached
