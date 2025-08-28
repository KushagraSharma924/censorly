#!/usr/bin/env python3
"""
Script to analyze unused files in the codebase.
Scans for import statements, require calls, and other references.
"""

import os
import re
import json
from pathlib import Path

def find_all_files(directory, extensions):
    """Find all files with given extensions in directory"""
    files = []
    for ext in extensions:
        files.extend(Path(directory).rglob(f"*.{ext}"))
    return [str(f) for f in files]

def extract_imports_from_file(file_path):
    """Extract all import/require statements from a file"""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # TypeScript/JavaScript imports
        import_patterns = [
            r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',  # import ... from 'path'
            r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',  # import('path')
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',  # require('path')
            r'@import\s+[\'"]([^\'"]+)[\'"]',  # CSS @import
            r'import\s+[\'"]([^\'"]+)[\'"]',  # import 'path'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.update(matches)
            
        # Python imports
        python_patterns = [
            r'from\s+([^\s]+)\s+import',  # from module import
            r'import\s+([^\s,]+)',  # import module
        ]
        
        for pattern in python_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.update(matches)
            
        # HTML/CSS references
        html_patterns = [
            r'src\s*=\s*[\'"]([^\'"]+)[\'"]',  # src="path"
            r'href\s*=\s*[\'"]([^\'"]+)[\'"]',  # href="path"
            r'url\s*\(\s*[\'"]?([^\'"]+)[\'"]?\s*\)',  # url(path)
        ]
        
        for pattern in html_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.update(matches)
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
    return imports

def resolve_import_path(import_path, current_file, project_root):
    """Resolve import path to actual file path"""
    resolved_paths = []
    
    # Handle relative imports
    if import_path.startswith('.'):
        base_dir = os.path.dirname(current_file)
        resolved = os.path.normpath(os.path.join(base_dir, import_path))
        resolved_paths.append(resolved)
    
    # Handle absolute imports with @/ alias
    elif import_path.startswith('@/'):
        # For frontend, @/ typically maps to src/
        if 'frontend' in current_file:
            resolved = os.path.join(project_root, 'frontend', 'src', import_path[2:])
            resolved_paths.append(resolved)
    
    # Handle node_modules and external packages (skip these)
    elif not import_path.startswith('.') and not import_path.startswith('/'):
        # This is likely an external package, skip
        return []
    
    # Handle absolute paths
    else:
        resolved_paths.append(import_path)
    
    # Try to find actual file with extensions
    final_paths = []
    for path in resolved_paths:
        extensions = ['', '.js', '.jsx', '.ts', '.tsx', '.py', '.css', '.json']
        for ext in extensions:
            full_path = path + ext
            if os.path.exists(full_path):
                final_paths.append(full_path)
                break
        else:
            # Try index files
            for ext in ['.js', '.jsx', '.ts', '.tsx']:
                index_path = os.path.join(path, f'index{ext}')
                if os.path.exists(index_path):
                    final_paths.append(index_path)
                    break
    
    return final_paths

def analyze_project(project_root):
    """Analyze the entire project for unused files"""
    
    # Find all source files
    extensions = ['ts', 'tsx', 'js', 'jsx', 'py', 'css', 'json', 'html']
    all_files = find_all_files(project_root, extensions)
    
    # Filter to only include source files (exclude node_modules, dist, etc.)
    source_files = []
    exclude_dirs = {'node_modules', 'dist', 'build', '__pycache__', '.git', 'coverage'}
    
    for file_path in all_files:
        if not any(exclude_dir in file_path for exclude_dir in exclude_dirs):
            source_files.append(file_path)
    
    print(f"Found {len(source_files)} source files")
    
    # Track referenced files
    referenced_files = set()
    
    # Special files that are always considered "used"
    always_used = {
        'package.json', 'package-lock.json', 'tsconfig.json', 'tsconfig.app.json', 
        'tsconfig.node.json', 'vite.config.ts', 'tailwind.config.ts', 'postcss.config.js',
        'eslint.config.js', 'components.json', 'vercel.json', 'index.html', 'main.tsx',
        'App.tsx', 'index.css', 'vite-env.d.ts', '__init__.py', 'app.py', 'config.py',
        'requirements.txt', 'requirements-cloud.txt', 'requirements-phase1.txt'
    }
    
    # Add always used files to referenced set
    for file_path in source_files:
        filename = os.path.basename(file_path)
        if filename in always_used:
            referenced_files.add(file_path)
    
    # Analyze each file for imports
    for file_path in source_files:
        imports = extract_imports_from_file(file_path)
        
        for import_path in imports:
            resolved_paths = resolve_import_path(import_path, file_path, project_root)
            referenced_files.update(resolved_paths)
    
    # Find unused files
    unused_files = []
    for file_path in source_files:
        if file_path not in referenced_files:
            unused_files.append(file_path)
    
    return unused_files, referenced_files, source_files

def main():
    project_root = "/Users/kushagra/Desktop/censorly"
    
    print("Analyzing project for unused files...")
    unused_files, referenced_files, all_files = analyze_project(project_root)
    
    print(f"\nTotal files analyzed: {len(all_files)}")
    print(f"Referenced files: {len(referenced_files)}")
    print(f"Potentially unused files: {len(unused_files)}")
    
    if unused_files:
        print("\n" + "="*50)
        print("POTENTIALLY UNUSED FILES:")
        print("="*50)
        
        # Group by type
        by_type = {}
        for file_path in unused_files:
            ext = os.path.splitext(file_path)[1][1:]  # remove the dot
            if ext not in by_type:
                by_type[ext] = []
            by_type[ext].append(file_path)
        
        for ext, files in sorted(by_type.items()):
            print(f"\n{ext.upper()} files ({len(files)}):")
            for file_path in sorted(files):
                rel_path = os.path.relpath(file_path, project_root)
                print(f"  - {rel_path}")
    
    # Save results to JSON for further analysis
    results = {
        'unused_files': [os.path.relpath(f, project_root) for f in unused_files],
        'referenced_files': [os.path.relpath(f, project_root) for f in referenced_files],
        'total_files': len(all_files)
    }
    
    with open(os.path.join(project_root, 'unused_files_analysis.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed analysis saved to: unused_files_analysis.json")

if __name__ == "__main__":
    main()
