# ClawHub Publisher Skill

Automate skill publishing to ClawHub with best practices and error handling.

## Features

- 🛠 **Skill Preparation**: Validate and prepare skills for publishing
- 🚀 **Smart Publishing**: Handle version conflicts and retries
- 🔍 **Validation**: Pre-publish checks and post-publish verification
- 📊 **Workflow Automation**: Batch processing and CI/CD integration

## Quick Start

### 1. Check Setup
```bash
python3 check_clawhub_setup.py
```

### 2. Prepare Skill
```bash
python3 prepare_skill.py --path /path/to/your/skill --version 1.0.0
```

### 3. Publish Skill
```bash
python3 publish_skill.py --path /path/to/your/skill --slug your-skill --version 1.0.0
```

## Installation

### Prerequisites
- Python 3.8+
- Node.js 18+ (for clawhub CLI)
- ClawHub account

### Install Dependencies
```bash
pip install requests pyyaml semantic-version
npm install -g clawhub
clawhub login
```

## Usage Examples

### Basic Publishing
```bash
# Prepare and publish in one go
python3 prepare_skill.py --path my-skill --clean-binary --backup
python3 publish_skill.py --path my-skill --no-input
```

### Advanced Usage
```bash
# Custom version and changelog
python3 publish_skill.py \
  --path my-skill \
  --slug custom-name \
  --version 2.1.0 \
  --changelog "Added new features and bug fixes" \
  --tags "latest,production,featured"

# Dry run (test without publishing)
python3 publish_skill.py --path my-skill --dry-run

# With retries
python3 publish_skill.py --path my-skill --retry 5 --timeout 120
```

## File Structure

```
clawhub-publisher/
├── SKILL.md                    # Skill definition
├── check_clawhub_setup.py      # Environment validation
├── prepare_skill.py           # Skill preparation
├── publish_skill.py           # Skill publishing
├── validate_skill.py          # Format validation
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
1. **Test Locally**: Ensure your skill works
2. **Validate Format**: Run preparation checks
3. **Check Version**: Ensure unique version number
4. **Write Changelog**: Document changes clearly

### During Publishing
1. **Use --no-input**: For automated workflows
2. **Handle Errors**: Implement retry logic
3. **Monitor Progress**: Log each step
4. **Verify Upload**: Check file counts

### After Publishing
1. **Verify Publication**: Confirm skill is live
2. **Update Documentation**: Keep docs in sync
3. **Share Announcement**: Notify users
4. **Monitor Feedback**: Watch for issues

## Common Issues & Solutions

### "clawhub command not found"
```bash
# Use full path
/usr/local/lib/nodejs/node-v22.22.1-linux-arm64/bin/clawhub

# Or add to PATH
export PATH="/usr/local/lib/nodejs/node-v22.22.1-linux-arm64/bin:$PATH"
```

### "Version already exists"
```bash
# Check existing versions
clawhub inspect <slug>

# Use next version
python3 publish_skill.py --path <path> --version 1.0.1
```

### "Only text-based files are allowed"
```bash
# Clean binary files
python3 prepare_skill.py --path <path> --clean-binary
```

## CI/CD Integration

### GitHub Actions Example
```yaml
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
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          pip install requests pyyaml semantic-version
          npm install -g clawhub
      - name: Login to ClawHub
        run: clawhub login --token ${{ secrets.CLAWHUB_TOKEN }}
      - name: Publish skill
        run: |
          python3 publish_skill.py \
            --path . \
            --slug ${{ github.event.repository.name }} \
            --version ${GITHUB_REF#refs/tags/v} \
            --no-input
```

## Support

### Documentation
- [ClawHub API Docs](https://github.com/openclaw/clawhub/blob/main/docs/http-api.md)
- [Skill Format Docs](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md)

### Community
- [OpenClaw Discord](https://discord.com/invite/clawd)
- [GitHub Issues](https://github.com/yanxi1024-git/clawhub-publisher/issues)

### Related Skills
- [papermc-ai-ops](https://clawhub.ai/skills/papermc-ai-ops) - PaperMC server management
- [skill-creator](https://clawhub.ai/skills/skill-creator) - Skill creation and optimization

## License

MIT License - see [LICENSE](LICENSE) file for details.
