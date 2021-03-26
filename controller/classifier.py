# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import csv

def main():
    #µg/m³, dB(A), uV, C, lux, Occurrences/month, Occurrences/month, (none, shared, isolated)
    type = list()
    input = list()
    output = list()

    with open('input.csv') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',')
        firstLine = True
        for row in filereader:
            if firstLine is True:
                firstLine = False
                type = row
            else:
                input = list()
                for data in row:
                    try:
                        input.append(float(data))
                    except:
                        input.append(str(data))


                print("[INFO] Input")
                for index in range(8):
                    print ("  ("+str(index)+") "+str(input[index])+" "+type[index])
                print("")

                variables_levels = computeLevels(input)
                M1_level, M2_level = computeMean(variables_levels)
                output.append(computeQuality(M1_level, M2_level))

                print("--------------------------------------------------------")

        filewriter = open('output.csv', 'w')
        with filewriter:
            writer = csv.writer(filewriter)
            writer.writerow(['M1','M2', 'BikeWay', 'Color'])
            for row in output:
                writer.writerow(row)


def computeGaussianFunction(x, sigma, u):
    return np.exp(-np.power(x - u, 2.) / (2 * np.power(sigma, 2.)))

def computeLevels(input):
    print("[INFO] Compute variables levels")
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
        print("  ("+str(index)+") "+str(y)+",\tsigma = "+str(sigma)+" u = "+str(u))

    #Get literal level
    x = input[7]
    if x == "None":
        y = 1.0
    elif x == "Shared":
        y = 0.5
    elif x == "Isolated":
        y = 0.0
    output.append(y)
    print("  (7) "+str(y))
    print("")

    return output

def computeMean(input):
    print("[INFO] Compute mean")
    #Metric groups
    M1_values = input[0:5]
    M2_values = input[5:8]

    #Groups
    #µg/m³, dB(A), uV, C, lux
    M1_weights = [0.2, 0.2, 0.2, 0.2, 0.2]
    #accidents/month, occurrences/month, lane
    M2_weights = [0.333333, 0.333333, 0.333333]

    M1_level = 0
    i = 0
    print("  M1 Group")
    for y in M1_values:
        print ("  ("+str(i)+") "+str(y)+" * "+str(M1_weights[i])+" = "+"{:.2f}".format(y * M1_weights[i]))
        M1_level = M1_level + (y * M1_weights[i])
        i = i + 1
    M1_level = float("{:.2f}".format(M1_level))
    print("    Level: "+str(M1_level))

    M2_level = 0
    i = 0
    print("  M2 Group")
    for y in M2_values:
        print ("  ("+str(i+5)+") "+str(y)+" * "+str(M2_weights[i])+" = "+"{:.2f}".format(y * M2_weights[i]))
        M2_level = M2_level + (y * M2_weights[i])
        i = i + 1
    M2_level = float("{:.2f}".format(M2_level))
    print("    Level: "+str(M2_level))
    print("")

    return (M1_level, M2_level)

def computeQuality(M1_level, M2_level):
    print("[INFO] Compute quality")

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

    M1_name = numericToName(M1_level)
    M2_name = numericToName(M2_level)

    BikeWay_name = "Very Bad"
    BikeWay_color = "Red"
    if (M1_name == "Bad" and (M2_name == 'Bad' or M2_name == 'Moderate')) or (M1_name == "Moderate" and M2_name == 'Bad'):
        BikeWay_name = "Bad"
        BikeWay_color = "Orange"
    elif (M1_name == "Bad" and (M2_name == "Good" or M2_name == "Very Good" )) or (M1_name == "Moderate" and M2_name == "Moderate") or ((M1_name == "Good" or M1_name == "Very Good") and M2_name == "Bad"):
        BikeWay_name = "Moderate"
        BikeWay_color = "Yellow"
    elif (M1_name == "Moderate" and (M2_name == "Good" or M2_name == "Very Good")) or (M1_name == "Good" and (M2_name == "Moderate" or M2_name == "Good")) or (M1_name == "Very Good" and M2_name == "Moderate"):
        BikeWay_name = "Good"
        BikeWay_color = "Green"
    elif (M1_name == "Good" or M1_name == "Very Good") and (M2_name == "Good" or M2_name == "Very Good"):
        BikeWay_name = "Very Good"
        BikeWay_color = "Blue"

    print("  M1 level = "+M1_name)
    print("  M2 level = "+M2_name)
    print("  BikeWay level = "+BikeWay_name+"/"+BikeWay_color+" ("+str(BikeWay_level)+")")

    #BikeWay.view(sim=BikeWay_simulator)
    #plt.show()

    return M1_name, M2_name, BikeWay_name, BikeWay_color

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


if __name__ == "__main__":
    main()
