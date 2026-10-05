export const metrics = [
  { label: "Total vendors", value: "284", change: "+12.8%", detail: "vs. last quarter", icon: "◈", tone: "mint" },
  { label: "Verified vendors", value: "248", change: "87.3%", detail: "of total portfolio", icon: "✓", tone: "blue" },
  { label: "Open purchase orders", value: "36", change: "8 need attention", detail: "across 12 teams", icon: "▤", tone: "violet" },
  { label: "In transit", value: "18", change: "2 delayed", detail: "estimated this week", icon: "⇢", tone: "amber" },
];

export const activity = [
  { icon: "✓", title: "Vendor verification complete", name: "Northstar Logistics", time: "8 min ago", status: "Verified", tone: "mint" },
  { icon: "▤", title: "New purchase order created", name: "PO-2026-084 · Meridian Supply", time: "32 min ago", status: "Pending", tone: "blue" },
  { icon: "⚠", title: "Certificate expiring soon", name: "Atlas Components · ISO 14001", time: "1 hour ago", status: "Review", tone: "amber" },
  { icon: "⇢", title: "Shipment checkpoint recorded", name: "SHP-2026-219 · Port of Singapore", time: "2 hours ago", status: "On track", tone: "violet" },
];

export const approvals = [
  { title: "Office network equipment", vendor: "NexWave Systems", amount: "$24,800", kind: "PURCHASE ORDER", initials: "NS", color: "blue" },
  { title: "Q3 logistics services", vendor: "Northstar Logistics", amount: "$18,250", kind: "CONTRACT REVIEW", initials: "NL", color: "mint" },
  { title: "Cloud security audit", vendor: "Verity Assurance", amount: "$9,600", kind: "VENDOR ONBOARDING", initials: "VA", color: "violet" },
];
