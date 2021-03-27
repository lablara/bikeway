# coding: utf-8
import sys
import json
from datetime import datetime
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl

sys.path.append('../model/')
from city import City
from classifiersample import ClassifierSample


def main():
    cities = list()
    print("\n######################################################## CLASSIFIER ##############################################\n")
    #Load cities paths------------------------------------------------------------------------------
    print("[INFO] Importing cities data from BikeWay Processor")
    bikePathGenPath = "processorInput/BikePathGenerator/"
    bikePathGenFiles = [f for f in listdir(bikePathGenPath) if isfile(join(bikePathGenPath, f))]
    #Gets each city file
    nCities = 1
    for bikePathGenFile in bikePathGenFiles:
        print("  "+str(nCities)+". "+bikePathGenFile.replace(".json",""))
        cities.append(importCity(bikePathGenFile))
        nCities+=1

    print("\n---------------------------------------------------------------------------------------------------------------------\n")

    print("[INFO] Classifying cities paths stretches")
    #Get new city----------------------------------------------------------------------------------
    nCities = 1
    for city in cities:
        print("  "+str(nCities)+". "+city.ID)
        print("    > Monitoring weights: "+str(city.monitoringDataWeights))
        print("    > Statistic weights: "+str(city.statisticDataWeights))

        nPaths = 1
        for path in city.paths:
            print("    > Path "+str(nPaths)+": "+path.ID)
            nStretches = 1
            for stretch in path.stretches:
                print("      - Stretch "+str(nStretches)+": "+stretch.ID)
                classifierSample = ClassifierSample(stretch.ID ,city.monitoringDataWeights, city.statisticDataWeights, stretch.averageMonitoringData, stretch.statisticData, stretch.type)
                print("        . Classifier input: "+str(classifierSample.data))
                print("        . Input levels: ")
                sampleLevels = computeLevels(classifierSample.data)
                M1Level, M2Level = computeMean(sampleLevels, city.monitoringDataWeights, city.statisticDataWeights)
                print("        . Stretch quality")
                bikeWayQuality = computeQuality(M1Level, M2Level)
                stretch.bikeWayQuality = bikeWayQuality
                nStretches+=1
            nPaths+=1
        exportCity(city)
        nCities += 1

def computeLevels(input):
    output = list()
    xmin = 0
    xmax = 0
    sigma = 0
    u = 0
    for index in range(7):
        x = input[index]
        #M1.1 - Air Pollution; x = [0:70] µg/m³
        if index == 0:
            #Data pre-processing
            xmin, xmax = [0,70]
            #Gaussian definition
            sigma, u = [40,70]
        #M1.2 - Noise Pollution; x = [0:65] dB(A)
        elif index == 1:
            #Data pre-processing
            xmin, xmax = [0,65]
            #Gaussian definition
            sigma, u = [6,65]
        #M1.3 - UV Radiation; x = [0:11] uV
        elif index == 2:
            #Data pre-processing
            xmin, xmax = [0,11]
            #Gaussian definition
            sigma, u = [4,11]
        #M1.4 - Temperature; x = [-10:52] C
        elif index == 3:
            #Data pre-processing
            xmin, xmax = [-10,52]
            #1st Gaussian definition
            if (x >= -10 and x < 10) or x < -10:
                sigma, u = [7,-10]
            #2nd Gaussian definition
            elif (x >= 10 and x <= 52) or x > 52:
                sigma, u = [12,52]
        #M1.5 - Luminosity; x = [0:32000] lux
        elif index == 4:
            #Data pre-processing
            xmin, xmax = [0,32000]
            #Gaussian definition
            sigma, u = [15000,32000]
        #M2.2 - Accidents; x = [0:20] Occurrences/month
        elif index == 5:
            #Data pre-processing
            xmin, xmax = [0,20]
            #Gaussian definition
            sigma, u = [6,20]
        #M2.3 - Assaults and murders; x = [0:8] Occurrences/month
        elif index == 6:
            #Data pre-processing
            xmin, xmax = [0,8]
            #Gaussian definition
            sigma, u = [3,8]

        #Normalize input
        if x < xmin:
            x = xmin
        elif x > xmax:
            x = xmax

        #Get gaussian levels and translate
        y = float("{:.2f}".format(computeGaussianFunction(x, sigma, u)))
        output.append(y)
        print("          ["+str(index+1)+"] "+str(x)+" -> "+str(y)+"\t sigma = "+str(sigma)+" u = "+str(u))

    #Get literal level
    x = input[7]
    if x == "None":
        y = 1.0
    elif x == "Shared":
        y = 0.5
    elif x == "Isolated":
        y = 0.0
    output.append(y)
    print("          [8] "+x+" -> "+str(y))

    return output

