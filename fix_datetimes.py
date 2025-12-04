"""Script to fix datetime and timezone imports in all test files"""
import os
import re

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

for file_path in test_files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ensure timezone is imported
        if 'from datetime import' in content:
            if 'timezone' not in content:
                content = content.replace(
                    'from datetime import datetime, timedelta',
                    'from datetime import datetime, timedelta, timezone'
                )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Fixed imports in {file_path}")

print("\nAll files fixed!")
