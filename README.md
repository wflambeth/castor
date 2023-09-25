# C.A.S.T.O.R. 
*[American Beaver (Castor canadensis)](https://animaldiversity.org/accounts/Castor_canadensis/)* || https://cs-planner.com

Welcome to the **C**S **A**lternative **S**cheduling **T**ool - **OR**egon State. 

This tool is designed for current and prospective students in Oregon State's Postbaccalaureate BSCS program. I hope it can be a quick and painless alternative to MyDegrees, giving you all the information you need to plan your path at OSU. 

## Usage

### Scheduling Courses
To start building a schedule, simply select from the available courses and drag them into a quarter. When dragging a course, any prerequsites are highlighted in brown, and quarters where a course can be dropped are outlined in green. (You can add more quarters via the "+" buttons at the top and bottom of the schedule.)

![Demo GIF 1](https://github.com/wflambeth/castor/blob/main/demo_content/castor_demo_1.gif)

### Logging In and Creating New Schedules
Once you log in (via the "Log In" or "Sign Up" links), you can create up to 10 schedules at a time in the sidebar. These schedules can be renamed with the "Edit Title" button, and deleted via the "x" mark in the schedule list. 

![Demo GIF 2](https://github.com/wflambeth/castor/blob/main/demo_content/castor_demo_2.gif)

### Saving Changes

Don't forget to save any changes you make! CASTOR does not auto-save, so you'll need to manually press "Save Changes" after updating a schedule. 

![Demo GIF 3](https://github.com/wflambeth/castor/blob/main/demo_content/castor_demo_3.gif)

## Technical Details

CASTOR is built on Python's Django webserver framework, along with a PostgreSQL database and a vanilla-JavaScript frontend. (Let's generously call the design "retro-chic".) Dragging and dropping is courtesy of the [Dragula](https://github.com/bevacqua/dragula) JS library.

Course data is programmatically scraped from the [Oregon State CS Catalog](https://ecampus.oregonstate.edu/soc/ecatalog/ecourselist.htm?termcode=all&subject=CS) on a regular basis, and updated with any changes to course availability. (Courses are *generally* available in the same quarters every year, but this isn't always the case; CASTOR does not track availability specific to a given year, so inconsistencies are possible.) 

In terms of hosting, CASTOR lives in AWS ECR as a Docker container, and is deployed via AWS App Runner. The database is hosted by AWS RDS, and protected behind a Virtual Private Cloud. This ensures high availability and rock-solid data security for all CASTOR users. 

## Roadmap 
These are the next features I'd love to add: 
- A credit-counter system for highlighting when the 60-credit threshhold for graduation is met
- The ability to create copies of existing schedules
- A "confirm" modal for deleting schedules, and for exiting a page with unsaved schedule changes
- Proper handling of courses which are reusable (CS 469) and/or have variable credit options (CS 406)
- OAuth options for account authentication


## Feedback? 

Feel free to drop me a line at lambethw@oregonstate.edu if you have any thoughts, or [open an issue here](https://github.com/wflambeth/castor/issues) if you see anything amiss!

Finally, a special thanks to hschallh's original [CS Scheduler](https://github.com/hschallh/cs-scheduler), the inspiration for this project. 