def computeGaussianFunction(x, sigma, u):
    return np.exp(-np.power(x - u, 2.) / (2 * np.power(sigma, 2.)))

def computeMean(input, M1_weights, M2_weights):
    #Metric groups
    M1_values = input[0:5]
    M2_values = input[5:8]

    M1_level = 0
    i = 0
    print("        . M1: Monitoring data")
    for y in M1_values:
        print ("          ["+str(i+1)+"] "+str(y)+" * "+str(M1_weights[i])+" = "+"{:.2f}".format(y * M1_weights[i]))
        M1_level = M1_level + (y * M1_weights[i])
        i = i + 1
    M1_level = float("{:.2f}".format(M1_level))
    print("          Level: "+str(M1_level))

    M2_level = 0
    i = 0
    print("        . M2: Infrastructure data")
    for y in M2_values:
        print ("          ["+str(i+6)+"] "+str(y)+" * "+str(M2_weights[i])+" = "+"{:.2f}".format(y * M2_weights[i]))
        M2_level = M2_level + (y * M2_weights[i])
        i = i + 1
    M2_level = float("{:.2f}".format(M2_level))
    print("          Level: "+str(M2_level))

    return (M1_level, M2_level)

def computeQuality(M1_level, M2_level):
    #INPUT-------------------------------------------------------------------------
    M1 = ctrl.Antecedent(np.arange(0, 1.0, 0.01), 'M1 level')
    M2 = ctrl.Antecedent(np.arange(0, 1.0, 0.01), 'M2 level')

    #OUTPUT-------------------------------------------------------------------------
    BikeWay = ctrl.Consequent(np.arange(0, 1.0, 0.01), 'BikeWay')

    #SET DEFINITION-----------------------------------------------------------------
    M1.automf(names=['Very Good', 'Good', 'Moderate', 'Bad', 'Very Bad'])
    M2.automf(names=['Very Good', 'Good', 'Moderate', 'Bad', 'Very Bad'])
    BikeWay.automf(names=['Very Good', 'Good', 'Moderate', 'Bad', 'Very Bad'])

    #RULES--------------------------------------------------------------------------
    rule1 = ctrl.Rule(M1['Very Bad'] | M2['Very Bad'], BikeWay['Very Bad'])
    rule2 = ctrl.Rule(((M1['Bad'] & (M2['Bad'] | M2['Moderate'])) | (M1['Moderate'] & M2['Bad'])), BikeWay['Bad'])
    rule3 = ctrl.Rule(((M1['Bad'] & (M2['Good'] | M2['Very Good'])) | (M1['Moderate'] & M2['Moderate']) | ((M1['Good'] | M1['Very Good']) & M2['Bad'])), BikeWay['Moderate'])
    rule4 = ctrl.Rule(((M1['Moderate'] & (M2['Good'] | M2['Very Good'])) | (M1['Good'] & (M2['Moderate'] | M2['Good'])) | (M1['Very Good'] & M2['Moderate'])), BikeWay['Good'])
    rule5 = ctrl.Rule(((M1['Good'] | M1['Very Good']) & (M2['Good'] | M2['Very Good'])), BikeWay['Very Good'])

    BikeWay_control = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
    BikeWay_simulator = ctrl.ControlSystemSimulation(BikeWay_control)

    BikeWay_simulator.input['M1 level'] = M1_level
    BikeWay_simulator.input['M2 level'] = M2_level
    BikeWay_simulator.compute()
    BikeWay_level = BikeWay_simulator.output['BikeWay']

    M1Quality = numericToName(M1_level)
    M2Quality = numericToName(M2_level)

    bikeWayQuality = "Very Bad"
    if (M1Quality == "Bad" and (M2Quality == 'Bad' or M2Quality == 'Moderate')) or (M1Quality == "Moderate" and M2Quality == 'Bad'):
        bikeWayQuality = "Bad"
    elif (M1Quality == "Bad" and (M2Quality == "Good" or M2Quality == "Very Good" )) or (M1Quality == "Moderate" and M2Quality == "Moderate") or ((M1Quality == "Good" or M1Quality == "Very Good") and M2Quality == "Bad"):
        BikeWay_name = "Moderate"
    elif (M1Quality == "Moderate" and (M2Quality == "Good" or M2Quality == "Very Good")) or (M1Quality == "Good" and (M2Quality == "Moderate" or M2Quality == "Good")) or (M1Quality == "Very Good" and M2Quality == "Moderate"):
        BikeWay_name = "Good"
    elif (M1Quality == "Good" or M1Quality == "Very Good") and (M2Quality == "Good" or M2Quality == "Very Good"):
        BikeWay_name = "Very Good"

    print("          M1 quality = "+M1Quality)
    print("          M2 quality = "+M2Quality)
    print("          BikeWay quality = "+bikeWayQuality+" ("+str(BikeWay_level)+")")

    #BikeWay.view(sim=BikeWay_simulator)
    #plt.show()

    return encodeQuality(bikeWayQuality)

