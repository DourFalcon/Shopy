from Website import create_app

app = create_app()
client = app.test_client()

routes = ['/', '/login', '/sign-up', '/register', '/shop', '/cart', '/checkout', '/product/1', '/category/1']
for r in routes:
    resp = client.get(r)
    print(r, resp.status_code)
    if resp.status_code not in (200, 302):
        print(resp.data.decode('utf-8')[:2000])
