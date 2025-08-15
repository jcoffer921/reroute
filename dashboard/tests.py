from django.test import TestCase
from django.contrib.auth.models import User
from resumes.models import Resume
from job_list.models import Job
from core.models import Skill
from job_list.matching import match_jobs_for_user

class JobMatchingTest(TestCase):
    def setUp(self):
        # Create user and resume
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.resume = Resume.objects.create(user=self.user)

        # Create and fetch skills from DB to ensure they are saved properly
        Skill.objects.bulk_create([
            Skill(name="Plumbing"),
            Skill(name="Customer Service")
        ])
        self.skill1 = Skill.objects.get(name="Plumbing")
        self.skill2 = Skill.objects.get(name="Customer Service")

        # Assign M2M relationship using Skill instances
        self.resume.skills.set([self.skill1])

        # Create jobs
        self.job1 = Job.objects.create(title="Maintenance Tech")
        self.job2 = Job.objects.create(title="Retail Associate")

        # Assign job skills
        self.job1.skills_required.set([self.skill1])
        self.job2.skills_required.set([self.skill2])

    def test_match_jobs_for_user_returns_correct_jobs(self):
        from job_list.matching import match_jobs_for_user
        matched_jobs = match_jobs_for_user(self.user)

        self.assertIn(self.job1, matched_jobs)
        self.assertNotIn(self.job2, matched_jobs)

