import networkx as nx


def create_network():
    """
    Create the initial NATSim network topology.
    """

    graph = nx.Graph()

    # -----------------------------------------------------
    # Network Devices
    # -----------------------------------------------------

    graph.add_node(
        "PC1",
        device_type="client",
        label="PC-1",
        ip="192.168.1.10"
    )

    graph.add_node(
        "PC2",
        device_type="client",
        label="PC-2",
        ip="192.168.1.11"
    )

    graph.add_node(
        "PC3",
        device_type="client",
        label="PC-3",
        ip="192.168.1.12"
    )

    graph.add_node(
        "NAT",
        device_type="nat",
        label="NAT Router",
        ip="203.0.113.5"
    )

    graph.add_node(
        "INTERNET",
        device_type="internet",
        label="Internet",
        ip="Public Network"
    )

    graph.add_node(
        "SERVER",
        device_type="server",
        label="Web Server",
        ip="8.8.8.8"
    )

    # -----------------------------------------------------
    # Network Connections
    # -----------------------------------------------------

    graph.add_edges_from(
        [
            ("PC1", "NAT"),
            ("PC2", "NAT"),
            ("PC3", "NAT"),
            ("NAT", "INTERNET"),
            ("INTERNET", "SERVER")
        ]
    )

    return graph