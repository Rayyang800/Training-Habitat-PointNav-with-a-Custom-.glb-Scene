# Training-Habitat-PointNav-with-a-Custom-.glb-Scene
This tutorial demonstrates how to train and evaluate a PointNav agent in Habitat using your own .glb 3D model.
The workflow includes:
1.Modifying Habitat-Lab configuration

2.Generating a navigation mesh (NavMesh)

3.Creating a custom PointNav dataset

4.Running PPO training / evaluation

5.Visualizing results with TensorBoard

This setup is ideal if you want to train agents in custom indoor environments instead of the default Gibson scenes.


1. Modify run.py (Habitat Baselines Entry Point)

In habitat-baselines/habitat_baselines/run.py, update the Hydra decorator to use the standard PointNav PPO config:
@hydra.main(
    version_base=None,
    config_path="config",
    config_name="pointnav/ppo_pointnav",
)

2. Configure the Dataset (gibson.yaml)

Edit the dataset configuration file:
habitat-lab/habitat/config/habitat/dataset/pointnav/gibson.yaml
# @package habitat.dataset
defaults:
  - /habitat/dataset: dataset_config_schema
  - _self_
type: PointNav-v1
#split: train
data_path: /home/user/habitat-lab/customdataset/roomCustom.json.gz

⚠️ Even though the file name is gibson.yaml, it can point to any custom dataset.

3. Generate a NavMesh from Your .glb Scene
This script:
a.Loads your .glb scene
b.Recomputes the NavMesh
c.Saves the NavMesh to disk
d.Generates top-down maps and path visualizations
Key Settings:
a.Agent height: 1.5 m
b.Agent radius: 0.25 m
c.climbing (agent_max_climb = 0.2)
Please use the scripts provided in this repository.(genNavmesh.py)

4. Generate a Custom PointNav Dataset
This step creates a .json.gz dataset containing navigation episodes.
Dataset Properties:
a.Random start & goal positions
b.Uses geodesic distance
c.Filters out trivial or invalid paths
d.Output format compatible with Habitat PointNav
output:
/home/user/habitat-lab/customdataset/roomCustom.json.gz
Episode Structure:
{
  "episode_id": 0,
  "scene_id": ".../roomTest.glb",
  "start_position": [x, y, z],
  "start_rotation": [0, 0, 0, 1],
  "goals": [{ "position": [x, y, z] }]
}
Please use the scripts provided in this repository.(genDataset.py)

5. PPO PointNav Configuration
Please run training first (`habitat_baselines.evaluate=False`), and then run evaluation (`habitat_baselines.evaluate=True`).Training must be executed first with `habitat_baselines.evaluate=False`.
After training completes, run evaluation with `habitat_baselines.evaluate=True`.
ppo_pointnav.yaml:
# @package _global_
#num_environment=.glb_number

defaults:
  - /benchmark/nav/pointnav: pointnav_gibson
  - /habitat_baselines: habitat_baselines_rl_config_base
  - _self_

habitat_baselines:
  checkpoint_interval: -1
  writer_type: tb
  load_resume_state_config: False
  verbose: true
  trainer_name: "ppo"
  torch_gpu_id: 0
  tensorboard_dir: "tb"
  video_dir: "video_dir"
  eval_ckpt_path_dir: "data/new_checkpoints"
  num_environments: 1
  checkpoint_folder: "data/new_checkpoints"
  num_updates: -1
  total_num_steps: 3e5
  log_interval: 10
  num_checkpoints: 100
  force_torch_single_threaded: False
  evaluate: false
  
 
  eval:
    video_option: ["disk"]
    should_load_ckpt: True
    split: roomcustom
    

  rl:
    ppo:
      clip_param: 0.2
      ppo_epoch: 4
      num_mini_batch: 2
      value_loss_coef: 0.5
      entropy_coef: 0.01
      lr: 2.5e-4
      eps: 1e-5
      max_grad_norm: 0.5
      num_steps: 128
      hidden_size: 512
      use_gae: true
      gamma: 0.99
      tau: 0.95
      use_linear_clip_decay: true
      use_linear_lr_decay: true
      reward_window_size: 50
      use_double_buffered_sampler: false

6. Training & Evaluation Commands
rm data/new_checkpoints/.habitat-resume-stateeval.pth
rm data/new_checkpoints/.habitat-resume-state.pth
python habitat-baselines/habitat_baselines/run.py
tensorboard --logdir /home/user/habitat-lab/tb --port 6007

7.If you find any mistakes, feel free to point them out.
