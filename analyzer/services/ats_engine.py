# analyzer/services/ats_engine.py
import re
from collections import Counter

class ATSEngine:
    """Core ATS scoring algorithm - working version"""
    
    def __init__(self):
        self.stop_words = {'and', 'or', 'the', 'a', 'an', 'of', 'to', 'for', 'in', 'on', 'at', 'with', 'by', 'is', 'are', 'was', 'were'}
        
        # Common skills dictionary
        self.common_skills = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 
            'django', 'flask', 'spring', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'sql', 'mongodb', 'postgresql', 'mysql', 'git', 'jenkins', 'ci/cd',
            'machine learning', 'ai', 'data science', 'analytics', 'tableau', 'power bi',
            'agile', 'scrum', 'project management', 'leadership', 'communication',
            'html', 'css', 'rest api', 'graphql', 'typescript', 'redux', 'tailwind',
            'excel', 'word', 'powerpoint', 'salesforce', 'hubspot', 'photoshop', 'illustrator'
        }
    
    def extract_skills_from_jd(self, job_description):
        """Extract key skills from job description"""
        jd_lower = job_description.lower()
        found_skills = []
        
        for skill in self.common_skills:
            if skill in jd_lower:
                found_skills.append(skill)
        
        # Extract words that appear frequently (potential custom skills)
        words = re.findall(r'\b[a-z][a-z]{3,}\b', jd_lower)  # Words with 4+ letters
        word_freq = Counter([w for w in words if w not in self.stop_words])
        
        # Add top 5 most frequent words as potential skills
        custom_skills = [word for word, count in word_freq.most_common(5) if count > 2]
        
        # Combine and remove duplicates
        all_skills = list(set(found_skills + custom_skills))
        
        return all_skills[:15]  # Return top 15 skills
    
    def calculate_keyword_match(self, resume_text, job_description):
        """Calculate keyword match percentage"""
        jd_skills = self.extract_skills_from_jd(job_description)
        resume_lower = resume_text.lower()
        
        found = []
        missing = []
        
        for skill in jd_skills:
            if skill in resume_lower:
                found.append(skill)
            else:
                missing.append(skill)
        
        match_percentage = (len(found) / len(jd_skills)) * 100 if jd_skills else 0
        
        return {
            'found': found,
            'missing': missing,
            'percentage': round(match_percentage, 1)
        }
    
    def calculate_semantic_similarity(self, resume_text, job_description):
        """Calculate similarity score (simplified version without sklearn)"""
        # Simple word overlap calculation
        resume_words = set(re.findall(r'\b[a-z][a-z]{3,}\b', resume_text.lower()))
        jd_words = set(re.findall(r'\b[a-z][a-z]{3,}\b', job_description.lower()))
        
        # Remove stop words
        resume_words = resume_words - self.stop_words
        jd_words = jd_words - self.stop_words
        
        if not jd_words:
            return 50
        
        # Calculate overlap
        common_words = resume_words.intersection(jd_words)
        similarity = (len(common_words) / len(jd_words)) * 100
        
        return min(100, similarity)
    
    def analyze_profile_compatibility(self, resume_text, job_description):
        """Check job title alignment and experience level"""
        score = 50  # Start at 50%
        
        # Extract potential job titles from resume
        title_pattern = r'(?:as a|as an|experienced|seeking|position of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        titles = re.findall(title_pattern, resume_text, re.IGNORECASE)
        
        # Check if any title matches job description
        jd_lower = job_description.lower()
        for title in titles:
            if title.lower() in jd_lower:
                score += 25
                break
        
        # Check for seniority indicators
        if 'senior' in resume_text.lower() and 'senior' in jd_lower:
            score += 10
        if 'lead' in resume_text.lower() and 'lead' in jd_lower:
            score += 10
        if 'manager' in resume_text.lower() and 'manager' in jd_lower:
            score += 10
        
        # Penalty for junior applying to senior role
        if 'junior' in resume_text.lower() and 'senior' in jd_lower:
            score -= 15
        if 'entry' in resume_text.lower() and 'senior' in jd_lower:
            score -= 15
        
        return max(0, min(100, score))
    
    def analyze_format(self, resume_text):
        """Analyze resume format and structure"""
        score = 70  # Start at 70%
        
        # Check for section headers
        sections = ['summary', 'experience', 'education', 'skills', 'projects', 'certifications', 'work history']
        found_sections = 0
        
        for section in sections:
            if re.search(r'\b' + section + r'\b', resume_text.lower()):
                found_sections += 1
        
        section_score = (found_sections / len(sections)) * 20
        score += section_score
        
        # Check for bullet points (good formatting)
        bullet_count = len(re.findall(r'[•\-*]\s+', resume_text))
        if bullet_count > 10:
            score += 10
        elif bullet_count > 5:
            score += 5
        
        # Check for metrics (numbers with %, $, or numbers with words)
        metric_count = len(re.findall(r'\b\d+%|\$\d+|\b\d+\s+(?:years|months|people|members|clients)\b', resume_text, re.IGNORECASE))
        if metric_count > 5:
            score += 10
        elif metric_count > 2:
            score += 5
        
        # Check for email and phone (contact info)
        if re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', resume_text):
            score += 5
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', resume_text):
            score += 5
        
        return min(100, score)
    
    def calculate_overall_score(self, resume_text, job_description):
        """Calculate final weighted ATS score"""
        
        # 1. Critical Skills Match (40% weight)
        keyword_result = self.calculate_keyword_match(resume_text, job_description)
        critical_score = keyword_result['percentage']
        
        # 2. Semantic Similarity (30% weight)
        semantic_score = self.calculate_semantic_similarity(resume_text, job_description)
        
        # 3. Profile Compatibility (15% weight)
        profile_score = self.analyze_profile_compatibility(resume_text, job_description)
        
        # 4. Format Score (15% weight)
        format_score = self.analyze_format(resume_text)
        
        # Weighted calculation
        total_score = (
            critical_score * 0.40 +
            semantic_score * 0.30 +
            profile_score * 0.15 +
            format_score * 0.15
        )
        
        return {
            'total_score': round(total_score, 1),
            'breakdown': {
                'critical_skills_match': round(critical_score, 1),
                'semantic_similarity': round(semantic_score, 1),
                'profile_compatibility': round(profile_score, 1),
                'format_score': round(format_score, 1)
            },
            'critical_skills': keyword_result['found'][:7],  # Top 7 found skills
            'missing_keywords': keyword_result['missing'][:10],  # Top 10 missing
            'found_keywords': keyword_result['found'][:20]
        }


# For testing the engine
if __name__ == "__main__":
    # Test the ATS Engine
    engine = ATSEngine()
    
    sample_resume = """
    John Doe - Senior Python Developer
    Summary: Experienced Python developer with 5 years of experience in Django and React.
    Skills: Python, Django, JavaScript, React, SQL, Git
    Experience: Senior Developer at Tech Corp (2020-2024)
    - Led a team of 5 developers
    - Increased efficiency by 30%
    Education: BS in Computer Science
    """
    
    sample_job = """
    Looking for a Senior Python Developer with experience in:
    - Python
    - Django
    - React
    - SQL
    - AWS
    - Leadership skills
    
    Requirements: 5+ years experience, team leadership
    """
    
    result = engine.calculate_overall_score(sample_resume, sample_job)
    
    print("ATS Score:", result['total_score'])
    print("\nBreakdown:")
    for key, value in result['breakdown'].items():
        print(f"  {key}: {value}%")
    print("\nFound Keywords:", result['found_keywords'][:5])
    print("Missing Keywords:", result['missing_keywords'][:5])