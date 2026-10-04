import streamlit as st
import networkx as nx
import plotly.graph_objects as go

from src.nat_engine import NATEngine


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NATSim | Network Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

if "nat_engine" not in st.session_state:
    st.session_state.nat_engine = NATEngine()

if "packets_sent" not in st.session_state:
    st.session_state.packets_sent = 0

if "packets_dropped" not in st.session_state:
    st.session_state.packets_dropped = 0

if "packet_history" not in st.session_state:
    st.session_state.packet_history = []

if "last_packet" not in st.session_state:
    st.session_state.last_packet = None


nat_engine = st.session_state.nat_engine


# =========================================================
# DEVICE CONFIGURATION
# =========================================================

DEVICES = {
    "PC-1": {
        "ip": "192.168.1.10",
        "port": 52341
    },
    "PC-2": {
        "ip": "192.168.1.11",
        "port": 52342
    },
    "PC-3": {
        "ip": "192.168.1.12",
        "port": 52343
    }
}


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* -----------------------------------------------------
       APPLICATION
    ----------------------------------------------------- */

    .stApp {
        background-color: #0b1120;
        color: #e5e7eb;
    }


    /* -----------------------------------------------------
       SIDEBAR
    ----------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: #e5e7eb;
    }


    /* -----------------------------------------------------
       BRAND
    ----------------------------------------------------- */

    .brand {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0;
    }

    .subtitle {
        color: #60a5fa;
        font-size: 0.92rem;
        margin-top: -8px;
    }


    /* -----------------------------------------------------
       STATUS
    ----------------------------------------------------- */

    .status {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        background-color: #052e16;
        color: #4ade80;
        border: 1px solid #166534;
        font-size: 0.82rem;
        font-weight: 600;
    }


    /* -----------------------------------------------------
       METRIC CARDS
    ----------------------------------------------------- */

    .metric-card {
        background: linear-gradient(
            145deg,
            #111827,
            #0f172a
        );

        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 18px 20px;
        min-height: 110px;
    }

    .metric-title {
        color: #94a3b8;
        font-size: 0.78rem;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 1.8rem;
        font-weight: 700;
    }

    .metric-description {
        color: #64748b;
        font-size: 0.75rem;
        margin-top: 4px;
    }


    /* -----------------------------------------------------
       SECTION HEADERS
    ----------------------------------------------------- */

    .section-title {
        color: #f8fafc;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 12px;
    }


    /* -----------------------------------------------------
       PANELS
    ----------------------------------------------------- */

    .panel {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
    }


    /* -----------------------------------------------------
       PACKET ACTIVITY
    ----------------------------------------------------- */

    .packet-card {
        background: linear-gradient(
            145deg,
            #111827,
            #0f172a
        );

        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .packet-title {
        color: #f8fafc;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .packet-details {
        color: #94a3b8;
        font-size: 0.78rem;
        margin-top: 5px;
    }

    .packet-success {
        color: #4ade80;
        font-weight: 600;
    }


    /* -----------------------------------------------------
       INFO BOX
    ----------------------------------------------------- */

    .info-box {
        background-color: #0f172a;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 14px 16px;
        color: #94a3b8;
    }


    /* -----------------------------------------------------
       FOOTER
    ----------------------------------------------------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TOPOLOGY GENERATOR
# =========================================================

def create_topology():

    graph = nx.Graph()

    nodes = [
        "PC-1",
        "PC-2",
        "PC-3",
        "NAT Router",
        "Internet",
        "Web Server"
    ]

    graph.add_nodes_from(nodes)

    graph.add_edges_from(
        [
            ("PC-1", "NAT Router"),
            ("PC-2", "NAT Router"),
            ("PC-3", "NAT Router"),
            ("NAT Router", "Internet"),
            ("Internet", "Web Server")
        ]
    )

    positions = {
        "PC-1": (0, 2),
        "PC-2": (0, 1),
        "PC-3": (0, 0),
        "NAT Router": (2, 1),
        "Internet": (4, 1),
        "Web Server": (6, 1)
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
            color="#475569"
        ),
        hoverinfo="none"
    )

    node_x = []
    node_y = []
    node_text = []

    for node in nodes:

        x, y = positions[node]

        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_colors = [
        "#38bdf8",
        "#38bdf8",
        "#38bdf8",
        "#a78bfa",
        "#94a3b8",
        "#4ade80"
    ]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="bottom center",
        hoverinfo="text",
        marker=dict(
            size=24,
            color=node_colors,
            line=dict(
                width=2,
                color="#e2e8f0"
            )
        ),
        textfont=dict(
            color="#cbd5e1",
            size=11
        )
    )

    figure = go.Figure(
        data=[
            edge_trace,
            node_trace
        ]
    )

    figure.update_layout(
        height=300,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        showlegend=False,
        xaxis=dict(
            visible=False,
            range=[-0.7, 6.7]
        ),
        yaxis=dict(
            visible=False,
            range=[-0.7, 2.7]
        )
    )

    return figure


# =========================================================
# PACKET PROCESSING
# =========================================================

def process_packet(
    source_device,
    nat_mode,
    protocol
):

    device = DEVICES[source_device]

    private_ip = device["ip"]
    private_port = device["port"]

    protocol = protocol.upper()

    try:

        # -------------------------------------------------
        # PAT
        # -------------------------------------------------

        if nat_mode == "PAT / NAT Overload":

            mapping = nat_engine.pat_translate(
                private_ip=private_ip,
                private_port=private_port,
                protocol=protocol
            )

        # -------------------------------------------------
        # STATIC NAT
        # -------------------------------------------------

        elif nat_mode == "Static NAT":

            public_ip = {
                "PC-1": "203.0.113.21",
                "PC-2": "203.0.113.22",
                "PC-3": "203.0.113.23"
            }[source_device]

            if private_ip not in nat_engine.static_table:

                nat_engine.add_static_mapping(
                    private_ip,
                    public_ip
                )

            mapping = nat_engine.static_translate(
                private_ip
            )

        # -------------------------------------------------
        # DYNAMIC NAT
        # -------------------------------------------------

        else:

            mapping = nat_engine.dynamic_translate(
                private_ip
            )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        st.session_state.packets_sent += 1

        packet_number = st.session_state.packets_sent

        private_endpoint = private_ip

        if mapping.private_port is not None:
            private_endpoint += (
                f":{mapping.private_port}"
            )

        public_endpoint = mapping.public_ip

        if mapping.public_port is not None:
            public_endpoint += (
                f":{mapping.public_port}"
            )

        packet = {
            "id": packet_number,
            "source": source_device,
            "protocol": protocol,
            "nat_type": mapping.nat_type,
            "private": private_endpoint,
            "public": public_endpoint,
            "status": "TRANSLATED"
        }

        st.session_state.packet_history.insert(
            0,
            packet
        )

        st.session_state.packet_history = (
            st.session_state.packet_history[:10]
        )

        st.session_state.last_packet = packet

    except (RuntimeError, ValueError, LookupError) as error:

        st.session_state.packets_dropped += 1

        st.session_state.last_packet = {
            "status": "DROPPED",
            "reason": str(error)
        }


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🌐 NATSim")
    st.caption("Network Simulation Platform")

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Network Topology",
            "Packet Simulator",
            "NAT Table",
            "Analytics"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### Simulation")

    st.markdown(
        f"""
        **Status**

        🟢 Ready

        **NAT Mode**

        PAT / NAT Overload

        **Protocol**

        TCP

        **Active Mappings**

        {len(nat_engine.mappings)}
        """
    )

    st.divider()

    st.caption("NATSim v0.3")
    st.caption("Interactive Network Simulator")


# =========================================================
# HEADER
# =========================================================

header_left, header_right = st.columns([5, 1])

with header_left:

    st.markdown(
        '<div class="brand">🌐 NATSim</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Interactive Network Address Translation & Packet Flow Simulator'
        '</div>',
        unsafe_allow_html=True
    )

with header_right:

    st.markdown(
        '<div style="text-align:right; margin-top:15px;">'
        '<span class="status">● SIMULATION READY</span>'
        '</div>',
        unsafe_allow_html=True
    )


st.divider()


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    # -----------------------------------------------------
    # OVERVIEW
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Network Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    NETWORK NODES
                </div>

                <div class="metric-value">
                    06
                </div>

                <div class="metric-description">
                    Simulated devices
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    PACKETS SENT
                </div>

                <div class="metric-value">
                    {st.session_state.packets_sent:02d}
                </div>

                <div class="metric-description">
                    Simulation packets
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    NAT MAPPINGS
                </div>

                <div class="metric-value">
                    {len(nat_engine.mappings):02d}
                </div>

                <div class="metric-description">
                    Active translations
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    PACKETS DROPPED
                </div>

                <div class="metric-value">
                    {st.session_state.packets_dropped:02d}
                </div>

                <div class="metric-description">
                    Transmission failures
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # MAIN PANELS
    # -----------------------------------------------------

    left_panel, right_panel = st.columns(
        [2.2, 1]
    )

    with left_panel:

        st.markdown(
            '<div class="section-title">'
            'Network Topology'
            '</div>',
            unsafe_allow_html=True
        )

        st.plotly_chart(
            create_topology(),
            width="stretch",
            config={
                "displayModeBar": False
            }
        )

    with right_panel:

        st.markdown(
            '<div class="section-title">'
            'Simulation Controls'
            '</div>',
            unsafe_allow_html=True
        )

        with st.container(border=True):

            nat_mode = st.selectbox(
                "NAT Mode",
                [
                    "PAT / NAT Overload",
                    "Static NAT",
                    "Dynamic NAT"
                ]
            )

            protocol = st.selectbox(
                "Protocol",
                [
                    "TCP",
                    "UDP",
                    "ICMP"
                ]
            )

            source_device = st.selectbox(
                "Source Device",
                [
                    "PC-1",
                    "PC-2",
                    "PC-3"
                ]
            )

            device_info = DEVICES[source_device]

            st.caption(
                f"Source IP: "
                f"`{device_info['ip']}:{device_info['port']}`"
            )

            send_packet = st.button(
                "📦  Send Packet",
                width="stretch"
            )

            if send_packet:

                process_packet(
                    source_device,
                    nat_mode,
                    protocol
                )

                st.rerun()

    # -----------------------------------------------------
    # LAST PACKET
    # -----------------------------------------------------

    if st.session_state.last_packet:

        last = st.session_state.last_packet

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="section-title">'
            'Latest Packet'
            '</div>',
            unsafe_allow_html=True
        )

        if last.get("status") == "TRANSLATED":

            st.success(
                f"Packet #{last['id']} translated successfully: "
                f"{last['private']} → {last['public']}"
            )

        else:

            st.error(
                f"Packet dropped: {last['reason']}"
            )

    # -----------------------------------------------------
    # LIVE ACTIVITY
    # -----------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">'
        'Live Packet Activity'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.packet_history:

        st.markdown(
            """
            <div class="info-box"
                 style="text-align:center;">

                <div style="font-size:2rem;">
                    📡
                </div>

                <div style="
                    margin-top:8px;
                    color:#94a3b8;
                ">
                    No packet activity yet
                </div>

                <div style="
                    margin-top:5px;
                    font-size:0.8rem;
                ">
                    Send a packet to begin the NAT simulation.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        for packet in st.session_state.packet_history:
            st.html(
                f"""
                <div class="packet-card">

                    <div class="packet-title">
                        📦 Packet #{packet['id']}
                        &nbsp; • &nbsp;
                        <span class="packet-success">
                            {packet['status']}
                        </span>
                    </div>

                    <div class="packet-details">
                        {packet['source']}
                        &nbsp; | &nbsp;
                        {packet['protocol']}
                        &nbsp; | &nbsp;
                        {packet['nat_type']}
                    </div>

                    <div class="packet-details">
                        {packet['private']}
                        &nbsp;
                        →
                        &nbsp;
                        {packet['public']}
                    </div>

                </div>
                """
            )


# =========================================================
# NETWORK TOPOLOGY PAGE
# =========================================================

elif page == "Network Topology":

    st.markdown(
        '<div class="section-title">'
        'Interactive Network Topology'
        '</div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        create_topology(),
        width="stretch",
        config={
            "displayModeBar": False
        }
    )

    st.markdown(
        """
        <div class="info-box">

        <b>Network Architecture</b><br><br>

        PC-1, PC-2 and PC-3 represent private network
        clients. Their traffic is forwarded through the
        NAT Router before reaching the simulated Internet
        and Web Server.

        <br><br>

        <b>Private Network</b> →
        <b>NAT Router</b> →
        <b>Internet</b> →
        <b>Web Server</b>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# PACKET SIMULATOR PAGE
# =========================================================

elif page == "Packet Simulator":

    st.markdown(
        '<div class="section-title">'
        'Packet Simulator'
        '</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(
        [1, 1.5]
    )

    with left:

        with st.container(border=True):

            st.markdown("### Generate Packet")

            source_device = st.selectbox(
                "Source Device",
                list(DEVICES.keys())
            )

            nat_mode = st.selectbox(
                "NAT Mode",
                [
                    "PAT / NAT Overload",
                    "Static NAT",
                    "Dynamic NAT"
                ]
            )

            protocol = st.selectbox(
                "Protocol",
                [
                    "TCP",
                    "UDP",
                    "ICMP"
                ]
            )

            device = DEVICES[source_device]

            st.info(
                f"Private endpoint: "
                f"{device['ip']}:{device['port']}"
            )

            if st.button(
                "🚀 Generate & Translate Packet",
                width="stretch"
            ):

                process_packet(
                    source_device,
                    nat_mode,
                    protocol
                )

                st.rerun()

    with right:

        st.markdown("### Packet Flow")

        if st.session_state.last_packet:

            packet = st.session_state.last_packet

            if packet.get("status") == "TRANSLATED":

                st.markdown(
                    f"""
                    <div class="panel">

                    <div style="
                        color:#38bdf8;
                        font-weight:600;
                    ">
                        PRIVATE NETWORK
                    </div>

                    <div style="
                        margin-top:8px;
                        font-size:1.1rem;
                    ">
                        {packet['private']}
                    </div>

                    <div style="
                        text-align:center;
                        font-size:1.5rem;
                        margin:12px;
                    ">
                        ↓
                    </div>

                    <div style="
                        color:#a78bfa;
                        font-weight:600;
                    ">
                        NAT ROUTER
                    </div>

                    <div style="
                        margin-top:8px;
                    ">
                        {packet['nat_type']}
                    </div>

                    <div style="
                        text-align:center;
                        font-size:1.5rem;
                        margin:12px;
                    ">
                        ↓
                    </div>

                    <div style="
                        color:#4ade80;
                        font-weight:600;
                    ">
                        PUBLIC NETWORK
                    </div>

                    <div style="
                        margin-top:8px;
                        font-size:1.1rem;
                    ">
                        {packet['public']}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.error(
                    packet["reason"]
                )

        else:

            st.info(
                "Generate a packet to visualize "
                "its NAT translation."
            )


# =========================================================
# NAT TABLE PAGE
# =========================================================

elif page == "NAT Table":

    st.markdown(
        '<div class="section-title">'
        'NAT Translation Table'
        '</div>',
        unsafe_allow_html=True
    )

    table = nat_engine.get_translation_table()

    if table:

        st.dataframe(
            table,
            width="stretch",
            hide_index=True
        )

    else:

        st.info(
            "No active NAT mappings. "
            "Send a packet to create a translation."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "🗑️ Clear NAT Mappings",
        width="stretch"
    ):

        nat_engine.clear_mappings()

        st.session_state.packet_history = []
        st.session_state.last_packet = None

        st.rerun()


# =========================================================
# ANALYTICS PAGE
# =========================================================

elif page == "Analytics":

    st.markdown(
        '<div class="section-title">'
        'Simulation Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    total_packets = (
        st.session_state.packets_sent
        + st.session_state.packets_dropped
    )

    success_rate = 0

    if total_packets > 0:

        success_rate = (
            st.session_state.packets_sent
            / total_packets
        ) * 100

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Packets Sent",
            st.session_state.packets_sent
        )

    with col2:

        st.metric(
            "Packets Dropped",
            st.session_state.packets_dropped
        )

    with col3:

        st.metric(
            "Translation Success Rate",
            f"{success_rate:.1f}%"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="info-box">

        <b>Simulation Metrics</b><br><br>

        NATSim records packet activity and translation
        results during the current simulation session.

        These metrics will be expanded in later versions
        with protocol statistics, traffic volume,
        translation distribution and packet-flow analysis.

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="
        text-align:center;
        color:#475569;
        font-size:0.75rem;
        padding:15px;
    ">
        NATSim • Network Address Translation &
        Packet Flow Simulator • v0.3
    </div>
    """,
    unsafe_allow_html=True
)