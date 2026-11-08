export async function api(path, options = {}) {
  const response = await fetch(`/djangoapp/${path}`, { credentials: 'same-origin', ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || data.message || 'The request could not be completed.');
  return data;
}

export async function writeApi(path, payload) {
  // Refresh the token because Django rotates it after successful login.
  const session = await api('session');
  return api(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': session.csrfToken },
    body: JSON.stringify(payload),
  });
}
