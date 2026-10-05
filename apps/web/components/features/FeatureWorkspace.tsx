"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ArrowRight, Plus, Search, X } from "lucide-react";
import { featureConfig, type FeatureKey } from "@/lib/feature-config";

type Row = Record<string, unknown>;
type Choices = { rfqs?: Row[]; vendors?: Row[]; contracts?: Row[] };

export function FeatureWorkspace({ module, initialRows, choices = {} }: { module: FeatureKey; initialRows: Row[]; choices?: Choices }) {
  const config = featureConfig[module];
  const [rows, setRows] = useState(initialRows);
  const [search, setSearch] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editingRow, setEditingRow] = useState<Row | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const visibleRows = useMemo(() => rows.filter((row) => config.columns.some((key) => String(row[key] ?? "").toLowerCase().includes(search.toLowerCase()))), [rows, search, config.columns]);

  async function refresh() {
    const response = await fetch(`/api/backend${config.endpoint}`, { cache: "no-store" });
    if (response.ok) setRows(await response.json());
  }

  async function create(form: FormData) {
    setBusy(true);
    setError("");
    setNotice("");
    const values: Record<string, unknown> = {};
    for (const field of config.fields) {
      const raw = String(form.get(field.name) ?? "").trim();
      if (raw) values[field.name] = field.type === "number" ? Number(raw) : raw;
    }
    if (["shipments", "finance", "risks", "credentials", "assets"].includes(module)) {
      const name = String(values.name ?? "");
      values.data = Object.fromEntries(Object.entries(values).filter(([key]) => key !== "name"));
      values.name = name;
      values.status = "open";
    }
    if (module === "purchase-orders") {
      values.items = [{ name: values.item_name, quantity: values.quantity, unit_price: values.unit_price }];
      delete values.item_name; delete values.quantity; delete values.unit_price;
    }
    try {
      const response = await fetch(`/api/backend${config.endpoint}${editingRow ? `/${editingRow.id}` : ""}`, {
        method: editingRow ? "PATCH" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? "Could not save this record.");
      setNotice(editingRow ? "Record updated successfully." : "Record created successfully.");
      setFormOpen(false);
      setEditingRow(null);
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The service is unavailable.");
    } finally {
      setBusy(false);
    }
  }

  async function runAction(row: Row, action: string, confirmation?: string) {
    if (action === "edit") { setEditingRow(row); setFormOpen(true); setError(""); return; }
    if (confirmation && !window.confirm(confirmation)) return;
    setError("");
    setNotice("");
    const endpoint = module === "approvals" || module === "bids"
      ? `/${module}/${row.id}/decision`
      : ["shipments", "finance", "risks", "credentials", "assets"].includes(module)
        ? `${config.endpoint}/${row.id}/decision`
        : `${config.endpoint}/${row.id}/${action}`;
    try {
      const response = await fetch(`/api/backend${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision: action }),
      });
      const result = response.status === 204 ? null : await response.json();
      if (!response.ok) throw new Error(result?.detail ?? "Could not update this record.");
      setNotice("Record updated.");
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The service is unavailable.");
    }
  }

  function isActionDisabled(row: Row, action: string) {
    if (module === "vendors") return action === "edit" ? row.status === "suspended" : action === "verify"
      ? row.verification_status !== "pending" || row.status !== "active"
      : row.status !== "active";
    if (module === "approvals") return row.status !== "pending";
    if (module === "bids") return row.status !== "submitted";
    if (["shipments", "finance", "risks", "credentials", "assets"].includes(module)) return row.status === action;
    return row.status !== "draft";
  }

  function fieldOptions(name: string) {
    if (name === "rfq_id") return (choices.rfqs ?? []).map((row) => ({ value: String(row.id), label: `${row.rfq_number} · ${row.title}` }));
    if (name === "vendor_id") return (choices.vendors ?? []).map((row) => ({ value: String(row.id), label: `${row.vendor_number} · ${row.name}` }));
    if (name === "contract_id") return (choices.contracts ?? []).map((row) => ({ value: String(row.id), label: `${row.contract_number} · ${row.title}` }));
    return [];
  }

  function formatValue(key: string, row: Row) {
    const value = row[key];
    if (key === "status" || key === "verification_status" || key === "risk_level") {
      const label = String(value ?? "pending").replaceAll("_", " ");
      return <span className={`feature-status status-${label.toLowerCase().replaceAll(" ", "-")}`}>{label}</span>;
    }
    if (["amount", "budget", "value"].includes(key)) {
      const formatted = Number(value ?? 0).toLocaleString(undefined, { style: "currency", currency: String(row.currency ?? "USD"), maximumFractionDigits: 0 });
      const bestBid = module === "bids" && Number(value) === Math.min(...rows.map((item) => Number(item.amount)));
      return bestBid ? <span className="comparison-best">{formatted}<i>Lowest price</i></span> : formatted;
    }
    if (module === "bids" && key === "technical_score" && Number(value) === Math.max(...rows.map((item) => Number(item.technical_score)))) return <span className="comparison-best">{String(value)}<i>Top score</i></span>;
    if (module === "bids" && key === "delivery_days" && Number(value) === Math.min(...rows.map((item) => Number(item.delivery_days)))) return <span className="comparison-best">{String(value)} days<i>Fastest</i></span>;
    if (module === "bids" && key === "vendor_trust_score" && Number(value) === Math.max(...rows.map((item) => Number(item.vendor_trust_score)))) return <span className="comparison-best">{String(value)}<i>Highest trust</i></span>;
    return String(value ?? "—");
  }

  const recordLabel = module === "rfqs" ? "RFQ" : module === "purchase-orders" ? "purchase order" : module === "vendors" ? "vendor" : module.slice(0, -1);

  return <section className="feature-workspace">
    <div className="feature-heading">
      <div><div className="eyebrow">TRUSTFLOW WORKSPACE</div><h1>{config.title}</h1><p>{config.description}</p></div>
      {config.fields.length > 0 && <button className="button" onClick={() => { setFormOpen(!formOpen); setEditingRow(null); setError(""); }}>
        {formOpen ? <X size={16}/> : <Plus size={16}/>} {formOpen ? "Close" : `New ${recordLabel}`}
      </button>}
    </div>
    {(error || notice) && <p className={error ? "feature-message feature-error" : "feature-message feature-success"} role={error ? "alert" : "status"}>{error || notice}</p>}
    {formOpen && <form action={create} className="feature-form">
      <div className="feature-form-heading"><b>{editingRow ? `Edit ${recordLabel}` : `Create ${recordLabel}`}</b><span>Fields marked required must be filled.</span></div>
      <div className="feature-form-grid">{config.fields.map((field) => {
        const relationOptions = fieldOptions(field.name);
        return <label className={field.type === "textarea" ? "wide-field" : ""} key={field.name}>
          {field.label}
          {field.options?.length ? <select name={field.name} required={field.required}><option value="">Choose…</option>{field.options.map((item) => <option key={item}>{item}</option>)}</select>
            : relationOptions.length > 0 ? <select name={field.name} required={field.required}><option value="">Choose…</option>{relationOptions.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select>
            : field.type === "textarea" ? <textarea name={field.name} rows={3}/>
            : <input name={field.name} type={field.type ?? "text"} required={field.required} min={field.type === "number" ? "0" : undefined} defaultValue={String(editingRow?.[field.name] ?? "")}/>}
        </label>;
      })}</div>
      {error && <p className="feature-error" role="alert">{error}</p>}
      <button className="button" disabled={busy}>{busy ? "Saving…" : "Save record"}</button>
    </form>}
    <div className="feature-toolbar"><label><Search size={16}/><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder={`Search ${config.title.toLowerCase()}…`}/></label><span>{visibleRows.length} records</span></div>
    <div className="feature-table-wrap"><table className="feature-table"><thead><tr>{config.columns.map((key) => <th key={key}>{key.replaceAll("_", " ")}</th>)}{(config.actions.length > 0 || module === "vendors") && <th>Actions</th>}</tr></thead>
      <tbody>{visibleRows.map((row, index) => <tr key={String(row.id ?? index)}>{config.columns.map((key) => <td key={key}>{formatValue(key, row)}</td>)}
        {(config.actions.length > 0 || module === "vendors") && <td className="feature-actions">{module === "vendors" && <Link href={`/vendors/${row.id}`} className="small-link">Passport <ArrowRight size={13}/></Link>}
          {config.actions.map((action) => <button key={action.action} disabled={isActionDisabled(row, action.action)} onClick={() => runAction(row, action.action, action.confirmation)}>{action.label}</button>)}
        </td>}</tr>)}
      {visibleRows.length === 0 && <tr><td colSpan={config.columns.length + 1} className="feature-empty">No records found. Add the first record to this workspace.</td></tr>}</tbody>
    </table></div>
  </section>;
}
