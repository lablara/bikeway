import json
import csv
from os import listdir
from os.path import isfile, join
import reverse_geocode
import matplotlib.pyplot as plt
from datetime import datetime

from modules.util.city import City
from modules.util.statisticsample import StatisticSample
from modules.util.monitoringsample import MonitoringSample

class Processor:
    #################### PUBLIC FUNCTIONS ######################################
    def __init__(self, rootPath):
        self.cities = list()
        self.monitoringSamples = list()
        self.statisticSamples = list()
        self.rootPath = rootPath 

    def importData(self):
        #Load cities paths------------------------------------------------------
        print("[INFO] Importing cities data from BikePathGen sub-system")
        bikePathGenPath = self.rootPath+"inputFiles/BikePathGen/"
        bikePathGenFiles = [f for f in listdir(bikePathGenPath) if isfile(join(bikePathGenPath, f))]
        #Gets each city file
        nCities = 1
        for bikePathGenFile in bikePathGenFiles:
            print("  "+str(nCities)+". "+bikePathGenFile.replace(".json",""))
            self.cities.append(self.importBikePathGenFile(bikePathGenFile))
            nCities+=1
        print("\n---------------------------------------------------------------------------------------------------------------------\n")

        #Load statistical data-------------------------------------------------------------------------
        print("[INFO] Importing statistic data from BikeData sub-system")
        bikeDataFile = self.rootPath+"inputFiles/BikeData/cities.csv"
        self.statisticSamples = self.importStatisticData(bikeDataFile).copy()

        print("\n---------------------------------------------------------------------------------------------------------------------\n")

        #Load monitoring samples------------------------------------------------------------------------
        print("[INFO] Importing monitoring samples from BikeSensor module")
        bikeSensorPath = self.rootPath+"inputFiles/BikeSensor/"
        bikeSensorFiles = [f for f in listdir(bikeSensorPath) if isfile(join(bikeSensorPath, f))]
        #Gets each MMS sample file
        nCities = 1
        for bikeSensorFile in bikeSensorFiles:
            print("  "+str(nCities)+". "+bikeSensorFile.replace(".csv",""))
            fileMonitoringSamples = self.importMonitoringSample(bikeSensorFile).copy()
            for fileMonitoringSample in fileMonitoringSamples:
                self.monitoringSamples.append(fileMonitoringSample)
        print("\n---------------------------------------------------------------------------------------------------------------------\n")

        #Delete all input files------------------------------------------------------------------------
        #os.system("sudo rm -r inputFiles/")

    def processData(self):
        print("[INFO] Processing cities monitoring samples")
        #Get new city----------------------------------------------------------------------------------
        nCities = 1
        for city in self.cities:
            print("  "+str(nCities)+". "+city.ID)
            statisticData = list()
            detectedPoints = list()
            undetectedPoints = list()

            #Process statistical data------------------------------------------------------------------
            for statisticSample in self.statisticSamples:
                if statisticSample.city == city.ID:
                    statisticData = statisticSample.data.copy()

            #Process monitoring data-------------------------------------------------------------------
            nSamples = 1
            for monitoringSample in self.monitoringSamples:
                if monitoringSample.city == city.ID:
                    nStretches = 1
                    for path in city.paths:
                        for stretch in path.stretches:
                            stretch.statisticData = statisticData.copy()

                            if stretch.containsPoint(monitoringSample.coordinate):
                                detectedPoints.append(monitoringSample.coordinate)
                                print("    > Sample "+str(nSamples)+": "+monitoringSample.deviceID+"-"+monitoringSample.date+"-"+monitoringSample.time)
                                print("      - Stretch "+str(nStretches)+": "+stretch.ID)
                                stretch.accountSample(monitoringSample.data)
                                break
                            else:
                                undetectedPoints.append(monitoringSample.coordinate)
                            nStretches+=1
                nSamples+=1

            #Export processed city data------------------------------------------------------------------
            self.exportCity(city)
            self.exportCityGraph(city.ID,city.getPathsPoints(), detectedPoints, undetectedPoints)
            nCities+=1

    #################### PRIVATE FUNCTIONS #####################################
    def importBikePathGenFile(self, cityFileName):
        #City file name
        fileName = self.rootPath+"inputFiles/BikePathGen/"+cityFileName
        #City object
        city = None

        with open(fileName) as infile:
            #Loads city JSON file
            cityData = json.load(infile)

            #Loads city info by JSON data
            city = City(cityFileName.replace(".json", ''), cityData['statisticDataWeights'], cityData['monitoringDataWeights'])
            print("    > Monitoring weights: "+str(cityData['monitoringDataWeights']))
            print("    > Statistic weights: "+str(cityData['statisticDataWeights']))

            pathCount = 1
            for pathData in cityData['paths']:
                print("    > Path "+str(pathCount)+": "+pathData['ID'])
                print("      - Construction date: "+pathData['constructionDate'])
                print("      - Maintenance date: "+pathData['maintenanceDate'])
                print("      - Inspection date: "+pathData['inspectionDate'])
                print("      - Creator: "+str(pathData['creator']))

                #Loads path info by JSON data
                path = city.insertPath(pathData['ID'], pathData['constructionDate'], pathData['maintenanceDate'], pathData['inspectionDate'], pathData['creator'])
                stretchCount = 1
                #Loads stretch info by JSON data
                for stretchData in pathData['stretches']:
                    print("      - Stretch "+str(stretchCount)+": "+stretchData['ID'])
                    print("        . Type: "+str(stretchData['type']))
                    print("        . Signage: "+str(stretchData['signage']))
                    directionSymbol = "<-->"
                    if stretchData['direction'] == 1:
                        directionSymbol = "-->"
                    elif stretchData['direction'] == 2:
                        directionSymbol = "<--"
                    print("        . Points connection: "+str(stretchData['P0'])+" "+directionSymbol+" "+str(stretchData['P1']))

                    path.insertStretch(stretchData['ID'], stretchData['P0'], stretchData['P1'], stretchData['type'], stretchData['direction'], stretchData['signage'])
                    stretchCount+=1
                pathCount+=1

        return city

    def importStatisticData(self, statisticDataFileName):
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
            nSample = 1

            for cityData in statisticData:
                #First read, variables codes
                if len(dataTypes) == 0:
                    dataTypes = cityData.copy()
                    dataTypes = [int(type) for type in dataTypes]
                    print("  Variables types: "+str(dataTypes))
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

                    print("  "+str(nSample)+". "+cityID)
                    print("    Data: "+str(data))
                    statisticSamples.append(StatisticSample(cityID, data))
                    nSample += 1

        return statisticSamples

    def importMonitoringSample(self, monitoringSampleFileName):
        #Monitoring samples file name
        fileName = self.rootPath+"inputFiles/BikeSensor/"+monitoringSampleFileName
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
            nSample = 1

            #Gets device ID and date from filename
            deviceID = monitoringSampleFileName[0:monitoringSampleFileName.find("_")]
            date = monitoringSampleFileName[(monitoringSampleFileName.find("_") + 1):len(monitoringSampleFileName)]
            date = date.replace(".csv", "")
            date = date.replace("-", "/")

            for sample in sampleData:
                #First read, variables codes
                if len(dataTypes) == 0:
                    dataTypes = sample.copy()
                    dataTypes = [int(type) for type in dataTypes]
                    print("    > Variables types: "+str(dataTypes))
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

                    print("    > Sample "+str(nSample)+": "+sample[0])
                    print("      - Coordinate: "+str(coordinate[0]))
                    print("      - City: "+city)
                    print("      - Data: "+str(data))
                    monitoringSamples.append(MonitoringSample(deviceID, date, sample[0], city, coordinate[0], data))
                    nSample += 1

        return monitoringSamples

    def exportCity(self, city):
        #File name
        fileName = self.rootPath+"processedFiles/classifierInput/"+city.ID+".json"
        #File JSON data
        fileData = {}

        #Insert city weights data in JSON
        fileData['statisticDataWeights'] = city.statisticDataWeights
        fileData['monitoringDataWeights'] = city.monitoringDataWeights

        fileData['paths'] = list()
        for path in city.paths:
            pathStretches = list()

            for stretch in path.stretches:
                stretch.statisticData.append(stretch.type)

                #Process all stretch samples
                stretch.processSamples()
                #Insert stretch data in JSON
                pathStretches.append({
                    'ID': stretch.ID,
                    'P0': stretch.P1,
                    'P1': stretch.P2,
                    'direction': stretch.direction,
                    'signage': stretch.signage,
                    'statisticData': stretch.statisticData,
                    'bikePassageNumber': stretch.bikePassageNumber,
                    'averageMonitoringData': stretch.averageMonitoringData,
                    'peakMonitoringData': stretch.peakMonitoringData,
                    'valleyMonitoringData': stretch.valleyMonitoringData
                })
            #Insert path data in JSON
            fileData['paths'].append({
                'ID': path.ID,
                'constructionDate': path.constructionDate,
                'maintenanceDate': path.maintenanceDate,
                'inspectionDate': path.inspectionDate,
                'creator': path.creator,
                'stretches': pathStretches
            })

        with open(fileName, 'w') as outfile:
            json.dump(fileData, outfile, indent=2)

    def exportCityGraph(self, cityID, cityPathsPoints, detectedPoints, undetectedPoints):
        for cityPathPoints in cityPathsPoints:
            x = list()
            y = list()
            for cityPathPoint in cityPathPoints:
                x.append(cityPathPoint[1])
                y.append(cityPathPoint[0])
            plt.plot(x, y, marker = 'o', color = 'black')

        for undetectedPoint in undetectedPoints:
            plt.plot(undetectedPoint[1], undetectedPoint[0], marker = 'o', color = 'red')

        for detectedPoint in detectedPoints:
            plt.plot(detectedPoint[1], detectedPoint[0], marker = 'o', color = 'green')

        today = datetime.today()
        monthYear = str(today.month)+"-"+str(today.year)
        fileName = self.rootPath+"processedFiles/belongingGraphs/"+cityID+"_"+monthYear+".png"

        plt.legend(loc="upper left")
        plt.title(cityID+"_"+monthYear)
        plt.xlabel('Longitude (°)')
        plt.ylabel('Latitude (°)')
        plt.grid()
        plt.savefig(fileName)
        plt.clf()
