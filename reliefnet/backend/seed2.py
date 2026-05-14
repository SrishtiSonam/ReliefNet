import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['reliefnet']
    
    await db.warehouses.delete_many({})
    
    mock_warehouses = [
        {
            'warehouse_id': 'WH001', 'name': 'Mumbai Central Depot', 'district': 'Mumbai', 'state': 'MH',
            'latitude': 19.0760, 'longitude': 72.8777, 'capacity_tons': 5000,
            'stock_rice_tons': 2000, 'stock_wheat_tons': 1500, 'stock_medicine_kits': 10000, 'stock_tarpaulin_units': 5000,
            'location': {'type': 'Point', 'coordinates': [72.8777, 19.0760]}
        },
        {
            'warehouse_id': 'WH002', 'name': 'Pune Logistics Hub', 'district': 'Pune', 'state': 'MH',
            'latitude': 18.5204, 'longitude': 73.8567, 'capacity_tons': 8000,
            'stock_rice_tons': 4000, 'stock_wheat_tons': 3000, 'stock_medicine_kits': 25000, 'stock_tarpaulin_units': 12000,
            'location': {'type': 'Point', 'coordinates': [73.8567, 18.5204]}
        }
    ]
    await db.warehouses.insert_many(mock_warehouses)
    print('Re-inserted 2 warehouses near Mumbai.')
        
if __name__ == '__main__':
    asyncio.run(main())
