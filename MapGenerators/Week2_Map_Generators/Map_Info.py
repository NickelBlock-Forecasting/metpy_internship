'''
    All Maps Classes
'''
class VeryWide:
    def __init__(self):
        map_info = MapInfo()
        self.map_type = 'verywide'
        self.cities = map_info.very_wide_cities()
        self.NorthSouthEastWest = [37, 28, -81, -97]


class Regional:
    def __init__(self):
        map_info = MapInfo()
        self.map_type = 'regional'
        self.cities = map_info.regional_cities()
        self.NorthSouthEastWest = [35.5, 28.5, -84.5, -93.5]


class Local:
    def __init__(self):
        map_info = MapInfo()
        self.map_type = 'local'
        self.cities = map_info.local_cities()
        self.NorthSouthEastWest = [33.5, 29.5, -86.5, -91.5]


class Tropical:
    def __init__(self):
        self.map_type = 'tropical'
        self.NorthSouthEastWest = [40.5, 8.5, -15.5, -97.5]


'''
    All Maps information with all cities defined
'''
class MapInfo:
    def __init__(self):
        self.hattiesburg = City('Hattiesburg', 31.3271, -89.2903)
        self.jackson = City('Jackson', 32.2988, -90.1848)
        self.tupelo = City('Tupelo', 34.2576, -88.7034)
        # - LOUISIANA
        self.new_orleans = City('New Orleans', 29.9511, -90.0715)
        self.baton_rouge = City('Baton Rouge', 30.4515, -91.1871)
        self.shreveport = City('Shreveport', 32.5252, -93.7502)
        # - ALABAMA
        self.mobile = City('Mobile', 30.6954, -88.0399)
        self.montgomery = City('Montgomery', 32.3792, -86.3077)
        self.tuscaloosa = City('Tuscaloosa', 33.2098, -87.5692)
        self.huntsville = City('Huntsville', 34.7304, -86.5861)
        self.dothan = City('Dothan', 31.2232, -85.3905)
        # - TENNESSEE
        self.memphis = City('Memphis', 35.1495, -90.0490)
        self.jackson_tenn = City('Jackson', 35.6145, -88.8139)
        self.clarksville = City('Clarksville', 36.5298, -87.3595)
        self.knoxville = City('Knoxville', 35.9606, -83.9207)
        # - GEORGIA
        self.atlanta = City('Atlanta', 33.7490, -84.3880)
        self.macon = City('Macon', 32.8407, -83.6324)
        # - FLORIDA
        self.pensacola = City('Pensacola', 30.4213, -87.2169)
        self.tallahassee = City('Tallahassee', 30.4383, -84.2807)
        self.jacksonville = City('Jacksonville', 30.3322, -81.6557)
        # - ARKANSAS
        self.little_rock = City('Little Rock', 34.7465, -92.2896)
        self.fort_smith = City('Fort Smith', 35.3859, -94.3985)
        # - SOUTH CAROLINA
        self.augusta = City('Augusta', 33.4735, -82.0105)
        # - TEXAS
        self.houston = City('Houston', 29.7604, -95.3698)

    def very_wide_cities(self):
        cities = [
            self.hattiesburg,
            self.jackson,
            self.tupelo,

            self.new_orleans,
            self.baton_rouge,
            self.shreveport,

            self.mobile,
            self.montgomery,
            self.tuscaloosa,
            self.huntsville,
            self.dothan,

            self.memphis,
            self.jackson_tenn,
            self.clarksville,
            self.knoxville,

            self.atlanta,
            self.macon,

            self.pensacola,
            self.tallahassee,
            self.jacksonville,

            self.little_rock,
            self.fort_smith,

            self.augusta,

            self.houston
        ]
        return cities

    def local_cities(self):
        cities = [
            self.hattiesburg,
            self.jackson,
            self.tupelo,

            self.new_orleans,
            self.baton_rouge,

            self.mobile,
            self.tuscaloosa,

            self.memphis,

            self.pensacola,
        ]
        return cities

    def regional_cities(self):
        cities = [
            self.hattiesburg,
            self.jackson,
            self.tupelo,

            self.new_orleans,
            self.baton_rouge,

            self.mobile,
            self.montgomery,
            self.tuscaloosa,
            self.huntsville,
            self.dothan,

            self.memphis,

            self.pensacola,

            self.little_rock,
        ]
        return cities


'''
    Class for defining cities to plot
'''
class City:
    def __init__(self, city_name, lat, lon, temp=None):
        self.city_name = city_name
        self.lat = lat
        self.lon = lon
        self.temp = temp
