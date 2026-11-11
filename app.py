import streamlit as st

import ollama

import re

# ==================================================

# CONFIGURATION

# ==================================================

st.set_page_config(

          page_title="Adaptive Prompt Engineering Framework",

          page_icon="🧠",

          layout="wide"

)

MODEL_NAME = "qwen2.5:1.5b"

st.title("Adaptive Prompt Engineering Framework")

st.caption(

          "An adaptive research prototype for improving "

          "LLM reliability and reducing bias."

)

# ==================================================

# MODULE 1: ADAPTIVE TECHNIQUE SELECTION

# All nine techniques from the seminar PPT

# ==================================================

ALL_TECHNIQUES = [

          "Zero-shot Prompting",

          "Few-shot Prompting",

          "Chain-of-Thought (CoT)",

          "Role-based Prompting",

          "Structured Prompting",

          "Iterative Prompting",

          "Test-driven Prompting",

          "Retrieval-Augmented Generation (RAG)",

          "Query Transformation"

]

def select_techniques(task, query):

          # Task-based selection. Techniques are chosen

          # according to the task, not applied universally.

          if task == "Question Answering":

                    techniques = [

                              "Zero-shot Prompting",

                              "Structured Prompting"

                    ]

          elif task == "Text Classification":

                    techniques = [

                              "Few-shot Prompting",

                              "Structured Prompting"

                    ]

          elif task == "Code Generation":

                    techniques = [

                              "Test-driven Prompting",

                              "Iterative Prompting",

                              "Structured Prompting"

                    ]

          elif task == "Cybersecurity Analysis":

                    techniques = [

                              "Role-based Prompting",

                              "Structured Prompting",

                              "Zero-shot Prompting"

                    ]

                    # Recommend RAG when an external knowledge

                    # source is available in a future/extended setup.

                    techniques.append(

                              "Retrieval-Augmented Generation (RAG)"

                    )

          else:

                    techniques = [

                              "Zero-shot Prompting",

                              "Structured Prompting"

                    ]

          # Add query transformation for very short or

          # underspecified queries.

          if len(query.strip().split()) < 7:

                    if "Query Transformation" not in techniques:

                              techniques.append("Query Transformation")

          return techniques

# ==================================================

# MODULE 2: TECHNIQUE IMPLEMENTATION STATUS

# ==================================================

def technique_status(technique):

          statuses = {

                    "Zero-shot Prompting":

                              "Implemented: instructions are provided without examples.",

                    "Few-shot Prompting":

                              "Partially implemented: illustrative examples are added for classification tasks.",

                    "Chain-of-Thought (CoT)":

                              "Partially implemented: asks for a concise rationale, not private internal reasoning.",

                    "Role-based Prompting":

                              "Implemented: assigns a task-appropriate role.",

                    "Structured Prompting":

                              "Implemented: provides explicit instructions and output structure.",

                    "Iterative Prompting":

                              "Implemented: evaluates the initial response and allows a refinement attempt.",

                    "Test-driven Prompting":

                              "Partially implemented: code tasks can include test cases, but tests are not automatically executed.",

                    "Retrieval-Augmented Generation (RAG)":

                              "Recommended only: no document retrieval or knowledge base is connected yet.",

                    "Query Transformation":

                              "Implemented: expands short queries into a clearer task description."

          }

          return statuses.get(technique, "Status not defined.")

# ==================================================

# MODULE 3: QUERY TRANSFORMATION

# ==================================================

def transform_query(task, query):

          if len(query.strip().split()) < 7:

                    transformed = (

                              f"Task: {task}. "

                              f"Please address the following request clearly: {query}. "

                              "State relevant assumptions and missing information, "

                              "and provide an appropriate answer."

                    )

                    return transformed

          return query.strip()

# ==================================================

# MODULE 4: BUILD THE ADAPTIVE PROMPT

# ==================================================

