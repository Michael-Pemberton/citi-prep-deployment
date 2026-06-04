import React, { useEffect, useState } from 'react';
import {
  getAccounts, getCustomers, createAccount, updateAccount, deleteAccount, searchAccounts
} from '../api';
import ConfirmDialog from '../components/ConfirmDialog';

function fmt(n) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);
}

function AccountModal({ account, customers, onClose, onSave }) {
  const isEdit = !!account;
  const [form, setForm] = useState({
    account_number: account?.account_number || '',
    account_type: account?.account_type || 'Savings',
    balance: account?.balance ?? '',
    customer_id: account?.customer_id || (customers[0]?.id ?? ''),
  });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  async function submit(e) {
    e.preventDefault();
    if (!form.account_number.trim()) { setError('Account number is required.'); return; }
    if (form.balance === '' || isNaN(form.balance)) { setError('Valid balance is required.'); return; }
    setSaving(true);
    try {
      const payload = { 
        ...form, 
        balance: parseFloat(form.balance), 
        customer_id: form.customer_id  // remove parseInt - it's already a string
      };
      if (isEdit) {
        await updateAccount(account.id, { account_number: payload.account_number, account_type: payload.account_type, balance: payload.balance });
      } else {
        await createAccount(payload);
      }
      onSave();
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-title">{isEdit ? 'Edit Account' : 'Open New Account'}</div>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={submit}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Account Number</label>
              <input className="form-input" placeholder="S1001" value={form.account_number}
                onChange={e => set('account_number', e.target.value)} disabled={isEdit} />
            </div>
            <div className="form-group">
              <label className="form-label">Account Type</label>
              <select className="form-select" value={form.account_type}
                onChange={e => set('account_type', e.target.value)}>
                <option value="Savings">Savings</option>
                <option value="Checking">Checking</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Balance ($)</label>
            <input className="form-input" type="number" step="0.01" min="0" placeholder="0.00"
              value={form.balance} onChange={e => set('balance', e.target.value)} />
          </div>
          {!isEdit && (
            <div className="form-group">
              <label className="form-label">Customer</label>
              <select className="form-select" value={form.customer_id}
                onChange={e => set('customer_id', e.target.value)}>
                {customers.map(c => (
                  <option key={c.id} value={c.id}>{c.name} — {c.email}</option>
                ))}
              </select>
            </div>
          )}
          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : isEdit ? 'Save Changes' : 'Open Account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Accounts() {
  const [accounts, setAccounts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('All');
  const [modal, setModal] = useState(null);
  const [confirm, setConfirm] = useState(null);

  const load = () => {
    setLoading(true);
    Promise.all([getAccounts(), getCustomers()])
      .then(([a, c]) => { setAccounts(a.data); setCustomers(c.data); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const customerMap = Object.fromEntries(customers.map(c => [c.id, c]));

  const filtered = accounts.filter(a => {
    const c = customerMap[a.customer_id];
    const matchSearch = !search ||
      a.account_number.toLowerCase().includes(search.toLowerCase()) ||
      c?.name.toLowerCase().includes(search.toLowerCase());
    const matchType = typeFilter === 'All' || a.account_type === typeFilter;
    return matchSearch && matchType;
  });

  async function handleDelete(id) {
    await deleteAccount(id);
    setConfirm(null);
    load();
  }

  const totalAUM = filtered.reduce((s, a) => s + parseFloat(a.balance || 0), 0);

  return (
    <>
      {modal === 'create' && (
        <AccountModal customers={customers} onClose={() => setModal(null)}
          onSave={() => { setModal(null); load(); }} />
      )}
      {modal?.account && (
        <AccountModal account={modal.account} customers={customers} onClose={() => setModal(null)}
          onSave={() => { setModal(null); load(); }} />
      )}
      {confirm && (
        <ConfirmDialog
          title="Close Account"
          message="You are about to permanently close account"
          name={confirm.number}
          onConfirm={() => handleDelete(confirm.id)}
          onCancel={() => setConfirm(null)}
        />
      )}

      <div className="page-header">
        <div className="page-title">
          Accounts
          <span>{accounts.length} total accounts — {fmt(accounts.reduce((s,a) => s + parseFloat(a.balance||0),0))} AUM</span>
        </div>
        <button className="btn btn-primary" onClick={() => setModal('create')}
          disabled={customers.length === 0}>
          + Open Account
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <div style={{ display: 'flex', gap: 8 }}>
            <button className={`btn ${typeFilter === 'All' ? 'btn-primary' : 'btn-ghost'} btn-sm`}
              onClick={() => setTypeFilter('All')}>All</button>
            <button className={`btn ${typeFilter === 'Savings' ? 'btn-primary' : 'btn-ghost'} btn-sm`}
              onClick={() => setTypeFilter('Savings')}>Savings</button>
            <button className={`btn ${typeFilter === 'Checking' ? 'btn-primary' : 'btn-ghost'} btn-sm`}
              onClick={() => setTypeFilter('Checking')}>Checking</button>
          </div>
          <div className="search-bar">
            <span style={{ color: 'var(--text-muted)' }}>⌕</span>
            <input placeholder="Search account or customer…" value={search}
              onChange={e => setSearch(e.target.value)} />
          </div>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner" /> Loading…</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Account Number</th>
                  <th>Type</th>
                  <th>Balance</th>
                  <th>Customer</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={6}>
                      <div className="empty">
                        <div className="empty-icon">◎</div>
                        <div className="empty-text">No accounts found</div>
                      </div>
                    </td>
                  </tr>
                )}
                {filtered.map(a => {
                  const c = customerMap[a.customer_id];
                  return (
                    <tr key={a.id}>
                      <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>#{a.id}</td>
                      <td style={{ fontFamily: 'monospace', fontSize: 13 }}>{a.account_number}</td>
                      <td>
                        <span className={`badge badge-${a.account_type?.toLowerCase()}`}>
                          {a.account_type}
                        </span>
                      </td>
                      <td>
                        <span className="amount amount-positive">{fmt(a.balance)}</span>
                      </td>
                      <td style={{ color: 'var(--text-dim)' }}>
                        {c ? c.name : <span style={{ color: 'var(--text-muted)' }}>—</span>}
                      </td>
                      <td>
                        <div className="actions-cell">
                          <button className="btn btn-edit"
                            onClick={() => setModal({ account: a })}>Edit</button>
                          <button className="btn btn-danger"
                            onClick={() => setConfirm({ id: a.id, number: a.account_number })}>
                            Close
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
              {filtered.length > 0 && (
                <tfoot>
                  <tr>
                    <td colSpan={3} style={{ color: 'var(--text-muted)', fontSize: 12, padding: '10px 22px' }}>
                      Showing {filtered.length} account{filtered.length !== 1 ? 's' : ''}
                    </td>
                    <td style={{ padding: '10px 22px', fontWeight: 600 }}>
                      <span className="amount">{fmt(totalAUM)}</span>
                    </td>
                    <td colSpan={2} />
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        )}
      </div>
    </>
  );
}
