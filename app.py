import streamlit as st
import networkx as nx
import plotly.graph_objects as go

from src.nat_engine import NATEngine
from src.packet_analyzer import PacketAnalyzer


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NATSim — Network Address Translation Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #0b1120;
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] {
        background: #0f172a;
        border-right: 1px solid #1f2937;
    }

    .main-title {
        font-size: 34px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 15px;
        margin-bottom: 24px;
    }

    .status-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        background: rgba(34, 197, 94, 0.12);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.25);
        font-size: 12px;
        font-weight: 600;
    }

    .metric-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 18px;
        min-height: 115px;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 700;
    }

    .section-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .packet-flow {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        margin: 24px 0;
    }

    .endpoint {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px 20px;
        text-align: center;
        min-width: 190px;
    }

    .endpoint-title {
        color: #94a3b8;
        font-size: 12px;
        margin-bottom: 6px;
    }

    .endpoint-value {
        color: #f8fafc;
        font-weight: 600;
        font-size: 15px;
    }

    .arrow {
        color: #60a5fa;
        font-size: 28px;
        font-weight: bold;
    }

    .success-box {
        background: rgba(34, 197, 94, 0.08);
        border: 1px solid rgba(34, 197, 94, 0.25);
        border-radius: 10px;
        padding: 16px;
        color: #86efac;
    }

    .warning-box {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-radius: 10px;
        padding: 16px;
        color: #fcd34d;
    }

    .danger-box {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 10px;
        padding: 16px;
        color: #fca5a5;
    }

    .info-box {
        background: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 10px;
        padding: 16px;
        color: #93c5fd;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "nat_engine" not in st.session_state:
    st.session_state.nat_engine = NATEngine()

if "packet_analyzer" not in st.session_state:
    st.session_state.packet_analyzer = PacketAnalyzer()

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


nat_engine = st.session_state.nat_engine
packet_analyzer = st.session_state.packet_analyzer


# ============================================================
# DEVICE CONFIGURATION
# ============================================================

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


# ============================================================
# TOPOLOGY
# ============================================================

def create_topology():

    graph = nx.Graph()

    positions = {
        "PC-1": (-2, 1),
        "PC-2": (-2, 0),
        "PC-3": (-2, -1),
        "NAT Router": (0, 0),
        "Internet": (2, 0),
        "Web Server": (4, 0),
    }

    edges = [
        ("PC-1", "NAT Router"),
        ("PC-2", "NAT Router"),
        ("PC-3", "NAT Router"),
        ("NAT Router", "Internet"),
        ("Internet", "Web Server"),
    ]

    graph.add_edges_from(edges)

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
            color="#334155",
        ),
        hoverinfo="none",
    )

    node_x = []
    node_y = []
    node_text = []
    node_colors = []

    for node in graph.nodes():

        x, y = positions[node]

        node_x.append(x)
        node_y.append(y)

        if node in DEVICES:

            node_text.append(
                f"{node}<br>{DEVICES[node]['ip']}"
            )

            node_colors.append("#3b82f6")

        elif node == "NAT Router":

            node_text.append(node)
            node_colors.append("#8b5cf6")

        elif node == "Internet":

            node_text.append(node)
            node_colors.append("#22c55e")

        else:

            node_text.append(node)
            node_colors.append("#f59e0b")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="bottom center",
        hoverinfo="text",
        marker=dict(
            size=34,
            color=node_colors,
            line=dict(
                width=2,
                color="#e2e8f0",
            ),
        ),
    )

    figure = go.Figure(
        data=[
            edge_trace,
            node_trace,
        ]
    )

    figure.update_layout(
        height=420,
        paper_bgcolor="#0b1120",
        plot_bgcolor="#0b1120",
        showlegend=False,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
        ),
    )

    return figure


# ============================================================
# PACKET PROCESSING
# ============================================================

def process_packet(source_device, nat_mode, protocol):

    device = DEVICES[source_device]

    private_ip = device["ip"]
    private_port = device["port"]

    packet_number = (
        len(st.session_state.packet_history) + 1
    )

    try:

        # PAT
        if nat_mode == "PAT":

            mapping = nat_engine.pat_translate(
                private_ip,
                private_port,
                protocol,
            )

        # Static NAT
        elif nat_mode == "Static NAT":

            mapping = nat_engine.static_translate(
                private_ip,
            )

        # Dynamic NAT
        else:

            mapping = nat_engine.dynamic_translate(
                private_ip,
            )

        # Successful translation
        if mapping:

            private_endpoint = (
                f"{mapping.private_ip}:"
                f"{mapping.private_port}"
            )

            public_endpoint = (
                f"{mapping.public_ip}:"
                f"{mapping.public_port}"
            )

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

        # Translation failed
        else:

            packet = {
                "id": packet_number,
                "source": source_device,
                "protocol": protocol,
                "nat_type": nat_mode,
                "private": (
                    f"{private_ip}:"
                    f"{private_port}"
                ),
                "public": "",
                "status": "DROPPED",
            }

            st.session_state.packets_dropped += 1

    except Exception as error:

        packet = {
            "id": packet_number,
            "source": source_device,
            "protocol": protocol,
            "nat_type": nat_mode,
            "private": (
                f"{private_ip}:"
                f"{private_port}"
            ),
            "public": "",
            "status": "DROPPED",
            "error": str(error),
        }

        st.session_state.packets_dropped += 1

    st.session_state.packet_history.append(packet)
    st.session_state.last_packet = packet

    return packet


