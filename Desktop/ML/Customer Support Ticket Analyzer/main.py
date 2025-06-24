import os
import json
import sys
import asyncio
from dotenv import load_dotenv
from agents.routing_decision import routing_decision_agent
from agents.ticket_classifier import ticket_classifier_agent
import time

load_dotenv()

os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")


async def chat(prompt):
    classification_response = await ticket_classifier_agent.run(prompt)
    raw_classifier_output = classification_response.output # Always capture raw classifier output
    time.sleep(5)
    # These prints are for when main.py is run directly
    print("\n--- Output from Ticket Classifier Agent (raw): ---")
    print(raw_classifier_output)
    print("---------------------------------------------------\n")

    try:
        original_ticket_data = json.loads(prompt)
    except json.JSONDecodeError:
        print("Error: The initial prompt is not a valid JSON string.")
        # Return a tuple (error_message_for_classifier, error_message_for_router)
        return "ERROR: Invalid initial ticket format for classifier input", "ERROR: Invalid initial ticket format, could not proceed to router"

    raw_classification_output_for_parsing = raw_classifier_output

    if raw_classification_output_for_parsing.strip().startswith('```json') and \
       raw_classification_output_for_parsing.strip().endswith('```'):
        json_string_to_parse = raw_classification_output_for_parsing.strip()[len('```json'):-len('```')].strip()
    else:
        json_string_to_parse = raw_classification_output_for_parsing.strip()

    try:
        classification_data = json.loads(json_string_to_parse)
    except json.JSONDecodeError as e:
        error_msg = (f"ERROR: Classifier agent output is not valid JSON after stripping Markdown. "
                     f"Raw output was: '{raw_classification_output_for_parsing}' "
                     f"Attempted to parse: '{json_string_to_parse}' "
                     f"Error details: {e}")
        print(error_msg) # Print error to console
        # Return a tuple (classifier_output, error_message_for_router)
        return raw_classifier_output, error_msg # Return raw output and specific error for router

    combined_data = original_ticket_data.copy()
    combined_data["classification"] = classification_data

    prompt_for_routing_agent = json.dumps(combined_data, indent=4)

    print("\n--- Prompt being sent to Routing Decision Agent: ---")
    print(prompt_for_routing_agent)
    print("-----------------------------------------------------\n")

    routing_response = await routing_decision_agent.run(prompt_for_routing_agent)
    final_router_output = routing_response.output
    time.sleep(5)

    return raw_classifier_output, final_router_output

async def main():
    # sample_ticket = """{
    #     "ticket_id": "12345",
    #     "customer_tier": "premium",
    #     "subject": "The page is not working in mobile view, the images are going out of screen",
    #     "message": "Hi, our production system has been failing",
    #     "previous_tickets": 3,
    #     "monthly_revenue": 5000,
    #     "account_age_days": 450
    # }"""
    sample_ticket = """{
        "ticket_id": "12345",
        "customer_tier": "free",
        "subject": "Your site is worst, it shows more price as compared to other sites.",
        "message": "Pricing high",
        "previous_tickets": 0,
        "monthly_revenue": 0,
        "account_age_days": 2
    }"""

    print("Starting ticket processing...\n")
    final_routing_output = await chat(sample_ticket)

    print("\n--- Final Routing Decision Output: ---")
    print(final_routing_output)
    print("--------------------------------------\n")

if __name__ == "__main__":
    asyncio.run(main())