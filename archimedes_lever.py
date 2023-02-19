from luxai_s2.env import LuxAI_S2
from lux.kit import obs_to_game_state, GameState, EnvConfig
from lux.utils import my_turn_to_place_factory, direction_to 
import numpy as np
import plotly.express as px
import math

env = LuxAI_S2() # create the environment object
obs = env.reset(seed=69) # resets an environment with a seed

# the observation is always composed of observations for both players.
obs.keys(), obs["player_0"].keys()

# visualize the environment so far with rgb_array to get a quick look at the map
# dark orange - high rubble, light orange - low rubble
# blue = ice, yellow = ore
img = env.render("rgb_array", width=48, height=48)
px.imshow(img).show()


def remove_spawns_at_border(desirable_coordinates, map_width, map_height):
    for x in range(0, map_width):
        desirable_coordinates[0][x] = 0
        desirable_coordinates[map_width - 1][x] = 0

    for y in range(0, map_height):
        desirable_coordinates[0][x] = 0
        desirable_coordinates[y][map_height - 1] = 0

    return desirable_coordinates


def set_coords_zero(desirable_coordinates, resource_indexes):
    for x, y in resource_indexes:
        try:
            desirable_coordinates[x][y] = 0
       
        except IndexError:
            continue

    return desirable_coordinates


def set_coords_one(desirable_coordinates, spawn_indexes):
    for x, y in spawn_indexes:
        try:
            desirable_coordinates[x][y] = 1
       
        except IndexError:
            continue

    return desirable_coordinates


def get_factory_occupied_tiles(x, y):
    return np.array([
        (x, y), # factory center
        (x-1, y), (x, y-1), # left and top
        (x+1, y), (x, y+1), # right and bottom
        (x-1, y-1), (x+1, y-1), # diagonals
        (x-1, y+1), (x+1, y+1), # diagonals
        (x-2, y), (x, y-2), # left and top 
        (x+2, y), (x, y+2), # right and bottom 
        (x-2, y-1), (x-1, y-2), (x-2, y-2), # left and top diagonals 
        (x+2, y+1), (x+1, y+2), (x+2, y+2), # right and bottom diagonals 
        (x+2, y-1), (x+1, y-2), (x+2, y-2), # right and top diagonals 
        (x-2, y+1), (x-1, y+2), (x-2, y+2), # left and bottom diagonals 
        (x-3, y), (x, y-3), (x+3, y), (x, y+3), # left and top
        (x-3, y), (x, y-3), (x+3, y), (x, y+3), # right and bottom
        (x-3, y-1), (x-1, y-3), (x-3, y-3), # left and top diagonals 
        (x+3, y+1), (x+1, y+3), (x+3, y+3), # right and bottom diagonals 
        (x+3, y-1), (x+1, y-3), (x+3, y-3), # left and top diagonals 
        (x-3, y+1), (x-1, y+3), (x-3, y+3), # right and bottom diagonals 

    ]) 


def get_bordering_coords(x, y):
    return np.array([
        (x, y), # center
        (x-1, y), (x, y-1), # left and top
        (x+1, y), (x, y+1), # right and bottom
        (x-1, y-1), (x+1, y-1), # diagonals
        (x-1, y+1), (x+1, y+1), # diagonals
    ])


# function used by Agent_007 for locating resource border coordinates
def neighbors(x, y):
    return np.array([
        # commented to give buffer, avoiding placing factory on resource
        # layer 1
        #(x-1, y), (x, y-1), # left and top
        #(x+1, y), (x, y+1), # right and bottom

        # layer 2
        (x-2, y), (x, y-2), # left and top 
        (x+2, y), (x, y+2), # right and bottom 

        (x-2, y-1), #(x-1, y-2), (x-2, y-2), # left and top diagonals 
        (x+2, y+1), #(x+1, y+2), (x+2, y+2), # right and bottom diagonals 

        (x+2, y-1), #(x+1, y-2), (x+2, y-2), # right and top diagonals 
        (x-2, y+1), #(x-1, y+2), (x-2, y+2), # left and bottom diagonals 

        # commented away to try to get factory right next to resource
        # layer 3
        #(x-3, y), (x, y-3), (x+3, y), (x, y+3), # left and top
        #(x-3, y), (x, y-3), (x+3, y), (x, y+3), # right and bottom

        #(x-3, y-1), (x-1, y-3), (x-3, y-3), # left and top diagonals 
        #(x+3, y+1), (x+1, y+3), (x+3, y+3), # right and bottom diagonals 

        #(x+3, y-1), (x+1, y-3), (x+3, y-3), # left and top diagonals 
        #(x-3, y+1), (x-1, y+3), (x-3, y+3), # right and bottom diagonals 

    ])
    # expand this to include diagonal border coordinates, up to 3 away, or possibly make this method take a search grid range 
    # and return a np array with results from this grid range


