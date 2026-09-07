"""Structural Analysis Module: models operational entity graph and evaluates topological correlation."""

from itertools import combinations
from typing import Dict, List, Set
import networkx as nx
import numpy as np


class OperationalEntityGraph:
    """Represents hierarchical and functional connections between cold-storage operational components."""

    def __init__(self, warehouse_id: str = "WH_01"):
        self.warehouse_id = warehouse_id
        self.g = nx.Graph()
        self._build_topology()

    def _build_topology(self):
        """Builds standard topological hierarchy:
        Warehouse <-> OperationalLedger
        Warehouse <-> InventoryLedger
        Warehouse <-> StorageUnits
        StorageUnits <-> IoT Sensors
        InventoryLedger <-> Shipment Gateways
        """
        wh = self.warehouse_id
        op_ledger = "OPERATIONAL_LEDGER"
        inv_ledger = "INVENTORY_LEDGER"
        occ_sensor = "IOT_OCCUPANCY_SENSOR"
        shipment_gw = "DISPATCH_INBOUND_GATEWAY"
        hist_profile = "HISTORICAL_BASELINE_PROFILE"

        nodes = [wh, op_ledger, inv_ledger, occ_sensor, shipment_gw, hist_profile]
        for node in nodes:
            self.g.add_node(node)

        # Connect entities structurally
        self.g.add_edge(wh, op_ledger, weight=1.0)
        self.g.add_edge(wh, inv_ledger, weight=1.0)
        self.g.add_edge(wh, occ_sensor, weight=1.0)
        self.g.add_edge(wh, hist_profile, weight=1.5)
        self.g.add_edge(inv_ledger, shipment_gw, weight=1.0)
        self.g.add_edge(op_ledger, inv_ledger, weight=1.0)
        self.g.add_edge(op_ledger, occ_sensor, weight=1.0)

    def calculate_structural_relatedness(self, active_entities: List[str]) -> float:
        """Calculates topological cohesion score [0, 1] for a set of affected entity names."""
        # Filter to entities present in the graph
        valid = [e for e in set(active_entities) if e in self.g]
        if len(valid) < 2:
            return 0.1 if len(valid) == 1 else 0.0

        pair_affinities = []
        for u, v in combinations(valid, 2):
            try:
                dist = nx.shortest_path_length(self.g, source=u, target=v)
                affinity = 1.0 / (1.0 + float(dist))
                pair_affinities.append(affinity)
            except nx.NetworkXNoPath:
                pair_affinities.append(0.0)

        mean_affinity = float(np.mean(pair_affinities)) if pair_affinities else 0.0
        # Diversity scaling: reward multi-entity involvement up to 4 entities
        diversity_factor = min(1.0, len(valid) / 3.0)
        return float(np.clip(mean_affinity * diversity_factor, 0.0, 1.0))

    def get_graph_data(self) -> Dict:
        """Returns JSON-serializable node and edge data for dashboard visualization."""
        nodes = [{"id": n, "label": n} for n in self.g.nodes()]
        edges = [{"source": u, "target": v} for u, v in self.g.edges()]
        return {"nodes": nodes, "edges": edges}
