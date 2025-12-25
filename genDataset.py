import habitat_sim
import random
import json
import gzip
import os
import numpy as np

# ---------------------------------------------------------------------------------------------------Scene and navmesh paths
scene_path = "/home/user/habitat_data/data/scene_datasets/habitat-test-scenes/roomTest.glb"
navmesh_path = "/home/user/habitat_data/data/scene_datasets/habitat-test-scenes/roomTest1.navmesh"

# Verify files exist
if not os.path.exists(scene_path):
    raise FileNotFoundError(f"Scene file not found: {scene_path}")
if not os.path.exists(navmesh_path):
    raise FileNotFoundError(f"Navmesh file not found: {navmesh_path}. Generate it using habitat_sim.navmesh.")

# Create simulator configuration
sim_cfg = habitat_sim.SimulatorConfiguration()
sim_cfg.scene_id = scene_path
sim_cfg.enable_physics = False
sim_cfg.allow_sliding = True
sim_cfg.load_semantic_mesh = False  # Disable semantic mesh to avoid warnings

# Create agent configuration
agent_cfg = habitat_sim.agent.AgentConfiguration()

# Create simulator
cfg = habitat_sim.Configuration(sim_cfg, [agent_cfg])
sim = habitat_sim.Simulator(cfg)

# Load navmesh
if not sim.pathfinder.is_loaded:
    sim.pathfinder.load_nav_mesh(navmesh_path)
if not sim.pathfinder.is_loaded:
    raise RuntimeError(f"Failed to load navmesh: {navmesh_path}")

# Function to compute geodesic distance using find_path
def compute_geodesic_distance(pathfinder, start, goal):
    path = habitat_sim.ShortestPath()
    path.requested_start = start
    path.requested_end = goal
    if pathfinder.find_path(path):
        points = path.points
        if len(points) < 2:
            return float("inf")  # No valid path
        # Sum Euclidean distances between consecutive points
        distance = 0.0
        for i in range(len(points) - 1):
            distance += np.linalg.norm(np.array(points[i + 1]) - np.array(points[i]))
        return distance
    return float("inf")  # No path found

# Function to convert _magnum.Vector3 to list
def vector3_to_list(point):
    return [float(point.x), float(point.y), float(point.z)]

# Generate episodes
#-----------------------------------------------------------------------------------episodesnum
episodes = []
num_episodes = 500
episode_count = 0
max_attempts = 1000  # Prevent infinite loops

while len(episodes) < num_episodes and max_attempts > 0:
    max_attempts -= 1
    # Sample random navigable points
    start = sim.pathfinder.get_random_navigable_point()
    goal = sim.pathfinder.get_random_navigable_point()

    # Check if points are valid
    if not sim.pathfinder.is_navigable(start) or not sim.pathfinder.is_navigable(goal):
        print(f"Invalid navigable points, retrying... (Attempts left: {max_attempts})")
        continue

    # Calculate geodesic distance
    dist = compute_geodesic_distance(sim.pathfinder, start, goal)
    if dist == float("inf") or dist < 1.0:
        print(f"Invalid distance (dist={dist}), retrying... (Attempts left: {max_attempts})")
        continue

    # Create episode
    try:
        episode = {
            "episode_id": episode_count,
            "scene_id": scene_path,
            "start_position": vector3_to_list(start),
            "start_rotation": [0, 0, 0, 1],  # Fixed quaternion
            "goals": [{"position": vector3_to_list(goal)}]
        }
        episodes.append(episode)
        episode_count += 1
        print(f"Generated episode {episode_count}/{num_episodes}")
    except Exception as e:
        print(f"Error creating episode: {e}, retrying... (Attempts left: {max_attempts})")
        continue

# Check if we failed to generate enough episodes
if len(episodes) < num_episodes:
    print(f"Warning: Only generated {len(episodes)} episodes due to too many invalid attempts.")

# Save episodes to json.gz
#----------------------------------------------------------------------------------------------------outputname
out_file = "/home/user/habitat-lab/customdataset/roomCustom.json.gz"
os.makedirs(os.path.dirname(out_file), exist_ok=True)
with gzip.open(out_file, "wt") as f:
    json.dump({"episodes": episodes}, f)

print(f"✅ Saved {len(episodes)} episodes to {out_file}")

# Close simulator
sim.close()
