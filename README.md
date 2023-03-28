# My LuxAI-S2 Algorithm Submission

## Done TODOS
### Strategy
* Create excel spreadsheets to look at strategies for when to start producing lichen to find weather its more optimal to
     continually grow lichen, or to hoard water until a certain turn (depending on water gathered?) and mass produce lichen then
[X] Made graphs and have found good enough growth estimates with tables for further estimation if necessary.
* TODO Observe the total ammount of water possible to gather with 1 heavy bot
[X]
TODO Develop formula for when to start watering to optimize so that factory water, and a variable (average water gathering from 1 heavy),
     find the optimal turn for beginning watering
[X]
TODO Make sure coords round factory tiles (2 layers) are clear of rubble
[X]
* TODO Remove enemy factory tile coordinates from closest rubble low list to avoid clearing out rubble for opponent
[X]
* TODO Make bots with ore assignments fetch power from factory with "pickup", as power is not utilized to full extent
[X]

### Placement choice
* TODO Make the agent place a factory right next to one ice tile
[X]
* TODO Make the agent update its possible placing locations by removing coordinates around placed (friendly and foe) factory tiles
[X]
* TODO Fix bug where only 4 out of 5 factories are built 
[X]
* TODO Fix placement of factories? So that all place near ice
[X]
* TODO Fix bug where not every factory is watering lichen
[X]
* TODO Take second look at spawn selection functions as this might be running into "overtime" making me miss out on placing some crucial factories
     This can be reduced by looking at efficiency gains that can be made in the startup section
[X]
* TODO Take second look at border coordinate function to fix it so that it removes first and second rows on all 4 sides
[X]
* TODO, make selection of spawn points less random, by sorting for rubble value, and selecting first in list, not random
[X]
* TODO Update spawn selection so that spawn rubble values are set to average rubble value for the 9 factory tiles and one tile around these.
     This allows selecting areas with lower rubble
[X]
* TODO Check if bidding 10 water and metal affects the number of factories that can be placed, if factories dont cost metal, bid 1 as default. This
      secures the first, best location more often. Combined with selection of 3rd best spot forces opponent to choose more bad spots with more rubble
[X]

### Heavy behaviour
* TODO Update the assignments to have n heavy bots on ice gathering just outside the factory, and some light for ore collection
[X]
* TODO Fix ordering system so that heavies are assigned to ice tiles right by the factory for instant dropof and charging,
     and so that the bots are ordered to correct coordinates,
     and so that the return to factory scheduling works.
[X]
* TODO Optimize heavy bots ice collection, by increasing storage limit, and or tweaking their power level threshold
[X]
* TODO Check if there is logic in heavy and light bots that can be merged to reduce complexity in logic? If not, make sure google sheet matricees
     are up to date
[X]
* TODO Doing nothing equals recharging. Rewrite logic for light bots so that they do nothing instead of queueing 6 turn imobilizing recharge action.
[X]
* TODO Heavy bot sometimes dont have enough power to move back to factory if there is one tile between ice tile being mined and factory
[X]
* TODO Make heavy bots more defensive, and move to factory tile if low on power (made overwatch decision more random for moving home)
[X]
* TODO Fix the way heavy bots find their closest ice tile to look for manhattan distance from the heavy bots "home factory". And make further
     measures to ensure they select only ice tiles that are on factory ajacent tiles. Mabye filter the ice tiles by the condition if they are
     ajacent to a factory tile?
[X]
* TODO Add behaviour to heavy bot that checks its home factory water, and directly surrounding rubble tiles. If the home factory has a certain
      level of water, while there are neighbouring tiles with rubble, send the bot to clear this instead of mining ice.
[X]

### Light behaviour
* TODO Incorporate a sorting function for rubble tiles as well as proximity to the light bot (changed to factory tile with closest proximity to unit),
     this allows "bootstrapping" from start pos in factory
[X]
* TODO Make function that gets the coordinates around factories with only rubble on, and assigns these tiles (by filtering for proximity) to light bots
[X]
* TODO Take second look at non colision function. Also make ice tiles "no go" for lights.
     Function should be rewritten so that bot logic places "tile bookings" for where they want to go. 
     If the booking is in the array of existing bookings, check opposite axis directions if in "tile bookings".
     If these are not in the np array, select that direction and return the direction.
     If doing nothing (recharging), place a booking for their current tile
     This booking system should consist of a tuple of two np arrays, that indicate a vector for that unit.
     Start function by checking straight directions from bot pos, if not occupied, do final check if tile is in "tile bookings" array.
     This way diagonal directions can be accounted for, for friendly bots
[X]
* TODO Add function that checks surrounding tiles for hostiles if on ice or factory tile, that affects behaviour of heavy bots (moves bot on hostile heavy bot on ajacent tile, ambush this bot by moving onto this tile)
[X]
* TODO Set rubble clearing bots to collect power from closest factory if it goes above a certain level (nice synergy with last few turns)
 [X]
* TODO Add bot behaviour for 1 light bot to serve as assistance for a heavy ice miner, providing power to it, thus achieving the max potential
      ice harvesting from this method.
[X]
* TODO Modify light overwatch to try to move the bot towards home factory if heavy tries moving on its center
[X]
* TODO Modify light overwatch to fall back to factory if power below a certain level so that they winn more battles
[X]
* TODO Modift light overwatch so that assisting bots dont attack other light bots
[X]
* TODO Modify light overwatch so that bots are triggered by hostile light bots when on factory tile, but so that assisting bots dont attack
[X]
* TODO Add check on light overwatch to see if tile it wants to attack is in move_bookings, if it is, dont move there, but move towards home factory
[X]
* TODO Convert move_bookings to a dictionary, as i think the number of times it is used justifies usage of this as opposed to an array.
[X]

### Misc
* TODO Update files in repo, or move agent files to new repo. Basically move from beta to season 2.
[X]
* TODO Clean up structure of notebook cells and segments of the algorithm to make it easier to find where what desicion is being made
[X]
* TODO Introduce switch for light bots toggling between curren behaviour (after turn 200), and creation of a "human chain" on a ore tile, if 
      there is one ore tile N distance away from the factory center tile (can find where center coords are defined).
      Here one light bot is assigned as miner, while rest follows, and charges during daytime, and transfers M power forwards to mining bot.
      The mining bot transfers ore towards factory tile, and supporting bots towards factory, if bot is on coordinate towards factory.
      If no bot can recieve, the light bot starts moving towards factory to drop off ore (it has ore greater than free cargo space)
[X]
* TODO Look over all sorts for tiles to ensure they look for the closest tiles the right way
[X]