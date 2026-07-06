<#
.SYNOPSIS
    Idempotent Google Cloud Provisioning Script for NEOVERSE AI OS.
.DESCRIPTION
    This script reads the .env file for the GOOGLE_CLOUD_PROJECT_ID and dynamically
    provisions the required resources in an isolated, safe, and idempotent manner.
    It will never overwrite existing resources.
#>

$ErrorActionPreference = "Stop"
$envFile = Join-Path $PSScriptRoot "..\.env"

# 1. Read .env file securely
if (-Not (Test-Path $envFile)) {
    Write-Error "Could not find .env file at $envFile"
    exit 1
}

$envVars = @{}
Get-Content $envFile | Where-Object { $_ -match '^([^#=]+)=(.*)$' } | ForEach-Object {
    $name = $Matches[1].Trim()
    $value = $Matches[2].Trim() -replace '^"|"$', ''
    $envVars[$name] = $value
}

$projectId = $envVars["GOOGLE_CLOUD_PROJECT_ID"]
$location = $envVars["GOOGLE_CLOUD_LOCATION"]

if ([string]::IsNullOrWhiteSpace($projectId)) {
    Write-Error "GOOGLE_CLOUD_PROJECT_ID not found in .env"
    exit 1
}

if ([string]::IsNullOrWhiteSpace($location)) {
    $location = "us-central1"
    Write-Host "Using default location: $location"
}

Write-Host "======================================================="
Write-Host "NEOVERSE GCP PROVISIONING"
Write-Host "Project ID: $projectId"
Write-Host "Location:   $location"
Write-Host "======================================================="

# Set active project
Write-Host "`n[1] Setting active GCP project..."
gcloud config set project $projectId --quiet

# 2. Enable Required APIs (Idempotent by nature)
Write-Host "`n[2] Enabling required GCP APIs..."
$apis = @(
    "firestore.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "logging.googleapis.com"
)
foreach ($api in $apis) {
    gcloud services enable $api --project $projectId --quiet
}

# 3. Create Service Account (Idempotent)
$saName = "neoverse-ai-sa"
$saEmail = "${saName}@${projectId}.iam.gserviceaccount.com"
Write-Host "`n[3] Checking Service Account: $saEmail"

$saExists = gcloud iam service-accounts list --project $projectId --filter="email=$saEmail" --format="value(email)"
if ([string]::IsNullOrWhiteSpace($saExists)) {
    Write-Host "Creating Service Account..."
    gcloud iam service-accounts create $saName --display-name="NEOVERSE AI System Account" --project $projectId --quiet
} else {
    Write-Host "Service Account already exists. Skipping creation."
}

# 4. Assign IAM Roles (Idempotent)
Write-Host "`n[4] Assigning IAM roles..."
$roles = @(
    "roles/datastore.user",
    "roles/bigquery.dataEditor",
    "roles/storage.objectAdmin",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter"
)
foreach ($role in $roles) {
    gcloud projects add-iam-policy-binding $projectId `
        --member="serviceAccount:$saEmail" `
        --role="$role" `
        --condition=None `
        --quiet > $null
    Write-Host "  -> Assigned $role"
}

# 5. Create Service Account Key (Idempotent logic)
$keyPath = Join-Path $PSScriptRoot "..\neoverse-service-account.json"
Write-Host "`n[5] Checking Service Account Key at $keyPath"
if (-Not (Test-Path $keyPath)) {
    Write-Host "Generating new JSON key..."
    gcloud iam service-accounts keys create $keyPath --iam-account=$saEmail --project $projectId --quiet
} else {
    Write-Host "Service Account Key already exists locally. Skipping generation to prevent key rotation issues."
}

# 6. Create BigQuery Dataset (Idempotent)
$bqDataset = "neoverse_ai"
Write-Host "`n[6] Checking BigQuery Dataset: $bqDataset"
$bqExists = bq ls --project_id=$projectId --format=json | ConvertFrom-Json | Where-Object { $_.datasetReference.datasetId -eq $bqDataset }
if ($null -eq $bqExists) {
    Write-Host "Creating BigQuery dataset..."
    bq mk --location=$location --dataset "${projectId}:${bqDataset}"
} else {
    Write-Host "BigQuery dataset already exists. Skipping creation."
}

# 7. Create Cloud Storage Bucket (Idempotent)
$bucketName = "neoverse-ai-storage-$projectId"
Write-Host "`n[7] Checking Cloud Storage Bucket: gs://$bucketName"
$bucketExists = gcloud storage ls --project $projectId | Select-String "gs://$bucketName/"
if ($null -eq $bucketExists) {
    Write-Host "Creating Cloud Storage bucket..."
    gcloud storage buckets create "gs://$bucketName" --project $projectId --location=$location --quiet
} else {
    Write-Host "Cloud Storage bucket already exists. Skipping creation."
}

# 8. Create Secret Manager Secret (Idempotent)
$secretName = "NEOVERSE_GEMINI_API_KEY"
Write-Host "`n[8] Checking Secret Manager Secret: $secretName"
$secretExists = gcloud secrets list --project $projectId --filter="name=$secretName" --format="value(name)"
if ([string]::IsNullOrWhiteSpace($secretExists)) {
    Write-Host "Creating placeholder Secret in Secret Manager..."
    echo "PLACEHOLDER_KEY" | gcloud secrets create $secretName --project $projectId --data-file=- --replication-policy="automatic" --quiet
} else {
    Write-Host "Secret already exists. Skipping creation."
}

# 9. Firestore Default Database Check
Write-Host "`n[9] Checking Firestore Database..."
$fsExists = gcloud firestore databases list --project $projectId --format="value(name)"
if ([string]::IsNullOrWhiteSpace($fsExists) -or ($fsExists -notcontains "(default)")) {
    Write-Host "WARNING: The (default) Firestore database does not exist in this project."
    Write-Host "Please create it manually in the GCP Console, as CLI creation requires AppEngine linking in older projects, or specific region mapping."
} else {
    Write-Host "Firestore (default) database exists."
}

Write-Host "`n======================================================="
Write-Host "PROVISIONING COMPLETE"
Write-Host "Please ensure your .env file matches the following:"
Write-Host "GOOGLE_APPLICATION_CREDENTIALS=`"neoverse-service-account.json`""
Write-Host "======================================================="
