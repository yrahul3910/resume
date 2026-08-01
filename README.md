# Resume

This repository contains my most up-to-date resumes. There are four, all built from the same source: [master](pdf/master.pdf) (the kitchen-sink CV), [sde](pdf/sde.pdf), [ml](pdf/ml.pdf), and [academic](pdf/academic.pdf). Because of the complexities of compiling multiple PDFs, the code is based on a custom templating engine I wrote, called [progres](https://github.com/yrahul3910/programmable-resumes). To compile this code, you will need to have that installed.

## Compiling

To generate the PDFs, run

```
progres -o pdf
```

You can also use `make`, which runs the same thing with `-d` (debug mode). These will generate all the PDFs simultaneously and move them to the `pdf/` directory. If you're editing the source and run into LaTeX or Python errors, you can remove intermediate files using `make clean`. There is also `progres --anon`, which builds scrubbed versions: placeholder name and contact details, with links truncated to their domains.

## How does this work?

The resume that led you here is written using a custom resume templating system I wrote, called `progres`. The README for that project (linked above) goes into detail, but in brief:

* `data.json` - Contains all the raw data. Different PDFs use different parts of this data based on the role. Items have a `tags` attribute: these are used for filtering. Employment entries render only if *all* of their tags are enabled; projects render if *any* of theirs is.
* `schema.json` - A JSON Schema describing the shape of `data.json`, for editor tooling and manual validation.
* `configs.json` - This file describes, for each config, what tags are/aren't set. These are simply arrays of Python code, and they set different variables (which are the same as the tags) for each config.
* `computeRole.py` - This adds additional rules; the main one being that for the "master" resume, all tags are enabled. It also forces a few tags off everywhere (see below).
* `preamble.tex` - This is the preamble section of the intermediate LaTeX document, see below.
* `spec.py` - Describes how to generate the LaTeX files for each config. It also version-gates the data: if `data.json` declares a newer version than `spec.py` supports, the build refuses to run.
* `Specfile` - A set of commands that describes how to build the resumes. It first imports a few necessary files described above. Each `PARSE` command is a call to one of the `parse_` functions from `spec.py`, and any arguments are forwarded as-is. Lines that don't start with a recognized command are treated as Python code.

With these files in place, the "main" file is the `Specfile`. `progres` performs the following conversions:

```
Specfile --> Python files --> LaTeX files --> PDFs
```

`progres` is an interpreter that parses the commands and Python code from `Specfile`, and generates one Python file for each config. These are then run in parallel, and each of them generates a LaTeX file. These are compiled in parallel (generating the PDFs), and the intermediate files are deleted.

## The configs

| Config | Included |
| --- | --- |
| `master` | Everything: full employment history, all projects, full publications, preprints, funding, service, and talks, with academic ordering (education first). |
| `sde` | Skills first, employment in last 5 years, and the 5 most recent `sde`-tagged projects. No research sections. |
| `ml` | Skills first, employment in last 5 years, the 5 most recent `ml`-tagged projects, the 5 most recent publications, plus funding and service. |
| `academic` | Education first, employment in last 5 years, full publications, preprints, funding, service, and invited talks. No projects section. |

Some tags (`hidden`, `sde_hidden`, `ta`) are never enabled by any config, so entries carrying them render nowhere. This lets me maintain detail that doesn't fit a resume but is worth keeping, such as more detailed stats, early-stage projects, a brag sheet, etc. right next to the visible content it backs, ready to be promoted to a visible tag later.

## FAQ

### Why not a single resume?

To generate tailored resumes for different roles. When applying to ML roles, for example, a lot of the research-related data is pulled in; these are excluded for SDE.

### This is too complex/over-engineered!

Correct, but it's *cool*. I have crazy ideas; sometimes they work. This is one of those times.

I had a very specific need and wanted an easy way to generate up-to-date versions of each PDF.

### Why not [alternative]?

Most likely, it was not flexible enough when I started writing this.
