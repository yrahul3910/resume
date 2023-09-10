# Resume

This repository contains my most up-to-date resumes. The PDFs themselves are in the `pdf/` directory, while the source needed to compile them is in the root directory. Because of the complexities of compiling multiple PDFs, the code is based on a custom templating engine I wrote, called [progres](https://github.com/yrahul3910/programmable-resumes). To compile this code, you will need to have that installed.

## Compiling

To generate the PDFs, run

```
progres -o pdf
```

This will generate all the PDFs simultaneously and move them to the `pdf/` directory.
