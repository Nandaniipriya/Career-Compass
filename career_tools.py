import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

def display_career_comparison(comparison_data):
    """
    Displays a side-by-side comparison of different career paths.
    
    Args:
        comparison_data (list): List of dictionaries with career comparison data
    """
    if not comparison_data:
        st.warning("No comparison data available")
        return
    
    # Create tabs for different comparison views
    tab1, tab2, tab3 = st.tabs(["Overview", "Skills & Education", "Pros & Cons"])
    
    with tab1:
        # Create columns for each career
        cols = st.columns(len(comparison_data))
        
        for i, career_data in enumerate(comparison_data):
            with cols[i]:
                st.subheader(career_data.get("career", "Career"))
                st.write(f"**Salary Range:** {career_data.get('salary_range', 'N/A')}")
                
                # Create metrics for ratings
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Work-Life", f"{career_data.get('work_life_balance', 'N/A')}/10")
                with col2:
                    st.metric("Stability", f"{career_data.get('job_stability', 'N/A')}/10")
                with col3:
                    st.metric("Growth", f"{career_data.get('growth_potential', 'N/A')}/10")
        
        # Create radar chart comparing all careers
        st.subheader("Career Comparison")
        
        categories = ['Work-Life Balance', 'Job Stability', 'Growth Potential']
        fig = go.Figure()
        
        for career_data in comparison_data:
            career_name = career_data.get("career", "Career")
            values = [
                career_data.get('work_life_balance', 5),
                career_data.get('job_stability', 5),
                career_data.get('growth_potential', 5)
            ]
            # Close the polygon by appending the first value
            values.append(values[0])
            
            # Add categories to the list and close it
            categories_closed = categories + [categories[0]]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories_closed,
                fill='toself',
                name=career_name
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Display skills and education requirements
        for career_data in comparison_data:
            st.subheader(career_data.get("career", "Career"))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Education Required:**")
                st.write(career_data.get("education_required", "N/A"))
            
            with col2:
                st.write("**Key Skills:**")
                skills = career_data.get("skill_requirements", [])
                for skill in skills:
                    st.markdown(f"- {skill}")
            
            st.divider()
    
    with tab3:
        # Display pros and cons
        for career_data in comparison_data:
            st.subheader(career_data.get("career", "Career"))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Pros:**")
                pros = career_data.get("pros", [])
                for pro in pros:
                    st.markdown(f"- ✅ {pro}")
            
            with col2:
                st.write("**Cons:**")
                cons = career_data.get("cons", [])
                for con in cons:
                    st.markdown(f"- ⚠️ {con}")
            
            st.divider()

