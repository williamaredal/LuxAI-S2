from lux.kit import obs_to_game_state, GameState, EnvConfig
from lux.utils import my_turn_to_place_factory, direction_to 
import numpy as np
import random
import math

def rubble_tile_vision(x, y, rubble_map):
    height = len(rubble_map) - 1
    width = len(rubble_map[0]) - 1
    vision_coords =  [

        [x-1, y], [x, y-1], # left and top
        [x+1, y], [x, y+1], # right and bottom
        [x-1, y-1], [x+1, y-1], # diagonals
        [x-1, y+1], [x+1, y+1], # diagonals
        [x-2, y],   [x, y-2], # left and top 
        [x+2, y],   [x, y+2], # right and bottom 
        [x-2, y-1], [x-1, y-2], [x-2, y-2], # left and top diagonals 
        [x+2, y+1], [x+1, y+2], [x+2, y+2], # right and bottom diagonals 
        [x+2, y-1], [x+1, y-2], [x+2, y-2], # right and top diagonals 
        [x-2, y+1], [x-1, y+2], [x-2, y+2], # left and bottom diagonals 

        # feeler coords
        [x-3, y],   [x, y-3], # left and top 
        [x+3, y],   [x, y+3], # right and bottom 

        [x, y-5],
        [x-2, y-3], [x+2, y-3],
        [x-5, y-2], [x-3, y-2], [x+3, y-2], [x+5, y-2],
        [x+4, y-1], [x-4, y-1],
        [x-6, y], [x+6, y],
        [x+4, y+1], [x-4, y+1],
        [x-5, y+2], [x-3, y+2], [x+3, y+2], [x+5, y+2],
        [x-2, y+3], [x+2, y+3],
        [x, y+5],

    ]

    return [(rubble_coord, rubble_map[rubble_coord[0]][rubble_coord[1]]) for rubble_coord in vision_coords 
        if rubble_coord[0] >= 0 and rubble_coord[0] <= width and
           rubble_coord[1] >= 0 and rubble_coord[1] <= height
    ]
'''
                  [ ]
            [ ]   ^-5   [ ]
    [ ]  [ ]      [ ]      [ ]   [ ]
               [ ][ ][ ]   
      [ ]   [ ][ ][ ][ ][ ]   [ ]
[ ]      [ ][ ][ ] x [ ][ ][ ]      [ ]
^-6   [ ]   [ ][ ][ ][ ][ ]   [ ]   ^+6
               [ ][ ][ ]   
    [ ]  [ ]      [ ]      [ ]   [ ]
            [ ]         [ ]
                  [ ]
                  ^+5
'''


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


def get_factory_tiles_from_center(x, y):
    return np.array([
        (x, y), # factory center
        (x-1, y), (x, y-1), # left and top
        (x+1, y), (x, y+1), # right and bottom
        (x-1, y-1), (x+1, y-1), # diagonals
        (x-1, y+1), (x+1, y+1), # diagonals
    ]) 
    '''
    [.][.][.]
    [.][.][.]
    [.][.][.]
    '''


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
        (x-4, y), (x, y-4), (x+4, y), (x, y+4), # left and top
        (x-5, y), (x, y-5), (x+5, y), (x, y+5), # right and bottom
    ]) 
    '''
    [ ][ ][.][ ][ ]
    [ ][ ][.][ ][ ]
    [ ][.][.][.][ ]
 [.][.][.][X][.][.][.]
    [ ][.][.][.][ ]
    [ ][ ][.][ ][ ]
    [ ][ ][.][ ][ ]
    '''


def get_bordering_coords(x, y):
    return np.array([
        (x, y), # center
        (x-1, y), (x, y-1), # left and top
        (x+1, y), (x, y+1), # right and bottom
        (x-1, y-1), (x+1, y-1), # diagonals
        (x-1, y+1), (x+1, y+1), # diagonals
    ])


