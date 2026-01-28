import streamlit as st
import pandas as pd
from typing import Optional
import os
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

class DatabricksLoader:
    """Load data from Databricks Unity Catalog with caching."""
    
    def __init__(self):
        self.settings = get_settings()
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish Databricks connection."""
        try:
            from databricks import sql
            
            self.connection = sql.connect(
                server_hostname=self.settings.databricks.host.replace("https://", "").replace("adb-", "").split(".")[0] + ".cloud.databricks.com",
                http_path="/sql/1.0/warehouses/default",
                auth_type="pat",
                token=self.settings.databricks.token,
            )
            logger.info("✓ Connected to Databricks")
        except Exception as e:
            logger.error(f"✗ Databricks connection failed: {e}")
            self.connection = None
    
    def query(self, sql_query: str) -> pd.DataFrame:
        """Execute Databricks SQL query."""
        if not self.connection:
            logger.warning("Not connected to Databricks, returning empty DataFrame")
            return pd.DataFrame()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(result, columns=columns)
        except Exception as e:
            logger.error(f"Query error: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600)
    def load_students(_self) -> pd.DataFrame:
        """Load students table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.students
        LIMIT 10000
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_career_interests(_self) -> pd.DataFrame:
        """Load career_interests table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.career_interests
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_career_pathways(_self) -> pd.DataFrame:
        """Load career_pathways table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.career_pathways
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_quiz_attempts(_self) -> pd.DataFrame:
        """Load quiz_attempts table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.quiz_attempts
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_student_progress(_self) -> pd.DataFrame:
        """Load student_progress table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.student_progress
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_student_skills(_self) -> pd.DataFrame:
        """Load student_skills table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.student_skills
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_learning_modules(_self) -> pd.DataFrame:
        """Load learning_modules table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.learning_modules
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_teachers(_self) -> pd.DataFrame:
        """Load teachers table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.teachers
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_achievements(_self) -> pd.DataFrame:
        """Load achievements table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.achievements
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_student_achievements(_self) -> pd.DataFrame:
        """Load student_achievements table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.student_achievements
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_points_ledger(_self) -> pd.DataFrame:
        """Load points_ledger table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.points_ledger
        """
        return _self.query(query)
    
    @st.cache_data(ttl=3600)
    def load_pathway_skills(_self) -> pd.DataFrame:
        """Load pathway_skills table."""
        query = f"""
        SELECT * FROM {_self.settings.databricks.catalog}.{_self.settings.databricks.schema}.pathway_skills
        """
        return _self.query(query)
    
    def close(self):
        """Close Databricks connection."""
        if self.connection:
            self.connection.close()

# Global loader instance
@st.cache_resource
def get_databricks_loader():
    return DatabricksLoader()