def numericToName(value):
    limits = [0.12375, 0.37125, 0.61875, 0.86625]

    name = "Very Good"
    if value > limits[0] and value <= limits[1]:
        name = "Good"
    elif value > limits[1] and value <= limits[2]:
        name = "Moderate"
    elif value > limits[2] and value <= limits[3]:
        name = "Bad"
    elif value > limits[3]:
        name = "Very Bad"

    return name

def encodeQuality(quality):
    code = 4
    if quality == "Very Bad":
        code = 0
    elif quality == "Bad":
        code = 1
    elif quality == "Moderate":
        code = 2
    elif quality == "Good":
        code = 3
    return code

def importCity(cityFileName):
    #City file name
    fileName = "classifierInput/"+cityFileName
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
            print("      - Inspection feedback: "+str(pathData['inspectionFeedback']))

            #Loads path info by JSON data
            path = city.insertPath(pathData['ID'], pathData['constructionDate'], pathData['maintenanceDate'], pathData['inspectionDate'], pathData['inspectionFeedback'])
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
                print("        . Points connection: "+str(stretchData['P1'])+" "+directionSymbol+" "+str(stretchData['P2']))
                print("        . Statistic data: "+str(stretchData['statisticData']))
                print("        . Bike passage number: "+str(stretchData['bikePassageNumber']))
                print("        . Average monitoring variables: "+str(stretchData['averageMonitoringData']))
                print("        . Peak monitoring variables: "+str(stretchData['peakMonitoringData']))
                print("        . Valley monitoring variables: "+str(stretchData['valleyMonitoringData']))

                stretch = path.insertStretch(stretchData['ID'], stretchData['P1'], stretchData['P2'], stretchData['type'], stretchData['direction'], stretchData['signage'])
                stretch.statisticData = stretchData['statisticData']
                stretch.bikePassageNumber = stretchData['bikePassageNumber']
                stretch.averageMonitoringData = stretchData['averageMonitoringData']
                stretch.peakMonitoringData = stretchData['peakMonitoringData']
                stretch.valleyMonitoringData = stretchData['valleyMonitoringData']

                stretchCount+=1
            pathCount+=1

    os.system("sudo rm "+fileName)

    return city

def exportCity(city):
    #File name
    today = datetime.today()
    monthYear = str(today.month)+"-"+str(today.year)
    fileName = "mapgeneratorInput/"+city.ID+"_"+monthYear+".json"
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

if __name__ == "__main__":
    main()
