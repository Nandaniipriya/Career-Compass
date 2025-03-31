import pandas as pd

def get_personality_types():
    """
    Returns a list of common personality assessment types.
    """
    personality_types = {
        "Work Style": [
            "Analytical", 
            "Creative", 
            "Detail-oriented", 
            "Independent", 
            "Collaborative", 
            "Leadership-oriented",
            "Supportive"
        ],
        "Work Environment": [
            "Fast-paced", 
            "Structured", 
            "Flexible", 
            "Competitive", 
            "Collaborative", 
            "Remote-friendly",
            "Office-based"
        ],
        "Communication Style": [
            "Direct", 
            "Diplomatic", 
            "Expressive", 
            "Reserved", 
            "Written", 
            "Verbal"
        ],
        "Decision Making": [
            "Data-driven", 
            "Intuitive", 
            "Consultative", 
            "Decisive", 
            "Cautious", 
            "Risk-taking"
        ],
        "Values": [
            "Work-life balance", 
            "Career advancement", 
            "Helping others", 
            "Innovation", 
            "Stability", 
            "Recognition",
            "Autonomy"
        ]
    }
    
    return personality_types

def get_career_matches_by_personality(personality_traits):
    """
    Returns career matches based on selected personality traits.
    
    Args:
        personality_traits (dict): Dictionary of selected traits by category
        
    Returns:
        dict: Career matches and reasons for the match
    """
    # Create mapping of personality traits to career fields
    trait_to_career_mapping = {
        # Work Style traits
        "Analytical": ["Data Scientist", "Financial Analyst", "Research Scientist", "Cybersecurity Specialist"],
        "Creative": ["UX/UI Designer", "Content Creator", "Graphic Designer", "Marketing Specialist"],
        "Detail-oriented": ["Software Engineer", "Accountant", "Quality Assurance Specialist", "Project Manager"],
        "Independent": ["Freelance Writer", "Consultant", "Researcher", "Entrepreneur"],
        "Collaborative": ["Product Manager", "Team Lead", "Human Resources Manager", "Event Coordinator"],
        "Leadership-oriented": ["Project Manager", "Executive", "Department Head", "Business Owner"],
        "Supportive": ["Nurse Practitioner", "Teacher", "Human Resources Specialist", "Customer Support Manager"],
        
        # Work Environment traits
        "Fast-paced": ["Digital Marketer", "Journalist", "Emergency Medical Technician", "Startup Employee"],
        "Structured": ["Accountant", "Civil Engineer", "Legal Professional", "Operations Manager"],
        "Flexible": ["Freelancer", "Remote Worker", "Content Creator", "Consultant"],
        "Competitive": ["Sales Representative", "Investment Banker", "Management Consultant", "Business Development"],
        "Collaborative": ["Team Manager", "Agile Coach", "Educational Administrator", "Non-profit Coordinator"],
        "Remote-friendly": ["Software Developer", "Digital Marketer", "Virtual Assistant", "Online Teacher"],
        "Office-based": ["Administrative Assistant", "Executive", "Corporate Lawyer", "Human Resources Manager"],
        
        # Communication Style traits
        "Direct": ["Sales Manager", "Executive", "Project Manager", "Emergency Services"],
        "Diplomatic": ["Human Resources", "Mediator", "Public Relations", "Customer Success Manager"],
        "Expressive": ["Marketing Manager", "Teacher", "Sales Representative", "Public Speaker"],
        "Reserved": ["Data Analyst", "Researcher", "Accountant", "Software Developer"],
        "Written": ["Content Writer", "Editor", "Technical Writer", "Legal Professional"],
        "Verbal": ["Sales Representative", "Counselor", "Public Relations", "Teacher"],
        
        # Decision Making traits
        "Data-driven": ["Data Scientist", "Business Analyst", "Research Scientist", "Financial Analyst"],
        "Intuitive": ["Entrepreneur", "Creative Director", "Executive", "Counselor"],
        "Consultative": ["Management Consultant", "Counselor", "Team Leader", "Project Manager"],
        "Decisive": ["Emergency Medical Professional", "Executive", "Military Officer", "Project Manager"],
        "Cautious": ["Quality Assurance Specialist", "Risk Analyst", "Safety Officer", "Compliance Manager"],
        "Risk-taking": ["Entrepreneur", "Venture Capitalist", "Startup Founder", "Investment Banker"],
        
        # Values traits
        "Work-life balance": ["Government Employee", "Teacher", "Corporate Positions with flex time", "Remote Worker"],
        "Career advancement": ["Management Consultant", "Corporate Executive", "Sales Representative", "Tech Industry Professional"],
        "Helping others": ["Nurse Practitioner", "Social Worker", "Teacher", "Non-profit Employee"],
        "Innovation": ["Research Scientist", "Product Manager", "Software Engineer", "Startup Employee"],
        "Stability": ["Government Employee", "Accountant", "Healthcare Professional", "Engineer"],
        "Recognition": ["Sales Representative", "Performer", "Public Relations", "Marketing"],
        "Autonomy": ["Freelancer", "Consultant", "Research Scientist", "Entrepreneur"]
    }
    
    # Process personality traits to find matching careers
    career_matches = {}
    match_reasons = {}
    
    for category, traits in personality_traits.items():
        for trait in traits:
            if trait in trait_to_career_mapping:
                for career in trait_to_career_mapping[trait]:
                    if career not in career_matches:
                        career_matches[career] = 0
                        match_reasons[career] = []
                    
                    career_matches[career] += 1
                    match_reasons[career].append(f"{trait} ({category})")
    
    # Sort careers by match strength
    sorted_careers = sorted(career_matches.items(), key=lambda x: x[1], reverse=True)
    
    # Prepare final results with top matches and reasons
    results = []
    for career, strength in sorted_careers[:10]:  # Top 10 matches
        results.append({
            "career": career,
            "match_strength": strength,
            "reasons": match_reasons[career]
        })
    
    return results

