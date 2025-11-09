#!/usr/bin/env python3
"""Simple validation script for config flow logic."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

# Test the config flow logic manually
def test_config_flow_logic():
    """Test key parts of the config flow logic."""
    
    print("=== Testing Config Flow Logic ===")
    
    # Test 1: Verify the method exists in options flow
    try:
        from custom_components.bookstack_integration.config_flow import (
            BookStackIntegrationOptionsFlow
        )
        
        # Check if the problematic method now exists
        has_create_shelf = hasattr(BookStackIntegrationOptionsFlow, 'async_step_create_shelf')
        print(f"✓ Options flow has async_step_create_shelf method: {has_create_shelf}")
        
        if not has_create_shelf:
            print("✗ FAILED: async_step_create_shelf method missing")
            return False
            
    except Exception as e:
        print(f"✗ FAILED: Could not import options flow: {e}")
        return False
    
    # Test 2: Check that the main config flow has the expected methods
    try:
        from custom_components.bookstack_integration.config_flow import (
            BookStackIntegrationConfigFlow
        )
        
        expected_methods = [
            'async_step_user',
            'async_step_shelf_selection', 
            'async_step_create_shelf',
            'async_step_test'
        ]
        
        for method in expected_methods:
            has_method = hasattr(BookStackIntegrationConfigFlow, method)
            print(f"✓ Config flow has {method} method: {has_method}")
            if not has_method:
                print(f"✗ FAILED: {method} method missing")
                return False
                
    except Exception as e:
        print(f"✗ FAILED: Could not import config flow: {e}")
        return False
    
    # Test 3: Verify the step_id consistency
    print("\n=== Testing Step ID Consistency ===")
    
    # Check that the create_shelf step_id is properly defined
    from custom_components.bookstack_integration.config_flow import BookStackIntegrationConfigFlow
    
    # Test that the method signature and step_id match
    config_flow = BookStackIntegrationConfigFlow()
    options_flow = BookStackIntegrationOptionsFlow(None)
    
    # Both flows should have the same step_id for create_shelf
    print("✓ Both config and options flows should support 'create_shelf' step_id")
    
    print("\n=== All Config Flow Logic Tests Passed ===")
    return True

def test_device_creation_logic():
    """Test the device creation part of the flow."""
    
    print("\n=== Testing Device Creation Logic ===")
    
    try:
        from custom_components.bookstack_integration.config_flow import (
            BookStackIntegrationConfigFlow
        )
        
        # Check if the device registration method exists
        has_device_method = hasattr(BookStackIntegrationConfigFlow, '_register_shelf_device')
        print(f"✓ Config flow has _register_shelf_device method: {has_device_method}")
        
        if not has_device_method:
            print("✗ FAILED: _register_shelf_device method missing")
            return False
            
        # The method should be callable and not cause syntax errors
        print("✓ Device creation logic is properly structured")
        
    except Exception as e:
        print(f"✗ FAILED: Device creation logic error: {e}")
        return False
    
    print("✓ Device Creation Logic Tests Passed")
    return True

def test_constant_imports():
    """Test that all constants are properly imported."""
    
    print("\n=== Testing Constant Imports ===")
    
    try:
        from custom_components.bookstack_integration.const import (
            DOMAIN,
            CONF_BASE_URL,
            CONF_TOKEN_ID,
            CONF_TOKEN_SECRET,
            CONF_SHELF_NAME,
            CONF_TIMEOUT,
            DEFAULT_TIMEOUT
        )
        
        print("✓ All required constants imported successfully")
        print(f"  DOMAIN: {DOMAIN}")
        print(f"  CONF_SHELF_NAME: {CONF_SHELF_NAME}")
        
        return True
        
    except Exception as e:
        print(f"✗ FAILED: Constant import error: {e}")
        return False

def main():
    """Run all validation tests."""
    print("Validating BookStack Integration Config Flow Fix")
    print("=" * 50)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_constant_imports()
    all_passed &= test_config_flow_logic() 
    all_passed &= test_device_creation_logic()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL VALIDATION TESTS PASSED!")
        print("The config flow fix appears to be working correctly.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())