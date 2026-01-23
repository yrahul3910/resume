# List of tags used in `data.json`
tags = {"master", "sde", "sde_emp", "ml", "ml_emp", "academic", "ta", "phd", "hidden"}
for tag in tags:
    # It's important to use `globals()`!
    if tag not in globals():
        globals()[tag] = False

# Go top-down, starting with `master`
if master:
    for tag in tags - {"ta"}:
        globals()[tag] = True

# Always include concise employment records
sde_emp = True
ml_emp = True

# Always hide `hidden` items
hidden = False

outFile.writelines(
    [
        r"\newcommand{\role}{}",
        r"\newif\ifroleset",
        r"\rolesetfalse",
    ]
)

if sde and not master:
    outFile.writelines([r"\renewcommand{\role}{ Software Developer}", r"\rolesettrue"])
