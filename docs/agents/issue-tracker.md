# Issue tracker: GitHub

Issues and specs live in GitHub Issues for `lh7314/mattpocock_test`.
Use the `gh` CLI. Pass `--repo lh7314/mattpocock_test` explicitly
for issue, pull request, and label operations.

## Conventions

- Create: `gh issue create --title "..." --body-file <path>`.
  Write multiline bodies to a temporary UTF-8 file first.
- Read: `gh issue view <number> --json number,title,body,labels,comments`.
- List: `gh issue list --state open --json number,title,body,labels`;
  apply label and state filters as needed.
- Comment: `gh issue comment <number> --body-file <path>`.
- Apply or remove labels: `gh issue edit <number> --add-label "..."`
  or `--remove-label "..."`. Use `triage-labels.md` for the mapping.
- Close: post the explanation as a comment, then `gh issue close <number>`.
- Sub-issues: use `gh issue create --parent <parent>` or
  `gh issue edit <parent> --add-sub-issue <child>`.
  If unavailable, put `Part of #<parent>` in the child and a task list
  of children in the parent.
- Blocking: use native issue dependencies through
  `gh issue edit <child> --add-blocked-by <blocker>`.
  If unavailable, record `Blocked by: #<number>` near the top of the body.
  A ticket is unblocked when every blocker is closed.

Before the first issue creation in a session, verify the target:
`gh repo view lh7314/mattpocock_test --json nameWithOwner`.
Publish only to this configured repository.

## Pull requests as a triage surface

**PRs as a request surface: no.**

If changed to `yes`, read PR descriptions, comments, and diffs, and use
the same triage labels through the corresponding `gh pr` operations.
GitHub shares issue and PR numbers; resolve the object type before acting.

## Skill operations

- "Publish to the issue tracker": create a GitHub issue.
- "Fetch the relevant ticket": read the referenced GitHub issue.

## Wayfinding operations

- Map: one issue labelled `wayfinder:map`, containing Notes,
  Decisions-so-far, and Fog.
- Child: a sub-issue labelled `wayfinder:<type>`, where type is
  `research`, `prototype`, `grilling`, or `task`.
- Frontier: open children with no open blockers and no assignee;
  choose the first in map order.
- Claim: assign the child to the driving developer before working.
- Resolve: comment with the answer, close the child, and append
  a gist and link to the map's Decisions-so-far.
- Create any missing wayfinding labels when that workflow is first used.
