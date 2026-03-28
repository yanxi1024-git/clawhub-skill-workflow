#!/usr/bin/env python3
"""
Prepare a skill for publishing to ClawHub.
"""

import os
import sys
import json
import yaml
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Allowed text file extensions (from ClawHub docs)
TEXT_EXTENSIONS = {
    '.py', '.md', '.json', '.txt', '.sh', '.yaml', '.yml', 
    '.js', '.ts', '.html', '.css', '.xml', '.csv', '.toml',
    '.ini', '.cfg', '.conf', '.properties', '.rst', '.tex'
}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Prepare skill for ClawHub publishing")
    parser.add_argument("--path", required=True, help="Path to skill directory")
    parser.add_argument("--version", help="Version to set (e.g., 1.0.0)")
    parser.add_argument("--name", help="Skill name")
    parser.add_argument("--description", help="Skill description")
    parser.add_argument("--clean-binary", action="store_true", help="Remove binary files")
    parser.add_argument("--backup", action="store_true", help="Create backup before changes")
    parser.add_argument("--output", help="Output directory (default: same as input)")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't modify")
    
    return parser.parse_args()

def validate_skill_directory(path):
    """Validate skill directory structure."""
    print(f"🔍 Validating skill directory: {path}")
    
    if not os.path.exists(path):
        print(f"❌ Directory does not exist: {path}")
        return False
    
    if not os.path.isdir(path):
        print(f"❌ Not a directory: {path}")
        return False
    
    # Check for SKILL.md
    skill_md_path = os.path.join(path, "SKILL.md")
    skill_md_lower_path = os.path.join(path, "skill.md")
    
    if not os.path.exists(skill_md_path) and not os.path.exists(skill_md_lower_path):
        print("❌ No SKILL.md or skill.md found")
        return False
    
    print("✅ Valid directory structure")
    return True

