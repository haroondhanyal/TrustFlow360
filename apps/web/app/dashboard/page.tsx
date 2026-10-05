import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Activity, ArrowRight, Bell, Box, Building2, ChevronDown, CircleHelp, ClipboardCheck, FileCheck2, LayoutDashboard, LifeBuoy, MoreHorizontal, PackageCheck, Search, ShieldCheck, Sparkles, Users, WalletCards } from "lucide-react";
import { Logo } from "@/components/Logo";
import { MobileNavBackdrop, MobileNavToggle } from "@/components/dashboard/MobileNavToggle";

const nav = [
  { label: "WORKSPACE", items: [[LayoutDashboard,"Overview"],[Users,"Vendors"],[ClipboardCheck,"Procurement"],[FileCheck2,"Contracts"],[PackageCheck,"Shipments"]] as const },
  { label: "TRUST & CONTROL", items: [[ShieldCheck,"Trust passport"],[Activity,"Risk & compliance"],[Box,"Proof ledger"],[FileCheck2,"Credentials"],[PackageCheck,"Assets"],[Sparkles,"Trust assistant"]] as const },
  { label: "MANAGE", items: [[Building2,"Organization"],[WalletCards,"Finance"]] as const },
];

const navLinks: Record<string,string> = {Overview:"/dashboard",Vendors:"/vendors",Procurement:"/rfqs",Contracts:"/contracts",Shipments:"/shipments","Trust passport":"/vendors","Risk & compliance":"/risks","Proof ledger":"/proofs",Credentials:"/credentials",Assets:"/assets","Trust assistant":"/assistant",Finance:"/finance",Organization:"/organization",Users:"/organization",Departments:"/organization"};

