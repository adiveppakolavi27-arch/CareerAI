from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user
from database.database import db
from backend.models.application import Application

applications_bp = Blueprint("applications", __name__)


# VIEW APPLICATION TRACKER
@applications_bp.route("/applications")
@login_required
def application_tracker():

    applications = Application.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Application.applied_date.desc()
    ).all()

    return render_template(
        "applications.html",
        applications=applications
    )


# ADD APPLICATION
@applications_bp.route("/add-application", methods=["POST"])
@login_required
def add_application():

    job_title = request.form.get("job_title", "").strip()
    company = request.form.get("company", "").strip()
    location = request.form.get("location", "").strip()
    apply_url = request.form.get("apply_url", "").strip()
    job_id = request.form.get("job_id", "").strip()

    # Validate job title
    if not job_title:
        flash("Job title is required.", "warning")
        return redirect(url_for("applications.application_tracker"))

    # CHECK FOR DUPLICATE APPLICATION
    duplicate_query = Application.query.filter_by(
        user_id=current_user.id,
        job_title=job_title,
        company=company
    )

    if job_id:
        duplicate_query = duplicate_query.filter_by(job_id=job_id)

    existing_application = duplicate_query.first()

    if existing_application:
        flash(
            "You are already tracking this job!",
            "warning"
        )
        return redirect(url_for("applications.application_tracker"))

    # CREATE NEW APPLICATION
    application = Application(
        user_id=current_user.id,
        job_id=job_id or None,
        job_title=job_title,
        company=company,
        location=location,
        apply_url=apply_url,
        status="Applied"
    )

    try:

        db.session.add(application)
        db.session.commit()

        flash(
            "Job added to your Application Tracker successfully!",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to add application. Please try again.",
            "danger"
        )

    return redirect(url_for("applications.application_tracker"))


# UPDATE APPLICATION STATUS
@applications_bp.route(
    "/update-application/<int:application_id>",
    methods=["POST"]
)
@login_required
def update_application(application_id):

    application = Application.query.filter_by(
        id=application_id,
        user_id=current_user.id
    ).first_or_404()

    allowed_statuses = [
        "Applied",
        "In Progress",
        "Interview",
        "Selected",
        "Rejected"
    ]

    new_status = request.form.get("status", "").strip()

    if new_status not in allowed_statuses:

        flash("Invalid application status.", "warning")

        return redirect(url_for("applications.application_tracker"))

    application.status = new_status

    try:

        db.session.commit()

        flash(
            "Application status updated successfully!",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update application status.",
            "danger"
        )

    return redirect(url_for("applications.application_tracker"))


# UPDATE APPLICATION NOTES
@applications_bp.route(
    "/update-notes/<int:application_id>",
    methods=["POST"]
)
@login_required
def update_application_notes(application_id):

    application = Application.query.filter_by(
        id=application_id,
        user_id=current_user.id
    ).first_or_404()

    application.notes = request.form.get("notes", "").strip()

    try:

        db.session.commit()

        flash(
            "Application notes updated!",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update notes.",
            "danger"
        )

    return redirect(url_for("applications.application_tracker"))


# DELETE APPLICATION
@applications_bp.route(
    "/delete-application/<int:application_id>",
    methods=["POST"]
)
@login_required
def delete_application(application_id):

    application = Application.query.filter_by(
        id=application_id,
        user_id=current_user.id
    ).first_or_404()

    try:

        db.session.delete(application)
        db.session.commit()

        flash(
            "Application deleted successfully!",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to delete application.",
            "danger"
        )

    return redirect(url_for("applications.application_tracker"))