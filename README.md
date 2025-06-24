# Customer Support Ticket Analyzer: Multi-Agent System

This document outlines the architecture, setup, usage, and evaluation of a multi-agent system designed to automatically classify and route customer support tickets. The system leverages large language models (LLMs) to intelligently process ticket details, determine their nature, and assign them to the most appropriate team with a recommended service level agreement (SLA).

## 1. Project Overview

The current implementation is a robust, chained multi-agent system focusing on structured data exchange between agents and including a dedicated testing framework for systematic evaluation.

* **Chained Execution:** Agents are executed sequentially (Ticket Classifier Agent output feeds into Routing Decision Agent).
* **Structured Data Flow:** Inputs and outputs for each agent are strictly defined in JSON formats, enabling reliable information transfer and processing.
* **Robust Error Handling:** The system includes mechanisms to catch and report errors during API calls or JSON parsing, ensuring graceful degradation and informative feedback during testing.
* **Automated Testing:** A separate `test.py` script facilitates running multiple predefined test cases and saving the results into organized output files.
* **API Rate Limit Management:** A short delay (`asyncio.sleep(5)`) is implemented between agent calls during batch testing to mitigate API rate limits and ensure smooth execution.

## 2. System Architecture: Specialized Agents

The system is built upon `pydantic-ai` agents, utilizing Mistral AI's `mistral-large-latest` model for its language understanding and decision-making capabilities.

### Agent 1: Ticket Classifier Agent

This agent is the first point of contact for a new support ticket. It focuses on deep understanding of the ticket's qualitative content.

* **Role:** Analyzes the subject and message of a customer support ticket to extract critical information, categorize the issue, and assess its immediate impact.
* **Input (Metadata):** Receives the raw customer support ticket in a JSON format.
    ```json
    {
        "ticket_id": "12345",
        "customer_tier": "premium", 
        "subject": "API returning 500 errors intermittently",
        "message": "Hi, our production system has been failing",
        "previous_tickets": 3,
        "monthly_revenue": 5000,
        "account_age_days": 450
    }
    ```
* **Determines:**
    * **Issue Type:** The primary category of the problem (e.g., "bug", "feature_request", "security_issue", "UI_problem", "other").
    * **Severity Level:** The technical impact or urgency of the issue from a technical standpoint (e.g., "low", "medium", "high", "critical").
    * **Sentiment:** The emotional tone of the customer's message (e.g., "angry", "neutral", "polite").
    * **Priority Score:** A quantitative score (0-1) indicating the overall priority, considering factors like customer tier and subject urgency.
* **Output (JSON Format):**
    ```json
    {
        "issue_type": "bug",
        "severity_level": "critical",
        "sentiment": "angry",
        "priority_score": 0.85
    }
    ```

### Agent 2: Routing Decision Agent

This agent takes the classified information from the first agent and combines it with broader customer context to make an informed routing decision.

* **Role:** Determines the most appropriate internal team to handle the ticket, along with an escalation flag and a recommended Service Level Agreement (SLA).
* **Input:** Receives a combined JSON object that includes both the original ticket metadata and the detailed classification output from the Ticket Classifier Agent.
    ```json
    {
        "ticket_id": "12345",
        "customer_tier": "premium",
        "subject": "API returning 500 errors intermittently",
        "message": "Hi, our production system has been failing",
        "previous_tickets": 3,
        "monthly_revenue": 5000,
        "account_age_days": 450,
        "classification": { 
            "issue_type": "bug",
            "severity_level": "critical",
            "sentiment": "angry",
            "priority_score": 0.95
        }
    }
    ```
* **Decides:**
    * **Assigned Team:** The specific team responsible (e.g., "Backend Engineering Support", "Frontend Development", "Security Team", "Product Team", "General Support L1", "Billing & Accounts").
    * **Assigned Queue:** A more granular queue within the assigned team for prioritization (e.g., "Premium Critical P1", "High Priority Bug Queue").
    * **Recommended SLA:** The suggested response timeframe (e.g., "Immediate attention (1-hour response)", "Within 4 hours", "Within 24 hours").
    * **Flag for Manager Review:** A boolean indicating if the ticket requires immediate attention from a manager/senior personnel.
* **Output (JSON Format):**
    ```json
    {
        "assigned_team": "Backend Engineering Support",
        "assigned_queue": "Premium Critical P1",
        "recommended_SLA": "Immediate attention (1-hour response)",
        "flag_for_manager_review": true
    }
    ```

## 3. Code Directories and Structure

The project follows a modular structure for better organization and maintainability.


