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

I'm planning to use this tool as an administration panel for myself on my laptop, such that whenver I write a new blog I register it in the database, and a minimal api for my blog site to load blogs information in its main page and user can browse them. But how would I sync blogs content/files and database between my laptop and my hosting server? simply by using github and open-sourcing the shit out of it, such that on every new push there is a workflow that deploys new blogs on my server.


##### 16/12/2025 Just before my database project discussion _(for the 4th time)_
I succeeded in improving the performance of rendering the main blogs page, also to ~fully~ partially remove the need of javascript (only js used is to alert the user not to js)

I really need to find a better database than the shitty csv, I also need to find a keying strategy that sorts my blogs in publishing date order (latest->oldest), and a way to separate


##### 22/12/2025 _(one day after my database final)_ Shit, i got sick
So, I've done some major changes in the application without documenting anything, and this is what I hate about myself, the inability to speak my mind. However, new updates were about the database and generally _how_ and _where_ to save the blogs' metadata, I made some stress testing on the previous strategy -that uses csv files- and it was so bad that it took >100ms for fetching/displaying 5K entries only (I know I wouldn't be writing 5K pages any sooner, but hey, as I mentioned before I'm building this tool with a software engineer mindset, so Im trying to maximize the performance of everything), so that was the motivation to move to Postgres database. HOWEVER. after stress testing again to approximately measure the improvement of how to save the data, I got great numbers _(e.g. ~30ms)_, but after doing it I didn't feel that I was supposed to go in this path, to use such great software one created before me and just use it because it works and works good, what my real intuition was to build a full system from the ground up, considering the points where and how am I going to save the data, how to later fetch this data and process it and how can I use the best data structure for my cases _(i.e. my todo list)_, all the way up to how to create enough abstraction to represent this data for whatever the method of view users of this tool will be using.