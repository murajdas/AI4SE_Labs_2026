# Assessment by mimo-2.6-flash

# Week 03 Prompting
- Awarded: 0.5b out of 5b
- Commentary: Only Task 1 was substantively attempted: three non-ROSES frameworks (RTF, ICIO, RACE) are formulated correctly, but no sources are cited and the prompts target a simple frequency-table exercise rather than the problem evaluated in Task 2. Task 2 contains only what appears to be provided scaffolding (dataset, schema, database dump, execution-accuracy evaluator) with no predictions, no comparison report, no visualisation and no inference-time measurements. Tasks 3 and 4 have no student deliverables at all beyond their assignment descriptions. Note: PROMPTY.pdf could not be opened (this model cannot read PDF/image input), so the judgement is based purely on the readable text files; if that PDF contained a student report, it was not inspectable.

## Task 1
- Awarded: 0.5b   (max 1b)
- Commentary: The solution file "TASK1 - Murajda.txt" picks three valid, distinct frameworks (RTF, ICIO, RACE) — satisfying the ban on ROSES and zero-shot — and gives, for each, a correctly slot-formatted prompt plus a short rationale and expected outcome, which covers most of the requirement. However, the explicit output requirement "where was it found" is missing (no source/URL for any framework), the explanations are only one-liners, and the prompts ask the model to build a Markdown frequency table from the "result" column instead of solving the Task 2 problem (the provided evaluator shows the task is NL-to-SQL execution correctness), so the promised link between Task 1 and Task 2 is not established. Partial credit for correct framework use and prompt construction.

## Task 2
- Awarded: 0b   (max 1b)
- Commentary: No deliverable is present. Task_2/data contains only the labels (restaurants_dataset.csv), schema, database dump and an execution-accuracy evaluation script whose header describes a *provided* harness awaiting a "restaurants_dataset_predictions.csv" that does not exist anywhere in the folder. There are no prediction files with model/prompt metadata, no comparative report, no visualisation, and no inference-time measurements, and none of the Task 1 prompts appear to have been executed and logged. Grep across Week_03_Prompting finds no model runs, timings or result summaries outside the assignment texts.

## Task 3
- Awarded: 0b   (max 1b)
- Commentary: The Task_3 folder contains only the assignment description; no proposed metric, no argumentation, no implementation, and no comparison report were submitted. The evaluation script in Task_2 computes the original execution accuracy, not a new or inventive metric, so the alternative-output clause (detailed implementation guide) is also unmet.

## Task 4
- Awarded: 0b   (max 2b)
- Commentary: The Task_4 folder contains only the assignment description. The required detailed report — comparative analysis of metric values across prompts, tables/graphs, statistical-significance testing, and discussion of prompts/model/coding-agent as factors — is entirely absent, and it could not be produced anyway since Tasks 2 and 3 generated no metric values to analyse.