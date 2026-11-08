import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

const dealer = { id: 1, full_name: 'Kansas Motors', city: 'Topeka', state: 'Kansas', address: '1 Main Street', zip: '66601' };

function mockApi(authenticated = false) {
  global.fetch = jest.fn(async (url) => ({
    ok: true,
    json: async () => url.includes('/session')
      ? { authenticated, userName: authenticated ? 'huynguyen' : '', csrfToken: 'test-csrf' }
      : { status: 200, dealers: [dealer] },
  }));
}

afterEach(() => jest.restoreAllMocks());

test('anonymous visitors can browse and filter dealers without review controls', async () => {
  mockApi();
  render(<MemoryRouter initialEntries={['/']}><App /></MemoryRouter>);
  expect(await screen.findByText('Kansas Motors')).toBeInTheDocument();
  expect(screen.queryByRole('link', { name: 'Review Dealer' })).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Filter by state'), { target: { value: 'Kansas' } });
  expect(await screen.findByText('1 dealership in Kansas')).toBeInTheDocument();
  await waitFor(() => expect(global.fetch).toHaveBeenCalledWith('/djangoapp/get_dealers/Kansas', expect.any(Object)));
});

test('authenticated home shows the server username and review action', async () => {
  mockApi(true);
  render(<MemoryRouter initialEntries={['/dealers']}><App /></MemoryRouter>);
  expect(await screen.findByText('huynguyen')).toBeInTheDocument();
  expect(await screen.findByRole('link', { name: 'Review Dealer' })).toHaveAttribute('href', '/postreview/1');
});

test('registration has all five required named fields', async () => {
  mockApi(true);
  render(<MemoryRouter initialEntries={['/register']}><App /></MemoryRouter>);
  expect(await screen.findByText('huynguyen')).toBeInTheDocument();
  for (const label of ['Username', 'First Name', 'Last Name', 'Email', 'Password']) {
    expect(screen.getByLabelText(label)).toBeRequired();
  }
  expect(screen.getByRole('button', { name: 'Register' })).toBeInTheDocument();
});
