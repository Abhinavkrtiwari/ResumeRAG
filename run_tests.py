#!/usr/bin/env python3
"""
Test runner script for ResumeRAG
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print("Error:", e.stderr)
        return False

def main():
    """Main test runner"""
    print("🧪 ResumeRAG Test Runner")
    print("=" * 50)
    
    # Change to project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    tests_passed = 0
    total_tests = 0
    
    # Backend tests
    total_tests += 1
    if run_command("cd backend && python -m pytest tests/ -v", "Backend API Tests"):
        tests_passed += 1
    
    # Frontend tests (if available)
    if os.path.exists("frontend/package.json"):
        total_tests += 1
        if run_command("cd frontend && npm test -- --watchAll=false", "Frontend Tests"):
            tests_passed += 1
    
    # Linting
    total_tests += 1
    if run_command("cd backend && python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Backend Linting"):
        tests_passed += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Test Summary: {tests_passed}/{total_tests} tests passed")
    print('='*50)
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
