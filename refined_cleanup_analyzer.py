#!/usr/bin/env python3
"""
Refined script to analyze unused files with proper import resolution.
"""

import os
import re
import json
from pathlib import Path

def get_project_files():
    """Get all relevant project files excluding dependencies"""
    project_root = "/Users/kushagra/Desktop/censorly"
    
    # Find all source files
    extensions = ['ts', 'tsx', 'js', 'jsx', 'py', 'css', 'json', 'html']
    all_files = []
    
    for ext in extensions:
        all_files.extend(Path(project_root).rglob(f"*.{ext}"))
    
    # Filter to only include actual project files
    project_files = []
    exclude_patterns = [
        '.venv/', 'node_modules/', 'dist/', 'build/', '__pycache__/', 
        '.git/', 'coverage/', '.pytest_cache/', 'venv/', 'env/'
    ]
    
    for file_path in all_files:
        file_str = str(file_path)
        if not any(pattern in file_str for pattern in exclude_patterns):
            project_files.append(file_str)
    
    return project_files

def extract_references(file_path):
    """Extract all file references from a file"""
    references = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return references
    
    # TypeScript/JavaScript/JSX imports and requires
    patterns = [
        r'import\s+.*?from\s+[\'"]([^\'\"]+)[\'"]',  # import ... from 'path'
        r'import\s*\(\s*[\'"]([^\'\"]+)[\'"]\s*\)',  # import('path')
        r'require\s*\(\s*[\'"]([^\'\"]+)[\'"]\s*\)',  # require('path')
        r'import\s+[\'"]([^\'\"]+)[\'"]',  # import 'path'
    ]
    
    # Python imports
    if file_path.endswith('.py'):
        patterns.extend([
            r'from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import',  # from module import
            r'import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',  # import module
        ])
    
    # HTML/CSS references
    if file_path.endswith(('.html', '.css', '.tsx', '.jsx')):
        patterns.extend([
            r'src\s*=\s*[\'"]([^\'\"]+)[\'"]',  # src="path"
            r'href\s*=\s*[\'"]([^\'\"]+)[\'"]',  # href="path"
            r'url\s*\(\s*[\'"]?([^\'\"]+)[\'"]?\s*\)',  # url(path)
        ])
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        references.update(matches)
    
    return references

def resolve_import_to_file(import_path, current_file, project_root):
    """Resolve an import path to actual file paths"""
    resolved_files = []
    
    # Skip external packages
    if (not import_path.startswith('.') and 
        not import_path.startswith('/') and 
        not import_path.startswith('@/') and
        not any(import_path.startswith(prefix) for prefix in ['backend', 'frontend', 'src'])):
        return []
    
    # Handle @/ alias (maps to frontend/src/)
    if import_path.startswith('@/'):
        base_path = os.path.join(project_root, 'frontend', 'src', import_path[2:])
    # Handle relative imports
    elif import_path.startswith('.'):
        current_dir = os.path.dirname(current_file)
        base_path = os.path.normpath(os.path.join(current_dir, import_path))
    # Handle absolute imports
    else:
        base_path = os.path.join(project_root, import_path)
    
    # Try different extensions and index files
    extensions = ['', '.js', '.jsx', '.ts', '.tsx', '.py', '.css', '.json']
    
    for ext in extensions:
        full_path = base_path + ext
        if os.path.exists(full_path):
            resolved_files.append(full_path)
            break
    else:
        # Try index files
        for ext in ['.js', '.jsx', '.ts', '.tsx']:
            index_path = os.path.join(base_path, f'index{ext}')
            if os.path.exists(index_path):
                resolved_files.append(index_path)
                break
    
    return resolved_files

