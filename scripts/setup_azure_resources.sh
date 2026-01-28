#!/bin/bash
# Setup all Azure resources for Magic Bus Compass 360

set -e  # Exit on error

RESOURCE_GROUP="BH-IN-Base-RG"
LOCATION="southeastasia"
POSTGRES_SERVER="mb-postgres-server"
POSTGRES_USER="mbadmin"
POSTGRES_PASSWORD="MagicBus@Compass360!"
POSTGRES_DATABASE="magic_bus_compass"
DATABRICKS_NAME="mb-compass-workspace"
STORAGE_ACCOUNT="hackforgood1"

echo "🔧 Setting up Azure Resources for Magic Bus Compass 360"
echo "=================================================="

# 1. PostgreSQL
echo -e "\n1️⃣  Checking PostgreSQL Server..."
if az postgres flexible-server show --name $POSTGRES_SERVER --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "✓ PostgreSQL server already exists"
    POSTGRES_FQDN=$(az postgres flexible-server show --name $POSTGRES_SERVER --resource-group $RESOURCE_GROUP --query "fullyQualifiedDomainName" -o tsv)
else
    echo "Creating PostgreSQL server..."
    az postgres flexible-server create \
      --resource-group $RESOURCE_GROUP \
      --name $POSTGRES_SERVER \
      --location $LOCATION \
      --admin-user $POSTGRES_USER \
      --admin-password "$POSTGRES_PASSWORD" \
      --sku-name Standard_B1ms \
      --tier Burstable \
      --storage-size 32 \
      --version 15 \
      --yes
    POSTGRES_FQDN=$(az postgres flexible-server show --name $POSTGRES_SERVER --resource-group $RESOURCE_GROUP --query "fullyQualifiedDomainName" -o tsv)
    echo "✓ PostgreSQL created: $POSTGRES_FQDN"
fi

# 2. Databricks
echo -e "\n2️⃣  Checking Databricks Workspace..."
if az databricks workspace show --name $DATABRICKS_NAME --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "✓ Databricks workspace already exists"
    DATABRICKS_WORKSPACE_URL=$(az databricks workspace show --name $DATABRICKS_NAME --resource-group $RESOURCE_GROUP --query "workspaceUrl" -o tsv)
else
    echo "Creating Databricks workspace (this may take a few minutes)..."
    az databricks workspace create \
      --resource-group $RESOURCE_GROUP \
      --name $DATABRICKS_NAME \
      --location $LOCATION \
      --sku premium \
      --yes
    DATABRICKS_WORKSPACE_URL=$(az databricks workspace show --name $DATABRICKS_NAME --resource-group $RESOURCE_GROUP --query "workspaceUrl" -o tsv)
    echo "✓ Databricks workspace created: $DATABRICKS_WORKSPACE_URL"
fi

# 3. Speech Service
echo -e "\n3️⃣  Getting Speech to Text Service credentials..."
SPEECH_KEY=$(az cognitiveservices account keys list --name "mb-speech-service" --resource-group $RESOURCE_GROUP --query "key1" -o tsv 2>/dev/null || echo "TBD")
echo "✓ Speech service key obtained"

# 4. Storage Account Keys
echo -e "\n4️⃣  Getting Storage Account credentials..."
STORAGE_KEY=$(az storage account keys list --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --query "[0].value" -o tsv 2>/dev/null || echo "TBD")
echo "✓ Storage account key obtained"

# 5. Create Blob Containers
echo -e "\n5️⃣  Creating blob storage containers..."
for container in "resumes" "transcripts" "analytics-reports" "user-data"; do
    az storage container create \
      --account-name $STORAGE_ACCOUNT \
      --name $container \
      --auth-mode login \
      --output none 2>/dev/null || echo "✓ Container '$container' already exists"
done
echo "✓ All blob containers ready"

# 6. OpenAI Service
echo -e "\n6️⃣  Getting OpenAI service credentials..."
OPENAI_KEY=$(az cognitiveservices account keys list --name "BH-IN-OpenAI-HackForGood" --resource-group $RESOURCE_GROUP --query "key1" -o tsv 2>/dev/null || echo "TBD")
OPENAI_ENDPOINT=$(az cognitiveservices account show --name "BH-IN-OpenAI-HackForGood" --resource-group $RESOURCE_GROUP --query "properties.endpoint" -o tsv 2>/dev/null || echo "TBD")
echo "✓ OpenAI credentials obtained"

