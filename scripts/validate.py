"""Validate the standalone Codex agent profiles."""

from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_NAMES = {
    "adversarial-review.toml": "adversarial_reviewer",
    "escalation.toml": "escalation",
    "executor.toml": "executor",
    "planner.toml": "planner",
    "small-task.toml": "small_task",
}
REQUIRED_KEYS = {
    "name",
    "description",
    "model",
    "model_reasoning_effort",
    "sandbox_mode",
    "developer_instructions",
}
ALLOWED_SANDBOX_MODES = {"read-only", "workspace-write", "danger-full-access"}
ALLOWED_REASONING_EFFORTS = {"low", "medium", "high", "xhigh", "max"}


def main() -> int:
    errors: list[str] = []
    actual_files = {path.name for path in ROOT.glob("*.toml")}

    missing = set(EXPECTED_NAMES) - actual_files
    unexpected = actual_files - set(EXPECTED_NAMES)
    errors.extend(f"missing expected profile: {name}" for name in sorted(missing))
    errors.extend(f"unexpected TOML profile: {name}" for name in sorted(unexpected))

    names: dict[str, str] = {}
    for filename, expected_name in EXPECTED_NAMES.items():
        path = ROOT / filename
        if not path.exists():
            continue

        try:
            data = tomllib.loads(path.read_text())
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"{filename}: cannot parse TOML: {exc}")
            continue

        missing_keys = REQUIRED_KEYS - data.keys()
        errors.extend(f"{filename}: missing key: {key}" for key in sorted(missing_keys))

        name = data.get("name")
        if name != expected_name:
            errors.append(f"{filename}: expected name {expected_name!r}, got {name!r}")
        elif name in names:
            errors.append(f"duplicate agent name {name!r}: {names[name]} and {filename}")
        else:
            names[name] = filename

        sandbox_mode = data.get("sandbox_mode")
        if (
            not isinstance(sandbox_mode, str)
            or sandbox_mode not in ALLOWED_SANDBOX_MODES
        ):
            errors.append(f"{filename}: invalid sandbox_mode: {sandbox_mode!r}")

        reasoning_effort = data.get("model_reasoning_effort")
        if (
            not isinstance(reasoning_effort, str)
            or reasoning_effort not in ALLOWED_REASONING_EFFORTS
        ):
            errors.append(
                f"{filename}: invalid model_reasoning_effort: {reasoning_effort!r}"
            )

    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1

    print(f"validated {len(EXPECTED_NAMES)} Codex agent profiles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
