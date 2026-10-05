from pydantic import BaseModel

class Item(BaseModel):
    name: str
    # both have same meaning, either str or None. Neither | None nor Optional[] makes a field optional to the client on its own. The = None at the end is what actually makes the field optional in Pydantic.
    description: str | None = None # Here no import is needed. but this required import Optional-> description: Optional[str] = None
    price: float

# created a [Pydantic object instance / class  instance]
existing_item = Item(name="Phone", description="Old phone", price=999.99)

# Incoming partial update data (only updating price)
class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None

update_data = ItemUpdate(price=799.99)

# here all dic data will be show. Even if user change all values or not, unset will got None
cvt = update_data.model_dump()
print("only Model dump eg: ", cvt)

# patch_dict will contain only that which was updated/changed excluding unset fields
patch_dict = update_data.model_dump(exclude_unset=True)
print("Model dump excluded eg: ", patch_dict)

# Merge changes into a copy or update directly
updated_item = existing_item.model_copy(update=patch_dict)
print("Model copy eg: ", updated_item)