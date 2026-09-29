# Updating Hot Folder

## Manual update

1. Pull the latest main commit.
2. Create a clean Python virtual environment using the supported Python version documented by the project.
3. Install requirements.txt.
4. Run the available tests or smoke checks before deployment.

## Dependency maintenance

Dependabot checks Python and GitHub Actions dependencies weekly. Review updates through CI before merging.

## Automatic updates

The application does not silently replace itself. Updates are applied manually so deployments remain auditable and reversible.
