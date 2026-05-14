import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['reliefnet']
    
    mock_warehouses = [
        {
            'warehouse_id': 'WH003', 'name': 'Nagpur Supply Chain', 'district': 'Nagpur', 'state': 'MH',
            'latitude': 21.1458, 'longitude': 79.0882, 'capacity_tons': 6000,
            'stock_rice_tons': 3000, 'stock_wheat_tons': 2000, 'stock_medicine_kits': 15000, 'stock_tarpaulin_units': 8000,
            'location': {'type': 'Point', 'coordinates': [79.0882, 21.1458]},
            'transactions': []
        },
        {
            'warehouse_id': 'WH004', 'name': 'Nashik Emergency Hub', 'district': 'Nashik', 'state': 'MH',
            'latitude': 20.0110, 'longitude': 73.7903, 'capacity_tons': 4000,
            'stock_rice_tons': 1500, 'stock_wheat_tons': 1000, 'stock_medicine_kits': 8000, 'stock_tarpaulin_units': 4000,
            'location': {'type': 'Point', 'coordinates': [73.7903, 20.0110]},
            'transactions': []
        },
        {
            'warehouse_id': 'WH005', 'name': 'Aurangabad Depot', 'district': 'Aurangabad', 'state': 'MH',
            'latitude': 19.8762, 'longitude': 75.3433, 'capacity_tons': 4500,
            'stock_rice_tons': 1800, 'stock_wheat_tons': 1200, 'stock_medicine_kits': 9000, 'stock_tarpaulin_units': 5000,
            'location': {'type': 'Point', 'coordinates': [75.3433, 19.8762]},
            'transactions': []
        },
        {
            'warehouse_id': 'WH006', 'name': 'Thane Distribution Center', 'district': 'Thane', 'state': 'MH',
            'latitude': 19.2183, 'longitude': 72.9781, 'capacity_tons': 7000,
            'stock_rice_tons': 3500, 'stock_wheat_tons': 2500, 'stock_medicine_kits': 20000, 'stock_tarpaulin_units': 10000,
            'location': {'type': 'Point', 'coordinates': [72.9781, 19.2183]},
            'transactions': []
        }
    ]
    # Use update_one with upsert to avoid duplicates if run multiple times
    for w in mock_warehouses:
        await db.warehouses.update_one({'warehouse_id': w['warehouse_id']}, {'$set': w}, upsert=True)
    print('Added 4 new warehouses in Maharashtra.')
        
if __name__ == '__main__':
    asyncio.run(main())
