import os
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
load_dotenv()

def initialize_llm():
    """
    Initialize and return the LLM client using Groq API.
    Falls back to a default model if API key is not available.
    """
    # Get API key from environment variables
    api_key = os.getenv("GROQ_API_KEY", "")
    
    # If no API key is available, print a warning
    if not api_key:
        print("Warning: GROQ_API_KEY not found in environment variables. Using default model.")
        
    # Initialize the LLM - using Groq's Llama 3 model
    llm = ChatGroq(
        api_key=api_key,
        model_name="llama3-8b-8192",  # Using Llama 3 model
        temperature=0.5,
        max_tokens=4096,
    )
    
    return llm

def get_career_advice(user_question, context, llm):
    """
    Generate career advice based on user questions and context.
    
    Args:
        user_question (str): The user's question about careers
        context (dict): Additional context like education, experience, interests
        llm: The initialized language model
    
    Returns:
        str: The generated career advice
    """
    # Create system message with career advisor persona
    system_template = """You are CareerCompass AI, an expert career advisor with extensive knowledge about job markets, 
    career paths, required skills, education requirements, and salary expectations across various industries.
    
    Your goal is to provide accurate, helpful, and tailored career guidance based on the user's questions.
    
    When providing advice:
    1. Be specific and actionable
    2. Base your answers on current job market trends
    3. Consider the user's education level, experience, and interests when relevant
    4. Provide balanced perspectives on career options
    5. Be encouraging but realistic about requirements and expectations
    6. Format your responses with clear headings and bullet points when appropriate
    
    Avoid:
    - Giving generic advice that doesn't address the specific question
    - Making up statistics or data you're unsure about
    - Overwhelming the user with too much information
    
    User context information:
    - Education Level: {education_level}
    - Experience Level: {experience_level}
    - Interests: {interests}
    - Career being explored: {selected_career}
    """
    
    # Format system message with available context
    education_level = context.get('education_level', 'Not specified')
    experience_level = context.get('experience_level', 'Not specified')
    interests = ', '.join(context.get('interests', [])) if context.get('interests') else 'Not specified'
    selected_career = context.get('selected_career', 'Not specified')
    
    system_message = SystemMessage(
        content=system_template.format(
            education_level=education_level,
            experience_level=experience_level,
            interests=interests,
            selected_career=selected_career
        )
    )
    
    # Create human message with user question
    human_message = HumanMessage(content=user_question)
    
    # Generate response using the LLM
    try:
        messages = [system_message, human_message]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        print(f"Error generating career advice: {e}")
        return "I'm sorry, I encountered an error while generating career advice. Please try again or rephrase your question."
