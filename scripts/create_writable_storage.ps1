# ============================================
# Create Writable Storage Account in BH-IN-Hack For Good Subscription
# ============================================
# Purpose: Create a new Azure Storage Account in BH-IN-Hack For Good subscription
# for writable operations (uploads, logs, application data)

param(
    [string]$ResourceGroupName = "mb-compass-rg",
    [string]$StorageAccountName = "mbcompasswrite$(Get-Random -Minimum 100 -Maximum 999)",
    [string]$Location = "southeastasia",
    [string]$SubscriptionId = "5293e508-036d-433a-a64d-6afe15f3fdc9",
    [string]$ContainerName = "application-data"
)

Write-Host "========================================"
Write-Host "Creating Writable Storage Account"
Write-Host "========================================"
Write-Host "Subscription ID: $SubscriptionId"
Write-Host "Resource Group: $ResourceGroupName"
Write-Host "Storage Account: $StorageAccountName"
Write-Host "Location: $Location"
Write-Host "Container: $ContainerName"
Write-Host ""

# 1. Set the subscription context
Write-Host "[1/6] Setting Azure subscription context..."
$currentSub = az account show --query "id" -o tsv
if ($currentSub -eq $SubscriptionId) {
    Write-Host "[OK] Already on correct subscription: $SubscriptionId"
}
else {
    Write-Host "Switching to subscription: $SubscriptionId"
    az account set --subscription $SubscriptionId
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to set subscription context"
        exit 1
    }
    Write-Host "[OK] Subscription context set"
}
Write-Host ""

# 2. Create Resource Group (if not exists)
Write-Host "[2/6] Creating/verifying resource group..."
$rgExists = az group exists --name $ResourceGroupName | ConvertFrom-Json
if (-not $rgExists) {
    Write-Host "Creating new resource group: $ResourceGroupName"
    az group create --name $ResourceGroupName --location $Location
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create resource group"
        exit 1
    }
    Write-Host "[OK] Resource group created"
}
else {
    Write-Host "[OK] Resource group already exists"
}
Write-Host ""

# 3. Create Storage Account
Write-Host "[3/6] Creating storage account..."
Write-Host "Command: az storage account create --name $StorageAccountName --resource-group $ResourceGroupName --location $Location --sku Standard_LRS --kind StorageV2 --access-tier Hot"

$createResult = az storage account create `
    --name $StorageAccountName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku Standard_LRS `
    --kind StorageV2 `
    --access-tier Hot 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Output: $createResult"
    Write-Error "Failed to create storage account"
    exit 1
}
Write-Host "[OK] Storage account created: $StorageAccountName"
Write-Host ""

# 4. Create Container
Write-Host "[4/6] Creating blob container..."
az storage container create `
    --account-name $StorageAccountName `
    --name $ContainerName

if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Container may already exist or requires connection string"
    Write-Host "Attempting with connection string..."
    $connString = az storage account show-connection-string `
        --name $StorageAccountName `
        --resource-group $ResourceGroupName `
        --query connectionString `
        -o tsv
    
    az storage container create `
        --name $ContainerName `
        --connection-string $connString
}
Write-Host "[OK] Blob container created: $ContainerName"
Write-Host ""

# 5. Get Storage Account Key
Write-Host "[5/6] Retrieving storage account keys..."
$accountKey = az storage account keys list `
    --account-name $StorageAccountName `
    --resource-group $ResourceGroupName `
    --query "[0].value" `
    -o tsv

Write-Host "[OK] Storage account key retrieved"
Write-Host ""

# 6. Display Configuration
Write-Host "[6/6] Configuration Summary"
Write-Host "========================================"
Write-Host ""
Write-Host "Update your .env file with:"
Write-Host ""
Write-Host "AZURE_STORAGE_WRITABLE_ACCOUNT_NAME=$StorageAccountName"
Write-Host "AZURE_STORAGE_WRITABLE_ACCOUNT_KEY=$accountKey"
Write-Host "AZURE_STORAGE_WRITABLE_CONTAINER=$ContainerName"
Write-Host ""
Write-Host "========================================"
Write-Host "[SUCCESS] Writable storage account ready!"