def check_skill_md(path):
    """Check and parse SKILL.md."""
    print("\n🔍 Checking SKILL.md...")
    
    skill_md_path = os.path.join(path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        skill_md_path = os.path.join(path, "skill.md")
    
    if not os.path.exists(skill_md_path):
        print("❌ SKILL.md not found")
        return None
    
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for YAML frontmatter
        if not content.startswith('---'):
            print("⚠️  No YAML frontmatter found (should start with '---')")
            return {"content": content, "has_frontmatter": False}
        
        # Parse YAML frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            print("⚠️  Malformed YAML frontmatter")
            return {"content": content, "has_frontmatter": True, "malformed": True}
        
        try:
            frontmatter = yaml.safe_load(parts[1])
            print("✅ Valid YAML frontmatter")
            
            # Check required fields
            if 'name' not in frontmatter:
                print("⚠️  Missing 'name' field in frontmatter")
            else:
                print(f"  Name: {frontmatter.get('name')}")
            
            if 'description' not in frontmatter:
                print("⚠️  Missing 'description' field in frontmatter")
            else:
                desc = frontmatter.get('description', '')
                print(f"  Description: {desc[:50]}..." if len(desc) > 50 else f"  Description: {desc}")
            
            if 'version' not in frontmatter:
                print("⚠️  Missing 'version' field in frontmatter")
            else:
                print(f"  Version: {frontmatter.get('version')}")
            
            if 'license' not in frontmatter:
                print("⚠️  Missing 'license' field in frontmatter (recommended: MIT)")
            
            return {
                "content": content,
                "has_frontmatter": True,
                "frontmatter": frontmatter,
                "parts": parts
            }
            
        except yaml.YAMLError as e:
            print(f"❌ YAML parsing error: {e}")
            return {"content": content, "has_frontmatter": True, "yaml_error": str(e)}
            
    except Exception as e:
        print(f"❌ Error reading SKILL.md: {e}")
        return None

def check_file_types(path):
    """Check for non-text files."""
    print("\n🔍 Checking file types...")
    
    non_text_files = []
    total_files = 0
    text_files = 0
    
    for root, dirs, files in os.walk(path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            # Skip hidden files
            if file.startswith('.'):
                continue
                
            total_files += 1
            filepath = os.path.join(root, file)
            
            # Check extension
            ext = os.path.splitext(file)[1].lower()
            
            if ext in TEXT_EXTENSIONS:
                text_files += 1
            else:
                # Check if it might be text by content
                try:
                    with open(filepath, 'rb') as f:
                        chunk = f.read(1024)
                        # Very basic text detection
                        if b'\x00' not in chunk:
                            text_files += 1
                            print(f"  ⚠️  {filepath} (no extension but appears to be text)")
                        else:
                            non_text_files.append(filepath)
                except:
                    non_text_files.append(filepath)
    
    print(f"  Total files: {total_files}")
    print(f"  Text files: {text_files}")
    print(f"  Non-text files: {len(non_text_files)}")
    
    if non_text_files:
        print("\n⚠️  Non-text files found (may cause publishing issues):")
        for f in non_text_files[:10]:  # Show first 10
            print(f"  - {os.path.relpath(f, path)}")
        if len(non_text_files) > 10:
            print(f"  ... and {len(non_text_files) - 10} more")
    
    return non_text_files

def check_file_sizes(path):
    """Check file sizes."""
    print("\n🔍 Checking file sizes...")
    
    large_files = []
    total_size = 0
    
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
                
            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath)
                total_size += size
                
                # Check individual file size (200KB limit)
                if size > 200 * 1024:  # 200KB
                    large_files.append((filepath, size))
            except:
                pass
    
    # Convert to human readable
    def human_size(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    print(f"  Total size: {human_size(total_size)}")
    
    if total_size > 50 * 1024 * 1024:  # 50MB
        print(f"⚠️  Total size exceeds 50MB limit: {human_size(total_size)}")
    
    if large_files:
        print("\n⚠️  Large files found (>200KB):")
        for filepath, size in large_files[:5]:
            relpath = os.path.relpath(filepath, path)
            print(f"  - {relpath}: {human_size(size)}")
    
    return large_files, total_size

def update_skill_md(path, version=None, name=None, description=None):
    """Update SKILL.md with new information."""
    print("\n📝 Updating SKILL.md...")
    
    skill_info = check_skill_md(path)
    if not skill_info:
        print("❌ Cannot update SKILL.md")
        return False
    
    skill_md_path = os.path.join(path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        skill_md_path = os.path.join(path, "skill.md")
    
    if not skill_info.get("has_frontmatter") or not skill_info.get("frontmatter"):
        print("❌ SKILL.md doesn't have valid frontmatter to update")
        return False
    
    frontmatter = skill_info["frontmatter"].copy()
    
    # Update fields if provided
    updated = False
    if version and frontmatter.get('version') != version:
        print(f"  Updating version: {frontmatter.get('version')} → {version}")
        frontmatter['version'] = version
        updated = True
    
    if name and frontmatter.get('name') != name:
        print(f"  Updating name: {frontmatter.get('name')} → {name}")
        frontmatter['name'] = name
        updated = True
    
    if description and frontmatter.get('description') != description:
        old_desc = frontmatter.get('description', '')
        new_desc_short = description[:50] + "..." if len(description) > 50 else description
        print(f"  Updating description: {old_desc[:50]}... → {new_desc_short}")
        frontmatter['description'] = description
        updated = True
    
    if not updated:
        print("  No updates needed")
        return True
    
    # Reconstruct content
    try:
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        new_content = f"---\n{new_frontmatter}---\n{skill_info['parts'][2]}"
        
        # Create backup
        backup_path = skill_md_path + ".backup"
        shutil.copy2(skill_md_path, backup_path)
        
        # Write new content
        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ SKILL.md updated successfully")
        print(f"   Backup saved to: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating SKILL.md: {e}")
        return False

def clean_binary_files(path, dry_run=False):
    """Remove binary files."""
    print("\n🧹 Cleaning binary files...")
    
    files_to_remove = []
    
    for root, dirs, files in os.walk(path):
        # Skip .git and other hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            # Skip hidden files
            if file.startswith('.'):
                continue
                
            filepath = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            # Skip text extensions
            if ext in TEXT_EXTENSIONS:
                continue
            
            # Check if it's binary
            try:
                with open(filepath, 'rb') as f:
                    chunk = f.read(1024)
                    if b'\x00' in chunk:  # Null byte indicates binary
                        files_to_remove.append(filepath)
            except:
                files_to_remove.append(filepath)
    
    if not files_to_remove:
        print("  No binary files found")
        return []
    
    print(f"  Found {len(files_to_remove)} binary files")
    
    if not dry_run:
        removed = []
        for filepath in files_to_remove:
            try:
                os.remove(filepath)
                removed.append(filepath)
                print(f"  Removed: {os.path.relpath(filepath, path)}")
            except Exception as e:
                print(f"  ❌ Error removing {filepath}: {e}")
        
        print(f"✅ Removed {len(removed)} binary files")
        return removed
    else:
        print("Dry run - would remove:")
        for filepath in files_to_remove[:10]:
            print(f"  - {os.path.relpath(filepath, path)}")
        if len(files_to_remove) > 10:
            print(f"  ... and {len(files_to_remove) - 10} more")
        return files_to_remove

def create_backup(path, output_dir=None):
    """Create backup of skill directory."""
    print("\n💾 Creating backup...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    skill_name = os.path.basename(os.path.normpath(path))
    backup_name = f"{skill_name}_backup_{timestamp}"
    
    if output_dir:
        backup_path = os.path.join(output_dir, backup_name)
    else:
        backup_path = os.path.join(os.path.dirname(path), backup_name)
    
    try:
        shutil.copytree(path, backup_path, 
                       ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.git', '*.backup'))
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def generate_report(path, non_text_files, large_files, total_size):
    """Generate preparation report."""
    print("\n" + "=" * 60)
    print("Preparation Report")
    print("=" * 60)
    
    skill_info = check_skill_md(path)
    
    if skill_info and skill_info.get("frontmatter"):
        fm = skill_info["frontmatter"]
        print(f"Skill: {fm.get('name', 'Unknown')}")
        print(f"Version: {fm.get('version', 'Unknown')}")
        print(f"Description: {fm.get('description', 'Unknown')[:80]}...")
    
    # Convert sizes
    def human_size(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    print(f"\nFile Statistics:")
    print(f"  Total size: {human_size(total_size)}")
    print(f"  Non-text files: {len(non_text_files)}")
    print(f"  Large files (>200KB): {len(large_files)}")
    
    print(f"\nIssues found:")
    issues = []
    
    if total_size > 50 * 1024 * 1024:
        issues.append("Total size exceeds 50MB limit")
    
    if len(non_text_files) > 0:
        issues.append(f"Has {len(non_text_files)} non-text files")
    
    if len(large_files) > 0:
        issues.append(f"Has {len(large_files)} files >200KB")
    
    if not skill_info or not skill_info.get("has_frontmatter"):
        issues.append("Missing or invalid YAML frontmatter")
    else:
        fm = skill_info.get("frontmatter", {})
        if 'name' not in fm:
            issues.append("Missing 'name' in frontmatter")
        if 'version' not in fm:
            issues.append("Missing 'version' in frontmatter")
        if 'description' not in fm:
            issues.append("Missing 'description' in frontmatter")
    
    if not issues:
        print("  ✅ No issues found!")
        print("\n🎉 Skill is ready for publishing!")
    else:
        for issue in issues:
            print(f"  ⚠️  {issue}")
        
        print("\n⚠️  Please fix the issues above before publishing.")
        print("\nRecommended actions:")
        if len(non_text_files) > 0:
            print("  - Run with --clean-binary to remove non-text files")
        if total_size > 50 * 1024 * 1024:
            print("  - Reduce total size by removing large files")
        if not skill_info or not skill_info.get("has_frontmatter"):
            print("  - Ensure SKILL.md has valid YAML frontmatter")
    
    return len(issues) == 0

def main():
    """Main function."""
    args = parse_args()
    
    print("=" * 60)
    print("ClawHub Skill Preparation")
    print("=" * 60)
    
    # Validate input
    if not validate_skill_directory(args.path):
        return 1
    
    # Create backup if requested
    backup_path = None
    if args.backup and not args.validate_only:
        backup_path = create_backup(args.path, args.output)
    
    # Check SKILL.md
    skill_info = check_skill_md(args.path)
    if not skill_info:
        print("❌ Cannot proceed without valid SKILL.md")
        return 1
    
    # Update SKILL.md if requested
    if (args.version or args.name or args.description) and not args.validate_only:
        if not update_skill_md(args.path, args.version, args.name, args.description):
            print("❌ Failed to update SKILL.md")
            return 1
    
    # Check file types
    non_text_files = check_file_types(args.path)
    
    # Clean binary files if requested
    if args.clean_binary and not args.validate_only:
        removed = clean_binary_files(args.path, dry_run=False)
        # Re-check after cleaning
        non_text_files = check_file_types(args.path)
    
    # Check file sizes
    large_files, total_size = check_file_sizes(args.path)
    
    # Generate report
    is_ready = generate_report(args.path, non_text_files, large_files, total_size)
    
    print("\n" + "=" * 60)
    if args.validate_only:
        print("Validation complete")
        if is_ready:
            print("✅ Skill is ready for publishing!")
            return 0
        else:
            print("⚠️  Skill needs fixes before publishing")
            return 1
    else:
        print("Preparation complete")
        if backup_path:
            print(f"📦 Backup saved to: {backup_path}")
        
        if is_ready:
            print("🎉 Skill is ready for publishing!")
            print("\nNext step:")
            print(f"  python3 publish_skill.py --path {args.path}")
        else:
            print("⚠️  Please fix the issues above before publishing")
        
        return 0 if is_ready else 1

if __name__ == "__main__":
    sys.exit(main())