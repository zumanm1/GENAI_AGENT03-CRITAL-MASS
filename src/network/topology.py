from typing import Dict

MOCK_TOPO = {
    "elements": {
        "nodes": [
            {"data": {"id": "R15", "label": "R15 (PE)"}},
            {"data": {"id": "R16", "label": "R16 (PE)"}},
            {"data": {"id": "R17", "label": "R17 (P)"}},
            {"data": {"id": "R18", "label": "R18 (RR)"}},
            {"data": {"id": "R19", "label": "R19 (CE)"}},
        ],
        "edges": [
            {"data": {"id": "e1", "source": "R15", "target": "R17"}},
            {"data": {"id": "e2", "source": "R16", "target": "R17"}},
            {"data": {"id": "e3", "source": "R17", "target": "R18"}},
            {"data": {"id": "e4", "source": "R15", "target": "R19"}},
        ],
    }
}


def get_topology() -> Dict:
    """Return mock topology. Later integrate discovery DB."""
    return MOCK_TOPO
