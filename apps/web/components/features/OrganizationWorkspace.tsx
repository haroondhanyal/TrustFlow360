"use client";

import { useState } from "react";
import { Building2, Copy, Plus, Trash2, Users, ShieldCheck, Send } from "lucide-react";

type Department = { id: string; name: string; description?: string };
type Member = { id: string; first_name: string; last_name: string; email: string; role: string; department_id: string | null; is_active: boolean };
type RoleItem = { key: string; name: string; permissions: string[] };
type Invitation = { id: string; email: string; role: string; department_id?: string | null; expires_at: string; accepted: boolean };

const roles = ["organization_admin", "procurement_manager", "vendor_manager", "finance_manager", "auditor", "viewer"];

export function OrganizationWorkspace({ initialDepartments, initialMembers, initialRoles, initialInvitations }: {
  initialDepartments: Department[]; initialMembers: Member[]; initialRoles: { roles: RoleItem[]; custom_roles: RoleItem[] }; initialInvitations: Invitation[];
}) {
  const [departments, setDepartments] = useState(initialDepartments);
  const [members, setMembers] = useState(initialMembers);
  const [availableRoles, setAvailableRoles] = useState([...initialRoles.roles, ...initialRoles.custom_roles]);
  const [invitations, setInvitations] = useState(initialInvitations);
  const [tab, setTab] = useState("People");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [inviteUrl, setInviteUrl] = useState("");

  async function send(path: string, method: string, data?: unknown) {
    const response = await fetch(`/api/backend${path}`, { method, headers: { "Content-Type": "application/json" }, body: data === undefined ? undefined : JSON.stringify(data) });
    const result = response.status === 204 ? null : await response.json();
    if (!response.ok) throw new Error(result?.detail ?? "Could not save your changes.");
    return result;
  }

  async function invite(form: FormData) {
    setError(""); setMessage(""); setInviteUrl("");
    try {
      const result = await send("/organization/invitations", "POST", { email: form.get("email"), role: form.get("role"), department_id: form.get("department_id") || null });
      const url = `${window.location.origin}/join?token=${encodeURIComponent(result.invite_token)}`;
      setInviteUrl(url); setMessage("Invitation created. Copy its secure link and share it with your teammate.");
      setInvitations([{ ...result, accepted: false }, ...invitations]);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not create invitation."); }
  }

  async function createDepartment(form: FormData) {
    setError(""); setMessage("");
    try {
      const department = await send("/organization/departments", "POST", { name: form.get("name"), description: form.get("description") || null });
      setDepartments([...departments, department].sort((a,b) => a.name.localeCompare(b.name)));
      setMessage("Department created.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not create department."); }
  }

  async function removeDepartment(department: Department) {
    if (!window.confirm(`Delete ${department.name}? Team members will become unassigned.`)) return;
    try {
      await send(`/organization/departments/${department.id}`, "DELETE");
      setDepartments(departments.filter((item) => item.id !== department.id));
      setMembers(members.map((member) => member.department_id === department.id ? { ...member, department_id: null } : member));
      setMessage("Department deleted.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not delete department."); }
  }

  async function updateMember(member: Member, role: string, department_id: string | null) {
    try {
      const updated = await send(`/organization/users/${member.id}`, "PATCH", { role, department_id });
      setMembers(members.map((item) => item.id === member.id ? updated : item));
      setMessage("Member access updated."); setError("");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not update member."); }
  }

  async function createRole(form: FormData) {
    try {
      const result = await send("/organization/roles", "POST", { key: form.get("key"), name: form.get("name"), permissions: String(form.get("permissions") ?? "").split(",").map((item) => item.trim()).filter(Boolean) });
      setAvailableRoles([...availableRoles, result]); setMessage("Role created."); setError("");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not create role."); }
  }

  return <section className="feature-workspace">
    <div className="feature-heading"><div><div className="eyebrow">WORKSPACE ADMINISTRATION</div><h1>People & access</h1><p>Manage members, departments, invitations and organization roles.</p></div></div>
    {(message || error) && <p className={`feature-message ${error ? "feature-error" : "feature-success"}`} role={error ? "alert" : "status"}>{error || message}</p>}
    <div className="org-tabs">{["People","Departments","Roles"].map((item) => <button className={tab===item?"active":""} onClick={()=>setTab(item)} key={item}>{item}</button>)}</div>
    {tab === "People" && <>
      <form action={invite} className="org-invite-form"><div><b><Send size={16}/> Invite a teammate</b><span>Create a one-time, seven-day invitation link.</span></div><input name="email" type="email" required placeholder="teammate@company.com"/><select name="role" defaultValue="viewer">{roles.map((role)=><option key={role} value={role}>{role.replaceAll("_"," ")}</option>)}</select><select name="department_id" defaultValue=""><option value="">No department</option>{departments.map((department)=><option key={department.id} value={department.id}>{department.name}</option>)}</select><button className="button"><Plus size={15}/> Create invite</button></form>
      {inviteUrl && <div className="invite-link"><span>{inviteUrl}</span><button onClick={()=>navigator.clipboard.writeText(inviteUrl)}><Copy size={15}/> Copy</button></div>}
      <div className="org-subheading"><div><h2>Organization members</h2><p>Update each member’s role and department.</p></div><span>{members.length} members</span></div>
      <div className="feature-table-wrap"><table className="feature-table"><thead><tr><th>MEMBER</th><th>EMAIL</th><th>ROLE</th><th>DEPARTMENT</th><th>STATUS</th></tr></thead><tbody>{members.map((member)=><tr key={member.id}><td>{member.first_name} {member.last_name}</td><td>{member.email}</td><td><select value={member.role} onChange={(event)=>updateMember(member,event.target.value,member.department_id)}>{availableRoles.map((role)=><option key={role.key} value={role.key}>{role.name}</option>)}</select></td><td><select value={member.department_id ?? ""} onChange={(event)=>updateMember(member,member.role,event.target.value||null)}><option value="">Unassigned</option>{departments.map((department)=><option key={department.id} value={department.id}>{department.name}</option>)}</select></td><td><span className={`feature-status ${member.is_active?"status-verified":"status-pending"}`}>{member.is_active?"active":"inactive"}</span></td></tr>)}</tbody></table></div>
      <div className="org-subheading"><div><h2>Pending invitations</h2><p>Unaccepted invitations expire seven days after they are created.</p></div></div>
      <div className="feature-table-wrap"><table className="feature-table"><thead><tr><th>EMAIL</th><th>ROLE</th><th>EXPIRES</th><th>STATUS</th></tr></thead><tbody>{invitations.map((invite)=><tr key={invite.id}><td>{invite.email}</td><td>{invite.role.replaceAll("_"," ")}</td><td>{new Date(invite.expires_at).toLocaleDateString("en-US",{timeZone:"UTC"})}</td><td><span className={`feature-status ${invite.accepted?"status-verified":"status-pending"}`}>{invite.accepted?"accepted":"pending"}</span></td></tr>)}{!invitations.length&&<tr><td colSpan={4} className="feature-empty">No invitations yet.</td></tr>}</tbody></table></div>
    </>}
    {tab === "Departments" && <><form action={createDepartment} className="feature-form"><div className="feature-form-heading"><b><Building2 size={16}/> Add a department</b><span>Departments help group members and approvals.</span></div><div className="feature-form-grid"><label>Name<input name="name" required minLength={2}/></label><label>Description<input name="description"/></label></div><button className="button"><Plus size={15}/> Add department</button></form><div className="department-grid">{departments.map((department)=><article key={department.id}><span className="department-icon"><Building2 size={18}/></span><div><b>{department.name}</b><small>{department.description||"No description"}</small><small>{members.filter((member)=>member.department_id===department.id).length} members</small></div><button aria-label={`Delete ${department.name}`} onClick={()=>removeDepartment(department)}><Trash2 size={15}/></button></article>)}{departments.length===0&&<p className="feature-empty">Create your first department.</p>}</div></>}
    {tab === "Roles" && <><form action={createRole} className="feature-form"><div className="feature-form-heading"><b><ShieldCheck size={16}/> Add a custom role</b><span>Use permission keys such as vendors.view and rfqs.manage.</span></div><div className="feature-form-grid"><label>Role key<input name="key" required pattern="[a-z][a-z0-9_]*" placeholder="regional_buyer"/></label><label>Display name<input name="name" required placeholder="Regional Buyer"/></label><label className="wide-field">Permissions<input name="permissions" placeholder="vendors.view, rfqs.manage"/></label></div><button className="button"><Plus size={15}/> Add role</button></form><div className="role-grid">{availableRoles.map((role)=><article key={role.key}><span className="role-icon"><Users size={17}/></span><div><b>{role.name}</b><small>{role.key}</small><div className="permission-list">{role.permissions.map((permission)=><i key={permission}>{permission}</i>)}</div></div></article>)}</div></>}
  </section>;
}
