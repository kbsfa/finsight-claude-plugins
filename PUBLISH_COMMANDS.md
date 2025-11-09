# Quick Publish Commands

Copy and paste these commands in order:

## Step 1: Navigate to Directory
```bash
cd "C:\Users\konne\OneDrive - Finsight Analytics LLP (1)\claudecodeproj\genericchat\finsight-claude-plugins"
```

## Step 2: Initialize Git
```bash
git init
```

## Step 3: Create .gitignore
```bash
echo __pycache__/ > .gitignore
echo *.pyc >> .gitignore
echo *.pyo >> .gitignore
echo .DS_Store >> .gitignore
echo .env >> .gitignore
echo *.log >> .gitignore
```

## Step 4: Add and Commit
```bash
git add .
git commit -m "Initial commit - Data Reconciliation Plugin v2.0.0"
```

## Step 5: Create GitHub Repository

**DO THIS MANUALLY:**
1. Go to: https://github.com/new
2. Repository name: `finsight-claude-plugins`
3. Description: `Professional data analytics plugins for Claude Code`
4. Make it **Public**
5. **Don't** check "Add a README file"
6. **Don't** check "Add .gitignore"
7. License: MIT
8. Click **"Create repository"**

## Step 6: Connect to GitHub and Push
```bash
git remote add origin https://github.com/kbsfa/finsight-claude-plugins.git
git branch -M main
git push -u origin main
```

## Step 7: Create Version Tag
```bash
git tag -a v2.0.0 -m "Data Reconciliation Plugin v2.0.0"
git push origin v2.0.0
```

## Step 8: Test Installation (In Claude Code)
```bash
/plugin marketplace add kbsfa/finsight-claude-plugins
/plugin install data-reconciliation@finsight-plugins
/skill data-reconciliation
```

---

## For Users to Install

Tell others to run:
```bash
/plugin marketplace add kbsfa/finsight-claude-plugins
/plugin install data-reconciliation@finsight-plugins
```

Then use:
```bash
/skill data-reconciliation
```

## Repository URL
https://github.com/kbsfa/finsight-claude-plugins

## If You Make Updates Later

```bash
# 1. Make your changes
# 2. Commit
git add .
git commit -m "Update: description of changes"

# 3. Update version tag
git tag -a v2.1.0 -m "Version 2.1.0 - new features"

# 4. Push
git push origin main --tags
```

Users update with:
```bash
/plugin update data-reconciliation@finsight-plugins
```
