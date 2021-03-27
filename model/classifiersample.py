class ClassifierSample:
    def __init__(self, stretchID ,monitoringDataWeights, statisticDataWeights, monitoringData, statisticData, type):
        self.monitoringDataWeights = monitoringDataWeights.copy()
        self.statisticDataWeights = statisticDataWeights.copy()
        self.stretchID = stretchID

        self.data = list()
        for monitoringVariableData in monitoringData:
            self.data.append(monitoringVariableData)

        for statisticVariableData in statisticData:
            self.data.append(statisticVariableData)

        if type == 0:
            self.data.append("None")
        elif type == 1:
            self.data.append("Shared")
        elif type == 2:
            self.data.append("Isolated")
