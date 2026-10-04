from src.nat_engine import NATEngine


# ---------------------------------------------------------
# PAT TEST
# ---------------------------------------------------------

def test_pat_translation():

    nat = NATEngine()

    mapping = nat.pat_translate(
        private_ip="192.168.1.10",
        private_port=52341,
        protocol="TCP"
    )

    assert mapping.private_ip == "192.168.1.10"
    assert mapping.private_port == 52341

    assert mapping.public_ip == "203.0.113.5"
    assert mapping.public_port == 40000

    assert mapping.nat_type == "PAT"


# ---------------------------------------------------------
# PAT REUSE TEST
# ---------------------------------------------------------

def test_existing_pat_mapping_is_reused():

    nat = NATEngine()

    first = nat.pat_translate(
        "192.168.1.10",
        52341,
        "TCP"
    )

    second = nat.pat_translate(
        "192.168.1.10",
        52341,
        "TCP"
    )

    assert first.public_port == second.public_port

    assert len(nat.mappings) == 1


# ---------------------------------------------------------
# DIFFERENT CLIENT TEST
# ---------------------------------------------------------

def test_multiple_clients_get_different_ports():

    nat = NATEngine()

    first = nat.pat_translate(
        "192.168.1.10",
        52341,
        "TCP"
    )

    second = nat.pat_translate(
        "192.168.1.11",
        52341,
        "TCP"
    )

    assert first.public_ip == second.public_ip

    assert first.public_port != second.public_port


# ---------------------------------------------------------
# INBOUND LOOKUP TEST
# ---------------------------------------------------------

def test_inbound_lookup():

    nat = NATEngine()

    mapping = nat.pat_translate(
        "192.168.1.10",
        52341,
        "TCP"
    )

    result = nat.inbound_lookup(
        mapping.public_port,
        "TCP"
    )

    assert result.private_ip == "192.168.1.10"
    assert result.private_port == 52341


# ---------------------------------------------------------
# STATIC NAT TEST
# ---------------------------------------------------------

def test_static_nat():

    nat = NATEngine()

    nat.add_static_mapping(
        "192.168.1.20",
        "203.0.113.20"
    )

    mapping = nat.static_translate(
        "192.168.1.20"
    )

    assert mapping.private_ip == "192.168.1.20"
    assert mapping.public_ip == "203.0.113.20"
    assert mapping.nat_type == "Static NAT"


# ---------------------------------------------------------
# DYNAMIC NAT TEST
# ---------------------------------------------------------

def test_dynamic_nat():

    nat = NATEngine(
        dynamic_pool=[
            "203.0.113.10",
            "203.0.113.11"
        ]
    )

    first = nat.dynamic_translate(
        "192.168.1.10"
    )

    second = nat.dynamic_translate(
        "192.168.1.11"
    )

    assert first.public_ip == "203.0.113.10"
    assert second.public_ip == "203.0.113.11"

    assert first.public_ip != second.public_ip