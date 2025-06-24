import os
import json
import asyncio
import time
from main import chat 

test_cases = [
    # Test Case 1: Free customer, angry, product broken
    """{
    "ticket_id": "SUP-001",
    "customer_tier": "free",
    "subject": "This product is completely broken!!!",
    "message": "Nothing works! I can't even log in. This is the worst software I've ever used. I'm extremely frustrated and need this fixed NOW.",
    "previous_tickets": 0,
    "monthly_revenue": 0,
    "account_age_days": 2
    }""",
    # Test Case 2: Enterprise customer, minor UI issue
    """{
    "ticket_id": "SUP-002",
    "customer_tier": "enterprise",
    "subject": "Minor UI issue with dashboard",
    "message": "Hi team, just noticed the dashboard numbers are slightly misaligned on mobile view. It's a minor aesthetic issue, but could you please look into it when you have a moment?",
    "previous_tickets": 15,
    "monthly_revenue": 25000,
    "account_age_days": 730
    }""",
    # Test Case 3: Premium customer, feature request (bulk export)
    """{
    "ticket_id": "SUP-003",
    "customer_tier": "premium",
    "subject": "Feature Request: Bulk export",
    "message": "We need bulk export functionality for our quarterly reports. Currently exporting our data line by line is very time-consuming. A bulk export option would be a huge time-saver.",
    "previous_tickets": 5,
    "monthly_revenue": 5000,
    "account_age_days": 400
    }""",
    # Test Case 4: Premium customer, API rate limits unclear
    """{
    "ticket_id": "SUP-004",
    "customer_tier": "premium",
    "subject": "API rate limits unclear",
    "message": "Getting rate limited but documentation says we should have 1000 requests/hour. We're well below that threshold but still hitting limits. Could you clarify our actual rate limits and investigate if there's an issue?",
    "previous_tickets": 8,
    "monthly_revenue": 3000,
    "account_age_days": 180
    }""",
    # Test Case 5: Enterprise customer, urgent security vulnerability
    """{
    "ticket_id": "SUP-005",
    "customer_tier": "enterprise",
    "subject": "Urgent: Security vulnerability?",
    "message": "Our security team flagged that your API responses include internal server paths in error messages. This is a potential information disclosure vulnerability that needs immediate attention.",
    "previous_tickets": 20,
    "monthly_revenue": 50000,
    "account_age_days": 900
    }"""
]

async def run_all_tests():
    # Define the directory where results will be saved.
    results_base_dir = "evaluations"
    results_output_dir = os.path.join(results_base_dir, "test_results")
    
    os.makedirs(results_output_dir, exist_ok=True) 

    for i, sample_ticket_input in enumerate(test_cases):
        test_case_num = i + 1
        output_filename = os.path.join(results_output_dir, f"testcase_{test_case_num}.txt")
        
        print(f"\n--- Processing Test Case {test_case_num} ---")
        
        classifier_output, router_output = await chat(sample_ticket_input)

        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(f"Test Case {test_case_num} Input:\n")
            f.write(json.dumps(json.loads(sample_ticket_input), indent=4))
            f.write("\n\n---\n\n")
            f.write("Text Classifier Agent Output:\n")
            f.write(classifier_output)
            f.write("\n\n---\n\n")
            f.write("Routing Decision Agent Output:\n")
            f.write(router_output)
            f.write("\n")

        print(f"Results for Test Case {test_case_num} saved to: {output_filename}")
        print(f"--- Finished Test Case {test_case_num}. ---\n")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
    
    