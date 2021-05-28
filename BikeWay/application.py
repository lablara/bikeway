import os
from modules.processor import Processor
from modules.classifier import Classifier

def main():
    rootPath = "/home/franklin/Desktop/Projetos/iBikeSafe/BikeWay/"

    #CREATES FOLDERS TO SAVE FILES
    if not os.path.exists(rootPath+'inputFiles/'):
        os.makedirs(rootPath+'inputFiles/')
        os.makedirs(rootPath+'inputFiles/BikePathGen/')
        os.makedirs(rootPath+'inputFiles/BikeSensor/')
        os.makedirs(rootPath+'inputFiles/BikeData/')

    if not os.path.exists(rootPath+'processedFiles/'):
        os.makedirs(rootPath+'processedFiles/')
        os.makedirs(rootPath+'processedFiles/classifierInput/')
        os.makedirs(rootPath+'processedFiles/belongingGraphs/')

    if not os.path.exists(rootPath+'outputFiles/'):
        os.makedirs(rootPath+'outputFiles/')
        os.makedirs(rootPath+'outputFiles/CyclingView/')

    #DOWNLOAD ALL FILES PRO SUB-SYSTEMS DATABASES

    print("\n######################################################## PROCESSOR ##############################################\n")
    #DATA PROCESSING ROUTINE
    processor = Processor(rootPath)
    processor.importData()
    processor.processData()

    print("\n######################################################## CLASSIFIER ##############################################\n")
    #PATHS CLASSIFICATION ROUTINE
    classifier = Classifier(rootPath)
    classifier.importData()


if __name__ == "__main__":
    main()
