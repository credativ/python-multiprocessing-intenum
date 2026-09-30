# Contributing to Python multiprocessing-intenum

## Repository signing

This project uses signed commits and tags, to allow verifying the
authenticity and integrity of the git repository.

After cloning, enable commit signing from inside the working directory:
```
git config --local commit.gpgsign true
git config --local tag.gpgsign true
```

## Merge process

Due to an issue with GitHub, it for no good reason refuses to merge an
accepted pull request onto a signed main branch using the UI and it thus has
to be done manually.

Manually merge approved pull request:
```
git checkout main
git pull
git merge --ff-only feature/branch
git push
```
