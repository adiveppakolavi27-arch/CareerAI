import os
import uuid
import json

from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    send_file,
    abort
)

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from database.database import db
from backend.models.analysis_history import AnalysisHistory

from backend.utils.pdf_extractor import extract_text_from_pdf
from backend.utils.skills_extractor import extract_skills
from backend.utils.job_matcher import analyze_job_match
from backend.utils.ats_scorer import score_resume
from backend.utils.gemini_analyzer import analyze_resume_with_gemini
from backend.utils.report_generator import generate_resume_report
from backend.utils.resume_quality import analyze_resume_quality


analysis = Blueprint("analysis", __name__)

ALLOWED_EXTENSIONS = {"pdf"}


# ==========================================
# CHECK ALLOWED FILE EXTENSION
# ==========================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ==========================================
# RESUME UPLOAD AND ANALYSIS
# ==========================================

@analysis.route("/upload", methods=["GET", "POST"])
@login_required
def upload_resume():

    if request.method == "POST":

        job_description = request.form.get(
            "job_description", ""
        ).strip()

        # 1. Check uploaded file

        if "resume" not in request.files:

            return render_template(
                "upload.html",
                error="Please select a resume.",
                job_description=job_description
            )

        file = request.files["resume"]

        if file.filename == "":

            return render_template(
                "upload.html",
                error="No file selected.",
                job_description=job_description
            )

        # 2. Check file extension

        if not allowed_file(file.filename):

            return render_template(
                "upload.html",
                error="Only PDF files are allowed.",
                job_description=job_description
            )

        # 3. Secure filename

        original_name = secure_filename(file.filename)

        if not original_name:

            return render_template(
                "upload.html",
                error="Invalid filename.",
                job_description=job_description
            )

        # 4. Validate PDF signature

        file_header = file.stream.read(5)
        file.stream.seek(0)

        if file_header != b"%PDF-":

            return render_template(
                "upload.html",
                error="The uploaded file is not a valid PDF.",
                job_description=job_description
            )

        # 5. Create temporary upload file

        unique_name = f"{uuid.uuid4().hex}.pdf"

        upload_folder = current_app.config["UPLOAD_FOLDER"]

        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(
            upload_folder,
            unique_name
        )

        try:

            # ----------------------------------
            # STEP 1: SAVE PDF
            # ----------------------------------

            file.save(file_path)

            # ----------------------------------
            # STEP 2: EXTRACT PDF TEXT
            # ----------------------------------

            resume_text = extract_text_from_pdf(file_path)

            if not resume_text:

                return render_template(
                    "upload.html",
                    error=(
                        "No readable text found in this PDF. "
                        "Scanned PDFs may require OCR."
                    ),
                    job_description=job_description
                )

            # ----------------------------------
            # STEP 3: EXTRACT SKILLS
            # ----------------------------------

            skills = extract_skills(resume_text)

            # ----------------------------------
            # STEP 4: CALCULATE ATS SCORE
            # ----------------------------------

            ats_result = score_resume(
                resume_text,
                skills
            )

            # ----------------------------------
            # STEP 5: JOB DESCRIPTION MATCHING
            # ----------------------------------

            jd_result = None

            if job_description:

                jd_result = analyze_job_match(
                    skills,
                    job_description
                )

            # ----------------------------------
            # STEP 6: RESUME QUALITY ANALYSIS
            # ----------------------------------

            quality_result = analyze_resume_quality(
                resume_text
            )

            # ----------------------------------
            # STEP 7: GEMINI AI ANALYSIS
            # ----------------------------------

            gemini_result = analyze_resume_with_gemini(
                resume_text,
                job_description
            )

            # ----------------------------------
            # STEP 8: GENERATE PROFESSIONAL PDF
            # ----------------------------------

            report_folder = os.path.join(
                current_app.root_path,
                "reports"
            )

            report_name = generate_resume_report(

                report_folder=report_folder,

                user_id=current_user.id,

                filename=original_name,

                ats_result=ats_result,

                skills=skills,

                jd_result=jd_result,

                gemini_result=gemini_result,

                # NEW: Pass resume quality results
                quality_result=quality_result
            )

            # ----------------------------------
            # STEP 9: SAVE ANALYSIS HISTORY
            # ----------------------------------

            match_percentage = 0

            if jd_result:

                match_percentage = jd_result.get(
                    "match_percentage", 0
                )

            history_record = AnalysisHistory(

                user_id=current_user.id,

                filename=original_name,

                ats_score=ats_result["total_score"],

                ats_category=ats_result["category"],

                match_percentage=match_percentage,

                skills=json.dumps(skills),

                report_name=report_name
            )

            db.session.add(history_record)

            db.session.commit()

            current_app.logger.info(
                "Analysis history saved. ID: %s",
                history_record.id
            )

            # ----------------------------------
            # STEP 10: DISPLAY RESULTS
            # ----------------------------------

            return render_template(

                "upload.html",

                success="Resume analyzed successfully!",

                filename=original_name,

                resume_text=resume_text[:10000],

                skills=skills,

                ats_score=ats_result["total_score"],

                ats_result=ats_result,

                quality_result=quality_result,

                job_description=job_description,

                jd_result=jd_result,

                gemini_result=gemini_result,

                report_name=report_name
            )

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "Resume analysis or history saving failed"
            )

            return render_template(
                "upload.html",
                error=(
                    "Unable to complete the resume analysis. "
                    "Please check the VS Code terminal."
                ),
                job_description=job_description
            )

        finally:

            # Always delete temporary uploaded PDF

            if os.path.exists(file_path):

                os.remove(file_path)

    # GET REQUEST

    return render_template("upload.html")


# ==========================================
# ANALYSIS HISTORY PAGE
# ==========================================

@analysis.route("/history")
@login_required
def analysis_history():

    records = (

        AnalysisHistory.query

        .filter_by(user_id=current_user.id)

        .order_by(AnalysisHistory.created_at.desc())

        .all()
    )

    history_data = []

    for record in records:

        try:

            saved_skills = json.loads(
                record.skills or "[]"
            )

        except (json.JSONDecodeError, TypeError):

            saved_skills = []

        history_data.append({

            "id": record.id,

            "filename": record.filename,

            "ats_score": record.ats_score,

            "ats_category": record.ats_category,

            "match_percentage": record.match_percentage,

            "skills": saved_skills,

            "report_name": record.report_name,

            "created_at": record.created_at
        })

    return render_template(
        "history.html",
        history=history_data
    )


# ==========================================
# DOWNLOAD PDF ANALYSIS REPORT
# ==========================================

@analysis.route("/download-report/<report_name>")
@login_required
def download_report(report_name):

    # 1. Prevent directory traversal

    if os.path.basename(report_name) != report_name:

        abort(404)

    # 2. Check report ownership

    expected_prefix = f"user_{current_user.id}_"

    if not report_name.startswith(expected_prefix):

        abort(404)

    # 3. Allow only PDF reports

    if not report_name.endswith(".pdf"):

        abort(404)

    # 4. Find report file

    report_folder = os.path.join(
        current_app.root_path,
        "reports"
    )

    report_path = os.path.join(
        report_folder,
        report_name
    )

    # 5. Check file existence

    if not os.path.isfile(report_path):

        abort(404)

    # 6. Download report

    return send_file(

        report_path,

        as_attachment=True,

        download_name="AI_Resume_Analysis_Report.pdf",

        mimetype="application/pdf"
    )