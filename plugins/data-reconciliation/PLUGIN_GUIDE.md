# Claude Code Plugin Publishing Guide

This guide explains how to publish your data-reconciliation skill as a Claude Code managed plugin.

## Understanding Claude Code Plugins

### Local Skills vs Managed Plugins

**Local Skills** (what you have now):
- Stored in `.claude/skills/your-skill/`
- Only available in your workspace
- Manual installation required
- Good for personal/private skills

**Managed Plugins** (what you want):
- Published to Claude Code plugin registry
- Installable via `/install-plugin` command
- Available to all Claude Code users
- Automatic updates
- Versioning support

## Prerequisites

Before publishing as a plugin:

1. ✅ Skill structure is correct (you have this)
2. ✅ `SKILL.md` exists and is well-documented
3. ✅ `plugin.json` with metadata (just created)
4. ✅ `README.md` for documentation
5. ✅ `requirements.txt` for dependencies
6. ⬜ GitHub repository (recommended)
7. ⬜ Testing completed
8. ⬜ Examples provided

## Step-by-Step Publishing Process

### Step 1: Prepare Your Plugin Structure

Ensure your structure looks like this:

```
data-reconciliation/
├── SKILL.md              ✅ Main skill definition
├── plugin.json           ✅ Plugin metadata
├── README.md             ✅ Documentation
├── requirements.txt      ✅ Dependencies
├── LICENSE               ⬜ License file (create)
├── CHANGELOG.md          ⬜ Version history (create)
├── scripts/              ✅ Python modules
│   ├── __init__.py       ⬜ Make it a package
│   ├── data_loader.py
│   ├── data_profiler.py
│   ├── reconcile_engine.py
│   ├── gemini_analyzer.py
│   ├── visualizer.py
│   └── reconcile_cli.py
├── references/           ✅ Reference docs
│   ├── reconciliation_strategies.md
│   └── data_type_patterns.md
├── examples/             ⬜ Example scripts
│   ├── simple_reconciliation.py
│   ├── database_to_api.py
│   └── sample_data/
├── tests/                ⬜ Unit tests
│   └── test_reconciliation.py
└── .claudeignore         ⬜ Files to exclude
```

### Step 2: Create Missing Files

#### Create LICENSE
```bash
# MIT License (recommended)
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

#### Create .claudeignore
```bash
cat > .claudeignore << 'EOF'
# Exclude from plugin package
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
.env
.venv/
venv/
*.log
.DS_Store
Thumbs.db
EOF
```

#### Create CHANGELOG.md
```bash
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2024-11-09

### Added
- Intelligent data profiler with automatic strategy detection
- Comprehensive visualization module with charts and dashboards
- CLI interface for standalone usage
- Enhanced error handling and logging throughout
- Progress tracking for large dataset reconciliation
- Excel export with formatted multi-sheet reports
- Data quality scoring and proactive issue detection
- Automatic key column detection
- Transformation recommendations
- Confidence scoring for strategies

### Enhanced
- Reconciliation engine with validation and better error messages
- Data loader with auto-detection capabilities
- Gemini analyzer with improved JSON parsing

### Fixed
- Column validation edge cases
- Progress bar display issues
- Excel export formatting

## [1.0.0] - 2024-10-30

### Initial Release
- Core reconciliation engine
- Multi-source data loading (CSV, Excel, DB, API)
- Gemini AI integration for intelligent analysis
- Basic export functionality
- Reference documentation
EOF
```

### Step 3: Create __init__.py Files

```bash
# Make scripts a proper Python package
cat > scripts/__init__.py << 'EOF'
"""
Data Reconciliation Skill - Python Package
"""

from .data_loader import DataLoader, DataTransformer
from .data_profiler import IntelligentDataProfiler, DatasetProfile, ColumnProfile
from .reconcile_engine import ReconciliationEngine, ReconciliationConfig, ReconciliationResult
from .gemini_analyzer import GeminiReconciliationAnalyzer
from .visualizer import ReconciliationVisualizer

__version__ = "2.0.0"
__all__ = [
    "DataLoader",
    "DataTransformer",
    "IntelligentDataProfiler",
    "DatasetProfile",
    "ColumnProfile",
    "ReconciliationEngine",
    "ReconciliationConfig",
    "ReconciliationResult",
    "GeminiReconciliationAnalyzer",
    "ReconciliationVisualizer",
]
EOF
```

### Step 4: Validate plugin.json

Your `plugin.json` should have:

- ✅ `name`: Unique plugin identifier
- ✅ `version`: Semantic versioning (2.0.0)
- ✅ `description`: Clear, concise description
- ✅ `author`: Your name/organization
- ✅ `license`: License type (MIT)
- ✅ `type`: "skill-plugin"
- ✅ `entryPoint`: "SKILL.md"
- ✅ `dependencies`: Python version and packages
- ✅ `tags`: Searchable keywords
- ✅ `repository`: GitHub URL (if public)

### Step 5: Test Your Plugin Locally

Before publishing, test thoroughly:

```bash
# 1. Test CLI
python scripts/reconcile_cli.py version
python scripts/reconcile_cli.py profile examples/sample_data/test.csv

