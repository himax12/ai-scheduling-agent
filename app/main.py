from fastapi import FastAPI

# Create an instance of the FastAPI class
# This 'app' object is the main point of interaction for creating our API.
app = FastAPI(title="AI Scheduling Agent API")

# This is a "decorator". It tells FastAPI that the function right
# below it is in charge of handling GET requests to the "/" URL.
@app.get("/")
def read_root():
    """This is the root endpoint. It's used as a health check."""
    return {"status": "ok", "message": "Backend API is running!"}