def analyze_resume(resume_text, job_description="", llm=None):
    """
    Analyzes a resume against job requirements or provides general feedback.
    
    Args:
        resume_text (str): The text content of the resume
        job_description (str): Optional job description to compare against
        llm: Language model instance for analysis
    
    Returns:
        dict: Analysis results with feedback and suggestions
    """
    if not llm:
        return {
            "score": None,
            "strengths": ["Unable to analyze without LLM connection"],
            "weaknesses": ["Please ensure your LLM service is properly connected"],
            "suggestions": ["Try again after checking your API connection"],
            "keyword_matches": []
        }
    
    from langchain_core.prompts import ChatPromptTemplate
    
    if job_description:
        # Analyze resume against specific job description
        prompt = ChatPromptTemplate.from_template(
            """As an expert resume analyst, evaluate the following resume against the provided job description.
            
            Resume:
            {resume_text}
            
            Job Description:
            {job_description}
            
            Provide your analysis in the following JSON format:
            {{
                "score": <number between 1-10 representing match strength>,
                "strengths": [<list of 3-5 resume strengths related to the job>],
                "weaknesses": [<list of 3-5 areas for improvement>],
                "suggestions": [<list of 3-5 specific improvement suggestions>],
                "keyword_matches": [<list of important keywords from job description found in resume>]
            }}
            
            Return ONLY the JSON with no other text."""
        )
        
        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.messages import HumanMessage, SystemMessage
            import json
            
            system_message = SystemMessage(content="You are an expert resume analyzer that provides detailed, actionable feedback.")
            human_message = HumanMessage(content=prompt.format(resume_text=resume_text, job_description=job_description))
            
            result = llm.invoke([system_message, human_message])
            
            # Try to extract JSON from the response
            result_text = result.content
            # Find JSON in the response if it's embedded in other text
            try:
                import re
                json_match = re.search(r'({.*})', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(1)
                analysis = json.loads(result_text)
            except:
                # Fallback if JSON parsing fails
                analysis = {
                    "score": 5,
                    "strengths": ["Relevant experience identified", "Some matching skills found"],
                    "weaknesses": ["Resume could be better tailored to this specific job"],
                    "suggestions": ["Add more keywords from the job description", "Quantify achievements"],
                    "keyword_matches": ["Some relevant terms detected"]
                }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing resume: {e}")
            return {
                "score": 5,
                "strengths": ["Error during analysis"],
                "weaknesses": ["Could not complete full analysis"],
                "suggestions": ["Try again or check your input"],
                "keyword_matches": []
            }
    else:
        # General resume analysis
        prompt = ChatPromptTemplate.from_template(
            """As an expert resume analyst, evaluate the following resume and provide general feedback.
            
            Resume:
            {resume_text}
            
            Provide your analysis in the following JSON format:
            {{
                "strengths": [<list of 3-5 resume strengths>],
                "weaknesses": [<list of 3-5 areas for improvement>],
                "suggestions": [<list of 3-5 specific improvement suggestions>],
                "best_career_matches": [<list of 3-5 career paths that might match this resume>]
            }}
            
            Return ONLY the JSON with no other text."""
        )
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            import json
            
            system_message = SystemMessage(content="You are an expert resume analyzer that provides detailed, actionable feedback.")
            human_message = HumanMessage(content=prompt.format(resume_text=resume_text))
            
            result = llm.invoke([system_message, human_message])
            
            # Try to extract JSON from the response
            result_text = result.content
            # Find JSON in the response if it's embedded in other text
            try:
                import re
                json_match = re.search(r'({.*})', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(1)
                analysis = json.loads(result_text)
            except:
                # Fallback if JSON parsing fails
                analysis = {
                    "strengths": ["Experience clearly presented", "Education section well-structured"],
                    "weaknesses": ["Could use more quantifiable achievements", "Skills section could be expanded"],
                    "suggestions": ["Add metrics to achievements", "Tailor resume to specific positions", "Consider adding a brief summary"],
                    "best_career_matches": ["Based on resume content"]
                }
                
            return analysis
            
        except Exception as e:
            print(f"Error analyzing resume: {e}")
            return {
                "strengths": ["Error during analysis"],
                "weaknesses": ["Could not complete full analysis"],
                "suggestions": ["Try again or check your input"],
                "best_career_matches": []
            }

def generate_cover_letter(resume_text, job_description, personal_info, llm=None):
    """
    Generates a cover letter based on resume, job description and personal info.
    
    Args:
        resume_text (str): The text content of the resume
        job_description (str): Job description to tailor cover letter to
        personal_info (dict): Personal information including name, contact info
        llm: Language model instance for generation
    
    Returns:
        str: Generated cover letter text
    """
    if not llm:
        return "Unable to generate cover letter. Please ensure your LLM service is properly connected."
    
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    
    prompt = ChatPromptTemplate.from_template(
        """As an expert career advisor, generate a professional cover letter based on the following information:
        
        Personal Information:
        {personal_info}
        
        Resume Highlights:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Create a compelling, concise cover letter that highlights the most relevant skills and experiences from the resume that match the job description. 
        The cover letter should be professionally formatted, include a proper greeting and closing, and be about 250-350 words.
        DO NOT make up information not included in the resume. Focus on matching real experiences to job requirements.
        """
    )
    
    try:
        system_message = SystemMessage(content="You are an expert cover letter writer who creates compelling, tailored content that helps candidates stand out.")
        human_message = HumanMessage(content=prompt.format(
            personal_info=personal_info,
            resume_text=resume_text,
            job_description=job_description
        ))
        
        result = llm.invoke([system_message, human_message])
        return result.content
        
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return "An error occurred while generating your cover letter. Please try again."

def create_learning_plan(current_skills, target_career, experience_level, llm=None):
    """
    Creates a personalized learning plan based on skill gaps for a target career.
    
    Args:
        current_skills (list): List of current skills the user has
        target_career (str): The target career path
        experience_level (str): Current experience level
        llm: Language model instance for analysis
    
    Returns:
        dict: Learning plan with courses, resources and timeline
    """
    if not llm:
        return {
            "skill_gaps": ["Unable to identify skill gaps without LLM connection"],
            "recommended_courses": [],
            "learning_resources": [],
            "timeline": "Please ensure your LLM service is properly connected"
        }
    
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    import json
    
    prompt = ChatPromptTemplate.from_template(
        """As a career development specialist, create a personalized learning plan for someone transitioning to or advancing in the field of {target_career}.
        
        Current Skills: {current_skills}
        Current Experience Level: {experience_level}
        Target Career: {target_career}
        
        Provide your learning plan in the following JSON format:
        {{
            "skill_gaps": [<list of 3-5 key skills the person needs to develop>],
            "recommended_courses": [
                {{
                    "name": <course name>,
                    "provider": <provider name, e.g. Coursera, Udemy, etc.>,
                    "description": <brief description>,
                    "difficulty": <"Beginner", "Intermediate", or "Advanced">,
                    "time_commitment": <estimated time to complete>
                }}
                ... (3-5 courses)
            ],
            "learning_resources": [<list of 3-5 books, websites, or other resources>],
            "certification_paths": [<list of relevant certifications if applicable>],
            "timeline": <suggested timeline for completing the learning plan, e.g. "3-6 months">
        }}
        
        Return ONLY the JSON with no other text."""
    )
    
    try:
        system_message = SystemMessage(content="You are an expert career development advisor who creates practical, tailored learning plans.")
        human_message = HumanMessage(content=prompt.format(
            current_skills=", ".join(current_skills),
            target_career=target_career,
            experience_level=experience_level
        ))
        
        result = llm.invoke([system_message, human_message])
        
        # Try to extract JSON from the response
        result_text = result.content
        # Find JSON in the response if it's embedded in other text
        try:
            import re
            json_match = re.search(r'({.*})', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            learning_plan = json.loads(result_text)
        except:
            # Fallback if JSON parsing fails
            learning_plan = {
                "skill_gaps": ["Technical skill relevant to the field", "Industry-specific knowledge", "Project management"],
                "recommended_courses": [
                    {
                        "name": "Introduction to the Field",
                        "provider": "Coursera",
                        "description": "A beginner course covering fundamentals",
                        "difficulty": "Beginner",
                        "time_commitment": "4-6 weeks"
                    },
                    {
                        "name": "Advanced Techniques",
                        "provider": "Udemy",
                        "description": "More in-depth knowledge and practical skills",
                        "difficulty": "Intermediate",
                        "time_commitment": "8-10 weeks"
                    }
                ],
                "learning_resources": ["Industry standard textbook", "Professional association website", "Relevant online community"],
                "certification_paths": ["Entry-level certification", "Professional certification"],
                "timeline": "6-12 months depending on current experience"
            }
        
        return learning_plan
        
    except Exception as e:
        print(f"Error creating learning plan: {e}")
        return {
            "skill_gaps": ["Error during analysis"],
            "recommended_courses": [{"name": "Could not generate recommendations", "provider": "", "description": "", "difficulty": "", "time_commitment": ""}],
            "learning_resources": ["Try again later"],
            "certification_paths": [],
            "timeline": "Unable to estimate timeline"
        }

def get_company_culture_data(company_name, llm=None):
    """
    Returns information about company culture based on company name.
    
    Args:
        company_name (str): Name of the company
        llm: Language model instance for generation
        
    Returns:
        dict: Company culture information
    """
    if not llm:
        return {
            "overview": "Unable to retrieve company information without LLM connection",
            "values": [],
            "work_environment": "",
            "work_life_balance": "",
            "growth_opportunities": "",
            "interview_tips": []
        }
    
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    import json
    
    prompt = ChatPromptTemplate.from_template(
        """As a company culture expert, provide information about the culture at {company_name}.
        
        Provide your analysis in the following JSON format:
        {{
            "overview": <brief overview of the company culture>,
            "values": [<list of 3-5 core company values>],
            "work_environment": <description of typical work environment>,
            "work_life_balance": <assessment of work-life balance>,
            "growth_opportunities": <description of career growth opportunities>,
            "interview_tips": [<list of 3-5 tips for interviewing at this company>]
        }}
        
        Based on your knowledge, provide the most accurate information about {company_name}'s culture.
        If you do not have specific information about this company, indicate that the information is based on general industry knowledge or similar companies.
        Return ONLY the JSON with no other text."""
    )
    
    try:
        system_message = SystemMessage(content="You are an expert on company cultures who provides accurate and helpful information about workplaces.")
        human_message = HumanMessage(content=prompt.format(company_name=company_name))
        
        result = llm.invoke([system_message, human_message])
        
        # Try to extract JSON from the response
        result_text = result.content
        # Find JSON in the response if it's embedded in other text
        try:
            import re
            json_match = re.search(r'({.*})', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            culture_data = json.loads(result_text)
        except:
            # Fallback if JSON parsing fails
            culture_data = {
                "overview": f"Information about {company_name} is based on general knowledge and may not be completely accurate.",
                "values": ["Innovation", "Customer focus", "Integrity", "Teamwork"],
                "work_environment": "Varies by department and location",
                "work_life_balance": "Depends on team and role",
                "growth_opportunities": "Various opportunities depending on company size and structure",
                "interview_tips": ["Research the company thoroughly", "Prepare examples of relevant experience", "Ask thoughtful questions", "Follow up after the interview"]
            }
        
        # Add a note if using general knowledge
        if "based on general" not in culture_data["overview"].lower():
            culture_data["overview"] += " (Note: This information is synthesized from public knowledge and may not represent current conditions.)"
            
        return culture_data
        
    except Exception as e:
        print(f"Error retrieving company culture data: {e}")
        return {
            "overview": f"Unable to retrieve information about {company_name}",
            "values": ["Information not available"],
            "work_environment": "Information not available",
            "work_life_balance": "Information not available",
            "growth_opportunities": "Information not available",
            "interview_tips": ["Research the company thoroughly before applying"]
        }

def compare_careers(career_list, llm=None):
    """
    Compares different career paths side by side.
    
    Args:
        career_list (list): List of careers to compare
        llm: Language model instance for analysis
        
    Returns:
        dict: Comparison data for each career
    """
    if not llm or not career_list:
        return []
    
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    import json
    
    careers_str = ", ".join(career_list)
    
    prompt = ChatPromptTemplate.from_template(
        """As a career comparison expert, provide a detailed comparison of the following career paths: {careers_str}.
        
        For each career, provide information in the following JSON format:
        [
            {{
                "career": <career name>,
                "salary_range": <typical salary range>,
                "education_required": <typical education requirements>,
                "skill_requirements": [<list of 5-7 key skills needed>],
                "work_life_balance": <assessment from 1-10, with 10 being excellent>,
                "job_stability": <assessment from 1-10, with 10 being excellent>,
                "growth_potential": <assessment from 1-10, with 10 being excellent>,
                "pros": [<list of 3-4 advantages of this career>],
                "cons": [<list of 3-4 disadvantages or challenges>]
            }},
            ... (one object for each career)
        ]
        
        Provide fair and balanced comparisons based on current industry knowledge.
        Return ONLY the JSON array with no other text."""
    )
    
    try:
        system_message = SystemMessage(content="You are an expert on career comparison who provides balanced, accurate information to help people make career decisions.")
        human_message = HumanMessage(content=prompt.format(careers_str=careers_str))
        
        result = llm.invoke([system_message, human_message])
        
        # Try to extract JSON from the response
        result_text = result.content
        # Find JSON in the response if it's embedded in other text
        try:
            import re
            json_match = re.search(r'(\[.*\])', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            comparison_data = json.loads(result_text)
        except:
            # Fallback if JSON parsing fails
            comparison_data = []
            for career in career_list:
                comparison_data.append({
                    "career": career,
                    "salary_range": "Varies by location and experience",
                    "education_required": "Typically bachelor's degree or equivalent experience",
                    "skill_requirements": ["Communication", "Problem solving", "Industry knowledge", "Technical skills", "Teamwork"],
                    "work_life_balance": 7,
                    "job_stability": 6,
                    "growth_potential": 7,
                    "pros": ["Diverse career paths", "Opportunity for growth", "Potentially rewarding work"],
                    "cons": ["Can be competitive", "May require ongoing education", "Work pressure varies by employer"]
                })
        
        return comparison_data
        
    except Exception as e:
        print(f"Error comparing careers: {e}")
        return []