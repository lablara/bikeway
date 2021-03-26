import reverse_geocode
import folium

class MapGenerator:
    map = None
    location = None

    def __init__(self):
        self.map = folium.Map(location=[-12.280265953993627, -38.96356796067759], zoom_start=13)

        #CHANGE TO DATE
        #Translates request coordinate to city/country
        coordinate = (-12.280265953993627, -38.96356796067759),(0, 0)
        reverseCoordinate = reverse_geocode.search(coordinate)[0]
        location = reverseCoordinate['city'] + "_" + reverseCoordinate['country_code']
        self.location = location.replace(' ', '_')

    def generateMap(self):
        self.map.save(self.location+".html")

    def insertBikePath(self, path, quality):
        color = None
        if quality == "VG":
            color = 'blue'
        elif quality == "G":
            color = 'green'
        elif quality == "M":
            color = 'yellow'
        elif quality == "B":
            color = 'orange'
        elif quality == "VB":
            color = 'red'

        folium.PolyLine(path, color=color,  weight=8, opacity=0.5).add_to(self.map)

    def insertMonitoringPoint(self, point):
        folium.Marker(location=point).add_to(self.map)

#-------------------------------------------------------------------------------------
#PATH 1
place_lat = [-12.259737269514789, -12.26002063783269, -12.2558106495222]
place_lng = [-38.96369536812054, -38.95501595253243, -38.95481515670223]

path1 = []
for i in range(len(place_lat)):
    path1.append([place_lat[i], place_lng[i]])

#PATH 2
place_lat = [-12.257729504029106, -12.258063555067247, -12.255874275994563]
place_lng = [-38.95577592041933, -38.95124533258551, -38.95067091416719]

path2 = []
for i in range(len(place_lat)):
    path2.append([place_lat[i], place_lng[i]])

mg = MapGenerator()
mg.insertBikePath(path1, "VG")
mg.insertBikePath(path2, "VB")

#POINTS IN PATH 1
mg.insertMonitoringPoint([-12.259722626063445, -38.96313809688914])
mg.insertMonitoringPoint([-12.259769483899554, -38.96108073013457])
mg.insertMonitoringPoint([-12.25992365599116, -38.95654045755573])
mg.insertMonitoringPoint([-12.25997504666832, -38.9552958268488])
mg.insertMonitoringPoint([-12.2593959300763, -38.954920618973716])
mg.insertMonitoringPoint([-12.258729163246192, -38.954969159257566])
mg.insertMonitoringPoint([-12.256784506447909, -38.954910195567436])
mg.insertMonitoringPoint([-12.255970627309178, -38.954865972799844])

#POINTS IN PATH 2

mg.generateMap()
