from src.packet_statistics import PacketStatistics


def test_packet_statistics_summary():

    statistics = PacketStatistics()

    packets = [
        {
            "id": 1,
            "source": "PC-1",
            "protocol": "TCP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        },
        {
            "id": 2,
            "source": "PC-2",
            "protocol": "UDP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        },
        {
            "id": 3,
            "source": "PC-1",
            "protocol": "TCP",
            "nat_type": "PAT",
            "status": "DROPPED",
        },
    ]

    result = statistics.analyze(packets)

    assert result["total_packets"] == 3
    assert result["translated_packets"] == 2
    assert result["dropped_packets"] == 1
    assert result["success_rate"] == 66.67


def test_protocol_distribution():

    statistics = PacketStatistics()

    packets = [
        {
            "source": "PC-1",
            "protocol": "TCP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        },
        {
            "source": "PC-2",
            "protocol": "UDP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        },
        {
            "source": "PC-3",
            "protocol": "TCP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        },
        {
            "source": "PC-1",
            "protocol": "ICMP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        },
    ]

    result = statistics.analyze(packets)

    assert result["protocol_distribution"] == {
        "TCP": 2,
        "UDP": 1,
        "ICMP": 1,
    }


def test_device_distribution():

    statistics = PacketStatistics()

    packets = [
        {
            "source": "PC-1",
            "protocol": "TCP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        },
        {
            "source": "PC-1",
            "protocol": "UDP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        },
        {
            "source": "PC-2",
            "protocol": "TCP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        },
    ]

    result = statistics.analyze(packets)

    assert result["device_distribution"] == {
        "PC-1": 2,
        "PC-2": 1,
    }


def test_nat_distribution():

    statistics = PacketStatistics()

    packets = [
        {
            "source": "PC-1",
            "protocol": "TCP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        },
        {
            "source": "PC-2",
            "protocol": "TCP",
            "nat_type": "Static NAT",
            "status": "TRANSLATED",
        },
        {
            "source": "PC-3",
            "protocol": "UDP",
            "nat_type": "Dynamic NAT",
            "status": "TRANSLATED",
        },
    ]

    result = statistics.analyze(packets)

    assert result["nat_distribution"] == {
        "PAT": 1,
        "Static NAT": 1,
        "Dynamic NAT": 1,
    }


def test_empty_statistics():

    statistics = PacketStatistics()

    result = statistics.analyze([])

    assert result["total_packets"] == 0
    assert result["translated_packets"] == 0
    assert result["dropped_packets"] == 0
    assert result["success_rate"] == 0.0

    assert result["protocol_distribution"] == {}
    assert result["device_distribution"] == {}
    assert result["nat_distribution"] == {}


def test_analysis_count():

    statistics = PacketStatistics()

    packets = [
        {
            "source": "PC-1",
            "protocol": "TCP",
            "nat_type": "PAT",
            "status": "TRANSLATED",
        }
    ]

    statistics.analyze(packets)
    statistics.analyze(packets)

    assert statistics.get_analysis_count() == 2