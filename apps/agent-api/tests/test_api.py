from app.ingest import MAX_BYTES, chunk_text

def test_liveness(client):
    r = client.get('/health/live')
    assert r.status_code == 200 and r.json()['status'] == 'ok'

def test_document_ingestion_and_lookup(client):
    r = client.post('/api/v1/documents', files={'file': ('runbook.md', b'A test runbook\n' * 100, 'text/markdown')})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body['chunk_count'] >= 2 and body['duplicate'] is False
    lookup = client.get(f"/api/v1/documents/{body['id']}")
    assert lookup.status_code == 200 and lookup.json()['sha256'] == body['sha256']

def test_duplicate_document_is_idempotent(client):
    file = {'file': ('runbook.txt', b'stable content', 'text/plain')}
    first = client.post('/api/v1/documents', files=file)
    second = client.post('/api/v1/documents', files=file)
    assert first.json()['id'] == second.json()['id']
    assert second.json()['duplicate'] is True

def test_missing_document(client):
    assert client.get('/api/v1/documents/missing').status_code == 404

def test_bad_type(client):
    assert client.post('/api/v1/documents', files={'file': ('not_allowed.exe', b'bad')}).status_code == 415

def test_empty_file(client):
    assert client.post('/api/v1/documents', files={'file': ('empty.md', b'')}).status_code == 422

def test_utf8_enforced(client):
    assert client.post('/api/v1/documents', files={'file': ('bad.txt', b'\xff\xfe')}).status_code == 422

def test_too_big(client):
    assert client.post('/api/v1/documents', files={'file': ('big.txt', b'a' * (MAX_BYTES + 1))}).status_code == 413

def test_chunk_overlap():
    assert chunk_text('abcdefghij', size=6, overlap=2) == ['abcdef', 'efghij']

def test_chunk_params():
    try:
        chunk_text('abc', size=0)
        assert False, 'Expected ValueError'
    except ValueError:
        pass
