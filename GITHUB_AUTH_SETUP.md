# GitHub Authentication Setup Guide

## Current Status
- Your code is committed locally to git
- Remote repository: `https://github.com/mondocosm/magi.git`
- Push to GitHub is failing due to authentication
- No GitHub CLI or SSH keys are currently configured

## Option 1: Personal Access Token (Recommended)

### Step 1: Create a Personal Access Token
1. Go to GitHub.com and log in
2. Click your profile picture → Settings
3. In the left sidebar, click "Developer settings"
4. Click "Personal access tokens" → "Tokens (classic)"
5. Click "Generate new token" → "Generate new token (classic)"
6. Give it a name (e.g., "MAGI Pipeline")
7. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
8. Click "Generate token"
9. **Important:** Copy the token immediately (you won't see it again!)

### Step 2: Configure Git to Use the Token
Run these commands in your terminal:

```bash
# Configure git to use the token
git config --global credential.helper store

# Push to GitHub (you'll be prompted for username and password)
# Username: your GitHub username
# Password: the personal access token you just created
git push -u origin master
```

When prompted:
- **Username:** Your GitHub username (e.g., `mondocosm`)
- **Password:** The personal access token you created (NOT your GitHub password)

### Step 3: Verify the Push
After successful authentication, your code will be pushed to GitHub. You can verify by visiting:
https://github.com/mondocosm/magi

## Option 2: SSH Key Setup (More Secure)

### Step 1: Generate SSH Key
```bash
# Generate a new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# When prompted, press Enter to accept default location
# You can optionally add a passphrase for extra security
```

### Step 2: Add SSH Key to GitHub
1. Copy the public key:
```bash
cat ~/.ssh/id_ed25519.pub
```

2. Go to GitHub.com → Settings → SSH and GPG keys
3. Click "New SSH key"
4. Paste the public key
5. Click "Add SSH key"

### Step 3: Update Git Remote to Use SSH
```bash
# Change remote URL from HTTPS to SSH
git remote set-url origin git@github.com:mondocosm/magi.git

# Push to GitHub
git push -u origin master
```

## Option 3: GitHub CLI (Easiest)

### Step 1: Install GitHub CLI
```bash
# On macOS with Homebrew
brew install gh

# Or download from: https://cli.github.com/
```

### Step 2: Authenticate
```bash
# Login to GitHub
gh auth login

# Follow the prompts:
# 1. Select "GitHub.com"
# 2. Select "HTTPS" or "SSH"
# 3. Select "Login with a web browser"
# 4. Copy the code and paste it in your browser
# 5. Authorize the GitHub CLI application
```

### Step 3: Push to GitHub
```bash
git push -u origin master
```

## Quick Start (Fastest Method)

If you want to push immediately, use Option 1 (Personal Access Token):

1. Create a token at: https://github.com/settings/tokens
2. Run: `git push -u origin master`
3. Enter your GitHub username and the token as password

## Troubleshooting

### "fatal: could not read Username"
This means git needs credentials. Use one of the methods above.

### "remote: Invalid username or password"
Make sure you're using your personal access token as the password, NOT your GitHub password.

### "Permission denied (publickey)"
This means SSH authentication failed. Check that your SSH key is added to GitHub.

### "fatal: repository not found"
Make sure the repository URL is correct: `https://github.com/mondocosm/magi.git`

## After Successful Push

Once your code is pushed to GitHub, you can:
- View your repository at: https://github.com/mondocosm/magi
- Share the repository URL with others
- Create issues and pull requests
- Set up GitHub Actions for CI/CD
- Enable GitHub Pages for documentation

## Security Notes

- Never share your personal access token
- Tokens can be revoked at: https://github.com/settings/tokens
- Consider using different tokens for different projects
- SSH keys are generally more secure than personal access tokens
- Enable two-factor authentication on your GitHub account

## Need Help?

If you encounter any issues:
1. Check GitHub's documentation: https://docs.github.com/en/authentication
2. Verify your repository URL: `git remote -v`
3. Check git configuration: `git config --list`
4. Test SSH connection: `ssh -T git@github.com`