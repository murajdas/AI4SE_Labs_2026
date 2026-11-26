# Personal LLM Workflow

My usual workflow is based on web chat interfaces rather than a coding assistant or subagents. I most often use Claude and Gemini, which is available to students for free, and compare their answers. If their responses differ or need additional checking, I use ChatGPT to verify whether the results are correct.

I validate responses mainly by cross-checking multiple models and also by reviewing the answer manually. The final decision is mine; I do not rely on a single generated response.

```mermaid
flowchart TD
    A[Define task or question] --> B[Choose web chat tool]
    B --> C[Claude]
    B --> D[Gemini]
    C --> E[Compare responses]
    D --> E
    E --> F{Agree and seem reliable?}
    F -->|Yes| G[Manual verification]
    F -->|No| H[Ask ChatGPT for a second opinion]
    H --> E
    G --> I{Manual check successful?}
    I -->|Yes| J[Use or submit the result]
    I -->|No| K[Refine prompt or compare with more sources]
    K --> B
```
