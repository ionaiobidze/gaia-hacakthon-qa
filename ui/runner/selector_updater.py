#!/usr/bin/env python3
"""
Selector Updater (Final Version)
"""

import os
import ast
import shutil
from datetime import datetime
from typing import Dict, Optional
from agents.selector_agent import SelectorAgent

class SelectorUpdater:
    def __init__(self, backup_enabled: bool = True):
        self.backup_enabled = backup_enabled

    def _create_backup(self, file_path: str) -> Optional[str]:
        if not self.backup_enabled or not os.path.exists(file_path): return None
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(os.path.dirname(file_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"{os.path.basename(file_path)}.{timestamp}.bak")
            shutil.copy2(file_path, backup_path)
            print(f"📦 Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup for {file_path}: {e}"); return None

    def _replace_selector_in_line(self, line: str, new_value: str) -> str:
        """Replaces the selector string in a tuple, using triple quotes for robustness."""
        parts = line.split(',')
        if len(parts) < 2: return line
        first_part = parts[0]
        return f"{first_part}, '''{new_value}''')\n"

    def batch_update_from_mapping(
        self, file_path: str, mapping_results: Dict[str, SelectorAgent],
        confidence_threshold: float = 0.5, create_new_version: bool = False
    ) -> Dict:
        
        updates_to_apply = {
            name: result.new_selector
            for name, result in mapping_results.items()
            if result.confidence >= confidence_threshold and result.new_selector
        }
        
        print(f"\nApplying {len(updates_to_apply)} high-confidence updates (threshold >= {confidence_threshold}).")

        if not updates_to_apply:
            print("No high-confidence updates to apply."); return {"updates_applied": 0}

        self._create_backup(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(); lines = content.splitlines(True)

        try:
            # --- CORRECTED AST PARSING LOGIC ---
            tree = ast.parse(content)
            selector_lines = {}
            # 1. Find the ClassDef node named 'Locators'
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == 'Locators':
                    # 2. Iterate through its body
                    for item in node.body:
                        # 3. Find assignment statements
                        if isinstance(item, ast.Assign):
                            # 4. Get the variable name and line number
                            var_name = item.targets[0].id
                            selector_lines[var_name] = item.lineno
        except Exception as e:
            print(f"❌ AST parsing failed: {e}"); return {"updates_applied": 0}

        successful_updates = 0
        for name, new_value in updates_to_apply.items():
            if name in selector_lines:
                line_idx = selector_lines[name] - 1
                lines[line_idx] = self._replace_selector_in_line(lines[line_idx], new_value)
                print(f"  - Updated {name} -> '''{new_value}'''")
                successful_updates += 1
        
        output_path = file_path
        if create_new_version:
            base, ext = os.path.splitext(file_path)
            output_path = f"{base.replace('_v1', '')}_v2{ext}"
        
        with open(output_path, 'w', encoding='utf-8') as f: f.write("".join(lines))
            
        print(f"\n✅ Successfully created updated selector file: {output_path}")
        
        return {"output_file": output_path, "updates_applied": successful_updates}