# America's Next Top Model: Demystifying Two Methods for Election Prediction

Bella Karduck (bkarduck@umich.edu), Haley Johnson (haleyej@umich.edu), Rohit Maramaju (rmaram@umich.edu) Philip Menchaca (pmench@umich.edu)

If knowledge is power then when it comes to election predictions, the public is in the dark. Media reports are filled with opinion polling data and pundits expound on which candidate will win, but how are these predictions made? 

We test two methods of election prediction—a classical statistical approach and a machine learning method—and make them understandable to a general audience. A public website walks readers through the details of each method and allows them to compare the models’ predictions with actual outcomes.

See [pollrbear.com](https://www.pollrbear.com/) for more details.

This project fufills the capstone requirement for the Master's of Science in Information at the University of Michigan.

## How To Run Our Code 
To run the MRP model, run the cells in ```models/mrp_model.Rmd``` in order 

To run the machine learning model, the the cells in ```src/clean_ML.ipynb``` in order


## Datasets 
All datasets we used are publically avaliable. All rights belongs to their respective owners.

**Polls**
* Monmouth Univeristy 
    * [March 2020](https://www.monmouth.edu/polling-institute/reports/monmouthpoll_us_032420/)
    * [May 2020](https://www.monmouth.edu/polling-institute/reports/monmouthpoll_us_050620/)
    * [July 2020](https://www.monmouth.edu/polling-institute/reports/monmouthpoll_us_070220/)
    * [August 2020](https://www.monmouth.edu/polling-institute/reports/monmouthpoll_us_081120/)
* [Harvard University Poll, October 2020](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/E9N6PH)
* [COMETrends Pre-election survey from UT Dallas, October 2020](https://cometrends.utdallas.edu/)
* [Reuter's Poll, January 2024](https://ropercenter.cornell.edu/ipoll/study?doi=10.25940/ROPER-31120717)


**Census Data**
* 2020 5-year estimates from the American Community's Survey (retrieved with [IPUMS](https://www.ipums.org/))


## Repository Structure
Our repistory has the following structure. Note that only key files are included for brevity. 

```
├── Project Poster                      <- Poster for UMSI project expo
├── data                                <- Data soruces used
| 
├── documentation                       <- Documents data cleaning
| 
├── models                              <- Code for MRP model and propensity scores
│   └── mrp_model.Rmd                   <- Model 
│   └── mrp_model.html                  <- HTML rendering of R notebook 
│
├── src                                 <- Python scripts & notebooks
│   └── clean_ML.ipynb                  <- Machine learning model   
│   └── census_getter.py                <- Script to pull data with census API
|   └── helper.py                       <- Helper functions to process Reuter's poll
│   └── process_census_data.ipynb       <- Clean census data 
|   └── process_comet_poll.py           <- Clean COMET poll
│   └── process_harvard_poll_data.ipynb <- Clean Harvard poll
│   └── process_poll_data.ipynb         <- Clean Monmouth poll
│   └── process_reuters_poll.py         <- Clean Reuter's poll
|
├── website_699                         <- Source code for website
├── LICENSE
├── README.md
└── requirements.txt
```

## A Note on Portugol

Portugol is a toy programming language designed for educational purposes. It is primarily used by Portuguese-speaking school children. Just 4k Github repositories contain code written in Portugol, including ours. We have no idea why our repository says it includes Portugol code — everything is written in R, Python, CSS, and HTML. But we do think it's a little silly! 