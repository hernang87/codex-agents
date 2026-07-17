# Codex agents

This repository contains TOML configuration files for specialized Codex
engineering agents. Each file defines an agent name, role description, model,
reasoning effort, sandbox mode, and developer instructions.

## Available agents

| Config | Agent | Role | Sandbox |
| --- | --- | --- | --- |
| [`planner.toml`](planner.toml) | `planner` | Investigates existing solutions and prepares plans for non-trivial, ambiguous, multi-file, or risky work. | Read-only |
| [`executor.toml`](executor.toml) | `executor` | Implements approved plans, coordinates specialized agents, and owns validation. | Workspace write |
| [`small-task.toml`](small-task.toml) | `small_task` | Handles isolated, low-risk changes such as localized fixes, focused tests, or straightforward lint/type fixes. | Workspace write |
| [`adversarial-review.toml`](adversarial-review.toml) | `adversarial_reviewer` | Read-only reviewer that tries to disprove the correctness of plans and implementations. | Read-only |
| [`escalation.toml`](escalation.toml) | `escalation` | Re-investigates difficult, stalled, ambiguous, or repeatedly failing tasks. | Workspace write |

## Usage

Choose the configuration whose role matches the work. Planning and adversarial
review are non-editing roles. Implementation roles make focused changes and
run targeted validation; `executor` also coordinates other agents and owns
final validation.

## Routing

- Small tasks may use `small_task` after confirming the change is isolated and
  low risk.
- Normal tasks invoke `planner` before implementation.
- Hard tasks use `planner`, Luna implementation, one evidence-based repair,
  Terra replanning through `planner`, revised implementation, and then
  `adversarial_reviewer`.
- Use `escalation` only after that recovery sequence fails, except for
  substantial security, data-loss, data-integrity, or irreversible migration
  risk.

## Cost efficiency

Token price alone is not a reliable measure of model cost efficiency. Reasoning
tokens are billed as output, and a cheaper model can consume substantially more
reasoning tokens or require more retries to reach the same accepted result.

Measure complete workflows rather than isolated model calls:

```text
cost per accepted task = total input, cached-input, and output/reasoning cost
                         / accepted results
```

Track the metric by model, reasoning level, and task type. Include total token
usage, median and p90 usage, cache-hit rate, retries, repairs, escalations,
latency, and test or human acceptance rate. A multi-agent task must include
the cost of planning, execution, review, context replay, and recovery.

When comparing pricing tables, record the unit and date, context-window tier,
reasoning-token treatment, cache eligibility and hit-rate assumptions, and
whether the prices apply to the API or an application subscription. Do not
change the role assignments based on token price alone:

- `small_task` uses Luna with medium reasoning for cheap, isolated work.
- `planner` uses Terra with high reasoning when better planning can reduce
  implementation rework.
- `executor` uses Luna with high reasoning for the normal implementation path.
- `adversarial_reviewer` uses Luna with max reasoning only for risk-gated work.
- `escalation` uses Terra with xhigh reasoning only as a rare recovery path.

## Install

Install the TOML files by cloning this repository into the Codex agents
directory, commonly `~/.codex/agents`:

```sh
git clone https://github.com/hernan87/codex-agents.git ~/.codex/agents
```

For an existing checkout, update it first:

```sh
git -C ~/.codex/agents pull --ff-only
```

To copy only the profiles from another checkout instead:

```sh
cp *.toml ~/.codex/agents/
```

Validate the profiles after installation or editing:

```sh
python3 scripts/validate.py
```

## Maintenance

- Keep each configuration focused on one role and avoid unrelated cleanup.
- Keep the `name`, `description`, model settings, sandbox mode, and
  `developer_instructions` consistent with the role described here.
- Preserve the repository-first guidance: inspect existing canonical solutions
  before proposing or implementing new code.
- Keep routing gates and escalation evidence requirements aligned across the
  profiles and this README.
- For implementation changes, retain focused validation and review the full
  diff before completion. Escalate when the task becomes ambiguous,
  cross-cutting, or unsupported by the available evidence.
