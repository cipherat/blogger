This document will be my dirty reference of what am I doing. A dumb, boring step by step document.
For you as a human I dont think this is much useful for you to read, but it is planned to be refurbished.

# First design
Things to keep in mind:
- all blog files are written in a single markdown ".md" file
- this tool is simply a one-big get function, alongside a good data structure with somewhere to save the files at

### Challenges:
- blogs with "published" state are the only blogs to represent, others are kept hidden until state changes
- I want the way of displaying blogs to be: by date _(I think of adding "by views" in the future)_