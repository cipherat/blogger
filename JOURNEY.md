This document will be my dirty reference of what am I doing. A dumb, boring step by step document.
For you as a human I dont think this is much useful for you to read, but it is planned to be refurbished.

# First design
Things to keep in mind:
- all blog files are written in a single markdown ".md" file
- this tool is simply a one-big get function, alongside a good data structure with somewhere to save the files at

### Challenges:
- blogs with "published" state are the only blogs to represent, others are kept hidden until state changes
- I want the way of displaying blogs to be: by date _(I think of adding "by views" in the future)_


## Chain of thoughts
##### 14/12/2025 After my "Family in Islam 102" final exam
So what I'm trying to achieve today is to find a way to:
- save blogs metadata in a small database (a csv file, until i notice its flaws and get to optimize it)
- simulate how the user registering a new blog would go (view page -> fill blog metadata -> request to api -> save in database)

As for now, I've noticed some limitations in using csv files:
1. updating and/or removing rows cost me read performance
2. I deal with literal strings rather than key-value entries, which is costly when retrieving data
3. parsing is ugly, because some fields I have are multivalued and I can't separate them with commas, so I use another "less-common" character for separation, which is.. meeh.. I don't like it