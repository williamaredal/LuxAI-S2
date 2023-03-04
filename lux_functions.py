from luxai_s2.env import LuxAI_S2
from lux.kit import obs_to_game_state, GameState
from luxai_s2.utils import animate
import numpy as np

env = LuxAI_S2() # create the environment object

# tools for animating actions in notebook
def animate(imgs, _return=True):
    # using cv2 to generate videos as moviepy doesn't work on kaggle notebooks
    import cv2
    import os
    import string
    import random
    video_name = ''.join(random.choice(string.ascii_letters) for i in range(18))+'.webm'
    height, width, layers = imgs[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'VP90')
    video = cv2.VideoWriter(video_name, fourcc, 10, (width,height))

    for img in imgs:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        video.write(img)
    video.release()
    if _return:
        from IPython.display import Video
        return Video(video_name)


def interact(env, agents, steps, video=True):
    # reset our env seed if not set earlier
    if env.state.seed == -1:
        obs = env.reset(seed=41)
    else: 
        obs = env.reset(seed=env.state.seed)

    np.random.seed(0)
    imgs = []
    step = 0
    # Note that as the environment has two phases, we also keep track a value called 
    # `real_env_steps` in the environment state. The first phase ends once `real_env_steps` is 0 and used below

    # iterate until phase 1 ends
    while env.state.real_env_steps < 0:
        if step >= steps: break
        actions = {}
        for player in env.agents:
            o = obs[player]
            a = agents[player].early_setup(step, o)
            actions[player] = a
        step += 1
        obs, rewards, dones, infos = env.step(actions)
        imgs += [env.render("rgb_array", width=640, height=640)]
    done = False
    while not done:
        if step >= steps: break
        actions = {}
        for player in env.agents:
            o = obs[player]
            a = agents[player].act(step, o)
            actions[player] = a
        step += 1
        obs, rewards, dones, infos = env.step(actions)
        imgs += [env.render("rgb_array", width=640, height=640)]
        done = dones["player_0"] and dones["player_1"]
    
    if video == True:
        return animate(imgs)
    else:
        return None


def test_agents(env, agents, steps):
    # reset our env seed if not set earlier
    if env.state.seed == -1:
        obs = env.reset(seed=41)
    else: 
        obs = env.reset(seed=env.state.seed)

    np.random.seed(0)
    step = 0
    # Note that as the environment has two phases, we also keep track a value called 
    # `real_env_steps` in the environment state. The first phase ends once `real_env_steps` is 0 and used below

    # iterate until phase 1 ends
    while env.state.real_env_steps < 0:
        if step >= steps: break
        actions = {}
        for player in env.agents:
            o = obs[player]
            a = agents[player].early_setup(step, o)
            actions[player] = a
        step += 1
        obs, rewards, dones, infos = env.step(actions)
    done = False

    # values storing lichen stats at end of interaction steps
    player0_total_lichen = 0
    player1_total_lichen = 0
    while not done:
        if step >= steps: break
        actions = {}
        for player in env.agents:
            o = obs[player]
            a = agents[player].act(step, o)
            actions[player] = a

        
 

        step += 1
        # prints lichen stats at end of interaction steps for both players
        if step == steps:
            player0_factories = obs['player_0']['factories']['player_0']
            player1_factories = obs['player_1']['factories']['player_1']

            for factory_id, factory in player0_factories.items():
                lichen_strain_tiles = np.argwhere(obs['player_0']['board']['lichen_strains'] == factory['strain_id'])
                for tile in lichen_strain_tiles:
                    player0_total_lichen += obs['player_0']['board']['lichen'][tile[0]][tile[1]]

            for factory_id, factory in player1_factories.items():
                lichen_strain_tiles = np.argwhere(obs['player_0']['board']['lichen_strains'] == factory['strain_id'])
                for tile in lichen_strain_tiles:
                    player1_total_lichen += obs['player_0']['board']['lichen'][tile[0]][tile[1]]


        obs, rewards, dones, infos = env.step(actions)
        done = dones["player_0"] and dones["player_1"]
    
    
    return [
        ('player_0', player0_total_lichen),
        ('player_1', player1_total_lichen),
        ('p0 % performance:', (player0_total_lichen/player1_total_lichen)),
        ('p0-p1 lichen difference:', player0_total_lichen - player1_total_lichen),
        ('map seed:', env.state.seed),
    ] 