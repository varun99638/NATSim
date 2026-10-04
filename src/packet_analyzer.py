"""
NATSim Packet Analyzer

Provides packet inspection and diagnostic information
for simulated network packets.
"""


class PacketAnalyzer:
    """Analyze and summarize simulated NAT packets."""

    def __init__(self):
        self.analyzed_packets = 0

    def analyze(self, packet):
        """
        Analyze a simulated packet.

        Expected packet fields:
            id
            source
            protocol
            nat_type
            private
            public
            status
        """

        self.analyzed_packets += 1

        private_endpoint = packet.get("private", "")
        public_endpoint = packet.get("public", "")

        private_ip, private_port = self._split_endpoint(
            private_endpoint
        )

        public_ip, public_port = self._split_endpoint(
            public_endpoint
        )

        return {
            "packet_id": packet.get("id"),
            "source": packet.get("source", "Unknown"),
            "protocol": packet.get("protocol", "Unknown"),
            "nat_type": packet.get("nat_type", "Unknown"),
            "status": packet.get("status", "Unknown"),
            "private_ip": private_ip,
            "private_port": private_port,
            "public_ip": public_ip,
            "public_port": public_port,
            "translation": self._get_translation_status(packet),
            "diagnostic": self._generate_diagnostic(packet),
        }

    def _split_endpoint(self, endpoint):
        """Split an IP:port endpoint safely."""

        if not endpoint:
            return "", ""

        endpoint = str(endpoint).strip()

        if ":" not in endpoint:
            return endpoint, ""

        ip, port = endpoint.rsplit(":", 1)

        return ip, port

    def _get_translation_status(self, packet):
        """Determine whether the packet was translated."""

        status = str(
            packet.get("status", "")
        ).upper()

        if status == "TRANSLATED":
            return "NAT translation successful"

        if status in {"DROPPED", "FAILED"}:
            return "NAT translation failed"

        return "No translation information"

    def _generate_diagnostic(self, packet):
        """Generate a human-readable packet diagnostic."""

        status = str(
            packet.get("status", "")
        ).upper()

        protocol = str(
            packet.get("protocol", "")
        ).upper()

        nat_type = str(
            packet.get("nat_type", "")
        ).upper()

        if status == "TRANSLATED":
            if nat_type == "PAT":
                return (
                    f"{protocol} packet successfully translated "
                    "using Port Address Translation."
                )

            return (
                f"{protocol} packet successfully translated "
                f"using {packet.get('nat_type', 'NAT')}."
            )

        if status in {"DROPPED", "FAILED"}:
            return (
                f"{protocol} packet was not successfully "
                "translated."
            )

        return "Packet requires further inspection."

    def get_summary(self):
        """Return analyzer statistics."""

        return {
            "analyzed_packets": self.analyzed_packets
        }