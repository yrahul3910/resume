# Resume

This repository contains my most up-to-date resumes. The PDFs themselves are in the `pdf/` directory, while the source needed to compile them is in the root directory. Because of the complexities of compiling multiple PDFs, the code is based on a custom templating engine I wrote, called [progres](https://github.com/yrahul3910/programmable-resumes). To compile this code, you will need to have that installed.

## Compiling

To generate the PDFs, run

```
progres -o pdf
```

You can also use

```
make
```

These will generate all the PDFs simultaneously and move them to the `pdf/` directory.

## How does this work?

The resume that led you here is written using a custom resume templating system I wrote, called `progres`. The readme for that project (linked above) goes into detail, but in brief:

* `data.json` - Contains all the raw data. Different PDFs use different parts of this data based on the role. Items have a `tags` attribute: these are used for filtering.
* `configs.json` - This file describes, for each role, what tags are/aren't set. These are simply arrays of Python code, and they set different variables (which are the same as the tags) for each config. Items are only shown in a config if *all* the tags are set to `True`.
* `computeRole.py` - This adds additional rules; the main one being that for the "master" resume, all tags are enabled.
* `preamble.tex` - This is the preamble section of the intermediate LaTeX document, see below.
* `spec.py` - Describes how to generate the LaTeX files for each config.
* `Specfile` - A set of commands that describes how to build the resumes. It first imports a few necessary files described above. Each `PARSE` command is a call to one of the `parse_` functions from `spec.py`, and any arguments are forwarded as-is. Lines that don't start with a recognized command are treated as Python code.

With these files in place, the "main" file is the `Specfile`. `progres` performs the following conversions:

```
Specfile --> Python files --> LaTeX files --> PDFs
```

`progres` is an interpreter that parses the commands and Python code from `Specfile`, and generates one Python file for each config. These are then run in parallel, and each of them generates a LaTeX file. These are compiled in parallel (generating the PDFs), and the intermediate files are deleted.

## FAQ

### Why not a single resume?

To generate tailored resumes for different roles. When applying to ML roles, for example, a lot of the research-related data is pulled in; these are excluded for SDE.

### This is too complex/over-engineered!

Correct, but it's *cool*. I have crazy ideas; sometimes they work. This is one of those times.

I had a very specific need and wanted an easy way to generate up-to-date versions of each PDF.

### Why not use [alternative]?

It wasn't quite as flexible as I wanted, most likely.
