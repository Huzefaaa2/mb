"""
Data Sources Package
Provides connectors and feature engineering for Decision Intelligence Dashboard

Modules:
- azure_blob_connector: Connects to Azure Blob Storage
- azure_feature_engineer: Computes enriched features
- azure_decision_dashboard: Analytics engine

Usage:
    from data_sources.azure_blob_connector import get_blob_connector
    from data_sources.azure_feature_engineer import get_azure_feature_engineer
    from data_sources.azure_decision_dashboard import get_azure_dashboard
"""

__version__ = "2.0"
__author__ = "Magic Bus Data Team"

from .azure_blob_connector import (
    AzureBlobConnector,
    get_blob_connector,
    test_connection
)

from .azure_feature_engineer import (
    AzureFeatureEngineer,
    get_azure_feature_engineer,
    refresh_all_azure_features
)

from .azure_decision_dashboard import (
    AzureDecisionDashboard,
    get_azure_dashboard
)

__all__ = [
    'AzureBlobConnector',
    'get_blob_connector',
    'test_connection',
    'AzureFeatureEngineer',
    'get_azure_feature_engineer',
    'refresh_all_azure_features',
    'AzureDecisionDashboard',
    'get_azure_dashboard',
]
