from flask import Flask, render_template, Response, redirect, request
import subprocess
import os
from os import listdir
from os.path import isfile, join

app = Flask(__name__)
currentMap = None

@app.route('/')
def index():
    mapsFiles = available_maps()
    return render_template('index.html', firstMonth = mapsFiles[0], lastMonth = mapsFiles[len(mapsFiles) - 1], currentMonth = currentMap)

@app.route('/monthChange/', methods=['POST'])
def monthChange():
    monthYear = request.form['month_change_picker']
    get_map(monthYear)
    return redirect('/')

#Gets the raspberry pi private address
def get_ip_address():
    ip = str(subprocess.check_output('hostname -I', shell=True).decode('utf-8'))
    return ip

def get_map(monthYear):
    global currentMap
    try:
        os.system("cp ../controller/webapplicationInput/"+monthYear+".html templates/map.html")
        currentMap = monthYear
    except:
        None

def available_maps():
    mapsPath = "../controller/webapplicationInput/"
    mapsFiles = [f.replace('.html', '') for f in listdir(mapsPath) if isfile(join(mapsPath, f))]
    mapsFiles.sort()
    return mapsFiles

if __name__ == '__main__':
    mapsFiles = available_maps()
    get_map(mapsFiles[len(mapsFiles) - 1])

    ip = get_ip_address().replace('\n', '')
    ip = ip[0:ip.find(' ')]

    app.run(host=ip, debug=True)
