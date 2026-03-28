#!/usr/bin/env python3
"""
Check ClawHub setup and configuration.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_clawhub_cli():
    """Check if clawhub CLI is installed and accessible."""
    print("🔍 Checking ClawHub CLI...")
    
    # Try different ways to find clawhub
    clawhub_paths = [
        "/usr/local/bin/clawhub",
        "/usr/bin/clawhub",
        os.path.expanduser("~/.local/bin/clawhub"),
        "/usr/local/lib/nodejs/node-v22.22.1-linux-arm64/bin/clawhub"
    ]
    
    found = False
    for path in clawhub_paths:
        if os.path.exists(path):
            print(f"  ✅ Found at: {path}")
            found = True
            break
    
    if not found:
        # Try which command
        try:
            result = subprocess.run(["which", "clawhub"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ Found via which: {result.stdout.strip()}")
                found = True
        except:
            pass
    
    if not found:
        print("  ❌ ClawHub CLI not found")
        return False
    
    # Check version
    try:
        result = subprocess.run(["clawhub", "-V"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Version: {result.stdout.strip()}")
        else:
            # Try alternative command
            result = subprocess.run(["clawhub", "--cli-version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ Version: {result.stdout.strip()}")
    except Exception as e:
        print(f"  ⚠️  Could not get version: {e}")
    
    return True

def check_clawhub_config():
    """Check ClawHub configuration."""
    print("\n🔍 Checking ClawHub configuration...")
    
    config_paths = [
        os.path.expanduser("~/.config/clawhub/config.json"),
        os.path.expanduser("~/Library/Application Support/clawhub/config.json"),
    ]
    
    config_found = False
    for config_path in config_paths:
        if os.path.exists(config_path):
            print(f"  ✅ Config found: {config_path}")
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                if 'token' in config:
                    token_preview = config['token'][:10] + "..." if len(config['token']) > 10 else config['token']
                    print(f"  ✅ Token: {token_preview}")
                
                if 'registry' in config:
                    print(f"  ✅ Registry: {config['registry']}")
                
                config_found = True
                break
            except Exception as e:
                print(f"  ❌ Error reading config: {e}")
    
    if not config_found:
        print("  ❌ No ClawHub config found")
        return False
    
    return True

def check_authentication():
    """Check if authenticated with ClawHub."""
    print("\n🔍 Checking authentication...")
    
    try:
        result = subprocess.run(["clawhub", "whoami"], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if "yanxi1024-git" in output or "Checking token" in output:
                print("  ✅ Authenticated")
                # Extract username if possible
                lines = output.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('-') and 'Checking' not in line:
                        print(f"  ✅ User: {line.strip()}")
                        break
                return True
            else:
                print(f"  ⚠️  Unexpected output: {output}")
        else:
            print(f"  ❌ Authentication failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("  ❌ Authentication check timed out")
    except Exception as e:
        print(f"  ❌ Error checking authentication: {e}")
    
    return False

def check_node_installation():
    """Check Node.js installation."""
    print("\n🔍 Checking Node.js...")
    
    try:
        # Check node
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Node.js: {result.stdout.strip()}")
        else:
            print("  ❌ Node.js not found")
            return False
        
        # Check npm
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ npm: {result.stdout.strip()}")
        else:
            print("  ⚠️  npm not found")
        
        return True
    except Exception as e:
        print(f"  ❌ Error checking Node.js: {e}")
        return False

def check_python_dependencies():
    """Check Python dependencies."""
    print("\n🔍 Checking Python dependencies...")
    
    dependencies = ['requests', 'pyyaml']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} (missing)")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  Missing dependencies. Install with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def check_network_connectivity():
    """Check network connectivity to ClawHub."""
    print("\n🔍 Checking network connectivity...")
    
    import requests
    
    try:
        response = requests.get("https://clawhub.ai", timeout=5)
        if response.status_code == 200:
            print("  ✅ ClawHub website accessible")
        else:
            print(f"  ⚠️  ClawHub website returned status: {response.status_code}")
        
        # Try API endpoint
        response = requests.get("https://clawhub.ai/api/v1", timeout=5)
        if response.status_code == 404:  # Expected for root API
            print("  ✅ ClawHub API accessible")
        else:
            print(f"  ⚠️  ClawHub API returned status: {response.status_code}")
        
        return True
    except requests.exceptions.Timeout:
        print("  ❌ Network timeout")
    except requests.exceptions.ConnectionError:
        print("  ❌ Network connection error")
    except Exception as e:
        print(f"  ❌ Network check error: {e}")
    
    return False

def main():
    """Main function."""
    print("=" * 60)
    print("ClawHub Setup Check")
    print("=" * 60)
    
    checks = [
        ("ClawHub CLI", check_clawhub_cli),
        ("ClawHub Config", check_clawhub_config),
        ("Authentication", check_authentication),
        ("Node.js", check_node_installation),
        ("Python Dependencies", check_python_dependencies),
        ("Network Connectivity", check_network_connectivity),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"  ❌ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for check_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 All checks passed! You're ready to publish to ClawHub.")
        print("\nNext steps:")
        print("1. Prepare your skill: python3 prepare_skill.py --path /path/to/skill")
        print("2. Publish: python3 publish_skill.py --slug your-skill --path /path/to/skill")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Install clawhub: npm install -g clawhub")
        print("2. Login: clawhub login")
        print("3. Check network connectivity")
        print("4. Install missing Python dependencies")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())