def career_path_visualization(career_data):
    """
    Visualizes career progression paths.
    
    Args:
        career_data (dict): Career progression data
    """
    if not career_data:
        st.warning("No career path data available")
        return
    
    # Extract the career roles at different levels
    entry_roles = career_data.get("entry_roles", [])
    mid_roles = career_data.get("mid_roles", [])
    senior_roles = career_data.get("senior_roles", [])
    
    # Create sankey diagram data
    labels = []
    source = []
    target = []
    value = []
    colors = []
    
    # Entry level is source
    for i, entry in enumerate(entry_roles):
        entry_title = entry.get("title", f"Entry Role {i+1}")
        labels.append(entry_title)
        
        # Connect each entry role to each mid role
        for j, mid in enumerate(mid_roles):
            mid_title = mid.get("title", f"Mid Role {j+1}")
            
            # Add mid role if not already in labels
            if mid_title not in labels:
                labels.append(mid_title)
            
            # Add connection
            source.append(i)  # Index of entry role
            target.append(labels.index(mid_title))  # Index of mid role
            value.append(1)  # Equal weight for simplicity
            colors.append('rgba(44, 160, 44, 0.4)')  # Green
    
    # Mid level to senior level
    for j, mid in enumerate(mid_roles):
        mid_title = mid.get("title", f"Mid Role {j+1}")
        mid_index = labels.index(mid_title)
        
        # Connect each mid role to each senior role
        for k, senior in enumerate(senior_roles):
            senior_title = senior.get("title", f"Senior Role {k+1}")
            
            # Add senior role if not already in labels
            if senior_title not in labels:
                labels.append(senior_title)
            
            # Add connection
            source.append(mid_index)  # Index of mid role
            target.append(labels.index(senior_title))  # Index of senior role
            value.append(1)  # Equal weight for simplicity
            colors.append('rgba(214, 39, 40, 0.4)')  # Red
    
    # Create figure
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="blue"
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=colors
        )
    )])
    
    fig.update_layout(
        title_text=f"Career Progression Paths",
        font_size=12,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display explanatory text
    st.markdown("""
    **How to read this chart:**
    - Left side shows entry-level positions
    - Middle shows mid-career roles
    - Right side shows senior positions
    - Lines show possible career transitions
    """)
    
    # Add additional details about each role level if needed
    with st.expander("Entry Level Details"):
        for role in entry_roles:
            st.markdown(f"**{role.get('title', 'Role')}**")
            resp = role.get('responsibilities', [])
            for r in resp:
                st.markdown(f"- {r}")
    
    with st.expander("Mid-Level Details"):
        for role in mid_roles:
            st.markdown(f"**{role.get('title', 'Role')}**")
            resp = role.get('responsibilities', [])
            for r in resp:
                st.markdown(f"- {r}")
    
    with st.expander("Senior Level Details"):
        for role in senior_roles:
            st.markdown(f"**{role.get('title', 'Role')}**")
            resp = role.get('responsibilities', [])
            for r in resp:
                st.markdown(f"- {r}")

def display_learning_plan(learning_plan):
    """
    Displays a personalized learning plan.
    
    Args:
        learning_plan (dict): Learning plan data
    """
    if not learning_plan:
        st.warning("No learning plan available")
        return
    
    # Display skill gaps
    st.subheader("Key Skills to Develop")
    skill_gaps = learning_plan.get("skill_gaps", [])
    for skill in skill_gaps:
        st.markdown(f"- {skill}")
    
    # Display recommended courses
    st.subheader("Recommended Courses")
    courses = learning_plan.get("recommended_courses", [])
    
    for i, course in enumerate(courses):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{course.get('name', 'Course')}**")
            st.markdown(f"_{course.get('provider', 'Provider')}_")
            st.markdown(f"{course.get('description', '')}")
        
        with col2:
            difficulty = course.get('difficulty', 'N/A')
            if difficulty == "Beginner":
                st.markdown("🟢 Beginner")
            elif difficulty == "Intermediate":
                st.markdown("🟠 Intermediate")
            elif difficulty == "Advanced":
                st.markdown("🔴 Advanced")
            else:
                st.markdown(f"⚪ {difficulty}")
        
        with col3:
            st.markdown(f"⏱️ {course.get('time_commitment', 'N/A')}")
        
        st.divider()
    
    # Display additional resources
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Additional Learning Resources")
        resources = learning_plan.get("learning_resources", [])
        for resource in resources:
            st.markdown(f"- {resource}")
    
    with col2:
        st.subheader("Certification Paths")
        certifications = learning_plan.get("certification_paths", [])
        for cert in certifications:
            st.markdown(f"- {cert}")
    
    # Display timeline with progress bar
    st.subheader("Suggested Timeline")
    timeline = learning_plan.get("timeline", "N/A")
    st.write(timeline)
    
    # Optional: Add a way for users to track progress
    st.progress(0, "Just getting started")

def job_application_tracker():
    """
    Interface for tracking job applications.
    """
    st.subheader("Job Application Tracker")
    
    # Initialize session state for job applications if it doesn't exist
    if 'job_applications' not in st.session_state:
        st.session_state.job_applications = []
    
    # Form for adding new applications
    with st.expander("Add New Application"):
        with st.form("new_application"):
            col1, col2 = st.columns(2)
            
            with col1:
                company = st.text_input("Company Name")
                position = st.text_input("Position")
                location = st.text_input("Location")
            
            with col2:
                application_date = st.date_input("Application Date", datetime.now())
                status_options = [
                    "Applied", "Screening", "Interview Scheduled", 
                    "Interviewed", "Follow-up", "Offered", "Accepted", "Rejected"
                ]
                status = st.selectbox("Status", status_options)
                url = st.text_input("Job Posting URL")
            
            notes = st.text_area("Notes (contacts, salary, etc.)")
            
            submitted = st.form_submit_button("Save Application")
            if submitted and company and position:
                # Add new application to the list
                st.session_state.job_applications.append({
                    "company": company,
                    "position": position,
                    "location": location,
                    "date": application_date,
                    "status": status,
                    "url": url,
                    "notes": notes
                })
                st.success("Application saved!")
    
    # Display existing applications
    if st.session_state.job_applications:
        # Tabs for different views
        tab1, tab2 = st.tabs(["List View", "Statistics"])
        
        with tab1:
            # Filter options
            status_filter = st.multiselect(
                "Filter by Status", 
                options=[
                    "Applied", "Screening", "Interview Scheduled", 
                    "Interviewed", "Follow-up", "Offered", "Accepted", "Rejected"
                ],
                default=[]
            )
            
            # Apply filters
            filtered_apps = st.session_state.job_applications
            if status_filter:
                filtered_apps = [app for app in filtered_apps if app["status"] in status_filter]
            
            # Convert to dataframe for display
            if filtered_apps:
                df = pd.DataFrame(filtered_apps)
                df = df.sort_values(by="date", ascending=False)
                
                # Custom formatter for the dataframe
                def make_clickable(url, text):
                    if pd.notnull(url) and url.strip():
                        return f'<a href="{url}" target="_blank">{text}</a>'
                    return text
                
                # Apply the formatter
                df['position'] = df.apply(
                    lambda row: make_clickable(row['url'], row['position']) if pd.notnull(row['url']) else row['position'], 
                    axis=1
                )
                
                # Select columns to display
                display_df = df[['company', 'position', 'location', 'date', 'status']]
                
                # Rename columns for display
                display_df.columns = ['Company', 'Position', 'Location', 'Date', 'Status']
                
                # Display the dataframe
                st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                # Show application details when selected
                if len(filtered_apps) > 0:
                    st.subheader("Application Details")
                    selected_company = st.selectbox("Select Application", df['company'].tolist())
                    selected_app = df[df['company'] == selected_company].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Company:** {selected_app['company']}")
                        st.write(f"**Position:** {selected_app['position']}")
                        st.write(f"**Location:** {selected_app['location']}")
                    
                    with col2:
                        st.write(f"**Applied On:** {selected_app['date']}")
                        st.write(f"**Current Status:** {selected_app['status']}")
                        if selected_app['url']:
                            st.write(f"**Job URL:** [Link]({selected_app['url']})")
                    
                    st.write("**Notes:**")
                    st.write(selected_app['notes'] if selected_app['notes'] else "No notes")
                    
                    # Update status
                    new_status = st.selectbox("Update Status", status_options, status_options.index(selected_app['status']))
                    if st.button("Update Status"):
                        # Find the application in the session state and update it
                        for app in st.session_state.job_applications:
                            if app['company'] == selected_app['company'] and app['position'] == selected_app['position']:
                                app['status'] = new_status
                                break
                        st.success("Status updated!")
                        st.rerun()
            else:
                st.info("No applications match the selected filters.")
        
        with tab2:
            # Application statistics
            if st.session_state.job_applications:
                df = pd.DataFrame(st.session_state.job_applications)
                
                # Status distribution
                st.subheader("Application Status Distribution")
                status_counts = df['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                
                fig = px.pie(
                    status_counts, 
                    values='Count', 
                    names='Status',
                    title="Application Status Distribution",
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Applications over time
                st.subheader("Applications Over Time")
                df['date'] = pd.to_datetime(df['date'])
                df['month'] = df['date'].dt.strftime('%Y-%m')
                monthly_apps = df.groupby('month').size().reset_index(name='count')
                
                fig = px.line(
                    monthly_apps, 
                    x='month', 
                    y='count',
                    markers=True,
                    title="Applications Submitted by Month"
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No job applications tracked yet. Add your first application above.")

def display_resume_feedback(analysis):
    """
    Displays feedback on a resume.
    
    Args:
        analysis (dict): Resume analysis results
    """
    if not analysis:
        st.warning("No resume analysis available")
        return
    
    # If there's a score, display it prominently
    if 'score' in analysis and analysis['score'] is not None:
        score = analysis['score']
        
        # Display score as a gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Match Score"},
            gauge = {
                'axis': {'range': [0, 10]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 3], 'color': "red"},
                    {'range': [3, 7], 'color': "orange"},
                    {'range': [7, 10], 'color': "green"}
                ]
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Display strengths and weaknesses in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Strengths")
        strengths = analysis.get('strengths', [])
        for strength in strengths:
            st.markdown(f"- {strength}")
    
    with col2:
        st.subheader("🔍 Areas for Improvement")
        weaknesses = analysis.get('weaknesses', [])
        for weakness in weaknesses:
            st.markdown(f"- {weakness}")
    
    # Display specific improvement suggestions
    st.subheader("📝 Suggestions")
    suggestions = analysis.get('suggestions', [])
    for suggestion in suggestions:
        st.markdown(f"- {suggestion}")
    
    # If there are keyword matches, display them
    if 'keyword_matches' in analysis and analysis['keyword_matches']:
        st.subheader("🔑 Keyword Matches")
        st.write("These important keywords from the job description were found in your resume:")
        
        keyword_matches = analysis['keyword_matches']
        # Split into columns if there are many keywords
        if len(keyword_matches) > 5:
            cols = st.columns(2)
            half = len(keyword_matches) // 2
            
            with cols[0]:
                for keyword in keyword_matches[:half]:
                    st.markdown(f"- {keyword}")
            
            with cols[1]:
                for keyword in keyword_matches[half:]:
                    st.markdown(f"- {keyword}")
        else:
            for keyword in keyword_matches:
                st.markdown(f"- {keyword}")
    
    # If there are career matches, display them
    if 'best_career_matches' in analysis and analysis['best_career_matches']:
        st.subheader("👔 Potential Career Matches")
        matches = analysis.get('best_career_matches', [])
        for match in matches:
            st.markdown(f"- {match}")

def display_company_culture(culture_data):
    """
    Displays company culture information.
    
    Args:
        culture_data (dict): Company culture information
    """
    if not culture_data:
        st.warning("No company culture data available")
        return
    
    # Display overview
    st.markdown(f"### Company Culture Overview")
    st.write(culture_data.get('overview', 'No overview available'))
    
    # Display values, environment and work-life balance in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Core Values")
        values = culture_data.get('values', [])
        for value in values:
            st.markdown(f"- {value}")
        
        st.subheader("Growth Opportunities")
        st.write(culture_data.get('growth_opportunities', 'Information not available'))
    
    with col2:
        st.subheader("Work Environment")
        st.write(culture_data.get('work_environment', 'Information not available'))
        
        st.subheader("Work-Life Balance")
        st.write(culture_data.get('work_life_balance', 'Information not available'))
    
    # Display interview tips
    st.subheader("Interview Tips")
    tips = culture_data.get('interview_tips', [])
    for tip in tips:
        st.markdown(f"- {tip}")