# function used by Agent_007 for sorting list of resource locations by point x and y value
def get_ordered_list(points, x, y):
    p_list2 = sorted(points, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    return p_list2


# function used by Agent_007 for deciding what action the unit should take to accieve its assignment
def assignment_action_decision(unit, unit_id, assignment_tile, actions, direction, move_power_cost, dig_power_cost):
    if type(assignment_tile) == str or (unit.power < move_power_cost) or (unit.power < dig_power_cost):
        print('idle assignment: ', assignment_tile)
        actions[unit_id] = [unit.recharge(1, repeat=0)]
        #actions[unit_id] = [unit.move(0, repeat=0)] # move 0 equals move center

    if all(unit.pos == assignment_tile) and (unit.power >= dig_power_cost):
        print('dig assignment: ', assignment_tile)
        actions[unit_id] = [unit.dig(repeat=0)]

    else:
        direction = direction_to(unit.pos, assignment_tile)
        print('move assignment: ', assignment_tile, direction)
        actions[unit_id] = [unit.move(direction, repeat=0)]




class Archimedes():
    def __init__(self, player: str, env_cfg: EnvConfig) -> None:
        self.player = player
        self.opp_player = "player_1" if self.player == "player_0" else "player_0"
        np.random.seed(0)
        self.env_cfg: EnvConfig = env_cfg

    # Setup of early game
    def early_setup(self, step: int, obs, remainingOverageTime: int = 60):
        if step == 0:
            # bid 0 to not waste resources bidding and declare as the default faction
            # you can bid -n to prefer going second or n to prefer going first in placement
            return dict(faction="AlphaStrike", bid=0)
        else:
            game_state = obs_to_game_state(step, self.env_cfg, obs)

            ### Resets spawn mask coordinates and sets desirable coords with proximity to ice/ore coordinates as spawn coordinates
            # sets all valid coordinates to 0 as only zero and one are possible 
            desirable_coordinates_filtered = np.copy(game_state.board.valid_spawns_mask)
            desirable_coordinates_filtered[desirable_coordinates_filtered == 1] = 0

            # gets border indexes of ore coordinates and ice coordinates
            indOre = np.transpose(np.where(game_state.board.ore > 0))
            oreSpawns = np.unique(np.concatenate([neighbors(*i) for i in indOre]), axis=0)

            indIce = np.transpose(np.where(game_state.board.ice > 0))
            iceSpawns = np.unique(np.concatenate([neighbors(*i) for i in indIce]), axis=0)

            # sets coordinates around ore and ice to 1
            '''
            desirable_coordinates_filtered = set_coords_one(desirable_coordinates=desirable_coordinates_filtered, spawn_indexes=oreSpawns)
            '''
            desirable_coordinates_filtered = set_coords_one(desirable_coordinates=desirable_coordinates_filtered, spawn_indexes=iceSpawns)

            # then replaces ore and ice coordinates (and directly ajacent ones) with 0, as these are not valid spawn locations
            oreNeighb = np.unique(np.concatenate([get_bordering_coords(*i) for i in indOre]), axis=0)
            desirable_coordinates_filtered = set_coords_zero(desirable_coordinates=desirable_coordinates_filtered, resource_indexes=oreNeighb)

            iceNeighb = np.unique(np.concatenate([get_bordering_coords(*i) for i in indIce]), axis=0)
            desirable_coordinates_filtered = set_coords_zero(desirable_coordinates=desirable_coordinates_filtered, resource_indexes=iceNeighb)
            
            
            # then replace border coordinates with 0, as these are not valid spawn locations
            map_width = len(desirable_coordinates_filtered[0])
            map_height = len(desirable_coordinates_filtered)
            desirable_coordinates_filtered = remove_spawns_at_border(desirable_coordinates=desirable_coordinates_filtered, map_width=map_width, map_height=map_height)

            # then replace coordinates where there are factories (and directly ajacent ones) with 0, as these are no longer valid spawn locations
            factory_indexes = np.transpose(np.where(game_state.board.factory_occupancy_map > 0))
            if len(factory_indexes) > 0:
                occupied_indexes = np.unique(np.concatenate([get_factory_occupied_tiles(*i) for i in factory_indexes]), axis=0)
                desirable_coordinates_filtered = set_coords_zero(desirable_coordinates=desirable_coordinates_filtered, resource_indexes=occupied_indexes)


            # visualizes the map and AI vision
            #img = env.render("rgb_array", width=48, height=48)
            #px.imshow(img).show()
            #px.imshow(desirable_coordinates_filtered.T).show()


            ### Factory placement period
            # how much water and metal you have in your starting pool to give to new factories
            water_left = game_state.teams[self.player].water
            metal_left = game_state.teams[self.player].metal
            
            # how many factories you have left to place
            factories_to_place = game_state.teams[self.player].factories_to_place

            # whether it is your turn to place a factory
            my_turn_to_place = my_turn_to_place_factory(game_state.teams[self.player].place_first, step)
            if factories_to_place > 0 and my_turn_to_place:
                # we will spawn our factory in a random location with 150 metal and water if it is our turn to place
                potential_spawns = np.array(list(zip(*np.where(desirable_coordinates_filtered == 1))))
                spawn_loc = potential_spawns[np.random.randint(0, len(potential_spawns))]

                return dict(spawn=spawn_loc, metal=150, water=150)

            # returns empty dictionary if no decisions were reached
            return dict()


    '''
    ROBOTS: Dict[str, UnitConfig] = dataclasses.field(
        default_factory=lambda: dict(
            LIGHT=UnitConfig(
                METAL_COST=10,
                POWER_COST=50,
                CARGO_SPACE=100,
                BATTERY_CAPACITY=150,
                DIG_COST=5,
                DIG_LICHEN_REMOVED=10, # if on hostile lichen with less than 10, and not at max power. charge.
            ),
            HEAVY=UnitConfig(
                METAL_COST=100,
                POWER_COST=500,
                CARGO_SPACE=1000,
                BATTERY_CAPACITY=3000,
                DIG_COST=60,
                DIG_RESOURCE_GAIN=20,
            ),
    '''


    # Setup of logic in the act phase
    def act(self, step: int, obs, remainingOverageTime: int = 60):
        # info used to make decisions in the act phase
        actions = dict()
        game_state: GameState = obs_to_game_state(step, self.env_cfg, obs)
        factories = game_state.factories[self.player]
        game_state.teams[self.player].place_first

        # storing of info about factories
        factory_tiles, factory_units = [], []
        for unit_id, factory in factories.items():
            factory_tiles += [factory.pos]
            factory_units += [factory]
        factory_tiles = np.array(factory_tiles)

        ### Creation of bots
        heavy_bot_cost = self.env_cfg.ROBOTS["HEAVY"]
        light_bot_cost = self.env_cfg.ROBOTS["HEAVY"]
        for unit_id, factory in factories.items():
            if factory.power >= heavy_bot_cost.POWER_COST and factory.cargo.metal >= heavy_bot_cost.METAL_COST:
                # sets factory with unit_id to construct heavy bot
                actions[unit_id] = factory.build_heavy()
        
        
        # wait with building light bots until heavies mine ice and dropoff successfully
        '''
        for unit_id, factory in factories.items():
            if factory.power >= light_bot_cost.POWER_COST and factory.cargo.metal >= light_bot_cost:
                actions[unit_id] = factory.build_light()
        '''


        ### Finds all ice tiles, sorts by proximity to heavy bot
        ice_map = game_state.board.ice 
        ice_tile_locations = np.argwhere(ice_map == 1) # numpy magic to get the position of every ice tile
        units = game_state.units[self.player]

        for unit_id, unit in units.items():
            isHeavy = unit.unit_type == 'HEAVY'
            isLight = unit.unit_type == 'LIGHT'

            # info about closest map tiles
            closest_ice_tile = sorted(ice_tile_locations, key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )[0]
            closest_factory_tile = sorted(factory_tiles, key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )[0]

            cargo_limit_ice = 100
            on_ice = all(unit.pos == closest_ice_tile)
            on_factory = all(unit.pos == closest_factory_tile)
            ajacent_factory = 1 >= abs((unit.pos[0] - closest_factory_tile[0]) + (unit.pos[1] - closest_factory_tile[1]))
            recharge_need_heavy = math.floor((1000/2) - unit.power)
            queue_empty = len(unit.action_queue) == 0
            #print(ajacent_factory)

            # on ice, but not over cargo capacity limit
            if isHeavy and on_ice and unit.cargo.ice <= cargo_limit_ice and queue_empty:
                actions[unit_id] = [unit.dig(repeat=0)]
            
            # not on ice, not over cargo capacity limit, moves to closest ice
            elif isHeavy and not on_ice and unit.cargo.ice <= cargo_limit_ice:
                direction = direction_to(unit.pos, closest_ice_tile)
                actions[unit_id] = [unit.move(direction, repeat=0)]
            
            # on factory, over cargo limit, transfers and pickup power
            elif isHeavy and on_factory and unit.cargo.ice >= cargo_limit_ice and queue_empty:
                direction = direction_to(unit.pos, closest_factory_tile)
                actions[unit_id] = [unit.transfer(direction, 0, unit.cargo.ice, repeat=0)]
                actions[unit_id] = [unit.pickup(0, recharge_need_heavy, repeat=0)]

            # ajacent to factory, over cargo limit, transfers and pickup power
            elif isHeavy and ajacent_factory and unit.cargo.ice >= cargo_limit_ice and queue_empty:
                direction = direction_to(unit.pos, closest_factory_tile)
                actions[unit_id] = [unit.move(direction, repeat=0)]

            # not on factory, moves to closest factory
            elif isHeavy and not on_factory and unit.cargo.ice >= cargo_limit_ice and queue_empty:
                direction = direction_to(unit.pos, closest_ice_tile)
                actions[unit_id] = [unit.move(direction, repeat=0)]

            


        ### Finds all ore tiles, sorts by proximity to light bot



        ### Watering lichen if at right turn
        '''
        # starting idea of some sort of regulating mechanism on when to start watering
        # see google sheets for optimal time to start watering by looking at water cargo,
        # number of turns left, 
        # and the water cost from the calculus of water consumption growth

        if self.env_cfg.max_episode_length - game_state.real_env_steps < 50:
                if factory.water_cost(game_state) <= factory.cargo.water:
                    actions[unit_id] = factory.water()
        '''

        return actions


    '''
    ### Movement of bots, towards resources if enough energy. to nearest factory if full or low energy
    # iterate over our units and have them mine the closest ice tile
    units = game_state.units[self.player]
    factory_tile_locations = np.array([factory.pos for id, factory in factories.items()])
    factories_midpoint_x = np.mean([factory[0] for factory in factory_tile_locations])
    factories_midpoint_y = np.mean([factory[1] for factory in factory_tile_locations])
    factories_midpoint_coordinate = np.array([factories_midpoint_x, factories_midpoint_y])


    ### Finds all ice tiles, sorts by proximity to factory 
    sorted_ice_locations = get_ordered_list(points=ice_tile_locations, x=factories_midpoint_coordinate[0], y=factories_midpoint_coordinate[1])


    ### Finds all ore tiles, sorts by proximity to factory
    ore_map = game_state.board.ore
    ore_tile_locations = np.argwhere(ore_map == 1)
    sorted_ore_locations = get_ordered_list(points=ore_tile_locations, x=factories_midpoint_coordinate[0], y=factories_midpoint_coordinate[1])


    ### Distributes 'tile assignments' for ore and ice tiles to 40 and 60 percent of the bots available, bots left are given ice assignments
    num_bots = len(units)
    ice_assignments = math.floor((num_bots * 0.4))
    ore_assignments = math.floor((num_bots * 0.6))
    # as long as distribution of assignments sum to 100%, only one remaining bot is required to give extra assignment
    if (ice_assignments + ore_assignments) < num_bots:
        ice_assignments += 1
        ore_assignments += 1

    print('\n', game_state.real_env_steps)
    print([(factory_id, factory.cargo.water) for factory_id, factory in factories.items()])
    #print(game_state.teams[self.player].water)
    assignment_count = 0
    for unit_id, unit in units.items():
        if (assignment_count == (assignment_count - 1) ):
            break

        factory_tile_distances = np.mean((factory_tile_locations - unit.pos) ** 2, 1)
        closest_factory_tile = factory_tile_locations[np.argmin(factory_tile_distances)]
        moves_to_closest_factory = abs(closest_factory_tile[0] - unit.pos[0]) + abs(closest_factory_tile[1] - unit.pos[1])

        # begins moving back if cargo is filled with ice
        home_direction = direction_to(unit.pos, closest_factory_tile)
        home_move_cost = unit.move_cost(game_state, home_direction) + unit.action_queue_cost(game_state)
        if (unit.cargo.ice >= 20) or (unit.cargo.ore >= 20) or (unit.power <= (home_move_cost * moves_to_closest_factory)):
            print('home chosen', assignment_count, num_bots)
            adjacent_to_factory = np.mean((closest_factory_tile - unit.pos) ** 2) == 0

            if adjacent_to_factory and (unit.cargo.ice > 0):
                direction = direction_to(unit.pos, closest_factory_tile)
                print('offloaded', unit.cargo.ice)
                actions[unit_id] = [unit.transfer(direction, 0, unit.cargo.ice, repeat=0)]
                continue

            if adjacent_to_factory and (unit.cargo.ore > 0):
                direction = direction_to(unit.pos, closest_factory_tile)
                print('offloaded', unit.cargo.ore)
                actions[unit_id] = [unit.transfer(direction, 0, unit.cargo.ore, repeat=0)]
                continue

            if adjacent_to_factory and (unit.cargo.ice == 0) and (unit.cargo.ore == 0):
                actions[unit_id] = [unit.recharge(150, repeat=0)]
                continue
            
            else:
                direction = direction_to(unit.pos, closest_factory_tile)
                actions[unit_id] = [unit.move(direction, repeat=0)]
                continue

        # assigns bot to ice duty to closest ice tile
        if assignment_count < ice_assignments:
            # decides weather bot can be assigned, is on assignement tile and should dig, or if it should move towards tile
            assignment_tile = sorted_ice_locations[0] if len(sorted_ice_locations) > 0 else 'unassigned'
            print('ice chosen', unit.pos, assignment_tile, unit.pos == assignment_tile)

            direction = direction_to(unit.pos, assignment_tile)
            move_power_cost = unit.move_cost(game_state, direction) + unit.action_queue_cost(game_state)
            dig_power_cost = unit.dig_cost(game_state) + unit.action_queue_cost(game_state)
            assignment_action_decision(
                unit=unit, 
                unit_id=unit_id,
                assignment_tile=assignment_tile,
                actions=actions,
                direction=direction,
                move_power_cost=move_power_cost,
                dig_power_cost=dig_power_cost
                )
            sorted_ice_locations = np.delete(sorted_ice_locations, 0, axis=0) if len(sorted_ice_locations) > 0 else sorted_ice_locations
            assignment_count += 1
            continue

        # assigns bot to ore duty to closest ore tile
        if assignment_count >= ice_assignments and assignment_count < ore_assignments:
            assignment_tile = sorted_ore_locations[0] if len(sorted_ore_locations) > 0 else 'unassigned'
            print('ore chosen', unit.pos, assignment_tile, num_bots)

            direction = direction_to(unit.pos, assignment_tile)
            move_power_cost = unit.move_cost(game_state, direction) + unit.action_queue_cost(game_state)
            dig_power_cost = unit.dig_cost(game_state) + unit.action_queue_cost(game_state)
            
            assignment_action_decision(
                unit=unit, 
                unit_id=unit_id,
                assignment_tile=assignment_tile,
                actions=actions,
                direction=direction,
                move_power_cost=move_power_cost,
                dig_power_cost=dig_power_cost
                )
            sorted_ore_locations = np.delete(sorted_ore_locations, 0, axis=0) if len(sorted_ore_locations) > 0 else sorted_ore_locations
            assignment_count += 1
            continue

        else:
            print('none chosen', unit_id, assignment_count, num_bots)
            assignment_count += 1
            continue


    return actions
    '''
    

import default_agent
import lux_functions

# recreate our agents and run
player0 = env.agents[0]
player1 = env.agents[1]
agents = {
    player0: Archimedes(env.agents[0], env.state.env_cfg), 
    player1: default_agent.Default_Agent(env.agents[1], env.state.env_cfg)
}


lux_functions.interact(env=env, agents=agents, steps=1000, video=True)