import streamlit as st
import networkx as nx
import plotly.graph_objects as go

from src.network import create_network


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="NATSim | Network Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0b1120;
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }

    .brand {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: -8px;
    }

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
        font-size: 0.82rem;
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

    .section-title {
        color: #f8fafc;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 12px;
    }

    .panel {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 15px;
    }

    .activity-empty {
        padding: 30px;
        text-align: center;
        color: #64748b;
        border: 1px dashed #334155;
        border-radius: 10px;
    }

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


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

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
        """
        **Status**

        🟢 Ready

        **NAT Mode**

        PAT / NAT Overload

        **Protocol**

        TCP
        """
    )

    st.divider()

    st.caption("NATSim v0.1")
    st.caption("Interactive Network Simulator")


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# NETWORK DATA
# ---------------------------------------------------------

network = create_network()


# ---------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">Network Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.html(
        """
        <div class="metric-card">
            <div class="metric-title">NETWORK NODES</div>
            <div class="metric-value">06</div>
            <div class="metric-description">
                Simulated devices
            </div>
        </div>
        """
    )


with col2:
    st.html(
        """
        <div class="metric-card">
            <div class="metric-title">PACKETS SENT</div>
            <div class="metric-value">00</div>
            <div class="metric-description">
                Simulation packets
            </div>
        </div>
        """
    )


with col3:
    st.html(
        """
        <div class="metric-card">
            <div class="metric-title">NAT MAPPINGS</div>
            <div class="metric-value">00</div>
            <div class="metric-description">
                Active translations
            </div>
        </div>
        """
    )


with col4:
    st.html(
        """
        <div class="metric-card">
            <div class="metric-title">PACKETS DROPPED</div>
            <div class="metric-value">00</div>
            <div class="metric-description">
                Transmission failures
            </div>
        </div>
        """
    )


st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# NETWORK TOPOLOGY
# ---------------------------------------------------------

left_panel, right_panel = st.columns([2.2, 1])


with left_panel:

    st.markdown(
        '<div class="section-title">Network Topology</div>',
        unsafe_allow_html=True
    )

    # Fixed positions for a clean network layout
    positions = {
        "PC1": (-2.5, 1.2),
        "PC2": (-2.5, 0),
        "PC3": (-2.5, -1.2),
        "NAT": (-0.5, 0),
        "INTERNET": (1.3, 0),
        "SERVER": (3.0, 0)
    }

    # -----------------------------------------------------
    # Edges
    # -----------------------------------------------------

    edge_x = []
    edge_y = []

    for source, target in network.edges():

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

    # -----------------------------------------------------
    # Nodes
    # -----------------------------------------------------

    node_x = []
    node_y = []
    node_text = []
    node_colors = []

    colors = {
        "client": "#38bdf8",
        "nat": "#a78bfa",
        "internet": "#64748b",
        "server": "#4ade80"
    }

    for node, data in network.nodes(data=True):

        x, y = positions[node]

        node_x.append(x)
        node_y.append(y)

        node_text.append(
            f"<b>{data['label']}</b><br>"
            f"{data['ip']}"
        )

        node_colors.append(
            colors[data["device_type"]]
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[
            network.nodes[node]["label"]
            for node in network.nodes()
        ],
        textposition="bottom center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            size=28,
            color=node_colors,
            line=dict(
                width=2,
                color="#e2e8f0"
            )
        )
    )

    # -----------------------------------------------------
    # Graph Figure
    # -----------------------------------------------------

    fig = go.Figure(
        data=[
            edge_trace,
            node_trace
        ]
    )

    fig.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-3.2, 3.6]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1.8, 1.8]
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ---------------------------------------------------------
# SIMULATION CONTROLS
# ---------------------------------------------------------

with right_panel:

    st.markdown(
        '<div class="section-title">Simulation Controls</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):

        st.selectbox(
            "NAT Mode",
            [
                "PAT / NAT Overload",
                "Static NAT",
                "Dynamic NAT"
            ]
        )

        st.selectbox(
            "Protocol",
            [
                "TCP",
                "UDP",
                "ICMP"
            ]
        )

        st.selectbox(
            "Source Device",
            [
                "PC-1",
                "PC-2",
                "PC-3"
            ]
        )

        st.button(
            "📦 Send Packet",
            use_container_width=True
        )


# ---------------------------------------------------------
# LIVE ACTIVITY
# ---------------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">Live Packet Activity</div>',
    unsafe_allow_html=True
)

st.html(
    """
    <div class="activity-empty">

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
            Packet events will appear here
            during simulation.
        </div>

    </div>
    """
)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)

st.html(
    """
    <div style="
        text-align:center;
        color:#475569;
        font-size:0.75rem;
        padding:15px;
    ">
        NATSim • Network Address Translation & Packet Flow Simulator
    </div>
    """
)