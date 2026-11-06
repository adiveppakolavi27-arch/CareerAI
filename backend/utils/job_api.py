import os
import requests

from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# ==========================================
# ADZUNA API CONFIGURATION
# ==========================================

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api"


# ==========================================
# SEARCH JOBS
# ==========================================

def search_jobs(
    keyword,
    location="India",
    page=1,
    results_per_page=20
):

    # Check API credentials

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:

        return {
            "success": False,
            "message": "Adzuna API credentials are not configured.",
            "jobs": []
        }

    # Validate search inputs

    keyword = (keyword or "").strip()
    location = (location or "").strip()

    if not keyword:

        return {
            "success": False,
            "message": "Please enter a job title or keyword.",
            "jobs": []
        }

    if not 1 <= page <= 100:

        return {
            "success": False,
            "message": "Invalid page number.",
            "jobs": []
        }

    results_per_page = max(
        1,
        min(int(results_per_page), 50)
    )

    # API endpoint

    endpoint = (
        f"{BASE_URL}/jobs/in/search/{page}"
    )

    # API parameters

    params = {

        "app_id": ADZUNA_APP_ID,

        "app_key": ADZUNA_APP_KEY,

        "what": keyword,

        "where": location,

        "results_per_page": results_per_page,

        "content-type": "application/json"
    }

    try:

        response = requests.get(

            endpoint,

            params=params,

            timeout=20

        )

        response.raise_for_status()

        data = response.json()

        jobs = []

        for item in data.get("results", []):

            company = item.get("company") or {}

            job_location = item.get("location") or {}

            jobs.append({

                "id": str(item.get("id", "")),

                "title": item.get("title", "Not available"),

                "company": company.get(
                    "display_name",
                    "Not available"
                ),

                "location": job_location.get(
                    "display_name",
                    "Not available"
                ),

                "description": item.get(
                    "description",
                    ""
                ),

                "salary_min": item.get("salary_min"),

                "salary_max": item.get("salary_max"),

                "created": item.get("created"),

                "apply_url": item.get("redirect_url"),

                "source": "Adzuna"

            })

        return {

            "success": True,

            "message": "Jobs retrieved successfully.",

            "total_jobs": data.get("count", len(jobs)),

            "jobs": jobs

        }

    except requests.exceptions.Timeout:

        return {

            "success": False,

            "message": "Job API request timed out.",

            "jobs": []

        }

    except requests.exceptions.HTTPError as error:

        return {

            "success": False,

            "message": (
                f"Job API returned HTTP "
                f"{error.response.status_code}."
            ),

            "jobs": []

        }

    except requests.exceptions.RequestException:

        return {

            "success": False,

            "message": "Unable to connect to the job service.",

            "jobs": []

        }

    except ValueError:

        return {

            "success": False,

            "message": "Invalid response received from job service.",

            "jobs": []

        }