# ============================================================
# PACKET ANALYSIS
# ============================================================

def get_packet_analysis(packet):

    packet_id = packet["id"]

    if packet_id not in st.session_state.analyzed_packets:

        analysis = packet_analyzer.analyze(packet)

        st.session_state.analyzed_packets[
            packet_id
        ] = analysis

    return st.session_state.analyzed_packets[
        packet_id
    ]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(
        """
        <div style="
            font-size:28px;
            font-weight:700;
            color:#f8fafc;
        ">
            🌐 NATSim
        </div>

        <div style="
            color:#64748b;
            font-size:13px;
            margin-bottom:20px;
        ">
            Network Address Translation Simulator
        </div>
        """
    )

    st.html(
        """
        <span class="status-badge">
            ● SIMULATION READY
        </span>
        """
    )

    st.divider()

    page = st.radio(
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

    st.divider()

    st.caption("NATSim v0.4.2")
    st.caption(
        "Network Diagnostics & Packet Intelligence"
    )


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.html(
        """
        <div class="main-title">
            Network Dashboard
        </div>

        <div class="subtitle">
            Monitor NAT translations, packet activity and network flow.
        </div>
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Packets Sent
                </div>

                <div class="metric-value">
                    {st.session_state.packets_sent}
                </div>

            </div>
            """
        )

    with col2:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Packets Dropped
                </div>

                <div class="metric-value">
                    {st.session_state.packets_dropped}
                </div>

            </div>
            """
        )

    with col3:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    NAT Mappings
                </div>

                <div class="metric-value">
                    {len(nat_engine.get_translation_table())}
                </div>

            </div>
            """
        )

    with col4:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Packets Analyzed
                </div>

                <div class="metric-value">
                    {len(st.session_state.analyzed_packets)}
                </div>

            </div>
            """
        )

    st.write("")

    st.markdown("### 🌐 Network Topology")

    st.plotly_chart(
        create_topology(),
        width="stretch",
        config={
            "displayModeBar": False
        },
    )

    st.markdown("### 📡 Live Packet Activity")

    if st.session_state.packet_history:

        for packet in reversed(
            st.session_state.packet_history[-5:]
        ):

            if packet["status"] == "TRANSLATED":
                icon = "🟢"
            else:
                icon = "🔴"

            st.html(
                f"""
                <div class="section-card">

                    {icon}

                    <strong>
                        Packet #{packet["id"]}
                    </strong>

                    &nbsp;

                    {packet["source"]}

                    &nbsp; → &nbsp;

                    {packet["protocol"]}

                    &nbsp; | &nbsp;

                    {packet["nat_type"]}

                    &nbsp; | &nbsp;

                    <strong>
                        {packet["status"]}
                    </strong>

                </div>
                """
            )

    else:

        st.info("No packet activity yet.")


# ============================================================
# NETWORK TOPOLOGY
# ============================================================

elif page == "Network Topology":

    st.html(
        """
        <div class="main-title">
            Network Topology
        </div>

        <div class="subtitle">
            Visual representation of the simulated private and public network.
        </div>
        """
    )

    st.plotly_chart(
        create_topology(),
        width="stretch",
        config={
            "displayModeBar": False
        },
    )

    st.markdown("### Connected Devices")

    cols = st.columns(3)

    for index, (device, details) in enumerate(
        DEVICES.items()
    ):

        with cols[index]:

            st.html(
                f"""
                <div class="section-card">

                    <div style="font-size:20px;">
                        💻
                    </div>

                    <h4>
                        {device}
                    </h4>

                    <div style="color:#94a3b8;">
                        Private IP
                    </div>

                    <strong>
                        {details["ip"]}
                    </strong>

                    <br><br>

                    <div style="color:#94a3b8;">
                        Port
                    </div>

                    <strong>
                        {details["port"]}
                    </strong>

                </div>
                """
            )


# ============================================================
# PACKET SIMULATOR
# ============================================================

elif page == "Packet Simulator":

    st.html(
        """
        <div class="main-title">
            Packet Simulator
        </div>

        <div class="subtitle">
            Generate packets and observe how NAT translates private addresses.
        </div>
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        source_device = st.selectbox(
            "Source Device",
            list(DEVICES.keys()),
        )

        nat_mode = st.selectbox(
            "NAT Mode",
            [
                "PAT",
                "Static NAT",
                "Dynamic NAT",
            ],
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

        st.write("")

        if st.button(
            "🚀 Send Packet",
            width="stretch",
            type="primary",
        ):

            process_packet(
                source_device,
                nat_mode,
                protocol,
            )

            st.rerun()

    st.divider()

    if st.session_state.last_packet:

        packet = st.session_state.last_packet

        if packet["status"] == "TRANSLATED":

            st.success(
                f"Packet #{packet['id']} successfully translated."
            )

        else:

            st.error(
                f"Packet #{packet['id']} was dropped."
            )

            if "error" in packet:

                st.caption(
                    f"Diagnostic error: {packet['error']}"
                )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Source",
                packet["source"],
            )

        with col2:

            st.metric(
                "Protocol",
                packet["protocol"],
            )

        with col3:

            st.metric(
                "NAT Type",
                packet["nat_type"],
            )

        with col4:

            st.metric(
                "Status",
                packet["status"],
            )

        public_endpoint = (
            packet["public"]
            if packet["public"]
            else "N/A"
        )

        st.html(
            f"""
            <div class="packet-flow">

                <div class="endpoint">

                    <div class="endpoint-title">
                        PRIVATE ENDPOINT
                    </div>

                    <div class="endpoint-value">
                        {packet["private"]}
                    </div>

                </div>

                <div class="arrow">
                    →
                </div>

                <div class="endpoint">

                    <div class="endpoint-title">
                        NAT ROUTER
                    </div>

                    <div class="endpoint-value">
                        {packet["nat_type"]}
                    </div>

                </div>

                <div class="arrow">
                    →
                </div>

                <div class="endpoint">

                    <div class="endpoint-title">
                        PUBLIC ENDPOINT
                    </div>

                    <div class="endpoint-value">
                        {public_endpoint}
                    </div>

                </div>

            </div>
            """
        )


