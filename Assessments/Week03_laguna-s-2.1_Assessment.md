# Assessment by laguna-s-2.1

# Week 03 Prompting
- Awarded: 1b out of 5b
- Commentary: The student completed Task 1 with a well-structured deliverable containing three valid prompting frameworks (RTF, ICIO, RACE) along with formulated prompts and reasoning. However, Tasks 2, 3, and 4 have no student-produced deliverables beyond the task description markdown files. In particular, the predictions file required by the evaluation script (restaurants_dataset_predictions.csv) does not exist, and no report, inference-time measurements, or visualizations were provided. The PROMTTY.pdf in the Task 2 folder could not be inspected because this model does not support PDF input, so it was not possible to evaluate any content it might contain.

## Task 1
- Awarded: 1b   (max 1b)
- Commentary: The student selected three prompting frameworks — RTF (Role-Task-Format), ICIO, and RACE — and formulated a concrete prompt for each, all written in Slovak. Each framework is explained in terms of why it was chosen and what output is expected. The prompts are well-structured and clearly aligned with the Task 2 restaurant-retrieval problem (counting occurrences of restaurant names in the result column). The frameworks are distinct from ROSES and zero-shot prompting, as required. The only minor shortcoming is that no explicit source/URL is provided for where each framework was found, but the reasoning for each choice is substantive and the prompts are concrete and applicable.

## Task 2
- Awarded: 0b   (max 1b)
- Commentary: The required deliverables — a predictions file (restaurants_dataset_predictions.csv with model and prompt metadata) and a brief report comparing how well the model solved the problems with different prompts (including inference-time measurements and a visualization) — are not present. The evaluation script (evaluate_retrieval_predictions.py) explicitly references a predictions file that does not exist in the data directory. The files present (restaurants_dataset.csv, restaurants-schema.csv, restaurants-db.txt) are the task's provided infrastructure, not student-produced solutions. A file named PROMTTY.pdf exists in the Task 2 folder, but this model does not support PDF input, so its contents could not be inspected and no text-based deliverables are available to judge from. No inference times, predictions, or comparison report were produced.

## Task 3
- Awarded: 0b   (max 1b)
- Commentary: No deliverable exists beyond the Task_3.md task description. There is no proposed metric, no implementation code, no calculation of metric values, and no report comparing metric values across prompts. The assignment asks for an invented/complementary metric with implementation and a comparison report, none of which are present.

## Task 4
- Awarded: 0b   (max 2b)
- Commentary: No deliverable exists beyond the Task_4.md task description. There is no detailed analysis report, no tables or graphs, and no statistical-significance testing of differences between prompts. Since Tasks 2 and 3 produced no results to reiterate on, this task could not be meaningfully addressed.

<!--
NOTES FOR THE GRADUER (delete this comment block in the output file):
- Max points: Task 1 = 1b, Task 2 = 1b, Task 3 = 1b, Task 4 = 2b. Total = 5b.
- The overall "Awarded" score MUST equal the sum of the four task scores.
- Half-points (0.5b steps) are allowed.
- Replace <model_name> with your model label.
- Keep the structure and headings exactly as above.
-->
