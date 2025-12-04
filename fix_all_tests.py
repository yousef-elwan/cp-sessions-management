"""Comprehensive fix for all test issues"""
import os
import re

# Fix 1: Ensure timezone import in all test files
test_files = [
    "tests/test_admin_workflows.py",
    "tests/test_authorization.py",
    "tests/test_edge_cases.py",
    "tests/test_integration.py",
    "tests/test_student_workflows.py",
    "tests/test_trainer_workflows.py",
    "tests/test_bookings.py",
    "tests/test_sessions.py",
]

print("=== Fixing timezone imports ===")
for file_path in test_files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        for i, line in enumerate(lines):
            # Fix import line
            if 'from datetime import datetime, timedelta' in line and 'timezone' not in line:
                lines[i] = 'from datetime import datetime, timedelta, timezone\n'
                modified = True
                break
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"  ✓ Fixed {file_path}")

# Fix 2: Fix endpoint paths in test files
print("\n=== Fixing endpoint paths ===")
fixes = [
    ("tests/test_student_workflows.py", "/bookings/my-bookings", "/sessions/my-bookings"),
    ("tests/test_integration.py", "/bookings/my-bookings", "/sessions/my-bookings"),
    ("tests/test_bookings.py", "/bookings/my-bookings", "/sessions/my-bookings"),
]

for file_path, old_path, new_path in fixes:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_path in content:
            content = content.replace(old_path, new_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Fixed endpoint in {file_path}")

print("\n✅ All fixes applied!")
