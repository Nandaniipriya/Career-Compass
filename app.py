import streamlit as st
from llm_service import get_career_advice, initialize_llm
from career_graph import generate_insight_graph
from career_data import (
    get_job_growth_data, 
    get_career_skills, 
    get_salary_data,
    get_career_paths
)
from personality_assessment import (
    get_personality_types,
    get_career_matches_by_personality,
    analyze_resume,
    generate_cover_letter,
    create_learning_plan,
    get_company_culture_data,
    compare_careers
)
from career_tools import (
    display_career_comparison,
    career_path_visualization,
    display_learning_plan,
    job_application_tracker,
    display_resume_feedback,
    display_company_culture
)
from job_scraper import (
    search_jobs,
    get_job_details,
    analyze_job_fit,
    suggest_courses_for_skills
)
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_css
import json

# Page configuration
st.set_page_config(
    page_title="Career Compass AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'career_path' not in st.session_state:
    st.session_state.career_path = None
if 'personality_traits' not in st.session_state:
    st.session_state.personality_traits = {}
if 'career_matches' not in st.session_state:
    st.session_state.career_matches = []
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'resume_analysis' not in st.session_state:
    st.session_state.resume_analysis = {}
if 'compared_careers' not in st.session_state:
    st.session_state.compared_careers = []
if 'learning_plan' not in st.session_state:
    st.session_state.learning_plan = {}
if 'current_skills' not in st.session_state:
    st.session_state.current_skills = []
if 'company_culture' not in st.session_state:
    st.session_state.company_culture = {}
if 'cover_letter' not in st.session_state:
    st.session_state.cover_letter = ""
if 'personal_info' not in st.session_state:
    st.session_state.personal_info = {}
# Job search variables
if 'job_search_results' not in st.session_state:
    st.session_state.job_search_results = []
if 'selected_job' not in st.session_state:
    st.session_state.selected_job = None
if 'job_details' not in st.session_state:
    st.session_state.job_details = {}
if 'job_fit_analysis' not in st.session_state:
    st.session_state.job_fit_analysis = {}
if 'job_skills_courses' not in st.session_state:
    st.session_state.job_skills_courses = []
if 'llm' not in st.session_state:
    st.session_state.llm = initialize_llm()

# Main header
st.title("🧭 Career Compass AI")
st.markdown("Explore career paths, analyze job markets, and discover required skills with AI-powered guidance")

# Sidebar for career selection and exploration
with st.sidebar:
    st.header("Career Explorer")
    
    # User education background
    education_level = st.selectbox(
        "Your Education Level",
        ["High School", "Associate's Degree", "Bachelor's Degree", "Master's Degree", "PhD", "Other"]
    )
    
    # User experience level
    experience_level = st.selectbox(
        "Your Experience Level",
        ["Student/Entry Level", "1-3 Years", "4-6 Years", "7-10 Years", "10+ Years"]
    )
    
    # User interests
    interests = st.multiselect(
        "Your Interests",
        ["Technology", "Healthcare", "Finance", "Education", "Arts", "Business", 
         "Engineering", "Science", "Social Service", "Environment", "Law"]
    )
    
    # Career path selection
    available_careers = get_career_paths(education_level, interests)
    selected_career = st.selectbox("Explore a Career Path", available_careers)
    
    if st.button("Analyze This Career"):
        st.session_state.career_path = selected_career
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### App Language")
    app_language = st.selectbox(
        "Select Language",
        ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Hindi"],
        index=0
    )
    
    st.markdown("*Multi-language support is experimental*")

# Main content area - split into tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Career Chat Assistant", 
    "Career Insights", 
    "Job Market Analysis", 
    "Personality Assessment",
    "Resume & Cover Letter",
    "Career Planning Tools",
    "Job Search & Match"
])

