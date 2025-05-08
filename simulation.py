from .road import Road
from copy import deepcopy
from .vehicle_generator import VehicleGenerator
from .traffic_signal import TrafficSignal
import csv

class Simulation:
    vehiclesPassed = 0;
    vehiclesPresent = 0;
    vehicleRate = 0;
    isPaused = False;
    
    # NEW Dictionary to track vehicles
    vehicle_tracking = {}  

    def __init__(self, config={}):
        # Set default configuration
        self.set_default_config()
        
        # NEW Collision tracking
        self.collision_count = 0
        self.colliding_vehicles = set()  # Tracks currently colliding vehicles

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

    def set_default_config(self):
        self.t = 0.0            # Time keeping
        self.frame_count = 0    # Frame count keeping
        self.dt = 1/60          # Simulation time step
        self.roads = []         # Array to store roads
        self.generators = []
        self.traffic_signals = []
        self.iteration = 0      # n-th iteration (of sampling, if enabled)

    def create_road(self, start, end):
        road = Road(start, end)
        self.roads.append(road)
        return road

    def create_roads(self, road_list):
        for road in road_list:
            self.create_road(*road)

    def create_gen(self, config={}):
        gen = VehicleGenerator(self, config)
        self.generators.append(gen)
        Simulation.vehicleRate = gen.vehicle_rate
        return gen

    def create_signal(self, roads, config={}):
        roads = [[self.roads[i] for i in road_group] for road_group in roads]
        sig = TrafficSignal(roads, config)
        self.traffic_signals.append(sig)
        return sig
    
    # NEW Main collision detection method
    def detect_collisions(self):
        # Get all vehicles with their bounds
        all_vehicles = []
        for road in self.roads:
            for vehicle in road.vehicles:
                all_vehicles.append({
                    'vehicle': vehicle,
                    'bounds': road.get_vehicle_bounds(vehicle)
                })
        
        # Reset collision states but maintain visual feedback
        for data in all_vehicles:
            vehicle = data['vehicle']
            if not any(self._check_collision(data['bounds'], other['bounds']) 
               for other in all_vehicles if other['vehicle'] != vehicle):
                # No longer colliding with anyone
                vehicle.is_colliding = False
                vehicle.has_counted_collision = False
                vehicle.color = vehicle._original_color
        
        # Check all vehicle pairs
        for i in range(len(all_vehicles)):
            for j in range(i+1, len(all_vehicles)):
                v1_data = all_vehicles[i]
                v2_data = all_vehicles[j]
                
                if self._check_collision(v1_data['bounds'], v2_data['bounds']):
                    v1 = v1_data['vehicle']
                    v2 = v2_data['vehicle']
                    
                    # Visual feedback (always turn red)
                    v1.is_colliding = True
                    v2.is_colliding = True
                    v1.color = (255, 0, 0)
                    v2.color = (255, 0, 0)
                    
                    # Only count if this is a new collision
                    if not v1.has_counted_collision or not v2.has_counted_collision:
                        self.collision_count += 1
                        v1.has_counted_collision = True
                        v2.has_counted_collision = True
                    
    def _check_collision(self, poly1, poly2):
        # SAT algorithm for convex polygon collision
        for polygon in [poly1, poly2]:
            for i in range(len(polygon)):
                x1, y1 = polygon[i]
                x2, y2 = polygon[(i+1)%len(polygon)]
                edge_x, edge_y = x2-x1, y2-y1
                normal_x, normal_y = -edge_y, edge_x
                
                # Project both polygons
                min1, max1 = self._project(poly1, normal_x, normal_y)
                min2, max2 = self._project(poly2, normal_x, normal_y)
                
                if max1 < min2 or max2 < min1:
                    return False
        return True

    def _project(self, polygon, x, y):
        # Project polygon onto axis
        min_p = max_p = polygon[0][0]*x + polygon[0][1]*y
        for px, py in polygon[1:]:
            p = px*x + py*y
            min_p = min(min_p, p)
            max_p = max(max_p, p)
        return (min_p, max_p)

    def _handle_collision(self, v1, v2):
        """Handle collision visual feedback and counting"""
        if v1.id not in self.colliding_vehicles:
            self.collision_count += 1
            self.colliding_vehicles.add(v1.id)
            self.colliding_vehicles.add(v2.id)
            v1.color = (255, 0, 0)  # Red
            v2.color = (255, 0, 0)  # Red

    def _handle_separation(self, v1, v2):
        """Reset vehicles when no longer colliding"""
        if v1.id in self.colliding_vehicles:
            v1.color = v1._original_color
            self.colliding_vehicles.remove(v1.id)
        if v2.id in self.colliding_vehicles:
            v2.color = v2._original_color
            self.colliding_vehicles.remove(v2.id)

    def update(self):
        # NEW Detect collisions
        self.detect_collisions()
        # Update every road
        for road in self.roads:
            road.update(self.dt)

        # Add vehicles
        for gen in self.generators:
            gen.update()

        for signal in self.traffic_signals:
            signal.update(self)

        # Check roads for out of bounds vehicle
        for road in self.roads:
            # If road has no vehicles, continue
            if len(road.vehicles) == 0: continue
            # If not
            vehicle = road.vehicles[0]
            # If first vehicle is out of road bounds
            if vehicle.x >= road.length:
                # If vehicle has a next road
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    # Update current road to next road
                    vehicle.current_road_index += 1
                    # Create a copy and reset some vehicle properties
                    new_vehicle = deepcopy(vehicle)
                    new_vehicle.x = 0
                    # Add it to the next road
                    next_road_index = vehicle.path[vehicle.current_road_index]
                    self.roads[next_road_index].vehicles.append(new_vehicle)
                else:
                    # NEW Track vehicle completion
                    Simulation.vehiclesPassed += 1
                    vehicle.exit_time = self.t
                    # NEW Record lifetime if we have both timestamps
                    if vehicle.spawn_time is not None:
                        lifetime = vehicle.exit_time - vehicle.spawn_time
                        self.vehicle_tracking[vehicle.id] = {
                            'spawn_time': vehicle.spawn_time,
                            'exit_time': vehicle.exit_time,
                            'lifetime': lifetime
                        }
                # In all cases, remove it from its road
                road.vehicles.popleft() 

                # if vehicle reached the end of the path
                # if vehicle.current_road_index + 1 == len(vehicle.path):
                #     Simulation.vehiclesPassed += 1
                    # print("Vehicle passed: " + str(Simulation.vehiclesPassed))

        # Check for the number of vehicles present
        Simulation.vehiclesPresent = 0
        for road in self.roads:
            Simulation.vehiclesPresent += len(road.vehicles)

        # Increment time
        self.t += self.dt
        self.frame_count += 1

        # Stop at certain time in seconds (for sampling purposes. Comment out if not needed)
        self.time_limit = 300
        if self.t >= self.time_limit:
            print("Traffic Signal Cycle Length: " + str(self.traffic_signals[0].cycle_length))
            print("Time: " + str(self.t))
            print("Vehicles Passed: " + str(Simulation.vehiclesPassed))
            print("Vehicles Present: " + str(Simulation.vehiclesPresent))
            print("Vehicle Rate: " + str(Simulation.vehicleRate))
            print("Traffic Density: " + str(Simulation.vehiclesPresent / (len(self.roads) * self.roads[0].length)))
            print("Iteration: " + str(self.iteration))

            # Add to CSV the time and vehicles passed
            with open('data.csv', mode='a') as data_file:
                data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow([self.traffic_signals[0].cycle_length, Simulation.vehiclesPassed])

            # Reset time and vehicles passed
            self.t = 0.001
            gen.delete_all_vehicles()
            Simulation.vehiclesPassed = 0
            Simulation.vehiclesPresent = 0
            self.iteration += 1
            if self.iteration % 5 == 0:
                # Set all traffic signals to +1
                for signal in self.traffic_signals:
                    signal.cycle_length += 1


    def run(self, steps):
        for _ in range(steps):
            self.update()

    def pause(self):
        self.isPaused = True

    def resume(self):
        self.isPaused = False