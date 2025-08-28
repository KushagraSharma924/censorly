#!/bin/bash

# Script to safely remove empty files by moving them to a trash directory
# Generated on: $(date)

set -e  # Exit on any error

TRASH_DIR="/Users/kushagra/Desktop/censorly/trash/empty_files_$(date +%Y%m%d_%H%M%S)"

echo "Creating trash directory: $TRASH_DIR"
mkdir -p "$TRASH_DIR"

# List of empty files to remove (verified to be truly empty and not referenced)
EMPTY_FILES=(
    "frontend/src/utils/test-user-utils.ts"
    "frontend/src/components/ui/user-avatar.tsx"
    "frontend/src/components/ApiMonitor.tsx"
    "backend/test_app_startup.py"
    "backend/config.py"
    "backend/test_dependencies.py"
    "backend/decorators/rate_limiting.py"
    "backend/start_docker.py"
    "backend/app_supabase.py"
    "backend/run_production.py"
    "backend/templates/dashboard.html"
    "backend/start_render.py"
    "backend/run_server.py"
)

echo "Moving empty files to trash directory..."

for file in "${EMPTY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Moving: $file"
        
        # Create directory structure in trash
        file_dir=$(dirname "$file")
        mkdir -p "$TRASH_DIR/$file_dir"
        
        # Move file to trash
        mv "$file" "$TRASH_DIR/$file"
        
        echo "  ✓ Moved to: $TRASH_DIR/$file"
    else
        echo "  ⚠ File not found: $file"
    fi
done

echo ""
echo "=========================================="
echo "CLEANUP SUMMARY"
echo "=========================================="
echo "Empty files moved to: $TRASH_DIR"
echo ""
echo "Files processed:"
for file in "${EMPTY_FILES[@]}"; do
    if [ -f "$TRASH_DIR/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (not found or failed to move)"
    fi
done

echo ""
echo "To restore files if needed:"
echo "  cp -r $TRASH_DIR/* ."
echo ""
echo "To permanently delete (after verification):"
echo "  rm -rf $TRASH_DIR"
echo ""
echo "=========================================="
echo "CLEANUP COMPLETED SUCCESSFULLY"
echo "=========================================="
