from flask import Flask, Response, request, jsonify
import json
from bson.objectid import ObjectId
import pymongo
from datetime import datetime

app = Flask(__name__)

# Connecting with MongoDB database
try:
    mongo_uri = "mongodb://username:password@localhost:27017/?authSource=admin"
    mongo = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
    mongo.server_info()  # Trigger exception if cannot connect to database
    db = mongo.agelgilotify
except:
    print("ERROR - Cannot connect to database")


# Create a job
@app.route("/jobs", methods=["POST"])
def create_job():
    try:
        job = {
            "title": request.form["title"],
            "description": request.form["description"],
            "category": request.form["category"],
            "location": request.form["location"],
            "price": float(request.form["price"]),
            "duration": request.form["duration"],
            "status": "Open",
            "is_emergency": bool(request.form.get("is_emergency")),
            "task_giver_id": ObjectId(request.form["task_giver_id"]),
            "photos": []
        }

        # Handle multiple photos
        photo_urls = request.form.getlist("photos_url")
        photo_captions = request.form.getlist("photos_caption")
        for url, caption in zip(photo_urls, photo_captions):
            photo = {
                "url": url,
                "caption": caption
            }
            job["photos"].append(photo)

        dbResponse = db.jobs.insert_one(job)
        return Response(
            response=json.dumps(
                {"message": "Job created", "id": str(dbResponse.inserted_id)}
            ),
            status=200,
            mimetype="application/json"
        )

    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Error creating a job"}),
            status=500,
            mimetype="application/json"
        )


# Get all jobs
@app.route("/jobs", methods=["GET"])
def get_jobs():
    try:
        jobs = list(db.jobs.find())
        for job in jobs:
            job["_id"] = str(job["_id"])
        return Response(
            response=json.dumps(jobs),
            status=200,
            mimetype="application/json"
        )
    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Error fetching jobs"}),
            status=500,
            mimetype="application/json"
        )


# Get a job by ID
@app.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    try:
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
        if job:
            job["_id"] = str(job["_id"])
            return Response(
                response=json.dumps(job),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps({"message": "Job not found"}),
                status=404,
                mimetype="application/json"
            )
    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Error fetching a job"}),
            status=500,
            mimetype="application/json"
        )


# Update a job
@app.route("/jobs/<job_id>", methods=["PUT"])
def update_job(job_id):
    try:
        updated_job = {
            "title": request.form["title"],
            "description": request.form["description"],
            "category": request.form["category"],
            "location": request.form["location"],
            "price": float(request.form["price"]),
            "duration": request.form["duration"],
            "status": request.form["status"],
            "is_emergency": bool(request.form.get("is_emergency")),
            "task_giver_id": ObjectId(request.form["task_giver_id"]),
            "photos": []
        }

        # Handle multiple photos
        photo_urls = request.form.getlist("photos_url")
        photo_captions = request.form.getlist("photos_caption")
        for url, caption in zip(photo_urls, photo_captions):
            photo = {
                "url": url,
                "caption": caption
            }
            updated_job["photos"].append(photo)

        dbResponse = db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": updated_job})
        if dbResponse.modified_count > 0:
            return Response(
                response=json.dumps({"message": "Job updated"}),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps({"message": "Job not found"}),
                status=404,
                mimetype="application/json"
            )

    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Error updating a job"}),
            status=500,
            mimetype="application/json"
        )


# Delete a job
@app.route("/jobs/<job_id>", methods=["DELETE"])
def delete_job(job_id):
    try:
        dbResponse = db.jobs.delete_one({"_id": ObjectId(job_id)})
        if dbResponse.deleted_count > 0:
            return Response(
                response=json.dumps({"message": "Job deleted"}),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps({"message": "Job not found"}),
                status=404,
                mimetype="application/json"
            )

    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Error deleting a job"}),
            status=500,
            mimetype="application/json"
        )


# Apply for a job
@app.route("/jobs/apply", methods=["POST"])
def apply_for_job():
    try:
        application = {
            "job_id": ObjectId(request.form["job_id"]),
            "user_id": ObjectId(request.form["user_id"]),
            "status": "Pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rating": None
        }

        dbResponse = db.applications.insert_one(application)
        return Response(
            response=json.dumps(
                {"message": "Application submitted", "id": str(dbResponse.inserted_id)}
            ),
            status=200,
            mimetype="application/json"
        )

    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Error applying for a job"}),
            status=500,
            mimetype="application/json"
        )


# Get applications for a job
@app.route("/jobs/<job_id>/applications", methods=["GET"])
def get_job_applications(job_id):
    try:
        applications = list(db.applications.find({"job_id": ObjectId(job_id)}))
        for application in applications:
            application["_id"] = str(application["_id"])
        return Response(
            response=json.dumps(applications),
            status=200,
            mimetype="application/json"
        )
    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Error fetching applications"}),
            status=500,
            mimetype="application/json"
        )

# Cancel an application
@app.route("/applications/<application_id>", methods=["DELETE"])
def cancel_application(application_id):
    try:
        dbResponse = db.applications.delete_one({"_id": ObjectId(application_id)})
        if dbResponse.deleted_count > 0:
            return Response(
                response=json.dumps({"message": "Application cancelled"}),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps({"message": "Application not found"}),
                status=404,
                mimetype="application/json"
            )

    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Error cancelling application"}),
            status=500,
            mimetype="application/json"
        )



# Provide rating for a worker
@app.route("/ratings/worker", methods=["POST"])
def rate_worker():
    try:
        rating = {
            "user_id": ObjectId(request.form["user_id"]),
            "rating": int(request.form["rating"])
        }

        dbResponse = db.user_ratings.insert_one(rating)
        return Response(
            response=json.dumps(
                {"message": "Rating submitted", "id": str(dbResponse.inserted_id)}
            ),
            status=200,
            mimetype="application/json"
        )

    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Error submitting rating"}),
            status=500,
            mimetype="application/json"
        )


# Provide rating for a task giver
@app.route("/ratings/task-giver", methods=["POST"])
def rate_task_giver():
    try:
        rating = {
            "task_giver_id": ObjectId(request.form["task_giver_id"]),
            "rating": int(request.form["rating"])
        }

        dbResponse = db.task_giver_ratings.insert_one(rating)
        return Response(
            response=json.dumps(
                {"message": "Rating submitted", "id": str(dbResponse.inserted_id)}
            ),
            status=200,
            mimetype="application/json"
        )

    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Error submitting rating"}),
            status=500,
            mimetype="application/json"
        )


if __name__ == "__main__":
    app.run(port=5000)
