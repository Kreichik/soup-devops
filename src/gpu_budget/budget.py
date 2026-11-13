"""Round each allocation before adding up the monthly bill."""

from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal


@dataclass(frozen=True)
class Schedule:
    name: str
    runs: int
    test_minutes: Decimal
    startup_minutes: Decimal
    max_attempts: int


def positive_decimal(value: object, name: str, *, zero_ok: bool = True) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not result.is_finite() or result < 0 or (not zero_ok and result == 0):
        raise ValueError(f"{name} must be finite and {'non-negative' if zero_ok else 'positive'}")
    return result


def whole_number(value: object, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def estimate(plan: dict) -> dict:
    rate = positive_decimal(plan["billing"]["usd_per_hour"], "usd_per_hour", zero_ok=False)
    quantum = positive_decimal(plan["billing"]["quantum_minutes"], "quantum_minutes", zero_ok=False)
    rows = []
    total = Decimal(0)
    upper_total = Decimal(0)
    for name in ("nightly", "release"):
        item = plan[name]
        schedule = Schedule(
            name,
            whole_number(item["runs"], f"{name}.runs"),
            positive_decimal(item["test_minutes"], f"{name}.test_minutes"),
            positive_decimal(item["startup_minutes"], f"{name}.startup_minutes"),
            whole_number(item["max_attempts"], f"{name}.max_attempts", minimum=1),
        )
        minutes = schedule.test_minutes + schedule.startup_minutes
        billed = (minutes / quantum).to_integral_value(rounding=ROUND_CEILING) * quantum
        cost = billed / 60 * rate * schedule.runs
        total += cost
        upper_total += cost * schedule.max_attempts
        rows.append(
            {
                "schedule": name,
                "runs": schedule.runs,
                "billed_minutes_per_run": str(billed),
                "usd": money(cost),
            }
        )
    return {
        "currency": "USD",
        "schedules": rows,
        "monthly_usd": money(total),
        "retry_ceiling_usd": money(upper_total),
        "scope": "GPU compute only; excludes storage, traffic and tax",
    }


def money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
