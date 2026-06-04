import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL
    ? `${process.env.REACT_APP_API_URL}/api`
    : '/api',
});

// ── Customers ──────────────────────────────────────────────
export const getCustomers = () => api.get('/customers');
export const getCustomerById = (id) => api.get(`/customers/${id}`);
export const createCustomer = (data) => api.post('/customers', data);
export const updateCustomer = (id, data) => api.put(`/customers/${id}`, data);
export const deleteCustomer = (id) => api.delete(`/customers/${id}`);

// ── Accounts ───────────────────────────────────────────────
export const getAccounts = () => api.get('/accounts');
export const getAccountById = (id) => api.get(`/accounts/${id}`);
export const searchAccounts = (name) => api.get(`/accounts/search?name=${encodeURIComponent(name)}`);
export const createAccount = (data) => api.post('/accounts', data);
export const updateAccount = (id, data) => api.put(`/accounts/${id}`, data);
export const deleteAccount = (id) => api.delete(`/accounts/${id}`);

export default api;
