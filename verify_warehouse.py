import duckdb

conn = duckdb.connect('data/warehouse/warehouse.duckdb')

print('=' * 60)
print('DuckDB Warehouse Tables')
print('=' * 60)

tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()
for t in tables:
    print(f'✓ Table: {t[0]}')

print('\n' + '=' * 60)
print('stg_products Schema')
print('=' * 60)
schema = conn.execute('DESCRIBE stg_products').fetchall()
for col in schema:
    print(f'  {col[0]}: {col[1]}')

print('\n' + '=' * 60)
print('Row Counts & Samples')
print('=' * 60)

for table in ['stg_products', 'stg_orders', 'stg_customers']:
    try:
        count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        print(f'\n{table}: {count} rows')
        
        # Show first row
        first_row = conn.execute(f'SELECT * FROM {table} LIMIT 1').fetchall()
        if first_row:
            print(f'  Sample: {first_row[0][:50]}...')
    except Exception as e:
        print(f'{table}: Error - {e}')

conn.close()
print('\n' + '=' * 60)
print('✓ Verification complete')
print('=' * 60)
