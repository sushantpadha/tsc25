
## git: what cs guys think trees actually look like
> HEAD = latest commit of branch we are on
> (essentially it indicates the end of a *chronological* sequence of *related* commits)
> 
> it is detached when we checkout to non-latest commit of some branch, or to some remote ref like `origin/main` and any commits made now are floating = **lost unless branched off**
### Config
```
git config --global user.name/email "asdf"/"asdf@clg.edu.in"
git config --global core.editor "vim"
git config --list  # show all setting
git config user.name   # show specific setting
```

### Adding

`git add .`  stage all changes in cd
`git add -u` stage only modified and deleted *tracked* files in entire repo
Note, it does not add untracked files

`git add -A`  stage everything everywhere
Does include untracked files

m/d/u = modification/deletion/add(was untracked earlier)

`git restore --staged <file>` to remove a file's m/d/u from staging area

`git commit -a ...` is the same as running `git add -u` and then committing

`git commit --amend` to append the staged changes to prev commit and amend commitmsggi

### Log
`git log` shows commit history of current branch
`git log BRANCH`
`git log FILE` only of commits that touched file FILE
`git log --oneline` one line per commit: hash and commitmsg
`git log -p` shows consecutive commit diffs
`git log -n N` only last N commits
`git log --stat` shows summary of file changes per commit

`git log --graph --decorate --all` visualize commit history across all branches (add `--oneline` to easy reading)

`git log --since="2025-01-01"`

### Diff
> diff output is a series of commands to change file a to file b

`git diff <COMMIT-A> [<COMMIT-B>]` (if left blank COMMIT-B is working directory) shows ***diff of B wrt A***
output:
```
                    (refers to commits a and b in order)
diff --git a/foo b/foo
                    (hashes computed for commits a and b in order)
index a2441b8..c92fafb 100644
                    (means we are showing diff of b/foo wrt a/foo)
--- a/foo
+++ b/foo
```

eg:
foo
```
you are all i need...
im in the middle of your picture...
lying in your reeds

its all wrong
```

boo
```
you are all i need
im in the middle of your picture...

its all wrong
bye
bye
```

`diff foo boo`
```
1c1
< you are all i need...
---
> you are all i need
3d2
< lying in your reeds
5a5,6
> bye
> bye
```

`1c1`: change line 1 in a to line 1 in b followed by `< <line-from-a>` and `> <line-from-b>`

`3d2`:  delete line 3 in a and now it'll become line 2 in b followed by `< <line-from-foo>`

`5a5,6`: add lines 5,6 of b after line 5 of a followed by `> <line-from-b>`

`diff -u foo boo` (gives unified diff which is what git uses)
```
--- foo 2025-04-08 16:26:41.095857600 +0530
+++ boo 2025-04-08 16:43:33.781042900 +0530
@@ -1,5 +1,6 @@
-you are all i need...
+you are all i need
 im in the middle of your picture...
-lying in your reeds

 its all wrong
+bye
+bye
```

`--- file a` and `+++ file b`
`@@ -1,5 +1,6 @@` means diff will show a piece of text spanning lines 1-5 in foo and 1-6 in boo
`-` means it was deleted in b (as compared to a) *delete from a to make it like b*
`+` means it was added in b (as compared to a) *add to a to make it like b*

---

`git diff --cached <a>` shows staged changes wrt a 

`git diff HEAD` shows changes in working directory (staged or unstaged) wrt latest commit of current branch ie HEAD

`git diff <commit> -- file-paths` to only diff some files

`git show COMMIT` detailed info
`git show :FILE` show file contents in *staging area*
`git show COMMIT:FILE` shows file contents in that commit
`git show BRANCH` latest commit

### checkout
`git checkout COMMIT` rollback to previous commit in working dir (useful for only viewing)
`git checkout COMMIT FILE` rollback to previous commit in working dir (useful for only viewing)
**alternate for above:** `git restore --source=COMMIT <file>`

### branches
`git branch [-r] [-a]` view local branches / remote branches / all
`git branch BRANCH` create new branch
`git switch BRANCH` checkout to it
`git switch -c BRANCH` create and checkout (useful if you're in detached head but u want to save changes to a new branch)
`git branch -b BRANCH` (same as above)
`git branch -d BRANCH` delete a branch (use `-D` to force)
`git branch -m OLDNAME NEWNAME`

`git merge -m "MERGE_COMMIT_MSG" branch-to-merge`
`git merge --no-ff branch` forces a merge commit even if a fast-forward is possible — useful for preserving merge history.

### reverting
`git revert COMMIT` introduces new commit with reverse changes

> [!danger] reset is dangerous

```
git reset HEAD FILE      # unstage a file
git reset --soft HEAD~1  # undo last commit, keep changes staged
git reset --mixed HEAD~1 # undo last commit, keep changes in working directory
git reset --hard HEAD~1  # discard commit AND changes
git reset --hard COMMIT  # move to any commit (dangerous if not backed up)
```

`git reset HEAD`  unstage changes (move them back to working directory) from the last commit
`git reset [--hard] HEAD~1` To discard the last commit (use with caution, as it rewrites history) (without brings reverted changes into working directory, hard removes them as well)
`git reset --hard ghi78` To move the branch pointer to a specific commit (e.g., ghi789)