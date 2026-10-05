import Link from "next/link";
import { ArrowRight, ShieldCheck, Boxes, ScanLine, LockKeyhole } from "lucide-react";
import { Logo } from "@/components/Logo";

const capabilities = [
  { icon: ShieldCheck, title: "Know who you work with", text: "A clear, continuously updated trust profile for every vendor and partner." },
  { icon: Boxes, title: "Keep every handoff visible", text: "Follow procurement and supply chain activity through one shared workspace." },
  { icon: ScanLine, title: "Verify the proof", text: "Check credentials and documents with a tamper-evident verification trail." },
];

export default function HomePage() {
  return <main className="marketing">
    <header className="site-header wrap"><Link href="/" aria-label="TrustFlow 360 home"><Logo /></Link><nav><a href="#platform">Platform</a><a href="#security">Security</a><Link href="/login">Sign in</Link><Link className="button button-small" href="/signup">Get started <ArrowRight size={15}/></Link></nav></header>
    <section className="hero wrap"><div className="hero-copy"><div className="eyebrow"><span className="pulse"/> THE TRUST LAYER FOR ENTERPRISE</div><h1>Trust every transaction.<br/><em>Verify every relationship.</em></h1><p>Bring vendor trust, procurement and supply chain verification into one calm, connected workspace.</p><div className="hero-actions"><Link className="button" href="/signup">Start your workspace <ArrowRight size={17}/></Link><Link className="text-link" href="/dashboard">Explore the platform <span>↗</span></Link></div><div className="hero-proof"><LockKeyhole size={15}/> Built for teams where trust is part of the work.</div></div>
      <div className="preview-wrap"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="preview-card"><div className="preview-top"><span className="window-dots">● ● ●</span><span>TRUST OVERVIEW</span><span className="live"><i/> LIVE</span></div><div className="preview-inner"><div className="preview-greeting"><span>Good morning, Sofia</span><b>Organization overview</b></div><div className="preview-score"><div><small>PORTFOLIO TRUST SCORE</small><strong>94<span>/100</span></strong><label>↑ 4.8% <span>this quarter</span></label></div><div className="score-ring"><b>94</b><small>TRUST</small></div></div><div className="preview-row"><div className="preview-stat"><span>Verified vendors</span><b>248 <small>↗ 12%</small></b><div className="mini-bars"><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/></div></div><div className="preview-stat"><span>Active relationships</span><b>1,206</b><div className="avatar-stack"><i>AM</i><i>JL</i><i>RK</i><i>+9</i></div></div></div><div className="preview-activity"><span className="activity-icon">✓</span><span><b>Document verified</b><small>Northstar Logistics · just now</small></span><span className="activity-check">ON CHAIN</span></div></div></div><div className="float-chip"><span>✦</span> Trust intelligence <b>Active</b></div></div>
    </section>
    <section className="trust-strip"><div className="wrap trust-content"><span>ONE WORKSPACE FOR</span><b>VENDOR TRUST</b><i/><b>PROCUREMENT</b><i/><b>SUPPLY CHAIN</b><i/><b>VERIFICATION</b></div></section>
    <section className="capabilities wrap" id="platform"><div className="section-heading"><div className="eyebrow">CONNECTED BY TRUST</div><h2>Clarity across every<br/>business relationship.</h2><p>Replace scattered checks and disconnected workflows with a complete view of enterprise trust.</p></div><div className="cap-grid">{capabilities.map(({icon: Icon,title,text},index)=><article className="cap-card" key={title}><span className={`cap-icon cap-${index}`}><Icon size={20}/></span><small>0{index+1}</small><h3>{title}</h3><p>{text}</p><a href="/signup">Discover more <ArrowRight size={14}/></a></article>)}</div></section>
    <footer className="site-footer wrap" id="security"><Logo/><span>Enterprise trust, made visible.</span><small>© 2026 TrustFlow 360</small></footer>
  </main>;
}