# ============================================================
# PACKET INSPECTOR
# ============================================================

elif page == "Packet Inspector":

    st.html(
        """
        <div class="main-title">
            Packet Inspector
        </div>

        <div class="subtitle">
            Inspect packet headers, NAT translation and automatic diagnostics.
        </div>
        """
    )

    packets = st.session_state.packet_history

    if not packets:

        st.html(
            """
            <div class="info-box">

                <strong>
                    No packets available.
                </strong>

                <br><br>

                Send a packet from the
                Packet Simulator to inspect it here.

            </div>
            """
        )

    else:

        packet_labels = [
            (
                f"Packet #{packet['id']} — "
                f"{packet['source']} — "
                f"{packet['protocol']} — "
                f"{packet['status']}"
            )
            for packet in packets
        ]

        selected_label = st.selectbox(
            "Select Packet",
            packet_labels,
        )

        selected_index = packet_labels.index(
            selected_label
        )

        selected_packet = packets[selected_index]

        analysis = get_packet_analysis(
            selected_packet
        )

        st.divider()

        # ----------------------------------------------------
        # PACKET OVERVIEW
        # ----------------------------------------------------

        st.markdown("### 📦 Packet Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Packet ID",
                analysis["packet_id"],
            )

        with col2:

            st.metric(
                "Source",
                analysis["source"],
            )

        with col3:

            st.metric(
                "Protocol",
                analysis["protocol"],
            )

        with col4:

            st.metric(
                "NAT Type",
                analysis["nat_type"],
            )

        st.write("")

        # ----------------------------------------------------
        # TRANSLATION FLOW
        # ----------------------------------------------------

        st.markdown("### 🔄 Translation Flow")

        private_endpoint = (
            f"{analysis['private_ip']}:"
            f"{analysis['private_port']}"
        )

        if analysis["public_ip"]:

            public_endpoint = (
                f"{analysis['public_ip']}:"
                f"{analysis['public_port']}"
            )

        else:

            public_endpoint = "N/A"

        st.html(
            f"""
            <div class="packet-flow">

                <div class="endpoint">

                    <div class="endpoint-title">
                        PRIVATE ADDRESS
                    </div>

                    <div class="endpoint-value">
                        {private_endpoint}
                    </div>

                </div>

                <div class="arrow">
                    →
                </div>

                <div class="endpoint">

                    <div class="endpoint-title">
                        NAT ROUTER
                    </div>

                    <div class="endpoint-value">
                        {analysis["nat_type"]}
                    </div>

                </div>

                <div class="arrow">
                    →
                </div>

                <div class="endpoint">

                    <div class="endpoint-title">
                        PUBLIC ADDRESS
                    </div>

                    <div class="endpoint-value">
                        {public_endpoint}
                    </div>

                </div>

            </div>
            """
        )

        # ----------------------------------------------------
        # PACKET DETAILS
        # ----------------------------------------------------

        st.markdown("### 🔍 Packet Details")

        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:

            st.html(
                f"""
                <div class="section-card">

                    <h4>
                        Private Network
                    </h4>

                    <b>
                        IP Address
                    </b>

                    <br>

                    {analysis["private_ip"]}

                    <br><br>

                    <b>
                        Port
                    </b>

                    <br>

                    {analysis["private_port"]}

                </div>
                """
            )

        with detail_col2:

            st.html(
                f"""
                <div class="section-card">

                    <h4>
                        Public Network
                    </h4>

                    <b>
                        IP Address
                    </b>

                    <br>

                    {analysis["public_ip"] or "N/A"}

                    <br><br>

                    <b>
                        Port
                    </b>

                    <br>

                    {analysis["public_port"] or "N/A"}

                </div>
                """
            )

        # ----------------------------------------------------
        # TRANSLATION STATUS
        # ----------------------------------------------------

        st.markdown("### 📡 Translation Status")

        if analysis["status"] == "TRANSLATED":

            st.html(
                f"""
                <div class="success-box">

                    <strong>
                        ✓ NAT Translation Successful
                    </strong>

                    <br><br>

                    {analysis["translation"]}

                </div>
                """
            )

        else:

            st.html(
                f"""
                <div class="danger-box">

                    <strong>
                        ✕ NAT Translation Failed
                    </strong>

                    <br><br>

                    {analysis["translation"]}

                </div>
                """
            )

        st.write("")

        # ----------------------------------------------------
        # AUTOMATIC DIAGNOSTIC
        # ----------------------------------------------------

        st.markdown("### 🧠 Automatic Diagnostic")

        if analysis["status"] == "TRANSLATED":

            diagnostic_class = "success-box"

        else:

            diagnostic_class = "warning-box"

        st.html(
            f"""
            <div class="{diagnostic_class}">

                <strong>
                    Diagnostic Result
                </strong>

                <br><br>

                {analysis["diagnostic"]}

            </div>
            """
        )

        st.write("")

        # ----------------------------------------------------
        # RAW PACKET
        # ----------------------------------------------------

        with st.expander("View Raw Packet Data"):

            st.json(selected_packet)


