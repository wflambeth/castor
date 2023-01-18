# C.A.S.T.O.R. 
*[American Beaver (Castor canadensis)](https://animaldiversity.org/accounts/Castor_canadensis/)* || https://castor.fly.dev 

Welcome to the **C**S **A**lternative **S**cheduling **T**ool - **OR**egon State. 

I'm building CASTOR to get my hands dirty hosting a public, full-stack webapp on an ongoing basis. (And of course, to fill the hole left by the death of the original [CS Scheduler](https://github.com/hschallh/cs-scheduler).) 

For current and prospective students in Oregon State's Postbaccalaureate BSCS program, I hope this can be a quick and painless alternative to MyDegrees, containing all the information you need to plan your time at OSU. 

# Current Status 
CASTOR is very much in active development, with the most recent release [live on fly.io](https://castor.fly.dev). Currently, users can: 
- Experiment with the drag-and-drop scheduling system via the demo landing page
- Create a password-protected account
- Build and save up to 10 custom schedules, pairing current OSU courses (both requirements and electives) with the year and quarter of their choice
- Feast their eyes on a UI that could generously be described as "Windows NT chic" 

# Roadmap 
Over the coming weeks, these features are next on my list: 
- A few final core functionalities: renaming schedules, the option to delete empty quarters
- Dynamic validation of drags/drops, so users can be sure their schedule is possible (both in terms of course prerequisites and quarter availability)
- A UI refresh that at least looks *deliberately* retro
- OAuth options for account authentication
- Importing or linking to additional course info: 
	- Official course descriptions
	- 	Instructor information
	- Avg rating/Avg difficulty from crowdsourced Google Doc data

# Tech
Currently, CASTOR leverages the following technologies: 
- Django 
- PostgreSQL
- JavaScript (just good ol' ECMAScript) 
- Jinja2
- HTML / CSS
- Docker
- Prometheus / Grafana

Coming soon:
- A comprehensive test suite 
- CI/CD via GitHub Actions
- OAuth 2.0
- Automated database cleanup and backup
- Periodic scraping of the [official Ecampus catalog](https://ecampus.oregonstate.edu/soc/ecatalog/ecourselist.htm?termcode=all&subject=CS) for validating stored course details


# Special Thanks
 - hschallh's [CS Scheduler](https://github.com/hschallh/cs-scheduler), of which this is basically a Python clone with some added features
 - [Dragula](https://github.com/bevacqua/dragula), the JS library that allowed me to drag and drop with panache without going full React
 
