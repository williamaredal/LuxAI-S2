from lux.kit import obs_to_game_state, GameState, EnvConfig
from lux.utils import my_turn_to_place_factory, direction_to 
import numpy as np
import random
import math


def remove_spawns_at_border(desirable_coordinates, map_width, map_height):
    for x in range(0, map_width):
        desirable_coordinates[0][x] = 0
        desirable_coordinates[1][x] = 0
        desirable_coordinates[map_width - 1][x] = 0
        desirable_coordinates[map_width - 2][x] = 0

    for y in range(0, map_height):
        desirable_coordinates[0][x] = 0
        desirable_coordinates[y][map_height - 1] = 0
        desirable_coordinates[y][map_height - 2] = 0

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
        #(x-3, y), (x, y-3), (x+3, y), (x, y+3), # left and top
        #(x-3, y), (x, y-3), (x+3, y), (x, y+3), # right and bottom
        #(x-3, y-1), (x-1, y-3), (x-3, y-3), # left and top diagonals 
        #(x+3, y+1), (x+1, y+3), (x+3, y+3), # right and bottom diagonals 
        #(x+3, y-1), (x+1, y-3), (x+3, y-3), # left and top diagonals 
        #(x-3, y+1), (x-1, y+3), (x-3, y+3), # right and bottom diagonals 

    ]) 
    '''
    [ ][ ][ ][ ][ ]
    [ ][.][.][.][ ]
    [ ][.][.][.][ ]
    [ ][.][.][.][ ]
    [ ][ ][ ][ ][ ]
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


# function used by Archimedes to check if tile is occupied by other bots
def check_tile_occupation(game_state, unit_x, unit_y, direction, player, opponent):
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
    up_friendly = (bot_up not in friendly_coords) * 1
    right_friendly = (bot_right not in friendly_coords) * 2
    down_friendly = (bot_down not in friendly_coords) * 3
    left_friendly = (bot_left not in friendly_coords) * 4

    # checks if hostile bot is on direction tile, if there is one of type 'LIGHT', direction remains, else set to 0
    up_hostile = True if (bot_up not in hostile_coords) or (bot_up in hostile_coords and hostile_coords[bot_up] == 'LIGHT' ) else False
    right_hostile = True if (bot_up not in hostile_coords) or (bot_up in hostile_coords and hostile_coords[bot_up] == 'LIGHT' ) else False
    down_hostile = True if (bot_up not in hostile_coords) or (bot_up in hostile_coords and hostile_coords[bot_up] == 'LIGHT' ) else False
    left_hostile = True if (bot_up not in hostile_coords) or (bot_up in hostile_coords and hostile_coords[bot_up] == 'LIGHT' ) else False

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
    return -1

    

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
            factory_indexes = np.transpose(np.where(game_state.board.factory_occupancy_map >= 0))
            if len(factory_indexes) > 0:
                occupied_indexes = np.unique(np.concatenate([get_factory_occupied_tiles(*i) for i in factory_indexes]), axis=0)
                desirable_coordinates_filtered = set_coords_zero(desirable_coordinates=desirable_coordinates_filtered, resource_indexes=occupied_indexes)

            '''
            # visualizes the map and AI vision
            img = env.render("rgb_array", width=48, height=48)
            px.imshow(game_state.board.rubble.T).show()
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
                potential_spawns = np.array(list(zip(*np.where(desirable_coordinates_filtered == 1))))
                spawn_loc = potential_spawns[np.random.randint(0, len(potential_spawns))]

                return dict(spawn=spawn_loc, metal=150, water=150)

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
       
        
        ### Finds all ice and ore tiles
        ice_map = game_state.board.ice 
        ore_map = game_state.board.ore 
        rubble_map = game_state.board.rubble
        ice_tile_locations = np.argwhere(ice_map == 1) # numpy magic to get the position of every ice tile
        ore_tile_locations = np.argwhere(ore_map == 1) # numpy magic to get the position of every ore tile
        rubble_tile_locations = np.argwhere(rubble_map > 0) # numpy magic to get the position of every rubble tile
        closest_rubble_tile = rubble_tile_locations[0]
        units = game_state.units[self.player]

        for unit_id, unit in units.items():
            isHeavy = unit.unit_type == 'HEAVY'
            isLight = unit.unit_type == 'LIGHT'

            # info about closest map tiles
            closest_factory_tile = sorted(factory_tiles, key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )[0]
            closest_ice_tile = sorted(ice_tile_locations, key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )[0]
            closest_ore_tiles = sorted(ore_tile_locations, key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )
            closest_rubble_tiles = sorted(rubble_tile_locations, key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )
            closest_ore_tile = closest_ore_tiles[0]
            closest_rubble_tile = closest_rubble_tiles[0]
            light_ore_miners = 1
            mine_assignments = 0
            rubble_assignments = 0

            cargo_limit_ice = 960
            cargo_limit_ore = 50
            on_factory = all(unit.pos == closest_factory_tile)
            ajacent_factory = 1 >= abs((unit.pos[0] - closest_factory_tile[0])**2 + (unit.pos[1] - closest_factory_tile[1])**2)


            ### Heavy bot logic
            if isHeavy:
                below_power_threshold_heavy = unit.power <= 100
                recharge_need_heavy = math.floor(1000 - unit.power)
                on_ice = all(unit.pos == closest_ice_tile)

                # Print out bot info 
                #print(unit.unit_type, unit_id, "at:", unit.pos, "power and ice:", unit.power, unit.cargo.ice, "unit queue:", len(unit.action_queue))

                # on ice, but not over cargo capacity limit
                if on_ice and unit.cargo.ice < cargo_limit_ice and not below_power_threshold_heavy:
                    actions[unit_id] = [unit.dig(repeat=0)]
                    #print(unit_id, "digging")
                
                # not on ice, not over cargo capacity limit, moves to closest ice
                elif not on_ice and unit.cargo.ice < cargo_limit_ice and not below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_ice_tile)
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "move dig")
                
                # on factory, below power threshold, pickup power
                elif on_factory and below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    actions[unit_id] = [unit.pickup(4, recharge_need_heavy, repeat=0)]
                    #print(unit_id, "recharging")
                
                # not on factory, below power threshold. move on factory
                elif not on_factory and below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "move recharge")

                # ajacent to factory, over cargo limit 
                elif ajacent_factory and unit.cargo.ice >= cargo_limit_ice and not below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    actions[unit_id] = [unit.transfer(direction, 0, unit.cargo.ice, repeat=0)]
                    #print(unit_id, "transfer")

                # not ajacent to factory, moves to closest factory
                elif not ajacent_factory and unit.cargo.ice >= cargo_limit_ice and not below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "move transfer")


            ### Finds all ore tiles, sorts by proximity to light bot
            ### Light bot logic
            if isLight:
                # decides if the bot should be assigned an ore location or find closest rubble
                on_ore_assignment = mine_assignments < light_ore_miners
                if on_ore_assignment and mine_assignments < len(closest_ore_tiles):
                    closest_ore_tile = closest_ore_tiles[mine_assignments]
                    mine_assignments += 1
                if not on_ore_assignment and rubble_assignments < len(closest_rubble_tiles):
                    rubble_assignments += 1

                power_threshold_light = 6
                below_power_threshold_light = unit.power < power_threshold_light
                power_for_dig = unit.power >= unit.dig_cost(game_state)
                recharge_need_light = math.floor(150 - unit.power)
                on_ore = all(unit.pos == closest_ore_tile)
                on_rubble = all(unit.pos == closest_rubble_tile) 


                # on ore, not on rubble, under cargo limit, not below power threshold. dig ore
                if on_ore and not on_rubble and unit.cargo.ore < cargo_limit_ore and not below_power_threshold_light:
                    actions[unit_id] = [unit.dig(repeat=0)]
                    #print(unit_id, "dig ore")
                

                # on rubble, under cargo limit, not below power threshold. dig rubble
                elif on_rubble and unit.cargo.ore < cargo_limit_ore and not below_power_threshold_light:
                    actions[unit_id] = [unit.dig(repeat=0)]
                    #print(unit_id, "dig rubble")
                

                # on ore assignment, not on ore, not on rubble, under cargo limit, not below power threshold. move towards ore
                elif on_ore_assignment and not on_ore and not on_rubble and unit.cargo.ore < cargo_limit_ore and not below_power_threshold_light:
                    direction = direction_to(unit.pos, closest_ore_tile)
                    newDirection = check_tile_occupation(game_state=game_state,
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        direction=direction,
                        player=self.player,
                        opponent=self.opp_player
                    )
                
                    if newDirection == -1:
                        actions[unit_id] = [unit.recharge(unit.power + power_threshold_light)]
                        #print(unit_id, "recharge instead of moving")
                        
                    else:
                        actions[unit_id] = [unit.move(newDirection, repeat=0)]
                        #print(unit_id, "move to ore")
                    

                # not on ore assignment, not on ore, not on rubble, under cargo limit, not below power threshold. move towards rubble
                elif not on_ore_assignment and not on_ore and not on_rubble and unit.cargo.ore < cargo_limit_ore and not below_power_threshold_light:
                    direction = direction_to(unit.pos, closest_rubble_tile)
                    newDirection = check_tile_occupation(game_state=game_state,
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        direction=direction,
                        player=self.player,
                        opponent=self.opp_player
                    )

                    if newDirection == -1:
                        actions[unit_id] = [unit.recharge(unit.power + power_threshold_light)]
                        #print(unit_id, "recharge instead of moving")
                        
                    else:
                        actions[unit_id] = [unit.move(newDirection, repeat=0)]
                        #print(unit_id, "move to rubble")


                # below power threshold, no actions in queue. recharge to power threshold
                elif below_power_threshold_light and len(unit.action_queue) < 1:
                    actions[unit_id] = [unit.recharge(power_threshold_light)]
                    #print(unit_id, "recharge")
                

                # ajacent to factory, at/over cargo limit, not below power threshold. transfer ore
                elif ajacent_factory and unit.cargo.ore >= cargo_limit_ore and not below_power_threshold_light:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    actions[unit_id] = [unit.transfer(direction, 1, unit.cargo.ore)]
                    #print(unit_id, "transfer cargo")
                

                # not ajacent to factory, at/over cargo limit, not below power threshold. move to factory
                elif not ajacent_factory and unit.cargo.ore >= cargo_limit_ore and not below_power_threshold_light:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "move to transfer cargo")

                
                # wait for recharging queue to finish
                else:
                    #print("do nothing")
                    continue
        

        return actions