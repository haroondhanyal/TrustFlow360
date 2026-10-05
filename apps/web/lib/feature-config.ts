export type FeatureKey = "vendors" | "rfqs" | "bids" | "approvals" | "contracts" | "purchase-orders" | "shipments" | "finance" | "risks" | "credentials" | "assets";

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
    fields: [{name:"title",label:"Request title",required:true},{name:"department",label:"Department",required:true},{name:"budget",label:"Budget",type:"number",required:true},{name:"currency",label:"Currency",required:true},{name:"deadline",label:"Submission deadline",type:"date",required:true},{name:"invited_vendors",label:"Vendors to invite",type:"number"},{name:"item_name",label:"First required item",required:true},{name:"quantity",label:"Quantity",type:"number",required:true},{name:"unit",label:"Unit",required:true},{name:"specifications",label:"Item specifications",type:"textarea"},{name:"description",label:"Request description",type:"textarea"}],
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
  shipments: {
    title: "Shipments", description: "Track logistics handoffs, expected delivery and shipment references.", endpoint: "/operations/shipments",
    columns: ["name", "status", "carrier", "tracking_number", "origin", "destination", "expected_delivery"],
    fields: [{name:"name",label:"Shipment title",required:true},{name:"carrier",label:"Carrier"},{name:"tracking_number",label:"Tracking reference"},{name:"origin",label:"Origin"},{name:"destination",label:"Destination"},{name:"expected_delivery",label:"Expected delivery",type:"date"}],
    actions: [{label:"In transit",action:"in_transit"},{label:"Delivered",action:"delivered"},{label:"Delayed",action:"delayed"}],
  },
  finance: {
    title: "Finance", description: "Track invoices and payment status using your workspace records.", endpoint: "/operations/finance",
    columns: ["name", "status", "vendor", "invoice_number", "amount", "currency", "due_date"],
    fields: [{name:"name",label:"Invoice title",required:true},{name:"vendor",label:"Vendor"},{name:"invoice_number",label:"Invoice number"},{name:"amount",label:"Amount",type:"number"},{name:"currency",label:"Currency",required:true},{name:"due_date",label:"Due date",type:"date"}],
    actions: [{label:"Mark paid",action:"paid"},{label:"Mark overdue",action:"overdue"}],
  },
  risks: {
    title: "Risk & compliance", description: "Record supplier and operational risks with clear ownership and mitigation state.", endpoint: "/operations/risks",
    columns: ["name", "status", "category", "severity", "owner", "review_date"],
    fields: [{name:"name",label:"Risk title",required:true},{name:"category",label:"Category"},{name:"severity",label:"Severity",options:["low","medium","high","critical"]},{name:"owner",label:"Owner"},{name:"review_date",label:"Review date",type:"date"}],
    actions: [{label:"Mitigated",action:"mitigated"},{label:"Accept risk",action:"accepted"}],
  },
  credentials: {
    title: "Credentials", description: "Register credential references and review verification state. Attachments are kept in your configured storage, not this local register.", endpoint: "/operations/credentials",
    columns: ["name", "status", "issuer", "credential_type", "reference", "expires_on"],
    fields: [{name:"name",label:"Credential name",required:true},{name:"issuer",label:"Issuer"},{name:"credential_type",label:"Credential type"},{name:"reference",label:"Credential reference"},{name:"expires_on",label:"Expiry date",type:"date"}],
    actions: [{label:"Verify",action:"verified"},{label:"Revoke",action:"revoked"}],
  },
  assets: {
    title: "Assets", description: "Keep an organization-scoped register of equipment and traceable supply-chain assets.", endpoint: "/operations/assets",
    columns: ["name", "status", "asset_tag", "category", "location", "custodian"],
    fields: [{name:"name",label:"Asset name",required:true},{name:"asset_tag",label:"Asset tag"},{name:"category",label:"Category"},{name:"location",label:"Location"},{name:"custodian",label:"Custodian"}],
    actions: [{label:"Activate",action:"active"},{label:"Retire",action:"retired"}],
  },
};
