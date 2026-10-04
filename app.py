import streamlit as st

# Page configuration
st.set_page_config(
    page_title="NATSim",
    page_icon="🌐",
    layout="wide"
)

# Title
st.title("🌐 NATSim")
st.caption("Network Address Translation & Packet Flow Simulator")

st.divider()

# Statistics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Active Connections", "0")

with col2:
    st.metric("Packets Sent", "0")

with col3:
    st.metric("Packets Translated", "0")

with col4:
    st.metric("Packets Dropped", "0")

st.divider()

# Main sections
left, right = st.columns([2, 1])

with left:
    st.subheader("🌐 Network Topology")

    st.info(
        "Network topology will be displayed here."
    )

with right:
    st.subheader("⚙️ Simulation Controls")

    st.selectbox(
        "NAT Mode",
        [
            "PAT (NAT Overload)",
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

    st.button("📦 Send Packet", use_container_width=True)

st.divider()

# NAT Translation Table
st.subheader("🔄 NAT Translation Table")

st.dataframe(
    {
        "Private IP": [],
        "Private Port": [],
        "Public IP": [],
        "Public Port": [],
        "Protocol": [],
        "Status": []
    },
    use_container_width=True
)

st.divider()

# Packet Inspector
st.subheader("📦 Packet Inspector")

col1, col2 = st.columns(2)

with col1:
    st.write("**Source**")
    st.code("192.168.1.10:5000")

with col2:
    st.write("**Destination**")
    st.code("8.8.8.8:443")

st.info("No packet has been sent yet.")