import folium
from folium.plugins import Search
import os
from os import listdir
from os.path import isfile, join
import json
from collections import namedtuple
import numpy as np
import math
from datetime import datetime

from util.city import City

rootPath = "/home/franklin/Desktop/Projetos/iBikeSafe/"

def main():
    map = folium.Map(location=[-12.280265953993627, -38.96356796067759], height = '91.5%', zoom_start=3, min_zoom = 2, max_bounds=True)
    cities = list()

    print("\n######################################################## MAP GENERATOR ##############################################\n")
    #Load cities paths------------------------------------------------------------------------------
    print("[INFO] Importing cities data from BikeWay system")
    classifierPath = rootPath+"BikeWay/outputFiles/CyclingView/"
    classifierFiles = [f for f in listdir(classifierPath) if isfile(join(classifierPath, f))]
    today = datetime.today()
    month = today.month
    if month < 10:
        month = "0"+str(month)
    monthYear = str(today.year)+"-"+month

    #Gets each city file
    nCities = 1
    for classifierFile in classifierFiles:
        print("  "+str(nCities)+". "+classifierFile.replace(".json",""))
        cities.append(importCity(classifierFile))
        nCities+=1

    print("\n---------------------------------------------------------------------------------------------------------------------\n")

    print("[INFO] Importing variables information")
    variablesInfo = importVariables()
    print("  Group 1: Environment")
    for variable in variablesInfo['monitoring']:
        print("    > "+variable[0]+" in "+variable[1])
    print("  Group 2: Infrastructure")
    for variable in variablesInfo['statistic']:
        print("    > "+variable[0]+" in "+variable[1])

    print("\n---------------------------------------------------------------------------------------------------------------------\n")

    print("[INFO] Plotting cities paths stretches on map")
    #Get new city----------------------------------------------------------------------------------
    nCities = 1
    for city in cities:
        print("  "+str(nCities)+". "+city.ID)
        for path in city.paths:
            for stretch in path.stretches:
                print("    > Plotting "+stretch.ID)
                insertBikePath(map, [stretch.P1, stretch.P2], stretch.type, stretch.direction, stretch.bikeWayQuality, getPopupLegend(stretch, variablesInfo))
        nCities+=1

    folium.plugins.LocateControl().add_to(map)
    folium.plugins.Geocoder().add_to(map)

    if not os.path.exists(rootPath+"CyclingView/BikeWay-view/modules/maps/"):
        os.makedirs(rootPath+"CyclingView/BikeWay-view/modules/maps/")

    map.save(rootPath+"CyclingView/BikeWay-view/modules/maps/"+monthYear+".html")

def importCity(cityFileName):
    #City file name
    fileName = rootPath+"BikeWay/outputFiles/CyclingView/"+cityFileName
    #City object
    city = None

    with open(fileName) as infile:
        #Loads city JSON file
        cityData = json.load(infile)

        #Loads city info by JSON data
        city = City(cityFileName.replace(".json", ''), [], [])

        pathCount = 1
        for pathData in cityData['paths']:
            print("    > Path "+str(pathCount)+": "+pathData['ID'])
            print("      - Construction date: "+pathData['constructionDate'])
            print("      - Maintenance date: "+pathData['maintenanceDate'])
            print("      - Inspection date: "+pathData['inspectionDate'])
            print("      - Creator: "+str(pathData['creator']))

            #Loads path info by JSON dataself.location
            path = city.insertPath(pathData['ID'], pathData['constructionDate'], pathData['maintenanceDate'], pathData['inspectionDate'], pathData['creator'])
            stretchCount = 1
            #Loads stretch info by JSON data
            for stretchData in pathData['stretches']:
                print("      - Stretch "+str(stretchCount)+": "+stretchData['ID'])
                print("        . Signage: "+str(stretchData['signage']))
                directionSymbol = "<-->"
                if stretchData['direction'] == 1:
                    directionSymbol = "-->"
                elif stretchData['direction'] == 2:
                    directionSymbol = "<--"
                print("        . Points connection: "+str(stretchData['P0'])+" "+directionSymbol+" "+str(stretchData['P1']))
                print("        . Statistic data: "+str(stretchData['statisticData']))
                print("        . Bike passage number: "+str(stretchData['bikePassageNumber']))
                print("        . Average monitoring variables: "+str(stretchData['averageMonitoringData']))
                print("        . Peak monitoring variables: "+str(stretchData['peakMonitoringData']))
                print("        . Valley monitoring variables: "+str(stretchData['valleyMonitoringData']))
                print("        . BikeWay Quality: "+str(stretchData['bikeWayQuality']))

                stretch = path.insertStretch(stretchData['ID'], stretchData['P0'], stretchData['P1'], stretchData['statisticData'][2], stretchData['direction'], stretchData['signage'])
                stretch.statisticData = stretchData['statisticData']
                stretch.bikePassageNumber = stretchData['bikePassageNumber']
                stretch.averageMonitoringData = stretchData['averageMonitoringData']
                stretch.peakMonitoringData = stretchData['peakMonitoringData']
                stretch.valleyMonitoringData = stretchData['valleyMonitoringData']
                stretch.bikeWayQuality = stretchData['bikeWayQuality']
                stretchCount+=1
            pathCount+=1

    #os.system("rm "+fileName)

    return city

