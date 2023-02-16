from lux.kit import obs_to_game_state, GameState, EnvConfig
from lux.utils import direction_to, my_turn_to_place_factory
import numpy as np
import math



# Create excel spreadsheets to look at strategies for when to start producing lichen to find weather its more optimal to
#      continually grow lichen, or to hoard water until a certain turn (depending on water gathered?) and mass produce lichen then
# [X] Made graphs and have found good enough growth estimates with tables for further estimation if necessary.

# TODO Update files in repo, or move agent files to new repo. Basically move from beta to season 2.
# [X]

# TODO Clean up structure of notebook cells and segments of the algorithm to make it easier to find where what desicion is being made
# []

# TODO Move functions used by algorithm to separate file?
# []

# TODO Make the agent place a factory right next to one ice tile
# []

# TODO Make the agent update its possible placing locations by removing coordinates around placed (friendly and foe) factory tiles
# []

# TODO Update placement of factories so that they place only right next to ice tiles, with no/low rubble
#      This can be acchieved through the "board.rubble" property
# []

# TODO Update the assignments to have n heavy bots on ice gathering just outside the factory, and some light for ore collection
# []

# TODO Fix ordering system so that heavies are assigned to ice tiles right by the factory for instant dropof and charging,
#      and so that the bots are ordered to correct coordinates,
#      and so that the return to factory scheduling works.
# []


# functions used by agent
def neighbors(x, y):
    return np.array([
        (x-1, y), (x, y-1), (x+1, y), (x, y+1),
        (x-2, y), (x, y-2), (x+2, y), (x, y+2),
        (x-3, y), (x, y-3), (x+3, y), (x, y+3),
        (x-4, y), (x, y-4), (x+4, y), (x, y+4),
    ])
    # expand this to include diagonal border coordinates, up to 3 away, or possibly make this method take a search grid range 
    # and return a np array with results from this grid range

# function used by agent for sorting list of resource locations by point x and y value
def get_ordered_list(points, x, y):
    p_list2 = sorted(points, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    #p_list = list(points)
    #p_list.sort(key= lambda p: abs(p[0] - x) + abs(p[1] - y))
    return p_list2


# function used by agent for deciding what action the unit should take to accieve its assignment
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




class Agent():
    def __init__(self, player: str, env_cfg: EnvConfig) -> None:
        self.player = player
        self.opp_player = "player_1" if self.player == "player_0" else "player_0"
        np.random.seed(0)
        self.env_cfg: EnvConfig = env_cfg

    def early_setup(self, step: int, obs, remainingOverageTime: int = 60):
        if step == 0:
            # bid 0 to not waste resources bidding and declare as the default faction
            # you can bid -n to prefer going second or n to prefer going first in placement
            return dict(faction="AlphaStrike", bid=0)
        else:
            game_state = obs_to_game_state(step, self.env_cfg, obs)

            ### finds desirable spawn coordinates to place factories
            # gets border indexes of ore coordinates and ice coordinates
            indOre = np.transpose(np.where(game_state.board.ore > 0))
            neighbOre = np.concatenate([neighbors(*i) for i in indOre])

            indIce = np.transpose(np.where(game_state.board.ice > 0))
            neighbIce = np.concatenate([neighbors(*i) for i in indIce])


            # sets all valid coordinates to 0 as only zero and one are possible 
            desirable_coordinates = np.copy(game_state.board.valid_spawns_mask)
            desirable_coordinates[desirable_coordinates == 1] = 0

            # replaces border coordinates around ore and ice with 1 values in valid spawn mask
            for row, col in neighbOre:
                try:
                    desirable_coordinates[row][col] = 1

                except IndexError:
                    continue
            
            for row, col in neighbIce:
                try:
                    desirable_coordinates[row][col] = 1

                except IndexError:
                    continue
            
            # then replaces ore and ice coordinates with 0, as these are not valid spawn locations
            for row, col in indOre:
                desirable_coordinates[row][col] = 0

            for row, col in indIce:
                desirable_coordinates[row][col] = 0


            ### factory placement period
            # how much water and metal you have in your starting pool to give to new factories
            water_left = game_state.teams[self.player].water
            metal_left = game_state.teams[self.player].metal
            
            # how many factories you have left to place
            factories_to_place = game_state.teams[self.player].factories_to_place

            # whether it is your turn to place a factory
            my_turn_to_place = my_turn_to_place_factory(game_state.teams[self.player].place_first, step)
            if factories_to_place > 0 and my_turn_to_place:
                # we will spawn our factory in a random location with 150 metal and water if it is our turn to place
                potential_spawns = np.array(list(zip(*np.where(desirable_coordinates == 1))))
                spawn_loc = potential_spawns[np.random.randint(0, len(potential_spawns))]
                return dict(spawn=spawn_loc, metal=150, water=150)

        # returns empty dictionary if no decisions were reached
        return dict()



    def act(self, step: int, obs, remainingOverageTime: int = 60):
        # info used to make decisions in the act phase
        actions = dict()
        game_state: GameState = obs_to_game_state(step, self.env_cfg, obs)
        factories = game_state.factories[self.player]

        ### creation of bots
        for unit_id, factory in factories.items():
            if factory.power >= self.env_cfg.ROBOTS["HEAVY"].POWER_COST and \
            factory.cargo.metal >= self.env_cfg.ROBOTS["HEAVY"].METAL_COST:
                # sets factory with unit_id to construct light bot
                actions[unit_id] = factory.build_heavy()

        # gathers relevant info for decision making
        units = game_state.units[self.player]
        factory_tile_locations = np.array([factory.pos for id, factory in factories.items()])
        factories_midpoint_x = np.mean([factory[0] for factory in factory_tile_locations])
        factories_midpoint_y = np.mean([factory[1] for factory in factory_tile_locations])
        factories_midpoint_coordinate = np.array([factories_midpoint_x, factories_midpoint_y])


        ### finds all ice tiles and ore tiles, sorts by proximity to factory 
        ice_map = game_state.board.ice 
        ice_tile_locations = np.argwhere(ice_map == 1) # numpy magic to get the position of every ice tile
        sorted_ice_locations = get_ordered_list(points=ice_tile_locations, x=factories_midpoint_coordinate[0], y=factories_midpoint_coordinate[1])

        ore_map = game_state.board.ore
        ore_tile_locations = np.argwhere(ore_map == 1)
        sorted_ore_locations = get_ordered_list(points=ore_tile_locations, x=factories_midpoint_coordinate[0], y=factories_midpoint_coordinate[1])


        ### distributes 'tile assignments' for ore and ice tiles to 40 and 60 percent of the bots available, bots left are given ice assignments
        num_bots = len(units)
        ice_assignments = math.floor((num_bots * 0.4))
        ore_assignments = math.floor((num_bots * 0.6))

        # TODO Update the assignments to have n heavy bots on ice gathering just outside the factory, and some light for ore collection
        # as long as distribution of assignments sum to 100%, only one remaining bot is required to give extra assignment
        if (ice_assignments + ore_assignments) < num_bots:
            ice_assignments += 1
            ore_assignments += 1

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
                adjacent_to_factory = np.mean((closest_factory_tile - unit.pos) ** 2) == 0

                if adjacent_to_factory and (unit.cargo.ice > 0):
                    direction = direction_to(unit.pos, closest_factory_tile)
                    actions[unit_id] = [unit.transfer(direction, 0, unit.cargo.ice, repeat=0)]
                    continue

                if adjacent_to_factory and (unit.cargo.ore > 0):
                    direction = direction_to(unit.pos, closest_factory_tile)
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
                assignment_count += 1
                continue


        return actions