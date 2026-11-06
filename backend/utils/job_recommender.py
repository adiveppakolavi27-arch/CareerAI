import re

from backend.utils.job_api import search_jobs


def recommend_jobs(skills, location="India"):

    if not skills:
        return {
            "success": False,
            "message": "No resume skills found. Please analyse your resume first.",
            "jobs": []
        }

    recommended_jobs = []
    seen_ids = set()

    # Use up to 3 skills for job searches
    search_skills = skills[:3]

    for skill in search_skills:

        result = search_jobs(
            keyword=skill,
            location=location,
            results_per_page=10
        )

        if not result["success"]:
            continue

        for job in result["jobs"]:

            job_id = job.get("id")

            if job_id and job_id not in seen_ids:

                seen_ids.add(job_id)

                recommended_jobs.append(job)

    if not recommended_jobs:
        return {
            "success": False,
            "message": "No matching jobs found. Try searching in another location.",
            "jobs": []
        }

    return {
        "success": True,
        "message": "Job recommendations generated successfully.",
        "jobs": recommended_jobs[:20]
    }