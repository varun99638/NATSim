import streamlit as st
import networkx as nx
import plotly.graph_objects as go

from src.nat_engine import NATEngine
from src.packet_analyzer import PacketAnalyzer
from src.packet_statistics import PacketStatistics


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="NATSim",
    page_icon="🌐",
    layout="wide",
)


# ---------------------------------------------------------
# CUSTOM STYLING
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        .stApp {
            background-color: #0b1120;
            color: #e5e7eb;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .metric-card {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 12px;
            padding: 20px;
            min-height: 120px;
        }

        .metric-title {
            color: #9ca3af;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #f9fafb;
            font-size: 30px;
            font-weight: 700;
        }

        .section-card {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 18px;
        }

        .flow-card {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 12px;
            padding: 18px;
            text-align: center;
        }

        .success-text {
            color: #22c55e;
            font-weight: 600;
        }

        .danger-text {
            color: #ef4444;
            font-weight: 600;
        }

        .info-text {
            color: #60a5fa;
            font-weight: 600;
        }

        h1, h2, h3 {
            color: #f9fafb;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "nat_engine" not in st.session_state:
    st.session_state.nat_engine = NATEngine()

if "packet_analyzer" not in st.session_state:
    st.session_state.packet_analyzer = PacketAnalyzer()

if "packet_statistics" not in st.session_state:
    st.session_state.packet_statistics = PacketStatistics()

if "packets_sent" not in st.session_state:
    st.session_state.packets_sent = 0

if "packets_dropped" not in st.session_state:
    st.session_state.packets_dropped = 0

if "packet_history" not in st.session_state:
    st.session_state.packet_history = []

if "last_packet" not in st.session_state:
    st.session_state.last_packet = None

if "analyzed_packets" not in st.session_state:
    st.session_state.analyzed_packets = {}

if "statistics_snapshot" not in st.session_state:
    st.session_state.statistics_snapshot = None

if "statistics_packet_count" not in st.session_state:
    st.session_state.statistics_packet_count = -1


nat_engine = st.session_state.nat_engine
packet_analyzer = st.session_state.packet_analyzer
packet_statistics = st.session_state.packet_statistics


# ---------------------------------------------------------
# DEVICE CONFIGURATION
# ---------------------------------------------------------

DEVICES = {
    "PC-1": {
        "ip": "192.168.1.10",
        "port": 52341,
    },
    "PC-2": {
        "ip": "192.168.1.11",
        "port": 52342,
    },
    "PC-3": {
        "ip": "192.168.1.12",
        "port": 52343,
    },
}


# ---------------------------------------------------------
# TOPOLOGY
# ---------------------------------------------------------

def create_topology():

    graph = nx.DiGraph()

    graph.add_node(
        "PC-1",
        category="private",
    )

    graph.add_node(
        "PC-2",
        category="private",
    )

    graph.add_node(
        "PC-3",
        category="private",
    )

    graph.add_node(
        "NAT Router",
        category="nat",
    )

    graph.add_node(
        "Internet",
        category="internet",
    )

    graph.add_node(
        "Web Server",
        category="server",
    )

    graph.add_edges_from(
        [
            ("PC-1", "NAT Router"),
            ("PC-2", "NAT Router"),
            ("PC-3", "NAT Router"),
            ("NAT Router", "Internet"),
            ("Internet", "Web Server"),
        ]
    )

    return graph


# ---------------------------------------------------------
# PACKET PROCESSING
# ---------------------------------------------------------

def process_packet(
    source_device,
    protocol,
    nat_type,
):

    device = DEVICES[source_device]

    private_ip = device["ip"]
    private_port = device["port"]

    packet_number = (
        len(st.session_state.packet_history) + 1
    )

    try:

        if nat_type == "PAT":

            mapping = nat_engine.pat_translate(
                private_ip,
                private_port,
                protocol,
            )

            private_endpoint = (
                f"{private_ip}:{private_port}"
            )

            public_endpoint = (
                f"{mapping.public_ip}:{mapping.public_port}"
            )

        elif nat_type == "Static NAT":

            mapping = nat_engine.static_translate(
                private_ip
            )

            private_endpoint = private_ip

            public_endpoint = mapping.public_ip

        else:

            mapping = nat_engine.dynamic_translate(
                private_ip
            )

            private_endpoint = private_ip

            public_endpoint = mapping.public_ip

        packet = {
            "id": packet_number,
            "source": source_device,
            "protocol": protocol,
            "nat_type": mapping.nat_type,
            "private": private_endpoint,
            "public": public_endpoint,
            "status": "TRANSLATED",
        }

        st.session_state.packets_sent += 1

    except Exception as error:

        packet = {
            "id": packet_number,
            "source": source_device,
            "protocol": protocol,
            "nat_type": nat_type,
            "private": (
                f"{private_ip}:{private_port}"
            ),
            "public": "",
            "status": "DROPPED",
            "error": str(error),
        }

        st.session_state.packets_dropped += 1

    st.session_state.packet_history.append(packet)
    st.session_state.last_packet = packet

    return packet


# ---------------------------------------------------------
# PACKET ANALYSIS
# ---------------------------------------------------------

def get_packet_analysis(packet):

    packet_id = packet.get("id")

    if packet_id not in st.session_state.analyzed_packets:

        analysis = packet_analyzer.analyze(packet)

        st.session_state.analyzed_packets[
            packet_id
        ] = analysis

    return st.session_state.analyzed_packets[
        packet_id
    ]


# ---------------------------------------------------------
# STATISTICS
# ---------------------------------------------------------

def get_packet_statistics():

    packets = st.session_state.packet_history

    packet_count = len(packets)

    if (
        st.session_state.statistics_snapshot is None
        or
        st.session_state.statistics_packet_count
        != packet_count
    ):

        if packet_count == 0:

            statistics = (
                packet_statistics.get_empty_summary()
            )

        else:

            statistics = packet_statistics.analyze(
                packets
            )

        st.session_state.statistics_snapshot = (
            statistics
        )

        st.session_state.statistics_packet_count = (
            packet_count
        )

    return st.session_state.statistics_snapshot


# ---------------------------------------------------------
# METRIC CARD
# ---------------------------------------------------------

def metric_card(title, value):

    st.html(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                {title}
            </div>

            <div class="metric-value">
                {value}
            </div>
        </div>
        """
    )


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("🌐 NATSim")

st.sidebar.caption(
    "Network Address Translation Simulator"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Network Topology",
        "Packet Simulator",
        "Packet Inspector",
        "NAT Table",
        "Analytics",
    ],
)


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

if page == "Dashboard":

    st.title("🌐 NATSim Dashboard")

    st.write(
        "Interactive Network Address Translation "
        "and Packet Flow Simulator"
    )

    st.markdown("### Network Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "Packets Sent",
            st.session_state.packets_sent,
        )

    with col2:
        metric_card(
            "Packets Dropped",
            st.session_state.packets_dropped,
        )

    with col3:
        metric_card(
            "NAT Mappings",
            len(
                nat_engine.get_translation_table()
            ),
        )

    with col4:
        metric_card(
            "Packets Analyzed",
            len(
                st.session_state.analyzed_packets
            ),
        )

    st.markdown("### Current Network")

    graph = create_topology()

    positions = {
        "PC-1": (0, 2),
        "PC-2": (0, 1),
        "PC-3": (0, 0),
        "NAT Router": (2, 1),
        "Internet": (4, 1),
        "Web Server": (6, 1),
    }

    edge_x = []
    edge_y = []

    for source, target in graph.edges():

        x0, y0 = positions[source]
        x1, y1 = positions[target]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(
            width=2,
            color="#475569",
        ),
        hoverinfo="none",
    )

    node_x = []
    node_y = []
    node_text = []

    for node in graph.nodes():

        x, y = positions[node]

        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="bottom center",
        marker=dict(
            size=35,
            color="#2563eb",
            line=dict(
                width=2,
                color="#93c5fd",
            ),
        ),
        hoverinfo="text",
    )

    figure = go.Figure(
        data=[
            edge_trace,
            node_trace,
        ]
    )

    figure.update_layout(
        height=400,
        paper_bgcolor="#0b1120",
        plot_bgcolor="#0b1120",
        showlegend=False,
        xaxis=dict(
            visible=False
        ),
        yaxis=dict(
            visible=False
        ),
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )


# ---------------------------------------------------------
# NETWORK TOPOLOGY
# ---------------------------------------------------------

elif page == "Network Topology":

    st.title("🖧 Network Topology")

    st.write(
        "Visual representation of the simulated "
        "private and public network."
    )

    graph = create_topology()

    positions = {
        "PC-1": (0, 2),
        "PC-2": (0, 1),
        "PC-3": (0, 0),
        "NAT Router": (2, 1),
        "Internet": (4, 1),
        "Web Server": (6, 1),
    }

    edge_x = []
    edge_y = []

    for source, target in graph.edges():

        x0, y0 = positions[source]
        x1, y1 = positions[target]

        edge_x.extend(
            [x0, x1, None]
        )

        edge_y.extend(
            [y0, y1, None]
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(
            width=3,
            color="#64748b",
        ),
        hoverinfo="none",
    )

    node_x = []
    node_y = []
    node_text = []

    for node in graph.nodes():

        x, y = positions[node]

        node_x.append(x)
        node_y.append(y)

        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="bottom center",
        marker=dict(
            size=42,
            color="#2563eb",
            line=dict(
                width=2,
                color="#bfdbfe",
            ),
        ),
        hoverinfo="text",
    )

    figure = go.Figure(
        data=[
            edge_trace,
            node_trace,
        ]
    )

    figure.update_layout(
        height=500,
        paper_bgcolor="#0b1120",
        plot_bgcolor="#0b1120",
        showlegend=False,
        xaxis=dict(
            visible=False
        ),
        yaxis=dict(
            visible=False
        ),
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )

    st.markdown("### Devices")

    device_columns = st.columns(3)

    for index, (
        device_name,
        device_info,
    ) in enumerate(DEVICES.items()):

        with device_columns[index]:

            st.html(
                f"""
                <div class="section-card">
                    <h3>{device_name}</h3>

                    <p>
                        Private IP:
                        <b>{device_info["ip"]}</b>
                    </p>

                    <p>
                        Port:
                        <b>{device_info["port"]}</b>
                    </p>
                </div>
                """
            )


# ---------------------------------------------------------
# PACKET SIMULATOR
# ---------------------------------------------------------

elif page == "Packet Simulator":

    st.title("📦 Packet Simulator")

    st.write(
        "Generate packets and observe how NAT "
        "translates private addresses."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        source_device = st.selectbox(
            "Source Device",
            list(DEVICES.keys()),
        )

    with col2:

        protocol = st.selectbox(
            "Protocol",
            [
                "TCP",
                "UDP",
                "ICMP",
            ],
        )

    with col3:

        nat_type = st.selectbox(
            "NAT Type",
            [
                "PAT",
                "Static NAT",
                "Dynamic NAT",
            ],
        )

    if st.button(
        "🚀 Send Packet",
        use_container_width=True,
    ):

        packet = process_packet(
            source_device,
            protocol,
            nat_type,
        )

        if packet["status"] == "TRANSLATED":

            st.success(
                "Packet translated successfully."
            )

        else:

            st.error(
                "Packet dropped during translation."
            )

    if st.session_state.last_packet:

        packet = st.session_state.last_packet

        st.markdown("### Latest Packet")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Packet ID",
                packet["id"],
            )

        with col2:

            st.metric(
                "Source",
                packet["source"],
            )

        with col3:

            st.metric(
                "Protocol",
                packet["protocol"],
            )

        with col4:

            st.metric(
                "Status",
                packet["status"],
            )

        st.markdown("### Translation")

        flow_col1, flow_col2, flow_col3 = st.columns(
            [2, 1, 2]
        )

        with flow_col1:

            st.html(
                f"""
                <div class="flow-card">
                    <h3>Private</h3>
                    <p>{packet["private"]}</p>
                </div>
                """
            )

        with flow_col2:

            st.markdown(
                "<h2 style='text-align:center;'>→</h2>",
                unsafe_allow_html=True,
            )

        with flow_col3:

            st.html(
                f"""
                <div class="flow-card">
                    <h3>Public</h3>
                    <p>
                        {packet["public"]
                        if packet["public"]
                        else "N/A"}
                    </p>
                </div>
                """
            )


# ---------------------------------------------------------
# PACKET INSPECTOR
# ---------------------------------------------------------

elif page == "Packet Inspector":

    st.title("🔍 Packet Inspector")

    packets = st.session_state.packet_history

    if not packets:

        st.info(
            "No packets available. "
            "Send a packet from the Packet Simulator first."
        )

    else:

        packet_ids = [
            packet["id"]
            for packet in packets
        ]

        selected_id = st.selectbox(
            "Select Packet",
            packet_ids,
        )

        selected_packet = next(
            packet
            for packet in packets
            if packet["id"] == selected_id
        )

        analysis = get_packet_analysis(
            selected_packet
        )

        st.markdown("### Packet Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            metric_card(
                "Packet ID",
                analysis["packet_id"],
            )

        with col2:

            metric_card(
                "Source",
                analysis["source"],
            )

        with col3:

            metric_card(
                "Protocol",
                analysis["protocol"],
            )

        with col4:

            metric_card(
                "NAT Type",
                analysis["nat_type"],
            )

        st.markdown("### Translation Flow")

        col1, col2, col3 = st.columns(
            [2, 1, 2]
        )

        with col1:

            st.html(
                f"""
                <div class="flow-card">
                    <h3>Private Endpoint</h3>
                    <p>
                        {analysis["private_ip"]}
                        :
                        {analysis["private_port"]}
                    </p>
                </div>
                """
            )

        with col2:

            st.markdown(
                "<h2 style='text-align:center;'>→</h2>",
                unsafe_allow_html=True,
            )

        with col3:

            st.html(
                f"""
                <div class="flow-card">
                    <h3>Public Endpoint</h3>
                    <p>
                        {
                            analysis["public_ip"]
                            if analysis["public_ip"]
                            else "N/A"
                        }
                        {
                            ":" + analysis["public_port"]
                            if analysis["public_port"]
                            else ""
                        }
                    </p>
                </div>
                """
            )

        st.markdown("### Translation Status")

        if (
            analysis["translation"]
            == "NAT translation successful"
        ):

            st.success(
                analysis["translation"]
            )

        else:

            st.error(
                analysis["translation"]
            )

        st.markdown("### Diagnostic")

        st.info(
            analysis["diagnostic"]
        )

        with st.expander(
            "View Raw Packet"
        ):

            st.json(
                selected_packet
            )


# ---------------------------------------------------------
# NAT TABLE
# ---------------------------------------------------------

elif page == "NAT Table":

    st.title("🔄 NAT Translation Table")

    table = nat_engine.get_translation_table()

    if not table:

        st.info(
            "No active NAT mappings."
        )

    else:

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
        )


# ---------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------

elif page == "Analytics":

    st.title("📊 Packet Analytics")

    st.write(
        "Statistical analysis of simulated packet "
        "traffic and NAT behavior."
    )

    statistics = get_packet_statistics()

    total_packets = statistics[
        "total_packets"
    ]

    translated_packets = statistics[
        "translated_packets"
    ]

    dropped_packets = statistics[
        "dropped_packets"
    ]

    success_rate = statistics[
        "success_rate"
    ]

    # -----------------------------------------------------
    # TOP METRICS
    # -----------------------------------------------------

    st.markdown("### Traffic Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        metric_card(
            "Total Packets",
            total_packets,
        )

    with col2:

        metric_card(
            "Translated",
            translated_packets,
        )

    with col3:

        metric_card(
            "Dropped",
            dropped_packets,
        )

    with col4:

        metric_card(
            "Success Rate",
            f"{success_rate:.2f}%",
        )

    # -----------------------------------------------------
    # TRAFFIC STATUS
    # -----------------------------------------------------

    st.markdown("### Traffic Status")

    if total_packets == 0:

        st.info(
            "No packet traffic available yet. "
            "Send packets from the Packet Simulator "
            "to generate analytics."
        )

    else:

        status_figure = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        "Translated",
                        "Dropped",
                    ],
                    values=[
                        translated_packets,
                        dropped_packets,
                    ],
                    hole=0.55,
                    textinfo="label+percent",
                )
            ]
        )

        status_figure.update_layout(
            height=380,
            paper_bgcolor="#0b1120",
            plot_bgcolor="#0b1120",
            font=dict(
                color="#e5e7eb"
            ),
            showlegend=True,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            status_figure,
            use_container_width=True,
        )

    # -----------------------------------------------------
    # DISTRIBUTIONS
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Protocol Distribution")

        protocol_distribution = statistics[
            "protocol_distribution"
        ]

        if protocol_distribution:

            protocol_figure = go.Figure(
                data=[
                    go.Bar(
                        x=list(
                            protocol_distribution.keys()
                        ),
                        y=list(
                            protocol_distribution.values()
                        ),
                        text=list(
                            protocol_distribution.values()
                        ),
                        textposition="auto",
                    )
                ]
            )

            protocol_figure.update_layout(
                height=380,
                paper_bgcolor="#0b1120",
                plot_bgcolor="#0b1120",
                font=dict(
                    color="#e5e7eb"
                ),
                xaxis_title="Protocol",
                yaxis_title="Packets",
                margin=dict(
                    l=40,
                    r=20,
                    t=30,
                    b=40,
                ),
            )

            st.plotly_chart(
                protocol_figure,
                use_container_width=True,
            )

        else:

            st.info(
                "No protocol data available."
            )

    with col2:

        st.markdown("### NAT Type Distribution")

        nat_distribution = statistics[
            "nat_distribution"
        ]

        if nat_distribution:

            nat_figure = go.Figure(
                data=[
                    go.Bar(
                        x=list(
                            nat_distribution.keys()
                        ),
                        y=list(
                            nat_distribution.values()
                        ),
                        text=list(
                            nat_distribution.values()
                        ),
                        textposition="auto",
                    )
                ]
            )

            nat_figure.update_layout(
                height=380,
                paper_bgcolor="#0b1120",
                plot_bgcolor="#0b1120",
                font=dict(
                    color="#e5e7eb"
                ),
                xaxis_title="NAT Type",
                yaxis_title="Packets",
                margin=dict(
                    l=40,
                    r=20,
                    t=30,
                    b=40,
                ),
            )

            st.plotly_chart(
                nat_figure,
                use_container_width=True,
            )

        else:

            st.info(
                "No NAT distribution data available."
            )

    # -----------------------------------------------------
    # DEVICE ACTIVITY
    # -----------------------------------------------------

    st.markdown("### Device Activity")

    device_distribution = statistics[
        "device_distribution"
    ]

    if device_distribution:

        device_figure = go.Figure(
            data=[
                go.Bar(
                    x=list(
                        device_distribution.keys()
                    ),
                    y=list(
                        device_distribution.values()
                    ),
                    text=list(
                        device_distribution.values()
                    ),
                    textposition="auto",
                )
            ]
        )

        device_figure.update_layout(
            height=380,
            paper_bgcolor="#0b1120",
            plot_bgcolor="#0b1120",
            font=dict(
                color="#e5e7eb"
            ),
            xaxis_title="Device",
            yaxis_title="Packets",
            margin=dict(
                l=40,
                r=20,
                t=30,
                b=40,
            ),
        )

        st.plotly_chart(
            device_figure,
            use_container_width=True,
        )

    else:

        st.info(
            "No device activity data available."
        )

    # -----------------------------------------------------
    # STATISTICS TABLE
    # -----------------------------------------------------

    st.markdown("### Statistics Summary")

    summary_data = {
        "Metric": [
            "Total Packets",
            "Translated Packets",
            "Dropped Packets",
            "Success Rate",
        ],
        "Value": [
            total_packets,
            translated_packets,
            dropped_packets,
            f"{success_rate:.2f}%",
        ],
    }

    st.dataframe(
        summary_data,
        use_container_width=True,
        hide_index=True,
    )