# TestMate

A easy-to-use command-line tool that helps you automate QA tasks.

## Overview

- *Analyze your code*: Examine UI and fix broken selectors
- *Generate tests*: Create pytest tests automatically from your API documentation (Swagger files)
- *AI-powered insights*: Get smart suggestions using OpenAI to improve your code

## Installation

### Requirements
- Python 3.7 or higher
- Git

### For Windows

1. *Install Python* (if not already installed):
   - Download from [python.org](https://python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. *Open Command Prompt* and run:
   
cmd
   git clone https://github.com/ionaiobidze/gaia-hacakthon-qa --depth=1
   cd gaia-hacakthon-qa
   pip install -r requirements.txt
   

### For macOS

1. *Install Python* (if not already installed):
   
   # Using Homebrew (recommended)
   brew install python
   # Or download from python.org
   

2. *Open Terminal* and run:
   
   git clone https://github.com/ionaiobidze/gaia-hacakthon-qa --depth=1
   cd gaia-hacakthon-qa
   pip3 install -r requirements.txt
   

### For Linux (Ubuntu/Debian)

1. *Install Python* (if not already installed):
   
   sudo apt update
   sudo apt install python3 python3-pip git
   

2. *Clone and install*:
   
   git clone https://github.com/ionaiobidze/gaia-hacakthon-qa --depth=1
   cd gaia-hacakthon-qa
   pip3 install -r requirements.txt
   

## How to Use

### Setup

To use AI-powered analysis, you need an OpenAI API key:

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Set it as an environment variable:

*Windows:*
cmd
set OPENAI_API_KEY=your_api_key_here

*macOS/Linux:*
export OPENAI_API_KEY=your_api_key_here

Or create a .env file in the project folder:
OPENAI_API_KEY=your_api_key_here

The tool works as a single command with different options:

python main.py [options]

### Command Options

You can access available options with the following command:
python main.py --help

| Option | Description |
|--------|-------------|
| --ui | Analyze UI and fix broken selectors |
| --back | Analyze backend code |
| --deep | Enable deep AI analysis |
| --swagger-path | Path to your Swagger/OpenAPI JSON file |
| --message | Custom requirements for test generation |
| --verbose | Show detailed output |

### Examples

# analyze backend code
python main.py --back
# analyze your ui code
python main.py --ui
# analyze both UI and backend
python main.py --ui --back
# generate tests from Swagger file
python main.py --back --swagger-path path/to/your/swagger.json
# generate tests with deep analysis
python main.py --deep --ui --back
# add custom requirements for test generation
python main.py --back --swagger-path swagger.json --message "Generate tests for user authentication"
# with verbose output
python main.py --back --verbose
