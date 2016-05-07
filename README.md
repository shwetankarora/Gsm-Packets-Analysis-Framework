# Gsm-packets-Analysis-Framework

This is a python based gsm packets real time analysis framework. It uses the gsm packets produced by [gsm-simulator](https://github.com/iostreamer-X/gsm_simulator) and stores it in a mongodb database for analysis using a node app named 'client'. It also provides an easy to use API for creating your own custom python scripts for analyzing packets already stored in mongo database. Not only this, it also gives you some ready made data visualization templates which uses google charts API and mapbox API allowing you to plot and visually interact with the data.

It is a part of my minor project of analyzing cellular data to understand population mobility pattern and prevent epidemic outspread in Delhi region.

I will be uploading the docs soon!!!

##Dependencies

1. **Node.js**
2. **mongodb**
3. **crossbar**
4. **virtualenv**
5. **python > 2.7.9**

##Install

Currently it works on a linux based system.

1. Do a git clone
2. [python](https://www.python.org/downloads/)
3. [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
4. [mongodb](https://docs.mongodb.com/manual/installation/)
5. [nodejs](https://nodejs.org/en/download/package-manager/)

No need to install crossbar because it is already there in `django_virtualenv`.

##Usage

1. **generating and storing gsm packets** : cd to the directory and run `python run.py -p <number>`. Make sure that you are running mongod instance in the background. Here *number* is the number of people in a state.
2. **running the framework** : fire up a terminal and activate virtualenv using `source ./django_virtualenv/bin/activate`. cd to *mainFramework* and run `crossbar start`. This will autmatically run a crossbar router with *main.py* file.
3. **analyzing and visualizing packets** : now open *GoogleCharts.html* template in a browser and run `python CellTowersData.py` in virtualenv activated terminal or new terminal.

If you see the bar chart, then the code is working

##Future

I will be adding support for other visualization elements like piechart, geochart, etc.
Till then, stay tuned!!!

##Screenshots
![Cell Towers in Delhi](https://github.com/shwetankarora/Gsm-Packets-Analysis-Framework/blob/master/mainFramework/screenshots/Cell_Towers_Delhi.png "Cell Towers in Delhi")
![Day1 stats](https://github.com/shwetankarora/Gsm-Packets-Analysis-Framework/blob/master/mainFramework/screenshots/Day1.png "Call Details of Day1")
![Person1 stats](https://github.com/shwetankarora/Gsm-Packets-Analysis-Framework/blob/master/mainFramework/screenshots/Person1.png "Call Details of Person1")

