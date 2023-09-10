for key in ['master', 'sde', 'ml']:
    if key not in globals():
        globals()[key] = False

if master:
    sde = True
    ml = True

outFile.writelines([
    r'\newcommand{\role}{}',
    r'\newif\ifroleset',
    r'\rolesetfalse',
])

if sde and not master:
    outFile.writelines([
        r'\renewcommand{\role}{ Software Developer}',
        r'\rolesettrue'
    ])
