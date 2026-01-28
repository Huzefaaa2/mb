"""
Azure configuration startup checks.
Validates that required services are properly configured on application startup.
"""

import logging
import sys
from config.settings import settings

logger = logging.getLogger(__name__)

def check_azure_configuration() -> dict:
    """
    Check Azure configuration and provide warnings/errors.
    
    Returns:
        dict with keys: 'errors' (critical), 'warnings' (non-critical)
    """
    errors = []
    warnings = []
    
    # ===== READONLY STORAGE CHECKS =====
    if not settings.azure_storage.readonly_account_name:
        errors.append(
            "READ-ONLY STORAGE: AZURE_STORAGE_READONLY_ACCOUNT_NAME is not configured. "
            "Cannot read datasets from Blob Storage."
        )
    
    # ===== WRITABLE STORAGE CHECKS =====
    if not settings.azure_storage.writable_account_name:
        warnings.append(
            "WRITABLE STORAGE: AZURE_STORAGE_WRITABLE_ACCOUNT_NAME is not configured. "
            "Resume uploads, file archival, and other write operations will be disabled. "
            "To enable, set writable storage credentials in .env (BH-IN-Hack For Good subscription)."
        )
    elif not settings.azure_storage.writable_account_key and settings.environment != "development":
        warnings.append(
            "WRITABLE STORAGE: AZURE_STORAGE_WRITABLE_ACCOUNT_KEY is not configured. "
            "Write operations will use connection string or managed identity (recommend for production)."
        )
    
    if not settings.azure_storage.writable_container and settings.azure_storage.writable_account_name:
        warnings.append(
            "WRITABLE STORAGE: AZURE_STORAGE_WRITABLE_CONTAINER is not configured. "
            "Container name is required for blob uploads."
        )
    
    # ===== SUBSCRIPTION CHECKS =====
    if not settings.azure.primary_subscription_id:
        warnings.append(
            "PRIMARY SUBSCRIPTION: AZURE_PRIMARY_SUBSCRIPTION_ID not set. "
            "Using AZURE_SUBSCRIPTION_ID if available."
        )
    
    if not settings.azure.shared_services_subscription_id:
        warnings.append(
            "SHARED SERVICES SUBSCRIPTION: AZURE_SHARED_SERVICES_SUBSCRIPTION_ID not set. "
            "Required for read-only storage account reference."
        )
    
    # ===== DATABRICKS CHECKS =====
    if not settings.databricks.host or not settings.databricks.token:
        warnings.append(
            "DATABRICKS: Host or token not configured. "
            "Databricks-based data loading will be unavailable. "
            "Set DATABRICKS_HOST and DATABRICKS_TOKEN if using Databricks."
        )
    
    # ===== POSTGRESQL CHECKS =====
    if not settings.postgres.password and settings.environment != "development":
        warnings.append(
            "POSTGRESQL: POSTGRES_PASSWORD is not set. "
            "Local development assumes no password. "
            "Production database should require a secure password."
        )
    
    return {"errors": errors, "warnings": warnings}

def print_startup_check(verbose: bool = False) -> bool:
    """
    Print configuration check results on startup.
    
    Args:
        verbose: If True, print all warnings; if False, only print errors.
    
    Returns:
        True if safe to continue; False if critical errors found.
    """
    result = check_azure_configuration()
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])
    
    if errors:
        logger.error("=" * 70)
        logger.error("CRITICAL CONFIGURATION ERRORS:")
        logger.error("=" * 70)
        for i, error in enumerate(errors, 1):
            logger.error(f"{i}. {error}")
        logger.error("=" * 70)
        return False
    
    if warnings and verbose:
        logger.warning("=" * 70)
        logger.warning("CONFIGURATION WARNINGS:")
        logger.warning("=" * 70)
        for i, warning in enumerate(warnings, 1):
            logger.warning(f"{i}. {warning}")
        logger.warning("=" * 70)
    elif warnings:
        logger.warning(f"[CONFIG] {len(warnings)} warning(s). Use --verbose to see details.")
    
    return True
