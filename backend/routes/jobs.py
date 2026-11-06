import json

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from backend.utils.job_api import search_jobs
from backend.utils.job_recommender import recommend_jobs
from backend.models.analysis_history import AnalysisHistory


# CREATE JOBS BLUEPRINT
jobs_bp = Blueprint("jobs", __name__)


# JOB FINDER
@jobs_bp.route("/jobs", methods=["GET", "POST"])
@login_required
def job_finder():

    jobs = []
    message = ""
    keyword = ""
    location = "India"
    total_jobs = 0

    if request.method == "POST":

        keyword = request.form.get("keyword", "").strip()
        location = request.form.get("location", "India").strip() or "India"

        if keyword:

            result = search_jobs(
                keyword=keyword,
                location=location
            )

            if result["success"]:
                jobs = result["jobs"]
                total_jobs = result.get("total_jobs", len(jobs))
            else:
                message = result["message"]

        else:
            message = "Please enter a job title or keyword."

    return render_template(
        "jobs.html",
        jobs=jobs,
        message=message,
        keyword=keyword,
        location=location,
        total_jobs=total_jobs
    )


# RESUME-BASED JOB RECOMMENDATIONS
@jobs_bp.route("/recommendations", methods=["GET", "POST"])
@login_required
def job_recommendations():

    jobs = []
    message = ""
    location = "India"

    latest_analysis = AnalysisHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        AnalysisHistory.created_at.desc()
    ).first()

    if not latest_analysis:
        message = "Please upload and analyse your resume first."

    else:

        try:
            skills = json.loads(latest_analysis.skills or "[]")

        except (json.JSONDecodeError, TypeError):
            skills = []

        if not skills:
            message = "No skills found. Please analyse your resume again."

        else:

            if request.method == "POST":
                location = request.form.get(
                    "location", "India"
                ).strip() or "India"

            result = recommend_jobs(
                skills=skills,
                location=location
            )

            if result["success"]:
                jobs = result["jobs"]
            else:
                message = result["message"]

    return render_template(
        "recommendation.html",
        jobs=jobs,
        message=message,
        location=location
    )