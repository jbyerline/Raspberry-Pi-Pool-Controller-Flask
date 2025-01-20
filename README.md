# Raspberry Pi Pool Controller Flask
 A raspberry pi and arduino pool controller made in python to work with a pentair pool system.

## Running Locally
This project should be runnable on non-linux systems, but it is designed to run on a raspberry pi. To run locally, follow these steps:
1. Install python3.9
2. Install pip3
3. Install git
4. Clone this repo:
5. Install all pip requirements with `pip3 install -r requirements.txt`
6. Create a `.env.local` file 
7. Be sure `USE_MOCK` is set to `True` in `app.py`
8. Run `python3 app.py` to start the server

Be sure to increment the version number in the `.env` file

## Deployment on RPI
1. Install python3.9
2. Install pip3
3. Install git
4. Clone this repo: https://github.com/jbyerline/Raspberry-Pi-Pool-Controller-Flask.git
5. Install all pip requirements with `pip3 install -r requirements.txt`
6. Create a `.env.local` file with the following:
```
MONGO_URI=mongodb://user:pass@10.1.1.66:27017/pool_data
MONGO_DB_NAME=pool_data
MONGO_COLLECTION=temperature_logs
LOG_TEMPS_EVERY_N_HOURS=2
NGROK_AUTHTOKEN=
NGROK_DOMAIN=poolservice.byerline.me
```
7. Test running locally with `python3 app.py`
8. Setup crontab to run `python3 app.py` on boot: `crontab -e` then add `@reboot cd /home/jbyerline/Raspberry-Pi-Pool-Controller-Flask && /usr/bin/python3 app.py >> logfile.log 2>&1`
9. Reboot and test, the service should be running on port 8000 and available at https://poolservice.byerline.me