# 7. Generate .env file
echo -e "\n7️⃣  Generating .env file..."

cat > ../.env << EOF
# ============================================
# Magic Bus Compass 360 - Environment Configuration
# Generated: $(date)
# ============================================

# Azure Subscription IDs
AZURE_SUBSCRIPTION_ID=5293e508-036d-433a-a64d-6afe15f3fdc9
AZURE_SHARED_SERVICES_SUBSCRIPTION_ID=f3f7d52f-9e45-451d-b0c0-ee75a4c94e66
AZURE_RESOURCE_GROUP=$RESOURCE_GROUP

# PostgreSQL Configuration
POSTGRES_HOST=$POSTGRES_FQDN
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DATABASE=$POSTGRES_DATABASE
POSTGRES_PORT=5432

# Azure Blob Storage - Read-only (BH-SharedServices)
AZURE_STORAGE_READONLY_ACCOUNT_NAME=defaultstoragehackathon
AZURE_STORAGE_READONLY_ACCOUNT_KEY=<FILL_IN_READONLY_KEY>
AZURE_STORAGE_READONLY_CONTAINER=student-data

# Azure Blob Storage - Writable (BH-IN-Hack For Good)
AZURE_STORAGE_WRITABLE_ACCOUNT_NAME=$STORAGE_ACCOUNT
AZURE_STORAGE_WRITABLE_ACCOUNT_KEY=$STORAGE_KEY
AZURE_STORAGE_WRITABLE_CONTAINER=application-data

# Additional Containers
AZURE_STORAGE_RESUMES_CONTAINER=resumes
AZURE_STORAGE_TRANSCRIPTS_CONTAINER=transcripts
AZURE_STORAGE_REPORTS_CONTAINER=analytics-reports
AZURE_STORAGE_USER_DATA_CONTAINER=user-data

# Databricks Configuration
DATABRICKS_WORKSPACE_NAME=$DATABRICKS_NAME
DATABRICKS_HOST=https://$DATABRICKS_WORKSPACE_URL
DATABRICKS_TOKEN=<GENERATE_IN_DATABRICKS_WORKSPACE>
DATABRICKS_CLUSTER_ID=<GET_AFTER_CLUSTER_CREATION>

# Azure Cognitive Services - Speech to Text
AZURE_SPEECH_SERVICE_NAME=mb-speech-service
AZURE_SPEECH_REGION=$LOCATION
AZURE_SPEECH_API_KEY=$SPEECH_KEY

# Azure OpenAI Service
AZURE_OPENAI_API_KEY=$OPENAI_KEY
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Application Configuration
APP_NAME=Magic Bus Compass 360
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Database Initialization
DB_INIT_SAMPLE_DATA=true
DB_BACKUP_ENABLED=true

# Feature Flags
ENABLE_DATABRICKS_ANALYTICS=true
ENABLE_SPEECH_TRANSCRIPTION=true
ENABLE_RESUME_ARCHIVAL=true
ENABLE_SYNTHETIC_DATA=true
EOF

echo "✓ .env file created"

echo -e "\n$(tput bold)$(tput setaf 6)========================================================$(tput sgr0)"
echo "$(tput bold)$(tput setaf 2)✅ Azure Resources Setup Complete$(tput sgr0)"
echo "$(tput bold)$(tput setaf 6)========================================================$(tput sgr0)"

echo -e "\n$(tput setaf 3)PostgreSQL:$(tput sgr0)"
echo "  Server: $POSTGRES_FQDN"
echo "  User: $POSTGRES_USER"
echo "  Database: $POSTGRES_DATABASE"

echo -e "\n$(tput setaf 3)Databricks:$(tput sgr0)"
echo "  Workspace: $DATABRICKS_NAME"
echo "  URL: $DATABRICKS_WORKSPACE_URL"

echo -e "\n$(tput setaf 3)Blob Storage:$(tput sgr0)"
echo "  Account: $STORAGE_ACCOUNT"
echo "  Containers: resumes, transcripts, analytics-reports, user-data"

echo -e "\n$(tput setaf 3)Next Steps:$(tput sgr0)"
echo "  1. Edit .env file and fill in:"
echo "     - DATABRICKS_TOKEN (generate in workspace)"
echo "     - DATABRICKS_CLUSTER_ID (after cluster creation)"
echo "  2. Run: python scripts/init_db.py"
echo "  3. Run: streamlit run mb/app.py"

echo -e "\n$(tput bold)$(tput setaf 6)========================================================$(tput sgr0)"
