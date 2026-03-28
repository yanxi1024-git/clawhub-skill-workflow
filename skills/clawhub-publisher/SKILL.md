---
name: clawhub-publisher
version: 1.0.0
description: Publish and manage skills on ClawHub with best practices and automation. Use for skill publishing, version management, and ClawHub workflow automation.
license: MIT
metadata:
  openclaw:
    requires:
      bins:
        - node
        - npm
        - curl
    emoji: "🚀"
    homepage: https://github.com/yanxi1024-git/clawhub-publisher
---

# ClawHub Publisher Skill

Automate skill publishing to ClawHub with best practices, error handling, and version management.

## When to Use This Skill

Use this skill when you need to:
- Publish new skills to ClawHub
- Update existing skills with new versions
- Manage skill versions and tags
- Troubleshoot ClawHub publishing issues
- Automate skill release workflows
- Follow ClawHub best practices

## Quick Start

### 1. Check ClawHub Setup
```bash
# Check if clawhub CLI is installed
python3 check_clawhub_setup.py

# Or check manually
which clawhub || echo "clawhub not found"
clawhub whoami
```

### 2. Prepare Your Skill
```bash
# Use the preparation script
python3 prepare_skill.py --path /path/to/your/skill --version 1.0.0

# Or manually ensure:
# - SKILL.md has correct frontmatter
# - All files are text-based
# - Version is unique and follows semver
```

### 3. Publish to ClawHub
```bash
# Publish with best practices
python3 publish_skill.py --slug your-skill-name --version 1.0.0 --path /path/to/skill

# Or use the CLI directly
clawhub publish /path/to/skill --slug your-skill-name --version 1.0.0 --name "Display Name" --changelog "Initial release"
```

## Features

### 🛠 **Skill Preparation**
- Validates SKILL.md format and frontmatter
- Checks for text-only files
- Ensures version uniqueness
- Creates backup before publishing

### 🚀 **Smart Publishing**
- Automatic version conflict resolution
- Changelog generation
- Tag management
- Error handling and retries

### 🔍 **Validation & Testing**
- Pre-publish validation
- File format checking
- Size and limit verification
- Post-publish verification

### 📊 **Workflow Automation**
- Batch processing for multiple skills
- Version bump automation
- Release note generation
- Integration with CI/CD

## File Structure

```
clawhub-publisher/
├── SKILL.md                    # This file
├── check_clawhub_setup.py      # Check ClawHub environment
├── prepare_skill.py           # Prepare skill for publishing
├── publish_skill.py           # Publish skill to ClawHub
├── validate_skill.py          # Validate skill format
├── manage_versions.py         # Version management
├── troubleshoot.py            # Troubleshooting tools
├── examples/                  # Usage examples
│   ├── basic_publish.py
│   ├── batch_publish.py
│   └── ci_cd_integration.py
├── templates/                 # Skill templates
│   ├── basic_skill/
│   ├── python_skill/
│   └── advanced_skill/
└── docs/                      # Documentation
    ├── quickstart.md
    ├── best_practices.md
    └── troubleshooting.md
```

## Best Practices

### Before Publishing
1. **Test Locally**: Ensure your skill works in local environment
2. **Check Format**: Validate SKILL.md and all files
3. **Unique Version**: Check if version already exists on ClawHub
4. **Meaningful Changelog**: Document changes clearly

### During Publishing
1. **Use --no-input**: For automated workflows
2. **Handle Errors**: Implement retry logic for network issues
3. **Verify Upload**: Check file counts and sizes
4. **Monitor Progress**: Log each step for debugging

### After Publishing
1. **Verify Publication**: Use `clawhub inspect` to confirm
2. **Update Documentation**: Keep docs in sync with published version
3. **Share Announcement**: Notify users of new version
4. **Monitor Feedback**: Watch for issues and feedback

## Common Issues & Solutions

### "clawhub command not found"
```bash
# Solution 1: Use full path
/usr/local/lib/nodejs/node-v22.22.1-linux-arm64/bin/clawhub

# Solution 2: Add to PATH
export PATH="/usr/local/lib/nodejs/node-v22.22.1-linux-arm64/bin:$PATH"

# Solution 3: Install globally
npm install -g clawhub
```

### "Version already exists"
```bash
# Check existing versions
clawhub inspect <slug>

# Increment version (e.g., 1.0.0 → 1.0.1)
python3 manage_versions.py --increment patch --path /path/to/skill
```

### "Only text-based files are allowed"
```bash
# Remove binary files
find /path/to/skill -type f ! -name "*.py" ! -name "*.md" ! -name "*.json" ! -name "*.txt" ! -name "*.sh" ! -name "*.yaml" ! -name "*.yml" -delete

# Or use the preparation script
python3 prepare_skill.py --clean-binary --path /path/to/skill
```

## Advanced Usage

### Batch Publishing
```python
# Publish multiple skills
python3 batch_publish.py --config publish_config.json
```

### CI/CD Integration
```yaml
# GitHub Actions example
name: Publish to ClawHub
on:
  push:
    tags:
      - 'v*'
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Publish to ClawHub
        run: |
          pip install -r requirements.txt
          python3 publish_skill.py --slug ${{ github.event.repository.name }} --version ${GITHUB_REF#refs/tags/v}
```

### Version Management
```bash
# Auto-increment version based on changes
python3 manage_versions.py --analyze-changes --path /path/to/skill

# Generate changelog from git history
python3 manage_versions.py --generate-changelog --path /path/to/skill
```

## Requirements

### System Requirements
- Python 3.8+
- Node.js 18+ (for clawhub CLI)
- npm or bun (for clawhub installation)
- Git (for version management)

### Python Dependencies
- requests (for API calls)
- pyyaml (for YAML parsing)
- semantic-version (for version management)

### ClawHub Setup
1. Install clawhub CLI: `npm install -g clawhub`
2. Login: `clawhub login`
3. Verify: `clawhub whoami`

## Support & Resources

### Documentation
- [ClawHub API Docs](https://github.com/openclaw/clawhub/blob/main/docs/http-api.md)
- [Skill Format Docs](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md)
- [Best Practices Guide](docs/best_practices.md)

### Community
- [OpenClaw Discord](https://discord.com/invite/clawd)
- [GitHub Issues](https://github.com/yanxi1024-git/clawhub-publisher/issues)
- [ClawHub Skills](https://clawhub.ai/skills)

### Related Skills
- [papermc-ai-ops](https://clawhub.ai/skills/papermc-ai-ops) - PaperMC server management
- [skill-creator](https://clawhub.ai/skills/skill-creator) - Skill creation and optimization
- [github-publisher](https://clawhub.ai/skills/github-publisher) - GitHub repository management

## Changelog

### v1.0.0 (2026-03-28)
- Initial release based on PaperMC AI Operations publishing experience
- Includes skill preparation, publishing, and validation tools
- Best practices and troubleshooting guides
- Templates and examples for common use cases

## License
MIT License - see LICENSE file for details.

---

**Tip**: Always test publishing with a test skill first before publishing important skills!