# Tab 1: AI Chat Assistant
with tab1:
    st.header("Ask me anything about careers")
    st.markdown("I can help you with specific questions about career paths, required skills, education needs, and more.")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Career AI:** {message['content']}")
    
    # Input for new questions
    user_question = st.text_input("Type your career question here:")
    
    if st.button("Get Advice"):
        if user_question:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            # Get AI response
            with st.spinner("Thinking..."):
                career_context = {
                    "education_level": education_level,
                    "experience_level": experience_level,
                    "interests": interests,
                    "selected_career": selected_career if st.session_state.career_path else None
                }
                response = get_career_advice(user_question, career_context, st.session_state.llm)
            
            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Clear chat history button
    if st.session_state.chat_history and st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Tab 2: Career Insights
with tab2:
    if st.session_state.career_path:
        st.header(f"Career Insights: {st.session_state.career_path}")
        
        # Create two columns for layout
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Career description and overview
            with st.spinner("Generating career insights..."):
                career_insight = get_career_advice(
                    f"Provide a detailed overview of a career in {st.session_state.career_path}. Include typical roles, day-to-day responsibilities, and career progression paths.", 
                    {}, 
                    st.session_state.llm
                )
            st.markdown(career_insight)
            
            # Display the career insight graph using LangGraph visualization
            with st.expander("Career Path Progression"):
                graph_data = generate_insight_graph(st.session_state.career_path, st.session_state.llm)
                st.markdown(graph_data)
        
        with col2:
            # Required skills for the career
            st.subheader("Required Skills")
            skills = get_career_skills(st.session_state.career_path)
            for category, skill_list in skills.items():
                st.markdown(f"**{category}**")
                for skill in skill_list:
                    st.markdown(f"- {skill}")
            
            # Salary information
            st.subheader("Salary Information")
            salary_data = get_salary_data(st.session_state.career_path)
            
            # Create a bar chart for salary by experience
            salary_df = pd.DataFrame({
                'Experience Level': list(salary_data['by_experience'].keys()),
                'Salary (USD)': list(salary_data['by_experience'].values())
            })
            
            fig = px.bar(
                salary_df, 
                x='Experience Level', 
                y='Salary (USD)',
                title=f'Salary by Experience Level for {st.session_state.career_path}',
                color='Salary (USD)',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Education requirements
            st.subheader("Typical Education Requirements")
            with st.spinner("Loading education requirements..."):
                education_req = get_career_advice(
                    f"What education requirements and certifications are typically needed for a career in {st.session_state.career_path}? List them in bullet points.", 
                    {}, 
                    st.session_state.llm
                )
            st.markdown(education_req)
    else:
        st.info("👈 Select a career path from the sidebar and click 'Analyze This Career' to see detailed insights.")

# Tab 3: Job Market Analysis
with tab3:
    st.header("Job Market Analysis")
    
    # Allow selection of industry/sector for broader analysis
    selected_industry = st.selectbox(
        "Select Industry/Sector",
        ["Technology", "Healthcare", "Finance", "Education", "Engineering", "Business", "Arts & Media", "Science", "All Sectors"]
    )
    
    # Get job growth data for visualization
    growth_data = get_job_growth_data(selected_industry)
    
    # Create a line chart for job growth trends
    fig1 = px.line(
        growth_data, 
        x="Year", 
        y="Job Growth (%)",
        color="Career",
        title=f"Job Growth Trends - {selected_industry}",
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Two columns for additional visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Demand by location visualization
        location_data = growth_data.groupby('Location')['Job Openings'].sum().reset_index()
        fig2 = px.bar(
            location_data, 
            x="Location", 
            y="Job Openings",
            title="Job Demand by Location",
            color="Job Openings",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Remote vs. In-person work trends
        work_mode_data = pd.DataFrame({
            'Work Mode': ['Remote', 'Hybrid', 'In-office'],
            'Percentage': [25, 45, 30]  # Example values - will be replaced by API data
        })
        
        fig3 = px.pie(
            work_mode_data, 
            values='Percentage', 
            names='Work Mode',
            title="Remote vs. In-Office Work Distribution",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # Future job market projections
    st.subheader("Future Job Market Projections")
    st.markdown("Based on current trends and AI analysis, here are projections for job market changes in the next 5 years:")
    
    # Generate job market projections using the LLM
    with st.spinner("Analyzing future job market trends..."):
        market_projection = get_career_advice(
            f"Provide a concise analysis of future job market projections for the {selected_industry} industry over the next 5 years. Focus on emerging roles, skills that will be in demand, and potential industry shifts.", 
            {}, 
            st.session_state.llm
        )
    
    st.markdown(market_projection)

# Tab 4: Personality Assessment
with tab4:
    st.header("Personality & Work Style Assessment")
    st.markdown("Understand how your personality traits align with different career paths.")
    
    # Get personality types
    personality_types = get_personality_types()
    
    # Tabs for assessment and results
    assess_tab, results_tab = st.tabs(["Take Assessment", "View Career Matches"])
    
    with assess_tab:
        st.markdown("### Select traits that describe you best")
        st.markdown("Choose traits from each category that most accurately reflect your preferences and style.")
        
        # Create a dictionary to store selected traits
        selected_traits = {}
        
        # Display each category in a separate expander
        for category, traits in personality_types.items():
            with st.expander(f"{category}", expanded=True):
                selected = st.multiselect(
                    f"Select traits that describe your {category.lower()}:",
                    traits,
                    key=f"traits_{category}"
                )
                if selected:
                    selected_traits[category] = selected
        
        # Button to analyze personality
        if st.button("Analyze My Personality"):
            if selected_traits:
                st.session_state.personality_traits = selected_traits
                
                # Get career matches based on personality
                st.session_state.career_matches = get_career_matches_by_personality(selected_traits)
                
                st.success("Analysis complete! View your career matches in the 'View Career Matches' tab.")
                st.rerun()
            else:
                st.warning("Please select at least one trait to analyze.")
    
    with results_tab:
        if st.session_state.career_matches:
            st.markdown("### Careers that Match Your Personality")
            st.markdown("These career paths align well with your personality traits and preferences:")
            
            # Display career matches
            for match in st.session_state.career_matches:
                with st.expander(f"**{match['career']}** (Match Strength: {match['match_strength']})"):
                    st.markdown("**Why this matches you:**")
                    for reason in match['reasons']:
                        st.markdown(f"- {reason}")
                    
                    # Add button to analyze this career
                    if st.button(f"Analyze {match['career']}", key=f"analyze_{match['career']}"):
                        st.session_state.career_path = match['career']
                        st.rerun()
        else:
            st.info("Complete the assessment in the 'Take Assessment' tab to see your career matches.")

# Tab 5: Resume & Cover Letter
with tab5:
    st.header("Resume & Cover Letter Tools")
    
    # Create tabs for Resume Analysis and Cover Letter Generator
    resume_tab, cover_letter_tab = st.tabs(["Resume Analyzer", "Cover Letter Generator"])
    
    with resume_tab:
        st.markdown("### Upload your resume for AI analysis")
        st.markdown("Get feedback on your resume and how well it matches job descriptions.")
        
        # Two options: analyze against job description or general analysis
        analysis_type = st.radio(
            "Choose analysis type:",
            ["General Resume Feedback", "Match Against Job Description"]
        )
        
        # Resume input
        resume_text = st.text_area(
            "Paste your resume text here:",
            st.session_state.resume_text,
            height=300,
            placeholder="Copy and paste the content of your resume here..."
        )
        
        if analysis_type == "Match Against Job Description":
            # Job description input
            job_description = st.text_area(
                "Paste the job description here:",
                st.session_state.job_description,
                height=200,
                placeholder="Copy and paste the job description you want to match against..."
            )
            
            if st.button("Analyze Resume Match") and resume_text and job_description:
                st.session_state.resume_text = resume_text
                st.session_state.job_description = job_description
                
                with st.spinner("Analyzing your resume against the job description..."):
                    analysis = analyze_resume(resume_text, job_description, st.session_state.llm)
                    st.session_state.resume_analysis = analysis
                
                st.success("Analysis complete!")
                
                # Display the analysis results
                display_resume_feedback(st.session_state.resume_analysis)
        else:
            if st.button("Get Resume Feedback") and resume_text:
                st.session_state.resume_text = resume_text
                
                with st.spinner("Analyzing your resume..."):
                    analysis = analyze_resume(resume_text, "", st.session_state.llm)
                    st.session_state.resume_analysis = analysis
                
                st.success("Analysis complete!")
                
                # Display the analysis results
                display_resume_feedback(st.session_state.resume_analysis)
    
    with cover_letter_tab:
        st.markdown("### AI-Powered Cover Letter Generator")
        st.markdown("Create a customized cover letter based on your resume and a job description.")
        
        # Personal information
        with st.expander("Your Personal Information", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name", 
                                    st.session_state.personal_info.get("name", ""))
                email = st.text_input("Email", 
                                     st.session_state.personal_info.get("email", ""))
                phone = st.text_input("Phone", 
                                     st.session_state.personal_info.get("phone", ""))
            
            with col2:
                address = st.text_input("Address", 
                                       st.session_state.personal_info.get("address", ""))
                linkedin = st.text_input("LinkedIn URL", 
                                        st.session_state.personal_info.get("linkedin", ""))
                portfolio = st.text_input("Portfolio URL", 
                                         st.session_state.personal_info.get("portfolio", ""))
        
        # Use existing resume or enter new one
        use_existing = st.checkbox("Use resume from Resume Analyzer", 
                                  value=True if st.session_state.resume_text else False,
                                  key="cover_letter_use_resume")
        
        if use_existing and st.session_state.resume_text:
            resume_for_cover = st.session_state.resume_text
            st.info("Using resume from Resume Analyzer")
        else:
            resume_for_cover = st.text_area(
                "Paste your resume text:",
                height=200,
                placeholder="Copy and paste your resume content here...",
                key="cover_letter_resume_input"
            )
        
        # Use existing job description or enter new one
        use_existing_jd = st.checkbox("Use job description from Resume Analyzer", 
                                     value=True if st.session_state.job_description else False,
                                     key="cover_letter_use_jd")
        
        if use_existing_jd and st.session_state.job_description:
            job_desc_for_cover = st.session_state.job_description
            st.info("Using job description from Resume Analyzer")
        else:
            job_desc_for_cover = st.text_area(
                "Paste the job description:",
                height=200,
                placeholder="Copy and paste the job description here...",
                key="cover_letter_jd_input"
            )
        
        # Button to generate cover letter
        if st.button("Generate Cover Letter") and resume_for_cover and job_desc_for_cover:
            # Update personal info
            st.session_state.personal_info = {
                "name": name,
                "email": email,
                "phone": phone,
                "address": address,
                "linkedin": linkedin,
                "portfolio": portfolio
            }
            
            personal_info_str = f"""
            Name: {name}
            Email: {email}
            Phone: {phone}
            Address: {address}
            LinkedIn: {linkedin}
            Portfolio: {portfolio}
            """
            
            with st.spinner("Generating your cover letter..."):
                cover_letter = generate_cover_letter(
                    resume_for_cover, 
                    job_desc_for_cover, 
                    personal_info_str,
                    st.session_state.llm
                )
                st.session_state.cover_letter = cover_letter
            
            st.success("Cover letter generated!")
        
        # Display generated cover letter
        if st.session_state.cover_letter:
            st.markdown("### Your Generated Cover Letter")
            st.markdown("---")
            st.markdown(st.session_state.cover_letter)
            st.markdown("---")
            
            # Copy to clipboard button
            if st.button("Copy to Clipboard"):
                st.code(st.session_state.cover_letter)
                st.info("Cover letter text displayed above. Select and copy as needed.")

# Tab 6: Career Planning Tools
with tab6:
    st.header("Career Planning Tools")
    
    # Create subtabs for different tools
    planning_tabs = st.tabs([
        "Learning Path", 
        "Company Culture Insights", 
        "Career Comparison", 
        "Job Application Tracker"
    ])
    
    # Learning Path Tool
    with planning_tabs[0]:
        st.markdown("### Personalized Learning Plan")
        st.markdown("Get a customized learning plan based on your current skills and target career.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_career = st.text_input(
                "Target Career Path",
                value=st.session_state.career_path if st.session_state.career_path else ""
            )
            
            exp_level = st.selectbox(
                "Your Current Experience Level",
                ["Beginner", "Intermediate", "Advanced", "Switching Careers"]
            )
        
        with col2:
            # Input for current skills
            current_skills = st.text_area(
                "Your Current Skills (one per line)",
                "\n".join(st.session_state.current_skills) if st.session_state.current_skills else "",
                height=150,
                help="List your current skills, one per line"
            )
            
            # Parse skills
            if current_skills:
                skill_list = [skill.strip() for skill in current_skills.split("\n") if skill.strip()]
            else:
                skill_list = []
        
        if st.button("Generate Learning Plan") and target_career and skill_list:
            st.session_state.current_skills = skill_list
            
            with st.spinner("Creating your personalized learning plan..."):
                learning_plan = create_learning_plan(
                    skill_list,
                    target_career,
                    exp_level,
                    st.session_state.llm
                )
                st.session_state.learning_plan = learning_plan
            
            st.success("Learning plan created!")
        
        # Display learning plan
        if st.session_state.learning_plan:
            display_learning_plan(st.session_state.learning_plan)
    
    # Company Culture Insights
    with planning_tabs[1]:
        st.markdown("### Company Culture Insights")
        st.markdown("Research company cultures to find the right fit for your work style.")
        
        company_name = st.text_input("Enter Company Name")
        
        if st.button("Research Company Culture") and company_name:
            with st.spinner(f"Researching culture at {company_name}..."):
                culture_data = get_company_culture_data(company_name, st.session_state.llm)
                st.session_state.company_culture = culture_data
            
            st.success(f"Culture information retrieved for {company_name}")
        
        # Display company culture information
        if st.session_state.company_culture:
            display_company_culture(st.session_state.company_culture)
    
    # Career Comparison Tool
    with planning_tabs[2]:
        st.markdown("### Career Comparison Tool")
        st.markdown("Compare different career paths side by side to help make decisions.")
        
        # Career selection
        career_options = get_career_paths("All", [])
        
        # Allow selection of up to 3 careers to compare
        selected_for_comparison = st.multiselect(
            "Select 2-3 careers to compare",
            career_options,
            default=st.session_state.compared_careers if st.session_state.compared_careers else []
        )
        
        if st.button("Compare Careers") and len(selected_for_comparison) >= 2:
            if len(selected_for_comparison) > 3:
                st.warning("Please select no more than 3 careers for optimal comparison.")
                selected_for_comparison = selected_for_comparison[:3]
            
            st.session_state.compared_careers = selected_for_comparison
            
            with st.spinner("Generating comparison data..."):
                comparison_data = compare_careers(selected_for_comparison, st.session_state.llm)
            
            # Store comparison data
            st.session_state.comparison_data = comparison_data
            
            st.success("Comparison complete!")
        
        # Display career comparison
        if hasattr(st.session_state, 'comparison_data') and st.session_state.comparison_data:
            display_career_comparison(st.session_state.comparison_data)
    
    # Job Application Tracker
    with planning_tabs[3]:
        job_application_tracker()

# Tab 7: Job Search & Match
with tab7:
    st.header("Real-Time Job Search & Fit Analysis")
    st.markdown("Search for real job listings, analyze job requirements, and check how well your profile matches the position.")
    
    # Create subtabs for different job search tools
    job_tabs = st.tabs(["Search Jobs", "Job Details & Analysis", "Skills Development"])
    
    # Job Search Tab
    with job_tabs[0]:
        st.markdown("### Find Real Job Opportunities")
        st.markdown("Search for job listings using keywords and location.")
        
        # Job search form
        col1, col2 = st.columns([2, 1])
        
        with col1:
            job_query = st.text_input("Job Title or Keywords:", 
                                    placeholder="e.g., Data Scientist, Software Engineer, Marketing Manager")
        
        with col2:
            job_location = st.text_input("Location (optional):", 
                                       placeholder="e.g., New York, Remote")
        
        # Number of results to return
        num_results = st.slider("Number of results:", min_value=5, max_value=20, value=10, step=5)
        
        # Search button
        if st.button("Search Jobs") and job_query:
            with st.spinner(f"Searching for {job_query} jobs..."):
                search_results = search_jobs(job_query, job_location, num_results)
                st.session_state.job_search_results = search_results
                
                # Reset selection
                st.session_state.selected_job = None
                st.session_state.job_details = {}
                st.session_state.job_fit_analysis = {}
                st.session_state.job_skills_courses = []
            
            if search_results:
                st.success(f"Found {len(search_results)} job listings!")
            else:
                st.error("No job listings found. Try different keywords or location.")
        
        # Display search results
        if st.session_state.job_search_results:
            st.markdown("### Search Results")
            
            for idx, job in enumerate(st.session_state.job_search_results):
                with st.expander(f"{job['title']} - {job['company']} ({job['location']})"):
                    st.markdown(f"**Source:** {job['source']}")
                    st.markdown(f"**Snippet:** {job['snippet']}")
                    
                    # Columns for view buttons
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if st.button(f"View Details", key=f"view_{idx}"):
                            st.session_state.selected_job = job
                            
                            # Fetch full job details
                            with st.spinner("Fetching job details..."):
                                job_details = get_job_details(job['url'])
                                st.session_state.job_details = job_details
                                
                                # Update the selected job with details
                                job['full_details'] = job_details
                            
                            st.rerun()
                    
                    with col2:
                        if st.button(f"Open Job Listing", key=f"open_{idx}"):
                            st.markdown(f"[Open job listing in new tab]({job['url']})")
    
    # Job Details & Analysis Tab
    with job_tabs[1]:
        if not st.session_state.selected_job:
            st.info("Please select a job from the Search Results tab to view details and analyze fit.")
        else:
            job = st.session_state.selected_job
            details = st.session_state.job_details
            
            st.markdown(f"## {job['title']}")
            st.markdown(f"**Company:** {job['company']}")
            st.markdown(f"**Location:** {job['location']}")
            
            if details.get('salary', '') != 'Salary not specified':
                st.markdown(f"**Salary:** {details.get('salary', 'Not specified')}")
            
            if details.get('job_type', '') != 'Not specified':
                st.markdown(f"**Job Type:** {details.get('job_type', 'Not specified')}")
            
            # Job description
            st.markdown("### Job Description")
            st.markdown(details.get('description', 'No detailed description available.'))
            
            # Job requirements
            if details.get('requirements'):
                st.markdown("### Requirements")
                for req in details.get('requirements', []):
                    st.markdown(f"- {req}")
            
            # Benefits
            if details.get('benefits'):
                st.markdown("### Benefits")
                for benefit in details.get('benefits', []):
                    st.markdown(f"- {benefit}")
            
            # Application link
            if details.get('application_link'):
                st.markdown("### Apply")
                st.markdown(f"[Apply for this position]({details.get('application_link')})")
            
            # Analyze fit against resume
            st.markdown("---")
            st.markdown("### Analyze Your Fit for This Position")
            
            # Use existing resume or paste new one
            use_existing = st.checkbox("Use resume from Resume Analyzer", 
                                     value=True if st.session_state.resume_text else False,
                                     key="job_search_use_resume")
            
            if use_existing and st.session_state.resume_text:
                resume_for_analysis = st.session_state.resume_text
                st.info("Using resume from Resume Analyzer tab")
            else:
                resume_for_analysis = st.text_area(
                    "Paste your resume text here to analyze your fit:",
                    height=200,
                    placeholder="Copy and paste your resume content here...",
                    key="job_search_resume_input"
                )
            
            if st.button("Analyze My Fit") and resume_for_analysis:
                # Store resume text
                st.session_state.resume_text = resume_for_analysis
                
                with st.spinner("Analyzing how well your profile matches this job..."):
                    # Analyze fit
                    fit_analysis = analyze_job_fit(
                        details, 
                        resume_for_analysis,
                        st.session_state.llm
                    )
                    st.session_state.job_fit_analysis = fit_analysis
                    
                    # Get course recommendations for missing skills
                    if 'skills_to_develop' in fit_analysis and fit_analysis['skills_to_develop']:
                        skills_courses = suggest_courses_for_skills(
                            fit_analysis['skills_to_develop'],
                            st.session_state.llm
                        )
                        st.session_state.job_skills_courses = skills_courses
                
                st.success("Analysis complete!")
            
            # Display fit analysis results
            if st.session_state.job_fit_analysis:
                fit = st.session_state.job_fit_analysis
                
                # Create gauge chart for match percentage
                match_percentage = fit.get('match_percentage', 0)
                
                # Create columns for layout
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Create a donut chart for match percentage
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=match_percentage,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Match Score"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "green" if match_percentage >= 70 else "orange" if match_percentage >= 50 else "red"},
                            'steps': [
                                {'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 70], 'color': "gray"},
                                {'range': [70, 100], 'color': "darkgray"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 70
                            }
                        }
                    ))
                    
                    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("### Match Analysis")
                    
                    # Matching qualifications
                    st.markdown("**Your Matching Qualifications:**")
                    for qual in fit.get('matching_qualifications', []):
                        st.markdown(f"✅ {qual}")
                    
                    # Missing qualifications
                    st.markdown("**Areas to Improve:**")
                    for qual in fit.get('missing_qualifications', []):
                        st.markdown(f"❌ {qual}")
                
                # Resume improvement tips
                st.markdown("### Resume Improvement Tips")
                for tip in fit.get('resume_improvement_tips', []):
                    st.markdown(f"- {tip}")
                
                # Skills to develop with courses
                st.markdown("### Skills to Develop")
                for skill in fit.get('skills_to_develop', []):
                    st.markdown(f"- {skill}")
                
                # CTA to view recommended courses
                if st.session_state.job_skills_courses:
                    st.markdown("See the 'Skills Development' tab for suggested courses and resources to develop these skills.")
    
    # Skills Development Tab
    with job_tabs[2]:
        if not st.session_state.job_skills_courses:
            if st.session_state.selected_job:
                st.info("Please analyze your fit for the selected job to get skill development recommendations.")
            else:
                st.info("Please select a job and analyze your fit to get skill development recommendations.")
        else:
            st.markdown("### Recommended Courses & Resources")
            st.markdown("Based on your job match analysis, here are resources to help you develop the required skills:")
            
            for course in st.session_state.job_skills_courses:
                with st.expander(f"**{course.get('skill', 'Skill')}**"):
                    st.markdown(f"**Recommended Course:** {course.get('course_name', 'N/A')}")
                    st.markdown(f"**Platform:** {course.get('platform', 'N/A')}")
                    st.markdown(f"**Why this is recommended:** {course.get('reason', 'N/A')}")
                    
                    # Check if we have a search URL for the course
                    course_name = course.get('course_name', '').replace(' ', '+')
                    platform = course.get('platform', '').replace(' ', '+')
                    search_url = f"https://www.google.com/search?q={course_name}+{platform}"
                    
                    st.markdown(f"[Search for this course]({search_url})")
            
            # Guidance on using the recommendations
            st.markdown("### How to Use These Recommendations")
            st.markdown("""
            1. **Prioritize skills** based on your career goals and the job requirements
            2. **Create a learning plan** with specific timelines for each skill
            3. **Track your progress** and update your resume as you acquire new skills
            4. **Apply your learning** through projects to demonstrate your capabilities
            """)

# Footer information
st.markdown("---")
st.markdown("Career Compass AI - Powered by Streamlit, LangChain & LangGraph")
st.markdown("Note: All career guidance is based on current market data and AI analysis. Always verify information with additional sources.")
