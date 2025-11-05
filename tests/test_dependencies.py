"""
Dependency Version Verification Tests

Purpose:
- Verify critical package versions match requirements
- Catch accidental upgrades (especially numpy 2.x)
- Prevent compatibility issues before they cause problems

Usage:
    pytest tests/test_dependencies.py
    python tests/test_dependencies.py  # Run standalone

Created: 2025-11-03
Related: Phase 0-DEP Task 0-DEP.5
See: DEPENDENCY-MANAGEMENT-GUIDE.md for version strategy
"""

import sys
import importlib.util


def check_package_installed(package_name):
    """Check if a package is installed."""
    spec = importlib.util.find_spec(package_name)
    return spec is not None


def get_package_version(package_name):
    """Get installed version of a package."""
    try:
        module = __import__(package_name)
        return module.__version__
    except (ImportError, AttributeError):
        return None


# ============================================================================
# CRITICAL PACKAGES - Must be exact versions
# ============================================================================
# These packages have breaking changes between versions
# numpy 2.x breaks compatibility with many ML packages

def test_numpy_version():
    """Verify numpy is 1.24.x (not 2.x)."""
    import numpy
    version = numpy.__version__

    # Must be 1.24.x
    assert version.startswith('1.24.'), \
        f"[FAIL] numpy version {version} is incorrect! Must be 1.24.x (numpy 2.x breaks compatibility)"

    print(f"[OK] numpy version: {version}")


def test_scipy_version():
    """Verify scipy is 1.11.x."""
    import scipy
    version = scipy.__version__

    # Must be 1.11.x
    assert version.startswith('1.11.'), \
        f"[FAIL] scipy version {version} is incorrect! Must be 1.11.x"

    print(f"[OK] scipy version: {version}")


def test_spacy_version():
    """Verify spacy is 3.7.5."""
    import spacy
    version = spacy.__version__

    # Must be exactly 3.7.5
    assert version == '3.7.5', \
        f"[FAIL] spacy version {version} is incorrect! Must be 3.7.5"

    print(f"[OK] spacy version: {version}")


def test_thinc_version():
    """Verify thinc is 8.2.x."""
    import thinc
    version = thinc.__version__

    # Must be 8.2.x
    assert version.startswith('8.2.'), \
        f"[FAIL] thinc version {version} is incorrect! Must be 8.2.x"

    print(f"[OK] thinc version: {version}")


# ============================================================================
# IMPORTANT PACKAGES - Should be within expected ranges
# ============================================================================

def test_redis_version():
    """Verify redis package is installed (5.x-7.x acceptable)."""
    import redis
    version = redis.__version__

    major = int(version.split('.')[0])
    assert 5 <= major < 8, \
        f"[FAIL] redis version {version} is outside expected range (5.x-7.x)"

    print(f"[OK] redis version: {version}")


def test_langchain_versions():
    """Verify LangChain packages are compatible versions."""
    import langgraph
    import langchain

    langgraph_version = langgraph.__version__
    langchain_version = langchain.__version__

    # LangGraph should be 0.2.x
    assert langgraph_version.startswith('0.2.'), \
        f"[FAIL] langgraph version {langgraph_version} is incorrect! Expected 0.2.x"

    # LangChain should be 0.3.x
    assert langchain_version.startswith('0.3.'), \
        f"[FAIL] langchain version {langchain_version} is incorrect! Expected 0.3.x"

    print(f"[OK] langgraph version: {langgraph_version}")
    print(f"[OK] langchain version: {langchain_version}")


def test_openai_version():
    """Verify OpenAI package is recent version."""
    import openai
    version = openai.__version__

    # Should be 1.x
    major = int(version.split('.')[0])
    assert major >= 1, \
        f"[FAIL] openai version {version} is too old! Must be 1.x+"

    print(f"[OK] openai version: {version}")


def test_pinecone_version():
    """Verify Pinecone client version."""
    import pinecone
    version = pinecone.__version__

    # Should be 5.x
    assert version.startswith('5.'), \
        f"[FAIL] pinecone version {version} is incorrect! Expected 5.x"

    print(f"[OK] pinecone version: {version}")


# ============================================================================
# OPTIONAL PACKAGES - Verify if installed
# ============================================================================

def test_presidio_installed():
    """Verify Presidio packages are installed (Phase 4)."""
    assert check_package_installed('presidio_analyzer'), \
        "[FAIL] presidio-analyzer is not installed! Required for Phase 4 (PII Detection)"

    assert check_package_installed('presidio_anonymizer'), \
        "[FAIL] presidio-anonymizer is not installed! Required for Phase 4 (PII Detection)"

    from presidio_analyzer import __version__ as analyzer_version
    from presidio_anonymizer import __version__ as anonymizer_version

    print(f"[OK] presidio-analyzer version: {analyzer_version}")
    print(f"[OK] presidio-anonymizer version: {anonymizer_version}")


