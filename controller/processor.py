import sys
import json
import csv
import reverse_geocode
from os import listdir
from os.path import isfile, join

sys.path.append('../model/')
from city import City
from monitoringsample import MonitoringSample
from statisticsample import StatisticSample

def main():
    cities = list()
    monitoringSamples = list()
    statisticSamples = list()

    #Load cities paths------------------------------------------------------------------------------
    print("[INFO] Importing cities data from BikePathGenerator module")
    bikePathGenPath = "processorInput/BikePathGenerator/"
    bikePathGenFiles = [f for f in listdir(bikePathGenPath) if isfile(join(bikePathGenPath, f))]
    #Gets each city file
    for bikePathGenFile in bikePathGenFiles:
        print("  Importing "+bikePathGenFile.replace(".json","")+" data")
        cities.append(importCity(bikePathGenFile))

    #Load monitoring samples------------------------------------------------------------------------
    print("[INFO] Importing monitoring data from BikeSensor module")
    bikeSensorPath = "processorInput/BikeSensor/"
    bikeSensorFiles = [f for f in listdir(bikeSensorPath) if isfile(join(bikeSensorPath, f))]
    #Gets each MMS sample file
    for bikeSensorFile in bikeSensorFiles:
        print("  Importing "+bikeSensorFile.replace(".csv","")+" data")
        fileMonitoringSamples = importMonitoringSample(bikeSensorFile).copy()
        for fileMonitoringSample in fileMonitoringSamples:
            monitoringSamples.append(fileMonitoringSample)

    #Load statistical data-------------------------------------------------------------------------
    print("[INFO] Importing statistic data from BikeData module")
    bikeDataFile = "processorInput/BikeData/cities.csv"
    statisticSamples = importStatisticData(bikeDataFile).copy()

    print("[INFO] Processing cities monitoring samples")
    #Get new city----------------------------------------------------------------------------------
    for city in cities:
        print("  City: "+city.ID)
        statisticData = list()
        #Process statistical data------------------------------------------------------------------
        for statisticSample in statisticSamples:
            if statisticSample.city == city.ID:
                statisticData = statisticSample.data.copy()

        #Process monitoring data-------------------------------------------------------------------
        for monitoringSample in monitoringSamples:
            if monitoringSample.city == city.ID:
                for path in city.paths:
                    for stretch in path.stretches:
                        stretch.statisticData = statisticData.copy()
                        if stretch.containsPoint(monitoringSample.coordinate):
                            print("    "+monitoringSample.deviceID+"-"+monitoringSample.date+"-"+monitoringSample.time+" located in "+stretch.ID)
                            stretch.accountSample(monitoringSample.data)
                            break
        #Export processed city data------------------------------------------------------------------
        exportCity(city)

def exportCity(city):
    #File name
    fileName = "classifierInput/"+city.ID+".json"
    #File JSON data
    fileData = {}

    #Insert city weights data in JSON
    fileData['statisticDataWeights'] = city.statisticDataWeights
    fileData['monitoringDataWeights'] = city.monitoringDataWeights

    fileData['paths'] = list()
    for path in city.paths:
        pathStretches = list()

        for stretch in path.stretches:
            #Process all stretch samples
            stretch.processSamples()
            #Insert stretch data in JSON
            pathStretches.append({
                'ID': stretch.ID,
                'P1': stretch.P1,
                'P2': stretch.P2,
                'type': stretch.type,
                'direction': stretch.direction,
                'signage': stretch.signage,
                'statisticData': stretch.statisticData,
                'bikePassageNumber': stretch.bikePassageNumber,
                'averageMonitoringData': stretch.averageMonitoringData,
                'peakMonitoringData': stretch.peakMonitoringData,
                'valleyMonitoringData': stretch.valleyMonitoringData,
                'bikeWayQuality': stretch.bikeWayQuality
            })
        #Insert path data in JSON
        fileData['paths'].append({
            'ID': path.ID,
            'constructionDate': path.constructionDate,
            'maintenanceDate': path.maintenanceDate,
            'inspectionDate': path.inspectionDate,
            'inspectionFeedback': path.inspectionFeedback,
            'stretches': pathStretches
        })

    with open(fileName, 'w') as outfile:
        json.dump(fileData, outfile, indent=2)