# function used by Archimedes for locating resource border coordinates
def neighbors(x, y):
    return np.array([
        # commented to give buffer, avoiding placing factory on resource
        # layer 1
        #(x-1, y), (x, y-1), # left and top
        #(x+1, y), (x, y+1), # right and bottom

        # layer 2
        (x-2, y), (x, y-2), # left and top 
        (x+2, y), (x, y+2), # right and bottom 

        (x-2, y-1), (x-1, y-2), # (x-2, y-2), # left and top diagonals 
        (x+2, y+1), (x+1, y+2), # (x+2, y+2), # right and bottom diagonals 

        (x+2, y-1), (x+1, y-2), # (x+2, y-2), # right and top diagonals 
        (x-2, y+1), (x-1, y+2), # (x-2, y+2), # left and bottom diagonals 

        # commented away to try to get factory right next to resource
        # layer 3
        #(x-3, y), (x, y-3), (x+3, y), (x, y+3), # left and top
        #(x-3, y), (x, y-3), (x+3, y), (x, y+3), # right and bottom

        #(x-3, y-1), (x-1, y-3), (x-3, y-3), # left and top diagonals 
        #(x+3, y+1), (x+1, y+3), (x+3, y+3), # right and bottom diagonals 

        #(x+3, y-1), (x+1, y-3), (x+3, y-3), # left and top diagonals 
        #(x-3, y+1), (x-1, y+3), (x-3, y+3), # right and bottom diagonals 

    ])
    '''
    [ ][.][.][.][ ]
    [.][ ][ ][ ][.]
    [.][ ][X][ ][.]
    [.][ ][ ][ ][.]
    [ ][.][.][.][ ]
    '''


def coord_from_direction(x, y, direction):
    if direction == 0:
        return (x, y)
    elif direction == 1:
        return (x, y-1)
    elif direction == 2:
        return (x+1, y)
    elif direction == 3:
        return (x, y+1)
    elif direction == 4:
        return (x-1, y)
'''
# a[1] = direction (0 = center, 1 = up, 2 = right, 3 = down, 4 = left)
move_deltas = np.array([[0, 0], [0, -1], [1, 0], [0, 1], [-1, 0]])
'''


# function used by Archimedes to check if tile is occupied by other bots
def check_tile_occupation(game_state, unit_x, unit_y, direction, booked_coords, player, opponent):
    friendly_bots = game_state.units[player]
    hostile_bots = game_state.units[opponent]

    friendly_coords = {(unit.pos[0], unit.pos[1]): unit.unit_type for (unit_id, unit) in friendly_bots.items()}
    hostile_coords = {(unit.pos[0], unit.pos[1]): unit.unit_type for (unit_id, unit) in hostile_bots.items()}

    # a[1] = direction (1 = up, 2 = right, 3 = down, 4 = left)
    # move_deltas = np.array([0, -1], [1, 0], [0, 1], [-1, 0]])
    bot_up = (unit_x, unit_y - 1)
    bot_right = (unit_x + 1, unit_y)
    bot_down = (unit_x, unit_y + 1)
    bot_left = (unit_x - 1, unit_y)


    # checks if no friendly is on direction tile, if none, direction remains, else set to 0
    up_friendly = (bot_up not in friendly_coords and bot_up not in booked_coords) * 1
    right_friendly = (bot_right not in friendly_coords and bot_right not in booked_coords) * 2
    down_friendly = (bot_down not in friendly_coords and bot_down not in booked_coords) * 3
    left_friendly = (bot_left not in friendly_coords and bot_left not in booked_coords) * 4

    # checks if hostile bot is on direction tile, if there is one of type 'LIGHT', direction remains, else set to 0
    up_hostile = True if (bot_up not in hostile_coords) or (bot_up in hostile_coords and hostile_coords[bot_up] == 'LIGHT' ) else False
    right_hostile = True if (bot_right not in hostile_coords) or (bot_right in hostile_coords and hostile_coords[bot_right] == 'LIGHT' ) else False
    down_hostile = True if (bot_down not in hostile_coords) or (bot_down in hostile_coords and hostile_coords[bot_down] == 'LIGHT' ) else False
    left_hostile = True if (bot_left not in hostile_coords) or (bot_left in hostile_coords and hostile_coords[bot_left] == 'LIGHT' ) else False

    '''
    # this is where the hostile attack decision making will be placed, as distinguishing between light/heavy is important for combat
    hostiles = [up_hostile, right_hostile, down_hostile, left_hostile]
    '''
    
    # sets non occupied tile directions
    up_free = up_friendly * up_hostile
    right_free = right_friendly * right_hostile
    down_free = down_friendly * down_hostile
    left_free = left_friendly * left_hostile


    # finds possible directions not occupied by friendly bots and hostile bots
    directions = [up_free, right_free, down_free, left_free]
    if direction in directions:
        return direction
    
    elif sum(directions) > 0:
        alt_directions = [d for d in directions if d > 0]
        return random.choice(alt_directions)
    '''
    # this directs the random movement choice in the opposite axis to direction to keep the bot moving in the general direction
    odd_direction = direction % 2 > 0
    for alt_direction in directions:
        alt_horisontal_directions = [d for d in directions if d > 0 and d % 2 == 0]
        if odd_direction and len(alt_horisontal_directions) > 0:
            return random.choice(alt_horisontal_directions)

        alt_vertical_directions = [d for d in directions if d > 0 and d % 2 == 1]
        if not odd_direction and len(alt_vertical_directions) > 0:
            return random.choice(alt_vertical_directions)
    '''

    '''
      []1
    []2[][]4
      []3
    ''' 

    # if all direction tiles occupied with friendly bots, recharge recommended
    return 0

    

