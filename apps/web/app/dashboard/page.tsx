import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Activity, ArrowDownRight, ArrowRight, ArrowUpRight, Bell, Box, Building2, Check, ChevronDown, CircleHelp, ClipboardCheck, FileCheck2, LayoutDashboard, LifeBuoy, MoreHorizontal, PackageCheck, Search, Settings2, ShieldCheck, Sparkles, Users, WalletCards } from "lucide-react";
import { Logo } from "@/components/Logo";
import { MobileNavBackdrop, MobileNavToggle } from "@/components/dashboard/MobileNavToggle";
import { activity, approvals, metrics } from "@/lib/dashboard-data";

const nav = [
  { label: "WORKSPACE", items: [[LayoutDashboard,"Overview"],[Users,"Vendors"],[ClipboardCheck,"Procurement"],[FileCheck2,"Contracts"],[PackageCheck,"Supply chain"]] as const },
  { label: "TRUST & CONTROL", items: [[ShieldCheck,"Trust passport"],[Activity,"Risk & compliance"],[Box,"Blockchain"]] as const },
  { label: "MANAGE", items: [[Building2,"Organization"],[WalletCards,"Finance"],[Settings2,"Settings"]] as const },
];

const navLinks: Record<string,string> = {Overview:"/dashboard",Vendors:"/vendors",Procurement:"/rfqs",Contracts:"/contracts","Trust passport":"/vendors","Organization":"/organization",Users:"/organization",Departments:"/organization"};

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
  const [profile, organization] = await Promise.all([fetchProfile("/auth/me"), fetchProfile("/organizations/me")]);
  if (!profile) redirect("/login");
  if (!organization) redirect("/signup?step=organization");
  const firstName = profile?.first_name ?? "there";
  const fullName = [profile?.first_name, profile?.last_name].filter(Boolean).join(" ") || "Workspace member";
  const workspaceName = organization?.workspace_name ?? "Your workspace";
  const initials = fullName.split(" ").map((part: string) => part[0]).join("").slice(0, 2).toUpperCase();
  return <main className="dashboard-layout"><MobileNavBackdrop/><aside className="sidebar" id="primary-navigation"><Link href="/"><Logo/></Link><button className="org-switch"><span className="org-mark">{workspaceName.slice(0,1).toUpperCase()}</span><span><b>{workspaceName}</b><small>Enterprise workspace</small></span><ChevronDown size={15}/></button>{nav.map(section=><div className="nav-section" key={section.label}><span className="nav-label">{section.label}</span>{section.items.map(([Icon,label],i)=><Link className={section.label==="WORKSPACE"&&i===0?"nav-link selected":"nav-link"} key={label} href={navLinks[label]??"#"}><Icon size={17}/>{label}{label==="Procurement"&&<i className="nav-count">4</i>}</Link>)}</div>)}<div className="sidebar-bottom"><a className="nav-link" href="#"><CircleHelp size={17}/>Help center</a><div className="user-chip"><span className="user-avatar">{initials}</span><span><b>{fullName}</b><small>Workspace admin</small></span><MoreHorizontal size={18}/></div></div></aside>
    <section className="dashboard-main"><header className="dashboard-topbar"><MobileNavToggle/><div className="crumb">Workspace <span>/</span> <b>Overview</b></div><div className="top-actions"><button className="search-button"><Search size={16}/> <span>Search anything...</span><kbd>⌘ K</kbd></button><button className="icon-button" aria-label="Notifications"><Bell size={18}/><i/></button><button className="help-button"><LifeBuoy size={17}/></button></div></header><div className="dashboard-content"><div className="dash-title-row"><div><div className="eyebrow"><span className="pulse"/> TUESDAY, OCTOBER 6, 2026</div><h1>Good morning, {firstName} <span>✦</span></h1><p>Here’s what’s happening across your organization today.</p></div><button className="button"><Sparkles size={16}/> Ask TrustFlow</button></div>
      <div className="metric-grid">{metrics.map((m,i)=><article className="metric-card" key={m.label}><div className="metric-head"><span>{m.label}</span><i className={`metric-icon ${m.tone}`}>{m.icon}</i></div><strong>{m.value}</strong><div className="metric-foot"><b className={i===3?"warn-text":"positive-text"}>{i===3?<ArrowDownRight size={14}/>:<ArrowUpRight size={14}/>} {m.change}</b><span>{m.detail}</span></div></article>)}</div>
      <div className="dash-grid"><section className="panel activity-panel"><div className="panel-heading"><div><h2>Trust activity</h2><p>Recent events across your workspace</p></div><button className="period-button">Last 7 days <ChevronDown size={14}/></button></div><div className="chart-box"><div className="chart-y"><span>100</span><span>75</span><span>50</span><span>25</span><span>0</span></div><div className="chart-area"><div className="chart-grid"><i/><i/><i/><i/><i/></div><svg viewBox="0 0 620 170" preserveAspectRatio="none" aria-label="Trust score trend: rising from 76 to 94"><defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#24b995" stopOpacity=".22"/><stop offset="1" stopColor="#24b995" stopOpacity="0"/></linearGradient></defs><path d="M0 126 C35 118 42 105 78 111 S126 122 155 95 S204 100 232 79 S275 90 307 66 S348 79 382 58 S427 70 458 48 S503 62 535 36 S580 47 620 20 V170 H0Z" fill="url(#fill)"/><path d="M0 126 C35 118 42 105 78 111 S126 122 155 95 S204 100 232 79 S275 90 307 66 S348 79 382 58 S427 70 458 48 S503 62 535 36 S580 47 620 20" fill="none" stroke="#20b995" strokeWidth="3" vectorEffect="non-scaling-stroke" strokeLinecap="round"/><circle cx="620" cy="20" r="5" fill="#fff" stroke="#20b995" strokeWidth="3" vectorEffect="non-scaling-stroke"/></svg><div className="chart-x"><span>Sep 30</span><span>Oct 1</span><span>Oct 2</span><span>Oct 3</span><span>Oct 4</span><span>Oct 5</span><span>Oct 6</span></div></div></div><div className="chart-summary"><span><i className="legend-dot"/> Trust score trend</span><b>+8.4% <small>this week</small></b></div></section>
        <section className="panel approval-panel"><div className="panel-heading"><div><h2>Needs your attention</h2><p>3 items are waiting for you</p></div><span className="attention-count">3</span></div><div className="approval-list">{approvals.map(item=><article className="approval-item" key={item.title}><i className={`approval-avatar ${item.color}`}>{item.initials}</i><span className="approval-info"><small>{item.kind}</small><b>{item.title}</b><span>{item.vendor}</span></span><span className="approval-right"><b>{item.amount}</b><a href="#review">Review <ArrowRight size={13}/></a></span></article>)}</div><a className="panel-link" href="#approvals">View all approvals <ArrowRight size={15}/></a></section></div>
      <section className="panel events-panel"><div className="panel-heading"><div><h2>Recent activity</h2><p>Latest updates from across your organization</p></div><a className="panel-link" href="#activity">View activity <ArrowRight size={15}/></a></div><div className="activity-table"><div className="activity-table-head"><span>EVENT</span><span>TIME</span><span>STATUS</span></div>{activity.map(item=><div className="activity-row" key={item.title}><i className={`event-icon ${item.tone}`}>{item.icon}</i><span className="event-name"><b>{item.title}</b><small>{item.name}</small></span><span className="event-time">{item.time}</span><span className={`status-pill ${item.tone}`}>{item.status}</span></div>)}</div></section><footer className="dashboard-footer"><span>TrustFlow 360 <i/> All systems operational</span><span>Secured with verifiable trust <ShieldCheck size={14}/></span></footer></div></section></main>
}