export default async function DashboardPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("tf_access")?.value;
  const apiOrigin = process.env.API_URL ?? "http://localhost:8000";
  const fetchProfile = async (path: string) => {
    if (!token) return null;
    try {
      const response = await fetch(`${apiOrigin}${path}`, { headers: { Authorization: `Bearer ${token}` }, cache: "no-store" });
      return response.ok ? response.json() : null;
  } catch { return null; }
  };
  const [profile, organization, summary] = await Promise.all([fetchProfile("/auth/me"), fetchProfile("/organizations/me"), fetchProfile("/dashboard/summary")]);
  if (!profile) redirect("/login");
  if (!organization) redirect("/signup?step=organization");
  if (!summary) redirect("/login");
  const firstName = profile?.first_name ?? "there";
  const fullName = [profile?.first_name, profile?.last_name].filter(Boolean).join(" ") || "Workspace member";
  const workspaceName = organization?.workspace_name ?? "Your workspace";
  const initials = fullName.split(" ").map((part: string) => part[0]).join("").slice(0, 2).toUpperCase();
  const today = new Intl.DateTimeFormat("en-PK", { weekday: "long", month: "long", day: "numeric", year: "numeric" }).format(new Date());
  return <main className="dashboard-layout"><MobileNavBackdrop/><aside className="sidebar" id="primary-navigation"><Link href="/"><Logo/></Link><Link className="org-switch" href="/organization"><span className="org-mark">{workspaceName.slice(0,1).toUpperCase()}</span><span><b>{workspaceName}</b><small>Enterprise workspace</small></span><ChevronDown size={15}/></Link>{nav.map(section=><div className="nav-section" key={section.label}><span className="nav-label">{section.label}</span>{section.items.map(([Icon,label],i)=><Link className={section.label==="WORKSPACE"&&i===0?"nav-link selected":"nav-link"} key={label} href={navLinks[label]??"/dashboard"}><Icon size={17}/>{label}</Link>)}</div>)}<div className="sidebar-bottom"><Link className="nav-link" href="/assistant"><CircleHelp size={17}/>Help & assistant</Link><div className="user-chip"><span className="user-avatar">{initials}</span><span><b>{fullName}</b><small>{profile.role?.replaceAll("_", " ") ?? "Workspace member"}</small></span><MoreHorizontal size={18}/></div></div></aside>
    <section className="dashboard-main"><header className="dashboard-topbar"><MobileNavToggle/><div className="crumb">Workspace <span>/</span> <b>Overview</b></div><div className="top-actions"><Link className="search-button" href="/vendors"><Search size={16}/> <span>Browse vendor records</span></Link><Link className="icon-button" aria-label="Approvals" href="/approvals"><Bell size={18}/></Link><Link className="help-button" aria-label="Help" href="/assistant"><LifeBuoy size={17}/></Link></div></header><div className="dashboard-content"><div className="dash-title-row"><div><div className="eyebrow"><span className="pulse"/> {today.toUpperCase()}</div><h1>Good morning, {firstName} <span>✦</span></h1><p>Here’s what’s happening across your organization today.</p></div><Link className="button" href="/assistant"><Sparkles size={16}/> Ask TrustFlow</Link></div>
      <div className="metric-grid">{summary.metrics.map((m: {label:string;value:string;change:string;detail:string;icon:string;tone:string})=><article className="metric-card" key={m.label}><div className="metric-head"><span>{m.label}</span><i className={`metric-icon ${m.tone}`}>{m.icon}</i></div><strong>{m.value}</strong><div className="metric-foot"><b>{m.change}</b><span>{m.detail}</span></div></article>)}</div>
      <div className="dash-grid"><section className="panel activity-panel"><div className="panel-heading"><div><h2>Vendor trust snapshot</h2><p>Calculated from vendor scores in this workspace</p></div><Link className="panel-link" href="/vendors">View vendors <ArrowRight size={15}/></Link></div><div className="chart-box" style={{display:"grid",placeItems:"center",minHeight:210}}><div style={{textAlign:"center"}}><strong style={{fontSize:64,color:"#1e9c7b"}}>{summary.trust_score}<span style={{fontSize:20,color:"#82908e"}}>/100</span></strong><p>Average vendor trust score</p></div></div></section>
        <section className="panel approval-panel"><div className="panel-heading"><div><h2>Needs your attention</h2><p>{summary.approvals_count} pending approval{summary.approvals_count===1?"":"s"}</p></div><span className="attention-count">{summary.approvals_count}</span></div><div className="approval-list">{summary.approvals.map((item: {title:string;vendor:string;amount:string;kind:string;initials:string;color:string})=><article className="approval-item" key={item.title}><i className={`approval-avatar ${item.color}`}>{item.initials}</i><span className="approval-info"><small>{item.kind}</small><b>{item.title}</b><span>{item.vendor}</span></span><span className="approval-right"><b>{item.amount}</b><Link href="/approvals">Review <ArrowRight size={13}/></Link></span></article>)}{summary.approvals.length===0&&<p className="feature-empty">No approvals are waiting.</p>}</div><Link className="panel-link" href="/approvals">View all approvals <ArrowRight size={15}/></Link></section></div>
      <section className="panel events-panel"><div className="panel-heading"><div><h2>Recent activity</h2><p>Latest records in your organization</p></div></div><div className="activity-table"><div className="activity-table-head"><span>EVENT</span><span>TIME</span><span>STATUS</span></div>{summary.activity.map((item: {icon:string;title:string;name:string;time:string;status:string;tone:string}, index:number)=><div className="activity-row" key={`${item.name}-${index}`}><i className={`event-icon ${item.tone}`}>{item.icon}</i><span className="event-name"><b>{item.title}</b><small>{item.name}</small></span><span className="event-time">{item.time}</span><span className={`status-pill ${item.tone}`}>{item.status}</span></div>)}{summary.activity.length===0&&<p className="feature-empty">New vendor, purchase order and shipment activity will appear here.</p>}</div></section><footer className="dashboard-footer"><span>TrustFlow 360 <i/> API connected</span><span>Organization-scoped workspace data <ShieldCheck size={14}/></span></footer></div></section></main>
}
