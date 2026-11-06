from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from sqlalchemy.exc import IntegrityError

from database.database import db
from backend.models.saved_job import SavedJob


saved_jobs_bp = Blueprint("saved_jobs", __name__)


# -----------------------------------------
# SAVE A JOB
# -----------------------------------------

@saved_jobs_bp.route("/save-job", methods=["POST"])
@login_required
def save_job():

    job_id = request.form.get("job_id", "").strip()
    title = request.form.get("title", "").strip()

    if not job_id or not title:
        flash("Job information is incomplete.", "warning")
        return redirect(url_for("jobs.job_finder"))

    source = request.form.get("source", "Adzuna").strip() or "Adzuna"

    existing_job = SavedJob.query.filter_by(
        user_id=current_user.id,
        job_id=job_id,
        source=source
    ).first()

    if existing_job:
        flash("You have already saved this job.", "info")
        return redirect(url_for("saved_jobs.saved_jobs_page"))

    job = SavedJob(
        user_id=current_user.id,
        job_id=job_id,
        title=title,
        company=request.form.get("company", "").strip(),
        location=request.form.get("location", "").strip(),
        description=request.form.get("description", "").strip(),
        apply_url=request.form.get("apply_url", "").strip(),
        source=source
    )

    try:
        db.session.add(job)
        db.session.commit()

        flash("Job saved successfully!", "success")

    except IntegrityError:
        db.session.rollback()
        flash("This job is already saved.", "info")

    except Exception:
        db.session.rollback()
        flash("Unable to save this job. Please try again.", "danger")

    return redirect(url_for("saved_jobs.saved_jobs_page"))


# -----------------------------------------
# DISPLAY SAVED JOBS
# -----------------------------------------

@saved_jobs_bp.route("/saved-jobs")
@login_required
def saved_jobs_page():

    jobs = SavedJob.query.filter_by(
        user_id=current_user.id
    ).order_by(
        SavedJob.created_at.desc()
    ).all()

    return render_template(
        "saved_jobs.html",
        jobs=jobs
    )


# -----------------------------------------
# REMOVE A SAVED JOB
# -----------------------------------------

@saved_jobs_bp.route(
    "/remove-saved-job/<int:saved_job_id>",
    methods=["POST"]
)
@login_required
def remove_saved_job(saved_job_id):

    job = SavedJob.query.filter_by(
        id=saved_job_id,
        user_id=current_user.id
    ).first()

    if job is None:
        flash("Saved job not found.", "warning")
    else:
        db.session.delete(job)
        db.session.commit()

        flash("Job removed from your saved jobs.", "success")

    return redirect(url_for("saved_jobs.saved_jobs_page"))