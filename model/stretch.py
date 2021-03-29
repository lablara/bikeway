from shapely.geometry import LineString as shls
from shapely.geometry import Point as shpt
import haversine as hs
from haversine import Unit

class Stretch:
    def __init__(self, ID, P1, P2, type, direction, signage):
        #String in 'Feira_de_Santana-BR-P1-S1' format
        self.ID = ID
        #Float array [0.0, 0.0]
        self.P1 = P1
        #Float array [0.0, 0.0]
        self.P2 = P2
        #Int value: 0 - none, 1 - shared, 2 - isolated
        self.type = type
        #Int value: 0 - P1 <--> P2, 1 - P1 --> P2, 2 - P1 <-- P2
        self.direction = direction
        #Int value: 0 - none, 1 - little signage, 2 - lots of signage
        self.signage = signage
        #Int array with number of statistic data in a month [0, 0, ..., 0]
        self.statisticData = list()
        #Int value showing how many times cyclists passed on the stretch
        self.bikePassageNumber = 0
        #Float array with each average monitoring data collected in a month [0.0, 0.0, ..., 0.0]
        self.averageMonitoringData = list()
        #Float array with each peak value of monitoring data collected in a month [0.0, 0.0, ..., 0.0]
        self.peakMonitoringData = list()
        #Float array with each valley value of monitoring data collected in a month [0.0, 0.0, ..., 0.0]
        self.valleyMonitoringData = list()
        #Int that classifies the bike path by the BikeWay: 0 - VB, 1 - B, 2 - M, 3 - G, 4 - VG
        self.bikeWayQuality = None

        #All monitoring data detected on stretch
        self.monitoringData = list()

    def containsPoint(self, point):
        #Gets stretch line
        stretchLine = shls([self.P1, self.P2])
        #Gets distance between point and stretch line
        pointLineDistance = shpt(point).distance(stretchLine)

        #Checks if distance is short
        if pointLineDistance <  0.00010061046804398176:
            return True
        return False

    def getDistance(self, P1 = None, P2 = None):
        #Stretch distance
        if P1 == None or P2 == None:
            P1 = self.P1
            P2 = self.P2
        return int(hs.haversine(P1, P2, unit=Unit.METERS))


    def accountSample(self, data):
        #First account then starts all lists
        if self.bikePassageNumber  == 0:
            maxMonitoringData = len(data)
            self.averageMonitoringData = [0.0]*maxMonitoringData
            self.modeMonitoringData = [0.0]*maxMonitoringData
            self.peakMonitoringData = [0.0]*maxMonitoringData
            self.valleyMonitoringData = [float("inf")]*maxMonitoringData

        #Account sample
        self.bikePassageNumber += 1
        self.monitoringData.append(data)

    def processSamples(self):
        #Check all sample collected
        for sampleData in self.monitoringData:
            #Check each variable for current sample
            for index in range(len(sampleData)):
                #Variable sum for average
                self.averageMonitoringData[index] = self.averageMonitoringData[index] + sampleData[index]

                #Gets peak value for variable
                if sampleData[index] > self.peakMonitoringData[index]:
                    self.peakMonitoringData[index] = sampleData[index]

                #Gets valley value for variable
                if sampleData[index] < self.valleyMonitoringData[index]:
                    self.valleyMonitoringData[index] = sampleData[index]

        #Gets average for each variable by sum
        self.averageMonitoringData = [avgVariableData/float(self.bikePassageNumber) for avgVariableData in self.averageMonitoringData]
