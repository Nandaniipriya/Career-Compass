"""
Job Scraper Module for Career Compass AI

This module handles scraping job listings from the web using DuckDuckGo Search API.
It provides functions to search for jobs, extract job details, and analyze job listings.
"""

import re
import json
import html2text
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from typing import List, Dict, Any, Optional, Tuple

# Initialize HTML to text converter
h2t = html2text.HTML2Text()
h2t.ignore_links = False
h2t.ignore_images = True

def search_jobs(query: str, location: str = "", num_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search for job listings using DuckDuckGo.
    
    Args:
        query (str): Job title or keywords to search for
        location (str): Optional location for the job
        num_results (int): Number of results to return
        
    Returns:
        List[Dict]: List of job listings with title, company, location, url, and snippet
    """
    search_query = f"{query} jobs"
    if location:
        search_query += f" in {location}"
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=num_results))
            
        # Process the results to extract job information
        job_listings = []
        for result in results:
            # Extract relevant info from each result
            listing = {
                "title": result.get("title", "").split(" - ")[0].strip(),
                "company": extract_company_from_title(result.get("title", "")),
                "url": result.get("href", ""),
                "snippet": result.get("body", ""),
                "source": extract_domain(result.get("href", "")),
                "location": extract_location(result.get("title", ""), result.get("body", ""), location),
                "full_details": None  # Will be populated when the user selects a job
            }
            job_listings.append(listing)
            
        return job_listings
    except Exception as e:
        print(f"Error searching for jobs: {str(e)}")
        return []

def extract_company_from_title(title: str) -> str:
    """Extract company name from job title"""
    parts = title.split(" - ")
    if len(parts) > 1:
        return parts[1].strip()
    return "Unknown Company"

def extract_domain(url: str) -> str:
    """Extract domain name from URL"""
    try:
        if url:
            matches = re.findall(r"https?://(?:www\.)?([^/]+)", url)
            if matches:
                return matches[0]
    except Exception:
        pass
    return "Unknown Source"

def extract_location(title: str, snippet: str, default_location: str) -> str:
    """Extract location from job details"""
    # Try to find location in title
    title_location = None
    if " - " in title and " in " in title:
        parts = title.split(" - ")
        if len(parts) > 1 and " in " in parts[1]:
            location_part = parts[1].split(" in ")[1].strip()
            title_location = location_part
    
    # Try to find location in snippet
    snippet_location = None
    location_patterns = [
        r"location:?\s*([^\.;]+)",
        r"in\s+([A-Za-z\s,]+(?:remote|hybrid|on-site))",
        r"(?:remote|hybrid|on-site)",
    ]
    
    for pattern in location_patterns:
        matches = re.search(pattern, snippet, re.IGNORECASE)
        if matches:
            snippet_location = matches.group(1).strip() if len(matches.groups()) > 0 else matches.group(0).strip()
            break

    # Return the most reliable location found, or default
    return title_location or snippet_location or default_location or "Not specified"

def extract_salary(text: str) -> str:
    """Extract salary information from text"""
    salary_patterns = [
        r"(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:\s*-\s*\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)?(?:\s*(?:per|a|/)\s*(?:year|yr|month|mo|hour|hr|annum))?)",
        r"((?:USD|EUR|GBP|AUD|CAD)\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:\s*-\s*(?:USD|EUR|GBP|AUD|CAD)\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)?)",
        r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|AUD|CAD)(?:\s*-\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|AUD|CAD))?)"
    ]
    
    for pattern in salary_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            return matches.group(1)
    
    return "Salary not specified"

def get_job_details(url: str) -> Dict[str, Any]:
    """
    Fetch and parse full job details from the URL.
    
    Args:
        url (str): URL of the job listing
        
    Returns:
        Dict: Detailed job information
    """
    try:
        # Try various user agents to avoid being blocked
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
        ]
        headers = {
            "User-Agent": user_agents[0],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        
        # First attempt with default settings
        response = requests.get(url, headers=headers, timeout=15)
        
        # If initial request fails, try alternative methods
        if response.status_code != 200:
            # Try with different user agent
            for agent in user_agents[1:]:
                headers["User-Agent"] = agent
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    break
                    
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Convert HTML to markdown for easier text processing
        text_content = h2t.handle(response.text)
        
        # Extract job details
        description = extract_job_description(soup, text_content)
        requirements = extract_job_requirements(soup, text_content)
        
        # If description and requirements are not properly extracted, try searching for job title on DuckDuckGo
        if not description or not requirements:
            # Try to extract job title and company
            title = ""
            company = ""
            
            # Extract title from meta tags or other elements
            title_tag = soup.find("title")
            if title_tag and title_tag.text:
                title_parts = title_tag.text.split(" - ")
                if len(title_parts) > 0:
                    title = title_parts[0].strip()
                if len(title_parts) > 1:
                    company = title_parts[1].strip()
            
            # If we have a title, search for more information
            if title:
                # Use DuckDuckGo to search for job information
                search_query = f"{title} job description"
                if company:
                    search_query += f" {company}"
                
                try:
                    with DDGS() as ddgs:
                        # Get first 3 results
                        alt_results = list(ddgs.text(search_query, max_results=3))
                        
                        # Try to extract information from alternate sources
                        alt_description = ""
                        alt_requirements = []
                        
                        for result in alt_results:
                            try:
                                alt_url = result.get("href", "")
                                alt_headers = {"User-Agent": user_agents[2]}
                                alt_response = requests.get(alt_url, headers=alt_headers, timeout=10)
                                
                                if alt_response.status_code == 200:
                                    alt_soup = BeautifulSoup(alt_response.text, 'html.parser')
                                    alt_text = h2t.handle(alt_response.text)
                                    
                                    if not description:
                                        description = extract_job_description(alt_soup, alt_text)
                                    
                                    if not requirements:
                                        requirements = extract_job_requirements(alt_soup, alt_text)
                                    
                                    # If we got both, break
                                    if description and requirements:
                                        break
                            except Exception:
                                continue
                except Exception:
                    pass
        
        # If we still don't have a description, use LLM to generate one
        if not description:
            # Generate a generic description based on the job title
            description = f"This job listing is for a {url.split('/')[-1].replace('-', ' ').title()} position. The full job details and requirements can be accessed on the original job posting."
        
        # If we still don't have requirements, extract them from text_content
        if not requirements:
            # Look for keyword patterns that might indicate requirements
            requirement_keywords = [
                "required", "qualification", "skill", "experience", "knowledge", 
                "proficiency", "ability", "competency", "education", "degree"
            ]
            
            potential_requirements = []
            for keyword in requirement_keywords:
                pattern = r'(?:^|\n|\s)(' + keyword + r'[^\.;:]*(?:\.|\n|$))'
                matches = re.finditer(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    req = match.group(1).strip()
                    if len(req) > 10:  # Only include if substantial
                        potential_requirements.append(req)
            
            if potential_requirements:
                requirements = potential_requirements[:10]
            else:
                # Generic requirements based on job title
                job_title = url.split('/')[-1].replace('-', ' ').title()
                requirements = [
                    f"Relevant experience in {job_title} or related field",
                    "Strong communication skills",
                    "Problem-solving abilities",
                    "Ability to work effectively in a team"
                ]
        
        job_details = {
            "description": description,
            "requirements": requirements,
            "salary": extract_salary(text_content),
            "job_type": extract_job_type(text_content),
            "benefits": extract_benefits(text_content),
            "application_link": extract_application_link(soup, url),
            "full_text": text_content[:5000]  # Limit the full text to prevent overwhelming
        }
        
        return job_details
    except Exception as e:
        print(f"Error fetching job details: {str(e)}")
        # Create fallback job details using the URL
        job_title = url.split('/')[-1].replace('-', ' ').title()
        
        return {
            "description": f"This is a job listing for a {job_title} position. The original job posting contains more detailed information.",
            "requirements": [
                f"Experience with {job_title} or similar roles",
                "Relevant skills and qualifications",
                "Education requirements as specified in the job posting",
                "Communication and teamwork skills"
            ],
            "salary": "Please refer to the original job listing for salary information",
            "job_type": "Full-time (refer to original listing for confirmation)",
            "benefits": ["Visit the original job listing for complete benefits information"],
            "application_link": url,
            "full_text": f"This is a simplified version of the job listing. Please visit the original posting at {url} for complete details."
        }

def extract_job_description(soup: BeautifulSoup, text_content: str) -> str:
    """Extract job description from parsed HTML"""
    # Try to find job description section in the HTML
    description_section = None
    
    # Common selectors for job descriptions
    description_selectors = [
        "div.job-description", 
        "div.description", 
        "#job-description",
        ".jobSectionHeader",
        "[data-testid='jobDescriptionText']",
        ".description__text"
    ]
    
    for selector in description_selectors:
        section = soup.select_one(selector)
        if section:
            description_section = section.get_text(strip=True)
            break
    
    # If can't find it with selectors, extract from text content
    if not description_section:
        # Look for common section headers
        patterns = [
            r"(?:Job|Position) Description[:\n](.*?)(?:Requirements|Qualifications|Responsibilities|About)",
            r"About the job[:\n](.*?)(?:Requirements|Qualifications|Responsibilities)",
            r"Overview[:\n](.*?)(?:Requirements|Qualifications|Responsibilities)",
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text_content, re.DOTALL | re.IGNORECASE)
            if matches:
                description_section = matches.group(1).strip()
                break
    
    # Fallback to first 500 characters if no description found
    if not description_section:
        description_section = text_content[:500] + "..."
        
    return description_section

def extract_job_requirements(soup: BeautifulSoup, text_content: str) -> List[str]:
    """Extract job requirements as a list"""
    requirements = []
    
    # Try to find requirements section
    req_patterns = [
        r"Requirements?[:\n](.*?)(?:Benefits|Apply|About Us|Company)",
        r"Qualifications?[:\n](.*?)(?:Benefits|Apply|About Us|Company)",
        r"Skills[:\n](.*?)(?:Benefits|Apply|About Us|Company)",
    ]
    
    req_section = None
    for pattern in req_patterns:
        matches = re.search(pattern, text_content, re.DOTALL | re.IGNORECASE)
        if matches:
            req_section = matches.group(1).strip()
            break
    
    if req_section:
        # Extract bullet points
        bullet_points = re.findall(r"[\*\-\•]\s*([^\n\*\-\•]+)", req_section)
        if bullet_points:
            requirements = [point.strip() for point in bullet_points if point.strip()]
        else:
            # Split by newlines if no bullet points found
            lines = [line.strip() for line in req_section.split('\n') if line.strip()]
            requirements = [line for line in lines if len(line) > 15]  # Filter out short lines
    
    # If no requirements found, look for keywords
    if not requirements:
        skill_keywords = [
            "experience with", "proficient in", "knowledge of", "degree in",
            "years of experience", "background in", "skill", "ability to"
        ]
        
        for keyword in skill_keywords:
            matches = re.finditer(r"{}[^.]+\.".format(keyword), text_content, re.IGNORECASE)
            for match in matches:
                requirements.append(match.group(0).strip())
    
    # Remove duplicates and limit to 10 requirements
    requirements = list(dict.fromkeys(requirements))[:10]
    return requirements

def extract_job_type(text_content: str) -> str:
    """Extract job type (full-time, part-time, contract, etc.)"""
    job_type_patterns = [
        r"(?:Job|Employment) Type:?\s*([^\n\.;]+)",
        r"(Full[- ]Time|Part[- ]Time|Contract|Temporary|Freelance|Permanent|Remote)"
    ]
    
    for pattern in job_type_patterns:
        matches = re.search(pattern, text_content, re.IGNORECASE)
        if matches:
            return matches.group(1).strip()
    
    # Look for keywords
    job_type_keywords = ["full-time", "part-time", "contract", "temporary", "freelance", "permanent", "remote", "hybrid"]
    for keyword in job_type_keywords:
        if re.search(r'\b{}\b'.format(keyword), text_content, re.IGNORECASE):
            return keyword.title()
    
    return "Not specified"

def extract_benefits(text_content: str) -> List[str]:
    """Extract benefits offered by the job"""
    benefits = []
    
    # Try to find benefits section
    benefit_section = None
    benefit_patterns = [
        r"Benefits[:\n](.*?)(?:Apply|About Us|Company)",
        r"Perks[:\n](.*?)(?:Apply|About Us|Company)",
        r"What we offer[:\n](.*?)(?:Apply|About Us|Company)",
    ]
    
    for pattern in benefit_patterns:
        matches = re.search(pattern, text_content, re.DOTALL | re.IGNORECASE)
        if matches:
            benefit_section = matches.group(1).strip()
            break
    
    if benefit_section:
        # Extract bullet points
        bullet_points = re.findall(r"[\*\-\•]\s*([^\n\*\-\•]+)", benefit_section)
        if bullet_points:
            benefits = [point.strip() for point in bullet_points if point.strip()]
        else:
            # Split by newlines if no bullet points found
            lines = [line.strip() for line in benefit_section.split('\n') if line.strip()]
            benefits = [line for line in lines if len(line) > 10]  # Filter out short lines
    
    # If no benefits found, look for common benefit keywords
    if not benefits:
        benefit_keywords = [
            "health insurance", "dental insurance", "vision insurance", "401k", "retirement",
            "paid time off", "pto", "vacation", "remote work", "flexible", "bonus"
        ]
        
        for keyword in benefit_keywords:
            if re.search(r'\b{}\b'.format(keyword), text_content, re.IGNORECASE):
                benefits.append(keyword.title())
    
    # Remove duplicates and limit to 8 benefits
    benefits = list(dict.fromkeys(benefits))[:8]
    return benefits

def extract_application_link(soup: BeautifulSoup, default_url: str) -> str:
    """Extract direct application link if available"""
    # Common apply button selectors
    apply_selectors = [
        "a.apply-button", 
        "a.job-apply", 
        "a[data-automation='job-detail-apply']",
        "a:contains('Apply')",
        "a.btn-apply",
        ".jobsearch-IndeedApplyButton"
    ]
    
    for selector in apply_selectors:
        try:
            apply_button = soup.select_one(selector)
            if apply_button and apply_button.get('href'):
                return apply_button['href']
        except Exception:
            continue
    
    # Return the original URL if no apply button found
    return default_url

def analyze_job_fit(job_details: Dict[str, Any], resume_text: str, llm) -> Dict[str, Any]:
    """
    Analyze how well a candidate's resume matches the job requirements.
    
    Args:
        job_details (Dict): Detailed job information
        resume_text (str): The candidate's resume text
        llm: The language model for analysis
        
    Returns:
        Dict: Analysis results with match score and feedback
    """
    try:
        # Extract skills and requirements from job description
        job_description = job_details.get("description", "")
        job_requirements = job_details.get("requirements", [])
        
        # Combine requirements into a single string
        requirements_text = "\n".join(f"- {req}" for req in job_requirements)
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert career advisor and job match analyzer. Compare the candidate's resume with the job details below.
        
        JOB DESCRIPTION:
        {job_description}
        
        JOB REQUIREMENTS:
        {requirements_text}
        
        CANDIDATE RESUME:
        {resume_text}
        
        Please analyze how well the candidate's resume matches this job and provide:
        1. A match percentage (0-100%)
        2. Key matching qualifications the candidate has
        3. Important missing qualifications or experience
        4. Suggestions for how the candidate could improve their resume for this specific role
        5. 3-5 specific skills the candidate should develop to be a stronger match
        
        Format your response as a JSON object with the following keys:
        - "match_percentage": a number from 0-100
        - "matching_qualifications": a list of strings
        - "missing_qualifications": a list of strings
        - "resume_improvement_tips": a list of strings
        - "skills_to_develop": a list of strings
        """
        
        # Get analysis from LLM
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Parse JSON response
        # Try to find JSON object in the response
        json_pattern = r'```json\s*(.*?)\s*```'
        json_match = re.search(json_pattern, response.content, re.DOTALL)
        
        if json_match:
            analysis_json = json.loads(json_match.group(1))
        else:
            # Try to extract anything that looks like a JSON object
            json_pattern = r'{[\s\S]*}'
            json_match = re.search(json_pattern, response.content, re.DOTALL)
            if json_match:
                analysis_json = json.loads(json_match.group(0))
            else:
                # Fallback
                analysis_json = {
                    "match_percentage": 50,
                    "matching_qualifications": ["Unable to parse LLM response"],
                    "missing_qualifications": ["Unable to parse LLM response"],
                    "resume_improvement_tips": ["Unable to parse LLM response"],
                    "skills_to_develop": ["Unable to parse LLM response"]
                }
        
        return analysis_json
    except Exception as e:
        print(f"Error analyzing job fit: {str(e)}")
        return {
            "match_percentage": 0,
            "matching_qualifications": ["Error in analysis"],
            "missing_qualifications": ["Error in analysis"],
            "resume_improvement_tips": ["Unable to complete analysis"],
            "skills_to_develop": ["Unable to complete analysis"]
        }

def suggest_courses_for_skills(skills_to_develop: List[str], llm) -> List[Dict[str, str]]:
    """
    Suggest courses or resources to develop the required skills.
    
    Args:
        skills_to_develop (List[str]): List of skills the candidate needs to develop
        llm: The language model for suggestions
        
    Returns:
        List[Dict]: Suggestions with skill, course name, platform, and URL
    """
    try:
        skills_text = "\n".join(f"- {skill}" for skill in skills_to_develop)
        
        prompt = f"""
        You are an expert in career development and education. Based on the skills below that a job candidate needs to develop,
        suggest specific courses, certifications, or resources for each skill.
        
        SKILLS TO DEVELOP:
        {skills_text}
        
        For each skill, provide:
        1. A specific course, certification, or resource name
        2. The platform or provider (e.g., Coursera, Udemy, LinkedIn Learning, etc.)
        3. Why this resource is good for developing this skill
        
        Format your response as a JSON array with objects containing:
        - "skill": the skill name
        - "course_name": name of recommended course/certification
        - "platform": where to find the course
        - "reason": brief explanation of why this is recommended
        
        Return ONLY a valid JSON response.
        """
        
        # Get suggestions from LLM
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Parse JSON response
        # Try to find JSON array in the response
        json_pattern = r'```json\s*(.*?)\s*```'
        json_match = re.search(json_pattern, response.content, re.DOTALL)
        
        if json_match:
            suggestions = json.loads(json_match.group(1))
        else:
            # Try to extract anything that looks like a JSON array
            json_pattern = r'\[\s*{[\s\S]*}\s*\]'
            json_match = re.search(json_pattern, response.content, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group(0))
            else:
                # Fallback with dummy data
                suggestions = [
                    {
                        "skill": skills_to_develop[0] if skills_to_develop else "Professional Skills",
                        "course_name": "Error retrieving course suggestions",
                        "platform": "Multiple platforms available",
                        "reason": "Please try again or search for courses related to these skills online"
                    }
                ]
        
        return suggestions
    except Exception as e:
        print(f"Error suggesting courses: {str(e)}")
        return [
            {
                "skill": "Error Analysis",
                "course_name": "Error retrieving course suggestions",
                "platform": "N/A",
                "reason": "An error occurred during analysis"
            }
        ]