from dataclasses import dataclass
from typing import Dict, Optional, Tuple


# ---------------------------------------------------------
# NAT TRANSLATION ENTRY
# ---------------------------------------------------------

@dataclass
class NATMapping:
    private_ip: str
    private_port: Optional[int]

    public_ip: str
    public_port: Optional[int]

    protocol: str
    nat_type: str


# ---------------------------------------------------------
# NAT ENGINE
# ---------------------------------------------------------

class NATEngine:

    def __init__(
        self,
        public_ip: str = "203.0.113.5",
        dynamic_pool: Optional[list[str]] = None,
        port_start: int = 40000,
        port_end: int = 50000
    ):
        """
        Initialize the NAT translation engine.

        Supports:
        - Static NAT
        - Dynamic NAT
        - PAT / NAT Overload
        """

        self.public_ip = public_ip

        self.dynamic_pool = dynamic_pool or [
            "203.0.113.10",
            "203.0.113.11",
            "203.0.113.12"
        ]

        self.port_start = port_start
        self.port_end = port_end

        self.next_port = port_start

        # -------------------------------------------------
        # Translation tables
        # -------------------------------------------------

        self.mappings: list[NATMapping] = []

        self.static_table: Dict[str, str] = {}

        self.dynamic_allocations: Dict[str, str] = {}

        self.port_allocations: Dict[
            Tuple[str, int, str],
            NATMapping
        ] = {}

    # -----------------------------------------------------
    # STATIC NAT
    # -----------------------------------------------------

    def add_static_mapping(
        self,
        private_ip: str,
        public_ip: str
    ) -> None:
        """
        Create a permanent one-to-one
        private IP → public IP mapping.
        """

        self.static_table[private_ip] = public_ip

    def static_translate(
        self,
        private_ip: str
    ) -> NATMapping:
        """
        Translate a private IP using Static NAT.
        """

        if private_ip not in self.static_table:
            raise ValueError(
                f"No static mapping exists for {private_ip}"
            )

        public_ip = self.static_table[private_ip]

        mapping = NATMapping(
            private_ip=private_ip,
            private_port=None,
            public_ip=public_ip,
            public_port=None,
            protocol="IP",
            nat_type="Static NAT"
        )

        self.mappings.append(mapping)

        return mapping

    # -----------------------------------------------------
    # DYNAMIC NAT
    # -----------------------------------------------------

    def dynamic_translate(
        self,
        private_ip: str
    ) -> NATMapping:
        """
        Allocate an available public IP
        from the dynamic NAT pool.
        """

        # Reuse an existing allocation
        if private_ip in self.dynamic_allocations:

            public_ip = self.dynamic_allocations[
                private_ip
            ]

        else:

            allocated_ips = set(
                self.dynamic_allocations.values()
            )

            available_ips = [
                ip for ip in self.dynamic_pool
                if ip not in allocated_ips
            ]

            if not available_ips:
                raise RuntimeError(
                    "Dynamic NAT public IP pool exhausted"
                )

            public_ip = available_ips[0]

            self.dynamic_allocations[
                private_ip
            ] = public_ip

        mapping = NATMapping(
            private_ip=private_ip,
            private_port=None,
            public_ip=public_ip,
            public_port=None,
            protocol="IP",
            nat_type="Dynamic NAT"
        )

        self.mappings.append(mapping)

        return mapping

    # -----------------------------------------------------
    # PAT / NAT OVERLOAD
    # -----------------------------------------------------

    def pat_translate(
        self,
        private_ip: str,
        private_port: int,
        protocol: str = "TCP"
    ) -> NATMapping:
        """
        Translate a private IP:port using PAT.

        Multiple private devices can share
        the same public IP because ports
        distinguish the connections.
        """

        key = (
            private_ip,
            private_port,
            protocol.upper()
        )

        # Reuse existing mapping
        if key in self.port_allocations:
            return self.port_allocations[key]

        public_port = self._allocate_port()

        mapping = NATMapping(
            private_ip=private_ip,
            private_port=private_port,
            public_ip=self.public_ip,
            public_port=public_port,
            protocol=protocol.upper(),
            nat_type="PAT"
        )

        self.port_allocations[key] = mapping

        self.mappings.append(mapping)

        return mapping

    # -----------------------------------------------------
    # PORT ALLOCATION
    # -----------------------------------------------------

    def _allocate_port(self) -> int:
        """
        Allocate the next available public port.
        """

        allocated_ports = {
            mapping.public_port
            for mapping in self.port_allocations.values()
        }

        attempts = self.port_end - self.port_start + 1

        for _ in range(attempts):

            port = self.next_port

            self.next_port += 1

            if self.next_port > self.port_end:
                self.next_port = self.port_start

            if port not in allocated_ports:
                return port

        raise RuntimeError(
            "PAT port range exhausted"
        )

    # -----------------------------------------------------
    # INBOUND PAT LOOKUP
    # -----------------------------------------------------

    def inbound_lookup(
        self,
        public_port: int,
        protocol: str = "TCP"
    ) -> NATMapping:
        """
        Find the private destination associated
        with a public PAT port.
        """

        protocol = protocol.upper()

        for mapping in self.port_allocations.values():

            if (
                mapping.public_port == public_port
                and mapping.protocol == protocol
            ):
                return mapping

        raise LookupError(
            f"No PAT mapping found for "
            f"{self.public_ip}:{public_port}/{protocol}"
        )

    # -----------------------------------------------------
    # REMOVE PAT MAPPING
    # -----------------------------------------------------

    def remove_pat_mapping(
        self,
        private_ip: str,
        private_port: int,
        protocol: str = "TCP"
    ) -> bool:
        """
        Remove an existing PAT translation.
        """

        key = (
            private_ip,
            private_port,
            protocol.upper()
        )

        mapping = self.port_allocations.pop(
            key,
            None
        )

        if mapping is None:
            return False

        if mapping in self.mappings:
            self.mappings.remove(mapping)

        return True

    # -----------------------------------------------------
    # CLEAR ALL TRANSLATIONS
    # -----------------------------------------------------

    def clear_mappings(self) -> None:
        """
        Clear all active NAT translations.
        """

        self.mappings.clear()

        self.dynamic_allocations.clear()

        self.port_allocations.clear()

    # -----------------------------------------------------
    # NAT TABLE
    # -----------------------------------------------------

    def get_translation_table(self) -> list[dict]:
        """
        Return NAT mappings in a UI-friendly format.
        """

        table = []

        for mapping in self.mappings:

            private_endpoint = mapping.private_ip

            if mapping.private_port is not None:
                private_endpoint += (
                    f":{mapping.private_port}"
                )

            public_endpoint = mapping.public_ip

            if mapping.public_port is not None:
                public_endpoint += (
                    f":{mapping.public_port}"
                )

            table.append(
                {
                    "Private": private_endpoint,
                    "Public": public_endpoint,
                    "Protocol": mapping.protocol,
                    "NAT Type": mapping.nat_type
                }
            )

        return table