# TODO can be replaced with the interval method for searching in a square radius, perhaps not required to have else vision

# TODO replace use of this function with the interval function
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


def get_tiles_by_interval(x, y, interval_x, interval_y):
    coordinates = np.array(
        [(x + n, y + m) for n in range((-1 * interval_x), interval_x +1) for m in range((-1 * interval_y), interval_y +1) if (0 <= (x + n) <= 47) and (0 <= (y + m) <= 47)]
    )
    return coordinates
'''
    ^ interval y
    [ ][ ][ ]
    [ ][ ][ ]
    [ ][ ][ ]
    interval x ->
'''


# TODO use this so i can remove opponent factory tile neighbours from rubble removal
def get_surrounding_tiles_by_interval(x, y, interval_x, interval_y):
    coordinates = np.array(
        [
            (x + n, y + m) for n in range((-1 * interval_x), interval_x +1) for m in range((-1 * interval_y), interval_y +1) if
            (0 <= (x + n) <= 47) and (n < -1 or n > 1 or m < -1 or m > 1) and
            (0 <= (y + m) <= 47) #and (m < -1 or m > 1)
        ]
    )
    return coordinates 
'''
X = not marked factory tiles
    ^ interval y
    [ ][ ][ ][ ][ ][ ][ ]
    [ ][ ][ ][ ][ ][ ][ ]
    [ ][ ][X][X][X][ ][ ]
    [ ][ ][X][X][X][ ][ ]
    [ ][ ][X][X][X][ ][ ]
    [ ][ ][ ][ ][ ][ ][ ]
    [ ][ ][ ][ ][ ][ ][ ]
    interval x ->
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
        # startes at layer 2 to give buffer, avoiding placing factory on resource
        (x-2, y), (x, y-2), # left and top 
        (x+2, y), (x, y+2), # right and bottom 

        (x-2, y-1), (x-1, y-2), # (x-2, y-2), # left and top diagonals 
        (x+2, y+1), (x+1, y+2), # (x+2, y+2), # right and bottom diagonals 

        (x+2, y-1), (x+1, y-2), # (x+2, y-2), # right and top diagonals 
        (x-2, y+1), (x-1, y+2), # (x-2, y+2), # left and bottom diagonals 
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


def expedition_check_tile_occupation(game_state, unit_x, unit_y, direction, player, opponent):
    friendly_bots = game_state.units[player]
    hostile_bots = game_state.units[opponent]

    friendly_coords = [(unit.pos[0], unit.pos[1]) for (unit_id, unit) in friendly_bots.items()]
    hostile_lights = [(unit.pos[0], unit.pos[1]) for unit_id, unit in hostile_bots.items() if unit.unit_type == 'LIGHT']
    hostile_heavys = [(unit.pos[0], unit.pos[1]) for unit_id, unit in hostile_bots.items() if unit.unit_type == 'HEAVY']

    # a[1] = direction (1 = up, 2 = right, 3 = down, 4 = left)
    # move_deltas = np.array([0, -1], [1, 0], [0, 1], [-1, 0]])
    bot_center = (unit_x, unit_y)
    bot_up = (unit_x, unit_y - 1)
    bot_right = (unit_x + 1, unit_y)
    bot_down = (unit_x, unit_y + 1)
    bot_left = (unit_x - 1, unit_y)

    # checks if no friendly is on direction tile, if none, direction remains, else set to 0
    up_friendly = (bot_up not in friendly_coords) * 1
    right_friendly = (bot_right not in friendly_coords) * 2
    down_friendly = (bot_down not in friendly_coords) * 3
    left_friendly = (bot_left not in friendly_coords) * 4



    # checks if no friendly is on direction tile, if none, direction remains, else set to 0
    up_friendly = (not any(bot_up == f_pos for f_pos in friendly_coords)) * 1
    right_friendly = (not any(bot_right == f_pos for f_pos in friendly_coords)) * 2
    down_friendly = (not any(bot_down == f_pos for f_pos in friendly_coords)) * 3
    left_friendly = (not any(bot_left == f_pos for f_pos in friendly_coords)) * 4
    
    # checks if hostile bot is on direction tile, if there is one of type 'LIGHT', direction remains, else set to 0
    up_hostile = True if not any(bot_up == h_pos for h_pos in hostile_heavys) or any(bot_up == h_pos for h_pos in hostile_lights) else False
    right_hostile = True if not any(bot_right == h_pos for h_pos in hostile_heavys) or any(bot_right == h_pos for h_pos in hostile_lights) else False
    down_hostile = True if not any(bot_down == h_pos for h_pos in hostile_heavys) or any(bot_down == h_pos for h_pos in hostile_lights) else False
    left_hostile = True if not any(bot_left == h_pos for h_pos in hostile_heavys) or any(bot_left == h_pos for h_pos in hostile_lights) else False


    # sets non occupied tile directions
    up_free = up_friendly * up_hostile
    right_free = right_friendly * right_hostile
    down_free = down_friendly * down_hostile
    left_free = left_friendly * left_hostile


    # finds possible directions not occupied by friendly bots and hostile bots
    directions = [up_free, right_free, down_free, left_free]
    if direction in directions:
        return direction

    # if all direction tiles occupied with friendly bots, recharge recommended
    return 0
'''
       []1
    []2[]0[]4
       []3
