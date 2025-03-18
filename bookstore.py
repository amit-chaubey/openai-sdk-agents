# -*- coding: utf-8 -*-
"""Bookstore Inventory Management System"""

import os
import asyncio
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setting OpenAI API Key
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OpenAI API key is not set. Please configure it in your .env file.")
else:
    os.environ["OPENAI_API_KEY"] = openai_api_key  # Make sure to set the environment variable

# Bookstore Inventory Dictionary
BOOK_CATALOG = {
    "fiction": {
        "1984": 10.99,
        "To Kill a Mockingbird": 9.49,
        "The Great Gatsby": 8.99,
        "Brave New World": 11.25,
        "The Catcher in the Rye": 10.50,
    },
    "non_fiction": {
        "Sapiens": 14.99,
        "Educated": 13.75,
        "Atomic Habits": 16.25,
        "The Power of Habit": 12.50,
        "Thinking, Fast and Slow": 17.99,
    },
}

DISCOUNTS = {
    "bulk": "Buy 2, Get 1 Free on select Fiction books",
    "threshold": "10% Discount on purchases above $50",
    "loyalty": "Loyalty Members get an extra 5% off on every order",
}

# Function to Calculate Tax - fixed to remove default value in schema
@function_tool
def calculate_tax(order_total: float, tax_rate: float = None) -> str:
    """Calculate tax and total price with tax.
    
    Args:
        order_total: The total amount before tax
        tax_rate: The tax rate as a decimal (e.g., 0.08 for 8%)
    
    Returns:
        A string with the tax amount and total with tax
    """
    # Handle default inside function body
    if tax_rate is None:
        tax_rate = 0.08
        
    tax_amount = order_total * tax_rate
    total_with_tax = order_total + tax_amount
    return f"Tax: ${tax_amount:.2f}, Total with Tax: ${total_with_tax:.2f}"

@function_tool
def get_book_price(title: str) -> str:
    """Get the price of a book by title.
    
    Args:
        title: The title of the book
        
    Returns:
        A string with the price and category
    """
    for category, books in BOOK_CATALOG.items():
        if title in books:
            return f"${books[title]:.2f} ({category})"
    return "Book not found in catalog"

@function_tool
def list_available_discounts() -> str:
    """List all available discounts.
    
    Returns:
        A string with all discount descriptions
    """
    result = "Available discounts:\n"
    for discount_name, discount_description in DISCOUNTS.items():
        result += f"- {discount_description}\n"
    return result

# Creating the Bookstore Agent
bookstore_agent = Agent(
    name="Bookstore Assistant",
    instructions="""You are a bookstore assistant. Help customers with book inquiries, pricing, and discounts.
You have access to the book catalog with the following categories:
- Fiction: 1984, To Kill a Mockingbird, The Great Gatsby, Brave New World, The Catcher in the Rye
- Non-fiction: Sapiens, Educated, Atomic Habits, The Power of Habit, Thinking, Fast and Slow

Use the get_book_price function to check book prices and list_available_discounts to provide discount information.
""",
    model="gpt-4o",
    tools=[calculate_tax, get_book_price, list_available_discounts]
)

# Function to Run the Agent Asynchronously
async def run_bookstore_agent():
    queries = [
        "How much is '1984'?",
        "Do you have any discounts on Fiction books?",
        "How much would be the total with tax for '1984' and 'Sapiens'?"
    ]
    for query in queries:
        print(f"\nQuery: {query}")
        result = await Runner.run(bookstore_agent, query)
        print(f"Response: {result.final_output}")

# Orchestrator Agent for Handling Multiple Requests
orchestrator_agent = Agent(
    name="Bookstore Orchestrator",
    instructions="Smart Assistant to manage book orders, tax calculations, and discounts.",
    tools=[bookstore_agent.as_tool("bookstore_assistant", "Find book prices and discounts"), calculate_tax],
)

async def run_orchestrator():
    queries = [
        "How much is 'Atomic Habits' and 'Sapiens' with tax?",
        "Do you have any books under $10?",
        "If I buy 3 books, do I get any discount?"
    ]
    for query in queries:
        print(f"\nQuery: {query}")
        result = await Runner.run(orchestrator_agent, query)
        print(f"Response: {result.final_output}")

async def main():
    print("===== Running Bookstore Agent =====")
    await run_bookstore_agent()
    print("\n===== Running Orchestrator Agent =====")
    await run_orchestrator()

if __name__ == "__main__":
    asyncio.run(main())