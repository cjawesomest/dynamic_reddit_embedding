# Dynamic Reddit Embedding

Currently in the works to create a Niche Subreddit Recommendation application. 
Intends to recommend a 'Niche Subreddit' based on the input query and a number of other refinement criteria. 

## Initial Results 2020
Plots showcase snapshots of three subreddits from the dates of May 21st, 2020 to June 4th, 2020. 
* *SubReddit Plots* showcase a set of nodes (SubReddits) connected by edges (Users who commented in both of the connected subreddits on the same day)
* *Comment Plots* showcase a set of nodes (SubReddits) connected by edges ([Comments whose content is only a link to another subreddit](https://www.reddit.com/r/ProgrammerHumor/comments/dk6b9t/have_you_tried_plugging_it_in/f4cv6ef?utm_source=share&utm_medium=web2x&context=3))

| r/<subreddit_name> | SubReddit Plot | Comments Plot |
| :---         |     :---:      |          ---: |
| r/AskReddit | ![r/AskReddit Plot over 2 weeks](img/AskReddit_plot_animated.gif?raw=true "AskReddit Plot") | ![r/AskReddit Plot Comments over 2 weeks](img/AskReddit_plot_animated_comment.gif?raw=true "AskReddit Comment Plot") |
| r/Bartenders | ![r/Bartenders Plot over 2 weeks](img/Bartenders_plot_animated.gif?raw=true "Bartenders Plot") | ![r/Bartenders Plot Comments over 2 weeks](img/Bartenders_plot_animated_comment.gif?raw=true "Bartenders Comment Plot") |
| r/Politics | ![r/Politics Plot over 2 weeks](img/Politics_plot_animated.gif?raw=true "Politics Plot") | ![r/Politics Plot Comments over 2 weeks](img/Politics_plot_animated_comment.gif?raw=true "Politics Comment Plot") |

## To-Do (Perhaps)
- [ ] Make those plots less psychedelic, or rather, more psychedelic... but *better*
