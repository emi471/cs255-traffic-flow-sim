import random

class TrafficSignal:
    def __init__(self, roads, config={}):
        # Initialize roads
        self.roads = roads
        
        # Set default configuration
        self.set_default_config()
        
        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)
            
        # Initialize properties - replaced init_properties() with direct initialization
        for i in range(len(self.roads)):
            for road in self.roads[i]:
                road.set_traffic_signal(self, i)
        
        # FCFS variables
        self.current_green = None
        self.green_timer = 0
        self.min_green_time = 0.5  # Minimum time a direction stays green (seconds)
        self.max_green_time = 1  # Maximum time a direction stays green
        self.yellow_time = 0.5  # Time for yellow light
        self.state = "red"  # Can be "red", "green", or "yellow"
        self.queues = [0] * len(self.roads)  # Track queue lengths for each direction

    def set_default_config(self):
        self.cycle = [(False, False, False, True), (False, False, True, False), 
                     (False, True, False, False), (True, False, False, False)]
        self.slow_distance = 30
        self.slow_factor = 0.4
        self.stop_distance = 6
        
        self.current_cycle_index = 0
        self.last_t = 0

    def update_queues(self):
        """Update queue lengths for each direction"""
        for i in range(len(self.roads)):
            total_vehicles = 0
            for road in self.roads[i]:
                # Count vehicles approaching the intersection (within 50 units)
                total_vehicles += sum(1 for v in road.vehicles if road.length - v.x < 10)
            self.queues[i] = total_vehicles

    def update(self, sim):
        self.update_queues()
        
        if self.current_green is None:
            # Initial state - find direction with most vehicles
            if any(q > 0 for q in self.queues):  # Only switch if there are vehicles
                self.current_green = self.queues.index(max(self.queues))
                self.state = "green"
                self.green_timer = 0
            return
            
        self.green_timer += sim.dt
        
        if self.state == "green":
            # Check if we should switch
            if (self.green_timer >= self.min_green_time and 
                all(q == 0 for q in self.queues)) or self.green_timer >= self.max_green_time:
                self.state = "yellow"
                self.green_timer = 0
                
        elif self.state == "yellow":
            if self.green_timer >= self.yellow_time:
                self.state = "red"
                self.green_timer = 0
                # Find next direction to serve
                next_green = None
                max_queue = 0
                for i, q in enumerate(self.queues):
                    if i != self.current_green and q > max_queue:
                        max_queue = q
                        next_green = i
                
                if next_green is not None:
                    self.current_green = next_green
                    self.state = "green"
                else:
                    # If no vehicles, keep red until someone arrives
                    self.current_green = None

    @property
    def current_cycle(self):
        """Returns the current traffic light state for each direction"""
        if self.current_green is None or self.state == "red":
            return [False] * len(self.roads)
        elif self.state == "yellow":
            return [i == self.current_green for i in range(len(self.roads))]
        else:  # green
            result = [False] * len(self.roads)
            result[self.current_green] = True
            return result
