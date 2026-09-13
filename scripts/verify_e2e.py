import httpx, time

c = httpx.Client(base_url='http://127.0.0.1:8000')

# 1. Root & HTML
print('1. Testing Root & HTML endpoints...')
assert c.get('/api').status_code == 200
for path in ['/', '/transactions', '/stats', '/settings', '/support', '/login', '/register']:
    assert c.get(path).status_code == 200, f'Failed {path}'
print('   -> All HTML pages returned 200 OK!')

# 2. Register new user
u = f'user_{int(time.time()*1000)}'
r_reg = c.post('/api/auth/register', json={'username': u, 'email': f'{u}@test.com', 'password': 'PassWord@123'})
print('2. Register status:', r_reg.status_code, r_reg.json()['roles'])
assert r_reg.status_code == 201
assert 'user' in r_reg.json()['roles']

# 3. Login - test Bearer token in JSON body
r_log = c.post('/api/auth/login', json={'username': u, 'password': 'PassWord@123'})
print('3. Login status:', r_log.status_code)
data_log = r_log.json()
assert 'access_token' in data_log, 'Missing access_token in body'
token = data_log['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 4. Access protected endpoint using ONLY Authorization Bearer header (no cookies)
c_bearer = httpx.Client(base_url='http://127.0.0.1:8000', headers=headers)
r_me = c_bearer.get('/api/auth/me')
print('4. GET /api/auth/me via Bearer header:', r_me.status_code, r_me.json()['username'])
assert r_me.status_code == 200

# 5. Create category
r_cat = c_bearer.post('/api/categories/', json={'name': 'Học bổng sinh viên', 'type': 'income'})
print('5. POST /api/categories/:', r_cat.status_code, r_cat.json()['name'])
assert r_cat.status_code == 201
cat_id = r_cat.json()['id']

# 6. Create income transaction with that category
r_tx_inc = c_bearer.post('/api/transactions/', json={
    'amount': 2500000,
    'description': 'Nhận học bổng kỳ 2',
    'transaction_date': '2026-09-13',
    'category_id': cat_id
})
print('6. POST income tx:', r_tx_inc.status_code, r_tx_inc.json()['category_name'], r_tx_inc.json()['category_type'])
assert r_tx_inc.status_code == 201
assert r_tx_inc.json()['category_name'] == 'Học bổng sinh viên'
assert r_tx_inc.json()['category_type'] == 'income'

# 7. Create expense transaction with AI classification
r_tx_ai = c_bearer.post('/api/transactions/', json={
    'amount': 35000,
    'description': 'Bát phở bò sáng nay',
    'transaction_date': '2026-09-13',
    'category_id': None
})
print('7. POST AI expense tx:', r_tx_ai.status_code, r_tx_ai.json()['category_name'], r_tx_ai.json()['category_type'])
assert r_tx_ai.status_code == 201
assert r_tx_ai.json()['category_name'] == 'Ăn uống'
assert r_tx_ai.json()['category_type'] == 'expense'

# 8. List transactions & verify fields
r_list = c_bearer.get('/api/transactions/')
print('8. GET /api/transactions/ count:', len(r_list.json()))
assert len(r_list.json()) == 2
for tx in r_list.json():
    print('   Item:', tx['description'], '=>', tx['category_name'], f"({tx['category_type']})", tx['amount'])
    assert tx['category_name'] is not None
    assert tx['category_type'] in ['income', 'expense']

# 9. Update transaction
tx_id = r_tx_ai.json()['id']
r_up = c_bearer.put(f'/api/transactions/{tx_id}', json={'amount': 40000, 'description': 'Bát phở tái nạm đặc biệt'})
print('9. PUT /api/transactions/{id}:', r_up.status_code, r_up.json()['amount'], r_up.json()['description'])
assert r_up.status_code == 200
assert r_up.json()['amount'] == 40000

# 10. Dashboard summary
r_sum = c_bearer.get('/api/dashboard/summary?time_range=this_month')
print('10. Dashboard summary:', r_sum.status_code, r_sum.json())
assert r_sum.status_code == 200
assert r_sum.json()['total_income'] == 2500000
assert r_sum.json()['total_expense'] == 40000
assert r_sum.json()['balance'] == 2460000

# 11. AI Advice
r_adv = c_bearer.post('/api/advice/')
print('11. AI advice:', r_adv.status_code, r_adv.json()['advice'])
assert r_adv.status_code == 200
assert len(r_adv.json()['advice']) > 10

print('\n🎉 TẤT CẢ 11 BƯỚC KIỂM THỬ END-TO-END ĐỀU THÀNH CÔNG RỰC RỠ!')
