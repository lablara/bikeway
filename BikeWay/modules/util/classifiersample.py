class ClassifierSample:
    def __init__(self, stretchID ,monitoringDataWeights, statisticDataWeights, monitoringData, statisticData):
        self.monitoringDataWeights = monitoringDataWeights.copy()
        self.statisticDataWeights = statisticDataWeights.copy()
        self.stretchID = stretchID

        self.data = list()
        for monitoringVariableData in monitoringData:
            self.data.append(monitoringVariableData)

        for statisticVariableData in statisticData:
            self.data.append(statisticVariableData)
