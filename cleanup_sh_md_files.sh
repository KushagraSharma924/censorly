#!/bin/bash

# Script to safely remove unused shell and markdown files
# Generated on: $(date)

set -e  # Exit on any error

TRASH_DIR="/Users/kushagra/Desktop/censorly/trash/unused_sh_md_files_$(date +%Y%m%d_%H%M%S)"

echo "Creating trash directory: $TRASH_DIR"
mkdir -p "$TRASH_DIR"

# List of unused/empty shell and markdown files to remove
UNUSED_FILES=(
    # Empty shell files
    "backend/deploy.sh"
    "backend/deployment-test.sh"
    "backend/start.sh"
    
    # Temporary/empty markdown files
    "RENDER_DEPLOYMENT_READY.md"
    "RENDER_PORT_FIX.md"
    "RENDER_PORT_FIXED.md"
    
    # Our own cleanup script (no longer needed)
    "cleanup_empty_files.sh"
    
    # Cleanup report (temporary documentation)
    "EMPTY_FILES_CLEANUP_REPORT.md"
)

# Files to KEEP (have useful content or are important)
KEEP_FILES=(
    "README.md"  # Has project documentation
)

echo "Files that will be KEPT (have useful content):"
for file in "${KEEP_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ Keeping: $file"
    fi
done

echo ""
echo "Moving unused files to trash directory..."

for file in "${UNUSED_FILES[@]}"; do
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
echo "Unused files moved to: $TRASH_DIR"
echo ""
echo "Files processed:"
for file in "${UNUSED_FILES[@]}"; do
    if [ -f "$TRASH_DIR/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (not found or failed to move)"
    fi
done

echo ""
echo "Files kept in project:"
for file in "${KEEP_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
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
