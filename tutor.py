import os
import asyncio
from agents import Agent, Runner, function_tool

# Set your OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OpenAI API key is not set. Please configure it in your environment.")

# Tool for solving math equations
@function_tool
def solve_equation(equation: str) -> str:
    """
    Solves a simple linear equation of the form 'ax + b = c'.
    """
    import sympy as sp
    x = sp.symbols('x')
    try:
        solution = sp.solve(sp.Eq(eval(equation.replace('=', '-(') + ')')), x)
        return f"The solution to the equation {equation} is x = {solution[0]}"
    except Exception as e:
        return f"Error solving equation: {str(e)}"

# Math Tutor Agent
math_tutor_agent = Agent(
    name="Math Tutor",
    instructions="You are a math tutor. Assist students with math problems, providing clear explanations.",
    tools=[solve_equation]
)

# History Tutor Agent
history_tutor_agent = Agent(
    name="History Tutor",
    instructions="You are a history tutor. Provide detailed and accurate information on historical events and figures.",
    # Add any history-specific tools here
)

# Triage Agent to route queries
triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You are an AI Tutor Assistant. Determine the subject of the student's question and "
        "route it to the appropriate tutor agent: Math Tutor or History Tutor."
    ),
    handoffs=[math_tutor_agent, history_tutor_agent]
)

# Function to run the triage agent
async def run_tutor_assistant():
    queries = [
        "Solve the equation 2*x + 3 = 7.",
        "Who was the first president of the United States?",
        "Explain the Pythagorean theorem.",
        "What caused the fall of the Roman Empire?"
    ]
    for query in queries:
        result = await Runner.run(triage_agent, query)
        print(f"Query: {query}\nResponse: {result.final_output}\n{'-'*50}\n")

# Execute the assistant
if __name__ == "__main__":
    asyncio.run(run_tutor_assistant())