def build_prompt(task, query, techniques):

          instructions = [

                    "Answer the user's request clearly and directly.",

                    "Separate observed facts from interpretations.",

                    "Do not present unsupported claims as established facts.",

                    "State uncertainty and identify missing information.",

                    "Avoid stereotypes and unfair assumptions.",

                    "Provide recommendations proportional to the evidence.",

                    "Do not invent facts, sources, or observations.",

                    "Use a clear and structured response."

          ]

          role_instruction = ""

          if "Role-based Prompting" in techniques:

                    if task == "Cybersecurity Analysis":

                              role_instruction = (

                                        "Act as a cautious cybersecurity analyst. "

                                        "Distinguish suspicious activity from confirmed incidents."

                              )

                    elif task == "Code Generation":

                              role_instruction = (

                                        "Act as a careful software developer. "

                                        "Produce readable code and explain how to test it."

                              )

                    else:

                              role_instruction = (

                                        "Act as a careful subject-matter assistant."

                              )

          few_shot_instruction = ""

          if "Few-shot Prompting" in techniques:

                    few_shot_instruction = """

Use the following format example for classification:

Input: "The server returned HTTP status 500."

Output: "Category: Server Error; Evidence: HTTP 500 status."

Apply the same evidence-based format to the user's input.

Do not assume this example determines the correct label.

"""

          reasoning_instruction = ""

          if "Chain-of-Thought (CoT)" in techniques:

                    reasoning_instruction = """

Provide a concise explanation of the key evidence,

criteria, and conclusion. Do not present speculation

as fact or provide unnecessary private internal reasoning.

"""

          test_instruction = ""

          if "Test-driven Prompting" in techniques:

                    test_instruction = """

For code-generation tasks:

- Include relevant test cases.

- Explain the expected output of each test.

- Identify important edge cases.

- Do not claim that code passed tests unless tests were executed.

"""

          rag_instruction = ""

          if "Retrieval-Augmented Generation (RAG)" in techniques:

                    rag_instruction = """

Retrieval note: this prototype does not currently retrieve

external documents. Do not claim that external sources were

searched or verified. Base the answer on the supplied query

and clearly state what cannot be confirmed.

"""

          prompt = f"""

{role_instruction}

Task type:

{task}

Selected prompting techniques:

{", ".join(techniques)}

Instructions:

{chr(10).join(

          str(i + 1) + ". " + item

          for i, item in enumerate(instructions)

)}

{few_shot_instruction}

{reasoning_instruction}

{test_instruction}

{rag_instruction}

User query:

{query}

Return a clear, useful, and appropriately structured answer.

"""

          return prompt.strip()

# ==================================================

# MODULE 5: LOCAL LLM RESPONSE

# ==================================================

def generate_response(prompt):

          response = ollama.chat(

                    model=MODEL_NAME,

                    messages=[

                              {

                                        "role": "user",

                                        "content": prompt

                              }

                    ],

                    options={

                              "temperature": 0.2

                    }

          )

          return response["message"]["content"]

# ==================================================

# MODULE 6: RELIABILITY AND BIAS INDICATORS

# ==================================================

def evaluate_response(query, answer):

          text = answer.lower()

          recommendation_terms = [

                    "recommend", "should", "implement",

                    "review", "action", "consider"

          ]

          uncertainty_terms = [

                    "possible", "possibly", "may", "might",

                    "could", "uncertain", "not enough evidence",

                    "cannot determine", "further investigation"

          ]

          evidence_terms = [

                    "observed", "evidence", "based on",

                    "available information", "indicates"

          ]

          certainty_phrases = [

                    "clear indication",

                    "definitely proves",

                    "certainly an attack",

                    "confirms that",

                    "undoubtedly",

                    "proves that"

          ]

          stereotype_phrases = [

                    "all women are",

                    "all men are",

                    "people from this country are",

                    "people of this religion are",

                    "all members of this group are"

          ]

          return {

                    "word_count": len(re.findall(r"\b\w+\b", answer)),

                    "has_recommendation": any(

                              term in text for term in recommendation_terms

                    ),

                    "discusses_evidence": any(

                              term in text for term in evidence_terms

                    ),

                    "acknowledges_uncertainty": any(

                              term in text for term in uncertainty_terms

                    ),

                    "flagged_phrases": [

                              phrase for phrase in certainty_phrases

                              if phrase in text

                    ],

                    "bias_flags": [

                              phrase for phrase in stereotype_phrases

                              if phrase in text

                    ]

          }

# ==================================================

# MODULE 7: PROMPT REFINEMENT

# ==================================================

def refine_prompt(task, query, answer, evaluation):

          issues = []

          if evaluation["flagged_phrases"]:

                    issues.append(

                              "Review potentially overconfident wording: "

                              + ", ".join(evaluation["flagged_phrases"])

                    )

          if not evaluation["acknowledges_uncertainty"]:

                    issues.append(

                              "State uncertainty and missing information more clearly."

                    )

          if not evaluation["discusses_evidence"]:

                    issues.append(

                              "Separate observed evidence from assumptions."

                    )

          if not evaluation["has_recommendation"]:

                    issues.append(

                              "Include relevant recommendations when appropriate."

                    )

          if evaluation["bias_flags"]:

                    issues.append(

                              "Review potentially stereotypical wording."

                    )

          if not issues:

                    issues.append(

                              "No listed heuristic issue was detected. "

                              "Still review factual claims and assumptions."

                    )

          refined_prompt = f"""

Revise the following answer for the task: {task}

Original query:

{query}

Previous answer:

{answer}

Issues for review:

{chr(10).join("- " + issue for issue in issues)}

Instructions for the revised answer:

1. Correct unsupported or overconfident statements.

2. Distinguish known facts from possible explanations.

3. Identify missing information and uncertainty.

4. Use fair and non-stereotypical language.

5. Give relevant, evidence-proportionate recommendations.

6. Do not invent evidence or claim that facts were verified.

Return the complete revised answer.

"""

          return refined_prompt.strip(), issues

# ==================================================

# USER INTERFACE

# ==================================================

st.subheader("1. Enter your task")

task = st.selectbox(

          "Select the task type",

          [

                    "Question Answering",

                    "Text Classification",

                    "Code Generation",

                    "Cybersecurity Analysis"

          ]

)

