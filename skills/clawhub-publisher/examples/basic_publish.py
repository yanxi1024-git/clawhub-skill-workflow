#!/usr/bin/env python3
"""
Basic example of publishing a skill to ClawHub.
"""

import os
import sys
import tempfile
import shutil

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_sample_skill():
    """Create a sample skill for testing."""
    temp_dir = tempfile.mkdtemp(prefix="sample_skill_")
    print(f"Created sample skill at: {temp_dir}")
    
    # Create SKILL.md
    skill_md = """---
name: sample-skill
version: 1.0.0
description: A sample skill for testing ClawHub publishing.
license: MIT
metadata:
  openclaw:
    requires:
      bins:
        - python3
    emoji: "🧪"
---

# Sample Skill

This is a sample skill for testing ClawHub publishing workflows.

## Features

- Sample feature 1
- Sample feature 2
- Sample feature 3

## Usage

```bash
python3 sample_script.py
```

## License

MIT License
"""
    
    with open(os.path.join(temp_dir, "SKILL.md"), "w") as f:
        f.write(skill_md)
    
    # Create a sample Python script
    sample_script = """#!/usr/bin/env python3
"""
Sample script for the sample skill.

This demonstrates a simple skill structure.
"""

def main():
    print("Hello from sample skill!")
    print("This skill was published using ClawHub Publisher.")
    return 0

if __name__ == "__main__":
    main()
"""
    
    with open(os.path.join(temp_dir, "sample_script.py"), "w") as f:
        f.write(sample_script)
    
    # Create a README
    readme = """# Sample Skill

This is a sample skill created for testing ClawHub publishing.
"""
    
    with open(os.path.join(temp_dir, "README.md"), "w") as f:
        f.write(readme)
    
    return temp_dir

def main():
    """Main function."""
    print("=" * 60)
    print("Basic Publishing Example")
    print("=" * 60)
    
    # Create sample skill
    skill_dir = create_sample_skill()
    
    try:
        # Import our modules
        from prepare_skill import main as prepare_main
        from publish_skill import main as publish_main
        
        print(f"\n1. Preparing skill at: {skill_dir}")
        
        # Prepare the skill
        import argparse
        
        # Mock args for preparation
        class Args:
            def __init__(self):
                self.path = skill_dir
                self.version = "1.0.0"
                self.clean_binary = True
                self.backup = True
                self.validate_only = False
                self.output = None
                self.name = None
                self.description = None
        
        args = Args()
        
        # We can't directly call main due to argparse, but we can show the commands
        print("\nRecommended commands:")
        print(f"  python3 prepare_skill.py --path {skill_dir} --clean-binary --backup")
        print(f"  python3 publish_skill.py --path {skill_dir} --slug sample-skill --version 1.0.0")
        
        print("\n2. Skill structure:")
        for root, dirs, files in os.walk(skill_dir):
            level = root.replace(skill_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f'{subindent}{file}')
        
        print("\n3. Next steps:")
        print("   - Run the preparation command above")
        print("   - Run the publishing command above")
        print("   - Check publication: clawhub inspect sample-skill")
        
        print(f"\nSkill directory: {skill_dir}")
        print("\nNote: This is a demonstration. To actually publish, run the commands above.")
        
    finally:
        # Cleanup
        response = input(f"\nDelete sample skill directory? ({skill_dir}) (y/N): ")
        if response.lower() == 'y':
            shutil.rmtree(skill_dir)
            print("Sample skill deleted.")
        else:
            print(f"Sample skill kept at: {skill_dir}")

if __name__ == "__main__":
    main()