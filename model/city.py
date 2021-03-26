from path import Path

class City:
    def __init__(self, ID, statisticDataWeights, monitoringDataWeights):
        #String in 'Feira_de_Santana-BR' format
        self.ID = ID
        #City bike paths list
        self.paths = list()
        #BikeWay classifier statistic group weights list
        self.statisticDataWeights = statisticDataWeights.copy()
        #BikeWay classifier monitoring group weights list
        self.monitoringDataWeights = monitoringDataWeights.copy()

    def insertPath(self, ID, constructionDate, maintenanceDate, inspectionDate, inspectionFeedback):
        #Create new bike path object
        path = Path(ID, constructionDate, maintenanceDate, inspectionDate, inspectionFeedback)
        #Add in paths list
        self.paths.append(path)
        return path
