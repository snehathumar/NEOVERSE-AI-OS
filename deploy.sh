#!/bin/bash

# Ensure required environment variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID environment variable is not set."
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GEMINI_API_KEY environment variable is not set."
    exit 1
fi

REGION="asia-south1"
REPO_NAME="neoverse-repo"
SERVICE_NAME="neoverse-ai-engine"
IMAGE_PATH="$REGION-docker.pkg.dev/$GCP_PROJECT_ID/$REPO_NAME/$SERVICE_NAME:latest"

echo "Setting active project to $GCP_PROJECT_ID..."
gcloud config set project $GCP_PROJECT_ID

echo "Creating Artifact Registry repository if it doesn't exist..."
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for NEOVERSE AI" || true

echo "Configuring Docker authentication..."
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

echo "Building Docker image..."
docker build -t $IMAGE_PATH .

echo "Pushing Docker image to Artifact Registry..."
docker push $IMAGE_PATH

echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_PATH \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="GEMINI_API_KEY=$GEMINI_API_KEY,GCP_PROJECT_ID=$GCP_PROJECT_ID"

echo "Deployment complete."
