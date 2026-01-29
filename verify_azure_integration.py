"""
Azure Integration Verification Script
Tests all components of the Azure-powered Decision Intelligence Dashboard
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "mb"))
sys.path.insert(0, str(project_root / "mb" / "data_sources"))

def test_imports():
    """Test that all modules import correctly"""
    print("\n" + "="*60)
    print("TEST 1: IMPORT VERIFICATION")
    print("="*60)
    
    try:
        from mb.data_sources.azure_blob_connector import get_blob_connector
        print("✅ azure_blob_connector imported")
    except Exception as e:
        print(f"❌ azure_blob_connector: {e}")
        return False
    
    try:
        from mb.data_sources.azure_feature_engineer import get_azure_feature_engineer
        print("✅ azure_feature_engineer imported")
    except Exception as e:
        print(f"❌ azure_feature_engineer: {e}")
        return False
    
    try:
        from mb.data_sources.azure_decision_dashboard import get_azure_dashboard
        print("✅ azure_decision_dashboard imported")
    except Exception as e:
        print(f"❌ azure_decision_dashboard: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ streamlit available")
    except Exception as e:
        print(f"⚠️  streamlit warning: {e}")
    
    print("\n✅ All imports successful!")
    return True

def test_connector():
    """Test Azure Blob Connector"""
    print("\n" + "="*60)
    print("TEST 2: AZURE BLOB CONNECTOR")
    print("="*60)
    
    try:
        from mb.data_sources.azure_blob_connector import get_blob_connector
        
        connector = get_blob_connector()
        print("✅ Connector initialized")
        
        # Test connection
        health = connector.get_health_report()
        print(f"✅ Health check: {health['connection_status'].upper()}")
        
        if 'available_datasets' in health:
            print(f"✅ Available datasets: {len(health.get('available_datasets', []))}")
        
        # Test table checks
        tables_checked = health.get('tables_checked', {})
        available = sum(1 for t in tables_checked.values() if t.get('status') == 'available')
        print(f"✅ Tables available: {available}/{len(tables_checked)}")
        
        return True
    
    except Exception as e:
        print(f"❌ Connector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_feature_engineer():
    """Test Feature Engineer"""
    print("\n" + "="*60)
    print("TEST 3: FEATURE ENGINEER")
    print("="*60)
    
    try:
        from mb.data_sources.azure_feature_engineer import get_azure_feature_engineer
        
        engineer = get_azure_feature_engineer()
        print("✅ Feature engineer initialized")
        
        # Check methods exist
        methods = [
            'compute_student_daily_features',
            'compute_dropout_risk',
            'compute_sector_fit',
            'compute_module_effectiveness',
            'compute_gamification_impact',
            'compute_mobilisation_funnel'
        ]
        
        for method_name in methods:
            if hasattr(engineer, method_name):
                print(f"  ✅ {method_name}")
            else:
                print(f"  ❌ {method_name} not found")
                return False
        
        print("\n✅ All feature methods available!")
        return True
    
    except Exception as e:
        print(f"❌ Feature engineer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashboard():
    """Test Decision Dashboard"""
    print("\n" + "="*60)
    print("TEST 4: DECISION DASHBOARD")
    print("="*60)
    
    try:
        from mb.data_sources.azure_decision_dashboard import get_azure_dashboard
        
        dashboard = get_azure_dashboard()
        print("✅ Dashboard initialized")
        
        # Check methods exist
        methods = [
            'get_executive_overview',
            'get_mobilisation_funnel',
            'get_sector_heatmap',
            'get_at_risk_youth',
            'get_module_effectiveness',
            'get_gamification_impact',
            'generate_proposal_insights'
        ]
        
        for method_name in methods:
            if hasattr(dashboard, method_name):
                print(f"  ✅ {method_name}")
            else:
                print(f"  ❌ {method_name} not found")
                return False
        
        print("\n✅ All dashboard methods available!")
        return True
    
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_files_exist():
    """Test that all required files exist"""
    print("\n" + "="*60)
    print("TEST 5: FILE VERIFICATION")
    print("="*60)
    
    required_files = [
        "mb/data_sources/__init__.py",
        "mb/data_sources/azure_blob_connector.py",
        "mb/data_sources/azure_feature_engineer.py",
        "mb/data_sources/azure_decision_dashboard.py",
        "mb/pages/4_decision_intelligence_azure.py",
        "AZURE_QUICKSTART.md",
        "AZURE_INTEGRATION_GUIDE.md",
        "AZURE_IMPLEMENTATION_SUMMARY.md",
        "START_HERE.md"
    ]
    
    base_path = Path(__file__).parent
    all_exist = True
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            size_kb = full_path.stat().st_size / 1024
            print(f"  ✅ {file_path} ({size_kb:.1f} KB)")
        else:
            print(f"  ❌ {file_path} NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n✅ All files present!")
    else:
        print("\n❌ Some files missing!")
    
    return all_exist

def main():
    """Run all verification tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "AZURE INTEGRATION VERIFICATION" + " "*14 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "Imports": test_imports(),
        "Connector": test_connector(),
        "Feature Engineer": test_feature_engineer(),
        "Dashboard": test_dashboard(),
        "Files": test_files_exist(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - SYSTEM READY!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - See details above")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
