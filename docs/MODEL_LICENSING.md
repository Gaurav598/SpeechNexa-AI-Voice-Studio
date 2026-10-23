# Model licensing boundary

SpeechNexa's application license covers the application source. Inference model
code, weights, conversions, tokenizers, voice samples, and outputs can have
different terms. The application license does not provide commercial-use or
redistribution permission for those assets.

`backend/config/model_licenses.json` is the current machine-readable inventory:
57 model entries and seven dynamic asset families in this imported archive.
Four model entries are marked `noncommercial`; 53 are `unreviewed`. A false
`commercial_use` flag can mean an unresolved review, not a finding that all use
is forbidden. No entry currently asserts complete commercial clearance.
Evidence revisions identify inspected terms, not necessarily the exact files
downloaded at runtime.

The generated disclosure snapshot at
[model-license-data.json](licensing/model-license-data.json) contains the same
57 entries and seven families. It is disclosure data, not proof of clearance
or a complete inventory of files a runtime SDK might fetch.
Bundled demonstration audio and video have a separate rights review; they are
outside this model inventory (see [third-party notices](../THIRD_PARTY_NOTICES.md)).

The default [OmniVoice card](https://huggingface.co/k2-fsa/OmniVoice) describes
its code as Apache-2.0 and pretrained weights as CC-BY-NC (without specifying
the CC version in that statement). Its audio tokenizer names additional Boson
Higgs Audio 2 and Meta Llama terms. The repository also records NLLB,
Llama-OuteTTS, and OmniVoice-GGUF as noncommercial; their evidence and exact
labels are in [model-inventory.md](licensing/model-inventory.md).

Before adding or redistributing a model, record the exact source and revision,
artifact hashes, component licenses, permitted use, attribution text, access
conditions, and whether redistribution is allowed. Do not commit downloaded
weights or treat model-card metadata as proof that all components have the same
terms. The [reviewed-file workflow](licensing/model-review-workflow.md) records
local acknowledgements where full evidence exists; it grants no provider rights.

Run the offline inventory checks after changing model configuration:

```sh
python scripts/check_model_licenses.py
pytest tests/test_model_licenses.py
```
