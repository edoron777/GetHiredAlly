"""
Determinism Tests for Static CV Detection

These tests verify that issue detection is DETERMINISTIC:
- Same CV text → Same issues (100% of the time)
- Same issue count (100% of the time)
- Same issue types (100% of the time)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.detection import detect_all_issues
from common.scoring.severity import assign_severity_to_issues


TEST_CV = """
John Doe
john@example.com
555-123-4567

SUMMARY
Experienced professional with various skills and multiple years of experience.

EXPERIENCE

Senior Developer at TechCorp (Jan 2020 - Present)
- Responsible for managing team
- Helped with various projects and stuff
- Worked on different things

Developer at StartupInc (2018 - 2020)
- Assisted with development
- Handled multiple tasks
- Did coding work

EDUCATION

Bachelor of Science in Computer Science
University of Example, 2018

SKILLS
Python, JavaScript, SQL, Leadership, Communication
"""


def test_same_issues_every_time():
    """
    CRITICAL TEST: Same CV must produce same issues.
    Run 10 times, compare results.
    """
    print("Test 1: Same CV → Same issues (10 runs)")
    
    results = []
    for i in range(10):
        issues = detect_all_issues(TEST_CV)
        issue_types = tuple(sorted([iss['issue_type'] for iss in issues]))
        results.append(issue_types)
    
    unique_results = set(results)
    
    assert len(unique_results) == 1, \
        f"FAIL: Got {len(unique_results)} different results in 10 runs!"
    
    print(f"✅ PASSED: All 10 runs produced identical issues ({len(results[0])} issues)")
    return True


def test_same_count_every_time():
    """
    Test that issue COUNT is consistent.
    """
    print("Test 2: Same issue count (10 runs)")
    
    counts = []
    for i in range(10):
        issues = detect_all_issues(TEST_CV)
        counts.append(len(issues))
    
    unique_counts = set(counts)
    
    assert len(unique_counts) == 1, \
        f"FAIL: Got different counts: {unique_counts}"
    
    print(f"✅ PASSED: All 10 runs produced {counts[0]} issues")
    return True


def test_severity_assignment():
    """
    Test that severity assignment is deterministic.
    """
    print("Test 3: Severity assignment (10 runs)")
    
    results = []
    for i in range(10):
        issues = detect_all_issues(TEST_CV)
        issues = assign_severity_to_issues(issues)
        severities = tuple(sorted([iss['severity'] for iss in issues]))
        results.append(severities)
    
    unique_results = set(results)
    
    assert len(unique_results) == 1, \
        f"FAIL: Got different severities in different runs!"
    
    issues = detect_all_issues(TEST_CV)
    issues = assign_severity_to_issues(issues)
    
    from collections import Counter
    counts = Counter([iss['severity'] for iss in issues])
    
    print(f"✅ PASSED: Consistent severities - {dict(counts)}")
    return True


def test_specific_detections():
    """
    Test that specific issues are detected correctly.
    """
    print("Test 4: Specific issue detection")
    
    issues = detect_all_issues(TEST_CV)
    issue_types = [iss['issue_type'] for iss in issues]
    
    expected = [
        'WEAK_ACTION_VERBS',
        'VAGUE_DESCRIPTION',
        'NO_METRICS',
    ]
    
    for expected_type in expected:
        assert expected_type in issue_types, \
            f"FAIL: Expected {expected_type} to be detected"
        print(f"  ✓ {expected_type} detected")
    
    print("✅ PASSED: All expected issues detected")
    return True


def run_all_tests():
    """Run all determinism tests."""
    print("\n" + "="*60)
    print("DETERMINISM TESTS FOR STATIC CV DETECTION")
    print("="*60 + "\n")
    
    tests = [
        test_same_issues_every_time,
        test_same_count_every_time,
        test_severity_assignment,
        test_specific_detections,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
        print()
    
    print("="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - Detection is DETERMINISTIC!")
    else:
        print("\n⚠️ SOME TESTS FAILED - Please fix before proceeding")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
