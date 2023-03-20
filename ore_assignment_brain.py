                # on ore expedition, on ore or rubble, free cargo ore, not below power threshold, not charge state. Dig ore/rubble
                if on_ore_expedition and (on_ore or on_rubble) and free_cargo_ore and not below_power_threshold_light:
                    move_bookings.append((unit.pos[0], unit.pos[1]))
                    actions[unit_id] = [unit.dig(repeat=0)]
                    #print(unit_id, unit.pos, unit.power, "dig ore/rubble")
                    continue

                # on ore expedition, not on ore, not on rubble, free cargo ore, not below power threshold, not charge state. Move to ore
                elif on_ore_expedition and not on_ore and not on_rubble and free_cargo_ore and not below_power_threshold_light and not charge_state:
                    direction = direction_to(unit.pos, closest_ore_tile)
                    # TODO bug is located here, seems i need to use expedition check and look for if it returns 0, then decide if i want to transfer power
                    newDirection = expedition_check_tile_occupation(
                        game_state=game_state,
                        unit_x=unit.pos[0],
                        unit_y=unit.pos[1],
                        direction=direction,
                        player=self.player,
                        opponent=self.opp_player
                    )
                    if newDirection == direction:
                        target_tile = coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=newDirection)
                        move_bookings.append(target_tile)
                        actions[unit_id] = [unit.move(newDirection, repeat=0)]
                        #print(unit_id, unit.pos, unit.power, "move to ore")
                        continue

                # on ore expedition, not on ore, not on rubble, free cargo ore, above power threshold transfer,
                # not charge state. Transfer power forward
                    elif newDirection == 0 and not on_ore:
                        target_tile = coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction)
                        transfer_available = unit.power - power_treshold_light 
                        transfer_requests = [unit.power for unit_id, unit in units.items() if (unit.pos[0], unit.pos[1]) == target_tile]
                        transfer_demand = 150 - transfer_requests[0] if len(transfer_requests) > 0 else 0
                        transfer_amount = transfer_demand if (0 <= transfer_demand <= transfer_available or transfer_demand == 0) else transfer_available

                        move_bookings.append((unit.pos[0], unit.pos[1]))
                        actions[unit_id] = [unit.transfer(direction, 4, transfer_amount)]
                        #print(unit_id, unit.pos, unit.power, "transfer power forward")
                        continue

                    else:
                        #print(unit_id, unit.pos, unit.power, "error deciding to move or transfer power")
                        continue

                # on ore expedition, not on rubble, not free cargo ore, not charge state, on factory or ajacent factory. Transfer ore factory
                elif on_ore_expedition and not on_rubble and not free_cargo_ore and not charge_state and (on_factory or ajacent_factory):
                    direction = direction_to(unit.pos, self.home_factory[unit_id])
                    move_bookings.append((unit.pos[0], unit.pos[1]))
                    actions[unit_id] = [unit.transfer(direction, 1, unit.cargo.ore)]
                    #print(unit_id, unit.pos, unit.power, "transfer ore factory")
                    continue

                # on ore expedition, not on rubble, not free cargo ore, not below power threshold, not charge state, not on factory,
                # not ajacent factory. Move to transfer ore factory
                elif on_ore_expedition and not on_rubble and not free_cargo_ore and not below_power_threshold_light and not charge_state and not (on_factory or ajacent_factory):
                    unit_side_coords = [
                        (unit.pos[0], unit.pos[1] - 1),
                        (unit.pos[0] + 1, unit.pos[1]),
                        (unit.pos[0], unit.pos[1] + 1),
                        (unit.pos[0] - 1, unit.pos[1]),
                    ]
                    light_bot_coords = [(unit.pos[0], unit.pos[1]) for unit_id, unit in units.items() if unit.unit_type == 'LIGHT']
                    bots_on_sides = [coord for coord in unit_side_coords if 
                        any(coord == l_coord for l_coord in light_bot_coords) or
                        any(coord == b_coord for b_coord in move_bookings)
                    ]
                    
                # on ore expedition, not on rubble, not free cargo ore, not charge state. Transfer ore backward
                    if len(bots_on_sides) >= 2 or (len(bots_on_sides) == 1 and on_ore):
                        sorted_bots_home = sorted(bots_on_sides, key=lambda p: (p[0] - self.home_factory[unit_id][0])**2 + (p[1] - self.home_factory[unit_id][1])**2)
                        closest_bot_home = sorted_bots_home[0]
                        direction = direction_to(unit.pos, closest_bot_home)
                        move_bookings.append((unit.pos[0], unit.pos[1]))
                        actions[unit_id] = [unit.transfer(direction, 1, unit.cargo.ore)]
                        #print(unit_id, unit.pos, unit.power, "transfer ore back")
                        continue
                    else:
                        direction = direction_to(unit.pos, self.home_factory[unit_id])
                        target_tile = coord_from_direction(x=unit.pos[0], y=unit.pos[1], direction=direction)
                        move_bookings.append(target_tile)
                        actions[unit_id] = [unit.move(direction, repeat=0)]
                        #print(unit_id, unit.pos, unit.power, "move to transfer ore to home factory")
                        continue


                # on ore expedition, below power threshold, not charge state, on factory. Pickup power Light
                elif on_ore_expedition and below_power_threshold_light and not charge_state and on_factory:
                    actions[unit_id] = [unit.pickup(4, 150 - unit.power)]
                    #print(unit_id, unit.pos, unit.power, "pickup power factory light")
                    continue

                # on ore expedition, below power threshold or charge state. Do nothing (recharge)
                elif on_ore_expedition and (below_power_threshold_light or charge_state) and not on_factory:
                    move_bookings.append((unit.pos[0], unit.pos[1]))
                    #print(unit_id, unit.pos, unit.power, "do nothing (recharge)")
                    continue

