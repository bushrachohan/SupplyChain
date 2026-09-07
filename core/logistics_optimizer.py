"""
core/logistics_optimizer.py
Vehicle Routing Problem (VRP) optimization using Google OR-Tools.
"""

from typing import List, Dict, Any
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def create_data_model(deliveries: List[Dict[str, Any]], num_vehicles: int, vehicle_capacities: List[int]) -> Dict[str, Any]:
    """
    Stores the data for the problem.
    Creates a mock distance matrix based on delivery distances.
    """
    data = {}
    
    # 0 is the depot
    num_locations = len(deliveries) + 1
    
    # Mock a distance matrix
    # We assume depot is at 0,0 and others are distributed
    # Distance from depot to i is approx deliveries[i-1]['distance_km']
    distance_matrix = []
    
    for i in range(num_locations):
        row = []
        for j in range(num_locations):
            if i == j:
                row.append(0)
            elif i == 0:
                # Depot to node
                row.append(int(deliveries[j-1].get('distance_km', 100)))
            elif j == 0:
                # Node to depot
                row.append(int(deliveries[i-1].get('distance_km', 100)))
            else:
                # Node to node - mock using a triangle inequality approx
                d_i = deliveries[i-1].get('distance_km', 100)
                d_j = deliveries[j-1].get('distance_km', 100)
                row.append(int(abs(d_i - d_j) + 10))  # +10 is arbitrary cross-distance
        distance_matrix.append(row)
        
    data["distance_matrix"] = distance_matrix
    
    # Mock demands: assume each delivery is a certain weight
    # Defaulting to 100 for each delivery if not provided
    demands = [0] + [int(d.get('weight', 100)) for d in deliveries]
    data["demands"] = demands
    
    data["vehicle_capacities"] = vehicle_capacities
    data["num_vehicles"] = num_vehicles
    data["depot"] = 0
    return data

def optimize_routes(delivery_ids: List[str], vehicle_constraints: Dict[str, Any], df_deliveries: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Optimize routes for the given deliveries and vehicle constraints.
    
    Args:
        delivery_ids: List of delivery IDs to route.
        vehicle_constraints: dict with 'num_vehicles' and 'capacities'
        df_deliveries: List of delivery dicts containing 'delivery_id' and 'distance_km'.
                       If None, will mock data.
    
    Returns:
        dict with total_distance, total_cost, and vehicle_routes
    """
    if not df_deliveries:
        # Mock deliveries if not provided
        df_deliveries = [{"delivery_id": did, "distance_km": 50 * (i + 1), "weight": 100} 
                         for i, did in enumerate(delivery_ids)]
    else:
        # Filter for requested delivery_ids
        df_deliveries = [d for d in df_deliveries if d.get('delivery_id') in delivery_ids]
        
    if not df_deliveries:
        return {"status": "No deliveries to route."}
        
    num_vehicles = vehicle_constraints.get("num_vehicles", 2)
    capacities = vehicle_constraints.get("capacities", [500] * num_vehicles)
    
    # Ensure capacities list matches num_vehicles
    if len(capacities) < num_vehicles:
        capacities.extend([capacities[-1]] * (num_vehicles - len(capacities)))
    elif len(capacities) > num_vehicles:
        capacities = capacities[:num_vehicles]
        
    data = create_data_model(df_deliveries, num_vehicles, capacities)

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data["vehicle_capacities"],  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity",
    )

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(2)

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        return _format_solution(data, manager, routing, solution, df_deliveries)
    else:
        return {"status": "No solution found. Check capacity constraints."}


def _format_solution(data, manager, routing, solution, deliveries) -> Dict[str, Any]:
    """Formats the OR-Tools solution into a readable dictionary."""
    result = {
        "status": "Success",
        "total_distance_km": 0,
        "total_load": 0,
        "routes": []
    }
    
    total_distance = 0
    total_load = 0
    
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        route_distance = 0
        route_load = 0
        stops = []
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data["demands"][node_index]
            
            # Map node_index to delivery_id
            delivery_id = "DEPOT" if node_index == 0 else deliveries[node_index - 1].get("delivery_id")
            stops.append({
                "node_index": node_index,
                "delivery_id": delivery_id,
                "load_at_stop": route_load
            })
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
        # Add the final depot return
        node_index = manager.IndexToNode(index)
        stops.append({
            "node_index": node_index,
            "delivery_id": "DEPOT",
            "load_at_stop": route_load
        })
        
        # Only add route if it actually made deliveries (stops > 2 means it left depot and returned)
        if len(stops) > 2:
            result["routes"].append({
                "vehicle_id": vehicle_id,
                "stops": stops,
                "route_distance_km": route_distance,
                "route_load": route_load
            })
            total_distance += route_distance
            total_load += route_load
            
    result["total_distance_km"] = total_distance
    result["total_load"] = total_load
    
    # We mock total cost as $2 per km
    result["total_cost"] = total_distance * 2.0
    
    return result

if __name__ == "__main__":
    dels = ["DEL_001", "DEL_002", "DEL_003", "DEL_004"]
    constraints = {"num_vehicles": 2, "capacities": [250, 250]}
    res = optimize_routes(dels, constraints)
    print(res)
