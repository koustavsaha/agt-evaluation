# agt-evaluation
Hands-on evaluation of Microsoft Agent Governance Toolkit



### Install Prerequisites

Open Terminal on your Mac and run each command one at a time:

```bash
# Check if Python 3.10+ is installed
python3 --version
# You need 3.10 or higher. If not installed:
# Go to https://www.python.org/downloads/ and install Python 3.12

# Check if git is installed
git --version
# If not: xcode-select --install

# Check if VS Code is installed
code --version
# If not: download from https://code.visualstudio.com/
```


### Clone and Set Up the Project

```bash
# Clone your new repo (replace YOUR_USERNAME)
cd ~/Documents
git clone https://github.com/koustavsaha/agt-evaluation.git
cd agt-evaluation

# Open in VS Code
code .
```



### Create a Python Virtual Environment

Run these commands in **VS Code's terminal**


```bash
# Create an isolated Python environment
python3 -m venv .venv

# Activate it (you must do this every time you open a new terminal)
source .venv/bin/activate

# Your terminal prompt should now show (.venv) at the start
# Example: (.venv) yourname@MacBook agt-evaluation %

# Upgrade pip
pip install --upgrade pip
```


###  Install Google ADK

```bash
pip install google-adk
```



### Set Up Gemini API Access

Your agent needs access to a Gemini model (the LLM that powers its reasoning).

```bash
# Get a free API key from: https://aistudio.google.com/apikey
# Click "Create API Key" and copy it

# Create a .env file (VS Code: right-click in file explorer → New File → .env)
```

**File: `.env`** (create this in the project root)
```
GOOGLE_GENAI_USE_VERTEXAI=False
GOOGLE_API_KEY=paste-your-api-key-here
```

> **Important:** Never commit API keys to GitHub. Let's add this to .gitignore:

**File: `.gitignore`** (create this in the project root)
```
.venv/
.env
__pycache__/
*.pyc
.DS_Store
```

```bash
source .venv/bin/activate

# Install the full stack (all 7 packages in one command)
pip install agent-governance-toolkit[full]
```



###  Verify Each Package


python tests/test_00_verify_install.py




##  Run and Test the  Agent

In VS Code's terminal:

```bash
# Make sure virtual environment is active
source .venv/bin/activate

# Start the ADK development server with web UI
adk web agent
```




###  Open the Dev UI

Open your web browser and go to: **http://localhost:8000**

You will see a chat interface. This is ADK's built-in development UI. On the left, you should see your agent name "research_analyst".