# 2. Test programmatically
python -c "from scripts import ReconciliationEngine; print('Import successful')"

# 3. Test with Claude Code
# In Claude Code chat:
/skill data-reconciliation
```

### Step 6: Create a GitHub Repository (Recommended)

```bash
# Initialize git
cd .claude/skills/data-reconciliation
git init

# Add files
git add .
git commit -m "Initial commit - Data Reconciliation Skill v2.0.0"

# Create repository on GitHub, then:
git remote add origin https://github.com/yourusername/data-reconciliation-skill.git
git push -u origin main

# Create a release
git tag -a v2.0.0 -m "Version 2.0.0 - Intelligent reconciliation with auto-strategy"
git push origin v2.0.0
```

### Step 7: Publish to Claude Code Plugin Registry

There are two ways to publish:

#### Option A: Official Claude Code Registry (Recommended)

1. **Submit to Anthropic**:
   ```bash
   # Use Claude Code CLI
   claude-code publish-plugin data-reconciliation
   ```

2. **Fill out plugin submission form**:
   - Go to: https://claude.com/plugins/submit
   - Provide repository URL
   - Include plugin.json details
   - Submit for review

3. **Wait for approval**:
   - Anthropic team reviews
   - Typically 3-5 business days
   - May request changes

4. **Once approved**:
   - Plugin appears in registry
   - Users can install via: `/install-plugin data-reconciliation`

#### Option B: Private Distribution

If not publishing publicly:

```bash
# Share as a .claude-plugin file
cd .claude/skills
tar -czf data-reconciliation-2.0.0.claude-plugin data-reconciliation/

# Users can install via:
/install-plugin-from-file data-reconciliation-2.0.0.claude-plugin
```

### Step 8: Maintain Your Plugin

After publishing:

1. **Monitor issues**: Respond to user issues on GitHub
2. **Release updates**: Use semantic versioning
3. **Document changes**: Update CHANGELOG.md
4. **Test thoroughly**: Before each release

```bash
# For updates:
# 1. Make changes
# 2. Update version in plugin.json
# 3. Update CHANGELOG.md
# 4. Commit and tag
git tag v2.1.0
git push origin v2.1.0

# 5. Republish
claude-code update-plugin data-reconciliation
```

## Alternative: Using NPM-Style Plugin Package

Some Claude Code plugins use an npm-style approach:

### Create package.json (alternative to plugin.json)

```json
{
  "name": "@your-org/data-reconciliation-skill",
  "version": "2.0.0",
  "description": "Intelligent data reconciliation for Claude Code",
  "main": "SKILL.md",
  "type": "claude-skill",
  "keywords": ["reconciliation", "data-quality", "claude-code"],
  "author": "Your Name",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/your-org/data-reconciliation-skill"
  },
  "claude": {
    "skillType": "plugin",
    "entryPoint": "SKILL.md",
    "pythonDependencies": "requirements.txt"
  }
}
```

Then publish via npm:
```bash
npm publish --access public
```

Users install via:
```bash
/install-plugin @your-org/data-reconciliation-skill
```

## Verification Checklist

Before submitting for publication:

- [ ] All scripts run without errors
- [ ] requirements.txt is complete and tested
- [ ] SKILL.md is comprehensive and clear
- [ ] plugin.json has all required fields
- [ ] README.md provides clear usage examples
- [ ] LICENSE file exists
- [ ] CHANGELOG.md documents all versions
- [ ] Examples are included and work
- [ ] Tests pass (if included)
- [ ] Repository is public (if using GitHub)
- [ ] No sensitive data or API keys in code
- [ ] .claudeignore excludes unnecessary files

## Best Practices

1. **Versioning**: Follow semantic versioning (MAJOR.MINOR.PATCH)
2. **Documentation**: Keep README and SKILL.md in sync
3. **Dependencies**: Pin major versions, allow minor updates
4. **Testing**: Include tests for critical functionality
5. **Examples**: Provide working examples
6. **Changelog**: Document all changes
7. **Support**: Respond to issues promptly

## Getting Help

- Claude Code Plugin Documentation: https://docs.claude.com/plugins
- Plugin Registry: https://claude.com/plugins
- Community Discord: https://discord.gg/claude-code
- GitHub Discussions: https://github.com/anthropics/claude-code/discussions

## Example Installation Commands for Users

Once published, users can install your plugin:

```bash
# Official registry
/install-plugin data-reconciliation

# With organization prefix
/install-plugin @your-org/data-reconciliation-skill

# From GitHub directly
/install-plugin github:yourusername/data-reconciliation-skill

# From local file
/install-plugin-from-file data-reconciliation.claude-plugin
```

## Summary

Your skill is now ready to be published! The key files are:

1. ✅ `plugin.json` - Plugin metadata
2. ✅ `SKILL.md` - Skill definition
3. ✅ `README.md` - User documentation
4. ✅ `requirements.txt` - Dependencies
5. ⬜ `LICENSE` - Legal terms
6. ⬜ `CHANGELOG.md` - Version history
7. ⬜ Scripts as Python package

Follow the steps above to publish to the Claude Code plugin registry!
