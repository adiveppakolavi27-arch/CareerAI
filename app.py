import os

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    send_from_directory
)

from dotenv import load_dotenv
from flask_login import LoginManager, login_required, current_user


# =========================================
# LOAD ENVIRONMENT VARIABLES
# =========================================

load_dotenv()


# =========================================
# DATABASE
# =========================================

from database.database import db


# =========================================
# DATABASE MODELS
# =========================================

from backend.models.user import User
from backend.models.analysis_history import AnalysisHistory
from backend.models.saved_job import SavedJob
from backend.models.application import Application
from backend.models.chat_history import ChatHistory
from backend.models.learning_progress import LearningProgress


# =========================================
# BLUEPRINTS
# =========================================

from backend.routes.auth import auth
from backend.routes.analysis import analysis
from backend.routes.jobs import jobs_bp
from backend.routes.saved_jobs import saved_jobs_bp
from backend.routes.applications import applications_bp
from backend.routes.career import career_bp


# =========================================
# CREATE FLASK APPLICATION
# =========================================

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)


# =========================================
# APPLICATION CONFIGURATION
# =========================================

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///resume_analyzer.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path,
    "uploads"
)


# =========================================
# CREATE REQUIRED FOLDERS
# =========================================

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

os.makedirs(
    os.path.join(app.root_path, "reports"),
    exist_ok=True
)


# =========================================
# INITIALIZE DATABASE
# =========================================

db.init_app(app)


# =========================================
# INITIALIZE FLASK LOGIN
# =========================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "auth.login"

login_manager.login_message = "Please log in to access this page."


@login_manager.user_loader
def load_user(user_id):

    try:
        return db.session.get(User, int(user_id))

    except (ValueError, TypeError):
        return None


# =========================================
# REGISTER BLUEPRINTS
# =========================================

app.register_blueprint(auth)

app.register_blueprint(analysis)

app.register_blueprint(jobs_bp)

app.register_blueprint(saved_jobs_bp)

app.register_blueprint(applications_bp)

app.register_blueprint(career_bp)


# =========================================
# CREATE DATABASE TABLES
# =========================================

with app.app_context():

    db.create_all()

    print("Database tables created successfully!")


# =========================================
# CAREERAI DASHBOARD
# =========================================

@app.route("/dashboard")
@login_required
def dashboard():

    latest_analysis = AnalysisHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        AnalysisHistory.created_at.desc()
    ).first()

    saved_jobs_count = SavedJob.query.filter_by(
        user_id=current_user.id
    ).count()

    applications = Application.query.filter_by(
        user_id=current_user.id
    ).all()

    applications_count = len(applications)

    applied_count = sum(
        1 for application in applications
        if (application.status or "").lower() == "applied"
    )

    interview_count = sum(
        1 for application in applications
        if (application.status or "").lower()
        in ["interview", "interviewing"]
    )

    selected_count = sum(
        1 for application in applications
        if (application.status or "").lower()
        in ["selected", "accepted"]
    )

    rejected_count = sum(
        1 for application in applications
        if (application.status or "").lower() == "rejected"
    )

    recent_saved_jobs = SavedJob.query.filter_by(
        user_id=current_user.id
    ).order_by(
        SavedJob.created_at.desc()
    ).limit(5).all()

    recent_applications = Application.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Application.applied_date.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        user=current_user,
        latest_analysis=latest_analysis,
        saved_jobs_count=saved_jobs_count,
        applications_count=applications_count,
        applied_count=applied_count,
        interview_count=interview_count,
        selected_count=selected_count,
        rejected_count=rejected_count,
        recent_saved_jobs=recent_saved_jobs,
        recent_applications=recent_applications
    )


# =========================================
# LEARNING DASHBOARD
# =========================================

@app.route("/learning-dashboard")
@login_required
def learning_dashboard():

    return render_template(
        "learning_dashboard.html"
    )


# =========================================
# ADVANCED LEARNING ROADMAP
# =========================================

@app.route("/learning-roadmap")
@login_required
def learning_roadmap():

    return render_template(
        "learning_roadmap.html"
    )


# =========================================
# INDIVIDUAL CAREER PATH PAGES
# =========================================

