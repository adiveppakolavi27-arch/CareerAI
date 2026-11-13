import json

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    current_app
)

from flask_login import login_required, current_user

from database.database import db

from backend.utils.career_assistant import ask_career_assistant

from backend.models.analysis_history import AnalysisHistory
from backend.models.chat_history import ChatHistory


career_bp = Blueprint("career", __name__)

MAX_HISTORY_MESSAGES = 4


# =========================================
# CAREER ASSISTANT PAGE
# =========================================

@career_bp.route("/career")
@login_required
def career_page():

    return render_template("career_assistant.html")


# =========================================
# LOAD CHAT HISTORY
# =========================================

@career_bp.route("/career-history")
@login_required
def career_history():

    try:

        history = ChatHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(
            ChatHistory.created_at.desc()
        ).limit(50).all()

        history.reverse()

        conversations = []

        for chat in history:

            conversations.append({

                "question": chat.message,

                "answer": chat.response,

                "created_at": (
                    chat.created_at.strftime(
                        "%d %b %Y %I:%M %p"
                    )
                    if chat.created_at else ""
                )

            })

        return jsonify({
            "success": True,
            "history": conversations
        }), 200

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Career history loading failed."
        )

        return jsonify({
            "success": False,
            "error": "Unable to load conversation history."
        }), 500


# =========================================
# GET RESUME CONTEXT
# =========================================

def get_resume_context():

    latest_analysis = AnalysisHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        AnalysisHistory.created_at.desc()
    ).first()

    if not latest_analysis:

        return (
            "The user has not analysed a resume yet. "
            "Provide general guidance without assuming "
            "qualifications or experience."
        )

    try:

        raw_skills = latest_analysis.skills

        if isinstance(raw_skills, str):

            skills = json.loads(raw_skills or "[]")

        elif isinstance(raw_skills, list):

            skills = raw_skills

        else:

            skills = []

        if not isinstance(skills, list):
            skills = []

    except (json.JSONDecodeError, TypeError):

        skills = []

    skills_text = ", ".join(
        str(skill) for skill in skills
    )

    ats_score = latest_analysis.ats_score or 0

    ats_category = (
        latest_analysis.ats_category or "Not available"
    )

    return f"""
USER RESUME INFORMATION

Extracted Skills:
{skills_text}

Latest ATS Score:
{ats_score}

ATS Category:
{ats_category}

Use this information only when relevant.
Never invent qualifications or experience.
"""


# =========================================
# BUILD CONVERSATION HISTORY
# =========================================

def get_conversation_history():

    chats = ChatHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ChatHistory.created_at.desc()
    ).limit(MAX_HISTORY_MESSAGES).all()

    chats.reverse()

    conversation = []

    for chat in chats:

        if chat.message:

            conversation.append({
                "role": "user",
                "content": chat.message
            })

        if chat.response:

            conversation.append({
                "role": "model",
                "content": chat.response
            })

    return conversation


# =========================================
# SEND QUESTION TO AI
# =========================================

@career_bp.route(
    "/career-assistant",
    methods=["POST"]
)
@login_required
def career_assistant():

    try:

        data = request.get_json(silent=True)

        if not isinstance(data, dict):

            return jsonify({
                "success": False,
                "error": "Invalid request data."
            }), 400

        question = data.get("question", "")

        if not isinstance(question, str):

            return jsonify({
                "success": False,
                "error": "Invalid question format."
            }), 400

        question = question.strip()

        if not question:

            return jsonify({
                "success": False,
                "error": "Please enter your question."
            }), 400

        if len(question) > 3000:

            return jsonify({
                "success": False,
                "error": "Maximum question length is 3000 characters."
            }), 400

        # Get previous conversation

        conversation_history = get_conversation_history()

        # Get resume information

        resume_context = get_resume_context()

        # Generate response

        result = ask_career_assistant(

            question=question,

            resume_text=resume_context,

            conversation_history=conversation_history

        )

        if not isinstance(result, dict):

            return jsonify({
                "success": False,
                "error": "Invalid response from AI service."
            }), 500

        if not result.get("success"):

            return jsonify({
                "success": False,
                "error": result.get(
                    "error",
                    "Unable to generate an answer."
                )
            }), 500

        answer = result.get("answer", "")

        if not isinstance(answer, str) or not answer.strip():

            return jsonify({
                "success": False,
                "error": "AI returned an empty response."
            }), 500

        answer = answer.strip()

        # Save conversation

        new_chat = ChatHistory(
            user_id=current_user.id,
            message=question,
            response=answer
        )

        db.session.add(new_chat)

        db.session.commit()

        return jsonify({

            "success": True,

            "answer": answer,

            "message": "Response generated successfully."

        }), 200

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Career Assistant Error."
        )

        return jsonify({
            "success": False,
            "error": "Something went wrong. Please try again."
        }), 500


# =========================================
# CLEAR CHAT HISTORY
# =========================================

@career_bp.route(
    "/clear-career-history",
    methods=["POST"]
)
@login_required
def clear_career_history():

    try:

        ChatHistory.query.filter_by(
            user_id=current_user.id
        ).delete(synchronize_session=False)

        db.session.commit()

        return jsonify({

            "success": True,

            "message": "Conversation history cleared successfully."

        }), 200

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Clear Career History Error."
        )

        return jsonify({
            "success": False,
            "error": "Unable to clear conversation history."
        }), 500