def importVariables():
    #Variables file name
    fileName = rootPath+"CyclingView/BikeWay-view/modules/util/variables.json"
    #Variables object
    variablesInfo = None

    with open(fileName) as infile:
        #Loads city JSON file
        variablesInfo = json.load(infile)

    return variablesInfo

def getPopupLegend(stretch, variablesInfo):
    signage = "high"
    if stretch.signage == 0:
        signage = "none"
    elif stretch.signage == 1:
        signage = "low"

    popupLegend="""
    <font size="2"><b>{id}</b></font><br>
    <font size="1.5"><b>Size</b></font></br>
    <font size="1">{size}m</font></br>
    <font size="1.5"><b>Signage</b></font></br>
    <font size="1">{signage}</font></br>
    <font size="1.5"><b>Monitoring samples</b></font></br>
    <font size="1">{bikePassageNumber}</font></br>
    """.format(id=stretch.ID, size=stretch.getDistance(), signage=signage, bikePassageNumber=stretch.bikePassageNumber)

    for index in range(len(variablesInfo["monitoring"])):
        average = "--"
        peak = "--"
        valley = "--"
        try:
            average = int(stretch.averageMonitoringData[index])
            peak = int(stretch.peakMonitoringData[index])
            valley = int(stretch.valleyMonitoringData[index])
        except:
            None

        popupLegend += """
        <font size="1.5"><b>{name}</b></font></br>
        <font size="1">{average}{unit}&ensp; <i>(Min: {valley} &nbsp; Max: {peak})</i></font></br>
        """.format(name = variablesInfo["monitoring"][index][0], average = average, peak = peak
        , valley = valley, unit = variablesInfo["monitoring"][index][1])

    for index in range(len(variablesInfo["statistic"]) - 1):
        statistic = "--"
        try:
            statistic = int(stretch.statisticData[index])
        except:
            None

        popupLegend += """<font size="1.5"><b>{name}</b></br>{value}{unit}</font><br>
        """.format(name = variablesInfo["statistic"][index][0], value = statistic, unit = variablesInfo["statistic"][index][1])

    return popupLegend

def insertBikePath(map, path, type, direction, quality , popupLegend):
    color = None
    if quality == 4:
        color = 'blue'
    elif quality == 3:
        color = 'green'
    elif quality == 2:
        color = 'yellow'
    elif quality == 1:
        color = 'orange'
    elif quality == 0:
        color = 'red'
    else:
        color = 'grey'

    dash_array = 0
    if type == 0:
        dash_array = 20
    elif type == 1:
        dash_array = 10

    popup = folium.Popup(popupLegend, max_width=180,min_width=180)
    folium.PolyLine(path, color=color,  weight=8, opacity=0.5, popup=popup, dash_array=dash_array).add_to(map)

    arrows = list()
    if direction == 0:
        arrows = getArrows([path[0],path[1]], color)
        arrows = arrows + getArrows([path[1],path[0]], color)
    elif direction == 1:
        arrows = getArrows([path[0],path[1]], color)
    elif direction == 2:
        arrows = getArrows([path[1],path[0]], color)

    for arrow in arrows:
        arrow.add_to(map)

def getArrows(locations, color):
    size = 3
    n_arrows = 5

    Point = namedtuple('Point', field_names=['lat', 'lon'])

    # creating point from Point named tuple
    point1 = Point(locations[0][0], locations[0][1])
    point2 = Point(locations[1][0], locations[1][1])

    # calculate the rotation required for the marker.
    #Reducing 90 to account for the orientation of marker
    # Get the degree of rotation
    angle = get_angle(point1, point2) - 90

    # get the evenly space list of latitudes and longitudes for the required arrows

    arrow_latitude = np.linspace(point1.lat, point2.lat, n_arrows + 2)[1:n_arrows+1]
    arrow_longitude = np.linspace(point1.lon, point2.lon, n_arrows + 2)[1:n_arrows+1]

    final_arrows = []

    #creating each "arrow" and appending them to our arrows list
    for points in zip(arrow_latitude, arrow_longitude):
        final_arrows.append(folium.RegularPolygonMarker(location=points, color = color, fill_color=color, number_of_sides=3, radius=size, rotation=angle))
    return final_arrows

def get_angle(p1, p2):
    longitude_diff = np.radians(p2.lon - p1.lon)

    latitude1 = np.radians(p1.lat)
    latitude2 = np.radians(p2.lat)

    x_vector = np.sin(longitude_diff) * np.cos(latitude2)
    y_vector = (np.cos(latitude1) * np.sin(latitude2)
        - (np.sin(latitude1) * np.cos(latitude2)
        * np.cos(longitude_diff)))
    angle = np.degrees(np.arctan2(x_vector, y_vector))

    # Checking and adjustring angle value on the scale of 360
    if angle < 0:
        return angle + 360
    return angle

if __name__ == "__main__":
    main()
