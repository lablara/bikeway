from stretch import Stretch

class Path:
    def __init__(self, ID, constructionDate, maintenanceDate, inspectionDate, creator):
        #String in 'Feira_de_Santana-BR-P1' format
        self.ID = ID
        #String with bike path construction date
        self.constructionDate = constructionDate
        #String with last bike path maintenance date
        self.maintenanceDate = maintenanceDate
        #String with last bike path inspection date
        self.inspectionDate = inspectionDate
        #String with the bike path creator
        self.creator = creator
        #Bike path stretches list
        self.stretches = list()

    def insertStretch(self,ID, P1, P2, type, direction, signage):
        #Create new bike path stretch object
        stretch = Stretch(ID, P1, P2, type, direction, signage)
        #Add in stretches list
        self.stretches.append(stretch)
        return stretch
