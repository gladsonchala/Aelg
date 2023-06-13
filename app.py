from flask import Flask, Response, request, jsonify
import json
from bson.objectid import ObjectId
import requests

app = Flask(__name__)

base_url = "https://us-east-2.aws.data.mongodb-api.com/app/data-vagob/endpoint/data/v1"  # Replace with your MongoDB Data API endpoint
headers = {
    "Content-Type": "application/json",
    "api-key": "WIAsG0L4dV89Jg1ZGNfUEYFhuBZ4XeXdpbj3vdb4KQMGagsSTijtGBtdNRocUp7x"  # Replace with your MongoDB Data API key
}

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

        # Make a request to MongoDB Data API to insert the job
        url = f"{base_url}/insertOne"
        payload = json.dumps({
            "database": "agelgilotify",
            "collection": "jobs",
            "document": job
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            job_id = response.json().get("insertedId")
            return Response(
                response=json.dumps(
                    {"message": "Job created", "id": str(job_id)}
                ),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps({"message": "Failed to create a job"}),
                status=500,
                mimetype="application/json"
            )

    except Exception as ex:
        error_message = "Error creating a job: " + str(ex)
        print(error_message)
        return Response(
            response=json.dumps({"message": error_message}),
            status=500,
            mimetype="application/json"
        )

# Get all jobs
@app.route("/jobs", methods=["GET"])
def get_jobs():
    try:
        # Make a request to MongoDB Data API to get all jobs
        url = f"{base_url}/find"
        payload = json.dumps({
            "database": "agelgilotify",
            "collection": "jobs"
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            jobs = response.json().get("documents")
            for job in jobs:
                job["_id"] = str(job["_id"])
            return Response(
                response=json.dumps(jobs),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps({"message": "Error fetching jobs"}),
                status=500,
                mimetype="application/json"
            )

    except Exception as ex:
        error_message = "Error fetching jobs: " + str(ex)
        print(error_message)
        return Response(
            response=json.dumps({"message": error_message}),
            status=500,
            mimetype="application/json"
        )

# Get a job by ID
@app.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    try:
        # Make a request to MongoDB Data API to get the job by ID
        url = f"{base_url}/findOne"
        payload = json.dumps({
            "database": "agelgilotify",
            "collection": "jobs",
            "filter": {"_id": ObjectId(job_id)}
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            job = response.json().get("document")
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
        error_message = "Error fetching job: " + str(ex)
        print(error_message)
        return Response(
            response=json.dumps({"message": error_message}),
            status=500,
            mimetype="application/json"
        )

# Update a job
@app.route("/jobs/<job_id>", methods=["PUT"])
def update_job(job_id):
    try:
        job_updates = {}

        if "title" in request.form:
            job_updates["title"] = request.form["title"]
        if "description" in request.form:
            job_updates["description"] = request.form["description"]
        if "category" in request.form:
            job_updates["category"] = request.form["category"]
        if "location" in request.form:
            job_updates["location"] = request.form["location"]
        if "price" in request.form:
            job_updates["price"] = float(request.form["price"])
        if "duration" in request.form:
            job_updates["duration"] = request.form["duration"]
        if "status" in request.form:
            job_updates["status"] = request.form["status"]
        if "is_emergency" in request.form:
            job_updates["is_emergency"] = bool(request.form.get("is_emergency"))
        if "task_giver_id" in request.form:
            job_updates["task_giver_id"] = ObjectId(request.form["task_giver_id"])

        # Handle multiple photo updates
        photo_urls = request.form.getlist("photos_url")
        photo_captions = request.form.getlist("photos_caption")
        if len(photo_urls) > 0 and len(photo_captions) > 0:
            photos = []
            for url, caption in zip(photo_urls, photo_captions):
                photo = {
                    "url": url,
                    "caption": caption
                }
                photos.append(photo)
            job_updates["photos"] = photos

        # Make a request to MongoDB Data API to update the job
        url = f"{base_url}/updateOne"
        payload = json.dumps({
            "database": "agelgilotify",
            "collection": "jobs",
            "filter": {"_id": ObjectId(job_id)},
            "update": {"$set": job_updates}
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
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
        error_message = "Error updating job: " + str(ex)
        print(error_message)
        return Response(
            response=json.dumps({"message": error_message}),
            status=500,
            mimetype="application/json"
        )

# Delete a job
@app.route("/jobs/<job_id>", methods=["DELETE"])
def delete_job(job_id):
    try:
        # Make a request to MongoDB Data API to delete the job by ID
        url = f"{base_url}/deleteOne"
        payload = json.dumps({
            "database": "agelgilotify",
            "collection": "jobs",
            "filter": {"_id": ObjectId(job_id)}
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
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
        error_message = "Error deleting job: " + str(ex)
        print(error_message)
        return Response(
            response=json.dumps({"message": error_message}),
            status=500,
            mimetype="application/json"
        )

if __name__ == "__main__":
    app.run()