class Archimedes_Lever():
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
            my_turn_to_evaluate_spawns = my_turn_to_place_factory(game_state.teams[self.player].place_first, step)

            # only processes map on my placement turns
            if my_turn_to_evaluate_spawns:
                ### Using numpy arrays, maps out desirable spawn locations
                # gets border indexes of ore coordinates and ice coordinates
                indOre = np.transpose(np.where(game_state.board.ore > 0))
                indIce = np.transpose(np.where(game_state.board.ice > 0))
                indFactories = np.transpose(np.where(game_state.board.factory_occupancy_map >= 0))

                # finds possible spawns around resources
                array_spawns = np.unique(np.concatenate(
                    [neighbors(*ind) for ind in indIce],
                    #[neighbors(*ind) for ind in iceSpawns],
                    ), axis=0)

                # finds tiles that are occupied or invalid spawn coords
                array_occupied_coords = np.unique(np.concatenate([get_factory_occupied_tiles(*i) for i in indFactories]), axis=0) if len(indFactories) > 0 else []
                array_invalid_coords = np.unique(np.concatenate(
                    (np.concatenate([get_bordering_coords(*ind) for ind in indOre], axis=0),
                    np.concatenate([get_bordering_coords(*ind) for ind in indIce], axis=0))
                ), axis=0)


                # filters spawn coords for outside map coords, and those overlapping ivalid or occupied tiles
                array_inside_map_spawns = [(np.array([c[0], c[1]]), game_state.board.rubble[c[0]][c[1]]) for c in array_spawns if (c[0] <= 46 and c[0] >= 1) and (c[1] <= 46 and c[1] >= 1)]
                array_valid_spawns = [coord for coord in array_inside_map_spawns if 
                    all(all(coord[0] == inv_coord) == False for inv_coord in array_invalid_coords) and 
                    all(all(coord[0] == occ_coord) == False for occ_coord in array_occupied_coords)
                ]

                '''
                desirable_coordinates_filtered = np.copy(game_state.board.valid_spawns_mask)
                desirable_coordinates_filtered[desirable_coordinates_filtered == 1] = 0
                # TODO mirror filtering here
                # visualizes the map and AI vision
                img = env.render("rgb_array", width=48, height=48)
                #px.imshow(game_state.board.rubble.T).show()
                px.imshow(img).show()
                px.imshow(desirable_coordinates_filtered.T).show()
                '''


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
                    array_sorted_spawns = sorted(array_valid_spawns, key=lambda coord: coord[1])
                    #print("spawn choices", len(array_sorted_spawns))
                    spawn_loc = array_sorted_spawns[0][0]

                    return dict(spawn=spawn_loc, metal=150, water=150)

            else:
                # returns empty dictionary if no decisions were reached
                return dict()


    
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
            tiles = get_factory_tiles_from_center(x=factory.pos[0], y=factory.pos[1])
            for tile in tiles:
                factory_tiles += [tile]
            factory_units += [factory]
        factory_tiles = np.array(factory_tiles)

        ### Creation of bots
        heavy_bot_cost = self.env_cfg.ROBOTS["HEAVY"]
        light_bot_cost = self.env_cfg.ROBOTS["LIGHT"]

        # heavy bots
        for unit_id, factory in factories.items():
            if factory.power >= heavy_bot_cost.POWER_COST and factory.cargo.metal >= heavy_bot_cost.METAL_COST:
                actions[unit_id] = factory.build_heavy()

        
        # light bots
        if game_state.real_env_steps >= 2:
            for unit_id, factory in factories.items():
                if factory.power >= light_bot_cost.POWER_COST and factory.cargo.metal >= light_bot_cost.METAL_COST:
                    actions[unit_id] = factory.build_light()


        

        #print(self.player)
        #print("turn:", game_state.real_env_steps)

        ### Decides when the factories should start growing Lichen
        # Watering lichen if at right turn
        '''
        # starting idea of some sort of regulating mechanism on when to start watering
        # see google sheets for optimal time to start watering by looking at water cargo,
        # number of turns left, 
        # and the water cost from the calculus of water consumption growth
        '''
        growth_turn = 990 - 300 # calculations suggenst 77 turns prior
        grow = game_state.real_env_steps >= growth_turn
        for factory_id, factory in factories.items():
            #print(factory_id, "has;", factory.cargo.metal, "metal", factory.cargo.water, "water", factory.cargo.ice, "ice", factory.power, "power", "watering cost: ", factory.water_cost(game_state))
            if game_state.real_env_steps >= growth_turn:
                actions[factory_id] = factory.water()
        '''
        # TODO continue this experiment of water to power conversion to see what strategies this unlocks, such as more efficient clearing of rubble,
        #      or mining assignments picking up power for ore mining
        grow = game_state.real_env_steps % 3 == 0
        for factory_id, factory in factories.items():
            #print(factory_id, "has;", factory.cargo.metal, "metal", factory.cargo.water, "water", factory.cargo.ice, "ice", factory.power, "power", "watering cost: ", factory.water_cost(game_state))
            if grow:
                actions[factory_id] = factory.water()
        '''

        ### Finds all ice and ore tiles
        ice_map = game_state.board.ice 
        ore_map = game_state.board.ore 
        rubble_map = game_state.board.rubble
        ice_tile_locations = np.argwhere(ice_map == 1) # numpy magic to get the position of every ice tile
        ore_tile_locations = np.argwhere(ore_map == 1) # numpy magic to get the position of every ore tile
        rubble_tile_locations = np.argwhere(rubble_map > 0) # numpy magic to get the position of every rubble tile
        rubble_tile_locations_low_rubble = np.argwhere(rubble_map <= 20)
        closest_rubble_tile = rubble_tile_locations[0]
        units = game_state.units[self.player]

        ### Specifies assignments for heavy and light bots
        light_ore_miners = 0
        mine_assignments = 0
        rubble_assignments = 0


        # booked tiles for avoiding 
        move_bookings = []

        for unit_id, unit in units.items():
            isHeavy = unit.unit_type == 'HEAVY'
            isLight = unit.unit_type == 'LIGHT'

            # info about closest map tiles
            closest_factory_tile = sorted(factory_tiles, key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )[0]
            closest_ice_tile = sorted(ice_tile_locations, key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )[0]
            

            cargo_limit_ice = 960
            cargo_limit_ore = 50
            on_factory = all(unit.pos == closest_factory_tile)
            ajacent_factory = 1 >= abs((unit.pos[0] - closest_factory_tile[0])**2 + (unit.pos[1] - closest_factory_tile[1])**2)


            ### Heavy bot logic
            if isHeavy:
                below_power_threshold_heavy = unit.power <= 100
                below_power_move_heavy = unit.power <= 50
                free_cargo_ice = unit.cargo.ice < cargo_limit_ice
                recharge_need_heavy = math.floor(1000 - unit.power)
                on_ice = all(unit.pos == closest_ice_tile)

                # Print out bot info 
                #print(unit.unit_type, unit_id, "at:", unit.pos, "power and ice:", unit.power, unit.cargo.ice, "unit queue:", len(unit.action_queue))
                
                # TODO perform some check if hostile bot is next to heavy bot vertical or horizontal axis

                # on ice, but not over cargo capacity limit. Dig ice
                if on_ice and free_cargo_ice and not below_power_threshold_heavy:
                    actions[unit_id] = [unit.dig(repeat=0)]
                    #print(unit_id, "digging")
                
                # not on ice, not over cargo capacity limit. Move to ice
                elif not on_ice and free_cargo_ice and not below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_ice_tile)
                    move_bookings.append(coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction))
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "move dig")
                
                # on factory, below power threshold. Pickup power
                elif on_factory and below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    actions[unit_id] = [unit.pickup(4, recharge_need_heavy, repeat=0)]
                    #print(unit_id, "pickup power")
                
                # not on factory, below power threshold. Move to recharge
                elif not on_factory and (below_power_threshold_heavy and not below_power_move_heavy):
                    direction = direction_to(unit.pos, closest_factory_tile)
                    move_bookings.append(coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction))
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "move recharge")

                # ajacent to factory, over cargo limit. Transfer ice
                elif ajacent_factory and not free_cargo_ice and not below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    actions[unit_id] = [unit.transfer(direction, 0, unit.cargo.ice, repeat=0)]
                    #print(unit_id, "transfer")

                # not ajacent to factory. Move to transfer
                elif not ajacent_factory and not free_cargo_ice and not below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    move_bookings.append(coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction))
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "move transfer")
                
                # not on factory, below critical power. Do nothing (recharge)
                elif not on_factory and (below_power_threshold_heavy and below_power_move_heavy):
                    #print(unit_id, "doing nothing (recharging)")
                    continue


            ### Finds all ore tiles, sorts by proximity to light bot
            ### Light bot logic
            if isLight:
                # TODO figure out weather to keep this vision function
                #bot_rubble_vision = rubble_tile_vision(x=unit.pos[0], y=unit.pos[1], rubble_map=game_state.board.rubble)
                # sorts low rubble tiles by proximity to closest factory tile to unit
                sorted_rubble_tile_vision = sorted(filter(lambda x: game_state.board.rubble[x[0]][x[1]] != 0, rubble_tile_locations_low_rubble), key=lambda coord: (coord[0] - closest_factory_tile[0])**2 + (coord[1] - closest_factory_tile[1])**2)
                lowest_rubble__tile_visible = sorted_rubble_tile_vision[0]

                closest_ore_tiles = sorted(ore_tile_locations, key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )
                closest_rubble_tiles = sorted(filter(lambda x: game_state.board.rubble[x[0]][x[1]] != 0, rubble_tile_locations_low_rubble), key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )
                closest_ore_tile = closest_ore_tiles[0]
                closest_rubble_tile = closest_rubble_tiles[0]
                
                # decides if the bot should be assigned an ore location or find closest rubble
                on_ore_assignment = mine_assignments < light_ore_miners
                if on_ore_assignment and mine_assignments < len(closest_ore_tiles):
                    closest_ore_tile = closest_ore_tiles[mine_assignments]
                    mine_assignments += 1
                if not on_ore_assignment and rubble_assignments < len(closest_rubble_tiles):
                    rubble_assignments += 1

                charge_state = game_state.is_day() and unit.power < 150 and not on_factory
                # TODO implement charge_state for better charging utilization
                power_threshold_light = 6
                below_power_threshold_light = unit.power <= 6
                power_for_dig = unit.power >= unit.dig_cost(game_state)
                recharge_need_light = math.floor(150 - unit.power)
                on_ore = all(unit.pos == closest_ore_tile)
                on_rubble = all(unit.pos == closest_rubble_tile)
                free_cargo_ore = unit.cargo.ore < cargo_limit_ore


                # Print out bot info 
                #print(unit.unit_type, unit_id, "at:", unit.pos, "power and ore:", unit.power, unit.cargo.ore, "unit queue:", len(unit.action_queue))

                # TODO perform some sort of check to see if bot has hostile bot (light = attack, heavy = flee) on horizontal/vertical tiles

                # on ore, under cargo limit, not below power threshold, not charge state, not charge state. Dig ore
                if on_ore and free_cargo_ore and not below_power_threshold_light and not charge_state:
                    actions[unit_id] = [unit.dig(repeat=0)]
                    #print(unit_id, "dig ore")
                

                # on rubble, under cargo limit, not below power threshold, not charge state. Dig rubble
                elif on_rubble and free_cargo_ore and not below_power_threshold_light and not charge_state:
                    actions[unit_id] = [unit.dig(repeat=0)]
                    #print(unit_id, "dig rubble")
                

                # on ore assignment, not on ore, not on rubble, under cargo limit, not below power threshold, not charge state. Move to ore
                elif on_ore_assignment and not on_ore and not on_rubble and free_cargo_ore and not below_power_threshold_light and not charge_state:
                    direction = direction_to(unit.pos, closest_ore_tile)
                    newDirection = check_tile_occupation(game_state=game_state,
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        direction=direction,
                        booked_coords=move_bookings,
                        player=self.player,
                        opponent=self.opp_player
                    )
                
                    if newDirection == 0:
                        continue
                        #print(unit_id, "recharge instead of moving")
                        
                    else:
                        move_bookings.append(coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=newDirection))
                        actions[unit_id] = [unit.move(newDirection, repeat=0)]
                        #print(unit_id, "move to ore")
                    

                # not on ore assignment, not on ore, not on rubble, under cargo limit, not below power threshold, not charge state. Move to rubble
                elif not on_ore_assignment and not on_rubble and free_cargo_ore and not below_power_threshold_light and not charge_state:
                    direction = direction_to(unit.pos, lowest_rubble__tile_visible)
                    newDirection = check_tile_occupation(game_state=game_state,
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        direction=direction,
                        booked_coords=move_bookings,
                        player=self.player,
                        opponent=self.opp_player
                    )

                    if newDirection == 0:
                        continue
                        #print(unit_id, "recharge instead of moving")
                        
                    else:
                        move_bookings.append(coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=newDirection))
                        actions[unit_id] = [unit.move(newDirection, repeat=0)]
                        #print(unit_id, "move to rubble")


                # below power threshold or in a charge state. Do nothing (recharge)
                elif below_power_threshold_light or charge_state:
                    continue
                    #print(unit_id, "recharge")
                

                # ajacent to factory, at/over cargo limit, not below power threshold, not charge state. Transfer ore
                elif ajacent_factory and not free_cargo_ore and not below_power_threshold_light and not charge_state:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    actions[unit_id] = [unit.transfer(direction, 1, unit.cargo.ore)]
                    #print(unit_id, "transfer cargo")
                

                # not ajacent to factory, at/over cargo limit, not below power threshold, not charge state. Move to transfer
                elif not ajacent_factory and not free_cargo_ore and not below_power_threshold_light and not charge_state:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    move_bookings.append(coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction))
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "move to transfer cargo")


        return actions