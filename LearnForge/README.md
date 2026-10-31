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