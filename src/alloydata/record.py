"""Field contract shared by every data source feeding the alloy database."""

from dataclasses import dataclass

REQUIRED_FIELDS = (
    "sample_id",
    "heat_id",
    "composition",
    "casting_process",
    "heat_treatment",
    "test_standard",
    "source",
)

CASTING_PROCESSES = frozenset(
    {
        "high_pressure_die_cast",
        "vacuum_high_pressure_die_cast",
        "low_pressure_die_cast",
        "gravity_cast",
        "sand_cast",
        "other",
    }
)

HEAT_TREATMENTS = frozenset({"as_cast", "T5", "T6", "other"})

KNOWN_ELEMENTS = frozenset(
    {
        "Al", "Si", "Mg", "Fe", "Cu", "Mn", "Zr", "Er", "Ti", "Sr",
        "Mo", "Ni", "Cr", "Sc", "Zn", "Sn", "Pb", "Ca", "Na", "B",
        "Be", "Li", "V", "Hf", "Y", "Ce", "La", "Nd", "Gd",
    }
)

DESIGN_SPACE = {
    "Al": (84.0, 92.0),
    "Si": (8.0, 11.0),
    "Mg": (0.3, 0.7),
    "Fe": (0.15, 0.8),
    "Cu": (0.0, 0.5),
    "Mn": (0.3, 0.7),
    "Zr": (0.0, 0.3),
    "Er": (0.0, 0.3),
    "Ti": (0.05, 0.15),
    "Sr": (0.015, 0.03),
}

SOURCE_PLACEHOLDERS = frozenset(
    {"", "n/a", "na", "unknown", "todo", "tbd", "none", "-", "待补", "未知"}
)

DEFAULT_SUM_TOLERANCE = 0.5


@dataclass(frozen=True)
class Issue:
    """One validation finding. Never raised, always returned."""

    code: str
    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} [{self.field}] {self.message}"