```text
your_project/
├── .env                          # Environment variables, specifically for API keys
├── main.py                       # Main application logic; contains the 'chat' function
├── test.py                       # Script for running multiple test cases and saving results
├── agents/                       # Directory containing individual agent definitions
│   ├── __pycache__/              # Makes 'agents' a Python package
│   ├── routing_decision.py       # Defines the Routing Decision Agent
│   └── ticket_classifier.py      # Defines the Ticket Classifier Agent
├── evaluations/                  # Directory for storing test results and evaluation metrics
│   ├── __init__.py               # Makes 'evaluations' a Python package
│   └── test_results/             # Directory where individual test case outputs are saved
│       ├── testcase_1.txt
│       ├── testcase_2.txt
│       └── ...
├── env/                          # Python virtual environment directory
├── __pycache__/                  # Python cache files (automatically generated)
├── ai_chat_history.txt           # Log of AI chat interactions, if implemented
└── requirements.txt              # Lists Python package dependencies
```


## 4. Setup and Installation

To set up and run this project, follow these steps:

### 4.1. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies and avoid conflicts with other Python projects.

1.  Open your terminal or command prompt in the project's root directory.
2.  Create the virtual environment:
    ```bash
    python -m venv env
    ```
3.  Activate the virtual environment:
    * On Windows:
        ```bash
        .\env\Scripts\activate
        ```
    * On macOS/Linux:
        ```bash
        source env/bin/activate
        ```

### 4.2. Install Dependencies

The project relies on `pydantic-ai` for agent orchestration and `python-dotenv` for environment variable management.

1.  Ensure your virtual environment is active.
2.  Install the required packages using `pip`:
    ```bash
    pip install -r requirements.txt
    ```
    (Your `requirements.txt` should contain `pydantic-ai` and `python-dotenv`).

### 4.3. Configure Mistral AI API Key

The agents utilize the Mistral AI model (`mistral-large-latest`). You need to provide your API key securely.

