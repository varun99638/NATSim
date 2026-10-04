from src.packet_analyzer import PacketAnalyzer


def test_packet_translation_analysis():

    analyzer = PacketAnalyzer()

    packet = {
        "id": 1,
        "source": "PC-1",
        "protocol": "TCP",
        "nat_type": "PAT",
        "private": "192.168.1.10:52341",
        "public": "203.0.113.5:40000",
        "status": "TRANSLATED",
    }

    result = analyzer.analyze(packet)

    assert result["packet_id"] == 1
    assert result["source"] == "PC-1"
    assert result["protocol"] == "TCP"
    assert result["nat_type"] == "PAT"

    assert result["private_ip"] == "192.168.1.10"
    assert result["private_port"] == "52341"

    assert result["public_ip"] == "203.0.113.5"
    assert result["public_port"] == "40000"

    assert result["translation"] == "NAT translation successful"


def test_failed_packet_analysis():

    analyzer = PacketAnalyzer()

    packet = {
        "id": 2,
        "source": "PC-2",
        "protocol": "UDP",
        "nat_type": "PAT",
        "private": "192.168.1.11:52342",
        "public": "",
        "status": "DROPPED",
    }

    result = analyzer.analyze(packet)

    assert result["status"] == "DROPPED"
    assert result["translation"] == "NAT translation failed"


def test_analyzer_summary():

    analyzer = PacketAnalyzer()

    packet = {
        "id": 3,
        "source": "PC-3",
        "protocol": "ICMP",
        "nat_type": "PAT",
        "private": "192.168.1.12:52343",
        "public": "203.0.113.5:40002",
        "status": "TRANSLATED",
    }

    analyzer.analyze(packet)

    summary = analyzer.get_summary()

    assert summary["analyzed_packets"] == 1