# Quick Start Guide

Get started with ClawHub Publisher in 5 minutes.

## Prerequisites

### 1. Install Python 3.8+
```bash
# Check Python version
python3 --version

# Install if needed (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Install Node.js 18+
```bash
# Check Node.js version
node --version
npm --version

# Install if needed (using nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### 3. Install ClawHub CLI
```bash
npm install -g clawhub

# Verify installation
clawhub --cli-version
```

### 4. Login to ClawHub
```bash
# This will open a browser for authentication
clawhub login

# Or use a token
clawhub login --token your_token_here

# Verify login
clawhub whoami
```

## Installation

### Option 1: Install as a Skill
```bash
# Install from ClawHub (once published)
clawhub install clawhub-publisher
```

### Option 2: Clone from GitHub
```bash
# Clone the repository
git clone https://github.com/yanxi1024-git/clawhub-publisher.git
cd clawhub-publisher

# Install Python dependencies
pip install -r requirements.txt
```

### Option 3: Use Directly
```bash
# Just download the scripts
curl -O https://raw.githubusercontent.com/yanxi1024-git/clawhub-publisher/main/check_clawhub_setup.py
curl -O https://raw.githubusercontent.com/yanxi1024-git/clawhub-publisher/main/prepare_skill.py
curl -O https://raw.githubusercontent.com/yanxi1024-git/clawhub-publisher/main/publish_skill.py
```

## Your First Publication

### Step 1: Check Your Setup
```bash
python3 check_clawhub_setup.py
```

You should see:
```
✅ All checks passed! You're ready to publish to ClawHub.
```

### Step 2: Prepare Your Skill
```bash
# Navigate to your skill directory
cd /path/to/your-skill

# Prepare for publishing
python3 /path/to/clawhub-publisher/prepare_skill.py --path . --version 1.0.0
```

This will:
- Validate your SKILL.md format
- Check for non-text files
- Verify file sizes
- Create a backup

### Step 3: Publish Your Skill
```bash
python3 /path/to/clawhub-publisher/publish_skill.py \
  --path . \
  --slug your-skill-name \
  --version 1.0.0 \
  --name "Your Skill Display Name" \
  --changelog "Initial release with basic features"
```

### Step 4: Verify Publication
```bash
# Check your skill on ClawHub
clawhub inspect your-skill-name

# Visit in browser
open https://clawhub.ai/skills/your-skill-name
```

## Common Workflows

### Update an Existing Skill
```bash
# 1. Check current version
clawhub inspect your-skill-name

# 2. Prepare with new version
python3 prepare_skill.py --path . --version 1.1.0

# 3. Publish update
python3 publish_skill.py --path . --version 1.1.0 --changelog "Added new feature X"
```

### Publish Multiple Skills
```bash
# Create a batch script
cat > publish_all.sh << 'EOF'
#!/bin/bash
SKILLS=("skill1" "skill2" "skill3")

for skill in "${SKILLS[@]}"; do
  echo "Publishing $skill..."
  python3 publish_skill.py --path "./$skill" --no-input
  echo ""
done
EOF

chmod +x publish_all.sh
./publish_all.sh
```

### Automated Publishing (CI/CD)
```bash
# GitHub Actions workflow example
# See examples/ci_cd_integration.py
```

## Troubleshooting

### "clawhub command not found"
```bash
# Find where it's installed
find /usr -name "clawhub" 2>/dev/null

# Use full path
/usr/local/bin/clawhub --version

# Or reinstall
npm install -g clawhub
```

### "Version already exists"
```bash
# Check existing versions
clawhub inspect your-skill-name

# Use next version
python3 publish_skill.py --path . --version 1.0.1
```

### Authentication Errors
```bash
# Re-login
clawhub logout
clawhub login

# Check token
cat ~/.config/clawhub/config.json
```

## Next Steps

### 1. Explore Examples
```bash
cd examples
python3 basic_publish.py
```

### 2. Read Best Practices
See [best_practices.md](best_practices.md) for detailed guidelines.

### 3. Join the Community
- [OpenClaw Discord](https://discord.com/invite/clawd)
- [GitHub Discussions](https://github.com/yanxi1024-git/clawhub-publisher/discussions)

### 4. Contribute
Found a bug or have a feature request? Open an issue on GitHub!

## Need Help?

1. Check the [troubleshooting guide](troubleshooting.md)
2. Search existing issues on GitHub
3. Ask in the OpenClaw Discord community
4. Open a new issue with details about your problem

---

**Congratulations!** You've successfully published your first skill to ClawHub. 🎉