# ============================================================
# NAT TABLE
# ============================================================

elif page == "NAT Table":

    st.html(
        """
        <div class="main-title">
            NAT Translation Table
        </div>

        <div class="subtitle">
            Active NAT mappings created during packet simulation.
        </div>
        """
    )

    table = nat_engine.get_translation_table()

    if table:

        st.dataframe(
            table,
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No NAT mappings available. "
            "Send a packet from the Packet Simulator."
        )

    st.write("")

    if st.button(
        "🗑 Clear NAT Mappings",
        width="stretch",
    ):

        nat_engine.clear_mappings()

        st.success(
            "NAT mappings cleared."
        )

        st.rerun()


# ============================================================
# ANALYTICS
# ============================================================

elif page == "Analytics":

    st.html(
        """
        <div class="main-title">
            Network Analytics
        </div>

        <div class="subtitle">
            Overview of simulated packet traffic and NAT behavior.
        </div>
        """
    )

    packets = st.session_state.packet_history

    total_packets = len(packets)

    translated_packets = sum(
        1
        for packet in packets
        if packet["status"] == "TRANSLATED"
    )

    dropped_packets = sum(
        1
        for packet in packets
        if packet["status"] == "DROPPED"
    )

    protocols = {}

    for packet in packets:

        protocol = packet["protocol"]

        protocols[protocol] = (
            protocols.get(protocol, 0) + 1
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Packets",
            total_packets,
        )

    with col2:

        st.metric(
            "Translated",
            translated_packets,
        )

    with col3:

        st.metric(
            "Dropped",
            dropped_packets,
        )

    st.divider()

    if protocols:

        st.markdown("### Protocol Distribution")

        figure = go.Figure(
            data=[
                go.Bar(
                    x=list(protocols.keys()),
                    y=list(protocols.values()),
                    text=list(protocols.values()),
                    textposition="auto",
                )
            ]
        )

        figure.update_layout(
            height=350,
            paper_bgcolor="#0b1120",
            plot_bgcolor="#111827",
            font=dict(
                color="#e5e7eb"
            ),
            xaxis_title="Protocol",
            yaxis_title="Packets",
        )

        st.plotly_chart(
            figure,
            width="stretch",
            config={
                "displayModeBar": False
            },
        )

    else:

        st.info(
            "No packet data available for analytics."
        )

    st.markdown("### Packet History")

    if packets:

        st.dataframe(
            packets,
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No packet history available."
        )