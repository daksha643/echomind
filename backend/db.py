# In-memory storage. Memories live in RAM and vanish when the server stops.
# That's fine for a hackathon. Swap for a real database later.

_memories = {}


def make_user(user_id, name):
    """Create a user slot if it doesn't exist."""
    _memories.setdefault(user_id, [])


def save_memory(user_id, text, entities):
    """Add one memory to a user's list."""
    _memories.setdefault(user_id, [])
    _memories[user_id].append({
        "text": text,
        "entities": entities,
    })


def list_memories(user_id, count=25):
    """Return the newest memories first."""
    return list(reversed(_memories.get(user_id, [])))[:count]