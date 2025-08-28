
from __future__ import annotations
import threading
import time
from typing import List
try:
    import networkx as nx  # Optional dependency for routing
    _USE_NETWORKX = True
except Exception:
    nx = None
    _USE_NETWORKX = False
from classical_network.enum import PacketType
from core.enums import NodeType
from core.exceptions import NotConnectedError
from core.s_object import Sobject
from classical_network.node import ClassicalNode

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from classical_network.packet import ClassicDataPacket
    from classical_network.connection import ClassicConnection

class RouteTable(object):

    def __init__(self):
        if _USE_NETWORKX:
            self.network_graph = nx.Graph()
        else:
            # Minimal undirected graph with BFS shortest path as a fallback
            class _SimpleGraph:
                def __init__(self):
                    self.adj = {}

                def add_edge(self, u, v):
                    if u not in self.adj:
                        self.adj[u] = set()
                    if v not in self.adj:
                        self.adj[v] = set()
                    self.adj[u].add(v)
                    self.adj[v].add(u)

                def shortest_path(self, source, target):
                    if source == target:
                        return [source]
                    from collections import deque
                    visited = {source}
                    parent = {source: None}
                    q = deque([source])
                    found = False
                    while q:
                        u = q.popleft()
                        for w in self.adj.get(u, ()): 
                            if w in visited:
                                continue
                            visited.add(w)
                            parent[w] = u
                            if w == target:
                                found = True
                                q.clear()
                                break
                            q.append(w)
                    if not found:
                        return []
                    # Reconstruct path
                    path = [target]
                    while parent[path[-1]] is not None:
                        path.append(parent[path[-1]])
                    path.reverse()
                    return path

            self.network_graph = _SimpleGraph()

    def add_edge(self, from_node: ClassicalNode, to_node: ClassicalNode):
        self.network_graph.add_edge(from_node, to_node)

    def get_path(
        self, from_node: ClassicalNode, to_node: ClassicalNode
    ) -> List[ClassicalNode]:
        if _USE_NETWORKX:
            path = nx.shortest_path(self.network_graph, from_node, to_node)
            return path
        else:
            # Use fallback BFS
            return self.network_graph.shortest_path(from_node, to_node)


class InternetExchange(ClassicalNode):
    __instance: "InternetExchange" = None
    route_table = RouteTable()
    
    def __init__(self, node_type, location, address, network, zone = None, name="", description=""):
        super().__init__(node_type, location, address, network, zone, name, description)

    @staticmethod
    def get_instance():
        if not InternetExchange.__instance:
            InternetExchange.__instance = InternetExchange(NodeType.INTERNET_EXCHANGE, (0, 0), "121.2.213.22", None, name="Internet Exchange")

        return InternetExchange.__instance

    def forward(self):
        for node_2, buffer in self.buffers.items():
            while not buffer.empty():
                packet = buffer.get()
                
                if packet.next_hop == self:
                    self.recive_packet(packet)
                else:
                    self.logger.warn(f"Unexpected packet '{packet}' received from {node_2}")
                    

    def recive_packet(self, packet: ClassicDataPacket):
        packet.append_hop(self)
        if packet.type == PacketType.DATA:
            self.route_packet(packet)

    def route_packet(self, packet: ClassicDataPacket):
        packet.append_hop(self)
        # direct_connection = self.get_connection(self, packet.to_address)
        
        # if direct_connection:
        #     packet.next_hop = packet.to_address
        #     direct_connection.transmit_packet(packet)
        #     return
        
        shortest_path = self.get_path(self, packet.to_address)
        
        if len(shortest_path) <= 1:
            raise NotConnectedError(self, packet.to_address)
        
        
        next_hop = shortest_path[1]
        
        packet.next_hop = next_hop
        next_connection = self.get_connection(self, next_hop)
        
        if not next_connection:
            raise NotConnectedError(self, next_hop)
        
        next_connection.transmit_packet(packet)
        
    def add_connection(self, connection: ClassicConnection):
        super().add_connection(connection)

        if connection.node_1 == self or connection.node_2 == self:
            return
        self.route_table.add_edge(connection.node_1, connection.node_2)
        

    def get_path(self, from_host, to_host):
        return self.route_table.get_path(from_host, to_host)
    
    def start(self, fps):
        def _start():
            while True:
                self.forward()
                
                time.sleep(fps)
                
        thread = threading.Thread(target=_start, daemon=True)
        
        thread.start()
