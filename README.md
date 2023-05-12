# C.A.S.T.O.R. 
*[American Beaver (Castor canadensis)](https://animaldiversity.org/accounts/Castor_canadensis/)* || https://castor.fly.dev 

Welcome to the **C**S **A**lternative **S**cheduling **T**ool - **OR**egon State. 

For current and prospective students in Oregon State's Postbaccalaureate BSCS program, I hope this can be a quick and painless alternative to MyDegrees, containing all the information you need to plan your time at OSU. 

# Current Status 
CASTOR is [live on fly.io](https://castor.fly.dev). Currently, users can: 
- Experiment with the drag-and-drop scheduling system on the demo landing page
- Create a password-protected account
- Build and save up to 10 custom schedules, with an easy drag-and-drop UI containing all current OSU course information, scraped regularly from the official catalog
- Enjoy dynamic validation of drags/drops, so users can be sure their schedule is possible (both in terms of course prerequisites and quarter availability)
- Feast their eyes on a UI that could generously be described as "Windows NT chic" 

# Roadmap 
Over the coming weeks, these features are next on my list: 
- The ability to create copies of existing schedules
- A credit-counter system for highlighting when the 60-credit threshhold for graduation is met
- OAuth options for account authentication
- Proper handling of courses which are reusable (CS 469) and/or have variable credit options (CS 406)

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
- OAuth 2.0

# Special Thanks
 - hschallh's [CS Scheduler](https://github.com/hschallh/cs-scheduler), of which this is basically a Python clone with some added features
 - [Dragula](https://github.com/bevacqua/dragula), the JS library that allowed me to drag and drop with panache without going full React
 
