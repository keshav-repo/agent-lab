### How to start 

For MacOS and Linux users, you can use the following commands to clone the repository, set up a virtual environment, install dependencies, and start the application:
```commandline
git clone https://github.com/keshav-repo/agent-lab.git
cd LearnForge

# setup virtual environment, if uv is installed
uv venv

# install dependencies
uv sync

# make the script executable
chmod +x StartApp.sh 

./StartApp.sh 
```

### BrowserAssistant
/clipboard -> copy to clipboard
/save <AbsolutePath> -> save the file to the given path

```shell
 source /Users/keshavkumar/learn26/agent-lab/LearnForge/.venv/bin/activate
 python /Users/keshavkumar/learn26/agent-lab/LearnForge/BrowserAssistant.py 
```

### Excalidraw diagram assistant

```shell
python DrawIoAgent.py
```

Example session:

```text
Diagram> Create a high-level architecture diagram for an online learning platform.
Diagram> Add a payment service and show the enrollment flow.
Diagram> Export this as diagram_exports/learning-platform.excalidraw.
```

Commands: `/open` opens the canvas, `/clear` clears chat context without changing
the canvas, and `/exit` ends the session. Optional environment settings:
`EXCALIDRAW_MCP_COMMAND`, `EXCALIDRAW_MCP_ARGS`, `EXPRESS_SERVER_URL`,
`EXCALIDRAW_EXPORT_DIR`, and `EXCALIDRAW_OPEN_BROWSER=0`.
