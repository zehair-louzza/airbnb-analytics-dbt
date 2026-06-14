import duckdb
c = duckdb.connect('./data/airbnb.duckdb')
existing = [r[0] for r in c.execute('DESCRIBE main.raw_listings').fetchall()]
print('Current cols:', existing)

cols_to_add = {
    'bedrooms': ('INTEGER', 'beds'),
}
for col, (dtype, expr) in cols_to_add.items():
    if col not in existing:
        c.execute(f'ALTER TABLE main.raw_listings ADD COLUMN {col} {dtype}')
        c.execute(f'UPDATE main.raw_listings SET {col} = {expr}')
        print(f'Added and filled {col}')
    else:
        print(f'{col} already exists')
c.execute('CHECKPOINT')
print('Done!')
new_cols = [r[0] for r in c.execute('DESCRIBE main.raw_listings').fetchall()]
print('New cols:', new_cols)