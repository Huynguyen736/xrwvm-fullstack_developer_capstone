import { api, writeApi } from './api';

afterEach(() => jest.restoreAllMocks());

test('writes obtain the current CSRF token and send the session cookie', async () => {
  global.fetch = jest.fn()
    .mockResolvedValueOnce({ ok: true, json: async () => ({ csrfToken: 'rotated-token' }) })
    .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'Authenticated' }) });
  await writeApi('login', { userName: 'huy', password: 'test-only' });
  expect(global.fetch).toHaveBeenNthCalledWith(2, '/djangoapp/login', {
    credentials: 'same-origin', method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': 'rotated-token' },
    body: JSON.stringify({ userName: 'huy', password: 'test-only' }),
  });
});

test('server errors are displayed instead of treating failed writes as success', async () => {
  global.fetch = jest.fn().mockResolvedValue({ ok: false, json: async () => ({ error: 'Invalid credentials' }) });
  await expect(api('login')).rejects.toThrow('Invalid credentials');
});
