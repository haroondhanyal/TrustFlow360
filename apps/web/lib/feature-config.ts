export type FeatureKey = "vendors" | "rfqs" | "bids" | "approvals" | "contracts" | "purchase-orders";

export type FieldConfig = { name: string; label: string; type?: string; required?: boolean; options?: string[] };
export type ActionConfig = { label: string; action: string; confirmation?: string };
export type FeatureConfig = { title: string; description: string; endpoint: string; columns: string[]; fields: FieldConfig[]; actions: ActionConfig[] };

export const featureConfig: Record<FeatureKey, FeatureConfig> = {
  vendors: {
    title: "Vendors", description: "Manage supplier records, verification status, risk and trust score.", endpoint: "/vendors",
    columns: ["vendor_number", "name", "category", "country", "trust_score", "verification_status", "risk_level", "status"],
    fields: [{name:"name",label:"Vendor name",required:true},{name:"category",label:"Category",required:true},{name:"country",label:"Country",required:true},{name:"website",label:"Website",type:"url"},{name:"registration_number",label:"Registration number"},{name:"tax_id",label:"Tax ID"},{name:"contact_name",label:"Contact name"},{name:"contact_email",label:"Contact email",type:"email"}],
    actions: [{label:"Edit",action:"edit"},{label:"Verify",action:"verify"},{label:"Suspend",action:"suspend",confirmation:"Suspend this vendor?"}],
  },
  rfqs: {
    title: "Requests for quotation", description: "Create sourcing requests, publish them for approval, and compare received bids.", endpoint: "/rfqs",
    columns: ["rfq_number", "title", "department", "budget", "currency", "deadline", "bid_count", "status"],
    fields: [{name:"title",label:"Request title",required:true},{name:"department",label:"Department",required:true},{name:"budget",label:"Budget",type:"number",required:true},{name:"currency",label:"Currency",required:true},{name:"deadline",label:"Submission deadline",type:"date",required:true},{name:"invited_vendors",label:"Vendors to invite",type:"number"},{name:"description",label:"Description",type:"textarea"}],
    actions: [{label:"Send for approval",action:"publish"}],
  },
  bids: {
    title: "Bids", description: "Review vendor proposals and award the selected bid for an open RFQ.", endpoint: "/bids",
    columns: ["rfq_number", "vendor_name", "amount", "technical_score", "delivery_days", "warranty_months", "vendor_trust_score", "vendor_risk_level", "status"],
    fields: [{name:"rfq_id",label:"Open RFQ",required:true,options:[]},{name:"vendor_id",label:"Verified vendor",required:true,options:[]},{name:"amount",label:"Bid amount",type:"number",required:true},{name:"technical_score",label:"Technical score",type:"number"},{name:"delivery_days",label:"Delivery days",type:"number"},{name:"warranty_months",label:"Warranty months",type:"number"},{name:"proposal",label:"Proposal summary",type:"textarea"}],
    actions: [{label:"Award",action:"award",confirmation:"Award this bid? Other bids will be declined."},{label:"Decline",action:"decline"}],
  },
  approvals: {
    title: "Approvals", description: "Review RFQ publishing, contract and purchase order approval requests.", endpoint: "/approvals",
    columns: ["title", "object_type", "status", "comment", "created_at"], fields: [],
    actions: [{label:"Approve",action:"approve"},{label:"Reject",action:"reject"}],
  },
  contracts: {
    title: "Contracts", description: "Track selected vendors, contract value, dates and approval state.", endpoint: "/contracts",
    columns: ["contract_number", "title", "vendor_name", "contract_type", "value", "start_date", "end_date", "status"],
    fields: [{name:"title",label:"Contract title",required:true},{name:"vendor_id",label:"Vendor ID",required:true},{name:"contract_type",label:"Contract type",required:true,options:["Services","Goods","Framework","SaaS"]},{name:"value",label:"Contract value",type:"number",required:true},{name:"start_date",label:"Start date",type:"date",required:true},{name:"end_date",label:"End date",type:"date",required:true}],
    actions: [],
  },
  "purchase-orders": {
    title: "Purchase orders", description: "Create purchase orders against vendors and active contracts, then track approval.", endpoint: "/purchase-orders",
    columns: ["po_number", "title", "vendor_name", "amount", "item_count", "expected_delivery", "status"],
    fields: [{name:"title",label:"Order title",required:true},{name:"vendor_id",label:"Verified vendor",required:true},{name:"contract_id",label:"Active contract ID"},{name:"amount",label:"Order total",type:"number",required:true},{name:"item_name",label:"Line item",required:true},{name:"quantity",label:"Quantity",type:"number",required:true},{name:"unit_price",label:"Unit price",type:"number",required:true},{name:"expected_delivery",label:"Expected delivery",type:"date"}],
    actions: [],
  },
};
