from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
import json

# This module handles the generation of career insight graphs using LangGraph

def generate_insight_graph(career_path, llm):
    """
    Generate a career path progression graph using LangGraph.
    
    Args:
        career_path (str): The career path to analyze
        llm: The initialized language model
    
    Returns:
        str: Markdown representation of the career progression
    """
    # Define the career analysis workflow using LangGraph
    
    # 1. Define the state
    class CareerState(dict):
        """The state of the career analysis workflow."""
        career: str
        entry_roles: list = None
        mid_roles: list = None
        senior_roles: list = None
        skills_progression: dict = None
        education_requirements: dict = None
        final_markdown: str = None

    # 2. Define the nodes (steps in our workflow)
    
    # First node: Analyze entry-level positions
    def analyze_entry_level(state):
        prompt = ChatPromptTemplate.from_template(
            """You are a career path analyst. Given the career path {career}, 
            identify 3-4 common entry-level positions and their core responsibilities.
            Return the result as a JSON list with 'title' and 'responsibilities' keys for each position."""
        )
        
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"career": state["career"]})
        
        # Parse the result as JSON
        try:
            entry_roles = json.loads(result)
        except:
            # Fallback if JSON parsing fails
            entry_roles = [{"title": f"Entry-level {state['career']}", "responsibilities": ["Learning fundamentals", "Assisting with projects", "Building core skills"]}]
        
        state["entry_roles"] = entry_roles
        return state

    # Second node: Analyze mid-level positions
    def analyze_mid_level(state):
        prompt = ChatPromptTemplate.from_template(
            """You are a career path analyst. Given the career path {career}, 
            identify 3-4 common mid-level positions and their core responsibilities.
            Return the result as a JSON list with 'title' and 'responsibilities' keys for each position."""
        )
        
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"career": state["career"]})
        
        # Parse the result as JSON
        try:
            mid_roles = json.loads(result)
        except:
            # Fallback if JSON parsing fails
            mid_roles = [{"title": f"Mid-level {state['career']}", "responsibilities": ["Leading small projects", "Specialized knowledge", "Mentoring juniors"]}]
        
        state["mid_roles"] = mid_roles
        return state

    # Third node: Analyze senior-level positions
    def analyze_senior_level(state):
        prompt = ChatPromptTemplate.from_template(
            """You are a career path analyst. Given the career path {career}, 
            identify 3-4 common senior-level positions and their core responsibilities.
            Return the result as a JSON list with 'title' and 'responsibilities' keys for each position."""
        )
        
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"career": state["career"]})
        
        # Parse the result as JSON
        try:
            senior_roles = json.loads(result)
        except:
            # Fallback if JSON parsing fails
            senior_roles = [{"title": f"Senior {state['career']}", "responsibilities": ["Strategic planning", "Department leadership", "High-level decision making"]}]
        
        state["senior_roles"] = senior_roles
        return state

    # Fourth node: Analyze skills progression across career levels
    def analyze_skills_progression(state):
        prompt = ChatPromptTemplate.from_template(
            """You are a career skills analyst. Given the career path {career}, 
            analyze how skills should develop as one progresses from entry-level to senior positions.
            Focus on technical skills, soft skills, and domain knowledge. Return the result as a JSON
            object with 'entry', 'mid', and 'senior' keys, each containing a list of skills."""
        )
        
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"career": state["career"]})
        
        # Parse the result as JSON
        try:
            skills_progression = json.loads(result)
        except:
            # Fallback if JSON parsing fails
            skills_progression = {
                "entry": ["Fundamental knowledge", "Basic technical skills", "Learning mindset"],
                "mid": ["Advanced technical skills", "Project management", "Mentoring"],
                "senior": ["Strategic thinking", "Leadership", "Business acumen"]
            }
        
        state["skills_progression"] = skills_progression
        return state

    # Fifth node: Generate final markdown representation of the career path
    def generate_markdown(state):
        entry_roles = state.get("entry_roles", [])
        mid_roles = state.get("mid_roles", [])
        senior_roles = state.get("senior_roles", [])
        skills = state.get("skills_progression", {})
        
        # Build markdown career progression
        markdown = f"## Career Progression Path for {state['career']}\n\n"
        
        # Entry level section
        markdown += "### Entry Level\n"
        for role in entry_roles:
            markdown += f"**{role.get('title', 'Entry Role')}**\n"
            responsibilities = role.get('responsibilities', [])
            if responsibilities:
                markdown += "Responsibilities:\n"
                for resp in responsibilities:
                    markdown += f"- {resp}\n"
            markdown += "\n"
        
        # Skills at entry level
        entry_skills = skills.get("entry", [])
        if entry_skills:
            markdown += "**Key Skills at This Level:**\n"
            for skill in entry_skills:
                markdown += f"- {skill}\n"
            markdown += "\n"
        
        # Mid level section
        markdown += "### Mid-Career Level\n"
        for role in mid_roles:
            markdown += f"**{role.get('title', 'Mid-Level Role')}**\n"
            responsibilities = role.get('responsibilities', [])
            if responsibilities:
                markdown += "Responsibilities:\n"
                for resp in responsibilities:
                    markdown += f"- {resp}\n"
            markdown += "\n"
        
        # Skills at mid level
        mid_skills = skills.get("mid", [])
        if mid_skills:
            markdown += "**Key Skills at This Level:**\n"
            for skill in mid_skills:
                markdown += f"- {skill}\n"
            markdown += "\n"
        
        # Senior level section
        markdown += "### Senior Level\n"
        for role in senior_roles:
            markdown += f"**{role.get('title', 'Senior Role')}**\n"
            responsibilities = role.get('responsibilities', [])
            if responsibilities:
                markdown += "Responsibilities:\n"
                for resp in responsibilities:
                    markdown += f"- {resp}\n"
            markdown += "\n"
        
        # Skills at senior level
        senior_skills = skills.get("senior", [])
        if senior_skills:
            markdown += "**Key Skills at This Level:**\n"
            for skill in senior_skills:
                markdown += f"- {skill}\n"
            markdown += "\n"
        
        # Add advancement tips
        markdown += "### Tips for Advancement\n"
        markdown += "1. **Continuous Learning**: Stay updated with industry trends and technologies\n"
        markdown += f"2. **Networking**: Connect with other professionals in {state['career']}\n"
        markdown += "3. **Projects**: Build a portfolio of successful projects and achievements\n"
        markdown += "4. **Mentorship**: Find mentors and become a mentor as you advance\n"
        markdown += "5. **Certifications**: Obtain relevant certifications to validate your expertise\n"
        
        state["final_markdown"] = markdown
        return state

    # 3. Define the graph
    workflow = StateGraph(CareerState)
    
    # Add nodes
    workflow.add_node("analyze_entry_level", analyze_entry_level)
    workflow.add_node("analyze_mid_level", analyze_mid_level)
    workflow.add_node("analyze_senior_level", analyze_senior_level)
    workflow.add_node("analyze_skills_progression", analyze_skills_progression)
    workflow.add_node("generate_markdown", generate_markdown)
    
    # Add edges
    workflow.add_edge("analyze_entry_level", "analyze_mid_level")
    workflow.add_edge("analyze_mid_level", "analyze_senior_level")
    workflow.add_edge("analyze_senior_level", "analyze_skills_progression")
    workflow.add_edge("analyze_skills_progression", "generate_markdown")
    
    # Set entry and end nodes
    workflow.set_entry_point("analyze_entry_level")
    workflow.set_finish_point("generate_markdown")
    
    # 4. Compile the graph
    app = workflow.compile()
    
    # 5. Run the graph
    try:
        result = app.invoke({"career": career_path})
        return result["final_markdown"]
    except Exception as e:
        print(f"Error generating career graph: {e}")
        return f"## Career Progression for {career_path}\n\nUnable to generate the full career progression graph at this time. Please try again later."