''' 




# function used by Archimedes to check if tile is occupied by other bots
def check_tile_occupation(game_state, unit_x, unit_y, direction, booked_coords, player, opponent):
    friendly_bots = game_state.units[player]
    hostile_bots = game_state.units[opponent]

    friendly_coords = {(unit.pos[0], unit.pos[1]): unit.unit_type for (unit_id, unit) in friendly_bots.items()}
    hostile_coords = {(unit.pos[0], unit.pos[1]): unit.unit_type for (unit_id, unit) in hostile_bots.items()}

    # coords relative to bot position
    # a[1] = direction (1 = up, 2 = right, 3 = down, 4 = left)
    # move_deltas = np.array([0, -1], [1, 0], [0, 1], [-1, 0]])
    bot_center = (unit_x, unit_y)
    bot_up = (unit_x, unit_y - 1)
    bot_right = (unit_x + 1, unit_y)
    bot_down = (unit_x, unit_y + 1)
    bot_left = (unit_x - 1, unit_y)


    # checks if no friendly is on direction tile, if none, direction remains, else set to 0
    up_friendly = (bot_up not in friendly_coords and (bot_up not in booked_coords)) * 1
    right_friendly = (bot_right not in friendly_coords and (bot_right not in booked_coords)) * 2
    down_friendly = (bot_down not in friendly_coords and (bot_down not in booked_coords)) * 3
    left_friendly = (bot_left not in friendly_coords and (bot_left not in booked_coords)) * 4

    # checks if hostile bot is on direction tile, if there is one of type 'LIGHT', direction remains, else set to 0
    up_hostile = True if (bot_up not in hostile_coords) or (bot_up in hostile_coords and hostile_coords[bot_up] == 'LIGHT' ) else False
    right_hostile = True if (bot_right not in hostile_coords) or (bot_right in hostile_coords and hostile_coords[bot_right] == 'LIGHT' ) else False
    down_hostile = True if (bot_down not in hostile_coords) or (bot_down in hostile_coords and hostile_coords[bot_down] == 'LIGHT' ) else False
    left_hostile = True if (bot_left not in hostile_coords) or (bot_left in hostile_coords and hostile_coords[bot_left] == 'LIGHT' ) else False

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
 
    # if all direction tiles occupied with friendly bots, recharge recommended
    return 0
'''
       []1
    []2[]0[]4
       []3
