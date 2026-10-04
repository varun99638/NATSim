"""
NATSim Packet Statistics

Provides statistical analysis of simulated network packets.
"""


class PacketStatistics:
    """Calculate statistics from simulated packet history."""

    def __init__(self):
        self.analysis_count = 0

    def analyze(self, packets):
        """
        Analyze a list of simulated packets.

        Expected packet fields:
            source
            protocol
            nat_type
            status
        """

        self.analysis_count += 1

        packets = packets or []

        total_packets = len(packets)

        translated_packets = sum(
            1
            for packet in packets
            if str(packet.get("status", "")).upper()
            == "TRANSLATED"
        )

        dropped_packets = sum(
            1
            for packet in packets
            if str(packet.get("status", "")).upper()
            == "DROPPED"
        )

        success_rate = self._calculate_percentage(
            translated_packets,
            total_packets,
        )

        return {
            "total_packets": total_packets,
            "translated_packets": translated_packets,
            "dropped_packets": dropped_packets,
            "success_rate": success_rate,
            "protocol_distribution": (
                self._count_by_field(
                    packets,
                    "protocol",
                )
            ),
            "device_distribution": (
                self._count_by_field(
                    packets,
                    "source",
                )
            ),
            "nat_distribution": (
                self._count_by_field(
                    packets,
                    "nat_type",
                )
            ),
        }

    def _calculate_percentage(self, value, total):
        """Calculate a percentage safely."""

        if total == 0:
            return 0.0

        return round(
            (value / total) * 100,
            2,
        )

    def _count_by_field(self, packets, field):
        """Count packets grouped by a packet field."""

        counts = {}

        for packet in packets:

            value = packet.get(
                field,
                "Unknown",
            )

            value = str(value)

            counts[value] = (
                counts.get(value, 0) + 1
            )

        return counts

    def get_empty_summary(self):
        """Return an empty statistics summary."""

        return {
            "total_packets": 0,
            "translated_packets": 0,
            "dropped_packets": 0,
            "success_rate": 0.0,
            "protocol_distribution": {},
            "device_distribution": {},
            "nat_distribution": {},
        }

    def get_analysis_count(self):
        """Return number of times statistics were calculated."""

        return self.analysis_count