def importCity(cityFileName):
    #City file name
    fileName = "processorInput/BikePathGenerator/"+cityFileName
    #City object
    city = None

    with open(fileName) as infile:
        #Loads city JSON file
        cityData = json.load(infile)

        #Loads city info by JSON data
        city = City(cityFileName.replace(".json", ''), cityData['statisticDataWeights'], cityData['monitoringDataWeights'])
        for pathData in cityData['paths']:
            print("    Loading "+pathData['ID']+" path")
            #Loads path info by JSON data
            path = city.insertPath(pathData['ID'], pathData['constructionDate'], pathData['maintenanceDate'], pathData['inspectionDate'], pathData['inspectionFeedback'])
            #Loads stretch info by JSON data
            for stretchData in pathData['stretches']:
                path.insertStretch(stretchData['ID'], stretchData['P1'], stretchData['P2'], stretchData['type'], stretchData['direction'], stretchData['signage'])
            print("      "+str(len(pathData['stretches']))+" stretches loaded")

    return city

def importMonitoringSample(monitoringSampleFileName):
    #Monitoring samples file name
    fileName = "processorInput/BikeSensor/"+monitoringSampleFileName
    #Monitoring samples list
    monitoringSamples = list()
    #Max of possible variables in monitoring system
    maxMonitoringData = 5
    #Identification sample data number
    nSampleIDdata = 3

    with open(fileName) as infile:
        sampleData = csv.reader(infile, delimiter='\t')
        #Variable code
        dataTypes = list()
        nSamples = 0

        #Gets device ID and date from filename
        deviceID = monitoringSampleFileName[0:monitoringSampleFileName.find("_")]
        date = monitoringSampleFileName[(monitoringSampleFileName.find("_") + 1):len(monitoringSampleFileName)]
        date = date.replace(".csv", "")
        date = date.replace("-", "/")

        for sample in sampleData:
            #First read, variables codes
            if len(dataTypes) == 0:
                dataTypes = sample.copy()
            #Samples data
            else:
                #Gets city by GPS coordinate
                coordinate = [float(sample[1]), float(sample[2])],[0, 0]
                reverseCoordinate = reverse_geocode.search(coordinate)[0]
                city = reverseCoordinate['city'] + "-" + reverseCoordinate['country_code']
                city = city.replace(' ', '_')

                #Creates a data list with each variable on its position code
                auxData = sample[nSampleIDdata:maxMonitoringData+nSampleIDdata]
                data = [None]*maxMonitoringData
                dataPosition = 0
                for index in dataTypes:
                    data[int(index) - 1] = float(auxData[dataPosition])
                    dataPosition += 1
                monitoringSamples.append(MonitoringSample(deviceID, date, sample[0], city, coordinate[0], data))
                nSamples += 1
        print("    "+str(nSamples)+" samples loaded")

    return monitoringSamples

def importStatisticData(statisticDataFileName):
    #Statistic samples file name
    statisticSamples = list()
    #Max of possible variables in statistic system
    maxStatisticData = 2
    #Identification sample data number
    nStatisticIData = 1

    with open(statisticDataFileName) as infile:
        statisticData = csv.reader(infile, delimiter='\t')
        #Variable code
        dataTypes = list()
        nSamples = 0

        for cityData in statisticData:
            #First read, variables codes
            if len(dataTypes) == 0:
                dataTypes = cityData.copy()
            #Samples data
            else:
                #Gets statistic city ID
                cityID = cityData[0]

                #Creates a data list with each variable on its position code
                auxData = cityData[nStatisticIData:maxStatisticData+nStatisticIData]
                data = [None]*maxStatisticData
                dataPosition = 0
                for index in dataTypes:
                    data[int(index) - 1] = float(auxData[dataPosition])
                    dataPosition += 1
                    
                statisticSamples.append(StatisticSample(cityID, data))
                nSamples += 1

    return statisticSamples

if __name__ == "__main__":
    main()