'''

def heavy_overwatch(unit, on_factory, closest_factory_tile, game_state, opponent):
    unit_x = unit.pos[0]
    unit_y = unit.pos[1]
    # gets hostile bot coords
    hostile_bots = game_state.units[opponent]
    hostile_coords_heavy = [(unit.pos[0], unit.pos[1]) for (unit_id, unit) in hostile_bots.items() if unit.unit_type == 'HEAVY']

    # coords relative to bot position
    # a[1] = direction (1 = up, 2 = right, 3 = down, 4 = left)
    # move_deltas = np.array([0, -1], [1, 0], [0, 1], [-1, 0]])
    bot_up = (unit_x, unit_y - 1)
    bot_right = (unit_x + 1, unit_y)
    bot_down = (unit_x, unit_y + 1)
    bot_left = (unit_x - 1, unit_y)

    # checks if hostile bot is on directly neighbouring tiles, and is of type HEAVY
    up_hostile = True if (bot_up in hostile_coords_heavy) else False
    right_hostile = True if (bot_right in hostile_coords_heavy) else False
    down_hostile = True if (bot_down in hostile_coords_heavy) else False
    left_hostile = True if (bot_left in hostile_coords_heavy) else False
    hostile_on_flank = (up_hostile or right_hostile or down_hostile or left_hostile)

    # check for heavy hostiles on opposing tiles, if on factory tile move on hostile tile, else move to closest factory tile 
    if on_factory and hostile_on_flank:
        up_target = up_hostile * 1
        right_target = right_hostile * 2
        down_target = down_hostile * 3
        left_target = left_hostile * 4
        directions = [up_target, right_target, down_target, left_target]
        target_dir = [target for target in directions if target != 0]

        return random.choice(target_dir)
    
    # attack if energy is greater than 240, but introduced random choice to disengage and move home
    elif not on_factory and hostile_on_flank:
        if unit.power > 240:
            up_target = up_hostile * 1
            right_target = right_hostile * 2
            down_target = down_hostile * 3
            left_target = left_hostile * 4
            directions = [up_target, right_target, down_target, left_target, direction_to(np.array([unit_x, unit_y]), target=closest_factory_tile)]
            target_dir = [target for target in directions if target != 0]
            return random.choice(target_dir)
        
        else:
            return direction_to(src=np.array([unit_x, unit_y]), target=closest_factory_tile)
    
    else:
        return False


def light_overwatch(unit, on_factory, on_ice_assistance, home_factory, booked_coords, overwatch_priority, game_state, player, opponent):
    # gets hostile bot coords
    hostile_bots = game_state.units[opponent]
    hostile_coords_heavy = [(unit.pos[0], unit.pos[1]) for (unit_id, unit) in hostile_bots.items() if unit.unit_type == 'HEAVY']
    hostile_coords_light = [(unit.pos[0], unit.pos[1]) for (unit_id, unit) in hostile_bots.items() if unit.unit_type == 'LIGHT']

    # coords relative to bot position
    # a[1] = direction (1 = up, 2 = right, 3 = down, 4 = left)
    # move_deltas = np.array([0, -1], [1, 0], [0, 1], [-1, 0]])
    unit_x = unit.pos[0]
    unit_y = unit.pos[1]
    bot_center = (unit_x, unit_y)
    bot_up = (unit_x, unit_y - 1)
    bot_right = (unit_x + 1, unit_y)
    bot_down = (unit_x, unit_y + 1)
    bot_left = (unit_x - 1, unit_y)

    # checks if light hostile bot is on directly neighbouring tiles
    up_hostile_light = True if (bot_up in hostile_coords_light) else False
    right_hostile_light = True if (bot_right in hostile_coords_light) else False
    down_hostile_light = True if (bot_down in hostile_coords_light) else False
    left_hostile_light = True if (bot_left in hostile_coords_light) else False
    light_hostile_on_flank = (up_hostile_light or right_hostile_light or down_hostile_light or left_hostile_light)

    # checks if heavy hostile bot is on directly neighbouring tiles
    up_hostile_heavy = True if (bot_up in hostile_coords_heavy) else False
    right_hostile_heavy = True if (bot_right in hostile_coords_heavy) else False
    down_hostile_heavy = True if (bot_down in hostile_coords_heavy) else False
    left_hostile_heavy = True if (bot_left in hostile_coords_heavy) else False
    heavy_hostile_on_flank = (up_hostile_heavy or right_hostile_heavy or down_hostile_heavy or left_hostile_heavy)


    # if only heavy hostile on flank, returns direction that is away from heavy hostile
    if heavy_hostile_on_flank and not light_hostile_on_flank and not on_factory:
        if up_hostile_heavy:
            return 3
        elif right_hostile_heavy:
            return 4
        elif down_hostile_heavy:
            return 1
        elif left_hostile_heavy:
            return 2
    
    # if light hostile on flank, attack
    elif light_hostile_on_flank and unit.power >= 20 and not on_ice_assistance:
        up_target = up_hostile_light * 1
        right_target = right_hostile_light * 2
        down_target = down_hostile_light * 3
        left_target = left_hostile_light * 4
        directions = [up_target, right_target, down_target, left_target]
        target_dir = [target for target in directions if target != 0]
        return random.choice(target_dir)

    # if light on flank, but below unit power threshold
    elif light_hostile_on_flank and unit.power < 20 and not on_ice_assistance:
        direction = direction_to(unit.pos, home_factory)
        newDirection = check_tile_occupation(
            game_state=game_state,
            unit_x=unit_x,
            unit_y=unit_y,
            direction=direction,
            booked_coords=booked_coords,
            player=player,
            opponent=opponent
        )
        booked_coords[coord_from_direction(x=unit_x, y=unit_y, direction=newDirection)] = overwatch_priority
        return newDirection

    # move home if unit position is booked
    elif bot_center in booked_coords:
        evasion_direction = direction_to([unit_x, unit_y], home_factory)
        newDirection = check_tile_occupation(
            game_state=game_state,
            unit_x=unit_x,
            unit_y=unit_y,
            direction=evasion_direction,
            booked_coords=booked_coords,
            player=player,
            opponent=opponent
        )
        booked_coords[coord_from_direction(x=unit_x, y=unit_y, direction=newDirection)] = overwatch_priority
        return newDirection

    # if no overwatch triggers return this status
    else:
        return False


def get_closest_factory_tile(unit_x, unit_y, factories):
    closest_factory = sorted([(factory.pos, factory) for factory_id, factory in factories.items()], key=lambda f: (f[0][0] - unit_x)**2 + (f[0][1] - unit_y)**2)[0]
    factory_pos = closest_factory[0]
    factory = closest_factory[1]
    return (factory_pos, factory)


# checks if any other bots have booked the coordinate, and keeps track of how many have booked the same coordinate through move_bookings
def book_coordinate(unit_id, booking_coordinate, move_bookings):
    if booking_coordinate in move_bookings:
        move_bookings[booking_coordinate].append(unit_id)
        return len(move_bookings[booking_coordinate])

    elif booking_coordinate not in move_bookings:
        move_bookings[booking_coordinate] = [unit_id]
        return len(move_bookings[booking_coordinate])


class Archimedes_Lever():
    def __init__(self, player: str, env_cfg: EnvConfig) -> None:
        self.player = player
        self.opp_player = "player_1" if self.player == "player_0" else "player_0"
        self.env_cfg: EnvConfig = env_cfg

        # dictionary for keeping track of bots home factory by unit_id and home coord
        self.home_factory = dict()

    # Setup of early game
    def early_setup(self, step: int, obs, remainingOverageTime: int = 60):
        if step == 0:
            # bid 0 to not waste resources bidding and declare as the default faction
            # you can bid -n to prefer going second or n to prefer going first in placement
            return dict(faction="AlphaStrike", bid=10)
        else:
            game_state = obs_to_game_state(step, self.env_cfg, obs)
            my_turn_to_evaluate_spawns = my_turn_to_place_factory(game_state.teams[self.player].place_first, step)

            ### Using numpy arrays, maps out desirable spawn locations
            # only processes map on my placement turns
            if my_turn_to_evaluate_spawns:
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


                # filters spawn coords for outside map coords (and those doesn't include spawns on map border), and those overlapping ivalid or occupied tiles
                x_search_radius = 3
                y_search_radius = 3
                array_inside_map_spawns = [
                    (np.array(
                        [spawn_coord[0], spawn_coord[1]]), # first element in tuple is np array coordinate
                        np.mean(                        # second elment in tuple is mean rubble value from ajacent coords
                            [game_state.board.rubble[c[0]][c[1]] for c in get_surrounding_tiles_by_interval(x=spawn_coord[0], y=spawn_coord[1], interval_x=x_search_radius, interval_y=y_search_radius)]
                        )
                    ) for spawn_coord in array_spawns if (2 <= spawn_coord[0] <= 45) and (2 <= spawn_coord[1] <= 45)
                ]
                array_valid_spawns = [coord for coord in array_inside_map_spawns if 
                    all(all(coord[0] == inv_coord) == False for inv_coord in array_invalid_coords) and 
                    all(all(coord[0] == occ_coord) == False for occ_coord in array_occupied_coords)
                ]

                '''
                # TODO mirror filtering here
                desirable_coordinates_filtered = np.copy(game_state.board.valid_spawns_mask)
                desirable_coordinates_filtered[desirable_coordinates_filtered == 1] = 0
                for coord in array_valid_spawns:
                    desirable_coordinates_filtered[coord[0]][coord[1]] == 1
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
                
                # how many factories you have left to place, and if its my turn to place
                factories_to_place = game_state.teams[self.player].factories_to_place
                my_turn_to_place = my_turn_to_place_factory(game_state.teams[self.player].place_first, step)

                if factories_to_place > 0 and my_turn_to_place and len(array_valid_spawns) > 0:
                    array_sorted_spawns = sorted(array_valid_spawns, key=lambda coord: coord[1])
                    #print("spawn choices", len(array_sorted_spawns))
                    #print(array_sorted_spawns[0][0])
                    spawn_loc = array_sorted_spawns[0][0]
                    if water_left < 150 and metal_left < 150:
                        return dict(spawn=spawn_loc, metal=metal_left, water=water_left)
                    else:
                        return dict(spawn=spawn_loc, metal=150, water=150)

                else:
                    # returns empty dictionary if there are no  valid spawn points to choose from
                    return dict()

            else:
                # returns empty dictionary if no decisions were reached
                return dict()


    
    # Setup of logic in the act phase
    def act(self, step: int, obs, remainingOverageTime: int = 60):
        # game state and other variables
        actions = dict()
        game_state: GameState = obs_to_game_state(step, self.env_cfg, obs)
        game_state.teams[self.player].place_first


        ### Factory decision making
        factories = game_state.factories[self.player]
        factory_tiles, factory_units, factory_centers = [], [], []
        for unit_id, factory in factories.items():
            center = factory.pos
            tiles = get_factory_tiles_from_center(x=center[0], y=center[1])
            factory_centers += [center]
            for tile in tiles:
                factory_tiles += [tile]
            factory_units += [factory]
        factory_tiles = np.array(factory_tiles)

        hostile_factory_centers, hostile_factory_tiles = [], []
        for h_unit_id, h_factory in game_state.factories[self.opp_player].items():
            center = h_factory.pos
            hostile_factory_centers.append(center)

            tiles = get_factory_tiles_from_center(x=center[0], y=center[1])
            for tile in tiles:
                hostile_factory_tiles += [tile]
        hostile_factory_tiles = np.array(hostile_factory_tiles)

        # Creation of bots
        heavy_bot_cost = self.env_cfg.ROBOTS["HEAVY"]
        light_bot_cost = self.env_cfg.ROBOTS["LIGHT"]

        # heavy bots
        for unit_id, factory in factories.items():
            center_occupied = any((factory.pos[0], factory.pos[1]) == (unit.pos[0], unit.pos[1]) for unit_id, unit in game_state.units[self.player].items())
            #print(center_occupied, (factory.pos[0], factory.pos[1]), [unit.pos for unit_id, unit in game_state.units[self.player].items()])
            if factory.power >= heavy_bot_cost.POWER_COST and factory.cargo.metal >= heavy_bot_cost.METAL_COST and not center_occupied:
                actions[unit_id] = factory.build_heavy()
        
        # light bots
        if game_state.real_env_steps > 1:
            center_occupied = any((factory.pos[0], factory.pos[1]) == (unit.pos[0], unit.pos[1]) for unit_id, unit in game_state.units[self.player].items())
            #print(center_occupied, (factory.pos[0], factory.pos[1]), [unit.pos for unit_id, unit in game_state.units[self.player].items()])
            for unit_id, factory in factories.items():
                if factory.power >= light_bot_cost.POWER_COST and factory.cargo.metal >= light_bot_cost.METAL_COST and not center_occupied:
                    actions[unit_id] = factory.build_light()


        # Watering lichen if at right turn
        growth_turn = 990 - 250 # calculations suggenst 77 turns prior
        turns_left = 988 - game_state.real_env_steps
        grow = game_state.real_env_steps >= growth_turn
        for factory_id, factory in factories.items():
            water_cost_reactor = turns_left
            water_per_turn = 3.2
            
            base_water_cost = (factory.cargo.water - water_cost_reactor + (water_per_turn * turns_left))
            water_cost_threshold = (factory.water_cost(game_state) * turns_left)
            water_formula = base_water_cost > water_cost_threshold and factory.cargo.water > factory.water_cost(game_state)

            # UNCOMMENT FOR TESTING OF LICHEN GROWTH
            '''
            if factory_id == 'factory_0' or factory_id == 'factory_1':
                water_gathered = factory.cargo.water - 150 + game_state.real_env_steps
                factory_lichen = 0
                lichen_strain_tiles = np.argwhere(game_state.board.lichen_strains == factory.strain_id)
                for tile in lichen_strain_tiles:
                    factory_lichen += game_state.board.lichen[tile[0]][tile[1]]

                print(str(factory.power) + "," +  str(water_gathered) + ',' + str(factory.cargo.water) + "," + str(factory.water_cost(game_state)) + ',' + str(factory_lichen))

            if(factory.can_water(game_state) and factory.power < 2000 and factory.cargo.water > 150):
                actions[factory_id] = factory.water()
            '''

            factory_power_formula = factory.can_water(game_state) and factory.power < 1500 and factory.cargo.water > 20 and factory.water_cost(game_state) < 3 and (game_state.real_env_steps >= 12)
            if (game_state.real_env_steps >= growth_turn and water_formula) or (factory_power_formula):
                actions[factory_id] = factory.water()

        ### Finds all ice and ore tiles
        ice_map = game_state.board.ice 
        ore_map = game_state.board.ore 
        rubble_map = game_state.board.rubble
        ice_tile_locations = np.argwhere(ice_map == 1) # numpy magic to get the position of every ice tile
        ore_tile_locations = np.argwhere(ore_map == 1) # numpy magic to get the position of every ore tile
        rubble_tile_locations = np.argwhere(rubble_map > 0) # numpy magic to get the position of every rubble tile
        rubble_tile_locations_low_rubble = np.argwhere(rubble_map <= 20)

        # sets hostile rubble mask
        hostile_rubble_mask = np.zeros((48, 48))
        hostile_factory_rubble = np.concatenate([
            get_surrounding_tiles_by_interval(
                x=hostile_factory_center[0],
                y=hostile_factory_center[1],
                interval_x=6,
                interval_y=6
            ) for hostile_factory_center in hostile_factory_centers
        ], axis=0)
        
        for tile in hostile_factory_rubble:
            hostile_rubble_mask[tile[0]][tile[1]] = 1


        units = game_state.units[self.player]


        ### Specifies assignments for heavy and light bots
        light_ice_supporters = len(factories)
        ice_support_assignments = 0
        rubble_assignments = 0
        power_assignments = 0

        # action priority values
        overwatch_priority = 6
        pickup_priority = 5
        transfer_priority = 4
        dig_priority = 3
        move_priority = 2
        recharge_priority = 1

        # booked tiles for avoiding 
        move_bookings = {}


        for unit_id, unit in units.items():
            # sets factory that built unit as home factory
            if unit_id not in self.home_factory:
                self.home_factory[unit_id] = get_closest_factory_tile(
                    unit_x=unit.pos[0],
                    unit_y=unit.pos[1],
                    factories=factories
                )

            # info about closest map tiles
            closest_factory_tile = sorted(factory_tiles, key=lambda p: (p[0] - unit.pos[0])**2 + (p[1] - unit.pos[1])**2 )[0]
            closest_hostile_factory_tile = sorted(hostile_factory_tiles, key=lambda p: abs(p[0] - unit.pos[0]) + abs(p[1] - unit.pos[1]) )[0]
            closest_ice_tile = sorted(ice_tile_locations, key=lambda p: (p[0] - self.home_factory[unit_id][0][0])**2 + (p[1] - self.home_factory[unit_id][0][1])**2 )[0]
            
            cargo_limit_ice = 960
            on_factory = all(unit.pos == closest_factory_tile)
            ajacent_factory = 1 >= (abs(unit.pos[0] - closest_factory_tile[0]) + abs(unit.pos[1] - closest_factory_tile[1]))
            ajacent_hostile_factory = 1 >= (abs(unit.pos[0] - closest_hostile_factory_tile[0]) + abs(unit.pos[1] - closest_hostile_factory_tile[1]))
            
            

            # relevant info for light and heavy bots
            home_factory_tile = self.home_factory[unit_id][0]
            isHeavy = unit.unit_type == 'HEAVY'
            isLight = unit.unit_type == 'LIGHT'


             

        
            ### Heavy bot logic
            if isHeavy:
                # sets new home factory if original died
                if len([(factory_id, factory) for factory_id, factory in factories.items() if all(self.home_factory[unit_id][0] == factory.pos)]) == 0:
                    self.home_factory[unit_id] = get_closest_factory_tile(
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        factories=factories
                    )

                # info about unit's home factory power and resources
                home_factory = [(factory_id, factory) for factory_id, factory in factories.items() if all(self.home_factory[unit_id][0] == factory.pos)]

                #print('heavy', unit_id, unit.pos, unit.power)
                below_power_threshold_heavy = unit.power <= 100
                below_power_move_heavy = unit.power <= 50
                free_cargo_ice = unit.cargo.ice < cargo_limit_ice
                recharge_need_heavy = math.floor(3000 - unit.power)
                on_ice = all(unit.pos == closest_ice_tile)

                # condition for when heavy is set to clear rubble
                on_rubble_clearing = (home_factory[0][1].cargo.water) > 500 and 0 != sum(
                    [game_state.board.rubble[tile[0]][tile[1]] for tile in get_surrounding_tiles_by_interval(
                        x=home_factory[0][1].pos[0], 
                        y=home_factory[0][1].pos[1], 
                        interval_x=2,
                        interval_y=2
                    ) if game_state.board.ore[tile[0]][tile[1]] != 1]
                ) and (
                    unit.power > below_power_threshold_heavy
                )
                #print(on_rubble_clearing, home_factory[0][0], home_factory[0][1].pos, home_factory[0][1].power, home_factory[0][1].cargo.water)
                if on_rubble_clearing:
                    closest_rubble_tiles = sorted(rubble_tile_locations, key=lambda p: abs(p[0] - unit.pos[0]) + abs(p[1] - unit.pos[1]))
                    closest_rubble_tile = closest_rubble_tiles[0]
                    on_rubble = all(unit.pos == closest_rubble_tile)
                    factory_rubble_tiles = [coord for coord in get_surrounding_tiles_by_interval(
                        x=home_factory[0][1].pos[0],
                        y=home_factory[0][1].pos[1],
                        interval_x=2,
                        interval_y=2
                    )]

                    closest_factory_rubble_tile = sorted([tile for tile in factory_rubble_tiles if 
                        (game_state.board.rubble[tile[0]][tile[1]] != 0) and 
                        (game_state.board.ore[tile[0]][tile[1]] != 1)
                    ], key=lambda p: (game_state.board.rubble[p[0]][p[1]]))[0]
                    #print(unit_id, closest_factory_rubble_tile)


                # has hostile HEAVY on flank, moves to attack, or to factory tile if not already on one
                overwatch_check = heavy_overwatch(
                    unit=unit,
                    on_factory=on_factory,
                    closest_factory_tile=closest_factory_tile,
                    game_state=game_state,
                    opponent=self.opp_player
                )
                if overwatch_check != False:
                    #move_bookings[coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check)] = [unit_id]
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.move(overwatch_check, repeat=0)]
                    continue

                ### Clearing factory rubble
                # on rubble clearing, on rubble, not below power limit. Dig rubble
                elif on_rubble_clearing and on_rubble and not below_power_threshold_heavy:
                    #move_bookings[(unit.pos[0], unit.pos[1])] = dig_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.dig(repeat=0)]
                    #print(unit_id, "clearing factory rubble")
                    continue

                # on rubble clearing, not on rubble, not below power limit. Move to factory rubble
                elif on_rubble_clearing and not on_rubble and not below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_rubble_tile)
                    #move_bookings[coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction)] = move_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "moving to factory rubble")
                    continue

                ### Collecting ice
                # on ice, but not over cargo capacity limit. Dig ice
                elif not on_rubble_clearing and on_ice and free_cargo_ice and not below_power_threshold_heavy:
                    #move_bookings[(unit.pos[0], unit.pos[1])] = dig_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.dig(repeat=0)]
                    #print(unit_id, "digging")
                    continue
                
                # not on ice, not over cargo capacity limit. Move to ice
                elif not on_rubble_clearing and not on_ice and free_cargo_ice and not below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_ice_tile)
                    #move_bookings[coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction)] = move_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "move dig")
                    continue
                
                # on factory, below power threshold. Pickup power
                elif not on_rubble_clearing and on_factory and below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    #move_bookings[(unit.pos[0], unit.pos[1])] = pickup_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.pickup(4, recharge_need_heavy, repeat=0)]
                    #print(unit_id, "pickup power")
                    continue
                
                # not on factory, below power threshold. Move to recharge
                elif not on_rubble_clearing and not on_factory and (below_power_threshold_heavy and not below_power_move_heavy):
                    direction = direction_to(unit.pos, closest_factory_tile)
                    newDirection = check_tile_occupation(
                        game_state=game_state,
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        direction=direction,
                        booked_coords=move_bookings,
                        player=self.player,
                        opponent=self.opp_player
                    )
                    if newDirection != direction:
                        #move_bookings[(unit.pos[0], unit.pos[1])] = recharge_priority
                        num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                        print(len(move_bookings))
                        #print(unit_id, "move recharge, wait")
                        continue

                    elif newDirection == direction:
                        #move_bookings[coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction)] = move_priority
                        num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), move_bookings=move_bookings)
                        print(len(move_bookings))
                        actions[unit_id] = [unit.move(direction, repeat=0)]
                        #print(unit_id, "move recharge")
                        continue

                # ajacent to factory, over cargo limit. Transfer ice
                elif not on_rubble_clearing and ajacent_factory and not free_cargo_ice and not below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    #move_bookings[(unit.pos[0], unit.pos[1])] = transfer_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.transfer(direction, 0, unit.cargo.ice, repeat=0)]
                    #print(unit_id, "transfer")
                    continue

                # not ajacent to factory. Move to transfer
                elif not on_rubble_clearing and not ajacent_factory and not free_cargo_ice and not below_power_threshold_heavy:
                    direction = direction_to(unit.pos, closest_factory_tile)
                    #move_bookings[coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction)] = move_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.move(direction, repeat=0)]
                    #print(unit_id, "move transfer")
                    continue
                
                # not on factory, below critical power. Do nothing (recharge)
                elif not on_factory and (below_power_threshold_heavy and below_power_move_heavy):
                    #move_bookings[(unit.pos[0], unit.pos[1])] = recharge_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                    print(len(move_bookings))
                    #print(unit_id, "doing nothing (recharging)")
                    continue


            ### Light bot logic
            if isLight:
                # sets new home factory if original died
                if len([(factory_id, factory) for factory_id, factory in factories.items() if all(self.home_factory[unit_id][0] == factory.pos)]) == 0:
                    self.home_factory[unit_id] = get_closest_factory_tile(
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        factories=factories
                    )

                # info about unit's home factory power and resources
                home_factory = [(factory_id, factory) for factory_id, factory in factories.items() if all(self.home_factory[unit_id][0] == (factory.pos[0], factory.pos[1]))]
                free_power = (home_factory[0][1].power - (power_assignments * 150)) > 500

                # sorts low rubble tiles by proximity to closest factory tile to unit
                sorted_rubble_tile_vision = sorted(
                    [
                        tile for tile in rubble_tile_locations_low_rubble if 
                        (hostile_rubble_mask[tile[0]][tile[1]] != 1) and
                        (game_state.board.rubble[tile[0]][tile[1]] != 0) and
                        (game_state.board.ice[tile[0]][tile[1]] != 1) and 
                        (game_state.board.ore[tile[0]][tile[1]] != 1)
                    ], 
                    key=lambda coord: (coord[0] - closest_factory_tile[0])**2 + (coord[1] - closest_factory_tile[1])**2
                )
                lowest_rubble__tile_visible = sorted_rubble_tile_vision[0]
                

                closest_ore_tiles = sorted(ore_tile_locations, key=lambda p: abs(p[0] - self.home_factory[unit_id][0][0]) + abs(p[1] - self.home_factory[unit_id][0][1]))
                closest_ice_tiles = sorted(ice_tile_locations, key=lambda p: (p[0] - self.home_factory[unit_id][0][0])**2 + (p[1] - self.home_factory[unit_id][0][1])**2 )
                closest_rubble_tiles = sorted(rubble_tile_locations, key=lambda p: abs(p[0] - unit.pos[0]) + abs(p[1] - unit.pos[1]))
                closest_ore_tile = closest_ore_tiles[0]
                closest_ice_tile = closest_ice_tiles[0]
                closest_rubble_tile = closest_rubble_tiles[0]
                assistance_ice_tile = sorted(factory_tiles, key=lambda p: (p[0] - closest_ice_tile[0])**2 + (p[1] - closest_ice_tile[1])**2 )[0]
                

                
                # decides if the bot should be assigned to assist its heavy bot in ice collection
                on_ice_assistance = ice_support_assignments < light_ice_supporters
                if on_ice_assistance:
                    ice_support_assignments += 1

                charge_state = game_state.is_day() and unit.power < 150 and not on_factory and not self.home_factory[unit_id][1].power < 500
                power_treshold_light = 30
                below_power_threshold_light = unit.power <= power_treshold_light
                above_power_threshold_light = not below_power_threshold_light
                above_assistance_power = unit.power >= 120
                ajacent_ice = (abs(unit.pos[0] - closest_ice_tile[0]) + abs(unit.pos[1] - closest_ice_tile[1])) <= 1
                on_ore = all(unit.pos == closest_ore_tile)
                on_rubble = all(unit.pos == closest_rubble_tile)
                free_cargo_ore = unit.cargo.ore < 50

                ### performs overwatch check to see if HEAVY bots on flanks
                overwatch_check = light_overwatch(
                    unit=unit,
                    on_factory=on_factory, 
                    on_ice_assistance=on_ice_assistance, 
                    home_factory=self.home_factory[unit_id][0], 
                    booked_coords=move_bookings, 
                    overwatch_priority=overwatch_priority,
                    game_state=game_state, 
                    player=self.player, 
                    opponent=self.opp_player
                )
                if overwatch_check != False:
                    #move_bookings[coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check)] = overwatch_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.move(overwatch_check, repeat=0)]
                    #print(game_state.real_env_steps, unit_id, unit.pos, 'moving to', coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), 'overwatch triggered')
                    continue
        



                ### On ice assistance duty
                # Light bot should move onto home factory tile if not on a factory tile.
                if on_ice_assistance and not on_factory and above_power_threshold_light:
                    direction = direction_to(unit.pos, assistance_ice_tile)
                    newDirection = check_tile_occupation(
                        game_state=game_state,
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        direction=direction,
                        booked_coords=move_bookings,
                        player=self.player,
                        opponent=self.opp_player
                    )
                    #move_bookings[coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=newDirection)] = move_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.move(direction=newDirection, repeat=0)]
                    #print(game_state.real_env_steps, unit_id, unit.pos, 'moving to assistance tile')
                    continue

                # Light bot should move towards ice tile until it is ajacent to it while being on a factory tile 
                elif on_ice_assistance and on_factory and not ajacent_ice and above_assistance_power:
                    direction = direction_to(unit.pos, assistance_ice_tile)
                    target_coord = coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction)
                    move_occupied = any(target_coord == (unit.pos[0], unit.pos[1]) for unit_id, unit in units.items())
                    # if factory tile occupied, wait
                    if move_occupied:
                        #move_bookings[(unit.pos[0], unit.pos[1])] = recharge_priority
                        num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                        print(len(move_bookings))
                        continue
                    
                    # else move towards goal
                    elif not move_occupied:
                        #move_bookings[coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction)] = move_priority
                        num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), move_bookings=move_bookings)
                        print(len(move_bookings))
                        actions[unit_id] = [unit.move(direction=direction, repeat=0)]
                        #print(game_state.real_env_steps, unit_id, unit.pos, 'moving from factory tile to assistance tile')
                        continue


                # If on factory tile, ajacent to ice, and has transferrable power. Look up heavy bot on ice tile, get its demand, and transfer power
                elif on_ice_assistance and on_factory and ajacent_ice and above_assistance_power: 
                    direction = direction_to(unit.pos, closest_ice_tile)
                    target_coord = coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction)
                    target_bot = [unit for unit_id, unit in units.items() if (unit.pos[0], unit.pos[1]) == target_coord]

                    # lookup ajacent ice heavy bot power demand, transfer demand or available supply to heavy on ice
                    if len(target_bot) > 0:
                        transfer_supply = unit.power - 3
                        transfer_demand = 400 - target_bot[0].power
                        transfer_amount = transfer_demand -3 if (0 < transfer_demand <= transfer_supply) else transfer_supply
                        #move_bookings[(unit.pos[0], unit.pos[1])] = transfer_priority
                        num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                        print(len(move_bookings))
                        actions[unit_id] = [unit.transfer(direction, 4, transfer_amount)]
                        #print(game_state.real_env_steps, unit_id, unit.pos, 'transferring power')
                        continue

                    # transfer nothing if there is no heavy bot on that tile
                    elif len(target_bot) == 0: 
                        #move_bookings[(unit.pos[0], unit.pos[1])] = transfer_priority
                        num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                        print(len(move_bookings))
                        #print(game_state.real_env_steps, unit_id, unit.pos, 'did not transfer power')
                        continue


                # If on facotry tile, ajacent to ice, and has not transferrable power. Pickup power so it gets to max power.
                elif on_ice_assistance and on_factory and not above_assistance_power:
                    #move_bookings[(unit.pos[0], unit.pos[1])] = pickup_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.pickup(4, 150 - unit.power, repeat=0)]
                    #print(game_state.real_env_steps, unit_id, unit.pos, 'pickup power')
                    continue

                # if bot is lost and not above power threshold, do nothing (recharge)
                elif on_ice_assistance and not on_factory and not above_power_threshold_light:
                    #move_bookings[(unit.pos[0], unit.pos[1])] = recharge_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                    print(len(move_bookings))
                    #print(game_state.real_env_steps, unit_id, unit.pos, 'do nothing')
                    continue
                



                ### Rubble clearing duty
                # on rubble, under cargo limit, not below power threshold, not charge state. Dig rubble
                if on_rubble and free_cargo_ore and not below_power_threshold_light and not charge_state:
                    #move_bookings[(unit.pos[0], unit.pos[1])] = dig_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.dig(repeat=0)]
                    #print(unit_id, "dig rubble")


                # not on ore, not on rubble, under cargo limit, not below power threshold, not charge state. Move to rubble
                elif not on_rubble and free_cargo_ore and not below_power_threshold_light and not charge_state:
                    direction = direction_to(unit.pos, lowest_rubble__tile_visible)
                    newDirection = check_tile_occupation(
                        game_state=game_state,
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        direction=direction,
                        booked_coords=move_bookings,
                        player=self.player,
                        opponent=self.opp_player
                    )
                    #move_bookings[coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=newDirection)] = move_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.move(newDirection, repeat=0)]
                    #print(unit_id, "move to rubble")
               
                # below power threshold, not in charge state, on factory tile, nearest factory power > 1500. Pickup power
                elif below_power_threshold_light and not charge_state and on_factory and free_power:
                    power_assignments += 1
                    #move_bookings[(unit.pos[0], unit.pos[1])] = pickup_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.pickup(4, 150 - unit.power, repeat=0)]
                    #print(unit_id, "pickup power light")
                
                # below power threshold, not in charge state, not on factory tile, nearest factory power > 1500. Pickup power
                elif below_power_threshold_light and not charge_state and not on_factory and free_power:
                    power_assignments += 1
                    direction = direction_to(unit.pos, closest_factory_tile)
                    newDirection = check_tile_occupation(
                        game_state=game_state,
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        direction=direction,
                        booked_coords=move_bookings,
                        player=self.player,
                        opponent=self.opp_player
                    )
                    #move_bookings[coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=newDirection)] = move_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=overwatch_check), move_bookings=move_bookings)
                    print(len(move_bookings))
                    actions[unit_id] = [unit.move(newDirection, repeat=0)]
                    #print(unit_id, "move to factory recharge")

                # below power threshold and in a charge state. Do nothing (recharge)
                elif below_power_threshold_light and charge_state:
                    #move_bookings[(unit.pos[0], unit.pos[1])] = recharge_priority
                    num_booked_on_coord = book_coordinate(unit_id=unit_id, booking_coordinate=(unit.pos[0], unit.pos[1]), move_bookings=move_bookings)
                    print(len(move_bookings))
                    continue
                    #print(unit_id, "recharge")
        


        ### Checks if any double coordinate bookings have been placed, and diverts light bots to avoid double bookings
        light_bots = [(unit_id, unit) for unit_id, unit in units.items() if unit.unit_type == 'LIGHT']
        units_double_booked = [unit_id for u_ids in move_bookings.values() if len(u_ids) > 1]
        print(move_bookings)
        #print(game_state.real_env_steps, units_double_booked)




        # returns the final decided actions
        return actions