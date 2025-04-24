# Simulation Loop
# Handles updating of car positions
# Also tracks the metrics of the simulation we want to record

class Simulation:
    # Some initial metrics
    carsPassed = 0
    avgCarTime = 0
    carRate = 0
    
    def reset(self):
        # Function to reset the simulation and all its variables to zero
        
    def newRoad(self, start, end):
        # Create a new road
    
    def importRoadList(self, road_list):
        # Import roads from a list
        # Probably good functionality to have if we want to have multiple road configurations
        
    def generateVehicles(self):
        # Function to start generating cars?
        :
    def newLight(self, roads):
        # Create a new traffic light at these roads
        
    def update(self):
        # Main simulation loop
    