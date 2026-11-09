# Model Registry

Record every model the project calls, including System One judgment models (for
example TypeSafe's Jev) and local checkpoints (for example a fine-tuned Laya
model). Model names, prices, and limits change often: record the exact provider
ID or checkpoint you call, and check the provider's documentation at each review
rather than relying on memory.

| Model ID | Provider | Exact API model ID or checkpoint | Purpose | Settings (effort, thinking, structured output) | Eval set | Approved For | Owner | Last Reviewed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M-001 | Example provider | example-model-1-0 | Example purpose | effort: medium | `evals/regression/` | Internal use only | Owner | YYYY-MM-DD |

Before switching to a new model version, rerun the eval set with the new model
and record the result here. When a new version performs better, also test
whether any harness workaround written for the old version can now be removed.