query = st.text_area(

          "Enter your query",

          placeholder=(

                    "Example: Analyze 10 failed logins followed by "

                    "a successful login and identify possible threats."

          ),

          height=120

)

if st.button("Analyze and Optimize Prompt", type="primary"):

          if not query.strip():

                    st.warning("Please enter a query first.")

          else:

                    transformed_query = transform_query(task, query)

                    techniques = select_techniques(task, query)

                    prompt = build_prompt(

                              task,

                              transformed_query,

                              techniques

                    )

                    with st.spinner("Generating response using Qwen..."):

                              try:

                                        answer = generate_response(prompt)

                                        evaluation = evaluate_response(

                                                  transformed_query,

                                                  answer

                                        )

                                        refined_prompt, issues = refine_prompt(

                                                  task,

                                                  transformed_query,

                                                  answer,

                                                  evaluation

                                        )

                                        st.session_state["task"] = task

                                        st.session_state["original_query"] = query

                                        st.session_state["transformed_query"] = transformed_query

                                        st.session_state["techniques"] = techniques

                                        st.session_state["prompt"] = prompt

                                        st.session_state["answer"] = answer

                                        st.session_state["evaluation"] = evaluation

                                        st.session_state["refined_prompt"] = refined_prompt

                                        st.session_state["issues"] = issues

                                        # Clear any result from an earlier refinement

                                        st.session_state.pop("improved_answer", None)

                              except Exception as error:

                                        st.error("Could not generate a response from Ollama.")

                                        st.code(str(error))

                                        st.info(

                                                  "Check that Ollama is running and "

                                                  "qwen2.5:1.5b is installed."

                                        )

# ==================================================

# DISPLAY THE RESULTS

# ==================================================

if "answer" in st.session_state:

          st.divider()

          st.subheader("2. Adaptive Technique Selection")

          st.write("**Detected task:**", st.session_state["task"])

          for technique in st.session_state["techniques"]:

                    st.markdown(f"**{technique}**")

                    st.caption(technique_status(technique))

          with st.expander("View all nine techniques and their status"):

                    for technique in ALL_TECHNIQUES:

                              st.markdown(f"**{technique}**")

                              st.caption(technique_status(technique))

          st.subheader("3. Query Transformation")

          st.write("**Original query:**")

          st.write(st.session_state["original_query"])

          st.write("**Query used by the framework:**")

          st.write(st.session_state["transformed_query"])

          st.subheader("4. Generated Optimized Prompt")

          st.code(st.session_state["prompt"], language="text")

          st.subheader("5. Model Response")

          st.markdown("### Qwen's Answer")

          st.write(st.session_state["answer"])

          st.divider()

          st.subheader("6. Reliability and Bias Evaluation")

          evaluation = st.session_state["evaluation"]

          col1, col2 = st.columns(2)

          with col1:

                    st.markdown("**Reliability indicators**")

                    st.metric("Response word count", evaluation["word_count"])

                    if evaluation["has_recommendation"]:

                              st.success("Recommendation-related wording detected")

                    else:

                              st.warning("No recommendation-related wording detected")

                    if evaluation["discusses_evidence"]:

                              st.success("Evidence-related wording detected")

                    else:

                              st.warning("Evidence-related wording not detected")

                    if evaluation["acknowledges_uncertainty"]:

                              st.success("Uncertainty-related wording detected")

                    else:

                              st.warning("Uncertainty-related wording not detected")

                    if evaluation["flagged_phrases"]:

                              st.warning(

                                        "Review overconfident phrases: "

                                        + ", ".join(evaluation["flagged_phrases"])

                              )

                    else:

                              st.info("No predefined certainty phrases detected")

          with col2:

                    st.markdown("**Bias screening**")

                    if evaluation["bias_flags"]:

                              st.warning(

                                        "Potential stereotype phrases detected: "

                                        + ", ".join(evaluation["bias_flags"])

                              )

                    else:

                              st.success("No predefined stereotype phrases detected")

                    st.caption(

                              "This limited phrase-based screen cannot detect all "

                              "forms of bias."

                    )

          st.caption(

                    "These are preliminary heuristic indicators. They do not "

                    "prove factual correctness, reliability, or absence of bias."

          )

          st.divider()

          st.subheader("7. Adaptive Prompt Refinement")

          st.write("Issues for the refinement attempt:")

          for issue in st.session_state["issues"]:

                    st.write(f"- {issue}")

          st.markdown("**Refined prompt:**")

          st.code(st.session_state["refined_prompt"], language="text")

          if st.button("Generate Improved Response"):

                    with st.spinner("Generating refined response..."):

                              try:

                                        improved_answer = generate_response(

                                                  st.session_state["refined_prompt"]

                                        )

                                        st.session_state["improved_answer"] = improved_answer

                              except Exception as error:

                                        st.error("Could not generate the refined response.")

                                        st.code(str(error))

          if "improved_answer" in st.session_state:

                    st.markdown("### Improved Model Response")

                    st.write(st.session_state["improved_answer"])

                    st.caption(

                              "Compare the initial and refined answers. Refinement "

                              "does not guarantee correctness or eliminate bias."

                    )