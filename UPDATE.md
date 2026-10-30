# Updating Hot Folder

## Source checkout

Back up the user's configuration first. From the repository directory:

```powershell
git switch main
git fetch origin main --prune
git pull --ff-only origin main
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Review release notes before using a new build. Do not run feature branches as a production updater source.

## Packaged application

The current build is a development distribution, not a signed enterprise installer. Stop monitoring, back up the configuration under `%LOCALAPPDATA%\\HotFolder\\config.json`, replace the application folder with a verified release, then relaunch and verify the printer and renderer settings. Never update while a print submission is in progress.

Automatic self-updating is not implemented.
