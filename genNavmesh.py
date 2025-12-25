import os
os.environ["MAGNUM_LOG"] = "quiet"
os.environ["HABITAT_SIM_LOG"] = "quiet"

import numpy as np
import matplotlib
matplotlib.use("Agg")  # 強制使用非交互式 backend，避免 GUI crash
import matplotlib.pyplot as plt
import imageio
import habitat_sim

OUTPUT_DIR = "output_navmesh"
os.makedirs(OUTPUT_DIR, exist_ok=True)
#----------------------------------------------------------------------------------------------------------name
NAVMESH_FILE = os.path.join(OUTPUT_DIR, "roomTest1.navmesh")


# ---------- 修改顯示函式：只存圖，不開視窗 ----------
def display_map(topdown_map, key_points=None, title=None, savepath=None):
    plt.figure(figsize=(10, 7))
    ax = plt.subplot(1, 1, 1)
    ax.axis("off")
    ax.imshow(topdown_map)
    if key_points is not None:
        for p in key_points:
            plt.plot(p[0], p[1], marker="o", markersize=8, alpha=0.9)
    if title:
        plt.title(title)
    if savepath:
        plt.savefig(savepath, bbox_inches="tight", dpi=200)
        print("Saved:", savepath)
    plt.close()

def convert_points_to_topdown(pathfinder, points, meters_per_pixel):
    points_topdown = []
    bounds = pathfinder.get_bounds()
    for point in points:
        px = (point[0] - bounds[0][0]) / meters_per_pixel
        py = (point[2] - bounds[0][2]) / meters_per_pixel
        points_topdown.append(np.array([px, py]))
    return points_topdown

# ---------- 初始化 Simulator --------------------------------------------------------------------------glbdata
scene_path = "/home/user/habitat_data/data/scene_datasets/habitat-test-scenes/roomTest.glb"
sim_cfg = habitat_sim.SimulatorConfiguration()
sim_cfg.scene_id = scene_path

agent_cfg = habitat_sim.agent.AgentConfiguration()
config = habitat_sim.Configuration(sim_cfg, [agent_cfg])
sim = habitat_sim.Simulator(config)

print("Pathfinder loaded?", sim.pathfinder.is_loaded)
print("NavMesh bounds:", sim.pathfinder.get_bounds())

# ---------- 生成 navmesh ----------
nav_settings = habitat_sim.NavMeshSettings()
nav_settings.set_defaults()
nav_settings.agent_height = 1.5
nav_settings.agent_radius = 0.25
nav_settings.agent_max_climb = 0.0

ok = sim.recompute_navmesh(sim.pathfinder, nav_settings)
print("NavMesh recompute success?", ok)
if ok:
    sim.pathfinder.save_nav_mesh(NAVMESH_FILE)
    print("NavMesh saved to:", NAVMESH_FILE)





"""
ok = sim.recompute_navmesh(sim.pathfinder, nav_settings)
print("NavMesh recompute success?", ok)
"""





# ---------- 取得 topdown map ----------
meters_per_pixel = 0.1
bounds = sim.pathfinder.get_bounds()
height = bounds[0][1]
topdown_map = sim.pathfinder.get_topdown_view(meters_per_pixel, height)
#------------------------------------------------------------------------------------------------------------------nametopdown
display_map(topdown_map, title="Topdown Raw", savepath=os.path.join(OUTPUT_DIR, "topdown_raw.png"))

# ---------- 試著找一條路徑並畫在地圖上 ----------
start = sim.pathfinder.get_random_navigable_point()
end = sim.pathfinder.get_random_navigable_point()

path_query = habitat_sim.ShortestPath()
path_query.requested_start = start
path_query.requested_end = end
found = sim.pathfinder.find_path(path_query)
print("Path found?", found, "Distance:", path_query.geodesic_distance)

if found:
    pts_2d = convert_points_to_topdown(sim.pathfinder, path_query.points, meters_per_pixel)
    # 把路徑畫在地圖上
    rgb_map = np.dstack([topdown_map * 255] * 3)
    display_map(rgb_map, key_points=pts_2d, title="Path on Topdown",
#-----------------------------------------------------------------------------------------------------------------namepath
                savepath=os.path.join(OUTPUT_DIR, "topdown_path.png"))

sim.close()
print("Done. Images saved in", OUTPUT_DIR)
