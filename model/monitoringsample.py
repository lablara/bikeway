class MonitoringSample:
    def __init__(self, deviceID, date, time, city, coordinate, data):
        #String with MMS ID
        self.deviceID = deviceID
        #String with sample date
        self.date = date
        #String with sample time
        self.time = time
        #String with sample city
        self.city = city
        #String with sample coordinate
        self.coordinate = coordinate.copy()
        #String with sample monitoring data
        self.data = data.copy()
