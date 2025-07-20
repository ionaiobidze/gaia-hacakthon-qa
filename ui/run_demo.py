import os
import subprocess
import sys
import time
import json
import inspect
import re
from typing import Optional, Dict
from runner.server_launcher import ReactServerManager
from runner.dom_fetcher import DOMFetcher
from agents.selector_agent import SelectorAgent
from runner.selector_updater import SelectorUpdater

# --- Configuration ---
REACT_V1_URL = "http://localhost:3000"
REACT_V2_URL = "http://localhost:3001"
PAGE_V1_SELECTORS_PATH = "page_selectors/page_v1.py"
TEST_FILE_PATH = "test/movie_app_tests.py"
DOM_SNAPSHOT_DIR = "dom_snapshots"
REPORTS_DIR = "reports"

last_test_output = ""

def run_command(command):
    global last_test_output
    print(f"\n▶️  Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=180)
        last_test_output = result.stdout + "\n" + result.stderr
        if result.returncode == 0:
            print("   ✅ Command successful.")
            return True
        else:
            print(f"   ❌ Command failed (Exit Code: {result.returncode}).")
            if last_test_output.strip():
                 print(f"--- Captured Log ---\n{last_test_output}\n--------------------")
            return False
    except Exception as e:
        print(f"   ❌ An error occurred: {e}"); last_test_output = str(e); return False

def get_selectors_from_module(module):
    selectors = {}
    for name, cls in inspect.getmembers(module, inspect.isclass):
        if name == 'Locators':
            for loc_name, loc_val in inspect.getmembers(cls):
                if not loc_name.startswith('__') and isinstance(loc_val, tuple):
                    selectors[loc_name] = loc_val[1]
    return selectors

def parse_failure_log_for_selector(log: str, all_selectors: Dict[str, str]) -> Optional[Dict[str, str]]:
    match = re.search(r'Unable to locate element: .* "selector": "([^"]*)"', log)
    if not match: return None
    failed_selector_value = match.group(1)
    for name, value in all_selectors.items():
        if value == failed_selector_value:
            print(f"   🕵️  Failure analysis determined selector '{name}' is the likely cause.")
            return {"selector_name": name, "error_message": f"Test failed with NoSuchElementException for selector: {failed_selector_value}"}
    return None

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key: print("⚠️  WARNING: OPENAI_API_KEY not set. Using rule-based fallback.")
    else: print("✅ OPENAI_API_KEY found. AI agent will be used.")

    os.makedirs(DOM_SNAPSHOT_DIR, exist_ok=True); os.makedirs(REPORTS_DIR, exist_ok=True)
    server_manager = ReactServerManager()
    
    try:
        print("\n" + "="*50 + "\n🚀 STEP 1: Starting Servers...\n" + "="*50)
        if not server_manager.start_all_servers(): raise RuntimeError("Could not start React servers.")
        
        # Prepare test module path for Python -m execution
        test_module_path = TEST_FILE_PATH.replace(".py", "").replace("/", ".").replace("\\", ".")
        print(f"📋 Using test module: {test_module_path}")
        
        print("\n" + "="*50 + "\n✅ STEP 2: Baseline Tests on V1...\n" + "="*50)
        os.environ['TEST_URL'] = REACT_V1_URL
        os.environ['SELECTOR_MODULE'] = "page_selectors.page_v1"
        if not run_command([sys.executable, "-m", test_module_path]): raise RuntimeError("Baseline tests on v1 failed.")

        print("\n" + "="*50 + "\n❌ STEP 3: Failure Detection on V2...\n" + "="*50)
        os.environ['TEST_URL'] = REACT_V2_URL
        if run_command([sys.executable, "-m", test_module_path]): raise RuntimeError("Tests on v2 passed unexpectedly.")
        
        # --- RE-ENGINEERED DOM FETCHING FOR GUARANTEED CORRECTNESS ---
        print("\n" + "="*50 + "\n📄 STEP 4: Fetching DOMs for Analysis...\n" + "="*50)
        
        print("   - Fetching DOM from V1 in an isolated session...")
        with DOMFetcher() as fetcher_v1:
            dom_v1 = fetcher_v1.fetch_dom(REACT_V1_URL)
            fetcher_v1.save_dom_to_file(dom_v1, os.path.join(DOM_SNAPSHOT_DIR, "react_v1_dom.json"))
            
        print("   - Fetching DOM from V2 in a new, isolated session...")
        with DOMFetcher() as fetcher_v2:
            dom_v2 = fetcher_v2.fetch_dom(REACT_V2_URL)
            fetcher_v2.save_dom_to_file(dom_v2, os.path.join(DOM_SNAPSHOT_DIR, "react_v2_dom.json"))

        if not (dom_v1.get("success") and dom_v2.get("success")):
            raise RuntimeError("Failed to fetch one or both DOMs.")
        
        agent = SelectorAgent(api_key=api_key)
        updater = SelectorUpdater()
        from page_selectors import page_v1
        selectors_to_map = get_selectors_from_module(page_v1)
        
        print("\n" + "="*50 + "\n🤖 STEP 5: Initial Healing Attempt...\n" + "="*50)
        mapping_results = agent.batch_map_selectors(selectors_to_map, dom_v1["html"], dom_v2["html"])
        updates_info = updater.batch_update_from_mapping(PAGE_V1_SELECTORS_PATH, mapping_results, create_new_version=True)
        
        # Quality gate: if no file was created because confidence was too low, abort.
        if updates_info['updates_applied'] < 1:
             raise RuntimeError(f"Mapping quality too low. No high-confidence selectors were found. Aborting.")

        print("\n" + "="*50 + "\n✅ STEP 6: Validating First Healing Attempt...\n" + "="*50)
        os.environ['SELECTOR_MODULE'] = "page_selectors.page_v2"
        first_heal_passed = run_command([sys.executable, "-m", test_module_path])

        final_test_passed = first_heal_passed
        
        if not first_heal_passed:
            print("\n" + "="*50 + "\n🧠 STEP 7: Initiating Self-Correction Loop...\n" + "="*50)
            failure_context = parse_failure_log_for_selector(last_test_output, selectors_to_map)
            
            if failure_context:
                print("\n" + "="*50 + "\n🤖 STEP 7b: Focused Re-Healing Attempt...\n" + "="*50)
                new_mapping_results = agent.batch_map_selectors(selectors_to_map, dom_v1["html"], dom_v2["html"], failure_context)
                updater.batch_update_from_mapping(PAGE_V1_SELECTORS_PATH, new_mapping_results, create_new_version=True)
                
                print("\n" + "="*50 + "\n✅ STEP 7c: Validating Second Healing Attempt...\n" + "="*50)
                final_test_passed = run_command([sys.executable, "-m", test_module_path])
            else:
                print("   ⚠️ Could not determine specific selector from failure log. Cannot re-heal.")
                
        print("\n" + "="*50)
        if final_test_passed:
            print("🎉🎉🎉 DEMO COMPLETE: SUCCESS! 🎉🎉🎉")
        else:
            print("💔 DEMO COMPLETE: FAILURE 💔")
        print("="*50)

    except Exception as e:
        print(f"\n❌ A critical error occurred: {e}"); sys.exit(1)
    finally:
        print("\n" + "="*50 + "\n🛑 FINAL STEP: Stopping Servers...\n" + "="*50)
        server_manager.stop_all_servers()

if __name__ == "__main__":
    main()