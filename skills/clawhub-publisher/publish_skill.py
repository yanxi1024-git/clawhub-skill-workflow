#!/usr/bin/env python3
"""
Publish a skill to ClawHub with best practices.
"""

import os
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Publish skill to ClawHub")
    parser.add_argument("--path", required=True, help="Path to skill directory")
    parser.add_argument("--slug", help="Skill slug (default: from SKILL.md or directory name)")
    parser.add_argument("--version", help="Version to publish (default: from SKILL.md)")
    parser.add_argument("--name", help="Display name (default: from SKILL.md)")
    parser.add_argument("--changelog", help="Changelog text")
    parser.add_argument("--tags", default="latest", help="Comma-separated tags (default: latest)")
    parser.add_argument("--no-input", action="store_true", help="Disable prompts")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be published")
    parser.add_argument("--retry", type=int, default=3, help="Number of retries on failure")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    
    return parser.parse_args()

def get_skill_info(path):
    """Get skill information from SKILL.md."""
    import yaml
    
    skill_md_path = os.path.join(path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        skill_md_path = os.path.join(path, "skill.md")
    
    if not os.path.exists(skill_md_path):
        return None
    
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return {"name": os.path.basename(path)}
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {"name": os.path.basename(path)}
        
        frontmatter = yaml.safe_load(parts[1])
        return frontmatter
    except:
        return {"name": os.path.basename(path)}

def check_existing_version(slug, version):
    """Check if version already exists on ClawHub."""
    print(f"🔍 Checking if version {version} already exists...")
    
    try:
        result = subprocess.run(
            ["clawhub", "inspect", slug],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout
            # Look for version in output
            for line in output.split('\n'):
                if "Latest:" in line:
                    latest_version = line.split("Latest:")[1].strip()
                    if latest_version == version:
                        print(f"⚠️  Version {version} is already the latest")
                        return True
                elif version in line and "version" in line.lower():
                    print(f"⚠️  Version {version} may already exist")
                    return True
        
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout checking existing version")
        return False
    except Exception as e:
        print(f"⚠️  Error checking existing version: {e}")
        return False

def generate_changelog(path, version):
    """Generate changelog if not provided."""
    # Simple changelog generation
    changelog = f"Release {version}\n\n"
    
    # Try to get git history if available
    try:
        result = subprocess.run(
            ["git", "-C", path, "log", "--oneline", "-10"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            changelog += "Recent changes:\n"
            for line in result.stdout.strip().split('\n'):
                changelog += f"- {line}\n"
        else:
            changelog += "Initial release or manual update\n"
    except:
        changelog += "Initial release or manual update\n"
    
    return changelog

def publish_skill(path, slug, version, name, changelog, tags, no_input=False, dry_run=False):
    """Publish skill to ClawHub."""
    print(f"\n🚀 Publishing {slug}@{version}")
    
    # Build command
    cmd = ["clawhub", "publish", path]
    
    if slug:
        cmd.extend(["--slug", slug])
    
    if version:
        cmd.extend(["--version", version])
    
    if name:
        cmd.extend(["--name", name])
    
    if changelog:
        # Handle multiline changelog
        changelog_single_line = changelog.replace('\n', '\\n')
        cmd.extend(["--changelog", changelog_single_line])
    
    if tags:
        cmd.extend(["--tags", tags])
    
    if no_input:
        cmd.append("--no-input")
    
    print(f"Command: {' '.join(cmd)}")
    
    if dry_run:
        print("📋 Dry run - would execute above command")
        return True, "Dry run completed"
    
    # Execute
    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        elapsed = time.time() - start_time
        
        print(f"Time: {elapsed:.1f}s")
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        
        if result.returncode == 0:
            print("✅ Publication successful!")
            
            # Try to extract publication ID
            publication_id = None
            for line in result.stdout.split('\n'):
                if "Published" in line and "(" in line and ")" in line:
                    start = line.find("(") + 1
                    end = line.find(")")
                    if start < end:
                        publication_id = line[start:end]
                        break
            
            return True, publication_id
        else:
            print(f"❌ Publication failed")
            if result.stderr:
                print(f"Error:\n{result.stderr}")
            
            # Check for specific errors
            error_msg = result.stderr or result.stdout or "Unknown error"
            
            if "Version already exists" in error_msg:
                return False, "VERSION_EXISTS"
            elif "Unauthorized" in error_msg or "401" in error_msg:
                return False, "AUTH_ERROR"
            elif "Not found" in error_msg or "404" in error_msg:
                return False, "NOT_FOUND"
            elif "timeout" in error_msg.lower():
                return False, "TIMEOUT"
            else:
                return False, error_msg[:100]
                
    except subprocess.TimeoutExpired:
        print("❌ Publication timed out")
        return False, "TIMEOUT"
    except Exception as e:
        print(f"❌ Publication error: {e}")
        return False, str(e)

def verify_publication(slug, version, timeout=30):
    """Verify skill was published successfully."""
    print(f"\n🔍 Verifying publication...")
    
    try:
        result = subprocess.run(
            ["clawhub", "inspect", slug],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            # Check for version
            if version in output:
                print(f"✅ Version {version} found in skill info")
                
                # Check if it's the latest
                for line in output.split('\n'):
                    if "Latest:" in line:
                        latest = line.split("Latest:")[1].strip()
                        if latest == version:
                            print(f"✅ Version {version} is marked as latest")
                            return True
                        else:
                            print(f"⚠️  Latest is {latest}, not {version}")
                            return False
                
                return True
            else:
                print(f"❌ Version {version} not found in skill info")
                return False
        else:
            print(f"❌ Failed to inspect skill: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def handle_version_conflict(slug, version):
    """Handle version conflict by suggesting new version."""
    print(f"\n⚠️  Version conflict detected: {slug}@{version}")
    
    # Try to get current version
    try:
        result = subprocess.run(
            ["clawhub", "inspect", slug],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if "Latest:" in line:
                    latest = line.split("Latest:")[1].strip()
                    print(f"Current latest version: {latest}")
                    
                    # Suggest next version
                    try:
                        from semantic_version import Version
                        current = Version(latest)
                        
                        # Suggest patch bump
                        next_patch = Version(
                            major=current.major,
                            minor=current.minor,
                            patch=current.patch + 1
                        )
                        print(f"Suggested next version: {next_patch}")
                        return str(next_patch)
                    except:
                        # Simple increment
                        parts = latest.split('.')
                        if len(parts) == 3 and parts[2].isdigit():
                            new_patch = int(parts[2]) + 1
                            new_version = f"{parts[0]}.{parts[1]}.{new_patch}"
                            print(f"Suggested next version: {new_version}")
                            return new_version
    except:
        pass
    
    # Fallback
    new_version = version + ".1" if not version.endswith(".1") else version[:-1] + "2"
    print(f"Suggested next version: {new_version}")
    return new_version

def main():
    """Main function."""
    args = parse_args()
    
    print("=" * 60)
    print("ClawHub Skill Publisher")
    print("=" * 60)
    
    # Validate path
    if not os.path.exists(args.path):
        print(f"❌ Path does not exist: {args.path}")
        return 1
    
    if not os.path.isdir(args.path):
        print(f"❌ Not a directory: {args.path}")
        return 1
    
    # Get skill info
    skill_info = get_skill_info(args.path)
    if not skill_info:
        print("❌ Could not read skill information")
        return 1
    
    # Determine slug
    slug = args.slug or skill_info.get("name") or os.path.basename(args.path)
    slug = slug.lower().replace(' ', '-')
    
    # Determine version
    version = args.version or skill_info.get("version")
    if not version:
        print("❌ Version not specified and not found in SKILL.md")
        return 1
    
    # Determine name
    name = args.name or skill_info.get("name") or os.path.basename(args.path)
    
    # Generate changelog if not provided
    changelog = args.changelog or generate_changelog(args.path, version)
    
    # Check for existing version
    if check_existing_version(slug, version):
        if args.no_input:
            print(f"⚠️  Version {version} may already exist, but proceeding due to --no-input")
        else:
            response = input(f"Version {version} may already exist. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Publication cancelled")
                return 1
    
    # Show summary
    print(f"\n📋 Publication Summary:")
    print(f"  Skill: {slug}")
    print(f"  Version: {version}")
    print(f"  Name: {name}")
    print(f"  Path: {args.path}")
    print(f"  Tags: {args.tags}")
    print(f"  Changelog preview: {changelog[:100]}...")
    
    if not args.no_input and not args.dry_run:
        response = input("\nProceed with publication? (y/N): ")
        if response.lower() != 'y':
            print("Publication cancelled")
            return 0
    
    # Publish with retries
    success = False
    publication_id = None
    error_type = None
    
    for attempt in range(1, args.retry + 1):
        print(f"\nAttempt {attempt}/{args.retry}")
        
        success, result = publish_skill(
            args.path, slug, version, name, changelog, args.tags,
            args.no_input, args.dry_run
        )
        
        if success:
            publication_id = result
            break
        else:
            error_type = result
            
            # Handle specific errors
            if error_type == "VERSION_EXISTS":
                new_version = handle_version_conflict(slug, version)
                if args.no_input:
                    print(f"Auto-incrementing version to {new_version}")
                    version = new_version
                    continue
                else:
                    response = input(f"Use new version {new_version}? (y/N): ")
                    if response.lower() == 'y':
                        version = new_version
                        continue
                    else:
                        break
            
            elif error_type == "AUTH_ERROR":
                print("Authentication error. Please run: clawhub login")
                break
            
            elif attempt < args.retry:
                wait_time = attempt * 2  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached")
    
    # Verify if published
    if success and not args.dry_run:
        print(f"\n📦 Publication ID: {publication_id}")
        
        # Verify
        if verify_publication(slug, version):
            print(f"\n🎉 Successfully published {slug}@{version}")
            print(f"🔗 https://clawhub.ai/skills/{slug}")
        else:
            print(f"\n⚠️  Published but verification failed")
            print("Skill may still be processing. Check manually:")
            print(f"  clawhub inspect {slug}")
    
    elif args.dry_run:
        print("\n📋 Dry run completed")
        return 0
    
    else:
        print(f"\n❌ Publication failed")
        if error_type:
            print(f"Error: {error_type}")
        
        print("\nTroubleshooting tips:")
        print("1. Check authentication: clawhub whoami")
        print("2. Check skill format: python3 prepare_skill.py --path <path> --validate-only")
        print("3. Check network connectivity")
        print("4. Try manual publish: clawhub publish <path> --slug <slug> --version <version>")
        
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())