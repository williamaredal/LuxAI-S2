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