def analyze_unused_files():
    """Main analysis function"""
    project_root = "/Users/kushagra/Desktop/censorly"
    project_files = get_project_files()
    
    print(f"Analyzing {len(project_files)} project files...")
    
    # Files that are always considered "entry points" or critical
    critical_files = {
        'package.json', 'package-lock.json', 'tsconfig.json', 'tsconfig.app.json', 
        'tsconfig.node.json', 'vite.config.ts', 'tailwind.config.ts', 'postcss.config.js',
        'eslint.config.js', 'components.json', 'vercel.json', 'index.html', 'main.tsx',
        'App.tsx', 'index.css', 'vite-env.d.ts', 'app.py', 'config.py', 'app_supabase.py',
        'requirements.txt', 'requirements-cloud.txt', 'requirements-phase1.txt',
        'Dockerfile', 'render.yaml', 'start.sh', '__init__.py'
    }
    
    referenced_files = set()
    
    # Add critical files
    for file_path in project_files:
        filename = os.path.basename(file_path)
        if filename in critical_files:
            referenced_files.add(file_path)
    
    # Analyze imports and references
    for file_path in project_files:
        imports = extract_references(file_path)
        
        for import_path in imports:
            resolved_paths = resolve_import_to_file(import_path, file_path, project_root)
            referenced_files.update(resolved_paths)
    
    # Find unused files
    unused_files = [f for f in project_files if f not in referenced_files]
    
    # Manual verification for some known used files
    definitely_used = [
        'backend/run_production.py',  # Production runner
        'backend/start_render.py',    # Render deployment
        'backend/start_docker.py',    # Docker deployment
        'backend/create_basic_user.py',  # User creation script
        'backend/test_app_startup.py',   # Testing
        'backend/test_dependencies.py',  # Testing
    ]
    
    for file_path in project_files:
        for used_file in definitely_used:
            if file_path.endswith(used_file):
                if file_path in unused_files:
                    unused_files.remove(file_path)
                referenced_files.add(file_path)
    
    return unused_files, referenced_files, project_files

def categorize_files(files, project_root):
    """Categorize files by type and location"""
    categories = {
        'frontend_components': [],
        'frontend_pages': [],
        'frontend_ui_components': [],
        'frontend_utils': [],
        'backend_api': [],
        'backend_services': [],
        'backend_utils': [],
        'backend_scripts': [],
        'data_files': [],
        'config_files': [],
        'other': []
    }
    
    for file_path in files:
        rel_path = os.path.relpath(file_path, project_root)
        
        if 'frontend/src/components/ui/' in file_path:
            categories['frontend_ui_components'].append(rel_path)
        elif 'frontend/src/components/' in file_path:
            categories['frontend_components'].append(rel_path)
        elif 'frontend/src/pages/' in file_path:
            categories['frontend_pages'].append(rel_path)
        elif 'frontend/src/' in file_path and ('/lib/' in file_path or '/utils/' in file_path):
            categories['frontend_utils'].append(rel_path)
        elif 'backend/api/' in file_path:
            categories['backend_api'].append(rel_path)
        elif 'backend/services/' in file_path:
            categories['backend_services'].append(rel_path)
        elif 'backend/utils/' in file_path:
            categories['backend_utils'].append(rel_path)
        elif 'backend/' in file_path and file_path.endswith('.py'):
            categories['backend_scripts'].append(rel_path)
        elif '/data/' in file_path or file_path.endswith('.json'):
            categories['data_files'].append(rel_path)
        elif any(config in file_path for config in ['config', '.json', '.css']):
            categories['config_files'].append(rel_path)
        else:
            categories['other'].append(rel_path)
    
    return categories

def main():
    project_root = "/Users/kushagra/Desktop/censorly"
    
    unused_files, referenced_files, all_files = analyze_unused_files()
    
    print(f"\nSUMMARY:")
    print(f"Total project files: {len(all_files)}")
    print(f"Referenced files: {len(referenced_files)}")
    print(f"Potentially unused files: {len(unused_files)}")
    
    if unused_files:
        print(f"\n{'='*60}")
        print("SAFE CANDIDATES FOR CLEANUP")
        print(f"{'='*60}")
        
        categories = categorize_files(unused_files, project_root)
        
        for category, files in categories.items():
            if files:
                print(f"\n{category.replace('_', ' ').title()} ({len(files)} files):")
                for file_path in sorted(files):
                    print(f"  - {file_path}")
    
    # Save detailed results
    results = {
        'summary': {
            'total_files': len(all_files),
            'referenced_files': len(referenced_files),
            'unused_files': len(unused_files)
        },
        'unused_files_by_category': categorize_files(unused_files, project_root),
        'unused_files': [os.path.relpath(f, project_root) for f in unused_files]
    }
    
    with open('cleanup_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed analysis saved to cleanup_analysis.json")

if __name__ == "__main__":
    main()