1.  Obtain your API key from your Mistral AI account.
2.  In the root directory of your project, create a file named `.env` (if it doesn't already exist).
3.  Add your Mistral API key to this file in the following format:
    ```
    MISTRAL_API_KEY=your_actual_mistral_api_key_here
    ```
    Replace `your_actual_mistral_api_key_here` with the key you obtained.

## 5. Usage

### 5.1. Running a Single Ticket Query (`main.py`)

The `main.py` file allows you to process a single customer support ticket, with outputs from both agents displayed directly in the terminal.

1.  **Modify Input:** Open `main.py` and locate the `sample_ticket` variable. You can directly edit the JSON string within the triple quotes to define your desired input ticket.
2.  **Execute:** Run the `main.py` file from your terminal (ensure your virtual environment is active):
    ```bash
    python main.py
    ```
    Alternatively, you can pass the ticket JSON directly as a command-line argument or from a file:

    * From File (recommended for longer inputs):
        Create a `.json` file (e.g., `my_ticket.json`) with your ticket's JSON content.
        ```bash
        python main.py --file my_ticket.json
        ```
3.  **Expected Output:** The terminal will display the raw output from the Ticket Classifier Agent, the combined prompt sent to the Routing Decision Agent, and finally, the output from the Routing Decision Agent.

### 5.2. Running Multiple Test Cases (`test.py`)

The `test.py` script is designed for automated evaluation, running a predefined set of test cases and saving the results to individual files.

1.  **Define Test Cases:** Open `test.py` and modify the `test_cases` list. Each element in this list should be a JSON string representing a customer support ticket.
2.  **Configure Output Directory:** The results will be saved in `evaluations/test_results/`. You can adjust this path by modifying the `results_base_dir` and `results_output_dir` variables within `test.py` if desired.
3.  **Execute:** Run the `test.py` file from your terminal (ensure your virtual environment is active):
    ```bash
    python test.py
    ```
4.  **Expected Output:**
    * The terminal will show progress messages for each test case.
    * For each test case, a `.txt` file (e.g., `testcase_1.txt`, `testcase_2.txt`) will be created in the `evaluations/test_results/` directory. Each file will contain:
        * The original input ticket.
        * The output from the Text Classifier Agent.
        * The output from the Routing Decision Agent.

## 6. Evaluation and Test Case Examples

The system has been evaluated using several test cases, demonstrating its ability to accurately classify tickets and make appropriate routing decisions. A crucial aspect of this system is its ability to correctly handle cases based on a combination of issue content, customer tier, and history. The inclusion of a 5-second `asyncio.sleep` after each agent call in batch testing (`test.py`) helps in managing API rate limits.
Here are examples from the test runs:

### Test Case 2: Minor UI Issue (Enterprise Customer)

This test case shows the system's ability to identify a low-severity issue, yet prioritize it due to the customer's enterprise tier and extensive history.

* **Test Case 2 Input:**
    ```json
    {
        "ticket_id": "SUP-002",
        "customer_tier": "enterprise",
        "subject": "Minor UI issue with dashboard",
        "message": "Hi team, just noticed the dashboard numbers are slightly misaligned on mobile view. It's a minor aesthetic issue, but could you please look into it when you have a moment?",
        "previous_tickets": 15,
        "monthly_revenue": 25000,
        "account_age_days": 730
    }
    ```
* **Text Classifier Agent Output:**
    ```json
    {
        "issue_type": "UI_problem",
        "severity_level": "low",
        "sentiment": "polite",
        "priority_score": 0.65
    }
    ```
* **Routing Decision Agent Output:**
    ```json
    {
        "assigned_team": "Frontend Development",
        "assigned_queue": "Standard Feature Requests",
        "recommended_SLA": "Within 4 hours",
        "flag_for_manager_review": true
    }
    ```
* **Analysis:** Despite being a "low" severity UI problem, the `priority_score` of 0.65 (influenced by "enterprise" tier and high `previous_tickets`) correctly routes it to "Frontend Development" with an accelerated "Within 4 hours" SLA, and even flags it for manager review, indicating the system recognizes the importance of maintaining service for high-value, long-standing customers.

### Test Case 5: Critical Security Vulnerability (Enterprise Customer)

This demonstrates the system's critical response capability for high-impact issues from top-tier customers.

* **Test Case 5 Input:**
    ```json
    {
        "ticket_id": "SUP-005",
        "customer_tier": "enterprise",
        "subject": "Urgent: Security vulnerability?",
        "message": "Our security team flagged that your API responses include internal server paths in error messages. This is a potential information disclosure vulnerability that needs immediate attention.",
        "previous_tickets": 20,
        "monthly_revenue": 50000,
        "account_age_days": 900
    }
    ```
* **Text Classifier Agent Output:**
    ```json
    {
        "issue_type": "security_issue",
        "severity_level": "critical",
        "sentiment": "neutral",
        "priority_score": 0.99
    }
    ```
* **Routing Decision Agent Output:**
    ```json
    {
        "assigned_team": "Security Team",
        "assigned_queue": "Premium Critical P1",
        "recommended_SLA": "Immediate attention (1-hour response)",
        "flag_for_manager_review": true
    }
    ```
* **Analysis:** The system correctly identified the "security_issue" with "critical" severity and a very high `priority_score` (0.99). This led to appropriate routing to the "Security Team" with an "Immediate attention (1-hour response)" SLA and a manager review flag, showcasing effective critical incident management.

### False Test Case (Low Priority, General Support)

This custom test case verifies the system's ability to appropriately de-prioritize tickets that are not core bugs or critical issues, even with a strong negative sentiment.

* **Input:**
    ```json
    {
        "ticket_id": "12345",
        "customer_tier": "free",
        "subject": "Your site is worst, it shows more price as compared to other sites.",
        "message": "Pricing high",
        "previous_tickets": 0,
        "monthly_revenue": 0,
        "account_age_days": 2
    }
    ```
* **Text Classifier Agent Output:**
    ```json
    {
        "issue_type": "other",
        "severity_level": "low",
        "sentiment": "angry",
        "priority_score": 0.1
    }
    ```
* **Routing Decision Agent Output:**
    ```json
    {
        "assigned_team": "General Support",
        "assigned_queue": "General Inquiry Queue",
        "recommended_SLA": "Within 48 hours",
        "flag_for_manager_review": false
    }
    ```
* **Analysis:** Despite the "angry" sentiment, the Ticket Classifier Agent correctly identifies the `issue_type` as "other" and `severity_level` as "low," resulting in a very low `priority_score` (0.1). Consequently, the Routing Decision Agent assigns it to "General Support" with a "Within 48 hours" SLA and no manager escalation. This demonstrates the system's robust prioritization logic, distinguishing between critical issues and general complaints, regardless of customer tone.

## 7. Customization and Extensibility

The modular design allows for easy customization and extension of the system:

* **Modifying Existing Agents:** You can adjust the behavior of the Ticket Classifier Agent or the Routing Decision Agent by editing their respective Python files located in the `agents/` directory (`agents/ticket_classifier.py` and `agents/routing_decision.py`). This includes refining their system prompts, adding new output categories, or changing decision-making logic.
* **Adding More Agents:** The `agents/` directory is designed to house additional specialized agents. For example, you could add an agent for:
    * **Sentiment Escalation:** A dedicated agent that flags tickets purely based on extreme negative sentiment, regardless of issue type.
    * **Knowledge Base Search:** An agent that, after classification, automatically searches a knowledge base for potential solutions and suggests them.
    * **Customer History Summarizer:** An agent that provides a concise summary of a customer's past interactions to the routing agent.
    * If new agents are added, you would need to manage their execution flow and data passing within the `chat` function in `main.py` accordingly.