@app.route("/learning/<string:career>")
@login_required
def individual_learning(career):

    career_pages = {

        "python": "python.html",

        "artificial-intelligence": "artificial_intelligence.html",

        "machine-learning": "machine_learning.html",

        "deep-learning": "deep_learning.html",

        "data-science": "data_science.html",

        "sql": "sql.html",

        "full-stack": "full_stack.html",

        "dsa": "dsa.html",

        "generative-ai": "generative_ai.html",

        "placement": "placement.html"

    }

    page = career_pages.get(career)

    if not page:

        return jsonify({
            "success": False,
            "message": "Career path not found."
        }), 404

    return render_template(
        f"career_paths/{page}"
    )


# =========================================
# SAVE LEARNING PROGRESS
# =========================================

@app.route(
    "/api/learning-progress",
    methods=["POST"]
)
@login_required
def save_learning_progress():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "success": False,
            "message": "Invalid JSON data."
        }), 400

    roadmap = data.get("roadmap")
    topic = data.get("topic")
    completed = data.get("completed")

    if not isinstance(roadmap, str) or not roadmap.strip():

        return jsonify({
            "success": False,
            "message": "Roadmap name is required."
        }), 400

    if not isinstance(topic, str) or not topic.strip():

        return jsonify({
            "success": False,
            "message": "Topic name is required."
        }), 400

    if len(roadmap) > 100 or len(topic) > 255:

        return jsonify({
            "success": False,
            "message": "Roadmap or topic name is too long."
        }), 400

    if not isinstance(completed, bool):

        return jsonify({
            "success": False,
            "message": "Completed must be true or false."
        }), 400

    roadmap = roadmap.strip()

    topic = topic.strip()

    try:

        progress = LearningProgress.query.filter_by(
            user_id=current_user.id,
            roadmap=roadmap,
            topic=topic
        ).first()

        if progress:

            progress.completed = completed

        else:

            progress = LearningProgress(
                user_id=current_user.id,
                roadmap=roadmap,
                topic=topic,
                completed=completed
            )

            db.session.add(progress)

        db.session.commit()

        return jsonify({

            "success": True,

            "message": "Learning progress saved successfully.",

            "roadmap": roadmap,

            "topic": topic,

            "completed": progress.completed

        })

    except Exception:

        db.session.rollback()

        app.logger.exception(
            "Could not save learning progress."
        )

        return jsonify({
            "success": False,
            "message": "Unable to save learning progress."
        }), 500


# =========================================
# GET LEARNING PROGRESS
# =========================================

@app.route(
    "/api/learning-progress/<string:roadmap>",
    methods=["GET"]
)
@login_required
def get_learning_progress(roadmap):

    roadmap = roadmap.strip()

    if not roadmap or len(roadmap) > 100:

        return jsonify({
            "success": False,
            "message": "Invalid roadmap name."
        }), 400

    try:

        progress_records = LearningProgress.query.filter_by(
            user_id=current_user.id,
            roadmap=roadmap
        ).all()

        completed_count = sum(
            1 for item in progress_records
            if item.completed
        )

        saved_topics_count = len(progress_records)

        return jsonify({

            "success": True,

            "roadmap": roadmap,

            "saved_topics": saved_topics_count,

            "completed_topics": completed_count,

            "progress": [

                {
                    "topic": item.topic,
                    "completed": item.completed
                }

                for item in progress_records

            ]

        })

    except Exception:

        app.logger.exception(
            "Could not retrieve learning progress."
        )

        return jsonify({
            "success": False,
            "message": "Unable to retrieve learning progress."
        }), 500


# =========================================
# CAREERAI SERVICE WORKER
# =========================================

@app.route("/sw.js")
def service_worker():

    response = send_from_directory(
        app.static_folder,
        "sw.js",
        mimetype="application/javascript"
    )

    response.headers["Service-Worker-Allowed"] = "/"

    return response


# =========================================
# HOMEPAGE
# =========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================
# HEALTH CHECK
# =========================================

@app.route("/health")
def health():

    return jsonify({

        "success": True,

        "message": "CareerAI Backend is Running!"

    })


# =========================================
# DATABASE TEST
# =========================================

@app.route("/db-test")
def database_test():

    return jsonify({

        "success": True,

        "message": "Database Connected Successfully!",

        "total_users": User.query.count(),

        "total_analyses": AnalysisHistory.query.count()

    })


# =========================================
# DISPLAY REGISTERED ROUTES
# =========================================

print("\n========== REGISTERED ROUTES ==========")

for rule in app.url_map.iter_rules():

    print(
        f"{rule.endpoint:30} {rule.rule}"
    )

print("=======================================\n")


# =========================================
# RUN APPLICATION
# =========================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )