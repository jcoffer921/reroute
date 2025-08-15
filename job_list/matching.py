from job_list.models import Job
from job_list.user.views import match_jobs


def match_jobs_for_user(user):
    from resumes.models import Resume, Skill

    # Try to fetch the user's resume
    resume = Resume.objects.filter(user=user).first()

    if not resume or not resume.skills.exists():
        return []

    # Normalize and parse the user's skills into a lowercase set
    user_skills = {skill.name.strip().lower() for skill in resume.skills.all()}

    scored_jobs = []

    # Loop through all jobs with their required skills preloaded
    for job in Job.objects.prefetch_related('skills_required'):
        job_skill_names = {s.name.strip().lower() for s in job.skills_required.all()}

        # Calculate overlap between user and job skills
        overlap = user_skills & job_skill_names

        if overlap:
            score = len(overlap)  # Count how many skills matched
            scored_jobs.append((score, job))

    # Sort by score descending (more matches = higher rank)
    scored_jobs.sort(key=lambda x: x[0], reverse=True)

    # Return only the job objects in sorted order
    return [job for score, job in scored_jobs]
