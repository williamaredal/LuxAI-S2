# Resource types
### Transfer function:
```
def sub_resource(self, resource_id, amount):
        if resource_id == 0:
            transfer_amount = min(self.cargo.ice, amount)
        elif resource_id == 1:
            transfer_amount = min(self.cargo.ore, amount)
        elif resource_id == 2:
            transfer_amount = min(self.cargo.water, amount)
        elif resource_id == 3:
            transfer_amount = min(self.cargo.metal, amount)
        elif resource_id == 4:
            transfer_amount = min(self.power, amount)
```

# Bot stats
### Heavy bot:
```
HEAVY=UnitConfig(
    METAL_COST=100,
    POWER_COST=500,
    INIT_POWER=500,
    CARGO_SPACE=1000,
    BATTERY_CAPACITY=3000,
    CHARGE=10,
    MOVE_COST=20,
    RUBBLE_MOVEMENT_COST=1,
    DIG_COST=60,
    SELF_DESTRUCT_COST=100,
    DIG_RUBBLE_REMOVED=20,
    DIG_RESOURCE_GAIN=20,
    DIG_LICHEN_REMOVED=100,
    RUBBLE_AFTER_DESTRUCTION=10,
    ACTION_QUEUE_POWER_COST=10,
)
```

### Light bot:
```
LIGHT=UnitConfig(
    METAL_COST=10,
    POWER_COST=50,
    INIT_POWER=50,
    CARGO_SPACE=100,
    BATTERY_CAPACITY=150,
    CHARGE=1,
    MOVE_COST=1,
    RUBBLE_MOVEMENT_COST=0.05,
    DIG_COST=5,
    SELF_DESTRUCT_COST=5,
    DIG_RUBBLE_REMOVED=2,
    DIG_RESOURCE_GAIN=2,
    DIG_LICHEN_REMOVED=10,
    RUBBLE_AFTER_DESTRUCTION=1,
    ACTION_QUEUE_POWER_COST=1,
)
```


# Actions
### Move
```
# a[1] = direction (0 = center, 1 = up, 2 = right, 3 = down, 4 = left)
move_deltas = np.array([[0, 0], [0, -1], [1, 0], [0, 1], [-1, 0]])
```