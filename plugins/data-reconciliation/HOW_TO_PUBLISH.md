# How to Publish Data Reconciliation as a Claude Code Plugin

## Quick Start: Create Your Plugin Marketplace

### Step 1: Create Marketplace Repository

```bash
# Create a new directory for your marketplace
mkdir finsight-claude-plugins
cd finsight-claude-plugins

# Create the required structure
mkdir -p .claude-plugin
mkdir -p plugins
```

### Step 2: Create Marketplace Configuration

Create `.claude-plugin/marketplace.json`:

```json
{
  "name": "finsight-plugins",
  "owner": {
    "name": "Finsight Analytics LLP",
    "email": "contact@finsightanalytics.com"
  },
  "description": "Professional data analytics and reconciliation plugins for Claude Code",
  "plugins": [
    {
      "name": "data-reconciliation",
      "source": "./plugins/data-reconciliation",
      "description": "Intelligent data reconciliation toolkit with AI-powered strategy recommendations. Automatically analyzes datasets, detects data quality issues, and suggests optimal reconciliation approaches.",
      "version": "2.0.0",
      "type": "skill",
      "tags": ["data", "reconciliation", "analytics", "ai", "data-quality"],
      "author": "Finsight Analytics LLP",
      "license": "MIT"
    }
  ]
}
```

### Step 3: Copy Your Skill to the Marketplace

```bash
# From the marketplace root
cp -r "C:/Users/konne/OneDrive - Finsight Analytics LLP (1)/claudecodeproj/genericchat/.claude/skills/data-reconciliation" ./plugins/
```

Or on Windows PowerShell:
```powershell
Copy-Item -Path ".claude\skills\data-reconciliation" -Destination ".\plugins\data-reconciliation" -Recurse
```

### Step 4: Add README.md for Your Marketplace

Create `README.md` in the marketplace root:

```markdown
# Finsight Claude Code Plugins

Professional data analytics plugins for Claude Code by Finsight Analytics LLP.

## Available Plugins

### 🔄 Data Reconciliation (v2.0.0)

Intelligent data reconciliation toolkit with:
- AI-powered strategy detection
- Automatic key column detection
- Data quality profiling
- Interactive visualizations
- Multi-source support (CSV, Excel, databases, APIs)

**Installation:**

\```bash
# Add this marketplace
/plugin marketplace add YOUR-GITHUB-USERNAME/finsight-claude-plugins

# Install the plugin
/plugin install data-reconciliation@finsight-plugins
\```

**Usage:**

\```
/skill data-reconciliation
\```

Then tell Claude what you need to reconcile!

## Support

For issues or questions, visit: https://github.com/YOUR-USERNAME/finsight-claude-plugins/issues
```

### Step 5: Initialize Git and Push to GitHub

```bash
# Initialize git
git init

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.DS_Store
.env
EOF

# Add and commit
git add .
git commit -m "Initial commit - Data Reconciliation Plugin v2.0.0"

# Create repository on GitHub (do this via GitHub web interface)
# Then connect and push:
git remote add origin https://github.com/YOUR-USERNAME/finsight-claude-plugins.git
git branch -M main
git push -u origin main
```

### Step 6: Create a Release (Optional but Recommended)

```bash
# Tag your version
git tag -a v2.0.0 -m "Data Reconciliation Plugin v2.0.0"
git push origin v2.0.0

# On GitHub, create a Release from this tag with release notes
```

## How Users Install Your Plugin

### Method 1: Via GitHub (Public Repository)

```bash
# In Claude Code terminal:
/plugin marketplace add YOUR-USERNAME/finsight-claude-plugins

# Then browse and install:
/plugin
# Navigate to: Browse and install plugins
# Select: finsight-plugins
# Install: data-reconciliation
```

### Method 2: Via Local Path (Testing)

```bash
# For local testing before publishing:
/plugin marketplace add /path/to/finsight-claude-plugins

# Then install as normal
/plugin install data-reconciliation@finsight-plugins
```

### Method 3: Via Full Git URL (Private Repositories)

```bash
# For private repos or custom git servers:
/plugin marketplace add https://github.com/YOUR-USERNAME/finsight-claude-plugins.git

# Or with authentication:
/plugin marketplace add https://token@github.com/YOUR-USERNAME/finsight-claude-plugins.git
```

## Testing Your Plugin Locally First

Before publishing, test locally:

```bash
# 1. Create a test marketplace locally
cd ~/test-marketplace
mkdir -p .claude-plugin plugins
# Copy your .claude-plugin/marketplace.json
# Copy your skill to plugins/

# 2. Add the local marketplace
/plugin marketplace add ~/test-marketplace

# 3. Install and test
/plugin install data-reconciliation@test-marketplace

# 4. Test the skill
/skill data-reconciliation

# 5. If issues, uninstall and fix
/plugin uninstall data-reconciliation@test-marketplace
# Make changes, then reinstall
```

## Alternative: Submit to Official Anthropic Skills

If you want your skill in the official repository:

1. **Fork**: https://github.com/anthropics/skills

2. **Add your skill**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/skills.git
   cd skills
   cp -r /path/to/data-reconciliation ./data-reconciliation
   ```

3. **Follow their contribution guidelines**:
   - Ensure SKILL.md follows their format
   - Add examples
   - Test thoroughly
   - Create PR with description

4. **Users will install with**:
   ```bash
   /plugin marketplace add anthropics/skills
   /plugin install data-reconciliation@anthropic-agent-skills
   ```

## Directory Structure After Publishing

Your marketplace will look like:

```
finsight-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── data-reconciliation/
│       ├── SKILL.md
│       ├── plugin.json
│       ├── README.md
│       ├── requirements.txt
│       ├── LICENSE
│       ├── CHANGELOG.md
│       ├── scripts/
│       │   ├── __init__.py
│       │   ├── data_loader.py
│       │   ├── data_profiler.py
│       │   ├── reconcile_engine.py
│       │   ├── gemini_analyzer.py
│       │   ├── visualizer.py
│       │   └── reconcile_cli.py
│       └── references/
│           ├── reconciliation_strategies.md
│           └── data_type_patterns.md
├── README.md
├── LICENSE
└── .gitignore
```

## Maintenance & Updates

When you update your plugin:

```bash
# 1. Update version in .claude-plugin/marketplace.json
# 2. Update CHANGELOG.md in your plugin
# 3. Commit and tag
git add .
git commit -m "Update data-reconciliation to v2.1.0"
git tag v2.1.0
git push origin main --tags

# Users update with:
/plugin update data-reconciliation@finsight-plugins
```

## Best Practices

1. **Versioning**: Use semantic versioning (MAJOR.MINOR.PATCH)
2. **Documentation**: Keep README and SKILL.md clear and updated
3. **Testing**: Test locally before pushing to GitHub
4. **Changelog**: Document all changes in CHANGELOG.md
5. **License**: Include LICENSE file (MIT recommended)
6. **Examples**: Provide working examples in your documentation
7. **Support**: Respond to issues on GitHub promptly

## Getting Help

- Claude Code Docs: https://code.claude.com/docs
- Plugin Marketplaces: https://code.claude.com/docs/en/plugin-marketplaces
- Skills Documentation: https://code.claude.com/docs/en/skills
- Community: GitHub Discussions on anthropics/skills

---

**Ready to publish?** Follow the steps above and your plugin will be available to the Claude Code community!