def test_sentence_transformers_installed():
    """Verify sentence-transformers is installed (Phase 2/3)."""
    assert check_package_installed('sentence_transformers'), \
        "[FAIL] sentence-transformers is not installed! Required for Phase 2/3"

    from sentence_transformers import __version__ as st_version
    print(f"[OK] sentence-transformers version: {st_version}")


def test_celery_installed():
    """Verify Celery is installed (Phase 7)."""
    assert check_package_installed('celery'), \
        "[FAIL] celery is not installed! Required for Phase 7 (Async Processing)"

    import celery
    print(f"[OK] celery version: {celery.__version__}")


# ============================================================================
# COMPATIBILITY CHECKS
# ============================================================================

def test_numpy_scipy_compatibility():
    """Verify numpy and scipy versions are compatible."""
    import numpy
    import scipy

    numpy_version = numpy.__version__
    scipy_version = scipy.__version__

    # numpy 1.24.x works with scipy 1.11.x
    # numpy 2.x does NOT work with scipy 1.11.x
    assert numpy_version.startswith('1.24.') and scipy_version.startswith('1.11.'), \
        f"[FAIL] numpy {numpy_version} and scipy {scipy_version} are not compatible!"

    print(f"[OK] numpy {numpy_version} and scipy {scipy_version} are compatible")


def test_spacy_model_installed():
    """Verify Spacy en_core_web_lg model is installed."""
    import spacy

    try:
        nlp = spacy.load('en_core_web_lg')
        model_name = nlp.meta['name']
        model_version = nlp.meta['version']
        print(f"[OK] Spacy model: {model_name} v{model_version}")
    except OSError:
        raise AssertionError(
            "[FAIL] Spacy model 'en_core_web_lg' is not installed!\n"
            "Install with: python -m spacy download en_core_web_lg"
        )


# ============================================================================
# SUMMARY TEST
# ============================================================================

def test_all_critical_packages_summary():
    """Print summary of all critical package versions."""
    print("\n" + "="*60)
    print("CRITICAL PACKAGE VERSIONS SUMMARY")
    print("="*60)

    packages = {
        'numpy': '1.24.x',
        'scipy': '1.11.x',
        'spacy': '3.7.5',
        'thinc': '8.2.x',
        'redis': '5.x-7.x',
        'langgraph': '0.2.x',
        'langchain': '0.3.x',
        'openai': '1.x+',
        'pinecone': '5.x',
    }

    print(f"\n{'Package':<20} {'Expected':<15} {'Installed':<15} {'Status'}")
    print("-" * 60)

    all_pass = True
    for package, expected in packages.items():
        try:
            version = get_package_version(package)
            if version:
                status = "[OK]"
            else:
                status = "[NOT INSTALLED]"
                all_pass = False
            print(f"{package:<20} {expected:<15} {version:<15} {status}")
        except Exception as e:
            print(f"{package:<20} {expected:<15} {'ERROR':<15} [FAIL] {str(e)[:20]}")
            all_pass = False

    print("="*60)
    if all_pass:
        print("[OK] ALL CRITICAL PACKAGES ARE CORRECT")
    else:
        print("[FAIL] SOME PACKAGES HAVE ISSUES")
    print("="*60 + "\n")

    assert all_pass, "Some critical packages have incorrect versions!"


# ============================================================================
# MAIN - Run all tests
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("DDN AI PROJECT - DEPENDENCY VERSION VERIFICATION")
    print("="*70 + "\n")

    tests = [
        ("numpy version", test_numpy_version),
        ("scipy version", test_scipy_version),
        ("spacy version", test_spacy_version),
        ("thinc version", test_thinc_version),
        ("redis package", test_redis_version),
        ("langchain versions", test_langchain_versions),
        ("openai version", test_openai_version),
        ("pinecone version", test_pinecone_version),
        ("presidio packages", test_presidio_installed),
        ("sentence-transformers", test_sentence_transformers_installed),
        ("celery package", test_celery_installed),
        ("numpy-scipy compatibility", test_numpy_scipy_compatibility),
        ("spacy model", test_spacy_model_installed),
        ("summary", test_all_critical_packages_summary),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n[TEST] Testing {test_name}...")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"[FAIL] ERROR: {e}")
            failed += 1

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")

    if failed > 0:
        print("[WARNING] DEPENDENCY ISSUES DETECTED!")
        print("See DEPENDENCY-MANAGEMENT-GUIDE.md for how to fix.")
        sys.exit(1)
    else:
        print("[OK] ALL DEPENDENCY CHECKS PASSED!")
        sys.exit(0)
