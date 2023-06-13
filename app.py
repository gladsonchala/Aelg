#base_url = "https://us-east-2.aws.data.mongodb-api.com/app/data-vagob/endpoint/data/v1"  # Replace with your MongoDB Data API endpoint
#api-key = "WIAsG0L4dV89Jg1ZGNfUEYFhuBZ4XeXdpbj3vdb4KQMGagsSTijtGBtdNRocUp7x"  # Replace with your MongoDB Data API key

from flask import Flask, Response, request, jsonify
import json
from bson.objectid import ObjectId
import requests

app = Flask(__name__)

# MongoDB Data API configuration
base_url = "https://us-east-2.aws.data.mongodb-api.com/app/data-vagob/endpoint/data/v1"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer WIAsG0L4dV89Jg1ZGNfUEYFhuBZ4XeXdpbj3vdb4KQMGagsSTijtGBtdNRocUp7x"
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
            #"task_giver_id": ObjectId(request.form["task_giver_id"]),
            "task_giver_id": request.form["task_giver_id"],
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

        # Make a request to MongoDB Data API to create the job
        url = f"{base_url}/insertOne"
        payload = json.dumps({
            "database": "agelgilotify",
            "collection": "jobs",
            "document": job
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            job_id = response.json()["insertedId"]
            return Response(
                response=json.dumps(
                    {"message": "Job created", "id": job_id}
                ),
                status=200,
                mimetype="application/json"
            )
        elif response.status_code == 500:
            return Response(
                response=json.dumps({"message": "Failed to create a job: Internal server error"}),
                status=500,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps({"message": f"Failed to create a job: {response.json()['message']}"}),
                status=response.status_code,
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
            "collection": "jobs",
            "limit": 100
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            jobs = response.json()["documents"]
            for job in jobs:
                job["_id"] = str(job["_id"])
            return Response(
                response=json.dumps(jobs),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps({"message": "Failed to fetch jobs"}),
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
            job = response.json()["document"]
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
        else:
            return Response(
                response=json.dumps({"message": "Failed to fetch the job"}),
                status=500,
                mimetype="application/json"
            )

    except Exception as ex:
        error_message = "Error fetching a job: " + str(ex)
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

        # Make a request to MongoDB Data API to update the job
        url = f"{base_url}/updateOne"
        payload = json.dumps({
            "database": "agelgilotify",
            "collection": "jobs",
            "filter": {"_id": ObjectId(job_id)},
            "update": {"$set": updated_job}
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            if response.json()["matchedCount"] > 0:
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
        else:
            return Response(
                response=json.dumps({"message": "Failed to update the job"}),
                status=500,
                mimetype="application/json"
            )

    except Exception as ex:
        error_message = "Error updating a job: " + str(ex)
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
        # Make a request to MongoDB Data API to delete the job
        url = f"{base_url}/deleteOne"
        payload = json.dumps({
            "database": "agelgilotify",
            "collection": "jobs",
            "filter": {"_id": ObjectId(job_id)}
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            if response.json()["deletedCount"] > 0:
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
        else:
            return Response(
                response=json.dumps({"message": "Failed to delete the job"}),
                status=500,
                mimetype="application/json"
            )

    except Exception as ex:
        error_message = "Error deleting a job: " + str(ex)
        print(error_message)
        return Response(
            response=json.dumps({"message": error_message}),
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

        # Make a request to MongoDB Data API to insert the application
        url = f"{base_url}/insertOne"
        payload = json.dumps({
            "database": "agelgilotify",
            "collection": "applications",
            "document": application
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            if response.json()["insertedId"]:
                return Response(
                    response=json.dumps(
                        {"message": "Application submitted", "id": str(response.json()["insertedId"])}
                    ),
                    status=200,
                    mimetype="application/json"
                )
            else:
                return Response(
                    response=json.dumps({"message": "Failed to submit the application"}),
                    status=500,
                    mimetype="application/json"
                )
        else:
            return Response(
                response=json.dumps({"message": "Failed to submit the application"}),
                status=500,
                mimetype="application/json"
            )

    except Exception as ex:
        error_message = "Error applying for a job: " + str(ex)
        print(error_message)
        return Response(
            response=json.dumps({"message": error_message}),
            status=500,
            mimetype="application/json"
        )


# Get applications for a job
@app.route("/jobs/<job_id>/applications", methods=["GET"])
def get_job_applications(job_id):
    try:
        # Make a request to MongoDB Data API to get the applications for the job
        url = f"{base_url}/find"
        payload = json.dumps({
            "database": "agelgilotify",
            "collection": "applications",
            "filter": {"job_id": ObjectId(job_id)}
        })
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            applications = response.json()["documents"]
            for application in applications:
                application["_id"] = str(application["_id"])
            return Response(
                response=json.dumps(applications),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps({"message": "Failed to fetch the applications"}),
                status=500,
                mimetype="application/json"
            )

    except Exception as ex:
        error_message = "Error fetching the applications: " + str(ex)
        print(error_message)
        return Response(
            response=json.dumps({"message": error_message}),
            status=500,
            mimetype="application/json"
        )


if __name__ == "__main__":
    app.run(debug=True)

