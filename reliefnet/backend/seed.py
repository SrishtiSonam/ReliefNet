import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['reliefnet']
    
    districts = await db.districts.find().to_list(10)
    print('Districts:')
    for d in districts:
        print(f"- {d.get('district')}: Lat {d.get('latitude')}, Lon {d.get('longitude')}")
        
    warehouses = await db.warehouses.find().to_list(10)
    if not warehouses:
        print('No warehouses found. Inserting some mock warehouses.')
        mock_warehouses = [
            {
                'warehouse_id': 'WH001', 'name': 'Kanpur Central Depot', 'district': 'Kanpur Nagar', 'state': 'UP',
                'latitude': 26.4499, 'longitude': 80.3319, 'capacity_tons': 5000,
                'stock_rice_tons': 2000, 'stock_wheat_tons': 1500, 'stock_medicine_kits': 10000, 'stock_tarpaulin_units': 5000,
                'location': {'type': 'Point', 'coordinates': [80.3319, 26.4499]}
            },
            {
                'warehouse_id': 'WH002', 'name': 'Lucknow Logistics Hub', 'district': 'Lucknow', 'state': 'UP',
                'latitude': 26.8467, 'longitude': 80.9462, 'capacity_tons': 8000,
                'stock_rice_tons': 4000, 'stock_wheat_tons': 3000, 'stock_medicine_kits': 25000, 'stock_tarpaulin_units': 12000,
                'location': {'type': 'Point', 'coordinates': [80.9462, 26.8467]}
            }
        ]
        await db.warehouses.insert_many(mock_warehouses)
        print('Inserted 2 warehouses.')
    else:
        print(f"Found {len(warehouses)} warehouses.")
        
if __name__ == '__main__':
    asyncio.run(main())
