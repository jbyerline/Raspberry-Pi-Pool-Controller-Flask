# Raspberry Pi Pool Controller Flask
 A raspberry pi and arduino pool controller made in python to work with a pentair pool system.

## Installation
1. Install python3
2. Install pip3
3. Install git
4. Clone this repo: https://github.com/jbyerline/Raspberry-Pi-Pool-Controller-Flask.git
5. Install all pip requirements
6. Test running locally with `python3 app.py`
7. Setup crontab to run `python3 app.py` on boot: `crontab -e` then add `@reboot /usr/bin/python3 /home/jbyerline/Raspberry-Pi-Pool-Controller-Flask/PoolService/app.py >> /home/jbyerline/Raspberry-Pi-Pool-Controller-Flask/PoolService/logfile.log 2>&1`
8. Reboot and test, the service should be running on port 8000 and available at https://poolservice.byerline.me