# SX Enterprise (CSD DataLake) — AI Query Reference (v2)

SX.e ERP database for a distribution company (generalize this line to describe your own company/business unit).
Use this file to identify the correct tables and fields when writing SQL queries against the CSD DataLake — and to translate what an operator says into the right field.

This is a rebuilt version of `SX_Dictionary_AI.md`, reorganized around how operators actually talk (business terms first, technical schema second) and enriched with:
- **451 business-term definitions** — the natural-language names operators actually use for CSD data — each mapped to its exact CSD table/field.
- **Field-level purpose, expected values, and code meanings** for 64 core tables, pulled from Infor's CSD data-conversion field maps.
- A **consolidated code/enumeration reference** so recurring coded fields (`stagecd`, `transtype`, `statustype`, etc.) don't need to be re-decoded per table.

## How to use this file
1. **Operator asks a question in plain language** → check the **Operator Vocabulary — Quick Index** below for the matching business term and its subject area.
2. **Quick Index gives you `table.field`** → jump to that table in **Table Definitions** for the full field list, data types, and index flags needed to write SQL.
3. **Field looks coded (short char/int value)** → check the table's **Field Notes** (if present) or the **Common Codes & Enumerations** section for what the values mean.
4. **Term isn't in the Quick Index** → it's likely a system/setup/administrative table not covered in the business glossary; search **Table Definitions** directly by table name or description.

## Query Tips
- Almost every table is keyed by `cono` (company number) — always include it as a filter
- Customer number = `custno` in AR tables; product/part number = `prod` in PD/IC tables
- `statustype` is used across tables to indicate active/inactive records — meaning varies by table, see Common Codes & Enumerations
- Index fields (marked `[i]`) are the fastest join and filter columns
- Progress DB table names are truncated to 14 characters — near-duplicate names (e.g. `core_component`) are usually distinct tables, not typos

## Table Groups by Domain

| Prefix | Domain |
|--------|--------|
| `ar__` | Accounts Receivable — customers, invoices, payments, ship-tos |
| `ap__` | Accounts Payable — vendors, invoices, payments |
| `oe__` | Order Entry — sales orders, lines, ship-tos |
| `po__` | Purchase Orders |
| `pd__` | Product / Pricing — item master, price records, contracts |
| `ic__` | Inventory Control — stock levels, warehouses, bins |
| `cr__` | Cash Receipts / Bank Reconciliation |
| `cm__` | Contact/Campaign Management (CRM) |
| `bi__` | Business Intelligence KPIs |
| `edi_` | EDI transactions |
| `gl__` | General Ledger — accounts, budgets, auto-distribution |
| `sa__` | System setup — tax, terms, freight, table-value codes |
| `sm__` | Salesrep master / setup |
| `wm__` / `twl_` / `wl__` | Warehouse management (TWL) — bins, picks, transactions |
| `wt__` | Warehouse Transfers |
| `vas__` | Value-Added Services — fabrication/kitting |
| `kps_` | Kit definitions (groups/options) |

---


---

## Operator Vocabulary — Quick Index

Fast lookup: what operators call something -> the CSD field behind it. Grouped by subject area. Use this before searching the technical Table Definitions below.

### Accounts Payable (AP)

| Business Term | Type | CSD Source | What it means |
|---|---|---|---|
| Company | Dimension | `apet.cono` | The operating company / legal entity the transaction belongs to. |
| Supplier | Dimension | `apet.vendno` | The vendor being paid or credited on this transaction. |
| Transaction Type | Property (Code) | `apet.transcd` | What kind of AP activity the row represents (invoice, payment, credit memo, scheduled payment, etc.). |
| Invoice Type | Property | `apet.invtype` | Classification of the invoice (e.g., merchandise vs. expense) as entered in CSD. |
| Created By | Property | `apet.createdby (links to pv_user.oper2)` | The user who entered the transaction. |
| Outstanding Balance | Measure | `apet: amount − (paymtamt + discamt)` | Amount still owed on the invoice after subtracting payments and discounts taken. |
| Invoice Amount | Measure | `apet.amount` | Original gross amount of the invoice as billed by the supplier. |
| Amount Paid | Measure | `apet.paymtamt` | Total dollars already paid against the invoice. |
| Discount Taken | Measure | `apet.discamt` | Early-payment or terms discount captured on the invoice. |
| Invoice Number | Key | `apet.apinvno` | The supplier's invoice number recorded in CSD. |
| Invoice Suffix | Key | `apet.apinvsuf` | Sequence suffix that distinguishes multiple records tied to the same invoice number. |
| Check Number | Key | `apet.checkno` | The check (or payment reference) number used to pay the invoice. |
| Reference | Property | `apet.ref` | Free-text reference recorded on the transaction. |
| Journal Number | Key | `apet.jrnlno` | The GL journal the transaction posted to. |
| Set Number | Key | `apet.setno` | Internal grouping/batch identifier for related transactions. |
| Payment Terms | Property (Code) | `apet.termstype` | The payment-terms code governing due date and discount (e.g., Net 30, 2% 10 Net 30). |
| GL Account | Property | `apet.glacctno` | General ledger account the invoice expense/cost posts to. |
| GL Division | Property | `apet.gldivno` | GL division segment for the posting. |
| GL Department | Property | `apet.gldeptno` | GL department segment for the posting. |
| Invoice Date | Date / Period | `apet.invdt` | Date the supplier invoice was dated/entered. |
| Due Date | Date / Period | `apet.duedt` | Date payment is due to the supplier. |
| Payment Date | Date / Period | `apet.paymtdt` | Date the payment was actually made. |
| Last Changed By | Property | `apet.lastchangedby` | User who most recently modified the transaction. |
| Supplier Code | Key | `apsv.vendno` | Unique identifier for the vendor. |
| Supplier Name | Property | `apsv.name` | Display name of the vendor. |
| Supplier Type | Property (Code) | `apsv.vendtype` | Vendor classification used to group suppliers (child dimension). |
| Invoice Type | Property (Code) | `apsv.invtype` | Default invoice classification for the vendor (child dimension). |
| Address Line 1 | Property | `apsv.addr_1` | Primary street address of the supplier. |
| Address Line 2 | Property | `apsv.addr_2` | Secondary address line. |
| City | Property | `apsv.city` | Supplier city. |
| State | Property | `apsv.state` | Supplier state/province. |
| Postal Code | Property | `apsv.zipcd` | Supplier ZIP/postal code. |
| Phone | Property | `apsv.phoneno` | Supplier phone number. |
| Fax | Property | `apsv.faxphoneno` | Supplier fax number. |
| Email | Property | `apsv.email` | Supplier email address. |
| Account Manager | Property | `apsv.slsnm` | The supplier's sales rep / our account contact for the vendor. |
| Payment Terms | Property (Code) | `apsv.termstype` | Default payment-terms code for the vendor. |
| Company Code | Key | `sasc.cono` | Identifier of the operating company. |
| Company Name | Property | `sasc.conm` | Display name of the operating company. |
| Transaction Type Name | Property (Code) | `Hard-coded lookup from apet.transcd` | Readable label for the AP transaction type code. |
| Created By Code | Key | `pv_user.oper2` | Login/operator code of the user who created a transaction. |
| Created By Name | Property | `pv_user.email (name from email prefix)` | Readable name of the transaction creator. |
| Supplier Type Code | Property (Code) | `sasta.codeval (codeiden = VT)` | Code value for supplier classification. |
| Supplier Type Name | Property | `sasta.descrip` | Readable description of the supplier type. |

### Accounts Receivable (AR)

| Business Term | Type | CSD Source | What it means |
|---|---|---|---|
| Company | Dimension | `aret.cono` | The operating company / legal entity for the transaction. |
| Customer | Dimension | `aret.custno` | The customer being billed or who made the payment. |
| Transaction Type | Property (Code) | `aret.transcd` | Type of AR activity (invoice, payment, credit memo, service charge, unapplied cash, etc.). |
| Dispute Flag | Property (Status) | `aret.disputefl` | Indicates whether the invoice is currently in dispute. |
| Outstanding Balance | Measure | `aret: amount − (paymtamt + discamt)` | Amount the customer still owes after payments and discounts. |
| Original Amount | Measure | `aret.amount` | Original gross amount billed on the invoice. |
| Payment Received | Measure | `aret.paymtamt` | Total cash received against the transaction. |
| Discount Given | Measure | `aret.discamt` | Early-payment/terms discount granted to the customer. |
| Write-Off / Paid-in-Full Adjustment | Measure | `aret.pifamt` | Amount written off or adjusted to close the balance. |
| Invoice (with Suffix) | Key | `aret: invno + invsuf` | Full invoice identifier combining number and suffix. |
| Invoice Number | Key | `aret.invno` | The invoice number. |
| Invoice Suffix | Key | `aret.invsuf` | Sequence suffix for the invoice number. |
| Source Code | Property (Code) | `aret.sourcecd` | Origin of the transaction. |
| Operator (Last Changed By) | Property | `aret.lastchangedby` | User who last modified the transaction. |
| Reference | Property | `aret.refer` | Free-text reference on the transaction. |
| Journal Number | Key | `aret.jrnlno` | GL journal the transaction posted to. |
| Set Number | Key | `aret.setno` | Batch/grouping identifier for related transactions. |
| Invoice Date | Date / Period | `aret.invdt` | Date the invoice was issued. |
| Due Date | Date / Period | `aret.duedt` | Date payment is due from the customer. |
| Payment Date | Date / Period | `aret.paymtdt` | Date payment was received. |
| Customer Code | Key | `arsc.custno` | Unique identifier for the customer. |
| Customer Name | Property | `arsc.name` | Display name of the customer. |
| Customer Type | Property (Code) | `arsc.custtype` | Customer classification/segment (child dimension). |
| Customer Price Type | Property (Code) | `arsc.pricetype` | Pricing class assigned to the customer (child dimension). |
| Outside Sales Rep | Dimension | `arsc.slsrepout` | The customer's assigned outside (field) sales rep (child dimension). |
| Inside Sales Rep | Dimension | `arsc.slsrepin` | The customer's assigned inside sales rep (child dimension). |
| AR Group | Property | `arsc.groupid` | Receivables grouping/parent-account identifier (child dimension). |
| Address Line 1 | Property | `arsc.addr_1` | Primary street address. |
| Address Line 2 | Property | `arsc.addr_2` | Secondary address line. |
| Address Line 3 | Property | `arsc.addr3` | Third address line. |
| City | Property | `arsc.city` | Customer city. |
| State | Property | `arsc.state` | Customer state/province. |
| Postal Code | Property | `arsc.zipcd` | Customer ZIP/postal code. |
| Phone | Property | `arsc.phoneno` | Customer phone number. |
| Fax | Property | `arsc.faxphoneno` | Customer fax number. |
| Email | Property | `arsc.email` | Customer email address. |
| Payment Terms | Property (Code) | `arsc.termstype` | Payment-terms code for the customer. |
| Sales Territory | Property | `arsc.salesterr` | Sales territory the customer belongs to. |
| Credit Limit | Measure | `arsc.credlim` | Maximum credit extended to the customer. |
| Account Status | Property (Status) | `arsc.statustype` | Whether the customer account is active. |
| Last Payment Date | Date / Period | `arsc.lastpaydt` | Date of the customer's most recent payment. |
| Last Sale Date | Date / Period | `arsc.lastsaledt` | Date of the customer's most recent sale. |
| Average Days to Pay | Measure | `arsc.avgpaydays` | Average number of days the customer takes to pay invoices. |
| Credit Manager | Property | `arsc.creditmgr` | The credit manager responsible for the account. |
| Company Code | Key | `sasc.cono` | Identifier of the operating company. |
| Company Name | Property | `sasc.conm` | Display name of the operating company. |
| Transaction Type Name | Property (Code) | `Hard-coded lookup from aret.transcd` | Readable label for the AR transaction-type code. |
| Sales Rep Code | Key | `smsn.slsrep` | Identifier for a sales rep. |
| Sales Rep Name | Property | `smsn.name` | Readable name of the sales rep. |
| Customer Type Code | Property (Code) | `sasta.codeval` | Code value for customer classification. |
| Customer Type Name | Property | `sasta.descrip` | Readable description of customer type. |
| Customer Price Type Code | Property (Code) | `sasta.codeval` | Code value for the pricing class. |
| Customer Price Type Name | Property | `sasta.descrip` | Readable description of the pricing class. |

### Inventory

| Business Term | Type | CSD Source | What it means |
|---|---|---|---|
| Company | Dimension | `icsw.cono` | Operating company that owns the stock. |
| Warehouse | Dimension | `icsw.whse` | The warehouse/branch holding the stock. |
| Product-Warehouse | Key | `icsw: prod + whse` | The product-at-a-warehouse combination — the grain of inventory. |
| On-Hand Value (Average Cost) | Measure | `icsw.avgcost (extended)` | Total value of on-hand stock at average cost. |
| Average Cost (Each) | Measure | `icsw.avgcost` | Average unit cost of the product (not extended). |
| On-Hand Quantity | Measure | `icsw.qtyonhand` | Units physically on hand and available. |
| Backorder Quantity | Measure | `icsw.qtybo` | Units on customer backorder awaiting supply. |
| Committed Quantity | Measure | `icsw.qtycommit` | Units committed/allocated to orders but not yet shipped. |
| Demand Quantity | Measure | `icsw.qtydemand` | Current demand units against the item. |
| In-Transit Quantity | Measure | `icsw.qtyintrans` | Units in transit (e.g., warehouse transfers in motion). |
| On-Order Quantity | Measure | `icsw.qtyonorder` | Units on open purchase orders to suppliers. |
| Reserved Quantity | Measure | `icsw.qtyreservd` | Units reserved/held aside. |
| Unavailable Quantity | Measure | `icsw.qtyunavail` | Units on hand but not available to sell (damaged, hold, etc.). |
| On-Hand Value (Last Cost) | Measure | `icsw.lastcost (extended)` | Total on-hand value at the most recent purchase cost. |
| Last Cost (Each) | Measure | `icsw.lastcost` | Most recent unit purchase cost (not extended). |
| On-Hand Value (Replacement Cost) | Measure | `icsw.replcost (extended)` | Total on-hand value at replacement cost. |
| Replacement Cost (Each) | Measure | `icsw.replcost` | Replacement unit cost (not extended). |
| On-Hand Value (Standard Cost) | Measure | `icsw.stndcost (extended)` | Total on-hand value at standard cost. |
| Standard Cost (Each) | Measure | `icsw.stndcost` | Standard unit cost (not extended). |
| Bin Location 1 | Property | `icsw.binloc1` | Primary bin/shelf location in the warehouse. |
| Bin Location 2 | Property | `icsw.binloc2` | Secondary bin/shelf location. |
| Product-Warehouse Code | Key | `icsw: prod + whse` | The product-at-warehouse identifier. |
| Product Name | Property | `icsp.descrip_1` | Primary product description. |
| Description 2 | Property | `icsp.descrip_2` | Second product description line. |
| Description 3 | Property | `icsp.descrip3` | Third product description line. |
| Product | Dimension | `icsw.prod` | The product/SKU code (child dimension). |
| Product Line | Dimension | `icsw.prodline` | The product line the SKU belongs to (child dimension). |
| Product Category | Dimension | `icsp.prodcat` | Merchandising category of the product (child dimension). |
| Stocking Status | Property (Code) | `icsw.statustype` | How the item is stocked/reordered (child dimension). |
| Inventory Class | Property (Code) | `icsw.class` | ABC-style classification tier (child dimension). |
| Replenishment Type | Property (Code) | `icsw.arptype` | How the item is replenished (child dimension). |
| Push Flag | Property (Status) | `icsw.arppushfl` | Indicates push-replenishment handling (child dimension). |
| Replenishment Vendor | Dimension | `icsw.arpvendno` | Primary vendor for replenishing the item (child dimension). |
| Replenishment Warehouse | Dimension | `icsw.arpwhse` | Source warehouse that replenishes this stock (child dimension). |
| Override In Reason | Property (Code) | `icsw.overridein` | Reason for an inbound replenishment override (child dimension). |
| Override Out Reason | Property (Code) | `icsw.overrideout` | Reason for an outbound replenishment override (child dimension). |
| Order Calculation Type | Property (Code) | `icsw.ordcalcty` | Method used to calculate suggested order quantities (child dimension). |
| Warehouse | Property | `icsw.whse` | Warehouse code (property of the record). |
| Warehouse Rank | Measure | `icsw.whserank` | Item's ranking within its warehouse (by value/velocity). |
| Company Rank | Measure | `icsw.companyrank` | Item's ranking across the whole company. |
| ABC Quantity Class | Property (Code) | `icsw.abcqtyclass` | ABC class based on quantity movement. |
| Obsolete Flag (UDF) | Property | `icsw.user1` | User-defined field flagging obsolete items. |
| Average Lead Time | Measure | `icsw.leadtmavg` | Average days from order to receipt for the item. |
| Line Point | Measure | `icsw.linept` | Replenishment line point (upper reorder trigger). |
| Order Point | Measure | `icsw.orderpt` | Reorder point — stock level that triggers a reorder. |
| Last Invoice Date | Date / Period | `icsw.lastinvdt` | Date the item was last invoiced/sold. |
| Last PO Date | Date / Period | `icsw.lastpowtdt` | Date of the last purchase order for the item. |
| Last Receipt Date | Date / Period | `icsw.lastrcptdt` | Date stock was last received. |
| Last Sales Order Date | Date / Period | `icsw.lastsodt` | Date of the last sales order for the item. |
| Created Date | Date / Period | `icsw.enterdt` | Date the product-warehouse record was created. |
| Average Cost | Measure | `icsw.avgcost` | Average unit cost on the master record. |
| Base Price | Measure | `icsw.baseprice` | Base selling price for the item. |
| Last Cost | Measure | `icsw.lastcost` | Most recent purchase cost. |
| List Price | Measure | `icsw.listprice` | List (catalog) price for the item. |
| Replacement Cost | Measure | `icsw.replcost` | Replacement cost reference. |
| Standard Cost | Measure | `icsw.stndcost` | Standard cost reference. |
| ARP Usage | Measure | `icsw.arpusage` | Replenishment usage figure used in reorder calculations. |
| Usage Control | Property | `icsw.usagectrl` | Control setting governing how usage is calculated. |
| Usage Rate | Measure | `icsw.usagerate` | Calculated rate of usage/consumption. |
| Company Code | Key | `sasc.cono` | Identifier of the operating company. |
| Company Name | Property | `sasc.conm` | Display name of the operating company. |
| Warehouse Code | Key | `icsd.whse` | Identifier of the warehouse. |
| Warehouse Name | Property | `icsd.name` | Display name of the warehouse. |
| Product Code | Key | `icsp.prod` | Identifier of the product. |
| Product Name | Property | `icsp.descrip_1` | Display name of the product. |
| Product Line Code | Key | `icsl.prodline` | Identifier of the product line. |
| Product Line Name | Property | `icsl.descrip` | Display name of the product line. |
| Product Category Code | Property (Code) | `sasta.codeval` | Code value for product category. |
| Product Category Name | Property | `sasta.descrip` | Readable description of product category. |
| Supplier Code | Key | `apsv.vendno` | Identifier of the supplier. |
| Supplier Name | Property | `apsv.name` | Display name of the supplier. |
| Override Reason Code | Property (Code) | `sasta.codeval (codeiden = o)` | Code value for replenishment override reasons. |
| Override Reason Name | Property | `sasta.descrip` | Readable description of the override reason. |

### Purchasing (Purchase Orders)

| Business Term | Type | CSD Source | What it means |
|---|---|---|---|
| Company | Dimension | `poel.cono` | Operating company placing the PO. |
| Warehouse | Dimension | `poel.whse` | Warehouse receiving the goods. |
| Supplier | Dimension | `poeh.vendno` | The vendor the PO is placed with. |
| Product-Warehouse | Key | `poel: shipprod + whse` | The product-at-warehouse being purchased. |
| Transaction Type | Property (Code) | `poeh.transtype` | Type of purchasing document. |
| Stage | Property (Code) | `poeh.stagecd` | Where the PO sits in its lifecycle. |
| Order Status | Property (Status) | `poel.statustype` | Active/inactive status of the PO line. |
| Buyer | Dimension | `poel.buyer` | The buyer responsible for the PO. |
| Received Cost | Measure | `poel.netrcv` | Extended cost of goods received on the line. |
| Received Cost (Each) | Measure | `poel: netrcv / qtyrcv` | Per-piece received cost. |
| Received Quantity | Measure | `poel.qtyrcv` | Units received on the line. |
| Ordered Cost | Measure | `poel: qtyord * price` | Extended cost of what was ordered. |
| Ordered Cost (Each) | Measure | `poel.price` | Per-piece ordered cost (unit price). |
| Ordered Quantity | Measure | `poel.qtyord` | Units ordered on the line. |
| Weight | Measure | `poel.weight` | Weight of the ordered goods. |
| Due Days | Measure | `poel/poeh: duedt, receiptdt` | Days between due date and receipt (or today for open POs). |
| Purchase Order Number | Key | `poel.pono` | The PO number. |
| PO Suffix | Key | `poel.posuf` | Suffix distinguishing PO records under one number. |
| Line Number | Key | `poel.lineno` | Line sequence within the PO. |
| Due Date | Date / Period | `poel.duedt` | Date the goods are due. |
| Order Date | Date / Period | `poel.enterdt` | Date the PO was entered. |
| Receipt Date | Date / Period | `poeh.receiptdt` | Date the goods were received. |
| Received Stream (by Receipt Date) | Stream | `n/a` | The Received view of purchasing. |
| Open Stream (by Order Date) | Stream | `n/a` | The Open view of purchasing. |
| Supplier Code | Key | `apsv.vendno` | Unique identifier for the vendor. |
| Supplier Name | Property | `apsv.name` | Display name of the vendor. |
| Supplier Type | Property (Code) | `apsv.vendtype` | Vendor classification (child dimension). |
| Product-Warehouse Code | Key | `icsw: prod + whse` | The product-at-warehouse identifier. |
| Product Name | Property | `icsp.descrip_1` | Primary product description. |
| Description 2 | Property | `icsp.descrip_2` | Second product description line. |
| Product | Dimension | `icsw.prod` | Product/SKU code (child dimension). |
| Product Line | Dimension | `icsw.prodline` | Product line (child dimension). |
| Product Category | Dimension | `icsp.prodcat` | Merchandising category (child dimension). |
| Stocking Status | Property (Code) | `icsw.statustype` | How the item is stocked/reordered (child dimension). |
| Replenishment Type | Property (Code) | `icsw.arptype` | How the item is replenished (child dimension). |
| Prime Supplier | Dimension | `icsw.arpvendno` | Primary vendor for replenishing the item (child dimension). |
| Warehouse Rank | Measure | `icsw.whserank` | Item ranking within its warehouse. |
| Company Rank | Measure | `icsw.companyrank` | Item ranking across the company. |
| ABC Quantity Class | Property (Code) | `icsw.abcqtyclass` | ABC class based on quantity movement. |
| Average Lead Time | Measure | `icsw.leadtmavg` | Average days from order to receipt. |
| Line Point | Measure | `icsw.linept` | Replenishment line point. |
| Order Point | Measure | `icsw.orderpt` | Reorder point. |
| Average Cost | Measure | `icsw.avgcost` | Average unit cost. |
| Base Price | Measure | `icsw.baseprice` | Base selling price. |
| Last Cost | Measure | `icsw.lastcost` | Most recent purchase cost. |
| List Price | Measure | `icsw.listprice` | List (catalog) price. |
| Replacement Cost | Measure | `icsw.replcost` | Replacement cost reference. |
| Standard Cost | Measure | `icsw.stndcost` | Standard cost reference. |
| Company Code | Key | `sasc.cono` | Identifier of the operating company. |
| Company Name | Property | `sasc.conm` | Display name of the operating company. |
| Warehouse Code | Key | `icsd.whse` | Identifier of the warehouse. |
| Warehouse Name | Property | `icsd.name` | Display name of the warehouse. |
| Buyer Code | Key | `pv_user.oper2` | Login/operator code of the buyer. |
| Buyer Name | Property | `pv_user.email (name from email prefix)` | Readable name of the buyer. |
| Supplier Type Code | Property (Code) | `sasta.codeval (codeiden = VT)` | Code value for supplier classification. |
| Supplier Type Name | Property | `sasta.descrip` | Readable description of supplier type. |
| Transaction Type Name | Property (Code) | `Hard-coded lookup from poeh.transtype` | Readable label for the PO transaction-type code. |
| Stage Name | Property (Code) | `Hard-coded lookup from poeh.stagecd` | Readable label for the PO stage code. |

### Sales

| Business Term | Type | CSD Source | What it means |
|---|---|---|---|
| Company | Dimension | `oeel.cono` | Operating company for the sale. |
| Customer | Dimension | `oeeh.custno` | The customer the order/invoice belongs to. |
| Product Warehouse | Key | `oeel: shipprod + whse` | The product-at-warehouse sold. |
| Warehouse | Dimension | `oeel.whse` | Warehouse fulfilling the line. |
| Ship To | Dimension | `oeel/oeeh: shipto + custno` | The specific ship-to location for the order. |
| Order Outside Rep | Dimension | `oeel.slsrepout` | Outside (field) rep credited on the order line. |
| Order Inside Rep | Dimension | `oeel.slsrepin` | Inside rep credited on the order line. |
| Ship Via | Property | `oeeh.shipviaty` | Shipping method/carrier for the order. |
| Stage | Property (Code) | `oeeh.stagecd` | Lifecycle stage of the order. |
| Taken By | Property | `oeeh.takenby` | User who took/entered the order. |
| Transaction Type | Property (Code) | `oeel.transtype` | Type of sales transaction. |
| Stock Status | Property (Code) | `oeel.specnstype` | Whether the item was stocked, non-stocked, special, or lost business. |
| Returned Flag | Property (Status) | `oeel.returnfl` | Indicates whether the line is a return. |
| Price Override Flag | Property (Status) | `oeel.priceoverfl` | Indicates a manual price override on the line. |
| Credit Reason | Property (Code) | `oeel.crreasonty` | Reason a credit was issued (Invoices stream only). |
| Sales Value (Net) | Measure | `oeel.netamt` | Net invoiced sales value of the line — the primary revenue measure. |
| Quantity Shipped | Measure | `oeel.qtyship` | Units shipped/invoiced on the line. |
| Cost of Goods Sold | Measure | `oeel.prodcost` | Product cost of the line for margin calculation. |
| Price (ex Whole-Order Disc) | Measure | `oeel: netamt − wodiscamt` | Net amount excluding whole-order discount. |
| Price (Each) | Measure | `oeel: (netamt − wodiscamt) / qtyship` | Per-piece price after excluding whole-order discount. |
| Cost (Each) | Measure | `oeel.prodcost (per piece)` | Per-piece cost after UOM and rebate adjustment. |
| Commission Cost | Measure | `oeel.commcost` | Cost basis used for commission calculations. |
| GL Cost | Measure | `oeel.glcost` | Cost basis posted to the general ledger. |
| Rebate Amount | Measure | `pder/pdsr.rebateamt` | Vendor rebates applied to the line. |
| Whole-Order Discount Amount | Measure | `oeel.wodiscamt` | Order-level discount allocated to the line. |
| Order Value | Measure | `oeel.netord` | Ordered (vs. shipped) value of the line. |
| Order Quantity | Measure | `oeel.qtyord` | Units ordered on the line. |
| Order Cost | Measure | `oeel: prodcost * qtyord` | Cost of ordered quantity. |
| Backorder Value | Measure | `oeel.netord (partial)` | Value of the unshipped (backordered) portion. |
| Backorder Quantity | Measure | `oeel: qtyord − qtyship` | Units on backorder (ordered minus shipped). |
| Backorder Cost | Measure | `oeel: prodcost * (qtyord − qtyship)` | Cost of the backordered quantity. |
| Amount Tendered | Measure | `oeeh.tendered` | Amount tendered (paid) on the order. |
| Invoice Number | Key | `oeel.orderno` | Invoice/order number used for the invoice. |
| Order Number | Key | `oeel.orderno` | The order number. |
| Order Suffix | Key | `oeel.ordersuf` | Suffix distinguishing records under one order number. |
| Order (with Suffix) | Key | `oeel: orderno + ordersuf` | Full order identifier combining number and suffix. |
| Related Order Number | Key | `oeel.orderaltno` | A linked/alternate order number. |
| Vendor RMA | Key | `oeel.vendrma` | Vendor return-merchandise-authorization number. |
| Line Number | Key | `oeel.lineno` | Line sequence within the order. |
| Customer PO | Property | `oeeh.custpo` | The customer's purchase-order reference. |
| Reference | Property | `oeeh.refer` | Free-text reference on the order header. |
| Unit of Measure | Property | `oeel.unit` | Selling unit of measure for the line. |
| Invoice Date | Date / Period | `oeeh.invoicedt` | Date the line was invoiced. |
| Entered Date | Date / Period | `oeel.enterdt` | Date the order was entered. |
| Promise Date | Date / Period | `oeel.promisedt` | Date promised to the customer. |
| Requested Ship Date | Date / Period | `oeel.reqshipdt` | Date the customer requested shipment. |
| Serial Number | Property | `icets.serialno` | Serial number(s) on the invoiced line. |
| Lost Business Type | Property (Code) | `oeel.lostbusty` | Reason an order was lost (Orders stream only). |
| Company | Dimension | `icsw.cono` | Operating company. |
| Warehouse | Dimension | `icsw.whse` | Warehouse holding the stock. |
| Product Warehouse | Key | `icsw: prod + whse` | Product-at-warehouse identifier. |
| On-Hand Quantity | Measure | `icsw.qtyonhand` | Units currently on hand. |
| On-Hand Value (Average Cost) | Measure | `icsw.avgcost (extended)` | Extended on-hand value at average cost. |
| Company Code | Key | `sasc.cono` | Identifier of the operating company. |
| Company Name | Property | `sasc.conm` | Display name of the operating company. |
| Warehouse Code | Key | `icsd.whse` | Identifier of the warehouse. |
| Warehouse Name | Property | `icsd.name` | Display name of the warehouse. |
| Customer Code | Key | `arsc.custno` | Unique identifier for the customer. |
| Customer Name | Property | `arsc.name` | Display name of the customer. |
| Customer Type | Property (Code) | `arsc.custtype` | Customer classification (child dimension). |
| Customer Price Type | Property (Code) | `arsc.pricetype` | Pricing class for the customer (child dimension). |
| Customer Outside Rep | Dimension | `arsc.slsrepout` | Customer's outside rep (child dimension). |
| Customer Inside Rep | Dimension | `arsc.slsrepin` | Customer's inside rep (child dimension). |
| Address Line 1 | Property | `arsc.addr_1` | Primary street address. |
| Address Line 2 | Property | `arsc.addr_2` | Secondary address line. |
| Address Line 3 | Property | `arsc.addr3` | Third address line. |
| City | Property | `arsc.city` | Customer city. |
| State | Property | `arsc.state` | Customer state/province. |
| Postal Code | Property | `arsc.zipcd` | Customer ZIP/postal code. |
| Phone | Property | `arsc.phoneno` | Customer phone number. |
| Fax | Property | `arsc.faxphoneno` | Customer fax number. |
| Email | Property | `arsc.email` | Customer email address. |
| Sales Territory | Property | `arsc.salesterr` | Sales territory of the customer. |
| Credit Limit | Measure | `arsc.credlim` | Maximum credit extended to the customer. |
| Account Status | Property (Status) | `arsc.statustype` | Whether the account is active. |
| Last Payment Date | Date / Period | `arsc.lastpaydt` | Date of most recent payment. |
| Last Sale Date | Date / Period | `arsc.lastsaledt` | Date of most recent sale. |
| Average Days to Pay | Measure | `arsc.avgpaydays` | Average days the customer takes to pay. |
| Credit Manager | Property | `arsc.creditmgr` | Credit manager for the account. |
| Ship To Code | Key | `arss: custno + shipto` | Identifier for the ship-to location. |
| Ship To Name | Property | `arss.name` | Display name of the ship-to location. |
| Ship To Outside Rep | Dimension | `arss.slsrepout` | Outside rep for the ship-to (child dimension). |
| Ship To Inside Rep | Dimension | `arss.slsrepin` | Inside rep for the ship-to (child dimension). |
| Address Line 1 | Property | `arss.addr_1` | Primary street address. |
| Address Line 2 | Property | `arss.addr_2` | Secondary address line. |
| City | Property | `arss.city` | Ship-to city. |
| State | Property | `arss.state` | Ship-to state/province. |
| Postal Code | Property | `arss.zipcd` | Ship-to ZIP/postal code. |
| Sales Territory | Property | `arss.salesterr` | Sales territory of the ship-to. |
| Product Warehouse Code | Key | `icsw: prod + whse` | Product-at-warehouse identifier. |
| Product Name | Property | `icsp.descrip_1` | Primary product description. |
| Description 2 | Property | `icsp.descrip_2` | Second product description line. |
| Product | Dimension | `icsw.prod` | Product/SKU code (child dimension). |
| Product Line | Dimension | `icsw.prodline` | Product line (child dimension). |
| Product Category | Dimension | `icsp.prodcat` | Merchandising category (child dimension). |
| Stocking Status | Property (Code) | `icsw.statustype` | How the item is stocked/reordered (child dimension). |
| Inventory Class | Property (Code) | `icsw.class` | ABC-style classification tier (child dimension). |
| Replenishment Type | Property (Code) | `icsw.arptype` | How the item is replenished (child dimension). |
| Vendor | Dimension | `icsw.arpvendno` | Primary vendor for the item (child dimension). |
| Warehouse Rank | Measure | `icsw.whserank` | Item ranking within its warehouse. |
| Company Rank | Measure | `icsw.companyrank` | Item ranking across the company. |
| ABC Quantity Class | Property (Code) | `icsw.abcqtyclass` | ABC class by quantity movement. |
| Average Cost | Measure | `icsw.avgcost` | Average unit cost. |
| Base Price | Measure | `icsw.baseprice` | Base selling price. |
| Last Cost | Measure | `icsw.lastcost` | Most recent purchase cost. |
| List Price | Measure | `icsw.listprice` | List (catalog) price. |
| Replacement Cost | Measure | `icsw.replcost` | Replacement cost reference. |
| Standard Cost | Measure | `icsw.stndcost` | Standard cost reference. |
| Product Code | Key | `icsp.prod` | Identifier of the product. |
| Product Name | Property | `icsp.descrip_1` | Primary product description. |
| Description 2 | Property | `icsp.descrip_2` | Second product description line. |
| Sales Rep Code | Key | `smsn.slsrep` | Identifier for a sales rep (all rep dimensions). |
| Sales Rep Name | Property | `smsn.name` | Readable name of the sales rep. |
| Product Line Code | Key | `icsl.prodline` | Identifier of the product line. |
| Product Line Name | Property | `icsl.descrip` | Display name of the product line. |
| Product Category Code | Property (Code) | `sasta.codeval` | Code value for product category. |
| Product Category Name | Property | `sasta.descrip` | Readable description of product category. |
| Customer Type Code | Property (Code) | `sasta.codeval` | Code value for customer classification. |
| Customer Type Name | Property | `sasta.descrip` | Readable description of customer type. |
| Customer Price Type Code | Property (Code) | `sasta.codeval` | Code value for pricing class. |
| Customer Price Type Name | Property | `sasta.descrip` | Readable description of pricing class. |
| Supplier Code | Key | `apsv.vendno` | Identifier of the supplier. |
| Supplier Name | Property | `apsv.name` | Display name of the supplier. |
| Taken By Code | Key | `pv_user.oper2` | Login/operator code of the order taker. |
| Taken By Name | Property | `pv_user.email (name from email prefix)` | Readable name of the order taker. |
| Transaction Type Name | Property (Code) | `Hard-coded lookup from oeeh/oeel.transtype` | Readable label for the sales transaction-type code. |
| Stage Name | Property (Code) | `Hard-coded lookup from oeel.stagecd` | Readable label for the sales stage code. |
| Stock Status Name | Property (Code) | `Hard-coded lookup from oeel.specnstype` | Readable label for the stock-status code. |
| Credit Reason Code | Property (Code) | `sasta.codeval (codeiden = M)` | Code value for credit reasons. |
| Credit Reason Name | Property | `sasta.descrip` | Readable description of the credit reason. |

### TWL (Warehouse Management)

| Business Term | Type | CSD Source | What it means |
|---|---|---|---|
| Company | Dimension | `transactions.co_num` | Operating company for the activity. |
| Warehouse | Dimension | `transactions.wh_num` | Warehouse where the activity occurred. |
| Product (Item) | Dimension | `transactions.item_num` | The item involved in the transaction. |
| Employee | Dimension | `transactions.emp_num` | The warehouse employee who performed the activity. |
| Transaction Type | Property (Code) | `transactions.trans_type` | Type of warehouse activity (pick, putaway, count, move, etc.). |
| Time of Day | Property | `transactions.date_time (derived hour)` | Hour of day the activity occurred. |
| Day of Week | Property | `transactions.date_time (derived day)` | Day of week the activity occurred. |
| Carton | Key | `transactions.carton_id` | The carton involved in the activity. |
| Bin | Dimension | `transactions.bin_num` | The bin location involved. |
| Quantity | Measure | `transactions.item_qty` | Units handled in the transaction. |
| Adjusted Quantity | Measure | `transactions.sugg_qty` | Suggested/adjusted quantity for the transaction. |
| Transaction Number | Key | `transactions.trans_num` | Unique identifier for the transaction. |
| Packer | Property | `transactions.packer` | The packer associated with the activity. |
| Bin From | Property | `transactions.bin_from` | Originating bin for a move. |
| Bin To | Property | `transactions.bin_to` | Destination bin for a move. |
| Pallet | Key | `transactions.pallet_id` | The pallet involved in the activity. |
| Pallet From | Property | `transactions.pallet_id_from` | Originating pallet for a move. |
| Cycle Count String | Property | `transactions.cc_string` | Cycle-count data string for the transaction. |
| PO Number | Key | `transactions.po_number` | Purchase-order number tied to the activity (e.g., receiving). |
| Serial Number | Property | `transactions.serial_num` | Serial number tied to the transaction. |
| Transaction Date | Date / Period | `transactions.date_time (date)` | Date the activity occurred. |
| Company Code | Key | `sasc.cono` | Identifier of the operating company (shared CSD dimension). |
| Company Name | Property | `sasc.conm` | Display name of the operating company. |
| Warehouse Code | Key | `icsd.whse` | Identifier of the warehouse (shared CSD dimension). |
| Warehouse Name | Property | `icsd.name` | Display name of the warehouse. |
| Product Code (UPC) | Key | `item.upc_num` | Universal product code for the item. |
| Product Item | Key | `item.item_num` | TWL item number. |
| Product Name | Property | `item.item_desc` | Item description. |
| Product Group | Dimension | `item.prod_grp` | Product grouping for the item. |
| Warehouse Zone (of Product) | Property | `item.wh_zone` | Warehouse zone assigned to the product (child of Product). |
| Employee Code | Key | `empmst.emp_num` | Identifier of the warehouse employee. |
| Employee Name | Property | `empmst.emp_name` | Display name of the employee. |
| RF Logon | Property | `empmst.rf_logon` | The employee's RF (handheld) logon ID. |
| Transaction Type Code | Property (Code) | `trans_type.trans_type` | Code for the warehouse transaction type. |
| Transaction Type Name | Property | `trans_type.trans_name` | Readable description of the transaction type. |
| Bin Code | Key | `binmst.bin_num` | Identifier of the bin location. |
| Bin Warehouse Zone | Property | `binmst.wh_zone` | Warehouse zone of the bin (child of Bin). |
| Bin Rank (ABC) | Property (Code) | `binmst.abc` | ABC ranking of the bin (child of Bin). |
| Bin Cycle-Count Flag | Property (Status) | `binmst.cycle_flag` | Whether the bin is flagged for cycle counting (child of Bin). |
| Carton Code | Key | `cartonmst.carton_num` | Identifier of the carton. |

### Warehouse Transfers

| Business Term | Type | CSD Source | What it means |
|---|---|---|---|
| Company | Dimension | `wtel.cono` | Operating company for the transfer. |
| Ship-To Warehouse | Dimension | `wtel.shiptowhse` | Destination warehouse receiving the stock. |
| Ship-From Warehouse | Dimension | `wteh.shipfmwhse` | Source warehouse sending the stock. |
| Product Warehouse | Key | `wtel: shipprod + shiptowhse or shipfmwhse` | The product-at-warehouse being transferred. |
| Transaction Type | Property (Code) | `wtel.transtype` | Type of transfer document. |
| Stage | Property (Code) | `wteh.stagecd` | Lifecycle stage of the transfer. |
| Entered By | Property | `wtel.operinit` | User who entered the transfer. |
| Approved By | Property | `wtel.approveinit` | User who approved the transfer. |
| Order Quantity | Measure | `wtel.qtyord` | Units requested on the transfer. |
| Ship Quantity | Measure | `wtel.qtyship` | Units actually shipped. |
| Net Amount | Measure | `wtel.netamt` | Net value of the transferred goods. |
| Cost | Measure | `wtel.prodcost` | Product cost of the transferred goods. |
| Open Due Days | Measure | `wtel/wteh: duedt vs today` | Days past due for open transfers. |
| Open Ship Days | Measure | `wteh: shipdt vs today` | Days since shipment for shipped transfers. |
| Transfer Number | Key | `wtel.wtno` | The transfer document number. |
| Transfer Suffix | Key | `wtel.wtsuf` | Suffix distinguishing records under one transfer number. |
| Transfer Line | Key | `wtel.lineno` | Line sequence within the transfer. |
| Unit of Measure | Property | `wtel.unit` | Unit of measure for the line. |
| Ship Via Type | Property | `wteh.shipviaty` | Shipping method/carrier for the transfer. |
| Entered Date | Date / Period | `wtel.enterdt` | Date the transfer was entered. |
| Printed Date | Date / Period | `wteh.printeddt` | Date the transfer document was printed. |
| Due Date | Date / Period | `wtel.duedt` | Date the transfer is due. |
| Approval Date | Date / Period | `wtel.approvedt` | Date the transfer was approved. |
| Requested Ship Date | Date / Period | `wteh.reqshipdt` | Date shipment was requested. |
| Shipped Date | Date / Period | `wteh.shipdt` | Date the transfer was shipped. |
| Receipt Date | Date / Period | `wteh.receiptdt` | Date the transfer was received. |
| Company Code | Key | `sasc.cono` | Identifier of the operating company. |
| Company Name | Property | `sasc.conm` | Display name of the operating company. |
| Warehouse Code | Key | `icsd.whse` | Identifier of the warehouse. |
| Warehouse Name | Property | `icsd.name` | Display name of the warehouse. |
| Transaction Type Name | Property (Code) | `Hard-coded lookup from wtel.transtype` | Readable label for the transfer transaction-type code. |
| Stage Name | Property (Code) | `Hard-coded lookup from wteh.stagecd` | Readable label for the transfer stage code. |
| Entered/Approved By Code | Key | `pv_user.oper2` | Login/operator code of the entering or approving user. |
| Entered/Approved By Name | Property | `pv_user.email (name from email prefix)` | Readable name of the entering or approving user. |
| Product Warehouse Code | Key | `icsw: prod + whse` | Product-at-warehouse identifier. |
| Product Name | Property | `icsp.descrip_1` | Primary product description. |
| Description 2 | Property | `icsp.descrip_2` | Second product description line. |
| Product | Dimension | `icsw.prod` | Product/SKU code (child dimension). |
| Product Line | Dimension | `icsw.prodline` | Product line (child dimension). |
| Product Category | Dimension | `icsp.prodcat` | Merchandising category (child dimension). |
| Stocking Status | Property (Code) | `icsw.statustype` | How the item is stocked/reordered (child dimension). |
| Inventory Class | Property (Code) | `icsw.class` | ABC-style classification tier (child dimension). |
| Replenishment Type | Property (Code) | `icsw.arptype` | How the item is replenished (child dimension). |
| Supplier | Dimension | `icsw.arpvendno` | Primary vendor for the item (child dimension). |
| Warehouse Rank | Measure | `icsw.whserank` | Item ranking within its warehouse. |
| Company Rank | Measure | `icsw.companyrank` | Item ranking across the company. |
| ABC Quantity Class | Property (Code) | `icsw.abcqtyclass` | ABC class by quantity movement. |
| Average Cost | Measure | `icsw.avgcost` | Average unit cost. |
| Base Price | Measure | `icsw.baseprice` | Base selling price. |
| Last Cost | Measure | `icsw.lastcost` | Most recent purchase cost. |
| List Price | Measure | `icsw.listprice` | List (catalog) price. |
| Replacement Cost | Measure | `icsw.replcost` | Replacement cost reference. |
| Standard Cost | Measure | `icsw.stndcost` | Standard cost reference. |

---

## Business Glossary — Full Definitions & Usage Notes

Same terms as the Quick Index, with full usage notes (including any embedded code meanings) for each. Organized by subject area, in the original tab order.

### Accounts Payable (AP)

- **Company** (Dimension) — The operating company / legal entity the transaction belongs to. *Use to separate or combine results across companies in multi-company reporting.*  `apet.cono`
- **Supplier** (Dimension) — The vendor being paid or credited on this transaction. *Primary way to slice payables — spend, open balances, and payment history by vendor.*  `apet.vendno`
- **Transaction Type** (Property (Code)) — What kind of AP activity the row represents (invoice, payment, credit memo, scheduled payment, etc.). *Filter to separate invoices from payments and credits. Codes: 0=Invoice Debit, 3=Scheduled Payment, 6=Credit Memo, 7=Payment Record.*  `apet.transcd`
- **Invoice Type** (Property) — Classification of the invoice (e.g., merchandise vs. expense) as entered in CSD. *Helps separate product-cost invoices from overhead/expense invoices.*  `apet.invtype`
- **Created By** (Property) — The user who entered the transaction. *Audit and accountability — who keyed the invoice or payment. Resolves to a name via Created By Name.*  `apet.createdby (links to pv_user.oper2)`
- **Outstanding Balance** (Measure) — Amount still owed on the invoice after subtracting payments and discounts taken. *The core 'what we still owe' figure. Calculated: Invoice Amount − (Paid + Discount).*  `apet: amount − (paymtamt + discamt)`
- **Invoice Amount** (Measure) — Original gross amount of the invoice as billed by the supplier. *Starting point for spend analysis before payments/discounts.*  `apet.amount`
- **Amount Paid** (Measure) — Total dollars already paid against the invoice. *Track payment progress and cash already disbursed.*  `apet.paymtamt`
- **Discount Taken** (Measure) — Early-payment or terms discount captured on the invoice. *Measure how well the team captures available payment discounts.*  `apet.discamt`
- **Invoice Number** (Key) — The supplier's invoice number recorded in CSD. *Look up or reconcile a specific invoice.*  `apet.apinvno`
- **Invoice Suffix** (Key) — Sequence suffix that distinguishes multiple records tied to the same invoice number. *Used with Invoice Number to uniquely identify an invoice record.*  `apet.apinvsuf`
- **Check Number** (Key) — The check (or payment reference) number used to pay the invoice. *Reconcile payments to bank/check register.*  `apet.checkno`
- **Reference** (Property) — Free-text reference recorded on the transaction. *Contextual note for matching or research.*  `apet.ref`
- **Journal Number** (Key) — The GL journal the transaction posted to. *Tie AP activity back to the general ledger.*  `apet.jrnlno`
- **Set Number** (Key) — Internal grouping/batch identifier for related transactions. *Trace a batch of related AP entries.*  `apet.setno`
- **Payment Terms** (Property (Code)) — The payment-terms code governing due date and discount (e.g., Net 30, 2% 10 Net 30). *Understand timing of obligations and discount windows.*  `apet.termstype`
- **GL Account** (Property) — General ledger account the invoice expense/cost posts to. *Map AP spend to the chart of accounts for financial reporting.*  `apet.glacctno`
- **GL Division** (Property) — GL division segment for the posting. *Allocate spend by division in the GL structure.*  `apet.gldivno`
- **GL Department** (Property) — GL department segment for the posting. *Allocate spend by department in the GL structure.*  `apet.gldeptno`
- **Invoice Date** (Date / Period) — Date the supplier invoice was dated/entered. *Primary date for aging from invoice and the standard transaction date.*  `apet.invdt`
- **Due Date** (Date / Period) — Date payment is due to the supplier. *Drives the 'By Due Date' stream and aging buckets for cash planning.*  `apet.duedt`
- **Payment Date** (Date / Period) — Date the payment was actually made. *Drives the 'By Payment Date' stream (from apetpaid). Use for cash-out analysis.*  `apet.paymtdt`
- **Last Changed By** (Property) — User who most recently modified the transaction. *Audit trail for edits after entry.*  `apet.lastchangedby`
**Master attributes describing each vendor. Use to enrich AP transactions with supplier details and to group spend.**

- **Supplier Code** (Key) — Unique identifier for the vendor. *The key that joins suppliers to AP transactions.*  `apsv.vendno`
- **Supplier Name** (Property) — Display name of the vendor. *Human-readable label for reporting and grouping.*  `apsv.name`
- **Supplier Type** (Property (Code)) — Vendor classification used to group suppliers (child dimension). *Segment spend by supplier category. Descriptions resolved from sasta where codeiden = VT.*  `apsv.vendtype`
- **Invoice Type** (Property (Code)) — Default invoice classification for the vendor (child dimension). *Group vendors by how their invoices are typically classified.*  `apsv.invtype`
- **Address Line 1** (Property) — Primary street address of the supplier. *Remittance and contact reference.*  `apsv.addr_1`
- **Address Line 2** (Property) — Secondary address line. *Remittance and contact reference.*  `apsv.addr_2`
- **City** (Property) — Supplier city. *Geographic grouping of vendors.*  `apsv.city`
- **State** (Property) — Supplier state/province. *Geographic grouping of vendors.*  `apsv.state`
- **Postal Code** (Property) — Supplier ZIP/postal code. *Geographic grouping and remittance.*  `apsv.zipcd`
- **Phone** (Property) — Supplier phone number. *Contact reference.*  `apsv.phoneno`
- **Fax** (Property) — Supplier fax number. *Contact reference.*  `apsv.faxphoneno`
- **Email** (Property) — Supplier email address. *Contact reference and remittance.*  `apsv.email`
- **Account Manager** (Property) — The supplier's sales rep / our account contact for the vendor. *Identify the relationship owner on the vendor side.*  `apsv.slsnm`
- **Payment Terms** (Property (Code)) — Default payment-terms code for the vendor. *Anticipate due dates and discount opportunities by vendor.*  `apsv.termstype`
**Supporting lookup/reference dimensions that resolve codes to readable names across the AP subject.**

- **Company Code** (Key) — Identifier of the operating company. *Joins company reference to transactions.*  `sasc.cono`
- **Company Name** (Property) — Display name of the operating company. *Readable company label.*  `sasc.conm`
- **Transaction Type Name** (Property (Code)) — Readable label for the AP transaction type code. *Turns transcd values into business terms (Invoice, Payment, Credit Memo).*  `Hard-coded lookup from apet.transcd`
- **Created By Code** (Key) — Login/operator code of the user who created a transaction. *Key used to resolve the creator's name.*  `pv_user.oper2`
- **Created By Name** (Property) — Readable name of the transaction creator. *Derived from the email-address prefix of the user.*  `pv_user.email (name from email prefix)`
- **Supplier Type Code** (Property (Code)) — Code value for supplier classification. *Filtered where codeiden = VT. Key for supplier-type grouping.*  `sasta.codeval (codeiden = VT)`
- **Supplier Type Name** (Property) — Readable description of the supplier type. *Business label for the supplier-type code.*  `sasta.descrip`

### Accounts Receivable (AR)

- **Company** (Dimension) — The operating company / legal entity for the transaction. *Separate or combine receivables across companies.*  `aret.cono`
- **Customer** (Dimension) — The customer being billed or who made the payment. *Primary slice for receivables, collections, and aging by customer.*  `aret.custno`
- **Transaction Type** (Property (Code)) — Type of AR activity (invoice, payment, credit memo, service charge, unapplied cash, etc.). *Separate billings from cash and credits. 0=Invoice, 1=Service Charge, 3=Unapplied Cash, 6=Credit Memo, 7=Check Record. Type 11 is filtered out.*  `aret.transcd`
- **Dispute Flag** (Property (Status)) — Indicates whether the invoice is currently in dispute. *Flag contested invoices that may delay collection. 1 = Yes, otherwise No.*  `aret.disputefl`
- **Outstanding Balance** (Measure) — Amount the customer still owes after payments and discounts. *Core open-receivable figure. Calculated: Original Amount − (Payment + Discount).*  `aret: amount − (paymtamt + discamt)`
- **Original Amount** (Measure) — Original gross amount billed on the invoice. *Starting value before payments, discounts, or write-offs.*  `aret.amount`
- **Payment Received** (Measure) — Total cash received against the transaction. *Track collections progress.*  `aret.paymtamt`
- **Discount Given** (Measure) — Early-payment/terms discount granted to the customer. *Measure discounts conceded during collection.*  `aret.discamt`
- **Write-Off / Paid-in-Full Adjustment** (Measure) — Amount written off or adjusted to close the balance. *Track bad-debt write-offs and small-balance adjustments.*  `aret.pifamt`
- **Invoice (with Suffix)** (Key) — Full invoice identifier combining number and suffix. *Uniquely identify a billing record. Concatenation of invoice number + suffix.*  `aret: invno + invsuf`
- **Invoice Number** (Key) — The invoice number. *Look up or reconcile a specific invoice.*  `aret.invno`
- **Invoice Suffix** (Key) — Sequence suffix for the invoice number. *Distinguishes multiple records under one invoice number.*  `aret.invsuf`
- **Source Code** (Property (Code)) — Origin of the transaction. *Identify how the receivable was generated. 0=Invoice, 1=Service Charge, 4=COD.*  `aret.sourcecd`
- **Operator (Last Changed By)** (Property) — User who last modified the transaction. *Audit trail for edits.*  `aret.lastchangedby`
- **Reference** (Property) — Free-text reference on the transaction. *Context for matching/research.*  `aret.refer`
- **Journal Number** (Key) — GL journal the transaction posted to. *Tie receivables back to the general ledger.*  `aret.jrnlno`
- **Set Number** (Key) — Batch/grouping identifier for related transactions. *Trace related AR entries.*  `aret.setno`
- **Invoice Date** (Date / Period) — Date the invoice was issued. *Drives the 'By Invoice Date' stream and aging from invoice.*  `aret.invdt`
- **Due Date** (Date / Period) — Date payment is due from the customer. *Drives the 'By Due Date' stream and aging buckets.*  `aret.duedt`
- **Payment Date** (Date / Period) — Date payment was received. *Analyze when cash actually arrives.*  `aret.paymtdt`
**Master attributes describing each customer, including credit and payment-behavior fields. Enriches AR transactions and supports collections.**

- **Customer Code** (Key) — Unique identifier for the customer. *Key joining customers to AR transactions.*  `arsc.custno`
- **Customer Name** (Property) — Display name of the customer. *Readable label for reporting.*  `arsc.name`
- **Customer Type** (Property (Code)) — Customer classification/segment (child dimension). *Group receivables by customer category. Descriptions from sasta.*  `arsc.custtype`
- **Customer Price Type** (Property (Code)) — Pricing class assigned to the customer (child dimension). *Understand pricing segment. Descriptions from sasta.*  `arsc.pricetype`
- **Outside Sales Rep** (Dimension) — The customer's assigned outside (field) sales rep (child dimension). *Attribute receivables/credit to the field rep. Links to smsn.slsrep.*  `arsc.slsrepout`
- **Inside Sales Rep** (Dimension) — The customer's assigned inside sales rep (child dimension). *Attribute activity to the inside rep. Links to smsn.slsrep.*  `arsc.slsrepin`
- **AR Group** (Property) — Receivables grouping/parent-account identifier (child dimension). *Roll up related customer accounts (e.g., chains/parents).*  `arsc.groupid`
- **Address Line 1** (Property) — Primary street address. *Billing/contact reference.*  `arsc.addr_1`
- **Address Line 2** (Property) — Secondary address line. *Billing/contact reference.*  `arsc.addr_2`
- **Address Line 3** (Property) — Third address line. *Billing/contact reference.*  `arsc.addr3`
- **City** (Property) — Customer city. *Geographic grouping.*  `arsc.city`
- **State** (Property) — Customer state/province. *Geographic grouping.*  `arsc.state`
- **Postal Code** (Property) — Customer ZIP/postal code. *Geographic grouping and billing.*  `arsc.zipcd`
- **Phone** (Property) — Customer phone number. *Collections/contact reference.*  `arsc.phoneno`
- **Fax** (Property) — Customer fax number. *Contact reference.*  `arsc.faxphoneno`
- **Email** (Property) — Customer email address. *Collections/contact reference.*  `arsc.email`
- **Payment Terms** (Property (Code)) — Payment-terms code for the customer. *Set expectations for due dates and discount windows.*  `arsc.termstype`
- **Sales Territory** (Property) — Sales territory the customer belongs to. *Territory-level receivables analysis.*  `arsc.salesterr`
- **Credit Limit** (Measure) — Maximum credit extended to the customer. *Monitor credit exposure vs. balance for risk management.*  `arsc.credlim`
- **Account Status** (Property (Status)) — Whether the customer account is active. *Filter active vs. inactive customers. 1 = Active, otherwise Inactive.*  `arsc.statustype`
- **Last Payment Date** (Date / Period) — Date of the customer's most recent payment. *Spot dormant or slow-paying accounts.*  `arsc.lastpaydt`
- **Last Sale Date** (Date / Period) — Date of the customer's most recent sale. *Identify recency of customer activity.*  `arsc.lastsaledt`
- **Average Days to Pay** (Measure) — Average number of days the customer takes to pay invoices. *Key collections KPI — a proxy for customer-level DSO.*  `arsc.avgpaydays`
- **Credit Manager** (Property) — The credit manager responsible for the account. *Assign ownership for collections/credit decisions.*  `arsc.creditmgr`
**Supporting lookup/reference dimensions resolving codes to names across the AR subject.**

- **Company Code** (Key) — Identifier of the operating company. *Joins company reference to transactions.*  `sasc.cono`
- **Company Name** (Property) — Display name of the operating company. *Readable company label.*  `sasc.conm`
- **Transaction Type Name** (Property (Code)) — Readable label for the AR transaction-type code. *Turns transcd into business terms (Invoice, Payment, Credit Memo).*  `Hard-coded lookup from aret.transcd`
- **Sales Rep Code** (Key) — Identifier for a sales rep. *Key used to resolve rep names.*  `smsn.slsrep`
- **Sales Rep Name** (Property) — Readable name of the sales rep. *Business label for rep reporting.*  `smsn.name`
- **Customer Type Code** (Property (Code)) — Code value for customer classification. *Filtered by codeiden. Key for customer-type grouping.*  `sasta.codeval`
- **Customer Type Name** (Property) — Readable description of customer type. *Business label for the customer-type code.*  `sasta.descrip`
- **Customer Price Type Code** (Property (Code)) — Code value for the pricing class. *Filtered by codeiden. Key for price-type grouping.*  `sasta.codeval`
- **Customer Price Type Name** (Property) — Readable description of the pricing class. *Business label for the price-type code.*  `sasta.descrip`

### Inventory

- **Company** (Dimension) — Operating company that owns the stock. *Separate inventory across companies.*  `icsw.cono`
- **Warehouse** (Dimension) — The warehouse/branch holding the stock. *Primary slice for stock by location.*  `icsw.whse`
- **Product-Warehouse** (Key) — The product-at-a-warehouse combination — the grain of inventory. *Each row is one product in one warehouse. Composite of product + warehouse.*  `icsw: prod + whse`
- **On-Hand Value (Average Cost)** (Measure) — Total value of on-hand stock at average cost. *Primary inventory valuation figure. Extended by (qtyonhand + qtyunavail) with UOM conversion via icss.csunperstk.*  `icsw.avgcost (extended)`
- **Average Cost (Each)** (Measure) — Average unit cost of the product (not extended). *Per-unit cost basis for margin and valuation.*  `icsw.avgcost`
- **On-Hand Quantity** (Measure) — Units physically on hand and available. *Core stock-level figure for availability and counts.*  `icsw.qtyonhand`
- **Backorder Quantity** (Measure) — Units on customer backorder awaiting supply. *Gauge unfilled demand.*  `icsw.qtybo`
- **Committed Quantity** (Measure) — Units committed/allocated to orders but not yet shipped. *Distinguish promised stock from truly available stock.*  `icsw.qtycommit`
- **Demand Quantity** (Measure) — Current demand units against the item. *Input to replenishment and availability planning.*  `icsw.qtydemand`
- **In-Transit Quantity** (Measure) — Units in transit (e.g., warehouse transfers in motion). *Account for stock arriving soon.*  `icsw.qtyintrans`
- **On-Order Quantity** (Measure) — Units on open purchase orders to suppliers. *Incoming supply for replenishment planning.*  `icsw.qtyonorder`
- **Reserved Quantity** (Measure) — Units reserved/held aside. *Stock not available for general allocation.*  `icsw.qtyreservd`
- **Unavailable Quantity** (Measure) — Units on hand but not available to sell (damaged, hold, etc.). *Adjust availability and valuation. Included in extended-cost valuations.*  `icsw.qtyunavail`
- **On-Hand Value (Last Cost)** (Measure) — Total on-hand value at the most recent purchase cost. *Alternate valuation lens. Extended by (qtyonhand + qtyunavail) with UOM conversion.*  `icsw.lastcost (extended)`
- **Last Cost (Each)** (Measure) — Most recent unit purchase cost (not extended). *Track latest acquisition cost per unit.*  `icsw.lastcost`
- **On-Hand Value (Replacement Cost)** (Measure) — Total on-hand value at replacement cost. *Valuation at today's replacement price. Extended with UOM conversion.*  `icsw.replcost (extended)`
- **Replacement Cost (Each)** (Measure) — Replacement unit cost (not extended). *Per-unit replacement cost basis.*  `icsw.replcost`
- **On-Hand Value (Standard Cost)** (Measure) — Total on-hand value at standard cost. *Standard-cost valuation lens. Extended with UOM conversion.*  `icsw.stndcost (extended)`
- **Standard Cost (Each)** (Measure) — Standard unit cost (not extended). *Per-unit standard cost basis.*  `icsw.stndcost`
- **Bin Location 1** (Property) — Primary bin/shelf location in the warehouse. *Locate stock for picking/counting.*  `icsw.binloc1`
- **Bin Location 2** (Property) — Secondary bin/shelf location. *Alternate pick location.*  `icsw.binloc2`
**Master attributes and replenishment settings describing each product at each warehouse — classification, costs, prices, lead times, reorder points, and last-activity dates.**

- **Product-Warehouse Code** (Key) — The product-at-warehouse identifier. *Grain key for product-warehouse master. Composite of product + warehouse.*  `icsw: prod + whse`
- **Product Name** (Property) — Primary product description. *Readable product label.*  `icsp.descrip_1`
- **Description 2** (Property) — Second product description line. *Additional product detail.*  `icsp.descrip_2`
- **Description 3** (Property) — Third product description line. *Additional product detail.*  `icsp.descrip3`
- **Product** (Dimension) — The product/SKU code (child dimension). *Slice inventory by product.*  `icsw.prod`
- **Product Line** (Dimension) — The product line the SKU belongs to (child dimension). *Group products by line. Links to icsl.prodline.*  `icsw.prodline`
- **Product Category** (Dimension) — Merchandising category of the product (child dimension). *Category-level inventory analysis.*  `icsp.prodcat`
- **Stocking Status** (Property (Code)) — How the item is stocked/reordered (child dimension). *Separate stocked vs. non-stocked items. D=Direct, O=Order as Needed, X=Do not Reorder, S=Stock.*  `icsw.statustype`
- **Inventory Class** (Property (Code)) — ABC-style classification tier (child dimension). *Prioritize management by value/velocity tier. Values 01 through 10.*  `icsw.class`
- **Replenishment Type** (Property (Code)) — How the item is replenished (child dimension). *Understand sourcing method. V=Vendor, W=Warehouse, K=Kit, C=Central Warehouse, etc.*  `icsw.arptype`
- **Push Flag** (Property (Status)) — Indicates push-replenishment handling (child dimension). *Identify items on push replenishment. Boolean flag.*  `icsw.arppushfl`
- **Replenishment Vendor** (Dimension) — Primary vendor for replenishing the item (child dimension). *Tie replenishment to a supplier. Links to apsv.vendno.*  `icsw.arpvendno`
- **Replenishment Warehouse** (Dimension) — Source warehouse that replenishes this stock (child dimension). *Identify the supplying warehouse for transfers.*  `icsw.arpwhse`
- **Override In Reason** (Property (Code)) — Reason for an inbound replenishment override (child dimension). *Explain manual inbound adjustments. Descriptions from sasta where codeiden = o.*  `icsw.overridein`
- **Override Out Reason** (Property (Code)) — Reason for an outbound replenishment override (child dimension). *Explain manual outbound adjustments. Descriptions from sasta where codeiden = o.*  `icsw.overrideout`
- **Order Calculation Type** (Property (Code)) — Method used to calculate suggested order quantities (child dimension). *Understand how reorder amounts are derived.*  `icsw.ordcalcty`
- **Warehouse** (Property) — Warehouse code (property of the record). *Location reference on the master record.*  `icsw.whse`
- **Warehouse Rank** (Measure) — Item's ranking within its warehouse (by value/velocity). *Prioritize SKUs at a location.*  `icsw.whserank`
- **Company Rank** (Measure) — Item's ranking across the whole company. *Company-wide SKU prioritization.*  `icsw.companyrank`
- **ABC Quantity Class** (Property (Code)) — ABC class based on quantity movement. *Velocity-based classification.*  `icsw.abcqtyclass`
- **Obsolete Flag (UDF)** (Property) — User-defined field flagging obsolete items. *Identify obsolete/dead stock for clean-up.*  `icsw.user1`
- **Average Lead Time** (Measure) — Average days from order to receipt for the item. *Plan reorder timing and safety stock.*  `icsw.leadtmavg`
- **Line Point** (Measure) — Replenishment line point (upper reorder trigger). *Upper threshold for replenishment ordering.*  `icsw.linept`
- **Order Point** (Measure) — Reorder point — stock level that triggers a reorder. *Core reorder trigger for replenishment.*  `icsw.orderpt`
- **Last Invoice Date** (Date / Period) — Date the item was last invoiced/sold. *Identify slow movers and recency of sales.*  `icsw.lastinvdt`
- **Last PO Date** (Date / Period) — Date of the last purchase order for the item. *When the item was last reordered.*  `icsw.lastpowtdt`
- **Last Receipt Date** (Date / Period) — Date stock was last received. *Recency of inbound supply.*  `icsw.lastrcptdt`
- **Last Sales Order Date** (Date / Period) — Date of the last sales order for the item. *Recency of demand.*  `icsw.lastsodt`
- **Created Date** (Date / Period) — Date the product-warehouse record was created. *Item setup age.*  `icsw.enterdt`
- **Average Cost** (Measure) — Average unit cost on the master record. *Reference cost basis.*  `icsw.avgcost`
- **Base Price** (Measure) — Base selling price for the item. *Pricing reference.*  `icsw.baseprice`
- **Last Cost** (Measure) — Most recent purchase cost. *Latest acquisition cost reference.*  `icsw.lastcost`
- **List Price** (Measure) — List (catalog) price for the item. *Reference list pricing.*  `icsw.listprice`
- **Replacement Cost** (Measure) — Replacement cost reference. *Current replacement-cost basis.*  `icsw.replcost`
- **Standard Cost** (Measure) — Standard cost reference. *Standard-cost basis.*  `icsw.stndcost`
- **ARP Usage** (Measure) — Replenishment usage figure used in reorder calculations. *Demand input to replenishment math.*  `icsw.arpusage`
- **Usage Control** (Property) — Control setting governing how usage is calculated. *Tunes the replenishment usage logic.*  `icsw.usagectrl`
- **Usage Rate** (Measure) — Calculated rate of usage/consumption. *Velocity input for replenishment.*  `icsw.usagerate`
**Supporting lookup/reference dimensions resolving codes to names across the Inventory subject.**

- **Company Code** (Key) — Identifier of the operating company. *Joins company reference.*  `sasc.cono`
- **Company Name** (Property) — Display name of the operating company. *Readable company label.*  `sasc.conm`
- **Warehouse Code** (Key) — Identifier of the warehouse. *Key joining warehouse reference.*  `icsd.whse`
- **Warehouse Name** (Property) — Display name of the warehouse. *Readable warehouse label.*  `icsd.name`
- **Product Code** (Key) — Identifier of the product. *Key for product reference. Stock from icsp; non-stock from oeel.shipprod.*  `icsp.prod`
- **Product Name** (Property) — Display name of the product. *Readable product label.*  `icsp.descrip_1`
- **Product Line Code** (Key) — Identifier of the product line. *Key for product-line grouping.*  `icsl.prodline`
- **Product Line Name** (Property) — Display name of the product line. *Readable product-line label.*  `icsl.descrip`
- **Product Category Code** (Property (Code)) — Code value for product category. *Filtered by codeiden. Key for category grouping.*  `sasta.codeval`
- **Product Category Name** (Property) — Readable description of product category. *Business label for the category code.*  `sasta.descrip`
- **Supplier Code** (Key) — Identifier of the supplier. *Key for supplier reference on replenishment.*  `apsv.vendno`
- **Supplier Name** (Property) — Display name of the supplier. *Readable supplier label.*  `apsv.name`
- **Override Reason Code** (Property (Code)) — Code value for replenishment override reasons. *Filtered where codeiden = o. Key for override grouping.*  `sasta.codeval (codeiden = o)`
- **Override Reason Name** (Property) — Readable description of the override reason. *Business label for the override code.*  `sasta.descrip`

### Purchasing (Purchase Orders)

- **Company** (Dimension) — Operating company placing the PO. *Separate purchasing across companies.*  `poel.cono`
- **Warehouse** (Dimension) — Warehouse receiving the goods. *Slice purchasing by receiving location.*  `poel.whse`
- **Supplier** (Dimension) — The vendor the PO is placed with. *Primary slice for supplier purchase analysis.*  `poeh.vendno`
- **Product-Warehouse** (Key) — The product-at-warehouse being purchased. *Grain for line-level purchasing. Composite of product + warehouse.*  `poel: shipprod + whse`
- **Transaction Type** (Property (Code)) — Type of purchasing document. *Separate POs from returns, direct orders, quotes, etc. PO=Purchase Order, RM=Return Merchandise, DO=Direct Order, QU=Quote, BL=Blanket, BR=Blanket Release, AC=Accumulative.*  `poeh.transtype`
- **Stage** (Property (Code)) — Where the PO sits in its lifecycle. *Track progress from entry to closed. 0=Entered, 1=Ordered, 2=Printed, 3=Acknowledged, 4=Pre-Receiving, 5=Received, 6=Costed, 7=Closed, 9=Cancelled.*  `poeh.stagecd`
- **Order Status** (Property (Status)) — Active/inactive status of the PO line. *Filter active vs. closed/cancelled lines. A=Active, I=Inactive, S=Costed, else Cancelled.*  `poel.statustype`
- **Buyer** (Dimension) — The buyer responsible for the PO. *Evaluate buyer activity and workload. Resolves to a name via Buyer Name.*  `poel.buyer`
- **Received Cost** (Measure) — Extended cost of goods received on the line. *Value of inbound receipts. Sign-flipped for RM (returns).*  `poel.netrcv`
- **Received Cost (Each)** (Measure) — Per-piece received cost. *Unit cost of received goods. Sign-flipped for RM.*  `poel: netrcv / qtyrcv`
- **Received Quantity** (Measure) — Units received on the line. *Track inbound receipt volume. Sign-flipped for RM.*  `poel.qtyrcv`
- **Ordered Cost** (Measure) — Extended cost of what was ordered. *Value of the purchase commitment. Sign-flipped for RM.*  `poel: qtyord * price`
- **Ordered Cost (Each)** (Measure) — Per-piece ordered cost (unit price). *Negotiated unit price. Sign-flipped for RM.*  `poel.price`
- **Ordered Quantity** (Measure) — Units ordered on the line. *Purchase order volume. Sign-flipped for RM.*  `poel.qtyord`
- **Weight** (Measure) — Weight of the ordered goods. *Freight/logistics planning.*  `poel.weight`
- **Due Days** (Measure) — Days between due date and receipt (or today for open POs). *Measure supplier on-time performance and lateness; zero if not yet due.*  `poel/poeh: duedt, receiptdt`
- **Purchase Order Number** (Key) — The PO number. *Look up a specific purchase order.*  `poel.pono`
- **PO Suffix** (Key) — Suffix distinguishing PO records under one number. *Uniquely identify a PO record.*  `poel.posuf`
- **Line Number** (Key) — Line sequence within the PO. *Identify a specific line item.*  `poel.lineno`
- **Due Date** (Date / Period) — Date the goods are due. *Expected receipt date for planning.*  `poel.duedt`
- **Order Date** (Date / Period) — Date the PO was entered. *Date field for the Open stream.*  `poel.enterdt`
- **Receipt Date** (Date / Period) — Date the goods were received. *Date field for the Received stream.*  `poeh.receiptdt`
**Definitions of how the two reporting streams filter and date PO data. Reference, not joinable fields.**

- **Received Stream (by Receipt Date)** (Stream) — The Received view of purchasing. *Filters to stagecd 5, 6, 7 (Received/Costed/Closed), excludes Cancelled; date field = poeh.receiptdt.*  `n/a`
- **Open Stream (by Order Date)** (Stream) — The Open view of purchasing. *Filters to stagecd 0–4 (Entered through Pre-Receiving), excludes Cancelled; date field = poel.enterdt.*  `n/a`
**Master attributes describing each vendor for purchasing.**

- **Supplier Code** (Key) — Unique identifier for the vendor. *Key joining suppliers to POs.*  `apsv.vendno`
- **Supplier Name** (Property) — Display name of the vendor. *Readable supplier label.*  `apsv.name`
- **Supplier Type** (Property (Code)) — Vendor classification (child dimension). *Group purchasing by supplier category. Descriptions from sasta where codeiden = VT.*  `apsv.vendtype`
**Master attributes and replenishment settings for products being purchased.**

- **Product-Warehouse Code** (Key) — The product-at-warehouse identifier. *Grain key. Composite of product + warehouse.*  `icsw: prod + whse`
- **Product Name** (Property) — Primary product description. *Readable product label.*  `icsp.descrip_1`
- **Description 2** (Property) — Second product description line. *Additional product detail.*  `icsp.descrip_2`
- **Product** (Dimension) — Product/SKU code (child dimension). *Slice purchasing by product.*  `icsw.prod`
- **Product Line** (Dimension) — Product line (child dimension). *Group by line. Links to icsl.prodline.*  `icsw.prodline`
- **Product Category** (Dimension) — Merchandising category (child dimension). *Category-level purchase analysis.*  `icsp.prodcat`
- **Stocking Status** (Property (Code)) — How the item is stocked/reordered (child dimension). *D=Direct, O=Order as Needed, X=Do not Reorder, S=Stock.*  `icsw.statustype`
- **Replenishment Type** (Property (Code)) — How the item is replenished (child dimension). *V=Vendor, W=Warehouse, K=Kit, C=Central Warehouse, etc.*  `icsw.arptype`
- **Prime Supplier** (Dimension) — Primary vendor for replenishing the item (child dimension). *Compare buying vs. the designated prime vendor. Links to apsv.vendno.*  `icsw.arpvendno`
- **Warehouse Rank** (Measure) — Item ranking within its warehouse. *Prioritize SKUs at a location.*  `icsw.whserank`
- **Company Rank** (Measure) — Item ranking across the company. *Company-wide SKU prioritization.*  `icsw.companyrank`
- **ABC Quantity Class** (Property (Code)) — ABC class based on quantity movement. *Velocity-based classification.*  `icsw.abcqtyclass`
- **Average Lead Time** (Measure) — Average days from order to receipt. *Plan reorder timing.*  `icsw.leadtmavg`
- **Line Point** (Measure) — Replenishment line point. *Upper reorder threshold.*  `icsw.linept`
- **Order Point** (Measure) — Reorder point. *Reorder trigger level.*  `icsw.orderpt`
- **Average Cost** (Measure) — Average unit cost. *Reference cost basis.*  `icsw.avgcost`
- **Base Price** (Measure) — Base selling price. *Pricing reference.*  `icsw.baseprice`
- **Last Cost** (Measure) — Most recent purchase cost. *Latest acquisition cost.*  `icsw.lastcost`
- **List Price** (Measure) — List (catalog) price. *Reference list pricing.*  `icsw.listprice`
- **Replacement Cost** (Measure) — Replacement cost reference. *Replacement-cost basis.*  `icsw.replcost`
- **Standard Cost** (Measure) — Standard cost reference. *Standard-cost basis.*  `icsw.stndcost`
**Supporting lookup/reference dimensions resolving codes to names across Purchasing.**

- **Company Code** (Key) — Identifier of the operating company. *Joins company reference.*  `sasc.cono`
- **Company Name** (Property) — Display name of the operating company. *Readable company label.*  `sasc.conm`
- **Warehouse Code** (Key) — Identifier of the warehouse. *Key joining warehouse reference.*  `icsd.whse`
- **Warehouse Name** (Property) — Display name of the warehouse. *Readable warehouse label.*  `icsd.name`
- **Buyer Code** (Key) — Login/operator code of the buyer. *Key used to resolve the buyer's name.*  `pv_user.oper2`
- **Buyer Name** (Property) — Readable name of the buyer. *Derived from the email-address prefix.*  `pv_user.email (name from email prefix)`
- **Supplier Type Code** (Property (Code)) — Code value for supplier classification. *Filtered where codeiden = VT.*  `sasta.codeval (codeiden = VT)`
- **Supplier Type Name** (Property) — Readable description of supplier type. *Business label for the supplier-type code.*  `sasta.descrip`
- **Transaction Type Name** (Property (Code)) — Readable label for the PO transaction-type code. *Turns transtype into business terms.*  `Hard-coded lookup from poeh.transtype`
- **Stage Name** (Property (Code)) — Readable label for the PO stage code. *Turns stagecd into business terms.*  `Hard-coded lookup from poeh.stagecd`

### Sales

- **Company** (Dimension) — Operating company for the sale. *Separate revenue across companies.*  `oeel.cono`
- **Customer** (Dimension) — The customer the order/invoice belongs to. *Primary slice for customer sales analysis.*  `oeeh.custno`
- **Product Warehouse** (Key) — The product-at-warehouse sold. *Grain for line-level sales. Composite of product + warehouse.*  `oeel: shipprod + whse`
- **Warehouse** (Dimension) — Warehouse fulfilling the line. *Slice sales by fulfilling location.*  `oeel.whse`
- **Ship To** (Dimension) — The specific ship-to location for the order. *Analyze sales by delivery destination. Composite of customer + ship-to suffix.*  `oeel/oeeh: shipto + custno`
- **Order Outside Rep** (Dimension) — Outside (field) rep credited on the order line. *Attribute revenue to the field rep.*  `oeel.slsrepout`
- **Order Inside Rep** (Dimension) — Inside rep credited on the order line. *Attribute revenue to the inside rep.*  `oeel.slsrepin`
- **Ship Via** (Property) — Shipping method/carrier for the order. *Analyze fulfillment by carrier/method.*  `oeeh.shipviaty`
- **Stage** (Property (Code)) — Lifecycle stage of the order. *Track from quote to paid. 0=Quoted, 1=Ordered, 2=Picked, 3=Shipped, 4=Invoiced, 5=Paid.*  `oeeh.stagecd`
- **Taken By** (Property) — User who took/entered the order. *Order-entry accountability. Resolves to a name via Taken By Name.*  `oeeh.takenby`
- **Transaction Type** (Property (Code)) — Type of sales transaction. *Separate stock orders, counter sales, direct orders, etc. SO=Stock Order, CS=Counter Sale, DO=Direct Order.*  `oeel.transtype`
- **Stock Status** (Property (Code)) — Whether the item was stocked, non-stocked, special, or lost business. *Distinguish stocked sales from special/non-stock and lost business. Blank=Stocked, N=NonStocked, S=Special Order, L=Lost Business.*  `oeel.specnstype`
- **Returned Flag** (Property (Status)) — Indicates whether the line is a return. *Separate returns from purchases. 1 = Returned, 0 = Purchased. Drives sign-flip on value/quantity/cost.*  `oeel.returnfl`
- **Price Override Flag** (Property (Status)) — Indicates a manual price override on the line. *Identify discretionary pricing. 1 = Yes, 0 = No.*  `oeel.priceoverfl`
- **Credit Reason** (Property (Code)) — Reason a credit was issued (Invoices stream only). *Analyze why credits/returns occur.*  `oeel.crreasonty`
- **Sales Value (Net)** (Measure) — Net invoiced sales value of the line — the primary revenue measure. *Headline revenue figure. Sign-flipped by Returned Flag.*  `oeel.netamt`
- **Quantity Shipped** (Measure) — Units shipped/invoiced on the line. *Volume sold. Sign-flipped by Returned Flag.*  `oeel.qtyship`
- **Cost of Goods Sold** (Measure) — Product cost of the line for margin calculation. *Pair with Sales Value for gross margin. Multiplied by qtyship, with UOM conversion (icss.csunperstk), rebate adjustment (pder/pdsr), and return sign-flip.*  `oeel.prodcost`
- **Price (ex Whole-Order Disc)** (Measure) — Net amount excluding whole-order discount. *Revenue lens that isolates line price from order-level discounting. Sign-flipped by Returned Flag.*  `oeel: netamt − wodiscamt`
- **Price (Each)** (Measure) — Per-piece price after excluding whole-order discount. *Unit selling price.*  `oeel: (netamt − wodiscamt) / qtyship`
- **Cost (Each)** (Measure) — Per-piece cost after UOM and rebate adjustment. *Unit cost for margin.*  `oeel.prodcost (per piece)`
- **Commission Cost** (Measure) — Cost basis used for commission calculations. *Analyze commissionable cost. Multiplied by qtyship, UOM conversion, return sign-flip.*  `oeel.commcost`
- **GL Cost** (Measure) — Cost basis posted to the general ledger. *Reconcile margin to GL. Multiplied by qtyship, UOM conversion, return sign-flip.*  `oeel.glcost`
- **Rebate Amount** (Measure) — Vendor rebates applied to the line. *Adjust effective cost/margin. One-time rebates from pder; recurring from pdsr.*  `pder/pdsr.rebateamt`
- **Whole-Order Discount Amount** (Measure) — Order-level discount allocated to the line. *Quantify order-wide discounting.*  `oeel.wodiscamt`
- **Order Value** (Measure) — Ordered (vs. shipped) value of the line. *Compare ordered vs. invoiced demand. Sign-flipped by Returned Flag.*  `oeel.netord`
- **Order Quantity** (Measure) — Units ordered on the line. *Ordered demand volume. Sign-flipped by Returned Flag.*  `oeel.qtyord`
- **Order Cost** (Measure) — Cost of ordered quantity. *Cost basis for ordered demand. With UOM conversion and return sign-flip.*  `oeel: prodcost * qtyord`
- **Backorder Value** (Measure) — Value of the unshipped (backordered) portion. *Quantify revenue stuck on backorder. Proportional value of qtyord − qtyship; zero if botype = N.*  `oeel.netord (partial)`
- **Backorder Quantity** (Measure) — Units on backorder (ordered minus shipped). *Track unfilled units. Zero if botype = N (no backorder allowed).*  `oeel: qtyord − qtyship`
- **Backorder Cost** (Measure) — Cost of the backordered quantity. *Cost exposure of backorders. With UOM conversion and return sign-flip; zero if botype = N.*  `oeel: prodcost * (qtyord − qtyship)`
- **Amount Tendered** (Measure) — Amount tendered (paid) on the order. *Counter-sale/payment analysis. Applied to the first line of each order only.*  `oeeh.tendered`
- **Invoice Number** (Key) — Invoice/order number used for the invoice. *Look up an invoice.*  `oeel.orderno`
- **Order Number** (Key) — The order number. *Look up an order.*  `oeel.orderno`
- **Order Suffix** (Key) — Suffix distinguishing records under one order number. *Uniquely identify an order record.*  `oeel.ordersuf`
- **Order (with Suffix)** (Key) — Full order identifier combining number and suffix. *Concatenation of order number + suffix.*  `oeel: orderno + ordersuf`
- **Related Order Number** (Key) — A linked/alternate order number. *Trace related orders (e.g., replacements).*  `oeel.orderaltno`
- **Vendor RMA** (Key) — Vendor return-merchandise-authorization number. *Tie returns to a vendor RMA.*  `oeel.vendrma`
- **Line Number** (Key) — Line sequence within the order. *Identify a specific line item.*  `oeel.lineno`
- **Customer PO** (Property) — The customer's purchase-order reference. *Match orders to the customer's PO.*  `oeeh.custpo`
- **Reference** (Property) — Free-text reference on the order header. *Contextual note.*  `oeeh.refer`
- **Unit of Measure** (Property) — Selling unit of measure for the line. *Interpret quantities correctly.*  `oeel.unit`
- **Invoice Date** (Date / Period) — Date the line was invoiced. *Date field for the Invoices stream — the standard revenue date.*  `oeeh.invoicedt`
- **Entered Date** (Date / Period) — Date the order was entered. *Date field for the Orders and Quotes streams.*  `oeel.enterdt`
- **Promise Date** (Date / Period) — Date promised to the customer. *Service-level/on-time analysis.*  `oeel.promisedt`
- **Requested Ship Date** (Date / Period) — Date the customer requested shipment. *Compare requested vs. actual fulfillment.*  `oeel.reqshipdt`
- **Serial Number** (Property) — Serial number(s) on the invoiced line. *Trace serialized items. Aggregated comma-separated per line; Invoices stream only.*  `icets.serialno`
- **Lost Business Type** (Property (Code)) — Reason an order was lost (Orders stream only). *Analyze lost-sale reasons.*  `oeel.lostbusty`
**On-hand snapshot tied into the Sales subject for availability context.**

- **Company** (Dimension) — Operating company. *Company context for stock.*  `icsw.cono`
- **Warehouse** (Dimension) — Warehouse holding the stock. *Location context for stock.*  `icsw.whse`
- **Product Warehouse** (Key) — Product-at-warehouse identifier. *Grain for stock. Composite of product + warehouse.*  `icsw: prod + whse`
- **On-Hand Quantity** (Measure) — Units currently on hand. *Availability context alongside sales.*  `icsw.qtyonhand`
- **On-Hand Value (Average Cost)** (Measure) — Extended on-hand value at average cost. *Inventory valuation context. Extended by (qtyonhand + qtyunavail), UOM conversion via icss.csunperstk.*  `icsw.avgcost (extended)`
**Operating-company reference.**

- **Company Code** (Key) — Identifier of the operating company. *Joins company reference.*  `sasc.cono`
- **Company Name** (Property) — Display name of the operating company. *Readable company label.*  `sasc.conm`
**Warehouse reference.**

- **Warehouse Code** (Key) — Identifier of the warehouse. *Joins warehouse reference.*  `icsd.whse`
- **Warehouse Name** (Property) — Display name of the warehouse. *Readable warehouse label.*  `icsd.name`
**Master attributes describing each customer for sales analysis (mirrors AR customer with sales-relevant fields).**

- **Customer Code** (Key) — Unique identifier for the customer. *Key joining customers to sales.*  `arsc.custno`
- **Customer Name** (Property) — Display name of the customer. *Readable label.*  `arsc.name`
- **Customer Type** (Property (Code)) — Customer classification (child dimension). *Segment sales by customer category. Descriptions from sasta.*  `arsc.custtype`
- **Customer Price Type** (Property (Code)) — Pricing class for the customer (child dimension). *Analyze sales by pricing segment. Descriptions from sasta.*  `arsc.pricetype`
- **Customer Outside Rep** (Dimension) — Customer's outside rep (child dimension). *Field-rep attribution. Links to smsn.slsrep.*  `arsc.slsrepout`
- **Customer Inside Rep** (Dimension) — Customer's inside rep (child dimension). *Inside-rep attribution. Links to smsn.slsrep.*  `arsc.slsrepin`
- **Address Line 1** (Property) — Primary street address. *Contact reference.*  `arsc.addr_1`
- **Address Line 2** (Property) — Secondary address line. *Contact reference.*  `arsc.addr_2`
- **Address Line 3** (Property) — Third address line. *Contact reference.*  `arsc.addr3`
- **City** (Property) — Customer city. *Geographic grouping.*  `arsc.city`
- **State** (Property) — Customer state/province. *Geographic grouping.*  `arsc.state`
- **Postal Code** (Property) — Customer ZIP/postal code. *Geographic grouping.*  `arsc.zipcd`
- **Phone** (Property) — Customer phone number. *Contact reference.*  `arsc.phoneno`
- **Fax** (Property) — Customer fax number. *Contact reference.*  `arsc.faxphoneno`
- **Email** (Property) — Customer email address. *Contact reference.*  `arsc.email`
- **Sales Territory** (Property) — Sales territory of the customer. *Territory-level sales analysis.*  `arsc.salesterr`
- **Credit Limit** (Measure) — Maximum credit extended to the customer. *Credit context for sales.*  `arsc.credlim`
- **Account Status** (Property (Status)) — Whether the account is active. *Filter active customers. 1 = Active, otherwise Inactive.*  `arsc.statustype`
- **Last Payment Date** (Date / Period) — Date of most recent payment. *Account activity recency.*  `arsc.lastpaydt`
- **Last Sale Date** (Date / Period) — Date of most recent sale. *Sales recency.*  `arsc.lastsaledt`
- **Average Days to Pay** (Measure) — Average days the customer takes to pay. *Payment-behavior context.*  `arsc.avgpaydays`
- **Credit Manager** (Property) — Credit manager for the account. *Credit-ownership reference.*  `arsc.creditmgr`
**Master attributes for each customer ship-to (delivery) location.**

- **Ship To Code** (Key) — Identifier for the ship-to location. *Grain key. Composite of customer + ship-to suffix.*  `arss: custno + shipto`
- **Ship To Name** (Property) — Display name of the ship-to location. *Readable label.*  `arss.name`
- **Ship To Outside Rep** (Dimension) — Outside rep for the ship-to (child dimension). *Field-rep attribution by location. Links to smsn.slsrep.*  `arss.slsrepout`
- **Ship To Inside Rep** (Dimension) — Inside rep for the ship-to (child dimension). *Inside-rep attribution by location. Links to smsn.slsrep.*  `arss.slsrepin`
- **Address Line 1** (Property) — Primary street address. *Delivery reference.*  `arss.addr_1`
- **Address Line 2** (Property) — Secondary address line. *Delivery reference.*  `arss.addr_2`
- **City** (Property) — Ship-to city. *Geographic grouping.*  `arss.city`
- **State** (Property) — Ship-to state/province. *Geographic grouping.*  `arss.state`
- **Postal Code** (Property) — Ship-to ZIP/postal code. *Geographic grouping.*  `arss.zipcd`
- **Sales Territory** (Property) — Sales territory of the ship-to. *Territory analysis by location.*  `arss.salesterr`
**Master attributes for products sold, by warehouse.**

- **Product Warehouse Code** (Key) — Product-at-warehouse identifier. *Grain key. Composite of product + warehouse.*  `icsw: prod + whse`
- **Product Name** (Property) — Primary product description. *Readable product label.*  `icsp.descrip_1`
- **Description 2** (Property) — Second product description line. *Additional detail.*  `icsp.descrip_2`
- **Product** (Dimension) — Product/SKU code (child dimension). *Slice sales by product. Links to icsp.prod.*  `icsw.prod`
- **Product Line** (Dimension) — Product line (child dimension). *Group by line. Links to icsl.prodline.*  `icsw.prodline`
- **Product Category** (Dimension) — Merchandising category (child dimension). *Category-level sales analysis. From product master.*  `icsp.prodcat`
- **Stocking Status** (Property (Code)) — How the item is stocked/reordered (child dimension). *D=Direct, O=Order as Needed, X=Do not Reorder, S=Stock.*  `icsw.statustype`
- **Inventory Class** (Property (Code)) — ABC-style classification tier (child dimension). *Value/velocity tier. Values 01 through 10.*  `icsw.class`
- **Replenishment Type** (Property (Code)) — How the item is replenished (child dimension). *V=Vendor, W=Warehouse, K=Kit, C=Central Warehouse, etc.*  `icsw.arptype`
- **Vendor** (Dimension) — Primary vendor for the item (child dimension). *Tie sold items to their supplier. Links to apsv.vendno.*  `icsw.arpvendno`
- **Warehouse Rank** (Measure) — Item ranking within its warehouse. *SKU prioritization at a location.*  `icsw.whserank`
- **Company Rank** (Measure) — Item ranking across the company. *Company-wide SKU prioritization.*  `icsw.companyrank`
- **ABC Quantity Class** (Property (Code)) — ABC class by quantity movement. *Velocity-based classification.*  `icsw.abcqtyclass`
- **Average Cost** (Measure) — Average unit cost. *Reference cost basis.*  `icsw.avgcost`
- **Base Price** (Measure) — Base selling price. *Pricing reference.*  `icsw.baseprice`
- **Last Cost** (Measure) — Most recent purchase cost. *Latest acquisition cost.*  `icsw.lastcost`
- **List Price** (Measure) — List (catalog) price. *List-pricing reference.*  `icsw.listprice`
- **Replacement Cost** (Measure) — Replacement cost reference. *Replacement-cost basis.*  `icsw.replcost`
- **Standard Cost** (Measure) — Standard cost reference. *Standard-cost basis.*  `icsw.stndcost`
**Product-master reference (item level, independent of warehouse).**

- **Product Code** (Key) — Identifier of the product. *Key for product reference. Stock from icsp; non-stock from oeel.shipprod.*  `icsp.prod`
- **Product Name** (Property) — Primary product description. *Readable label. Non-stock uses oeel.proddesc.*  `icsp.descrip_1`
- **Description 2** (Property) — Second product description line. *Additional detail.*  `icsp.descrip_2`
**Supporting lookup/reference dimensions resolving codes to names across Sales.**

- **Sales Rep Code** (Key) — Identifier for a sales rep (all rep dimensions). *Key resolving rep names. Used by Order/Customer/Ship-To Outside & Inside Rep.*  `smsn.slsrep`
- **Sales Rep Name** (Property) — Readable name of the sales rep. *Business label for rep reporting.*  `smsn.name`
- **Product Line Code** (Key) — Identifier of the product line. *Key for product-line grouping.*  `icsl.prodline`
- **Product Line Name** (Property) — Display name of the product line. *Readable product-line label.*  `icsl.descrip`
- **Product Category Code** (Property (Code)) — Code value for product category. *Filtered by codeiden.*  `sasta.codeval`
- **Product Category Name** (Property) — Readable description of product category. *Business label for the category code.*  `sasta.descrip`
- **Customer Type Code** (Property (Code)) — Code value for customer classification. *Filtered by codeiden.*  `sasta.codeval`
- **Customer Type Name** (Property) — Readable description of customer type. *Business label for the customer-type code.*  `sasta.descrip`
- **Customer Price Type Code** (Property (Code)) — Code value for pricing class. *Filtered by codeiden.*  `sasta.codeval`
- **Customer Price Type Name** (Property) — Readable description of pricing class. *Business label for the price-type code.*  `sasta.descrip`
- **Supplier Code** (Key) — Identifier of the supplier. *Key for supplier reference.*  `apsv.vendno`
- **Supplier Name** (Property) — Display name of the supplier. *Readable supplier label.*  `apsv.name`
- **Taken By Code** (Key) — Login/operator code of the order taker. *Key resolving the taker's name.*  `pv_user.oper2`
- **Taken By Name** (Property) — Readable name of the order taker. *Derived from the email-address prefix.*  `pv_user.email (name from email prefix)`
- **Transaction Type Name** (Property (Code)) — Readable label for the sales transaction-type code. *Turns transtype into business terms (Stock Order, Counter Sale, etc.).*  `Hard-coded lookup from oeeh/oeel.transtype`
- **Stage Name** (Property (Code)) — Readable label for the sales stage code. *Turns stagecd (0-9) into business terms.*  `Hard-coded lookup from oeel.stagecd`
- **Stock Status Name** (Property (Code)) — Readable label for the stock-status code. *Turns specnstype into business terms.*  `Hard-coded lookup from oeel.specnstype`
- **Credit Reason Code** (Property (Code)) — Code value for credit reasons. *Filtered where codeiden = M.*  `sasta.codeval (codeiden = M)`
- **Credit Reason Name** (Property) — Readable description of the credit reason. *Business label for the credit-reason code.*  `sasta.descrip`

### TWL (Warehouse Management)

- **Company** (Dimension) — Operating company for the activity. *Separate warehouse activity across companies.*  `transactions.co_num`
- **Warehouse** (Dimension) — Warehouse where the activity occurred. *Primary slice for warehouse activity by location.*  `transactions.wh_num`
- **Product (Item)** (Dimension) — The item involved in the transaction. *Analyze activity by item.*  `transactions.item_num`
- **Employee** (Dimension) — The warehouse employee who performed the activity. *Labor productivity and accountability. Resolves to a name via Employee Name.*  `transactions.emp_num`
- **Transaction Type** (Property (Code)) — Type of warehouse activity (pick, putaway, count, move, etc.). *Separate activity types for productivity analysis. Resolves to a name via the trans_type lookup.*  `transactions.trans_type`
- **Time of Day** (Property) — Hour of day the activity occurred. *Analyze activity by hour for staffing/peak analysis. Derived: hour extracted from date_time.*  `transactions.date_time (derived hour)`
- **Day of Week** (Property) — Day of week the activity occurred. *Analyze activity by weekday. Derived from date_time.*  `transactions.date_time (derived day)`
- **Carton** (Key) — The carton involved in the activity. *Trace carton-level handling.*  `transactions.carton_id`
- **Bin** (Dimension) — The bin location involved. *Bin-level activity analysis.*  `transactions.bin_num`
- **Quantity** (Measure) — Units handled in the transaction. *Volume/throughput measure.*  `transactions.item_qty`
- **Adjusted Quantity** (Measure) — Suggested/adjusted quantity for the transaction. *Compare actual vs. suggested handling.*  `transactions.sugg_qty`
- **Transaction Number** (Key) — Unique identifier for the transaction. *Look up a specific movement.*  `transactions.trans_num`
- **Packer** (Property) — The packer associated with the activity. *Packing accountability/productivity.*  `transactions.packer`
- **Bin From** (Property) — Originating bin for a move. *Trace where stock moved from.*  `transactions.bin_from`
- **Bin To** (Property) — Destination bin for a move. *Trace where stock moved to.*  `transactions.bin_to`
- **Pallet** (Key) — The pallet involved in the activity. *Trace pallet-level handling.*  `transactions.pallet_id`
- **Pallet From** (Property) — Originating pallet for a move. *Trace pallet source.*  `transactions.pallet_id_from`
- **Cycle Count String** (Property) — Cycle-count data string for the transaction. *Support cycle-count auditing.*  `transactions.cc_string`
- **PO Number** (Key) — Purchase-order number tied to the activity (e.g., receiving). *Link receiving activity to a PO.*  `transactions.po_number`
- **Serial Number** (Property) — Serial number tied to the transaction. *Trace serialized handling.*  `transactions.serial_num`
- **Transaction Date** (Date / Period) — Date the activity occurred. *Primary date for warehouse-activity trends. Extracted from date_time (YYYYMMDD).*  `transactions.date_time (date)`
**Master/reference dimensions for the TWL subject — company, warehouse, item, employee, transaction type, bin, and carton.**

- **Company Code** (Key) — Identifier of the operating company (shared CSD dimension). *Joins company reference.*  `sasc.cono`
- **Company Name** (Property) — Display name of the operating company. *Readable company label.*  `sasc.conm`
- **Warehouse Code** (Key) — Identifier of the warehouse (shared CSD dimension). *Joins warehouse reference.*  `icsd.whse`
- **Warehouse Name** (Property) — Display name of the warehouse. *Readable warehouse label.*  `icsd.name`
- **Product Code (UPC)** (Key) — Universal product code for the item. *Barcode/UPC reference.*  `item.upc_num`
- **Product Item** (Key) — TWL item number. *Key joining items to transactions.*  `item.item_num`
- **Product Name** (Property) — Item description. *Readable item label.*  `item.item_desc`
- **Product Group** (Dimension) — Product grouping for the item. *Group warehouse activity by product family.*  `item.prod_grp`
- **Warehouse Zone (of Product)** (Property) — Warehouse zone assigned to the product (child of Product). *Zone-level activity analysis by item.*  `item.wh_zone`
- **Employee Code** (Key) — Identifier of the warehouse employee. *Key resolving employee names.*  `empmst.emp_num`
- **Employee Name** (Property) — Display name of the employee. *Readable employee label for productivity.*  `empmst.emp_name`
- **RF Logon** (Property) — The employee's RF (handheld) logon ID. *Tie activity to handheld-device logons.*  `empmst.rf_logon`
- **Transaction Type Code** (Property (Code)) — Code for the warehouse transaction type. *Key resolving transaction-type names.*  `trans_type.trans_type`
- **Transaction Type Name** (Property) — Readable description of the transaction type. *Business label (Pick, Putaway, Count, etc.).*  `trans_type.trans_name`
- **Bin Code** (Key) — Identifier of the bin location. *Key joining bin reference.*  `binmst.bin_num`
- **Bin Warehouse Zone** (Property) — Warehouse zone of the bin (child of Bin). *Zone-level bin analysis.*  `binmst.wh_zone`
- **Bin Rank (ABC)** (Property (Code)) — ABC ranking of the bin (child of Bin). *Prioritize bins by velocity/value.*  `binmst.abc`
- **Bin Cycle-Count Flag** (Property (Status)) — Whether the bin is flagged for cycle counting (child of Bin). *Identify bins in the cycle-count program.*  `binmst.cycle_flag`
- **Carton Code** (Key) — Identifier of the carton. *Key joining carton reference.*  `cartonmst.carton_num`

### Warehouse Transfers

- **Company** (Dimension) — Operating company for the transfer. *Separate transfers across companies.*  `wtel.cono`
- **Ship-To Warehouse** (Dimension) — Destination warehouse receiving the stock. *Analyze inbound transfers by destination.*  `wtel.shiptowhse`
- **Ship-From Warehouse** (Dimension) — Source warehouse sending the stock. *Analyze outbound transfers by source.*  `wteh.shipfmwhse`
- **Product Warehouse** (Key) — The product-at-warehouse being transferred. *Grain for line-level transfers. Shipping Date stream uses Ship-From; Ship Date stream uses Ship-To.*  `wtel: shipprod + shiptowhse or shipfmwhse`
- **Transaction Type** (Property (Code)) — Type of transfer document. *Separate standard transfers from special/direct orders. WT=Warehouse Transfer, SP=Special Order, DO=Direct Order.*  `wtel.transtype`
- **Stage** (Property (Code)) — Lifecycle stage of the transfer. *Track from request to received. 0=Requested, 1=Ordered, 2=Picked, 3=Shipped, 4=Pre, 5=Exception, 6=Received, 9=Cancelled.*  `wteh.stagecd`
- **Entered By** (Property) — User who entered the transfer. *Entry accountability. Links to pv_user.oper2.*  `wtel.operinit`
- **Approved By** (Property) — User who approved the transfer. *Approval accountability. Links to pv_user.oper2.*  `wtel.approveinit`
- **Order Quantity** (Measure) — Units requested on the transfer. *Requested transfer volume.*  `wtel.qtyord`
- **Ship Quantity** (Measure) — Units actually shipped. *Fulfilled transfer volume; compare to ordered.*  `wtel.qtyship`
- **Net Amount** (Measure) — Net value of the transferred goods. *Value of inter-warehouse movement.*  `wtel.netamt`
- **Cost** (Measure) — Product cost of the transferred goods. *Cost basis for transferred inventory.*  `wtel.prodcost`
- **Open Due Days** (Measure) — Days past due for open transfers. *Identify late open transfers. Applies to stagecd 1-3; zero if not yet due or not open.*  `wtel/wteh: duedt vs today`
- **Open Ship Days** (Measure) — Days since shipment for shipped transfers. *Track aging of in-transit transfers. Applies to stagecd 3; zero otherwise.*  `wteh: shipdt vs today`
- **Transfer Number** (Key) — The transfer document number. *Look up a specific transfer.*  `wtel.wtno`
- **Transfer Suffix** (Key) — Suffix distinguishing records under one transfer number. *Uniquely identify a transfer record.*  `wtel.wtsuf`
- **Transfer Line** (Key) — Line sequence within the transfer. *Identify a specific line item.*  `wtel.lineno`
- **Unit of Measure** (Property) — Unit of measure for the line. *Interpret quantities correctly.*  `wtel.unit`
- **Ship Via Type** (Property) — Shipping method/carrier for the transfer. *Analyze transfer logistics by method.*  `wteh.shipviaty`
- **Entered Date** (Date / Period) — Date the transfer was entered. *Transfer-creation date.*  `wtel.enterdt`
- **Printed Date** (Date / Period) — Date the transfer document was printed. *Document-processing milestone.*  `wteh.printeddt`
- **Due Date** (Date / Period) — Date the transfer is due. *Expected fulfillment date.*  `wtel.duedt`
- **Approval Date** (Date / Period) — Date the transfer was approved. *Approval-cycle-time analysis.*  `wtel.approvedt`
- **Requested Ship Date** (Date / Period) — Date shipment was requested. *Compare requested vs. actual shipment.*  `wteh.reqshipdt`
- **Shipped Date** (Date / Period) — Date the transfer was shipped. *Date field for the Shipping Date stream.*  `wteh.shipdt`
- **Receipt Date** (Date / Period) — Date the transfer was received. *Date field for the Ship Date stream.*  `wteh.receiptdt`
**Supporting lookup/reference dimensions resolving codes to names across Transfers.**

- **Company Code** (Key) — Identifier of the operating company. *Joins company reference.*  `sasc.cono`
- **Company Name** (Property) — Display name of the operating company. *Readable company label.*  `sasc.conm`
- **Warehouse Code** (Key) — Identifier of the warehouse. *Used by both Ship-To and Ship-From warehouse dimensions.*  `icsd.whse`
- **Warehouse Name** (Property) — Display name of the warehouse. *Readable warehouse label.*  `icsd.name`
- **Transaction Type Name** (Property (Code)) — Readable label for the transfer transaction-type code. *Turns transtype into business terms.*  `Hard-coded lookup from wtel.transtype`
- **Stage Name** (Property (Code)) — Readable label for the transfer stage code. *Turns stagecd into business terms.*  `Hard-coded lookup from wteh.stagecd`
- **Entered/Approved By Code** (Key) — Login/operator code of the entering or approving user. *Key resolving the user's name.*  `pv_user.oper2`
- **Entered/Approved By Name** (Property) — Readable name of the entering or approving user. *Derived from the email-address prefix.*  `pv_user.email (name from email prefix)`
**Master attributes for products being transferred, by warehouse.**

- **Product Warehouse Code** (Key) — Product-at-warehouse identifier. *Grain key. Composite of product + warehouse.*  `icsw: prod + whse`
- **Product Name** (Property) — Primary product description. *Readable product label.*  `icsp.descrip_1`
- **Description 2** (Property) — Second product description line. *Additional detail.*  `icsp.descrip_2`
- **Product** (Dimension) — Product/SKU code (child dimension). *Slice transfers by product.*  `icsw.prod`
- **Product Line** (Dimension) — Product line (child dimension). *Group by line. Links to icsl.prodline.*  `icsw.prodline`
- **Product Category** (Dimension) — Merchandising category (child dimension). *Category-level transfer analysis.*  `icsp.prodcat`
- **Stocking Status** (Property (Code)) — How the item is stocked/reordered (child dimension). *D=Direct, O=Order as Needed, X=Do not Reorder, S=Stock.*  `icsw.statustype`
- **Inventory Class** (Property (Code)) — ABC-style classification tier (child dimension). *Value/velocity tier.*  `icsw.class`
- **Replenishment Type** (Property (Code)) — How the item is replenished (child dimension). *V=Vendor, W=Warehouse, K=Kit, C=Central Warehouse, etc.*  `icsw.arptype`
- **Supplier** (Dimension) — Primary vendor for the item (child dimension). *Tie transferred items to supplier. Links to apsv.vendno.*  `icsw.arpvendno`
- **Warehouse Rank** (Measure) — Item ranking within its warehouse. *SKU prioritization at a location.*  `icsw.whserank`
- **Company Rank** (Measure) — Item ranking across the company. *Company-wide SKU prioritization.*  `icsw.companyrank`
- **ABC Quantity Class** (Property (Code)) — ABC class by quantity movement. *Velocity-based classification.*  `icsw.abcqtyclass`
- **Average Cost** (Measure) — Average unit cost. *Reference cost basis.*  `icsw.avgcost`
- **Base Price** (Measure) — Base selling price. *Pricing reference.*  `icsw.baseprice`
- **Last Cost** (Measure) — Most recent purchase cost. *Latest acquisition cost.*  `icsw.lastcost`
- **List Price** (Measure) — List (catalog) price. *List-pricing reference.*  `icsw.listprice`
- **Replacement Cost** (Measure) — Replacement cost reference. *Replacement-cost basis.*  `icsw.replcost`
- **Standard Cost** (Measure) — Standard cost reference. *Standard-cost basis.*  `icsw.stndcost`

---

## Common Codes & Enumerations

Decoded values for coded fields, pulled from the business glossary notes and Infor data-conversion field maps. Field names recur across many tables (Progress DB convention) — check the table name for context.

**`addoncapfl1`**
- `poerah.addoncapfl1`: (C)apitalized (E)xpensed Available Starting 4.1

**`addoncapfl2`**
- `poerah.addoncapfl2`: (C)apitalized (E)xpensed Available Starting 4.1

**`addoncapfl3`**
- `poerah.addoncapfl3`: (C)apitalized (E)xpensed Available Starting 4.1

**`addoncapfl4`**
- `poerah.addoncapfl4`: (C)apitalized (E)xpensed Available Starting 4.1

**`addondist1`**
- `poerah.addondist1`: (D)ollar,(C)ube, (W)eight or (U)nit. Required if Cap Addon Flag is Yes. Available Starting 4.1

**`addondist2`**
- `poerah.addondist2`: (D)ollar,(C)ube, (W)eight or (U)nit. Required if Cap Addon Flag is Yes. Available Starting 4.1

**`addondist3`**
- `poerah.addondist3`: (D)ollar,(C)ube, (W)eight or (U)nit. Required if Cap Addon Flag is Yes. Available Starting 4.1

**`addondist4`**
- `poerah.addondist4`: (D)ollar,(C)ube, (W)eight or (U)nit. Required if Cap Addon Flag is Yes. Available Starting 4.1

**`arptype`**
- `icsw.arptype`: (V)endor, (W)arehouse , (C)entral Whse, (K)it, V(M)I or (F)ab VA

**`billlevelcd`**
- `sastf.billlevelcd`: (A)ll, (W)arehouse, (C)ustomer or (S)hipto

**`botype`**
- `oeelb.botype`: (Y)es backorder, (N)o don't backorder or (D)irect Ship Line Item - see notes below

**`buytype`**
- `pdsv.buytype`: (Q)uantity, (W)eight, or (C)ubes

**`comptype`**
- `kpsk.comptype`: (C)omponent, (G)roup, (K)eyword, (O)ption or (R)eference

**`contracttype`**
- `pdsvc.contracttype`: (P)urchase Order Only, (O)rder Entry Only or (B)oth. Blank defaults to (B)oth.

**`currstatus`**
- `icses.currstatus`: (A)vailable, (U)navailable, (S)old, (R)etired, or (D)O

**`dirpoaddonfl`**
- `apsv.dirpoaddonfl`: (Y)es to use default direct PO addons (N) to use only one set of defaults for all Pos Available Starting 10.0

**`esourcety`**
- `icsl.esourcety`: Type products sent to eSource: (S)pecial Only, (N)on-stock Only, (B)oth special & non-stock, st(O)ck Only, (A)ll or blank for None. Available Starting 4.0

**`gststatus`**
- `icsw.gststatus`: (T)axable, (E)xempt

**`gsttype`**
- `apsv.gsttype`: Use for GST and VAT taxing methods (R)egistered, (U)nregistered or (F)oreign Entity

**`inventorystatus`**
- `icsc.inventorystatus`: Allow OE Inventory Creation as (O)AN Stock Only, OAN (N)onstock Only, (X) Neither or blank for Both Available Starting in 6.1.080

**`kitrollty`**
- `icsp.kitrollty`: (C)ost, (P)rice, (B)oth or Blank PreBuilt = P or Blank, BOD = P, C, B or Blank

**`kittype`**
- `icsp.kittype`: (P)rebuilt, (B)uild on demand or (M)ixed or Blank

**`labortype`**
- `vaspsl.labortype`: (Q)ty, (W)eight, (C)ube Required for EX sections only, other sections use blank.

**`loc_type`**
- `binmst.loc_type`: (B)ulk, (C)arousel, (F)low Rack, (P)allet, (S)helf, S(T)age

**`maxqtytype`**
- `pdsc.maxqtytype`: Quantities are (C)ube, S(p)ecial Prc Cost, (S)tocking Quantity, or (W)eight Available starting 6.1.040
- `pdsvc.maxqtytype`: (C)ube, S(p)ecial Prc Cost, (S)tocking Quantity, or (W)eight

**`minbuytype`**
- `icsl.minbuytype`: (Q)uantity,(W)eight,(D)ollars,(C)ubes

**`notestype`**
- `notes.notestype`: (C)ustomer, (V)endor, (P)roduct, (G)Catalog, (O)rder, (CS)ShipTO, (AR)Invoice,(X)PO,(XP)PO RRAR, (BA)Batch Order, (CT)Contact

**`ordcalcty`**
- `icsw.ordcalcty`: (E)oq, (C)lass, (M)in-Max, (Q)uantity Break, (B)lanket Order, or (H)uman

**`orderdisp`**
- `arsc.orderdisp`: (S)hip Complete, (T)ag and Hold, (W)ill Call, (J)ust In Time or Blank
- `poerah.orderdisp`: (S)hip Complete, (T)ag & Hold, (W)ill Call or blank

**`ordertype`**
- `icsef.ordertype`: (I)nv Control,(O)rder Entry, (P)urchase Order, Whse (T)ransfer

**`priceonty`**
- `icsc.priceonty`: (B)ase, (L)ist or (C)ost

**`priceoverfl`**
- `oeel.priceoverfl`: Identify discretionary pricing. 1 = Yes, 0 = No. Indicates a manual price override on the line.

**`pricepercenton`**
- `pdsvc.pricepercenton`: (B)ase Price, List (P)rice, (S)tandard Cost, (L)ast Cost or (R)eplacement Cost

**`prim_pick_type`**
- `binmst.prim_pick_type`: Only used when Primary Pick is Yes. Blank, (F)ull Case, (S)plit Case, (C)ounter, (P)allet

**`pround`**
- `pdsc.pround`: (U)p, (D)own or (N)earest

**`qtytype`**
- `pdsvc.qtytype`: Max Qty applied per (C)ontract, (M)onthly, (Y)early or Blank if per Order

**`rebcalcty`**
- `pdsr.rebcalcty`: $ - Amount, % - Percent of Rebate From Value, (N)et, (M)argin

**`reservety`**
- `icsw.reservety`: (D)elay, (R)eceipts, (A)lways or Blank

**`returnfl`**
- `oeel.returnfl`: Separate returns from purchases. 1 = Returned, 0 = Purchased. Drives sign-flip on value/quantity/cost. Indicates whether the line is a return.

**`sourcecd`**
- `aret.sourcecd`: Identify how the receivable was generated. 0=Invoice, 1=Service Charge, 4=COD. Origin of the transaction.

**`speccostty`**
- `icsc.speccostty`: (Y)es, (T)housand, (H)undred or Blank Recommend either "Y" or Blank

**`specnstype`**
- `oeel.specnstype`: (S)pecial Order Product, (N)on-Stock Product, (L)ost Business Canelled Line or <Blank>. Will be set to (N) if no ICSW found. Note - Cancelled Lines (L) are NOT included in order totals.

**`stagecd`**
- `poeh.stagecd`: Track progress from entry to closed. 0=Entered, 1=Ordered, 2=Printed, 3=Acknowledged, 4=Pre-Receiving, 5=Received, 6=Costed, 7=Closed, 9=Cancelled. Where the PO sits in its lifecycle.
- `oeeh.stagecd`: Track from quote to paid. 0=Quoted, 1=Ordered, 2=Picked, 3=Shipped, 4=Invoiced, 5=Paid. Lifecycle stage of the order.
- `wteh.stagecd`: Track from request to received. 0=Requested, 1=Ordered, 2=Picked, 3=Shipped, 4=Pre, 5=Exception, 6=Received, 9=Cancelled. Lifecycle stage of the transfer.

**`statustype`**
- `icsel.statustype`: (A)ctive, (I)nactive or (H)old
- `icsp.statustype`: (A)ctive, (I)nactive, (L)abor or (S)uperceded
- `icsw.statustype`: (D)irect Ship, (O)rder as needed, (S)tock, (X)-Do not reorder or (N)-OAN-Nonstock (available starting in 6.0) BOD Kits must be S

**`stock_stat`**
- `inventory.stock_stat`: (O)verage, (I)nv. Hold / Damage, (T)rans. Hold / Damage, (S)crap, (L)iquidation, (R)eturn to Vendor, (Q)A Hold, (W)ork in Process, Return (H)old, (C)ustomer Hold or Blank

**`tarbuytype`**
- `icsl.tarbuytype`: (Q)uantity,(W)eight,(D)ollars,(C)ubes

**`taxablety`**
- `icsw.taxablety`: (Y)es, (N)o, or (V)ariable Recommend Variable

**`timeactty`**
- `vaspsl.timeactty`: (E)stimated, (A)ctual Used on IT and IS sections only

**`transcd`**
- `apet.transcd`: Filter to separate invoices from payments and credits. Codes: 0=Invoice Debit, 3=Scheduled Payment, 6=Credit Memo, 7=Payment Record. What kind of AP activity the row represents (invoice, payment, credit memo, scheduled payment, etc.).
- `aret.transcd`: Separate billings from cash and credits. 0=Invoice, 1=Service Charge, 3=Unapplied Cash, 6=Credit Memo, 7=Check Record. Type 11 is filtered out. Type of AR activity (invoice, payment, credit memo, service charge, unapplied cash, etc.).

**`transtype`**
- `oeeh.transtype`: (SO)Stock Order, (RM)Return, (DO)Direct, (CR)Correction, (CS)Counter Sale. See Chart Below.

**`usagectrl`**
- `icsl.usagectrl`: Available Starting 10.2.1.0 (F)orward, (B)ackward, (T)rend %, (D)emand Planning, (1)-(9) Alpha Factor, or Blank
- `icsw.usagectrl`: (F)orward, (B)ackward, (T)rend %, (D)emand Planning, (1)-(9) Alpha Factor, or Blank D Available starting 10.2.1.0

**`wmallocty`**
- `icsw.wmallocty`: (C)ube Capacity, (S)ize Type or Blank

**`xrefprodty`**
- `oeel.xrefprodty`: Type of Requested product: (C)ustomer, (I)nterchange, Su(P)erced, (S)ubstitute, (U)pgrade

---

## Table Definitions

Field flags: `[i]`=indexed (fast join/filter), `[m]`=mandatory, `[im]`=both. Tables enriched with **Field Notes** come from Infor data-conversion field maps (purpose, expected values, cross-reference tables, required flags) — the most reliable source for what a code actually means.

### `XL_Language`
**A list of languages**

### `XL_instance`
**Contains procedure-level instances of each string**

### `XL_string_info`
**Source phrases as defined in the source code**

### `XL_translation`
**Contains translation strings for foreign languages**

### `abc`
Fields: `co_num` (char) [im], `wh_num` (char) [im], `a_count_percent` (deci-2), `b_count_percent` (deci-2), `c_count_percent` (deci-2), `d_count_percent` (deci-2), `a_count_interval` (inte), `b_count_interval` (inte), `c_count_interval` (inte), `d_count_interval` (inte), `recalc_interval` (inte) [m], `recalc_timeframe` (char) [m], `recalc_last` (date) [i], `recalc_type` (char), `count_type` (char), `a_count_loc` (inte), `b_count_loc` (inte), `c_count_loc` (inte), `d_count_loc` (inte), `custom_data` (char[5]), `trans_sec_time` (inte) [m], `proc_created` (char), `history_interval` (inte) [m], `history_timeframe` (char) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `recalc_pend_date` (date) [i], `recalc_pending` (logi) [i], `exclude_prod_cat` (char), `recalc_lasttz` (datetm-tz), `recalc_pend_datetz` (datetm-tz), `trans_datetz` (datetm-tz), `cono` (inte) [i], `activityid` (deci-0) [im], `oper2` (char) [i], `activitycd` (char), `actstartdt` (date), `actstarttm` (char), `actstopdt` (date), `actstoptm` (char), `durationtm` (char), `comment` (char), `name` (char), `notesfl` (char), `phoneno` (char), `resultcd` (char), `schstartdt` (date) [i], `schstarttm` (char) [i], `statuscd` (char) [i], `priority` (inte), `parentactvid` (deci-0) [i], `contactid` (deci-0) [i], `subjecttype` (char) [i], `subjectprimarykey` (char) [i], `subjectsecondkey` (char) [i], `doctype` (char) [i], `docorderno` (inte) [i], `docordersuf` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `whse` (char), `msgwinselectfl` (logi) [m], `groupnm` (char) [i], `groupseqno` (inte) [i], `docjobid` (char) [i], `docjobrevno` (inte) [i], `actstopdttz` (datetm-tz)

### `activities`
**Activities Master**

### `addon`
**Addon Data**
Fields: `cono` (inte) [i], `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `seqno` (inte) [i], `addonno` (inte) [i], `addontype` (logi) [m], `addonamt` (deci-2), `addonnet` (deci-2), `addondist` (deci-2), `addondistr` (char), `addtaxgroup` (inte), `addoverfl` (logi) [m], `prevaddamt` (deci-2), `prevaddtype` (logi) [m], `keyindex` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `addoncapfl` (logi) [m], `directfl` (logi) [m], `transdttmz` (datetm-tz) [i], `rowpointer` (char) [i]

### `aodata`
**Administrative Options Data Table**
Fields: `cono` (inte) [im], `recordtype` (char) [i], `fieldname` (char) [i], `fieldvalue` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `rowpointer` (char) [i]

### `apeba`
**AP Batch Addons**
Fields: `cono` (inte) [i], `jrnlno` (inte) [i], `setno` (inte) [i], `addonno` (inte) [i], `vendno` (deci-0) [im], `apinvno` (char) [i], `transdt` (date), `transtm` (char), `origamt` (deci-2), `applyamt` (deci-2), `updatefl` (logi) [m], `currencyty` (char), `exchgrate` (deci-7[2]), `statustype` (logi) [im], `pono` (inte) [im], `operinit` (char), `alloctype` (char), `posuf` (deci-0) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `apebc`
**AP Batch Costing**
Fields: `cono` (inte) [i], `vendno` (deci-0) [i], `apinvno` (char) [i], `pono` (inte) [i], `costord` (deci-5), `statustype` (logi) [im], `proddesc` (char), `qtycost` (deci-2), `cost` (deci-5), `currencyty` (char), `exchgrate` (deci-7[2]), `jrnlno` (inte) [i], `setno` (inte) [i], `whse` (char), `costrcv` (deci-5), `qtyord` (deci-2), `qtyrcv` (deci-2), `unitconv` (deci-5), `eachfl` (logi) [m], `shipprod` (char) [m], `operinit` (char), `transdt` (date), `transtm` (char), `posuf` (deci-0) [i], `lineno` (deci-0) [i], `autorecfl` (char), `proddesc2` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `updatefl` (logi) [m], `transproc` (char), `revalno` (inte)

### `apebt`
**AP Batch Transaction**
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `invsuf` (inte), `amount` (deci-2), `discamt` (deci-2), `transcd` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `seqno` (inte) [i], `setno` (inte) [i], `invdt` (date), `duedt` (date), `discdt` (date), `refer` (char), `disputefl` (logi) [m], `termstype` (char) [m], `batchnm` (char) [i], `duedays` (inte), `discdays` (inte), `nopays` (inte), `freqdays` (inte), `discpct` (deci-5), `apinvno` (char) [i], `invtype` (char), `immedpyfl` (logi) [m], `name` (char) [m], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `manaddrfl` (logi) [m], `checkno` (deci-0), `bankno` (inte), `addonamt` (deci-2[2]), `gsttaxamt` (deci-2), `psttaxamt` (deci-2), `currencyty` (char), `exchgrate` (deci-7[2]), `divno` (inte), `maxpost` (inte), `nopost` (inte), `notresaleamt` (deci-2), `createdby` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `jrnlno` (inte), `suspfl` (logi) [m], `transproc` (char), `addr3` (char), `discdttz` (datetm-tz), `duedttz` (datetm-tz), `invdttz` (datetm-tz)

### `apef`
**Accounts Payable Floor Plan Entries**
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `apinvno` (char) [i], `termstype` (char) [im], `jrnlno` (inte) [i], `setno` (inte) [i], `statustype` (logi) [im], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `apei`
**AP Group Invoice Transaction**
Fields: `cono` (inte) [i], `vendno` (deci-0) [i], `amount` (deci-2), `transcd` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `groupseqno` (inte) [i], `invdt` (date) [i], `duedt` (date), `discdt` (date), `refer` (char), `disputefl` (logi) [m], `termstype` (char), `groupnm` (char) [i], `nopays` (inte), `freqdays` (inte), `discpct` (deci-2), `apinvno` (char) [i], `invtype` (char), `immedpyfl` (logi) [m], `name` (char), `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `manaddrfl` (logi) [m], `checkno` (deci-0), `bankno` (inte), `gsttaxamt` (deci-2), `psttaxamt` (deci-2), `currencyty` (char), `exchgrate` (deci-7[2]), `divno` (inte), `maxpost` (inte), `nopost` (inte), `notresaleamt` (deci-2), `createdby` (char), `suspfl` (logi) [m], `transproc` (char), `createddt` (date) [i], `invseqno` (inte) [i], `apetjrnlno` (inte), `apetsetno` (inte), `appinvdt` (date), `appinvno` (char), `apptranscd` (inte), `origdisc` (deci-2), `sourcecd` (inte), `statustype` (logi) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `xxc1` (char), `xxl1` (logi) [m], `autorecfl` (logi) [m], `paidseqno` (inte), `stagecd` (inte) [i], `proctype` (char), `statusmsg` (char), `gldefaultfl` (logi) [m], `gloverfl` (logi) [m], `newinvfl` (logi) [m], `termsoverfl` (logi) [m], `edifl` (logi), `reconoverfl` (logi), `reconty` (char), `notesfl` (char), `costty` (char), `appseqno` (inte), `addr3` (char), `openinit` (char), `revalno` (inte), `rowpointer` (char) [i], `settamt` (deci-2), `selfassessfl` (logi) [m], `npclaimno` (char), `nppaidinfullfl` (logi) [m], `appinvdttz` (datetm-tz), `createddttz` (datetm-tz), `discdttz` (datetm-tz), `duedttz` (datetm-tz), `invdttz` (datetm-tz)

### `apeia`
**AP Group Invoice Addons/Discounts**
Fields: `cono` (inte) [i], `addonno` (inte) [i], `vendno` (deci-0) [i], `apinvno` (char) [i], `transdt` (date), `transtm` (char), `origamt` (deci-2), `applyamt` (deci-2), `updatefl` (logi) [m], `statustype` (logi) [im], `operinit` (char), `alloctype` (char), `transproc` (char), `groupnm` (char) [i], `createddt` (date) [i], `groupseqno` (inte) [i], `addonseqno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `capfl` (logi) [m], `createddttz` (datetm-tz)

### `apeid`
**AP Group Invoice Costing Detail**
Fields: `cono` (inte) [i], `vendno` (deci-0) [i], `apinvno` (char) [i], `pono` (inte) [i], `costord` (deci-5), `statustype` (logi) [im], `polnseqno` (inte), `proddesc` (char), `cost` (deci-5), `whse` (char), `costrcv` (deci-5), `qtyord` (deci-2), `qtyrcv` (deci-2), `unitconv` (deci-5), `eachfl` (logi) [m], `shipprod` (char) [i], `proctype` (char), `operinit` (char), `transdt` (date), `transtm` (char), `lineno` (inte) [i], `proddesc2` (char), `updatefl` (logi) [m], `transproc` (char), `bundleid` (char) [i], `compseqno` (inte) [i], `groupnm` (char) [i], `createddt` (date) [i], `groupseqno` (inte) [i], `detailseqno` (inte) [i], `detailty` (char) [i], `receiverno` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `buyermsg` (char), `qtybuyer` (deci-2), `costbuyer` (deci-5), `addonseqno` (inte), `posuf` (inte) [i], `reconoverfl` (logi), `invunit` (char), `pounit` (char), `closefl` (logi) [m], `addonapplyty` (char), `addonfrompoln` (inte), `addontopoln` (inte), `addonpolnlist` (char), `vendprod` (char) [i], `closewhencostedfl` (logi) [m], `podoshipdt` (date), `createddttz` (datetm-tz), `podoshipdttz` (datetm-tz), `lastcostupdtfl` (logi) [m], `suppwarrallowpct` (deci-5), `suppwarrallownet` (deci-2)

### `apeie`
**AP Batch update and reconcilation errors**
Fields: `cono` (inte) [i], `groupnm` (char) [i], `createddt` (date) [i], `groupseqno` (inte) [i], `tablenm` (char) [i], `invseqno` (inte) [i], `errorseqno` (inte) [i], `errorno` (inte) [m], `errormsg` (char), `program` (char), `errorfld` (char), `vendno` (deci-0) [i], `apinvno` (char) [i], `transcd` (inte), `proctype` (char), `stagecd` (inte), `addonno` (inte), `pono` (inte) [i], `posuf` (deci-0) [i], `lineno` (deci-0) [i], `shipprod` (char), `receiverno` (char), `detailty` (char), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `buyer` (char) [i], `createddttz` (datetm-tz)

### `apeig`
**AP Group Invoice GL Transactions**
Fields: `cono` (inte) [i], `groupnm` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `amount` (deci-2), `transcd` (inte), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `groupseqno` (inte) [i], `transproc` (char), `createddt` (date) [i], `glseqno` (inte) [i], `statustype` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `xxc5` (char), `addonno` (inte), `notupdatablefl` (logi) [m], `postwhencostedfl` (logi) [m], `gltype` (char), `createddttz` (datetm-tz)

### `apeis`
**AP Group Invoice Costing Detail - Serial Numbers**
Fields: `cono` (inte) [im], `groupnm` (char) [im], `createddt` (date) [im], `groupseqno` (inte) [im], `detailseqno` (inte) [im], `serialno` (char) [im], `comment` (char), `transproc` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `createddttz` (datetm-tz)

### `apemf`
**Accounts Payable Floor Plan Entries Modified**
Fields: `cono` (inte) [i], `vendno` (deci-0) [m], `apinvno` (char) [i], `termstype` (char) [im], `prod` (char) [im], `qtydirected` (deci-2), `seqno` (inte) [i], `statustype` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `qtyavail` (deci-2), `pono` (inte) [im], `posuf` (inte) [i], `lineno` (inte) [i], `amtdue` (deci-2), `soldserfl` (logi) [m], `paidnsfl` (logi) [m], `invoicedt` (date) [i], `qtysold` (deci-2), `sorttype` (char) [i], `urecno` (deci-0) [i], `location` (char) [i], `transproc` (char), `invoicedttz` (datetm-tz)

### `apemm`
**AP Manual Addresses**
Fields: `cono` (inte) [i], `vendno` (deci-0) [m], `apinvno` (char), `jrnlno` (inte) [i], `setno` (inte) [i], `amount` (deci-2), `refer` (char), `name` (char) [m], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `operinit` (char), `transtm` (char), `transdt` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `addr3` (char)

### `apet`
**Accounts Payable Entries**
*AP transactions — vendor invoices and credits.*
**Operators call this:** "Company" (Accounts Payable), "Supplier" (Accounts Payable), "Transaction Type" (Accounts Payable), "Invoice Type" (Accounts Payable), "Created By" (Accounts Payable), "Invoice Amount" (Accounts Payable), "Amount Paid" (Accounts Payable), "Discount Taken" (Accounts Payable), "Invoice Number" (Accounts Payable), "Invoice Suffix" (Accounts Payable), "Check Number" (Accounts Payable), "Reference" (Accounts Payable), "Journal Number" (Accounts Payable), "Set Number" (Accounts Payable), "Payment Terms" (Accounts Payable), "GL Account" (Accounts Payable), "GL Division" (Accounts Payable), "GL Department" (Accounts Payable), "Invoice Date" (Accounts Payable), "Due Date" (Accounts Payable), "Payment Date" (Accounts Payable), "Last Changed By" (Accounts Payable), "Transaction Type Name" (Accounts Payable)
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `statustype` (logi) [im], `transcd` (inte) [i], `apinvno` (char) [i], `seqno` (inte) [i], `budgetno` (inte), `amount` (deci-2), `sourcecd` (inte), `jrnlno` (inte) [i], `perfisc` (inte), `percal` (inte), `setno` (inte) [i], `transno` (inte), `invdt` (date) [i], `discamt` (deci-2), `duedt` (date), `discdt` (date), `termstype` (char) [m], `paymtdt` (date), `paymtcd` (inte), `paymtamt` (deci-2), `origseqno` (inte), `nextseqno` (inte), `refer` (char), `transdt` (date), `transtm` (char), `operinit` (char), `jrnlamt` (deci-2), `disputefl` (logi) [m], `invtype` (char), `immedpyfl` (logi) [m], `bankno` (inte), `checkno` (deci-0), `divno` (inte), `chkprintfl` (logi) [m], `addonamt` (deci-2[2]), `manaddrfl` (logi) [m], `vendtype` (char), `pidjrnlno` (inte) [i], `pidsetno` (inte) [i], `vendno2` (deci-0), `manchkfl` (logi) [m], `module` (char), `gsttaxamt` (deci-2), `psttaxamt` (deci-2), `capaddonamt` (deci-2), `currencyty` (char), `exchgrate` (deci-7[2]), `origdisc` (deci-2), `postdt` (date), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `createdby` (char), `notesfl` (char), `fppayfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `urecno` (deci-0) [i], `apinvsuf` (inte), `appinvdt` (date), `appinvno` (char), `apptranscd` (inte), `appinvsuf` (inte), `apinvnosuf` (inte), `location` (char) [i], `transproc` (char), `wordindexfl` (logi) [m], `allocationty` (char), `rowpointer` (char) [i], `revalno` (inte), `bacsref` (char), `transdttmz` (datetm-tz) [i], `npclaimno` (char), `achinvno` (char), `achinvsuf` (inte), `achbankno` (inte), `appinvdttz` (datetm-tz), `discdttz` (datetm-tz), `duedttz` (datetm-tz), `invdttz` (datetm-tz), `paymtdttz` (datetm-tz), `postdttz` (datetm-tz), `percaltz` (datetm-tz), `perfisctz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `vendno` (Vendor #) — Can be CHAR(24) if using the Xref.; Valid values/xref: APSV; Required
- `transcd` (Transaction Code) — See Notes Below; Valid values/xref: 0, 5, 6, 8; Required
- `amount` (Amount) — See Notes Below In vendor currency; Required
- `divno` (Div#) — See Notes Below; Valid values/xref: SASTT - V; Default: Entered Value
- `invtype` (Invoice Type) — Used for Check Processing
- `immedpyfl` (Immediate Pay) — (Y)es or (N)o; Valid values/xref: Y, N; Default: N
- `disputefl` (Dispute Flag) — (Y)es or (N)o; Valid values/xref: Y, N; Default: N
- `termstype` (Terms) — Valid values/xref: SASTT - T; Required
- `discamt` (Discount Amount) — Must have AO set to take discounts on Credits to use with MC
- `checkno` (Check #) — Only allowed for Trans Code 6 if recording prior payment
- `bankno` (Bank #) — Only allowed for Trans Code 6 if recording prior payment; Valid values/xref: CRSB; Default: 0
- `currencyty` (Currency Type) — Vendor must be setup for Foreign Currency; Valid values/xref: SASTC
- `exchgrate1` (Exchange Rate1) — Vendor must be setup for Foreign Currency Exchange rate for invoice; Default: 1
- `exchgrate2` (Exchange Rate1) — Vendor must be setup for Foreign Currency Exchange rate for payment; Default: 1
- `user5` (user5) — Used for Conversion Import ID

### `apeta`
**ACH Credit Payments**
Fields: `achinvno` (char) [im], `achinvsuf` (char) [im], `amount` (deci-2), `bankno` (inte) [i], `token` (char), `charmedia` (char), `commcd` (inte), `cono` (inte) [im], `createdt` (date) [i], `createtm` (char), `currproc` (char), `currencyty` (char), `srcrowpointer` (char) [i], `mediacd` (inte), `merchantid` (char), `operinit` (char), `processno` (inte), `responsedt` (date), `response` (char), `responsetm` (char), `rowpointer` (char) [i], `shipfm` (inte), `statustype` (logi) [im], `submitdt` (date), `submittm` (char), `transcd` (char), `user1` (char), `transproc` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `vendno` (deci-0) [im], `vendno2` (deci-0), `whse` (char), `transdttmz` (datetm-tz), `createdttz` (datetm-tz), `responsedttz` (datetm-tz), `submitdttz` (datetm-tz)

### `apsd`
**Accounts Payable Setup defaults**
Fields: `cono` (inte) [im], `srcrowpointer` (char) [im], `shipviaty` (char) [im], `minleaddays` (inte), `deliverycd` (char), `shipsrvcd` (char), `addonno` (inte[2]), `addonamt` (deci-2[2]), `addontype` (logi[2]) [m], `capaddonno` (inte[4]), `capaddonamt` (deci-2[4]), `capaddontype` (logi[4]) [m], `diraddonno` (inte[2]), `diraddonamt` (deci-2[2]), `diraddontype` (logi[2]) [m], `dircapaddonno` (inte[4]), `dircapaddonamt` (deci-2[4]), `dircapaddontype` (logi[4]) [m], `wodiscpct` (deci-2), `wodisctype` (logi) [m], `usewodisc` (logi) [m], `useaddons` (logi) [m], `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `dirpoaddonfl` (logi) [m]

### `apsf`
**Accounts Payable Setup Federal Tax 1099**
Fields: `cono` (inte) [i], `taxyear` (inte) [i], `transmittername` (char), `companyname` (char), `companyname2` (char), `companyaddress` (char), `companycity` (char), `companystate` (char), `companyzip` (char), `contact` (char), `contactphone` (char), `contactemail` (char), `controlcode` (char), `fedtaxid` (char), `mediano` (char), `testfilefl` (logi) [m], `foreignentityfl` (logi) [m], `magtapefl` (logi) [m], `replacementfilechar` (char), `replacementfilename` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `apsp`
**AP Purchase History**
*AP purchase history by vendor.*
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `prodline` (char) [im], `yr` (inte) [i], `noinvbill` (inte), `nolinebill` (inte), `qtysold` (deci-2[12]), `purchamt` (deci-2[12]), `salesamt` (deci-2[12]), `cogamt` (deci-2[12]), `transdt` (date), `transtm` (char), `operinit` (char), `whse` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `transdttmz` (datetm-tz) [i], `yrtz` (datetm-tz), `rowpointer` (char) [i]

### `apss`
**AP Ship To**
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `shipfmno` (inte) [i], `name` (char) [m], `addr` (char[2]), `city` (char) [i], `state` (char) [i], `zipcd` (char) [i], `phoneno` (char) [i], `faxphoneno` (char), `slsnm` (char), `slsphoneno` (char), `expednm` (char), `exphoneno` (char), `apcustno` (char), `edilevel` (inte), `shipviaty` (char), `bofl` (logi) [m], `subfl` (logi) [m], `transdt` (date), `transtm` (char), `operinit` (char), `enterdt` (date), `dunsno` (char), `epotype` (char), `epoto` (logi) [m], `edipartner` (char), `langcd` (char), `ediyouraddr` (char), `edipartaddr` (char), `edipover` (char), `edienvtag` (char[2]), `edioutpswd` (char), `ediinpswd` (char), `edictrlno` (inte), `edinetwork` (char), `edi846ver` (char), `edi846no` (inte), `ecommercety` (char), `email` (char), `countrycd` (char), `equotetype` (char), `synccrmfl` (logi) [m], `equoteto` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `ptxcono` (inte), `ptxwhse` (char) [m], `ptxackfl` (logi) [m], `printfl` (logi) [m], `addr3` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `keyindex` (char), `freightexpectedty` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `intratodcd` (inte), `geocd` (inte), `outofcityfl` (logi) [m], `supaccessvendlocid` (char), `frttermscd` (char), `transferloc` (char), `esbactioncode` (char), `limitshipvia` (logi) [m], `transdttmz` (datetm-tz) [i], `statustype` (logi) [m], `allowpofl` (logi) [m], `restricteditfl` (logi) [m], `enterdttz` (datetm-tz), `addressoverfl` (logi) [m]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `vendno` (Vendor #) — Can be CHAR(24) if using the Xref.; Valid values/xref: APSV; Required
- `shipfmno` (Ship From) — Part of Primary Unique Index; Required
- `addr3` (Address 3) — Available for all companies starting in 6.1.040. Only accessible for Int'l companies in versions 4.2.002 - 6.1.030.
- `city` (City) — Length 20 prior to 6.1.040
- `state` (State) — Not used with Freeform Style Address AO option starting in 6.1.040.
- `geocd` (GEO Code) — Only used with Taxware Available starting in 6.1.060
- `outofcityfl` (Outside City Limits Flag) — Only used with Taxware Enterprise Available starting in 6.1.060; Valid values/xref: Y or N; Default: N
- `countrycd` (Country) — Valid values/xref: SASTT-W
- `langcd` (LanguageCode) — Valid values/xref: SASTT - Y
- `shipviaty` (Ship Via) — Valid values/xref: SASTT - S
- `limitshipvia` (Limit Ship Via) — Available Starting 10.3 Setup Shipvias in APSD after conversion; Valid values/xref: Y or N; Default: N
- `frttermscd` (Freight Terms) — Available Starting 10.0; Valid values/xref: SASTT - FT
- `transferloc` (Transfer Location) — Available Starting 10.0
- `bofl` (Back Orders OK) — Valid values/xref: Y or N; Default: Y
- `subfl` (Substitutes OK) — Valid values/xref: Y or N; Default: Y
- `synccrmfl` (Sync to CRM) — Available Starting 4.1; Valid values/xref: Y or N; Default: Y
- `freightexpectedty` (Freight Expected Type) — Available Starting 6.1; Valid values/xref: Y or N; Default: Y
- `intratodcd` (Intrastat Terms of Delivery code) — Used with VAT only. Required if country setup to report intrastat in SASTT Country setup Availabel starting 6.1.080; Valid values/xref: SASTT-TD
- `epotype` (Purchase Orders) — Valid values/xref: (F)ax, (E)di, (X)ML, E(M)ail, (I)ON or Blank
- `epoto` (PO To:) — Valid values/xref: (V)endor or (S)hipfrom; Default: S
- `equotetype` (Quotes) — Valid values/xref: (F)ax, (E)di, (X)ML, E(M)ail or Blank
- `equoteto` (Quotes To:) — Valid values/xref: (V)endor or (S)hipfrom; Default: S
- `edi846ver` (Inv Adv. Version) — Valid values/xref: ANSI Version
- `edipover` (PO Version) — Valid values/xref: ANSI Version
- `ecommercety` (Comm Type) — Available Starting 4.0; Valid values/xref: eBuy or blank
- `supaccessvendlocid` (Supplier Access Vendor Location ID) — Available Starting in 6.1.060
- `user5` (user5) — Used for Conversion Import ID
- `user10` (user10) — Available Starting 5.5
- `user11` (user11) — Available Starting 5.5
- `user12` (user12) — Available Starting 5.5
- `user13` (user13) — Available Starting 5.5
- `user14` (user14) — Available Starting 5.5
- `user15` (user15) — Available Starting 5.5
- `user16` (user16) — Available Starting 5.5
- `user17` (user17) — Available Starting 5.5
- `user18` (user18) — Available Starting 5.5
- `user19` (user19) — Available Starting 5.5
- `user20` (user20) — Available Starting 5.5
- `user21` (user21) — Available Starting 5.5
- `user22` (user22) — Available Starting 5.5
- `user23` (user23) — Available Starting 5.5
- `user24` (user24) — Available Starting 5.5
- `statustype` (statustype) — Available Starting in 11.18.9; Valid values/xref: Y or N; Default: Y
- `allowpofl` (allowpofl) — Available Starting in 11.18.9; Valid values/xref: Y or N; Default: Y
- `restricteditfl` (Restricted Editing) — Valid values/xref: Y or N; Default: N

### `apsv`
**Vendor Master**
*Vendor master — AP equivalent of arsc. Supplier info, terms, contacts.*
**Operators call this:** "Supplier Code" (Accounts Payable), "Supplier Name" (Accounts Payable), "Supplier Type" (Accounts Payable), "Invoice Type" (Accounts Payable), "Address Line 1" (Accounts Payable), "Address Line 2" (Accounts Payable), "City" (Accounts Payable), "State" (Accounts Payable), "Postal Code" (Accounts Payable), "Phone" (Accounts Payable), "Fax" (Accounts Payable), "Email" (Accounts Payable), "Account Manager" (Accounts Payable), "Payment Terms" (Accounts Payable), "Supplier Code" (Inventory), "Supplier Name" (Inventory), "Supplier Code" (Purchasing), "Supplier Name" (Purchasing), "Supplier Type" (Purchasing), "Supplier Code" (Sales), "Supplier Name" (Sales)
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `name` (char) [m], `addr` (char[2]), `city` (char) [i], `state` (char) [i], `zipcd` (char) [i], `lookupnm` (char) [i], `phoneno` (char) [i], `faxphoneno` (char), `slsnm` (char), `expednm` (char), `exphoneno` (char), `bankno` (inte), `slsphoneno` (char), `apcustno` (char), `fedtaxid` (char), `comment` (char), `statustype` (logi) [m], `shipviaty` (char), `termstype` (char) [m], `invtype` (char), `apvendcls` (inte), `bofl` (logi) [m], `subfl` (logi) [m], `orderdisp` (char), `fed1099no` (inte), `fed1099box` (inte), `notimelate` (inte), `nopoytd` (inte), `lastpono` (inte), `divno` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `enterdt` (date), `currbal` (deci-2), `paymtly` (deci-2), `ordbal` (deci-2), `ecommercety` (char), `rebatesdue` (deci-2), `updtprice` (char), `disctknytd` (deci-2), `erebtype` (char), `disclstytd` (deci-2), `countrycd` (char), `invytd` (deci-2), `ap1099nm` (char), `paymtytd` (deci-2), `equotetype` (char), `returnsytd` (deci-2), `rebatesytd` (deci-2), `invly` (deci-2), `discly` (deci-2), `returnsly` (deci-2), `rebatesly` (deci-2), `disputevndfl` (logi) [m], `lastinvdt` (date), `salesmgrfl` (logi) [m], `lastpaydt` (date), `lastpodt` (date), `lastactdt` (date), `user3` (char), `gldivno` (inte[6]), `user4` (char), `gldeptno` (inte[6]), `user5` (char), `glacctno` (inte[6]), `user6` (deci-5), `glsubno` (inte[6]), `user7` (deci-5), `addonno` (inte[2]), `user8` (date), `user9` (date), `resalefl` (logi) [m], `fobfl` (logi) [m], `vendno2` (deci-0), `vendtype` (char), `notesfl` (char), `arcustno` (deci-0) [im], `dunsno` (char), `rmaamount` (deci-2), `nopocopies` (inte), `epotype` (char), `edipartner` (char) [i], `currencyty` (char), `langcd` (char), `gsttype` (char), `gststatus` (logi) [m], `domesticbal` (deci-2), `wodiscpct` (deci-2), `user1` (char), `user2` (char), `capaddonamt` (deci-2[4]), `capaddontype` (logi[4]) [m], `capaddonno` (inte[4]), `wodisctype` (logi) [m], `edinetwork` (char), `edioutpswd` (char), `ediinpswd` (char), `edipartaddr` (char), `ediyouraddr` (char), `edictrlno` (inte), `edipover` (char), `edienvtag` (char[2]), `edi846ver` (char), `edi846no` (inte), `grossnetfl` (logi) [m], `centbuyfl` (logi) [m], `vendbankacct` (char), `vendbanktrno` (char), `paymentty` (char), `email` (char), `webpageext` (char), `updtsrc` (char), `webpage` (char), `apholdfl` (logi) [m], `synccrmfl` (logi) [m], `epmttype` (char), `keyindex` (char), `transproc` (char), `proctype` (char), `apinvtolpct` (deci-2), `apinvtolamt` (deci-2), `aplntolamt` (deci-2), `apqtytolamt` (deci-2), `apqtytolpct` (deci-2), `apvendtolfl` (logi) [m], `aplntolpct` (deci-2), `coreprice` (char), `taxmethod` (char), `ptxcono` (inte), `ptxwhse` (char) [m], `ptxackfl` (logi) [m], `exclecomm` (char), `printfl` (logi) [m], `addr3` (char), `weightty` (char), `addonamt` (deci-2[2]), `addontype` (logi[2]) [m], `wlasncreate` (logi) [m], `exclmdd` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `edi845netfmty` (char), `edi845netdwnto` (char), `edi845pcttoty` (char), `freightexpectedty` (char), `wlasnautorcvfl` (logi) [m], `wlblockpofl` (logi) [m], `rowpointer` (char) [i], `wordindexfl` (logi) [m], `intratodcd` (inte), `geocd` (inte), `addvatsettfl` (logi) [m], `outofcityfl` (logi) [m], `ap1099nmctrl` (char), `taxgroupno` (inte), `statecd` (char), `supaccessfl` (logi) [m], `supaccesscommty` (char), `supaccessftpaddr` (char), `supaccessftpuserid` (char), `supaccessftppasswd` (char), `supaccessftsyscode` (char), `supaccesshttpurl` (char), `supaccesshttpuserid` (char), `supaccesshttppasswd` (char), `supaccessprodidty` (char), `incladdonsfl` (logi) [m], `frttermscd` (char), `diraddonamt` (deci-2[2]), `diraddontype` (logi[2]) [m], `diraddonno` (inte[2]), `dircapaddonamt` (deci-2[4]), `dircapaddontype` (logi[4]) [m], `dircapaddonno` (inte[4]), `dirpoaddonfl` (logi) [m], `transferloc` (char), `esbactioncode` (char), `bacsref` (char), `rebatemultiplier` (char), `paymethod` (char), `underpmttolamt` (deci-2), `vendbankacctname` (char), `underpmttoltype` (logi) [m], `vendbankaccttype` (char), `overpmttolamt` (deci-2), `vendbanksortcode` (char), `overpmttoltype` (logi) [m], `limitshipvia` (logi) [m], `gldeptno2` (inte[6]), `glacctno2` (inte[6]), `gldivno2` (inte[6]), `glsubno2` (inte[6]), `esbgroupnm` (char), `esbtermshierarchyfl` (logi) [m], `esballowinvnopofl` (logi) [m], `esbapplyovrrcptfl` (logi) [m], `esbsetnotesprintfl` (logi) [m], `transdttmz` (datetm-tz) [i], `netbillfl` (logi) [m], `manrebspecfl` (logi) [m], `netbillreturns` (logi) [m], `esb855isetnotesprintfl` (logi) [m], `esb855ivmipotypefl` (logi) [m], `edi852usestatusfl` (logi) [m], `edi867ty` (char), `allowpofl` (logi) [m], `restricteditfl` (logi) [m], `enterdttz` (datetm-tz), `lastactdttz` (datetm-tz), `lastinvdttz` (datetm-tz), `lastpaydttz` (datetm-tz), `lastpodttz` (datetm-tz), `suppwarrallowpct` (deci-5), `edi820email` (char), `addressoverfl` (logi) [m], `repricepct` (deci-2)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `vendno` (Vendor #) — Can be CHAR(24) if using the Xref.; Required
- `name` (Name) — Name to print on check; Required
- `lookupnm` (Look Up Name) — Short Name for Searching for Vendor; Default: 1st 15 char of name
- `addr1` (Address) — Address to print on check
- `addr3` (Address) — Available for all companies starting in 6.1.040. Only accessible for Int'l companies in versions 4.2.002 - 6.1.030.
- `city` (City) — Length 20 prior to 6.1.040
- `state` (State) — Not used with Freeform Style Address AO option starting in 6.1.040.
- `geocd` (GEO Code) — Only used with Taxware Enterprise Available starting in 6.1.060
- `outofcityfl` (Outside City Limits Flag) — Only used with Taxware Enterprise Available starting in 6.1.060; Valid values/xref: Y or N; Default: N
- `countrycd` (Country) — Valid values/xref: SASTT-W
- `statustype` (Status) — Valid values/xref: (A)ctive or (I)nactive; Default: A
- `disputevndfl` (Dispute) — Valid values/xref: Y or N; Default: N
- `termstype` (Terms) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-T; Default: DCAOV Default
- `vendno2` (Send Check To Vendor #) — Print Other Vendor Address on Check. Can be CHAR(24) if using xref.; Valid values/xref: APSV
- `arcustno` (Their Cust #) — ARSC Customer Number in SX.e. Can be CHAR(24) if using Xref; Valid values/xref: ARSC
- `proctype` (Proc Type) — Defaults in AP Entry; Valid values/xref: (E)xpense,(T)rade,(A)ddon; Default: E
- `invtype` (Invoice Type) — Defaults during APET
- `paymethod` (Payment Method) — (S)tandard payment proces or (R)emittance/BACS Available starting 10.2.0; Valid values/xref: S or R; Default: S
- `langcd` (LanguageCode) — Valid values/xref: SASTT-Y
- `bankno` (Bank #) — Valid values/xref: CRSB; Default: DCAOV Default
- `divno` (Division #) — Only used if Full Div.; Valid values/xref: SASTT-V Can be CHAR(24) if using xref
- `vendtype` (Vendor Type) — Used for Check Runs; Valid values/xref: SASTT - VT
- `apvendcls` (Class) — Use APAV to Rank; Valid values/xref: Must be 1-13 2 digits
- `synccrmfl` (Sync to CRM) — Available Starting 4.1; Valid values/xref: Y or N; Default: Y
- `currencyty` (Currency) — Valid values/xref: SASTC
- `exclecomm` (Exclude in Esales) — Available Starting 4.1; Valid values/xref: Y or N; Default: N
- `exclmdd` (Exclude in MDD) — Available Starting 5.0; Valid values/xref: Y or N; Default: N
- `shipviaty` (Ship Via) — Defaults on PO entry. Can be CHAR(24) if using xref; Valid values/xref: SASTT - S
- `orderdisp` (Disposition) — Defaults on PO entry; Valid values/xref: (S)hip Complete, (T)ag and Hold, (W)ill Call or Blank
- `nopocopies` (PO Copies) — Valid values/xref: 1 digit; Default: 1
- `coreprice` (Core Price) — Used with the CORES Module. Available Starting 3.2; Valid values/xref: (B)oth,(C)ombine,(N)one; Default: B
- `frttermscd` (Freight Terms Code) — Available Starting 10.0; Valid values/xref: SASTT - FT
- `transferloc` (Transfer Location) — Available Starting 10.0
- `limitshipvia` (Limit Ship Via) — Available Starting 10.3 Setup Shipvias in APSD after conversion; Valid values/xref: Y or N; Default: N
- `bofl` (Back Orders OK) — Valid values/xref: Y or N; Default: Y
- `subfl` (Substitutes OK) — Valid values/xref: Y or N; Default: Y
- `resalefl` (Resale) — Valid values/xref: Y or N; Default: Y
- `fobfl` (Free on Board) — Valid values/xref: Y or N; Default: N
- `salesmgrfl` (Update Sales Mgr) — Valid values/xref: Y or N; Default: Y
- `apholdfl` (Hold AP Invoice) — Valid values/xref: Y or N; Default: N
- `freightexpectedty` (Freight Expected Type) — Available Starting 6.1; Valid values/xref: Y or N; Default: Y
- `centbuyfl` (Central Buy Method) — Valid values/xref: Y (Blanket) or N (Transfer); Default: Y
- `intratodcd` (Intrastat Terms of Delivery code) — Used with VAT only. Required if country setup to report intrastat in SASTT Country setup Availabel starting 6.1.080; Valid values/xref: SASTT-TD
- `grossnetfl` (Terms Disc On) — Valid values/xref: Y (Gross) or N (Net); Default: N
- `incladdonsfl` (Include Addons in Terms Disc (Net Only)) — Available Starting 6.1.080; Valid values/xref: Y or N; Default: N
- `wodiscpct` (Order Discount) — Can be Amount or Percentage
- `wodisctype` (Type $ for Amount or % for Percentage) — Determines what previous field is; Valid values/xref: $ or %; Default: %
- `rebatemultiplier` (Rebate Multiplier) — Used to compute Cap Sell Amount on Share Rebates Available starting 10.3.1; Valid values/xref: (B)ase price, (L)ist price or (C)ost used for pricing; Default: B
- `wlasncreate` (Create TWL ASN) — Available Starting 4.2; Valid values/xref: Y or N; Default: N
- `wlasnautorcvfl` (WL Auto Rcv ASN) — Within TWL, Allow Auto Receiving of ASNs for this Vendor Available Starting 6.1.040; Valid values/xref: Y or N; Default: N
- `wlblockpofl` (Block POs) — Block PO's from TWL - Using ASN (stops duplicate POs) Available starting 6.1.040; Valid values/xref: Y or N; Default: N
- `addonno1` (Expensed) — Default in PO/AP Entry; Valid values/xref: SASTT-X
- `addonamt1` (Type $ for Amount or % for Percentage) — Added in 6.0 version
- `addontype1` (Type) — Added in 6.0 version; Valid values/xref: $ or %; Default: %
- `addonno2` (Expensed) — Default in PO/AP Entry; Valid values/xref: SASTT-X
- `addonamt2` (Amount) — Added in 6.0 version
- `addontype2` (Type $ for Amount or % for Percentage) — Added in 6.0 version; Valid values/xref: $ or %; Default: %
- `capaddonno1` (Capitalized) — Default in PO/AP Entry; Valid values/xref: SASTT-X
- `capaddonamt1` (Amount) — Default in PO/AP Entry
- `capaddontype1` (Type $ for Amount or % for Percentage) — Default in PO/AP Entry; Valid values/xref: $ or %; Default: %
- `capaddonno2` (Capitalized) — Default in PO/AP Entry; Valid values/xref: SASTT-X
- `capaddonamt2` (Amount) — Default in PO/AP Entry
- `capaddontype2` (Type $ for Amount or % for Percentage) — Default in PO/AP Entry; Valid values/xref: $ or %; Default: %
- `capaddonno3` (Capitalized) — Default in PO/AP Entry; Valid values/xref: SASTT-X
- `capaddonamt3` (Amount) — Default in PO/AP Entry
- `capaddontype3` (Type $ for Amount or % for Percentage) — Default in PO/AP Entry; Valid values/xref: $ or %; Default: %
- `capaddonno4` (Capitalized) — Default in PO/AP Entry; Valid values/xref: SASTT-X
- `capaddonamt4` (Amount) — Default in PO/AP Entry
- `capaddontype4` (Type $ for Amount or % for Percentage) — Default in PO/AP Entry; Valid values/xref: $ or %; Default: %
- `dirpoaddonfl` (Direct PO Addon Flag) — (Y)es to use default direct PO addons (N) to use only one set of defaults for all Pos Available Starting 10.0; Valid values/xref: Yor N; Default: N
- `diraddonno1` (Direct Expensed PO Addon) — Available Starting 10.0; Valid values/xref: SASTT-X
- `diraddonamt1` (Type $ for Amount or % for Percentage) — Available Starting 10.0
- `diraddontype1` (Type) — Available Starting 10.0; Valid values/xref: $ or %; Default: %
- `diraddonno2` (Direct Expensed PO Addon) — Available Starting 10.0; Valid values/xref: SASTT-X
- `diraddonamt2` (Amount) — Available Starting 10.0
- `diraddontype2` (Type $ for Amount or % for Percentage) — Available Starting 10.0; Valid values/xref: $ or %; Default: %
- `dircapaddonno1` (Direct Capitalized PO Addon) — Available Starting 10.0; Valid values/xref: SASTT-X
- `dircapaddonamt1` (Amount) — Available Starting 10.0
- `dircapaddontype1` (Type $ for Amount or % for Percentage) — Available Starting 10.0; Valid values/xref: $ or %; Default: %
- `dircapaddonno2` (Direct Capitalized PO Addon) — Available Starting 10.0; Valid values/xref: SASTT-X
- `dircapaddonamt2` (Amount) — Available Starting 10.0
- `dircapaddontype2` (Type $ for Amount or % for Percentage) — Available Starting 10.0; Valid values/xref: $ or %; Default: %
- `dircapaddonno3` (Direct Capitalized PO Addon) — Available Starting 10.0; Valid values/xref: SASTT-X
- `dircapaddonamt3` (Amount) — Available Starting 10.0
- `dircapaddontype3` (Type $ for Amount or % for Percentage) — Available Starting 10.0; Valid values/xref: $ or %; Default: %
- `dircapaddonno4` (Direct Capitalized PO Addon) — Available Starting 10.0; Valid values/xref: SASTT-X
- `dircapaddonamt4` (Amount) — Available Starting 10.0
- `dircapaddontype4` (Type $ for Amount or % for Percentage) — Available Starting 10.0; Valid values/xref: $ or %; Default: %
- `gldivno4` (Expense - Div) — Default Expense GL; Valid values/xref: GLSA
- `gldeptno4` (Expense - Dept) — Default Expense GL; Valid values/xref: GLSA
- `glacctno4` (Expense - Acct. Old Account # if Using Xref) — Default Expense GL. May be CHAR(20) if using xref.; Valid values/xref: GLSA
- `glsubno4` (Expense - Sub) — Default Expense GL; Valid values/xref: GLSA
- `fed1099no` (1099 Style) — 6 for MISC 1099
- `fedtaxid` (Tax ID #) — SUT- FEIN Federal ID # GST - Registration # VAT - Registration #; Valid values/xref: GST and VAT require Reg # if GST Type is Registered
- `ap1099nm` (1099 Name) — Alternate name to print on 1099
- `ap1099nmctrl` (1099 Name Control) — 1099 Name Control Per IRS Guidelines Available Starting 6.1.080
- `gststatus` (GST Status) — Use for GST and VAT taxing methods (Y) Taxable or (N) Nontaxable; Valid values/xref: Y or N; Default: Y
- `gsttype` (GST Type) — Use for GST and VAT taxing methods (R)egistered, (U)nregistered or (F)oreign Entity; Valid values/xref: R, U or F; Default: R
- `statecd` (Taxing State) — Use for VAT Only Available starting 6.1.080; Valid values/xref: SASGV-gui / SASGS-chui & table name
- `addvatsettfl` (Add VAT to Settlement) — Use for VAT Only Available starting 6.1.080; Valid values/xref: Y or N; Default: N
- `epotype` (Purchase Orders) — Default Method; Valid values/xref: (F)ax, (E)di, (X)ML, E(M)ail, (I)ON or Blank
- `equotetype` (Quotes) — Default Method; Valid values/xref: (F)ax, (E)di, (X)ML, E(M)ail or Blank
- `erebtype` (Rebates) — Default Method; Valid values/xref: (E)di, (X)ml, (I)on or Blank
- `epmttype` (Payments) — Default Method; Valid values/xref: (E)di or Blank
- `Webpage` (Web Page) — Enter complete URL
- `Webpageext` (Web Page External) — Enter complete URL
- `edipover` (PO Version) — Valid values/xref: ANSI Version
- `edi846ver` (Inv Adv. Version) — Valid values/xref: ANSI Version
- `updtprice` (Update Price) — Valid values/xref: Y or N; Default: N
- `vendbankacctname` (Vendor's Bank Account Name) — Used for BACS Processing Available Starting 10.2.0
- `vendbanksortcode` (Vendor's Bank Sort Code) — Used for BACS Processing Available Starting 10.2.0
- `ecommercety` (Comm Type) — Available Starting 4.0; Valid values/xref: "eBuy" or blank
- `vendbankaccttype` ((C)urrent Account or (D)eposit Account) — Used for BACS Processing Available Starting 10.2.0; Valid values/xref: C or D; Default: C
- `bacsref` (BACS Reference for Remittance / Vendor Bank Statement) — Used for BACS Processing Available Starting 10.2.0
- `edi845netfmty` (Net Rebate Based From) — Available Starting 5.5 EDI 845 Defaults; Valid values/xref: See Chart Below
- `edi845netdwnto` (Net Rebate Down To) — Available Starting 5.5 EDI 845 Defaults; Valid values/xref: See Chart Below
- `edi845pcttoty` (Percent Rebate Based On) — Available Starting 5.5 EDI 845 Defaults; Valid values/xref: See Chart Below
- `aoqtytolamt` (Line Quantity Units) — Tolerances for APEI
- `apqtytolpct` (Line Qty Percent) — Tolerances for APEI
- `aplntolamt` (Line Amount) — Tolerances for APEI
- `aplntolpct` (Line Percent) — Tolerances for APEI
- `apinvtolamt` (Invoice Amount) — Tolerances for APEI
- `apinvtolpct` (Invoice Percent) — Tolerances for APEI
- `apvendtolfl` (Use Vendor Tolerances?) — Must be Yes to Use above values; Valid values/xref: Y or N; Default: N
- `user5` (user5) — Used for Conversion Import ID
- `user10` (user10) — Available Starting 5.5
- `user11` (user11) — Available Starting 5.5
- `user12` (user12) — Available Starting 5.5
- `user13` (user13) — Available Starting 5.5
- `user14` (user14) — Available Starting 5.5
- `user15` (user15) — Available Starting 5.5
- `user16` (user16) — Available Starting 5.5
- `user17` (user17) — Available Starting 5.5
- `user18` (user18) — Available Starting 5.5
- `user19` (user19) — Available Starting 5.5
- `user20` (user20) — Available Starting 5.5
- `user21` (user21) — Available Starting 5.5
- `user22` (user22) — Available Starting 5.5
- `user23` (user23) — Available Starting 5.5
- `user24` (user24) — Available Starting 5.5
- `supaccessfl` (Supplier Access Available) — Available Starting in 6.1.060; Valid values/xref: Y or N; Default: N
- `supaccessprodidty` (Supplier Access Product ID Type) — UP (UPC), BP (Buyer Prod), MG (Alt Prod) or MP (Mfg Prod) Available Starting in 6.1.060; Valid values/xref: UP, BP, MG, MP; Default: UP
- `supaccesscommty` (Supplier Access Comm Type) — HTTP or FTP Available Starting in 6.1.060; Valid values/xref: HTTP or FTP; Default: HTTP
- `supaccesshttpurl` (Supplier Access HTTP URL) — Available Starting in 6.1.060 Length 80 prior to 6.1.080
- `supaccesshttpuserid` (Supplier Access HTTP User ID) — Available Starting in 6.1.060
- `supaccesshttppasswd` (Supplier Access HTTP Password) — Available Starting in 6.1.060
- `supaccessftpaddr` (Supplier Access FTP IP Addr) — Available Starting in 6.1.060 Length 80 prior to 6.1.080
- `supaccessftpuserid` (Supplier Access FTP User ID) — Available Starting in 6.1.060
- `supaccessftppasswd` (Supplier Access FTP Password) — Available Starting in 6.1.060
- `supaccessftsyscode` (Supplier Access FTP Sys Code) — Available Starting in 6.1.060
- `esb855ivmipotypefl` (Create VMI Orders as Purchase Orders) — Available Starting in 11.18.8; Valid values/xref: Y or N; Default: N
- `esb855isetnotesprintfl` (Set Print Status for Notes) — Available Starting in 11.18.8; Valid values/xref: Y or N; Default: N
- `edi867ty` (Product Transfer/Resale (EDI 867)) — Available Starting in 11.18.8
- `allowpofl` (Allow PO Flag) — Available Starting in 11.18.9; Valid values/xref: Y or N; Default: Y
- `edi852usestatusfl` (EDI 852 Use Status Flag) — Available Starting in 11.18.9; Valid values/xref: Y or N; Default: N
- `restricteditfl` (Restricted Editing) — Available Starting in 11.19.6; Valid values/xref: Y or N; Default: N
- `suppwarrallowpct` (Supplier Warranty Allowance {ercemt) — Available Starting in 11.19.9
- `edi820email` (EDI 820 Email) — Available Starting in 11.19.11
- `repricepct` (Auto Vendor Reprice Percent) — Available Starting in 11.20.2
- `rentexpty` (Rental Invoice Source) — Available Starting in 11.21.1; Valid values/xref: P or R; Default: P
- `allowgenericprodrebfl` (Generic Prod Reb) — Available Starting in 11.21.2; Valid values/xref: Y or N; Default: N
- `esb855ivmicontractfl` (855 VMI Contract) — Available Starting in 11.21.5; Valid values/xref: Y or N; Default: N
- `onechkperinvfl` (One Check Per invoice) — Available starting in 11.21.10; Valid values/xref: Y or N; Default: N

### `araos`
**Accounts Receivable Other Service Charges**
Fields: `cono` (inte) [i], `recty` (char) [i], `custno` (deci-0) [im], `shipto` (char) [im], `state` (char) [i], `arscpct` (deci-2[4]), `arscpc2` (deci-2[4]), `arscbal` (deci-2[4]), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `groupid` (char) [i]

### `arbcb`
**Lockbox Batch Header**
Fields: `cono` (inte) [im], `batch` (char) [i], `recvdt` (date), `chkcnt` (inte), `amount` (deci-2), `rtpfl` (logi) [m], `transmission` (char) [i], `operinit` (char), `adddata1` (char), `adddata2` (char), `adddata3` (char), `adddata4` (char), `adddata5` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `recvdttz` (datetm-tz)

### `arbch`
**Lockbox Check Header**
Fields: `cono` (inte) [im], `custno` (deci-0) [im], `checkno` (inte) [im], `checkamt` (deci-2), `checkseq` (inte) [im], `recvdt` (date) [i], `batch` (char) [i], `statfl` (logi) [m], `badcustfl` (logi) [m], `autopostfl` (logi) [m], `adddata1` (char), `adddata2` (char), `adddata3` (char), `adddata4` (char), `adddata5` (char), `operinit` (char), `transdt` (date), `transmission` (char) [i], `transtm` (char), `transproc` (char), `lbxpostty` (char) [m], `xxc3` (char), `pymttranscd` (char), `pymttransno` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `lockboxno` (char), `recvdttz` (datetm-tz), `paymentrefer` (char)

### `arbcl`
**Lockbox Detail**
Fields: `cono` (inte) [im], `batch` (char) [i], `custno` (deci-0) [im], `checkno` (inte) [im], `lbxinvno` (char), `lbxamt` (deci-2), `aretid` (reci) [i], `invno` (inte) [i], `invsuf` (inte) [i], `seqno` (inte) [i], `invamt` (deci-2), `duedt` (date), `trancd` (char) [i], `piffl` (logi) [m], `applyamt` (deci-2), `discamt` (deci-2), `invcustno` (deci-0), `aretnffl` (logi) [m], `statfl` (logi) [m], `refer` (char), `prefix` (inte), `cbinvno` (inte), `adddata1` (char), `adddata2` (char), `adddata3` (char), `adddata4` (char), `adddata5` (char), `adddata6` (char), `adddata7` (char), `adddata8` (char), `adddata9` (char), `adddata10` (char), `operinit` (char), `autopostfl` (logi) [m], `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `duedttz` (datetm-tz), `paymentrefer` (char)

### `arbclw`
**Lock Box Write Off File**
Fields: `cono` (inte) [i], `batch` (char) [i], `custno` (deci-0) [i], `checkno` (inte) [i], `invno` (inte) [i], `invsuf` (inte) [i], `seqno` (inte) [i], `amt` (deci-2), `notesfl` (char), `lookupnm` (char), `arettid` (reci), `rid` (reci), `taxno` (inte), `adddata1` (char), `adddata2` (char), `adddata3` (char), `adddata4` (char), `adddata5` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `origamt` (deci-2), `origtaxamt` (deci-2), `adjbaseamt` (deci-2), `taxexemptamt` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `paymentrefer` (char)

### `arbct`
**Lockbox Transmission History**
Fields: `cono` (inte) [im], `transmission` (char) [i], `adddata1` (char), `adddata2` (char), `adddata3` (char), `adddata4` (char), `adddata5` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `arbsi`
**AR LockBox Setup Import**
Fields: `imptype` (char) [i], `lbxdelim` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `arbsid`
**AR LockBox Setup Import Detail**
Fields: `imptype` (char) [i], `recno` (inte) [i], `reckey` (char), `startpos` (inte[20]), `endpos` (inte[20]), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `arebt`
**AR Batch Entry**
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `invno` (inte) [i], `invsuf` (inte) [i], `amount` (deci-2), `discamt` (deci-2), `transcd` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `seqno` (inte) [i], `setno` (inte) [i], `invdt` (date), `duedt` (date), `discdt` (date), `refer` (char), `disputefl` (logi) [m], `termstype` (char) [m], `batchnm` (char) [i], `duedays` (inte), `discdays` (inte), `addon` (deci-2[2]), `nopays` (inte), `freqdays` (inte), `discpct` (deci-5), `divno` (inte), `shipto` (char) [m], `maxpost` (inte), `nopost` (inte), `slsytdfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `discdttz` (datetm-tz), `duedttz` (datetm-tz), `invdttz` (datetm-tz)

### `aret`
**AR Transactions**
*AR transactions — invoices, credits, and payments. Core receivables ledger.*
**Operators call this:** "Company" (Accounts Receivable), "Customer" (Accounts Receivable), "Transaction Type" (Accounts Receivable), "Dispute Flag" (Accounts Receivable), "Original Amount" (Accounts Receivable), "Payment Received" (Accounts Receivable), "Discount Given" (Accounts Receivable), "Write-Off / Paid-in-Full Adjustment" (Accounts Receivable), "Invoice Number" (Accounts Receivable), "Invoice Suffix" (Accounts Receivable), "Source Code" (Accounts Receivable), "Operator (Last Changed By)" (Accounts Receivable), "Reference" (Accounts Receivable), "Journal Number" (Accounts Receivable), "Set Number" (Accounts Receivable), "Invoice Date" (Accounts Receivable), "Due Date" (Accounts Receivable), "Payment Date" (Accounts Receivable), "Transaction Type Name" (Accounts Receivable)
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `statustype` (logi) [im], `invno` (inte) [i], `invsuf` (inte) [i], `amount` (deci-2), `discamt` (deci-2), `transcd` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `seqno` (inte) [i], `jrnlno` (inte) [i], `setno` (inte) [i], `invdt` (date) [i], `duedt` (date) [i], `discdt` (date), `pifamt` (deci-2), `paymtamt` (deci-2), `paymtdt` (date), `paymtcd` (inte), `nextseqno` (inte), `period` (inte), `refer` (char), `percal` (inte), `perfisc` (inte), `disputefl` (logi) [m], `termstype` (char) [m], `sourcecd` (inte) [i], `jrnlamt` (deci-2), `origseqno` (inte), `divno` (inte), `module` (char), `shipto` (char) [m], `checkno` (deci-0), `crjrnlno` (inte) [i], `crsetno` (inte) [i], `stmtfl` (logi[2]) [m], `codcollamt` (deci-2) [m], `postdt` (date), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `urecno` (deci-0) [i], `notesfl` (char), `salesexrate` (deci-7), `exchgrate` (deci-7[2]), `arexrate` (deci-7), `checknopaid` (deci-0), `sxextractdt` (date), `slsytdfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `addonamt` (deci-2[4]), `appinvdt` (date), `appinvno` (inte), `appinvsuf` (inte), `apptranscd` (inte), `origdisc` (deci-2), `location` (char) [i], `transproc` (char), `nostmts` (inte), `lbxautofl` (logi) [m], `pymttranscd` (char), `pymttransno` (char), `wordindexfl` (logi) [m], `rowpointer` (char) [i], `termsdisconpst` (deci-2), `revalno` (inte), `transdttmz` (datetm-tz) [i], `appinvdttz` (datetm-tz), `discdttz` (datetm-tz), `duedttz` (datetm-tz), `invdttz` (datetm-tz), `paymtdttz` (datetm-tz), `postdttz` (datetm-tz), `sxextractdttz` (datetm-tz), `percaltz` (datetm-tz), `perfisctz` (datetm-tz), `payrowpointer` (char), `reversedfl` (logi) [m], `paymentrefer` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `Custno` (Customer) — Can be CHAR(24) if using the Xref.; Valid values/xref: ARSC; Required
- `Shipto` (Ship To) — Valid values/xref: ARSS
- `Transcd` (Transaction Code) — See Chart Below; Valid values/xref: (IN)voice, (FC)Finance Charge, (MC)Misc Credit, (AJ)Adjustment, (CM)Credit Memo, (CK)Check; Required
- `Invsuf` (Suffix) — See Notes Below; Default: Entered Value
- `Amount` (Amount) — In customer's currency; Required
- `Discdt` (Discount Date) — Set to Due Date if N/A; Default: Calculated from Terms
- `Disputefl` (Dispute Flag) — Valid values/xref: (Y)es or (N)o; Default: N
- `Paymtdt` (Payment Date) — Only used on CK and CM Records
- `Discamt` (Discount Taken) — See Notes Below
- `Checkno` (Check #) — Only used in CK Records
- `Termstype` (Terms) — Can be CHAR(24) if using the Xref.; Valid values/xref: SASTT-T; Default: ARSC
- `Divno` (Division) — Can be CHAR(24) if using the Xref.; Valid values/xref: SASTT-V; Default: Entered Value
- `arexrate` (A/R Exchange Rate) — Customer must be setup for foreign currency. Exchange rate for payment; Default: 1
- `salesexrate` (SalesExchange Rate) — Customer must be setup for foreign currency. Exchange rate for invoice; Default: 1
- `user5` (user5) — Used for Conversion Import ID

### `aretp`
**AR Payment Transaction**
*AR payment transactions detail.*
Fields: `cono` (inte) [i], `checkno` (deci-0) [i], `rowpointer` (char) [i], `arscrowpointer` (char) [i], `debittransfl` (logi) [m], `divno` (inte), `jrnlno` (inte), `setno` (inte), `paymtamt` (deci-2), `pymttranscd` (char) [i], `postdttz` (datetm-tz) [i], `reasoncd` (inte), `revdesc` (char), `reversedfl` (logi) [m], `splitfl` (logi) [m], `taxoverfl` (logi) [m], `ucpartusedfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `transno` (inte), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz), `paymentrefer` (char)

### `arett`
**Sales Tax Transaction Audit File**
Fields: `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `recty` (inte) [i], `taxgroup` (inte) [i], `statecd` (char) [i], `countycd` (char) [i], `citycd` (char) [i], `othercd` (char) [i], `taxexemptamt` (deci-2), `taxexemptcd` (char) [i], `taxsalert` (deci-5), `taxsalebase` (deci-2), `taxsaleamt` (deci-2), `taxsaleadj` (deci-2), `taxusert` (deci-5), `taxusebase` (deci-2), `taxuseamt` (deci-2), `taxuseadj` (deci-2), `taxtransrt` (deci-5), `taxtransbase` (deci-2), `taxtransamt` (deci-2), `taxtransadj` (deci-2), `taxexcrt` (deci-5), `taxexcbase` (deci-2), `taxexcamt` (deci-2), `taxexcadj` (deci-2), `taxactcd` (char), `taxovercd` (char), `taxadjcd` (char), `invdt` (date) [i], `paiddt` (date) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `divno` (inte), `transtype` (char) [m], `custno` (deci-0) [m], `whse` (char) [m], `addonno` (inte[10]), `addonnet` (deci-2[10]), `transproc` (char), `taxexcadjbase` (deci-2), `taxsaleadjbase` (deci-2), `taxtransadjbase` (deci-2), `taxuseadjbase` (deci-2), `taxexcexempt` (deci-2), `taxsaleexempt` (deci-2), `taxtransexempt` (deci-2), `taxuseexempt` (deci-2), `transdttmz` (datetm-tz) [i], `invdttz` (datetm-tz), `paiddttz` (datetm-tz), `rowpointer` (char) [i]

### `arlspi`
**AR lsp Payment Record**
Fields: `cono` (inte) [im], `referno` (char) [im], `custno` (deci-0), `invno` (inte) [im], `paymtamt` (deci-2), `remainamt` (deci-2), `operinit` (char), `transdttmz` (datetm-tz), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `arlspp`
**AR lsp Payment Record**
Fields: `cono` (inte) [im], `referno` (char) [im], `jrnlno` (inte) [i], `statusfl` (logi) [im], `checkno` (inte), `custno` (deci-0) [i], `user1` (char), `paymtdttmz` (datetm-tz) [i], `paymtamt` (deci-2), `lspdatestampdttmz` (datetm-tz), `lspcertno` (char), `lsprfcprov` (char), `lspuuid` (char), `lspgovid` (char), `operinit` (char), `transdttmz` (datetm-tz), `transproc` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `arsa`
**Accounts Receivable COD Addon**
Fields: `custno` (deci-0) [im], `amount` (deci-2), `percent` (deci-2), `todate` (deci-2), `maxcharge` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `cono` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `rowpointer` (char) [i]

### `arsb`
**AR Billing - replaces pmsb**
*AR billing setup per customer — invoice delivery preferences.*
Fields: `cono` (inte) [im], `billingtype` (char) [im], `billingprimarykey` (char) [im], `billingsecondarykey` (char) [im], `chargefrght` (logi) [m], `flatordamt` (deci-2), `flatpkgamt` (deci-2), `freightpct` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `chargebofl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `arsc`
**Customer Master**
*PRIMARY customer master. Use for customer lookups, credit limits, pricing type, terms, sales rep assignments, and customer status. Core table for any customer-facing query.*
**Operators call this:** "Customer Code" (Accounts Receivable), "Customer Name" (Accounts Receivable), "Customer Type" (Accounts Receivable), "Customer Price Type" (Accounts Receivable), "Outside Sales Rep" (Accounts Receivable), "Inside Sales Rep" (Accounts Receivable), "AR Group" (Accounts Receivable), "Address Line 1" (Accounts Receivable), "Address Line 2" (Accounts Receivable), "Address Line 3" (Accounts Receivable), "City" (Accounts Receivable), "State" (Accounts Receivable), "Postal Code" (Accounts Receivable), "Phone" (Accounts Receivable), "Fax" (Accounts Receivable), "Email" (Accounts Receivable), "Payment Terms" (Accounts Receivable), "Sales Territory" (Accounts Receivable), "Credit Limit" (Accounts Receivable), "Account Status" (Accounts Receivable), "Last Payment Date" (Accounts Receivable), "Last Sale Date" (Accounts Receivable), "Average Days to Pay" (Accounts Receivable), "Credit Manager" (Accounts Receivable), "Customer Code" (Sales), "Customer Name" (Sales), "Customer Type" (Sales), "Customer Price Type" (Sales), "Customer Outside Rep" (Sales), "Customer Inside Rep" (Sales), "Address Line 1" (Sales), "Address Line 2" (Sales), "Address Line 3" (Sales), "City" (Sales), "State" (Sales), "Postal Code" (Sales), "Phone" (Sales), "Fax" (Sales), "Email" (Sales), "Sales Territory" (Sales), "Credit Limit" (Sales), "Account Status" (Sales), "Last Payment Date" (Sales), "Last Sale Date" (Sales), "Average Days to Pay" (Sales), "Credit Manager" (Sales)
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `name` (char) [m], `addr` (char[2]), `city` (char) [i], `state` (char) [i], `zipcd` (char) [i], `lookupnm` (char) [i], `phoneno` (char) [i], `faxphoneno` (char), `pophoneno` (char), `pocontctnm` (char), `comment` (char), `statustype` (logi) [m], `siccd` (inte[3]), `termstype` (char) [m], `servchgfl` (logi) [m], `custtype` (char), `dunningfl` (logi) [m], `unearnedfl` (logi) [m], `salesterr` (char), `class` (inte), `cyclecd` (char), `salesmgrfl` (logi) [m], `divno` (inte), `bankno` (inte), `operinit` (char), `transdt` (date), `transtm` (char), `custno2` (deci-0) [i], `enterdt` (date), `minord` (deci-0), `maxord` (deci-0), `route` (char), `uncashbal` (deci-2), `pickprno` (inte), `noinvcopy` (inte), `rebatety` (char), `bofl` (logi) [m], `countrycd` (char), `subfl` (logi) [m], `edichgcd` (char), `taxcert` (char), `ediordcd` (char), `shipinstr` (char), `eproptype` (char), `shipviaty` (char), `ardatcty` (char), `whse` (char), `slsrepin` (char), `slsrepout` (char), `shipreqfl` (logi) [m], `poreqfl` (logi) [m], `orderdisp` (char), `synccrmfl` (logi) [m], `pricetype` (char), `pricecd` (inte), `disccd` (inte), `user3` (char), `user4` (char), `wodisccd` (inte), `user5` (char), `statecd` (char), `user6` (deci-5), `taxauth` (char), `user7` (deci-5), `taxablety` (char), `user8` (date), `user9` (date), `nontaxtype` (char), `inbndfrtfl` (logi) [m], `outbndfrtfl` (logi) [m], `creditmgr` (char) [i], `crestdt` (date), `lastrevdt` (date), `nextrevdt` (date), `credlim` (deci-0), `holdpercd` (inte), `selltype` (char), `statusdt` (date), `apmgr` (char), `apphoneno` (char), `banknm` (char), `bankmgr` (char), `bankphoneno` (char), `bankacct` (char), `lastpayamt` (deci-2), `lastpaydt` (date), `pastduedt` (date), `nopastdue` (inte), `avgpaydays` (inte), `nopay` (inte), `noinv` (inte), `dunsno` (char), `lastrtg` (char[2]), `lastrtgdt` (date[2]), `crsname` (char), `crref` (char[2]), `securfl` (logi) [m], `periodbal` (deci-2[5]), `servchgbal` (deci-2), `futinvbal` (deci-2), `salesytd` (deci-2), `costytd` (deci-2), `returnsytd` (deci-2), `codbal` (deci-2), `futbal` (deci-2), `ordbal` (deci-2), `laststmtbal` (deci-2), `prstmtbal` (deci-2), `servchgytd` (deci-2), `discytd` (deci-2), `unearnedytd` (deci-2), `lastagedt` (date), `custprodfl` (logi) [m], `lastsaledt` (date), `laststmtdt` (date), `notesfl` (char), `cashrecfl` (logi) [m], `cashreqfl` (logi) [m], `rebatesdue` (deci-2), `rebatesytd` (deci-2), `ccno` (char), `ccexp` (char), `mediacd` (inte), `shipto` (char) [m], `gldivno` (inte[4]), `gldeptno` (inte[4]), `glacctno` (inte[4]), `glsubno` (inte[4]), `misccrbal` (deci-2), `pickprtfl` (logi) [m], `downpayamt` (deci-2), `addonno` (inte[4]), `custpo` (char), `eacktype` (char), `einvtype` (char), `estmttype` (char), `edipartner` (char) [i], `langcd` (char), `gstcert` (char), `gstreg` (char), `statementty` (char), `user1` (char), `user2` (char), `easngrp` (char), `easnto` (char), `edipartaddr` (char), `ediyouraddr` (char), `edictrlno` (inte), `edienvtag` (char[2]), `ediackver` (char), `ediinvver` (char), `edinetwork` (char), `taxdt` (date), `fpcustno` (deci-0), `fpcustfl` (logi) [m], `geocd` (inte), `tendqtyfl` (logi) [m], `taxreg` (char), `highbal` (deci-2), `currencyty` (char), `lastsaleamt` (deci-2), `highsaleamt` (deci-2), `pmcashfl` (logi) [m], `ardatccost` (deci-5), `glacctno2` (inte[4]), `glsubno2` (inte[4]), `gldivno2` (inte[4]), `gldeptno2` (inte[4]), `countycd` (char), `citycd` (char), `other1cd` (char), `other2cd` (char), `shiplbl` (char), `ecommwhse` (char), `spcdefaultty` (char) [m], `webpageext` (char), `webpage` (char), `keyindex` (char), `transproc` (char), `AuthGrpList` (char) [i], `email` (char), `xxc2` (char), `pdcustno` (deci-0), `linetermsfl` (logi) [m], `dealer` (char), `lastsalesytd` (deci-2), `lastcostytd` (deci-2), `lastreturnsytd` (deci-2), `lastservchgytd` (deci-2), `lastdiscytd` (deci-2), `lastunearnedytd` (deci-2), `lastrebatesytd` (deci-2), `ptxtype` (char) [m], `edicatprodfl` (logi) [m], `addonnum` (inte[8]), `ptxarfl` (logi) [m], `edinsprodfl` (logi) [m], `ptxapfl` (logi) [m], `ediprintnotesfl` (logi) [m], `ptxtransbillfl` (logi) [m], `edijitfl` (logi) [m], `editermsfl` (logi) [m], `ediprcfl` (logi) [m], `edi840fl` (logi) [m], `weightty` (char), `lbxpostty` (char) [m], `xxc15` (char), `addr3` (char), `swexaddfl` (logi[4]) [m], `custperiodbal` (deci-2[5]), `consolinvty` (char), `custcodbal` (deci-2), `custordbal` (deci-2), `custfutinvbal` (deci-2), `custmisccrbal` (deci-2), `custservchgbal` (deci-2), `custuncashbal` (deci-2), `consolterms` (char), `consolformat` (char), `consolinterval` (char), `nextconsoldt` (date), `lastconsoldt` (date), `syncmddfl` (logi) [m], `mastercono` (inte) [i], `mastercustno` (deci-0) [im], `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `basisavgpaydays` (inte), `basisnopay` (inte), `basisbegdt` (date), `basisenddt` (date), `srallownegoverfl` (logi) [m], `groupid` (char) [i], `rowpointer` (char) [i], `wordindexfl` (logi) [m], `intratodcd` (inte), `outofcityfl` (logi) [m], `vattype` (char), `usesettcalcfl` (logi) [m], `settdisctype` (char), `vatvariablefl` (logi) [m], `picklabelsize` (char), `strategicacct` (char), `picklabelprefix` (char), `balintdatetm` (char), `dnbireqcredlim` (deci-0), `dnbiscorecard` (deci-2), `dnbiriskcode` (char), `dnbiapplstatus` (char), `dnbiparentdunsno` (char), `dnbidomesticdunsno` (char), `dnbiglobaldunsno` (char), `dnbiname` (char), `dnbiaddress` (char), `dnbicity` (char), `dnbistate` (char), `dnbizipcd` (char), `dnbicountry` (char), `dnbiphoneno` (char), `dnbiexpiredate` (date), `dnbiresponse` (char), `dnbinocallfl` (logi) [m], `dnbiapplid` (char), `billdirectaddon` (char), `dnbirecomcredlim` (deci-0), `frttermscd` (char), `transferloc` (char), `esbactioncode` (char), `esbbalintvarid` (char), `extshipinstr` (char), `dlvprintty` (char), `ccblockfl` (logi), `glprtdetail` (char), `mincredchk` (deci-2), `servicevendno` (deci-0), `transdttmz` (datetm-tz) [i], `allowfulfillmentty` (char), `npclaimacctfl` (logi) [m], `npclaimnoprefix` (char), `npclaimnobegin` (inte), `npclaimnoend` (inte), `npclaimnonext` (inte), `npretclaimnoprefix` (char), `npretclaimnobegin` (inte), `npretclaimnoend` (inte), `npretclaimnonext` (inte), `custprodreqfl` (logi) [m], `sigreqtype` (char), `easntype` (char), `restricteditfl` (logi) [m], `createdby` (char), `createddt` (date), `createdtm` (char), `createdproc` (char), `sortcode` (char), `basisbegdttz` (datetm-tz), `createddttz` (datetm-tz), `crestdttz` (datetm-tz), `dnbiexpiredatetz` (datetm-tz), `enterdttz` (datetm-tz), `lastagedttz` (datetm-tz), `lastconsoldttz` (datetm-tz), `lastpaydttz` (datetm-tz), `lastrevdttz` (datetm-tz), `lastsaledttz` (datetm-tz), `laststmtdttz` (datetm-tz), `nextconsoldttz` (datetm-tz), `nextrevdttz` (datetm-tz), `pastduedttz` (datetm-tz), `statusdttz` (datetm-tz), `taxdttz` (datetm-tz), `lnshipcompfl` (logi) [m], `bolimit` (inte), `lastrtgdttz` (datetm-tz[2), `basisenddttz` (datetm-tz), `nonsf` (inte), `wlscmlblprefix` (char), `wlscmlblmixtxt` (char), `addressoverfl` (logi) [m], `cnconfirmshipty` (char), `cncartonty` (char), `cninvprintty` (char), `cntrackserlotty` (char), `ordrep1` (char), `ordrep2` (char), `ordrep3` (char), `ordrep4` (char), `ordrep5` (char), `orderreppct1` (deci-2), `orderreppct2` (deci-2), `orderreppct3` (deci-2), `orderreppct4` (deci-2), `orderreppct5` (deci-2)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `custno` (Customer #) — Can be CHAR(24) if using the Xref.; Required
- `addr3` (Address) — Available for all companies starting in 6.1.040. Only accessible for Int'l companies in versions 4.2.002 - 6.1.030.
- `city` (City) — Length 20 prior to 6.1.040
- `state` (State) — Not used with Freeform Style Address AO option starting in 6.1.040.
- `geocd` (GEO Code) — Used with TaxWare Only
- `outofcityfl` (Outside City Limit Flag) — Used with TaxWare Enterprise Only Available starting in 6.1.060; Valid values/xref: Y, N; Default: N
- `countrycd` (Country) — Valid values/xref: SASTT-W
- `statustype` (Status) — (A)ctive or (I)nactive; Valid values/xref: A or I; Default: A
- `groupid` (Group) — Group ID. Available starting with 6.1.040.; Valid values/xref: ARSG
- `termstype` (Terms) — Valid values/xref: SASTT-T; Default: DCAOC Default
- `fpcustfl` (Finance Co) — Valid values/xref: Y, N; Default: N
- `statementty` (Stmt Type) — Valid values/xref: (O)pen Item or (N)one; Default: O
- `dunningfl` (Dunning) — Yes means send dunning if appropriate.; Valid values/xref: Y, N; Default: N
- `servchgfl` (Service Chg.) — If set to Y, this customer is subject to service charges; Valid values/xref: Y, N; Default: N
- `custno2` (Send Statements to Customer #) — Can be CHAR(24) if using the Xref.; Valid values/xref: ARSC
- `unearnedfl` (Unearn Disc) — Valid values/xref: Y, N; Default: Y
- `langcd` (Language Code) — Valid values/xref: SASTT-Y
- `bankno` (Bank #) — Default Cash Receipts Bank; Valid values/xref: CRSB; Default: DCAOC Default
- `divno` (Division #) — Required if Full Divisonal. Can be CHAR(24) if using xref.; Valid values/xref: SASTT-V; Default: DCAOC Default
- `currencyty` (Currency Type) — Used for AR Balance in Foreign Currency; Valid values/xref: SASTC
- `class` (Customer Class) — Valid values/xref: 0 thru 13 Only; Default: 0
- `custtype` (Customer Type) — Valid values/xref: SASTT - CU
- `shiplbl` (Shipping Label) — Custom Label Design used with IB
- `synccrmfl` (Sync To CRM) — Available Starting 4.1; Valid values/xref: Y, N; Default: Y
- `syncmddfl` (Synchronize to MDD) — Available Starting 5.1; Valid values/xref: Y, N; Default: Y
- `picklabelsize` (Pick Label Size) — Available Starting 10.0; Valid values/xref: (S)mall or (L)arge; Default: L
- `picklabelprefix` (Pick Label Prefix) — Available Starting 10.0
- `strategicacct` (Strategic Account) — Available Starting 10.0 Only used when ICB Active Interface is turned on in AO.
- `glprtdetail` (Print GL Detail for Tendering) — Available Starting 10.3; Valid values/xref: <Blank>-AO Default, (R)eceipt, (I)nvoice, (N)either, (B)oth
- `consolinvty` (Consolidated Invoice Type) — Available Starting 4.3; Valid values/xref: <Blank>, (C)ustomer, (S)hipto, Cust (P)O, (O)rder; Default: Blank
- `consolterms` (Consolidated InvoiceTerms) — Available Starting 4.3, Required if Consolidating; Valid values/xref: SASTT - T
- `consolformat` (Consolidated Invoice Format) — Available Starting 4.3, Required if Consolidating; Valid values/xref: <Blank>, (O)rder or (P)roduct Sequence
- `consolinterval` (Consolidated Invoice Interval) — Available Starting 4.3, Required if Consolidating; Valid values/xref: <Blank>,DAily,SU,MO,TU,WE,TH,FR,SA,MThly,SMonthly, Day (1-31)
- `lastconsoldt` (Last Consolidation Date) — Available Starting 4.3
- `nextconsoldt` (Next Consolidation Date) — Available Starting 4.3
- `shipviaty` (Ship Via) — Can be CHAR(24) if using the Xref.; Valid values/xref: SASTT-S
- `extshipinstr` (Extended Shipping Instructions) — Valid values/xref: Available Starting 10.1.0.0
- `shipto` (Shipto) — Default Shipto for Order Entry; Valid values/xref: ARSS - Not Validated Since ARSC is Converted Before ARSS
- `slsrepout` (Salesrep Out) — Can be CHAR(24) if using the Xref.; Valid values/xref: SMSN; Default: DCAOC Default
- `slsrepin` (Salesrep In) — Can be CHAR(24) if using the Xref.; Valid values/xref: SMSN; Default: DCAOC Default
- `salesterr` (Territory) — Valid values/xref: SASTT-Z
- `whse` (Default Whse) — Can be CHAR(24) if using the Xref.; Valid values/xref: ICSD
- `dealer` (Core Dealer) — Available Starting 3.2
- `orderdisp` (Disposition) — (S)hip Complete, (T)ag and Hold, (W)ill Call, (J)ust In Time or Blank; Valid values/xref: <Blank>, S, T, W, J; Default: <Blank>
- `noinvcopy` (Invoice Copies) — If set to 0 the customer will not receive any invoices.; Default: 1
- `route` (Route/Day/Stop) — Format 3/2/2
- `frttermscd` (Freight Terms Code) — Available Starting 10.0; Valid values/xref: SASTT - FT
- `transferloc` (Transfer Location) — Available Starting 10.0
- `pickprno` (Pick Priority) — 9 is Highest Priority; Valid values/xref: 0 through 9; Default: 0
- `salesmgrfl` (Sales Manager) — Valid values/xref: Y, N; Default: Y
- `poreqfl` (Require PO #) — Valid values/xref: Y, N; Default: N
- `subfl` (Subs OK) — Valid values/xref: Y, N; Default: Y
- `bofl` (B/O OK) — Valid values/xref: Y, N; Default: Y
- `shipreqfl` (Require Ship To) — Must have ARSS records if set to Yes; Valid values/xref: Y, N; Default: N
- `linetermsfl` (Line Terms) — Payment Terms by Product. Available Starting 3.2; Valid values/xref: Y, N; Default: N
- `weightty` (Weight Type) — Used only for Int'l Companies - in US Blank. Available Starting 4.1; Valid values/xref: (U)S or (M)etric
- `pricetype` (Price Type) — Can be CHAR(24) if using the Xref.; Valid values/xref: SASTT-J
- `rebatety` (Rebate Type) — Valid values/xref: PDST-CT
- `spcdefaultty` (OE SPC Default) — Customer Requires Non-Standard Price Per Unit; Valid values/xref: I-ICSP, O-OE, N=no; Default: I
- `pricecd` (Price Level) — Must be > 0 to use PDSC Pricing; Default: 1
- `wodisccd` (Order Disc Level) — Must be > 0 to use PDSW Pricing
- `disccd` (Line Disc Level) — Must be > 0 to use PDSC Line Discounts
- `minord` (Minimum Order) — Orders < Min go on Hold; Default: 0
- `maxord` (Maximum Order) — Orders > Max go on Hold; Default: 0
- `pdcustno` (PD Customer) — Assign Pricing from this Customer. Can be CHAR(24) if using xref. Available Starting 4.0; Valid values/xref: ARSC
- `pickprtfl` (Print Price on Pick Tickets) — Valid values/xref: Y, N; Default: N
- `srallownegoverfl` (Allow Negative Overages) — Allow Negative Overage Amount on Showroom Quote Print Available starting 6.1.040; Valid values/xref: Y or N; Default: N
- `dlvprintty` (Delivery Print Type) — N & blank - Do Not Print Prices Y - Print Prices D - Print Prices Without Discounts O - Require OE selection Available starting 10.2.0; Valid values/xref: Blank, Y, D, N, O
- `mediacd` (Payment Type) — Default Method of Tendering Payment - Expanded to 2 digits in 6.0; Valid values/xref: SASTT-P
- `ccno` (Credit Card #) — Use SASO Flag to Mask Numbers from users
- `ccexp` (Expiration) — MMYY Only
- `ccblockfl` (Block Credit Card Creation) — Used with Cenpos to block creation of tokens Available starting 10.2.0; Valid values/xref: Y or N; Default: N
- `fpcustno` (Invoice To) — Finance Company. Can be CHAR(24) if using Xref.; Valid values/xref: ARSC
- `tendqtyfl` (Tender By) — Valid values/xref: (O)rdered or (S)hipped; Default: S
- `ardatcty` (Surcharge Method) — Valid values/xref: (P)roduct Charge, (C)ustomer Charge or (N)o Charge; Default: P
- `addonnum1` (Default Addons for Order Entry) — Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum2` (Default Addons for Order Entry) — Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum3` (Default Addons for Order Entry) — Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum4` (Default Addons for Order Entry) — Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum5` (Default Addons for Order Entry) — Available Starting 4.0; Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum6` (Default Addons for Order Entry) — Available Starting 4.0; Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum7` (Default Addons for Order Entry) — Available Starting 4.0; Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum8` (Default Addons for Order Entry) — Available Starting 4.0; Valid values/xref: SASTO; Default: DCAOC Default
- `inbndfrtfl` (Freight In (Addon no 1)) — Require Addon 1 > 0 to Invoice; Valid values/xref: Y, N; Default: N
- `outbndfrtfl` (Freight Out (Addon no 2)) — Require Addon 2 > 0 to Invoice; Valid values/xref: Y, N; Default: N
- `usesettcalcfl` (Include Addons in Settlement Calc) — Include addons in terms/settlement (net tax) discount. Available starting 6.1.080; Valid values/xref: Y, N; Default: N
- `billdirectaddon` (Bill Direct PO Addon) — Automatically include PO Receiving addons on tied Direct Order; Valid values/xref: (N)one, (A)ll, (F)reight addon only, (O)ther non-freight addons only; Default: N
- `swexaddfl` (Exclude Addons in Service Warranty) — Enter Y or N in each of 4 Positions for Addons 1 through 4. Available Starting 4.1; Valid values/xref: Y, N in each position 1-4; Default: NNNN
- `intratodcd` (Intrastat Terms of Delivery code) — Used with VAT only. Required if country setup to report intrastat in SASTT Country setup Available starting 6.1.080; Valid values/xref: SASTT-TD
- `creditmgr` (Credit Manager) — Valid values/xref: SASO; Default: DCAOC Default
- `securfl` (Security Agreement) — Valid values/xref: Y, N; Default: N
- `credlim` (Credit Limit) — 0 = Unlimited Credit
- `highbal` (High Balance) — Previous Highest Bal
- `holdpercd` (Hold Period) — 0 = No Past Due Check; Valid values/xref: 0 thru 5 only; Default: DCAOC Default
- `selltype` (Sales Order Status) — Valid values/xref: (Y)es, (N)o, (C)ash Only, Co(D) Only, (H)old Until or (O)pen Until; Default: DCAOC Default
- `pmcashfl` (PM Cash Only) — If "Y" only cash payment for customer through ClipShip; Valid values/xref: Y, N; Default: N
- `statusdt` (Hold or Open Date) — Used with Sales Order Status H or O
- `lbxpostty` (Lock Box Post Type) — Used with Lock Box Module. Available Starting 4.0; Valid values/xref: (O)ldest, (S)tatement, (T)otal or <Blank>; Default: <Blank>
- `dnbireqcredlim` (DNBi Requested Credit Limit) — ALL DNBI fields only used with DNBI Interface AO turned on, and SASTT Country code has interface turned on Available Starting 10.0
- `dnbirecomcredlim` (DNBi Recommended Credit Limit) — Available Starting 10.0
- `dnbinocallfl` (DNBi No Call Flag) — Available Starting 10.0; Valid values/xref: Y, N; Default: N
- `dnbiname` (DNBi Company Name) — Available Starting 10.0
- `dnbiaddress` (DNBi Address) — Available Starting 10.0
- `dnbicity` (DNBi City) — Available Starting 10.0
- `dnbistate` (DNBi State) — Available Starting 10.0
- `dnbizipcd` (DNBi Zip Code) — Available Starting 10.0
- `dnbiphoneno` (DNBi Phone Number) — Available Starting 10.0
- `dnbicountry` (DNBi Country) — Available Starting 10.0
- `dnbiscorecard` (DNBi Score Card) — Available Starting 10.0
- `dnbiriskcode` (DNBi Risk Code) — Available Starting 10.0
- `dnbiresponse` (DNBi Match / Response Type) — Available Starting 10.0; Valid values/xref: (E)xact, (L)ist, or blank
- `dnbiexpiredate` (DNBi Expiration Date) — Available Starting 10.0
- `dnbiapplstatus` (DNBi Application Status) — Available Starting 10.0
- `dnbiapplid` (DNBi Application ID) — Available Starting 10.0
- `dnbiparentdunsno` (DNBi Parent Duns Number) — Available Starting 10.0
- `dnbidomesticdunsno` (DNBi Domestic Duns Number) — Available Starting 10.0
- `dnbiglobaldunsno` (DNBi Global Duns Number) — Available Starting 10.0
- `statecd` (Taxing State/Province) — SUT uses SASGM GST uses SASGS VAT uses SASGS Blank if using Tax Xref; Valid values/xref: SASGM RecType 2 / SASGS; Required
- `taxauth` (Tax Authority) — "Old" Code for Use with Tax Xref Or used for GST - Dom or Gov; Valid values/xref: Tax Xref or SASGL
- `countycd` (County) — Only used for SUT Blank if using Tax Xref; Valid values/xref: SASGM Rec Type 3
- `citycd` (City) — Only used for SUT Blank if using Tax Xref; Valid values/xref: SASGM Rec Type 4
- `other1cd` (Other) — Only used for SUT Blank if using Tax Xref; Valid values/xref: SASGM Rec Type 5
- `other2cd` (Other) — Only used for SUT Blank if using Tax Xref; Valid values/xref: SASGM Rec Type 5
- `nontaxtype` (Non Tax Reason) — Can Use Tax Xref; Valid values/xref: SASTT-N; Default: DCAOC Default
- `taxablety` (Taxable Type) — Can Use Tax Xref; Valid values/xref: (Y)es, (N)o or (V)ariable; Default: N
- `taxcert` (Tax Cert #) — Use for SUT and GST SUT - Fed ID # GST - PST License #
- `taxdt` (Tax Cert Exp Date) — Use for SUT and GST SUT - Fed ID # Exp Date GST - PST License # Exp Date
- `taxreg` (PST Registration #) — Use for GST
- `gstcert` (GST/VAT Certificate) — Use for GST and VAT Available starting 5.1
- `gstreg` (GST/VAT Registration #) — Use for GST and VAT Available starting 5.1
- `settdisctype` (Settlement Disc Tax Type) — Use for VAT only Available starting 6.1.080; Valid values/xref: (N)et, (G)ross or Blank to use SASC setting
- `eacktype` (Acknowledgement Type) — Default Method to Send; Valid values/xref: <Blank>, (F)ax, (E)DI, (X)ML or E-(M)ail
- `einvtype` (Invoice Type) — Default Method to Send; Valid values/xref: <Blank>, (F)ax, (E)DI, (X)ML or E-(M)ail
- `estmttype` (Statement Type) — Default Method to Send; Valid values/xref: <Blank>, (F)ax, (E)DI or E-(M)ail
- `eproptype` (Proposal Type) — Default Method to Send; Valid values/xref: <Blank>, (F)ax or E-(M)ail
- `easnto` (Send ASN To) — Valid values/xref: <Blank> or (C)ustomer
- `easngrp` (ASN Group) — Valid values/xref: (O)rder or Sent To [(C)ustomer, (S)hipto, or (G)roup]
- `ecommwhse` (Ecommerce Warehouse) — Valid values/xref: ICSD
- `ediordcd` (Order Status Code) — ANSI X12 Shipment/Order Status Code, Element 368
- `edichgcd` (Change Reason Code) — ANSI X12 Change Reason Code, Element 371
- `edinetwork` (EDI Network) — EDI User 1 on Screen
- `edipartaddr` (EDI Partner Address) — EDI User 2 on Screen
- `ediyouraddr` (EDI Your Address) — EDI User 3 on Screen
- `edicatprodfl` (EDI Catalog Prod) — Accept Catalog Products via EDI. Available Starting 3.2; Valid values/xref: Y, N; Default: N
- `editermsfl` (EDI Terms Override) — Accept Terms Info via EDI. Available Starting 3.2; Valid values/xref: Y, N; Default: N
- `edinsprodfl` (EDI Non-Stock Product) — Accept Non Stock Products via EDI. Available Starting 3.2; Valid values/xref: Y, N; Default: N
- `edijitfl` (EDI JIT Orders) — Create JIT Orders via EDI. Available Starting 3.2; Valid values/xref: Y, N; Default: N
- `ediprintnotesfl` (EDI Print Note/Com) — Set Print Status for Notes/Comments via EDI. Available Starting 3.2; Valid values/xref: Y, N; Default: N
- `ediprcfl` (EDI Price Override) — Allow Price Overrides via EDI. Available Starting 3.2; Valid values/xref: Y, N; Default: N
- `lastcostytd` (Last Year Cost YTD) — Available Starting 3.2
- `lastdiscytd` (Last Year Cash Disc YTD) — Available Starting 3.2
- `lastrebatesytd` (Last Year Rebates YTD) — Available Starting 3.2
- `lastreturnsytd` (Last Year Returns YTD) — Available Starting 3.2
- `lastsalesytd` (Last Year Sales YTD) — Available Starting 3.2
- `lastservchgytd` (Last Year Serv.Chg YTD) — Available Starting 3.2
- `lastunearnedytd` (Last Year Unearned Disc YTD) — Available Starting 3.2
- `balintdatetm` (Balance Integration Date/Time) — Available Starting 10.0 Used with AR Integration to another system
- `user5` (user5) — Used for Conversion Import ID
- `user10` (user10) — Available Starting 5.5
- `user11` (user11) — Available Starting 5.5
- `user12` (user12) — Available Starting 5.5
- `user13` (user13) — Available Starting 5.5
- `user14` (user14) — Available Starting 5.5
- `user15` (user15) — Available Starting 5.5
- `user16` (user16) — Available Starting 5.5
- `user17` (user17) — Available Starting 5.5
- `user18` (user18) — Available Starting 5.5
- `user19` (user19) — Available Starting 5.5
- `user20` (user20) — Available Starting 5.5
- `user21` (user21) — Available Starting 5.5
- `user22` (user22) — Available Starting 5.5
- `user23` (user23) — Available Starting 5.5
- `user24` (user24) — Available Starting 5.5
- `npclaimacctfl` (National Account Program Flag) — Valid values/xref: Y, N; Default: N
- `allowfulfillmentty` (Allow OE Fulfillment) — Blank - Allowed; Valid values/xref: Blank, no, n; Default: Blank
- `createdby` (Created by Inits) — Blank - Allowed; Default: SXE
- `createddt` (Created Date) — Blank - Allowed; Default: g-today
- `createdproc` (Created Process) — Blank - Allowed; Default: DC Conv
- `createdtm` (Created Time) — Blank - Allowed; Default: SYS Time
- `restricteditfl` (Restricted Editing) — Valid values/xref: Y, N; Default: N
- `lnshipcompfl` (OE Line Ship Complete Default) — Available starting 11.19.6; Valid values/xref: Y,N; Default: N
- `bolimit` (OE Back Order Limit) — Available starting 11.19.6; Valid values/xref: < 99
- `nonsf` (Number of non-sufficient fund payments) — Available starting 11.19.9
- `cncartonty` (Use Cartonization) — Available starting 11.20.6
- `cnconfirmshipty` (Confirm Shipment) — Available starting 11.20.6
- `cninvprintty` (Print Carton Detail on Invoices) — Available starting 11.20.6
- `ordrep1` (Order Rep 1) — Available starting 11.20.10; Valid values/xref: Blank or Valid SMSN
- `ordrep2` (Order Rep 2) — Available starting 11.20.10; Valid values/xref: Blank or Valid SMSN
- `ordrep3` (Order Rep 3) — Available starting 11.20.10; Valid values/xref: Blank or Valid SMSN
- `ordrep4` (Order Rep 4) — Available starting 11.20.10; Valid values/xref: Blank or Valid SMSN
- `ordrep5` (Order Rep 5) — Available starting 11.20.10; Valid values/xref: Blank or Valid SMSN
- `orderreppct1` (Order Rep Percentage 1) — Available starting 11.20.10
- `orderreppct2` (Order Rep Percentage 2) — Available starting 11.20.10
- `orderreppct3` (Order Rep Percentage 3) — Available starting 11.20.10
- `orderreppct4` (Order Rep Percentage 4) — Available starting 11.20.10
- `orderreppct5` (Order Rep Percentage 5) — Available starting 11.20.10
- `mansalesfl` (Manufacturer Vendor) — Available starting 11.21.8
- `mancommcalcty` (Calculate Sales Rep Commission From) — Available starting 11.21.8
- `manapsvrowpointer` (Manufacturer Vendor Row Pointer) — Available starting 11.21.8
- `manusesalesrepfl` (Use Sales Rep In/Out For Commission Paid) — Available starting 11.21.8
- `mancustprintty` (Print Invoice For) — Available starting 11.21.8
- `shopifyfl` (Third Party eCommerce integration with Shopify) — Available starting 2022.04.00; Valid values/xref: Y, N; Default: N

### `arscl`
**Accounts Receivable Setup Customer List**
Fields: `cono` (inte) [i], `type` (char) [i], `custno` (deci-0) [im], `shipto` (char) [im], `operinit` (char), `transproc` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `arsd`
**Credit Card Master File**
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `mediacd` (inte) [i], `cardno` (char) [i], `name` (char), `seqno` (inte) [i], `maxamount` (deci-0), `addr` (char), `city` (char), `state` (char), `zipcd` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `createdt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `ccexp` (char), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `createdttz` (datetm-tz)

### `arsde`
**Credit Card Encryption**
Fields: `encseqno` (inte) [i], `createdt` (date), `createdtm` (char), `encryptcd` (raw), `completefl` (logi) [m], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `mstrseqno` (inte)

### `arsg`
**AR Master Group**
*AR master customer group — for grouping customers.*
Fields: `addr` (char[2]), `addr3` (char), `apmgr` (char), `apphoneno` (char), `city` (char) [i], `comment` (char), `cono` (inte) [i], `countrycd` (char), `creditmgr` (char) [i], `credlim` (deci-0), `credlimappty` (char), `crestdt` (date), `currencyty` (char), `email` (char), `faxphoneno` (char), `geocd` (inte), `groupid` (char) [i], `holdpercd` (char), `keyindex` (char), `lastrevdt` (date), `lookupnm` (char) [i], `name` (char) [m], `nextrevdt` (date), `operinit` (char), `phoneno` (char) [i], `pocontctnm` (char), `pophoneno` (char), `selltype` (char), `servchgty` (char), `state` (char) [i], `statusdt` (date), `statustype` (logi) [im], `transdt` (date), `transtm` (char), `transproc` (char), `unearnedty` (char), `zipcd` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `outofcityfl` (logi) [m], `transdttmz` (datetm-tz) [i], `crestdttz` (datetm-tz), `lastrevdttz` (datetm-tz), `nextrevdttz` (datetm-tz), `statusdttz` (datetm-tz), `addressoverfl` (logi) [m], `divno` (inte)

### `arsl`
**Customer Lock Box**
Fields: `cono` (inte) [i], `lockboxno` (char) [im], `custno` (deci-0) [im], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `rowpointer` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `Custno` (Customer) — Can be CHAR(24) if using the Xref.; Valid values/xref: ARSC; Required
- `lockboxno` (Lock Box #) — Valid values/xref: Only 1 record per lock box # allowed; Required
- `user5` (user5) — Used for Conversion Import ID

### `arso`
**Order Pad Filter**
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `custtype` (char) [i], `prodcat` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `arsop`
**Accounts Receivable Certification Program**
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `certifiedtype` (char) [i], `certifiedname` (char) [i], `certifiednbr` (char) [i], `certifiedorg` (char), `expiredt` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `arsp`
**Customer Payment History**
*Customer payment history summary.*
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `per1bal` (deci-0[12]), `per2bal` (deci-0[12]), `per3bal` (deci-0[12]), `per4bal` (deci-0[12]), `per5bal` (deci-0[12]), `lstmthup` (char), `operinit` (char), `transdt` (date), `transtm` (char), `servbal` (deci-0[12]), `credbal` (deci-0[12]), `lastupdt` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `avgpaydays` (inte[12]), `transproc` (char), `lastupdttz` (datetm-tz)

### `arspt`
**AR Customer Price Type Table**
*Customer price type table — controls which pricing tier a customer gets.*
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `pricetype` (char) [i], `pricecd` (inte), `disccd` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `custno` (Customer #) — Can be CHAR(24) if using the Xref.; Valid values/xref: ARSC; Required
- `shipto` (Ship To) — Valid values/xref: ARSS
- `pricetype` (Price Type) — Valid values/xref: SASTT-J; Required
- `pricecd` (Price Disc Level) — Valid values/xref: 1 - 9; Default: 1
- `disccd` (Discount Level) — Valid values/xref: 1 - 9; Default: 0
- `user5` (User5) — Used for Import ID

### `arsrt`
**AR Customer Rebate Type Table**
*Customer rebate type table.*
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `rebatety` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `custno` (Customer #) — Can be CHAR(24) if using the Xref.; Valid values/xref: ARSC; Required
- `shipto` (Ship To) — Valid values/xref: ARSS
- `rebatety` (Rebate Type) — Valid values/xref: SASTT - CT; Required
- `user5` (User5) — Used for Import ID

### `arss`
**AR Ship To**
*Customer ship-to addresses. One customer (arsc) can have many ship-to records. Join on cono+custno.*
**Operators call this:** "Ship To Name" (Sales), "Ship To Outside Rep" (Sales), "Ship To Inside Rep" (Sales), "Address Line 1" (Sales), "Address Line 2" (Sales), "City" (Sales), "State" (Sales), "Postal Code" (Sales), "Sales Territory" (Sales)
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `name` (char) [m], `addr` (char[2]), `city` (char) [i], `state` (char) [i], `zipcd` (char) [i], `phoneno` (char) [i], `faxphoneno` (char), `pocontctnm` (char), `pophoneno` (char), `shipviaty` (char), `shipinstr` (char), `slsrepin` (char), `slsrepout` (char), `whse` (char), `route` (char), `pricetype` (char), `pricecd` (inte), `disccd` (inte), `wodisccd` (inte), `poreqfl` (logi) [m], `orderdisp` (char), `bofl` (logi) [m], `subfl` (logi) [m], `taxablety` (char), `taxcert` (char), `nontaxtype` (char), `statecd` (char), `taxauth` (char), `pickprno` (inte), `noinvcopy` (inte), `lastsaledt` (date), `credlim` (deci-0), `enterdt` (date), `transdt` (date), `countrycd` (char), `transtm` (char), `shiptoeasncd` (char), `operinit` (char), `ediordcd` (char), `edichgcd` (char), `inbndfrtfl` (logi) [m], `eproptype` (char), `outbndfrtfl` (logi) [m], `holdpercd` (inte), `salesterr` (char), `ccno` (char), `ccexp` (char), `dunsno` (char), `synccrmfl` (logi) [m], `mediacd` (inte), `epropto` (logi) [m], `salesamt` (deci-2), `slslimitamt` (deci-0), `user3` (char), `jobdesc` (char), `user4` (char), `holdfl` (logi) [m], `user5` (char), `estcompdt` (date), `user6` (deci-5), `addonno` (inte[4]), `user7` (deci-5), `custpo` (char), `user8` (date), `eacktype` (char), `user9` (date), `eackto` (logi) [m], `einvto` (logi) [m], `edipartner` (char) [i], `einvtype` (char), `langcd` (char), `termstype` (char) [m], `invtofl` (logi) [m], `edinetwork` (char), `easngrp` (char), `easnto` (char), `edipartaddr` (char), `ediyouraddr` (char), `edictrlno` (inte), `ediackver` (char), `ediinvver` (char), `edienvtag` (char[2]), `jobclosedt` (date), `lienfiledt` (date), `lienpredt` (date), `lienprewith` (char), `lienfileoper` (char), `lienpreoper` (char), `gennm` (char) [m], `genaddr` (char[2]), `genst` (char), `gencity` (char), `genzip` (char), `genphoneno` (char), `startdt` (date), `revestdt` (date), `lienamt` (deci-2), `lienpreamt` (deci-2), `bondedfl` (logi) [m], `notesfl` (char), `bondno` (char), `ownnm` (char), `ownaddr` (char[2]), `owncity` (char), `ownst` (char), `ownzip` (char), `lennm` (char) [m], `lenaddr` (char[2]), `lencity` (char), `lenst` (char), `lenzip` (char), `holddays` (inte), `fpcustno` (deci-0), `user1` (char), `user2` (char), `servchgfl` (logi) [m], `geocd` (inte), `restrictfl` (logi) [m], `taxdt` (date), `taxreg` (char), `countycd` (char), `citycd` (char), `other1cd` (char), `other2cd` (char), `statustype` (logi) [m], `ecommwhse` (char), `custshipto` (char), `spcdefaultty` (char) [m], `webpage` (char), `shiplbl` (char), `transproc` (char), `email` (char), `obsedi` (char), `pdcustno` (deci-0), `linetermsfl` (logi) [m], `ptxtype` (char) [m], `addonnum` (inte[8]), `ptxarfl` (logi) [m], `ptxapfl` (logi) [m], `ptxtransbillfl` (logi) [m], `edicatprodfl` (logi) [m], `edinsprodfl` (logi) [m], `ediprintnotesfl` (logi) [m], `edijitfl` (logi) [m], `editermsfl` (logi) [m], `ediprcfl` (logi) [m], `edi840fl` (logi) [m], `consolinvty` (char) [m], `addr3` (char), `invtotype` (char), `genaddr3` (char), `lenaddr3` (char), `ownaddr3` (char), `jobperiodbal` (deci-2[5]), `jobordbal` (deci-2), `jobcodbal` (deci-2), `jobfutinvbal` (deci-2), `jobmisccrbal` (deci-2), `jobservchgbal` (deci-2), `jobuncashbal` (deci-2), `consolterms` (char), `consolformat` (char), `consolinterval` (char), `nextconsoldt` (date), `lastconsoldt` (date), `syncmddfl` (logi) [m], `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `keyindex` (char), `jmjobid` (char), `jmjobrevno` (inte), `rebatety` (char), `srallownegoverfl` (logi) [m], `rowpointer` (char) [i], `wordindexfl` (logi) [m], `intratodcd` (inte), `outofcityfl` (logi) [m], `vattype` (char), `gstreg` (char), `picklabelsize` (char), `strategicacct` (char), `picklabelprefix` (char), `siccd` (inte[3]), `industrytype` (char), `classrating` (char), `balintdatetm` (char), `billdirectaddon` (char), `frttermscd` (char), `transferloc` (char), `esbactioncode` (char), `extshipinstr` (char), `ccblockfl` (logi), `shiptogrp` (char), `transdttmz` (datetm-tz) [i], `allowfulfillmentty` (char), `sigreqtype` (char), `excsxapilstfl` (logi) [m], `bankno` (inte), `divno` (inte), `easntype` (char), `restricteditfl` (logi) [m], `alternateid` (char), `createdby` (char), `createddt` (date), `createdtm` (char), `createdproc` (char), `createddttz` (datetm-tz), `enterdttz` (datetm-tz), `estcompdttz` (datetm-tz), `jobclosedttz` (datetm-tz), `lastconsoldttz` (datetm-tz), `lastsaledttz` (datetm-tz), `lienfiledttz` (datetm-tz), `lienpredttz` (datetm-tz), `nextconsoldttz` (datetm-tz), `revestdttz` (datetm-tz), `taxdttz` (datetm-tz), `lnshipcompfl` (logi) [m], `bolimit` (inte), `addressoverfl` (logi) [m], `copymaintfl` (logi) [m], `ordrep1` (char), `ordrep2` (char), `ordrep3` (char), `ordrep4` (char), `ordrep5` (char), `orderreppct1` (deci-2), `orderreppct2` (deci-2), `orderreppct3` (deci-2), `orderreppct4` (deci-2), `orderreppct5` (deci-2)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `custno` (Customer #) — Can be CHAR(24) if using the Xref.; Valid values/xref: ARSC; Required
- `addr3` (Address - Int'l Only) — Available for all companies starting in 6.1.040. Only accessible for Int'l companies in versions 4.2.002 - 6.1.030.
- `city` (City) — Length 20 prior to 6.1.040
- `state` (State) — Not used with Freeform Style Address AO option starting in 6.1.040.
- `geocd` (GEO Code) — Used with TaxWare Only
- `outofcityfl` (Outside City Limits Flag) — Used with TaxWare Enterprise Only Available starting in 6.1.060; Valid values/xref: Y, N; Default: N
- `countrycd` (Country) — Valid values/xref: SASTT-W
- `statustype` (Status) — (A)ctive or (I)nactive; Valid values/xref: A or I; Default: A
- `termstype` (Terms) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-T; Default: DCAOC Default
- `fpcustno` (Invoice To) — Finance Company Can be CHAR(24) if using xref; Valid values/xref: ARSC
- `servchgfl` (Service Chg.) — If set to Y, this customer is subject to service charges; Valid values/xref: Y, N; Default: N
- `langcd` (Language Code) — Valid values/xref: SASTT-Y
- `shiplbl` (Shipping Label) — Custom Label Design used with IB
- `siccd1` (NAICS Code 1) — Available Starting 10.0
- `industrytype` (Industry Type) — Available Starting 10.0 Uses SASTT Customer Type values; Valid values/xref: SASTT - CU
- `siccd2` (NAICS Code 2) — Available Starting 10.0
- `synccrmfl` (Sync To CRM) — V4.0 and Higher; Valid values/xref: Y, N; Default: Y
- `siccd3` (NAICS Code 3) — Available Starting 10.0
- `syncmddfl` (Synchronize to MDD) — V5.5 and Higher; Valid values/xref: Y, N; Default: Y
- `picklabelsize` (Pick Label Size) — Available Starting 10.0; Valid values/xref: (S)mall or (L)arge; Default: L
- `picklabelprefix` (Pick Label Prefix) — Available Starting 10.0
- `strategicacct` (Strategic Account) — Available Starting 10.0 Only used when ICB Active Interface is turned on in AO.
- `classrating` (Class Rating) — Available Starting 10.0
- `consolinvty` (Consolidated Invoice Type) — Available Starting 4.3; Valid values/xref: <Blank>, (C)ustomer, (S)hipto, Cust (P)O, (O)rder; Default: Blank
- `consolterms` (Consolidated InvoiceTerms) — Available Starting 4.3, Required if Consolidating; Valid values/xref: SASTT - T
- `consolformat` (Consolidated Invoice Format) — Available Starting 4.3, Required if Consolidating; Valid values/xref: <Blank>, (O)rder or (P)roduct Sequence
- `consolinterval` (Consolidated Invoice Interval) — Available Starting 4.3, Required if Consolidating; Valid values/xref: <Blank>,DAily,SU,MO,TU,WE,TH,FR,SA,MThly,SMonthly, Day (1-31)
- `lastconsoldt` (Last Consolidation Date) — Available Starting 4.3
- `nextconsoldt` (Next Consolidation Date) — Available Starting 4.3
- `shipviaty` (Ship Via) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-S
- `custshipto` (Customer Ship to) — Cross Reference to XML Document Field CustJobNo
- `extshipinstr` (Extended Shipping Instructions) — Available Starting 10.1.0.0
- `slsrepout` (Salesrep Out) — Can be CHAR(24) if using xref; Valid values/xref: SMSN; Default: DCAOC Default
- `slsrepin` (Salesrep In) — Can be CHAR(24) if using xref; Valid values/xref: SMSN; Default: DCAOC Default
- `whse` (Default Whse) — Can be CHAR(24) if using xref; Valid values/xref: ICSD
- `salesterr` (Territory) — Valid values/xref: SASTT-Z
- `pickprno` (Pick Priority) — 9 is Highest Priority; Valid values/xref: 0 through 9
- `noinvcopy` (Invoice Copies) — If set to 0 the customer will not receive any invoices.; Default: 1
- `route` (Route/Day/Stop) — Format 3/2/2
- `frttermscd` (Freight Terms Code) — Available Starting 10.0; Valid values/xref: SASTT - FT
- `transferloc` (Transfer Location) — Available Starting 10.0
- `orderdisp` (Disposition) — (S)hip Complete, (T)ag and Hold, (W)ill Call, (J)ust In Time or Blank; Valid values/xref: <Blank>, S, T, W, J; Default: <Blank>
- `subfl` (Subs OK) — Valid values/xref: Y, N; Default: Y
- `bofl` (B/O OK) — Valid values/xref: Y, N; Default: Y
- `poreqfl` (Require PO #) — Valid values/xref: Y, N; Default: N
- `restrictfl` (Restrict Flag) — If (Y)es, Create Order For Ship To In Bid Prep Only; Valid values/xref: Y, N; Default: N
- `linetermsfl` (Line Terms) — Payment Terms by Product. Available Starting 3.2; Valid values/xref: Y, N; Default: N
- `invtofl` (Invoices To) — Send Documents to (B)illto Address or (S)hipto Address; Valid values/xref: B or S; Default: B
- `pricetype` (Price Type) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-J
- `rebatety` (Rebate Type) — Valid values/xref: PDST-CT
- `pricecd` (Price Level) — Must be > 0 to use PDSC Pricing; Default: 1
- `wodisccd` (Order Disc Level) — Must be > 0 to use PDSW Pricing
- `disccd` (Line Disc Level) — Must be > 0 to use PDSC Line Discount
- `pdcustno` (PD Customer) — Assign Pricing from this Customer. Can be CHAR(24) if using xref. Available Starting 4.0; Valid values/xref: ARSC
- `srallownegoverfl` (Allow Negative Overages) — Allow Negative Overage Amount on Showroom Quote Print Available starting 6.1.040; Valid values/xref: Y or N; Default: N
- `spcdefaultty` (OE SPC Default) — Customer Requires Non-Standard Price Per Unit; Valid values/xref: I-ICSP, O-OE, N=no; Default: I
- `inbndfrtfl` (Freight In (Addon no 1)) — Require Addon 1 > 0 to Invoice; Valid values/xref: Y, N; Default: N
- `outbndfrtfl` (Freight Out (Addon no 2)) — Require Addon 2 > 0 to Invoice; Valid values/xref: Y, N; Default: N
- `addonnum1` (Default Addons for Order Entry) — Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum2` (Default Addons for Order Entry) — Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum3` (Default Addons for Order Entry) — Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum4` (Default Addons for Order Entry) — Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum5` (Default Addons for Order Entry) — Available Starting 4.0; Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum6` (Default Addons for Order Entry) — Available Starting 4.0; Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum7` (Default Addons for Order Entry) — Available Starting 4.0; Valid values/xref: SASTO; Default: DCAOC Default
- `addonnum8` (Default Addons for Order Entry) — Available Starting 4.0; Valid values/xref: SASTO; Default: DCAOC Default
- `billdirectaddon` (Bill Direct PO Addon) — Automatically include PO Receiving addons on tied Direct Order; Valid values/xref: (N)one, (A)ll, (F)reight addon only, (O)ther non-freight addons only; Default: N
- `mediacd` (Payment type) — Default Method of Tendering Payment Expanded to 2 digits in 6.0; Valid values/xref: SASTT-P; Default: 0
- `ccno` (Credit Card #) — Use SASO Flag to Mask Numbers from users
- `ccexp` (Expiration) — MMYY Only
- `ccblockfl` (Block Credit Card Creation) — Used with Cenpos to block creation of tokens Available starting 10.2.0; Valid values/xref: Y or N; Default: N
- `credlim` (Credit Limit for Shipto) — If this field is Zero, then ARSC - Customer Credit Limit applies. If this field is not blank, then ARSS - Shipto Credit Limit is applied from this field, and you should also assign a holdpercd. Available Starting 4.0
- `holdpercd` (Hold Period for Shipto) — If Shipto Credit Limit is not Zero, then Hold Period code is set based on this field, where 0 will mean no past due credit check. If Shipto Credit Limit is not Zero and this field is blank then DCAOC default is used. If Shipto Credit Limit is Zero, then ARSC hold period is used and this field is set to zero and is not used by SX.e. Available Starting 4.0; Valid values/xref: Blank or 0 thru 5 only; Default: DCAOC Default
- `enterdt` (Enter Date) — Date the shipto was established Available starting 10.2.0
- `intratodcd` (Intrastat Terms of Delivery code) — Used with VAT only. Required if country setup to report intrastat in SASTT Country setup Available starting 6.1.080; Valid values/xref: SASTT-TD
- `statecd` (Taxing State/Province) — SUT uses SASGM GST uses SASGS VAT uses SASGS Blank if using Tax Xref; Valid values/xref: SASGM RecType 2 / SASGS; Required
- `taxauth` (Tax Authority) — "Old" Code for Use with Tax Xref Or used for GST - Dom or Gov; Valid values/xref: Tax Xref or SASGL
- `countycd` (County) — Only used for SUT Blank if using Tax Xref; Valid values/xref: SASGM Rec Type 3
- `citycd` (City) — Only used for SUT Blank if using Tax Xref; Valid values/xref: SASGM Rec Type 4
- `other1cd` (Other) — Only used for SUT Blank if using Tax Xref; Valid values/xref: SASGM Rec Type 5
- `other2cd` (Other) — Only used for SUT Blank if using Tax Xref; Valid values/xref: SASGM Rec Type 5
- `nontaxtype` (Non Tax Reason) — Can Use Tax Xref; Valid values/xref: SASTT-N; Default: DCAOC Default
- `taxablety` (Taxable Type) — Can Use Tax Xref; Valid values/xref: (Y)es, (N)o or (V)ariable; Default: N
- `taxcert` (Tax Cert #) — Use for SUT and GST SUT - Fed ID # GST - PST License #
- `taxreg` (PST Registration #) — Use for GST
- `gstcert` — Not used in ARSS
- `gstreg` (GST/VAT Registration #) — Use for GST and VAT Available starting 5.1
- `jobdesc` (Descrip) — Only Required if using the Job Screen, else leave blank
- `bondedfl` (Bonded) — Only Required if creating a JOB, else leave blank; Y or N; Valid values/xref: Y, N; Default: NO
- `jmjobid` (JM Job ID Available Starting 6.1) — Ties a shipto to a JM Job; Valid values/xref: JMEH
- `jmjobrevno` (JM Job Revision # Availabel Starting 6.1) — Ties a shipto to a JM Job; Valid values/xref: JMEH
- `genaddr3` (General Contractor Address 3) — Available Starting 4.2
- `gencity` (General Contractor City) — Length 20 prior to 6.1.040
- `ownaddr3` (Owner Address3) — Available Starting 4.2
- `owncity` (Owner City) — Length 20 prior to 6.1.040
- `lencity` (Lender City) — Length 20 prior to 6.1.040
- `holdfl` (Hold if Over) — Hold if Over Sales Limit?; Valid values/xref: Y, N; Default: Y
- `holddays` (Days) — Prelim Filing Deadline in Days From First Sale
- `jobclosedt` (Job Closed) — If Shipto is Inactive, this field is required.; Default: today's date
- `eacktype` (Acknowledgement Type) — Default Method to Send; Valid values/xref: <Blank>, (F)ax, (E)DI, (X)ML or E-(M)ail
- `eackto` (EDI Acknowledgement Sent To) — Valid values/xref: (C)ustomer or (S)hipto; Default: S
- `einvtype` (Invoice Type) — Default Method to Send; Valid values/xref: <Blank>, (F)ax, (E)DI, (X)ML or E-(M)ail
- `einvto` (EDI Invoice Sent To) — Valid values/xref: (C)ustomer or (S)hipto; Default: S
- `eproptype` (Proposal Type) — Default Method to Send; Valid values/xref: <Blank>, (F)ax or E-(M)ail
- `epropto` (EDI Proposal Sent To) — Valid values/xref: (C)ustomer or (S)hipto; Default: S
- `easnto` (Send ASN To) — Valid values/xref: <Blank> or (C)ustomer
- `easngrp` (ASN Group) — Valid values/xref: (O)rder or Sent To [(C)ustomer, (S)hipto, or (G)roup]
- `shiptoeasncd` (Ship To ASN Group Code) — Valid values/xref: ARSS
- `ediordcd` (Order Status Code) — ANSI X12 Shipment/Order Status Code, Element 368
- `edichgcd` (Change Reason Code) — ANSI X12 Change Reason Code, Element 371
- `ecommwhse` (Ecommerce Warehouse) — Valid values/xref: ICSD
- `edinetwork` (EDI Network) — EDI User 1 on Screen
- `edipartaddr` (EDI Partner Address) — EDI User 2 on Screen
- `ediyouraddr` (EDI Your Address) — EDI User 3 on Screen
- `edicatprodfl` (EDI Cat Prod) — Accept Catalog Products via EDI. Available Starting 4.0; Valid values/xref: Y, N; Default: NO
- `edinsprodfl` (EDI NS Product) — Accept Non Stock Products via EDI. Available Staring 4.0; Valid values/xref: Y, N; Default: NO
- `ediprintnotesfl` (EDI Print Notes) — Set Print Status for Notes/Comments via EDI. Available Starting 4.0; Valid values/xref: Y, N; Default: NO
- `edijitfl` (EDI JIT) — Create JIT Orders via EDI. Available Starting 4.0; Valid values/xref: Y, N; Default: NO
- `editermsfl` (EDI Terms) — Accept Terms Info via EDI. Available Starting 4.0; Valid values/xref: Y, N; Default: NO
- `ediprcfl` (EDI Price) — Allow Price Overrides via EDI. Available Starting 4.0; Valid values/xref: Y, N; Default: NO
- `user5` (user5) — Used for Conversion Import ID
- `user10` (user10) — Available Starting 5.5
- `user11` (user11) — Available Starting 5.5
- `user12` (user12) — Available Starting 5.5
- `user13` (user13) — Available Starting 5.5
- `user14` (user14) — Available Starting 5.5
- `user15` (user15) — Available Starting 5.5
- `user16` (user16) — Available Starting 5.5
- `user17` (user17) — Available Starting 5.5
- `user18` (user18) — Available Starting 5.5
- `user19` (user19) — Available Starting 5.5
- `user20` (user20) — Available Starting 5.5
- `user21` (user21) — Available Starting 5.5
- `user22` (user22) — Available Starting 5.5
- `user23` (user23) — Available Starting 5.5
- `user24` (user24) — Available Starting 5.5
- `balintdatetm` (Balance Integration Date/Time) — Available Starting 10.0 Used with AR Integration to another system
- `allowfulfillmentty` (Allow OE Fulfillment) — Blank - Allowed; Valid values/xref: Blank, no, n; Default: Blank
- `excsxapilstfl` — Available Starting 11.18.10 Blank - Allowed; Valid values/xref: Blank,n,y; Default: NO
- `divno` (Division) — 11.18.11; Default: 0
- `bankno` (Bank Number) — 11.18.11; Default: 0
- `alternateid` (Alternate Shipto ID) — 11.19.4
- `createdby` (Created by Inits) — Blank - Allowed; Default: SXE
- `createddt` (Created Date) — Blank - Allowed; Default: g-today
- `createdproc` (Created Process) — Blank - Allowed; Default: DC Conv
- `createdtm` (Created Time) — Blank - Allowed; Default: SYS Time
- `restricteditfl` (Restricted Editing) — Valid values/xref: Y, N; Default: N
- `lnshipcompfl` (OE Line Ship Complete Default) — Available starting 11.19.6; Valid values/xref: Y,N; Default: N
- `bolimit` (OE Back Order Limit) — Available starting 11.19.6; Valid values/xref: < 99
- `copymaintfl` (Copy ARSC Maintenance to ARSS) — Available starting 11.20.5; Valid values/xref: Y,N; Default: N
- `ordrep1` (Order Rep 1) — Available starting 11.20.10; Valid values/xref: Blank or Valid SMSN
- `ordrep2` (Order Rep 2) — Available starting 11.20.10; Valid values/xref: Blank or Valid SMSN
- `ordrep3` (Order Rep 3) — Available starting 11.20.10; Valid values/xref: Blank or Valid SMSN
- `ordrep4` (Order Rep 4) — Available starting 11.20.10; Valid values/xref: Blank or Valid SMSN
- `ordrep5` (Order Rep 5) — Available starting 11.20.10; Valid values/xref: Blank or Valid SMSN
- `orderreppct1` (Order Rep Percentage 1) — Available starting 11.20.10
- `orderreppct2` (Order Rep Percentage 2) — Available starting 11.20.10
- `orderreppct3` (Order Rep Percentage 3) — Available starting 11.20.10
- `orderreppct4` (Order Rep Percentage 4) — Available starting 11.20.10
- `orderreppct5` (Order Rep Percentage 5) — Available starting 11.20.10
- `cyclecd` (Cycle Code) — Available starting 2022.03
- `laststmtdt` (Last Statement Date) — Available starting 2022.03
- `estmttype` (Electronic Statements To) — Available starting 2022.03; Valid values/xref: <Blank>, (F)ax or E-(M)ail
- `estmtto` (Electronic Statements To) — Available starting 2022.03; Valid values/xref: (C)ustomer or (S)hipto; Default: S
- `statementty` (Statement Type) — Available starting 2022.03; Valid values/xref: <blank>, (O)pen or (N)one; Default: N
- `shopifyfl` (Third Party eCommerce integration with Shopify) — Available starting 2022.04.00; Valid values/xref: Y, N; Default: N

### `arst`
**AR Shipto Groups**
Fields: `cono` (inte) [i], `srcrowpointer` (char) [im], `shiptogrp` (char) [i], `name` (char), `rowpointer` (char) [im], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `programname` (char) [i], `busobjectname` (char) [i]

### `asprogram`
**Statefree Appserver Programs**

### `audit`
**Audit Log**
*Audit log — tracks changes across the system.*
Fields: `tablenm` (char) [i], `key` (char) [i], `chglist` (char), `operinit` (char) [i], `transdt` (date) [i], `transtm` (char), `fieldlist` (char), `transproc` (char) [i], `createdt` (date) [i], `createtm` (inte) [i], `xxc1` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `refer` (char), `createdttz` (datetm-tz), `ourproc` (char) [i], `key1` (char) [im], `key2` (char) [im], `mode` (char) [i], `transtype` (char) [im], `authdesc` (char) [m], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `trmgrlang` (char) [i], `standardty` (char), `cono` (inte) [i], `oper2` (char) [im], `ourproc` (char) [i], `key1` (char) [im], `key2` (char) [im], `mode` (char) [i], `transtype` (char) [im], `securcd` (inte) [im], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `authstatus` (char), `actionby` (char), `actiondt` (date), `actiontm` (char), `authtransid` (int6), `actiondttz` (datetm-tz), `cono` (inte) [i], `oper2` (char) [im], `attemptdt` (date) [i], `attempttm` (char) [i], `authstatus` (char), `actionby` (char), `actiondt` (date), `actiontm` (char), `useddt` (date), `usedtm` (char), `ourproc` (char) [i], `key1` (char) [im], `key2` (char) [im], `mode` (char) [i], `transtype` (char) [im], `data1` (char), `data2` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `actiondttz` (datetm-tz), `attemptdttz` (datetm-tz), `useddttz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [im], `printer` (char) [ci], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `authpoints`
**Authorization Points**

### `authsecure`
**Authorization Security**

### `authtrans`
**Authorization Transactions**

### `autodrpcfg`
**Auto Drop Configuration Table**

### `baaa`
**Analysis file activation file**
Fields: `cono` (inte) [i], `analysisnm` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `sourceno` (inte), `triggernm` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `co_num` (char) [i], `wh_num` (char) [im], `vendor_id` (char) [im], `barcode_id` (char) [i], `attribute_name` (char) [i], `attribute_desc` (char), `value_start` (inte), `value_length` (inte), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [im], `barcode_id` (char) [i], `vendor_id` (char) [i], `barcode_length` (inte) [i], `vendor_item_start` (inte), `vendor_item_length` (inte), `abs_num_start` (inte), `abs_num_length` (inte), `quantity_start` (inte), `quantity_length` (inte), `quantity_style` (char), `po_start` (inte), `custom_data` (char[5]), `po_length` (inte), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `barcodedtl`
**Barcode Detail Table**

### `barcodemst`
**Barcode Table**

### `basa`
**Trend Quality Setup Analysis**
Fields: `analysisnm` (char) [i], `descrip` (char), `sourceno` (inte) [i], `generatedfl` (logi) [m], `timeframety` (char), `standardty` (char), `operinit` (char), `transdt` (date), `transtm` (char), `triggernm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `co_num` (char) [im], `wh_num` (char) [im], `dept_num` (inte), `wh_zone` (char), `sys_name` (char) [i], `app_id` (char) [i], `app_name` (char), `app_descr` (char), `app_exe` (char), `app_label_arg` (char), `app_prn_arg` (char), `app_data_arg` (char), `app_fmt_arg` (char), `app_delim_arg` (char), `app_log_arg` (char), `app_other_arg` (char[10]), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `app_debugfl` (logi) [m], `app_directory_path` (char), `trans_datetz` (datetm-tz)

### `bcswmst`
**Barcode Software Integration Table**

### `bin_size`
**Table has the default bin sizes, keyed to company and warehouse**

### `binei`
**Location Extended Information Table**
Fields: `co_num` (char) [im], `wh_num` (char) [im], `bin_num` (char) [i], `ei_type` (char) [i], `ei_id` (char) [i], `ei_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `binmst`
**All locations in the warehouse**
*All bin/location records in the warehouse.*
**Operators call this:** "Bin Code" (TWL), "Bin Warehouse Zone" (TWL), "Bin Rank (ABC)" (TWL), "Bin Cycle-Count Flag" (TWL)
Fields: `co_num` (char) [i], `wh_num` (char) [im], `bin_num` (char) [im], `wh_zone` (char) [im], `aisle` (inte) [im], `loc_type` (char) [m], `prim_pick` (logi) [i], `prim_pick_type` (char) [i], `abs_num` (char) [i], `min_lvl` (deci-2), `max_lvl` (deci-2), `rep_qty` (deci-2), `rep_unit` (char), `max_pal` (inte) [m], `max_weight` (inte) [m], `height` (inte), `width` (inte), `depth` (inte), `cube` (deci-2) [i], `pallet_footprint` (inte), `stack_height` (inte), `bin_hits` (inte), `inboundstgfl` (logi) [m], `physical` (logi) [m], `abc` (char) [i], `check_qty` (logi) [m], `last_count` (char), `custom_data` (char[5]), `row_status` (logi) [m], `cycle_flag` (logi) [m], `pick_sequence` (inte) [i], `trans_user` (char), `abc_pending` (char) [i], `trans_date` (char), `trans_proc` (char), `putaway_group` (char) [i], `last_counttz` (datetm-tz), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `co_num` (char) [i], `wh_num` (char) [im], `loc_type` (char) [im], `loc_type_name` (char), `max_weight` (inte) [m], `height` (inte), `width` (inte), `depth` (inte), `max_pal` (inte) [m], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `wh_num` (Warehouse) — Can be CHAR(24) if Using Whse Cross Reference; Valid values/xref: ICSD, TWL-WHMST; Required
- `row_status` (Status) — (Y)es or (N)o; Valid values/xref: Y or N; Default: Y
- `physical` (Waiting to be counted in Physical) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `inboundstgfl` (Staging Location for Inbound Pallets) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `loc_type` (Location Type) — (B)ulk, (C)arousel, (F)low Rack, (P)allet, (S)helf, S(T)age; Valid values/xref: B, C, F P, S or T; Default: S
- `cube` (Cube) — If blank will be computed as H * W * D; Default: H * W * D
- `max_weight` (Max Weight) — Maximum weight for this location, in pounds.
- `max_pal` (Max Pallets) — Maximum pallets in this location
- `abc` (ABC Class) — Valid values/xref: A, B, C or D; Default: D
- `wh_zone` (Warehouse Zone) — Valid values/xref: WH_ZONE; Required; Default: WLAO
- `prim_pick` (Primary Pick) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `prim_pick_type` (Primary Pick Type) — Only used when Primary Pick is Yes. Blank, (F)ull Case, (S)plit Case, (C)ounter, (P)allet; Valid values/xref: F, S, C, P or blank; Default: S if Primary
- `abs_num` (Item Number) — Only used when Primary Pick is Yes. Can use Product Cross Reference; Valid values/xref: ICSW, TWL-ITEM
- `max_lvl` (Maximum Level) — Only used when Primary Pick is Yes
- `min_lvl` (Minimum Level) — Only used when Primary Pick is Yes
- `rep_qty` (Replenishment Quantity) — Only used when Primary Pick is Yes
- `rep_unit` (Replenishment Unit) — Only used when Primary Pick is Yes. (E)aches, Full (C)ases, Full (P)allets; Valid values/xref: E, C or P; Default: E if Primary
- `check_qty` (Check Quantity) — (Y)es or (N)o; Valid values/xref: Y or N; Default: Y
- `cycle_flag` (Cycle Flag) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `abc_pending` (ABC Pending) — Valid values/xref: A, B, C or D; Default: D
- `custom_data5` (Custom User Field 5) — Used for Import ID

### `birbd`
**Business Intelligence KPI Build Detail**
Fields: `cono` (inte) [i], `kpigroup` (char) [i], `gaugeno` (inte) [i], `pagenum` (inte) [i], `pagelabel` (char), `slicerdata` (char) [i], `slicerlabel` (char), `row1data` (char) [i], `row1label` (char), `row2data` (char) [i], `row2label` (char), `row3data` (char) [i], `row3label` (char), `col1data` (char) [i], `col1label` (char), `col2data` (char) [i], `col2label` (char), `col3data` (char) [i], `col3label` (char), `cell1data` (char), `cell1label` (char), `cell2data` (char), `cell2label` (char), `cell3data` (char), `cell3label` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `birbg`
**Business Intelligence Build KPI Gauge Data**
Fields: `cono` (inte) [i], `kpigroup` (char) [i], `gaugeno` (inte) [i], `name` (char), `type` (char), `currval` (deci-2), `minval` (deci-2), `maxval` (deci-2), `lowval` (deci-2), `highval` (deci-2), `builddt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `bisg`
**Business Intelligence Gauge Setup**
Fields: `cono` (inte) [i], `kpigroup` (char) [i], `gaugeno` (inte) [i], `whse` (char) [i], `name` (char), `type` (char), `minval` (deci-2), `maxval` (deci-2), `lowval` (deci-2), `highval` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `bisk`
**Table of KPI definitions**
Fields: `cono` (inte) [i], `kpi` (char) [i], `descrip` (char), `mathops` (char), `severitycd` (char), `groupcd` (char), `exportdt` (date), `notesfl` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `whse` (char)

### `bism`
**Table of measures definitions**
Fields: `cono` (inte) [i], `measure` (char) [i], `descrip` (char), `type` (char) [i], `exportdt` (date), `notesfl` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `whse` (char)

### `bisms`
**Table of measures_sub_types**
Fields: `cono` (inte) [i], `measure` (char) [i], `seqno` (inte) [i], `type` (char) [i], `key1` (char) [i], `key2` (char) [i], `key3` (char) [i], `key4` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `whse` (char)

### `bisv`
**Table of Stored Values Used in KPI Calculations**
Fields: `cono` (inte) [i], `value_name` (char) [i], `descrip` (char), `type` (char), `dec_value` (deci-4), `exportdt` (date), `notesfl` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `whse` (char) [i], `key1` (char) [i]

### `bpeh`
**Bid Prep Entry Header**
Fields: `cono` (inte) [im], `bpid` (char) [im], `revno` (inte) [im], `quoteno` (inte) [im], `shipto` (char), `custpros` (char) [i], `bptype` (char) [m], `cptype` (char) [i], `whse` (char) [m], `descrip` (char[2]), `enterdt` (date) [im], `entertm` (char) [m], `takenby` (char) [m], `duedt` (date), `begindt` (date), `expiredt` (date), `awarddt` (date), `commtype` (char), `lettercd` (char[6]), `stagecd` (inte) [m], `awardnm` (char), `awarddesc` (char), `custpo` (char), `user9` (date), `revision` (char), `user1` (char), `user2` (char), `transdt` (date) [m], `transtm` (char) [m], `operinit` (char) [m], `contact` (char), `contactphno` (char), `notesfl` (char), `lostbusty` (char), `openinit` (char), `termstype` (char), `slsrepin` (char), `slsrepout` (char), `hirevno` (inte), `pricetype` (char), `pricecd` (inte), `disccd` (inte), `submitfl` (logi) [m], `origcustpros` (char), `origcptype` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `relprocessfl` (logi) [im], `relcompfl` (logi) [m], `relinit` (char) [i], `refer` (char), `useshiptofl` (logi) [m], `usewhsefl` (logi) [m], `overpdscfl` (logi) [m], `transtype` (char) [m], `restrictty` (char), `orderdisp` (char), `reqshipdt` (date), `promisedt` (date), `opentorelfl` (logi) [m], `shipviaty` (char), `lumpbillamt` (deci-2), `lumpbillfl` (logi) [m], `lumppricefl` (logi) [m], `arpwhse` (char), `approvty` (char), `fpcustno` (deci-0), `transproc` (char)

### `bpehc`
**Bid Prep Header Customer/Prospect Cross Ref (Job Bids)**
Fields: `cono` (inte) [im], `bpid` (char) [im], `revno` (inte) [im], `custpros` (char) [i], `sentdt` (date) [i], `cptype` (char) [im], `name` (char), `contact` (char), `contactphno` (char), `sentby` (char) [m], `transdt` (date) [m], `transtm` (char) [m], `operinit` (char) [m], `user9` (date), `user1` (char), `user2` (char), `slsrepin` (char), `slsrepout` (char), `notesfl` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `tcontactno` (char[10]), `tcontactphno` (char[10]), `tcontactfaxno` (char[10]), `transproc` (char)

### `bpehj`
**Bid Prep Job Header**
Fields: `cono` (inte) [im], `bpid` (char) [im], `jobid` (char) [i], `name` (char), `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `phoneno` (char), `faxphoneno` (char), `contactnm` (char), `contactphno` (char), `ownnm` (char), `ownaddr` (char[2]), `owncity` (char), `ownstate` (char), `ownzipcd` (char), `ownphoneno` (char), `gennm` (char), `genaddr` (char[2]), `gencity` (char), `genstate` (char), `genzipcd` (char), `genphoneno` (char), `lennm` (char), `lenaddr` (char[2]), `lencity` (char), `lenstate` (char), `lenzipcd` (char), `lenphoneno` (char), `bondedfl` (logi) [m], `bondid` (char), `operinit` (char) [m], `transdt` (date) [m], `transtm` (char) [m], `lienpredt` (date), `lienpreoper` (char), `lienprewith` (char), `holdfl` (logi) [m], `holddays` (inte), `salesterr` (char), `statecd` (char), `taxauth` (char), `nontaxtype` (char), `taxcert` (char), `lienpreamt` (deci-2), `taxablety` (char), `user7` (deci-5), `user8` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user9` (date), `transproc` (char), `addr3` (char), `genaddr3` (char), `lenaddr3` (char), `ownaddr3` (char)

### `bpehv`
**Bid Prep Vendor Quote Header**
Fields: `cono` (inte) [im], `bpid` (char) [im], `contactnm` (char), `user9` (date), `user1` (char), `user2` (char), `transdt` (date) [m], `transtm` (char) [m], `operinit` (char) [m], `termstype` (char), `vendno` (deci-0) [i], `rcvtype` (char) [m], `notesfl` (char), `user3` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user4` (char), `shipviaty` (char), `fobfl` (logi) [m], `confirmfl` (logi) [m], `shipfmno` (inte) [i], `transproc` (char)

### `bpel`
**Bid Prep Detail Line**
Fields: `cono` (inte) [im], `bpid` (char) [im], `revno` (inte) [im], `user9` (date), `user1` (char), `user2` (char), `transdt` (date) [m], `transtm` (char) [m], `operinit` (char) [m], `lineno` (inte) [im], `linetype` (char) [im], `prod` (char) [im], `reqprod` (char), `xrefprodty` (char), `itemid` (char), `nonstockty` (char), `qtyord` (deci-2), `unit` (char), `price` (deci-5), `baseprice` (deci-5), `listprice` (deci-5), `awardprice` (deci-5), `pdcost` (deci-5), `prcformty` (char), `icspecrecno` (inte), `cstformty` (char), `prodline` (char), `descrip` (char[5]), `lockprfl` (logi) [m], `lockcsfl` (logi) [m], `linestat` (char), `vendno` (deci-0), `lockvnfl` (logi) [m], `minmargin` (deci-2), `printtype` (char), `user5` (char), `cost` (deci-5), `cstform` (deci-2[15]), `prcform` (deci-2[15]), `pricetype` (char), `pricecd` (inte), `prcformfl` (logi) [m], `marginpct` (deci-2), `priceoverfl` (logi) [m], `costoverfl` (logi) [m], `taxablety` (char), `specnstype` (char), `whse` (char) [m], `notimeschg` (inte), `convertstg` (char), `prodcat` (char), `commtype` (char), `lastcost` (deci-5), `lastprice` (deci-5), `lastmargin` (deci-2), `awardty` (char), `disccd` (inte), `priceclty` (char), `kitfl` (logi) [m], `kitrollty` (char), `pdrecno` (inte), `lastcstovfl` (logi) [m], `lastprcovfl` (logi) [m], `lastvendno` (deci-0), `qtybreakty` (char), `commentfl` (logi) [m], `promofl` (logi) [m], `extprice` (deci-2), `extcost` (deci-2), `lastextprc` (deci-2), `lastextcst` (deci-2), `unitconv` (deci-5), `prodcost` (deci-5), `pricecostty` (char), `lastlockfl` (char), `user3` (char), `user4` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `seqid` (char), `prccostty` (char), `relprocessfl` (logi) [m], `accepttype` (char) [i], `jobno` (char), `usepricefl` (logi) [m], `maxqty` (deci-2), `minqty` (deci-2), `termsdiscfl` (logi) [m], `termspct` (deci-2), `ordertype` (char), `cataddfl` (logi) [m], `reqshipdt` (date), `promisedt` (date), `qtyopen` (deci-2), `qtyrel` (deci-2), `qtybr` (deci-2), `speclinedo` (char), `duedt` (date), `shipfmno` (inte), `arpwhse` (char), `transproc` (char)

### `bpelc`
**Bid Prep Converted Line Detail**
Fields: `cono` (inte) [im], `bpid` (char) [im], `revno` (inte) [im], `seqno` (inte) [im], `user9` (date), `user1` (char), `user2` (char), `transdt` (date) [m], `transtm` (char) [m], `operinit` (char) [m], `lineno` (inte) [im], `qtyord` (deci-2), `unit` (char), `convertno` (inte) [im], `ordersuf` (inte) [im], `oelineno` (inte) [im], `transtype` (char) [m], `convertty` (char) [i], `shipto` (char), `refer` (char), `qtytype` (char), `minqty` (deci-2), `maxqty` (deci-2), `convertstg` (char), `releasedt` (date), `releaseno` (inte), `user6` (deci-5), `user7` (deci-5), `user3` (char), `user4` (char), `user5` (char), `user8` (date), `transproc` (char)

### `bpelv`
**Bid Prep Vendor Quote Detail Line**
Fields: `cono` (inte) [im], `bpid` (char) [im], `user9` (date), `user1` (char), `user2` (char), `transdt` (date) [m], `transtm` (char) [m], `operinit` (char) [m], `lineno` (inte) [im], `vendno` (deci-0) [i], `leadtime` (inte), `cstform` (deci-2[15]), `vendquote` (char), `quotedt` (date), `expiredt` (date), `linedisp` (char), `cstformty` (char), `cost` (deci-5), `prod` (char) [im], `user3` (char), `prodcost` (deci-5), `user5` (char), `revno` (inte) [im], `notesfl` (char), `pdcost` (deci-5), `user4` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `vendorprod` (char), `transproc` (char)

### `bpsc`
**Bid Preparation Item Group Components**
Fields: `itemid` (char) [im], `operinit` (char) [m], `transdt` (date) [m], `transtm` (char) [m], `cono` (inte) [im], `itemname` (char) [m], `seqno` (inte) [im], `qtyord` (deci-2), `unit` (char), `linetype` (char) [m], `user9` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `transproc` (char)

### `bpsi`
**Bid Prep Item Group**
Fields: `itemid` (char) [im], `descrip` (char[2]), `operinit` (char) [m], `transdt` (date) [m], `transtm` (char) [m], `cono` (inte) [im], `user9` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `transproc` (char)

### `bpsp`
**Bid Prep Phases Table**
Fields: `descrip` (char[2]), `operinit` (char) [m], `transdt` (date) [m], `transtm` (char) [m], `cono` (inte) [im], `phaseid` (char) [im], `user9` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `transproc` (char), `co_num` (char) [i], `wh_num` (char) [im], `carrier_id` (char) [im], `name` (char), `addr` (char[3]), `city` (char), `state` (char), `zip` (char), `country` (char), `contact` (char), `phone` (char), `fax` (char), `pro_use` (logi) [m], `pro_start` (inte), `pro_current` (inte), `pro_end` (inte), `current_manifest` (inte), `shipper_id` (char), `del_route` (char), `ship_amount` (char), `pm_irms` (char), `req_weight` (char), `req_size` (char), `carrier_type` (char), `fak` (char), `print_packlist` (logi), `scm_required` (logi), `custom_data` (char[5]), `row_status` (logi) [m], `pack_scm` (logi) [m], `trailer_required` (char), `sx_printer` (char), `carrier_printer` (char), `scm_printer` (char), `order_priority` (inte), `rush_orders` (logi), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `load_orderfl` (logi) [m], `load_order_classes` (char), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `carrier_id` (char) [i], `ei_type` (char) [i], `ei_id` (char) [i], `ei_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [im], `carrier_id` (char) [im], `service` (char) [i], `use_carrier_zone` (logi), `carrier_zone` (char) [m], `carrier_zone_commercial` (char), `default_zone` (char), `carrier_service` (char), `date_time` (char), `min_days` (inte), `max_days` (inte), `guaranteed_del_time` (char), `min_weight` (deci-2), `max_weight` (deci-2), `min_packages` (inte), `max_packages` (inte), `load_type` (char), `overridable` (logi), `rate_prg` (char), `custom_data` (char[5]), `row_status` (logi) [m], `com_code` (char), `add_charge` (deci-2), `add_cod` (deci-2), `service_printer` (char), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `carton_num` (inte) [im], `abs_num` (char) [im], `qty` (deci-2), `lot` (char), `uom` (char), `custom_data` (char[5]), `bin_num` (char) [m], `pick_id` (inte) [i], `row_status` (char) [m], `order` (char) [i], `order_suffix` (char) [i], `case_quantity` (deci-4), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `carton_id` (char) [i], `carton_num` (inte), `ei_type` (char) [i], `ei_id` (char) [i], `ei_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `carton_num` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `carton_id` (char) [i], `tracking_id` (char) [i], `box_id` (char), `package_code` (char), `last_order` (char) [im], `last_order_suffix` (char) [i], `cust_code` (char) [i], `carrier_id` (char) [i], `full` (logi) [m], `print_form` (char), `batch` (inte) [i], `sequence` (inte) [i], `weight` (deci-2), `height` (deci-2), `width` (deci-2), `length` (deci-2), `x_of_y` (char), `custom_data` (char[5]), `reference` (char) [i], `bin_num` (char), `return_reason` (char), `row_status` (char) [im], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [i], `box_id` (char) [i], `carrier_id` (char) [i], `length` (deci-2), `height` (deci-2), `width` (deci-2), `cube` (deci-2) [i], `weight` (deci-2), `preferred` (logi), `size_factor` (deci-2), `custom_data` (char[5]), `oversized` (logi) [m], `dim_weight` (deci-2), `description` (char), `package_code` (char), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `cono` (inte) [i], `custno` (deci-0) [i], `shipto` (char) [i], `whse` (char) [i], `recordno` (deci-0) [i], `mediacd` (inte), `cardno` (char), `transcd` (char), `processcd` (inte), `commcd` (inte), `processno` (inte), `exp` (char), `amount` (deci-2), `authamt` (deci-2), `saleamt` (deci-2), `preauthno` (inte), `category` (char), `response` (char), `mediaauth` (inte), `createdt` (date), `createtm` (char), `submitdt` (date), `submittm` (char), `respdt` (date), `resptm` (char), `transdt` (date), `transtm` (char), `operinit` (char), `bankno` (inte), `statustype` (logi) [m], `currproc` (char), `avadd` (char), `avzip` (char), `destzip` (char), `taxamt` (deci-2), `cardid` (inte), `cmc` (char), `cmm` (char), `origproccd` (inte), `origamt` (deci-2), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `charpreauth` (char), `charmediaauth` (char), `createdttz` (datetm-tz), `respdttz` (datetm-tz), `submitdttz` (datetm-tz), `cono` (inte) [i], `oper2` (char) [i], `orderno` (inte), `ordersuf` (inte), `amount` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `rowpointer` (char) [im], `recordid` (char) [i], `reqstream` (clob), `ansstream` (clob), `statusty` (char) [i], `filename` (char), `enterdt` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `enterdttz` (datetm-tz), `cono` (inte) [im], `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `cfgintdata` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `carrier`
**Carrier table**

### `carrier_servic`
**This table ties the carrier to the service, and has information liking a carrier/service combination to a rate table**

### `carrierei`
**Carrier Extended Information Table**

### `carton_size`
**This table will be used to select a box or boxes best suited to ship an order**

### `cartondtl`
**What is inside shipping cartons**

### `cartonei`
**Carton Extended Information Table**

### `cartonmst`
**Carton Master**
**Operators call this:** "Carton Code" (TWL)

### `ccpreauth`
**Credit Card Preauthorization Transaction File**

### `ccrecover`
**Credit Card Recovery Data**

### `cctrans`
**CC Transactions**

### `cfgdata`
**Configurator Order Data**

### `cmas`
**R&D Salesrep Security Matrix**
Fields: `slsrepin` (char) [i], `slsrepout` (char) [i], `dexfl` (logi) [m], `printfl` (logi) [im], `prostype` (char) [im], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `cmcet`
**R&D (T/M Campaign Activity)**
Fields: `campaigncd` (char) [im], `activitycd` (char), `scriptcd` (char), `mustdo` (logi) [im], `notesfl` (char), `operinit` (char), `transdt` (date), `transtm` (char), `schstartdt` (date) [im], `schstarttm` (char) [i], `statuscd` (char), `slsrep` (char) [m], `newrec` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `cmcsq`
**R&D Customer Marketing Campaign Questionaire**
Fields: `campaigncd` (char) [i], `heading` (char), `quest` (char[6]), `qtype` (char[6]), `rank` (inte), `pageno` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `mcdesc` (char[36]), `mcrank` (inte[36]), `entereddt` (date), `slsrep` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `cmet`
**R&D (T/M Activity)**
Fields: `prosno` (deci-0) [im], `slsrep` (char) [im], `statuscd` (char) [im], `mustdo` (logi) [im], `actstartdt` (date) [i], `actstarttm` (char) [im], `actstopdt` (date), `actstoptm` (char) [m], `durationtm` (char) [m], `activitycd` (char) [m], `resultcd` (char) [m], `scriptcd` (char) [m], `name` (char) [im], `campaigncd` (char) [im], `notesfl` (char), `operinit` (char), `transdt` (date) [i], `transtm` (char), `schstartdt` (date) [im], `schstarttm` (char) [im], `comment` (char) [m], `sequenceno` (inte) [i], `newrec` (logi) [m], `phoneno` (char) [m], `autoactfl` (logi) [m], `billfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `cmfu`
**R&D Telemarketing Follow-up file**
Fields: `prosno` (deci-0) [im], `statuscd` (char) [i], `mustdo` (logi) [im], `activitycd` (char), `campaigncd` (char), `prosname` (char), `name` (char) [i], `tz` (char), `notesfl` (char), `sequenceno` (inte) [i], `slsrep` (char) [i], `schstartdt` (date) [i], `schstarttm` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `cmfus`
**R&D Customer Marketing Followup List Generation Specs**
Fields: `slsrep` (char) [i], `forslsrep` (char), `begdt` (date), `enddt` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `cmpmst`
**All companies**
*Company master — all companies in the system. cono is the company number used as a key in virtually every table.*
Fields: `co_num` (char) [i], `co_name` (char), `addr` (char[2]), `city` (char), `state` (char), `zip` (char), `country` (char), `row_status` (logi) [m], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `addr_ext` (char[3]), `trans_datetz` (datetm-tz)

### `cmrp`
**R&D Telemarketing Report List temporary file**
Fields: `prosno` (deci-0) [i], `prod` (char) [i], `proposalno` (deci-0) [i], `name` (char) [i], `slsrep` (char) [im], `schstartdt` (date) [i], `schstarttm` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `cmsa`
**R&D Qualification Answers**
Fields: `prosno` (deci-0) [im], `campaigncd` (char) [i], `answer` (char[6]), `pageno` (inte) [i], `qualifiedfl` (logi) [m], `operinit` (char), `transtm` (char), `transdt` (date), `rank` (inte[6]), `totrank` (inte), `sequenceno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `cmsc`
**R&D (T/M Campaign)**
Fields: `campaigncd` (char) [im], `description` (char), `slsrep` (char), `quotaamt` (deci-0), `notesfl` (char), `operinit` (char), `transdt` (date), `transtm` (char), `costamt` (deci-0), `type` (logi) [m], `prod` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `cmscs`
**R&D (C/M Campaign Scripts)**
Fields: `campaigncd` (char) [im], `scriptcd` (char) [im], `description` (char), `notes` (char[15]), `operinit` (char), `transdt` (date), `transtm` (char), `pageno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `cmsi`
**R&D (C/M Interest)**
Fields: `prosno` (deci-0) [im], `prod` (char) [i], `interest` (char) [i], `qty` (deci-0), `sales` (deci-0), `comment` (char), `name` (char) [m], `notesfl` (char), `operinit` (char), `transdt` (date) [i], `transtm` (char), `frequency` (inte), `othinterest` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `cmsl`
**R&D (C/M Correspondence)**
Fields: `lettercd` (char) [im], `description` (char), `operinit` (char), `transdt` (date), `transtm` (char), `noteln` (char[18]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `cmsn`
**R&D (C/M Contacts)**
Fields: `prosno` (deci-0) [im], `priority` (inte) [i], `salutation` (char), `name` (char) [im], `cotitle` (char), `phoneno` (char) [i], `faxphoneno` (char), `comment` (char), `secretary` (char), `notesfl` (char), `operinit` (char), `transdt` (date) [i], `transtm` (char), `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `oascontactkey` (char), `groupcd` (char), `emailaddr` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `addr3` (char)

### `cmsp`
**R&D (C/M profiles)**
Fields: `prosno` (deci-0) [im], `name` (char) [im], `addr` (char[2]), `city` (char) [i], `state` (char) [i], `zipcd` (char) [i], `country` (char), `slsrep` (char) [i], `phoneno` (char) [i], `faxphoneno` (char), `contactfreq` (inte), `freqtype` (char), `lastcontdt` (date), `lastconttm` (char), `nextcontdt` (date), `nextconttm` (char), `prostype` (char) [im], `cosize` (char), `siccd` (inte[3]), `rating` (char), `stage` (char), `comment` (char), `competition` (char), `bestcall` (char), `sourcepros` (char), `custno` (deci-0) [i], `conoul` (inte) [i], `usercd` (char[2]), `usertype` (char[2]), `notesfl` (char), `operinit` (char), `transdt` (date), `transtm` (char), `autoactcd` (char), `newrec` (logi) [m], `inslsrep` (char), `spcdefaultty` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `eproptype` (char), `transproc` (char), `addr3` (char), `keyindex` (char), `synccrmfl` (logi) [m], `syncmddfl` (logi) [m], `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `cmsq`
**R&D (C/M Proposal)**
Fields: `prosno` (deci-0) [im], `proposalno` (deci-0) [i], `description` (char) [m], `proposaldt` (date), `estsaleamt` (deci-0), `estmarginamt` (deci-0), `estearlycldt` (date), `estlatecldt` (date), `closedt` (date), `earlyclpct` (deci-0), `lateclpct` (deci-0), `prod` (char), `statuscd` (char), `lostbusty` (char), `orderno` (inte), `ordersuf` (inte), `comment` (char), `competition` (char), `campaigncd` (char) [i], `stage` (char), `notesfl` (char), `operinit` (char), `transdt` (date) [i], `transtm` (char), `slsrep` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `cmst`
**R&D (C/M Table Setup)**
Fields: `codeiden` (char) [im], `codeval` (char) [im], `descrip` (char), `slsrep` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `ccfuncnm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `com`
**Comments**
Fields: `cono` (inte) [i], `comtype` (char) [i], `printfl` (logi) [im], `printfl2` (logi) [m], `noteln` (char[16]), `transdt` (date), `transtm` (char), `operinit` (char), `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `rowpointer` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `comtype` (Type of Comment) — See Chart Below; Required
- `orderno` (Order#) — See Chart Below; Required
- `ordersuf` (Order Suffix) — See Chart Below; Default: 0
- `lineno` (Line #) — See Chart Below; Required
- `printfl` (Print on Pick Tickt) — (Y)es or (N)o, Can only have total of 2 comments per order/suf/line, one Printfl = Yes and one Printfl = No; Valid values/xref: Y or N; Default: N
- `printfl2` (Print on Invoice) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `user5` (user5) — Used for Conversion Import ID
- `documentlist` (Print Documents) — Comma separated list of additional print documents for OE comments. Currently supported: oeepa and wltrans

### `comdet`
**Contains detail record information for each of the record formats used by the interface**
Fields: `record_type` (char) [im], `version` (char) [im], `field_name` (char) [im], `field_start` (inte) [im], `field_position` (inte), `field_length` (inte) [m], `active` (logi) [im], `procedure_name` (char), `add_in_reply` (logi) [i], `data_type` (char), `validate` (logi), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `comment_num` (inte) [im], `type` (char) [i], `id` (inte) [i], `line` (inte) [i], `line_sequence` (inte) [i], `comment_line` (inte) [i], `comment_text` (char), `attributes` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `comment`
**Hold multi-line comments for orders and R/T's**

### `commst`
**Contains master record information for each of the record formats used by the interface**
Fields: `record_type` (char) [im], `version` (char) [im], `record_length` (inte), `end_marker` (char), `active` (logi) [im], `upload` (logi) [im], `trans_type` (char) [i], `last_sent_number` (deci-0) [m], `last_sent_time` (char), `last_ack_number` (deci-0) [m], `last_ack_time` (char), `procedure_name` (char), `multiple` (logi) [m], `trailer` (char), `store_procedure` (char), `comments` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `last_ack_timetz` (datetm-tz), `last_sent_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `cono` (inte) [i], `contactid` (deci-0) [im], `comment` (char), `cotitle` (char), `groupcd` (char), `firstnm` (char), `notesfl` (char), `priority` (inte), `salutation` (char), `lastnm` (char), `keyindex` (char), `middlenm` (char), `contacttype` (char), `charuser1` (char), `charuser2` (char), `charuser3` (char), `charuser4` (char), `charuser5` (char), `charuser6` (char), `charuser7` (char), `charuser8` (char), `charuser9` (char), `charuser10` (char), `dateuser1` (date), `dateuser2` (date), `dateuser3` (date), `dateuser4` (date), `dateuser5` (date), `loguser1` (logi) [m], `loguser2` (logi) [m], `loguser3` (logi) [m], `loguser4` (logi) [m], `loguser5` (logi) [m], `decuser1` (deci-2), `decuser2` (deci-2), `decuser3` (deci-2), `decuser4` (deci-2), `decuser5` (deci-2), `intuser1` (inte), `intuser2` (inte), `intuser3` (inte), `intuser4` (inte), `intuser5` (inte), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `crmid` (char) [c], `cmprosno` (deci-0), `synccrmfl` (logi) [m], `langcd` (char), `syncmddfl` (logi) [m], `rowpointer` (char) [i], `wordindexfl` (logi) [m], `esbactioncode` (char), `transdttmz` (datetm-tz) [i], `donotcallfl` (logi) [m], `donotemailfl` (logi) [m], `donotfaxfl` (logi) [m], `donotmailfl` (logi) [m], `cono` (inte) [i], `contactid` (deci-0) [im], `methodkey` (char) [i], `methodtype` (char) [i], `seqno` (inte) [i], `descrip` (char), `primaryfl` (logi) [im], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `emailaddr` (char), `phoneno` (char), `faxphoneno` (char), `ccno` (char), `ccexp` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `addr3` (char), `countrycd` (char), `shipmentnoticefl` (logi) [m], `cono` (inte) [i], `roletype` (char) [i], `roledesc` (char), `primarykey` (char) [i], `secondarykey` (char) [i], `contactid` (deci-0) [im], `rowpointer` (char) [i], `wordindexfl` (logi) [m], `transdttmz` (datetm-tz) [i], `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `contacts`
**Contact Management - Contact Information**
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `roletype` (Role Type) — See Chart Below; Valid values/xref: See Chart; Required
- `primarykey` (Subject Primary) — See Chart Below; Valid values/xref: See Chart; Required
- `secondarykey` (Subject Secondary) — See Chart Below; Valid values/xref: See Chart
- `priority` (Priority) — Valid values/xref: 1 - 999; Default: 0
- `langcd` (Language Code) — Available Starting 5.1; Valid values/xref: SASTT - Y
- `contacttype` (Contact Type) — Valid values/xref: SASTT - CT
- `synccrmfl` (Sync To CRM) — Available Starting 5.1; Valid values/xref: Y or N; Default: Y
- `syncmddfl` (Sync to MDD) — Available Starting 5.1; Valid values/xref: Y or N; Default: Y
- `loguser2` (Logical User 2) — Valid values/xref: Y or N; Default: Y
- `loguser3` (Logical User 3) — Valid values/xref: Y or N; Default: Y
- `loguser4` (Logical User 4) — Valid values/xref: Y or N; Default: Y
- `loguser5` (Logical User 5) — Valid values/xref: Y or N; Default: Y
- `user1` (User 1) — Valid values/xref: Y or N; Default: Y
- `user5` (User 5) — Used for Conversion Import ID
- `donotcallfl` (Do Not Call Flag) — CRM Integration; Valid values/xref: Y or N; Default: Y
- `donotemailfl` (Do Not Email Flag) — CRM Integration; Valid values/xref: Y or N; Default: Y
- `donotfaxfl` (Do Not Fax Flag) — CRM Integration; Valid values/xref: Y or N; Default: Y
- `donotmailfl` (Do Not Mail Flag) — CRM Integration; Valid values/xref: Y or N; Default: Y
- `CAM Subject Type` (Primary Key) — Secondary Key; Valid values/xref: Secondary Key Validation
- `Customer` (Custno) — <Blank>
- `Customer/Shipto` (Custno) — Shipto; Valid values/xref: ARSS
- `Vendor` (Vendno) — <Blank>
- `Vendor/Shipfm` (Vendno) — Shipfmno; Valid values/xref: APSS
- `Prospect` (Prosno) — <Blank>
- `Product` (Prod) — <Blank>

### `contacts-metho`
**Contact Management - Contact Methods Information**
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `roletype` (Role Type) — See Chart Below; Valid values/xref: See Chart; Required
- `primarykey` (Subject Primary) — See Chart Below; Valid values/xref: See Chart; Required
- `secondarykey` (Subject Secondary) — See Chart Below; Valid values/xref: See Chart
- `methodkey` (Method Key) — See Chart Below; Valid values/xref: SASTT - CM; Required
- `descrip` (Description) — Identifier for this contact method such as Office or Home.
- `primaryfl` (Primary Flag) — Only One Record of each Method Key Type can be Primary; Valid values/xref: Y or N; Default: N
- `shipmentnoticefl` (Shipment Notice Flag) — Used only on Email type methods to send shipment notices to this email address during OEES. Available starting 10.3.1; Valid values/xref: Y or N; Default: N
- `addr3` (Address 3) — Available for all companies starting in 6.1.040. Only accessible for Int'l companies in versions 4.2.002 - 6.1.030.
- `city` (City) — Length 20 prior to 6.1.040
- `state` (State) — Not used with Freeform Style Address AO option starting in 6.1.040.
- `countrycd` (Country Code) — Available starting in 10.0; Valid values/xref: SASTT-W
- `ccexp` (Expiration) — Enter as MMYY
- `user5` (user5) — Used for Conversion Import ID
- `CAM Subject Type` (Primary Key) — Secondary Key; Valid values/xref: Secondary Key Validation
- `Customer` (Custno) — <Blank>
- `Customer/Shipto` (Custno) — Shipto; Valid values/xref: ARSS
- `Vendor` (Vendno) — <Blank>
- `Vendor/Shipfm` (Vendno) — Shipfmno; Valid values/xref: APSS
- `Prospect` (Prosno) — <Blank>
- `Method Key` (Descritpion) — Fields Used
- `addr` (Work Address) — address, city, state, zip
- `cc` (Work credit card for purchases) — Credit Card # and Expiration
- `workem` (Work E-mail (required for CRM interface)) — email address
- `homem` (Home email address (currently not interfaced with CRM)) — email address
- `fax` (Fax Phone) — fax phone number
- `workph` (Work/office phone number (required for CRM Interface)) — phone number
- `cellph` (Cell number (only 1 is supported, there is not a way to distinguish work vs personal) (required to interface with CRM)) — phone number
- `homeph` (Home phone (currently not interfaced with CRM)) — phone number
- `pageph` (Pager phone (currently not interfaced with CRM)) — phone number
- `tollph` (Toll-free phone (currently not interfaced with CRM)) — phone number

### `contacts-roles`
**Contact Management - Contact Roles Information**

### `conv`
**SX patch conversion programs.**
Fields: `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `xxde3` (deci-2), `startdt` (date), `enddt` (date), `starttm` (char), `endtm` (char), `patch` (inte) [i], `version` (char) [i], `prognm` (char) [i], `descrip` (char), `seqno` (inte) [i], `recoverydata` (char), `reccreated` (deci-0), `recupdated` (deci-0), `recdeleted` (deci-0), `criteria` (char), `cono` (inte) [i], `oper2` (char) [im], `reportnm` (char) [i], `c2` (char) [i], `c4` (char), `i7` (inte), `i2` (inte), `c1` (char), `dt` (date), `dt-2` (date), `c13` (char), `c15` (char), `c4-2` (char), `c2-2` (char), `de9d2s` (deci-2), `c2-3` (char), `de9d2s-2` (deci-2), `c6` (char), `l` (logi) [m], `c24` (char) [i], `c24-2` (char), `de12d0` (deci-0) [i], `de12d5` (deci-5), `i4` (inte), `i3` (inte), `de2d3` (deci-3), `c24-3` (char), `c20` (char) [i], `rid` (reci), `c20-2` (char), `dt-3` (date), `dt-4` (date), `de9d2s-3` (deci-2), `de2d3-2` (deci-3), `de2d3-3` (deci-3), `de2d3-4` (deci-3), `de2d3-5` (deci-3), `de12d5-2` (deci-5), `de12d5-3` (deci-5), `de12d5-4` (deci-5), `faxfl` (logi) [m], `outputty` (char) [i], `c12` (char) [i], `ComponentId` (char) [im], `ComponentName` (char) [i], `ComponentDescription` (char), `ComponentMethodId` (char) [im], `ComponentId` (char) [i], `MethodRequest` (char) [i], `MethodProcedure` (char), `MethodObject` (char), `MethodInputOutput` (logi), `MethodDAObject` (char), `MethodDatasetName` (char) [i], `MethodDatasetFile` (char) [i], `MethodIgnoreBuffer` (char), `ContextId` (char) [im], `ContextSeq` (inte) [i], `ContextSessionId` (char) [i], `ContextTaskId` (char) [i], `ContextField` (char) [i], `ContextValue` (char), `ContextRaw` (raw), `ContextSessionID` (char) [i], `StoreId` (char), `TableName` (char) [i], `KeyValues` (char), `RowSequence` (inte) [i], `isBeforeRow` (logi), `TimeStamp` (datetm-tz), `OriginRowid` (char), `RawData` (raw), `LanguageId` (char) [im], `LanguageCode` (char) [i], `LanguageDescription` (char), `MessageId` (char) [im], `MessageNum` (inte) [i], `MessageText` (char), `LanguageId` (char) [i], `consumerkey` (char) [im], `recvnonce` (char) [im], `transdttmz` (datetm-tz) [i], `PermissionId` (char) [im], `PermissionExecute` (logi), `UserGroupId` (char) [i], `ComponentMethodId` (char) [im], `sessionid` (char) [i], `cpobject` (raw), `expirationdate` (datetm-tz) [i], `externalguid` (char) [i], `tenantname` (char), `transdttmz` (datetm-tz) [i], `UserGroupId` (char) [im], `UserGroupName` (char) [i], `UserGroupDescription` (char), `UserLoginID` (char) [i], `UserLoginName` (char) [i], `UserLoginPassword` (char), `UserGroupID` (char), `c_id` (int6) [im], `c_xml` (blob), `c_tenant_id` (char) [i], `c_logical_id` (char) [i], `c_message_priority` (inte) [i], `c_created_date_time` (datetm) [i], `c_was_processed` (inte) [i], `accountingentity` (char) [i], `actioncode` (char), `bodid` (char) [i], `noun` (char) [i], `variationid` (int6), `c_id` (int6) [im], `c_inbox_id` (int6) [im], `c_header_key` (char), `c_header_value` (char), `c_id` (int6) [im], `c_xml` (blob), `c_tenant_id` (char) [i], `c_logical_id` (char) [i], `c_message_priority` (inte) [i], `c_created_date_time` (datetm) [i], `c_was_processed` (inte) [i], `accountingentity` (char) [i], `actioncode` (char), `bodid` (char) [i], `dbrowid` (char) [im], `noun` (char) [i], `variationid` (int6), `c_id` (int6) [im], `c_outbox_id` (int6) [im], `c_header_key` (char), `c_header_value` (char), `c_id` (int6) [im], `c_property_name` (char), `c_property_value` (char), `co_num` (char) [i], `wh_num` (char) [im], `abs_num` (char) [im], `bin_num` (char) [i], `count_type` (char) [im], `count_date` (date) [im], `emp_num` (char), `date_time` (char), `exp_qty` (deci-2), `actual_qty` (deci-2), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `count_datetz` (datetm-tz), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz)

### `convert`
**Tempory file for Conversions**

### `cor_inbox_entr`

### `cor_inbox_head`

### `cor_outbox_ent`

### `cor_outbox_hea`

### `cor_property`

### `core_component`

### `core_context`

### `core_contextst`

### `core_language`
**Maintains supported language codes**

### `core_messageda`
**Holds messages for use in translation, both application and systems messages**

### `core_nonce`

### `core_permissio`
**Contains cross-reference between UserLogin and ComponentMethod**

### `core_session`
**Service Interface Session**

### `core_tenantlin`
**Link to tenant**

### `core_usergroup`
**contains user group data**

### `core_userlogin`
**Table contains user login and password. All other details will be in an application database table, e.g. employee**

### `counthistory`
**Table contains a history of counts**

### `crerb`
**Bank Reconciliation Details**
Fields: `cono` (inte) [im], `bankno` (inte) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `transdttmz` (datetm-tz), `operinit` (char), `totmatched` (deci-2), `totunmatched` (deci-2), `totmanual` (deci-2), `totcredit` (deci-2), `totdebit` (deci-2), `endingbal` (deci-2), `statementdt` (date), `openinit` (char), `exchgrate` (deci-7)

### `crerm`
**Bank Reconciliation Matching between Bank Records and CR Transactions**
Fields: `cono` (inte) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `transdttmz` (datetm-tz), `operinit` (char), `srcrowpointer` (char) [im], `cretrowpointer` (char) [im]

### `crerr`
**Bank Reconciliation Records downloaded from the Bank**
Fields: `cono` (inte) [im], `bankno` (inte) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `rowpointer` (char) [i], `transdttmz` (datetm-tz), `operinit` (char), `seqno` (inte) [im], `postdt` (date), `checkno` (deci-0), `amount` (deci-2), `refer` (char), `ckrectype` (inte), `offsetbank` (inte) [m], `offsetcheck` (deci-0), `offsettype` (inte), `matchedamount` (deci-2), `modulenm` (char), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `description` (char), `bankrefer` (char), `rulename` (char) [im], `matchedfl` (logi) [im], `manualfl` (logi) [m], `keyindex` (char) [i], `offsetexrate` (deci-7)

### `cret`
**CR Transactions**
Fields: `cono` (inte) [i], `bankno` (inte) [i], `checkno` (deci-0) [i], `transdt` (date) [i], `transtm` (char) [i], `operinit` (char), `amount` (deci-2), `refer` (char), `ckrectype` (inte) [i], `enterdt` (date) [i], `modulenm` (char), `clearfl` (logi) [m], `voidfl` (logi) [m], `mancheckfl` (logi) [m], `jrnlno` (inte), `voiddt` (date), `balancedfl` (logi) [im], `balanceddt` (date), `cleardt` (date), `vendno` (deci-0) [m], `statustype` (logi) [im], `setno` (inte), `empno` (deci-0), `revfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `urecno` (deci-0) [i], `location` (char) [i], `transproc` (char), `bacsref` (char), `pospaydttmz` (datetm-tz) [i], `pospaytransno` (char), `rowpointer` (char) [i], `balanceddttz` (datetm-tz), `cleardttz` (datetm-tz), `enterdttz` (datetm-tz), `voiddttz` (datetm-tz)

### `crsb`
**R&D Check Rec Setup Banks**
Fields: `cono` (inte) [i], `bankno` (inte) [im], `name` (char) [m], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `phoneno` (char), `bankacct` (char), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `statustype` (logi) [im], `curbookbal` (deci-2), `lastbnkbal` (deci-2), `lastverbal` (deci-2), `lastchkdt` (date), `lastbaldt` (date), `lastchkno` (inte), `lastadjno` (inte), `lastoutno` (inte), `lastdepno` (inte), `lastintno` (inte), `lastchgeno` (inte), `lastinno` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `lasttrialno` (inte), `lastbalno` (inte), `currencyty` (char), `divno` (inte), `transrouteno` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `addr3` (char), `chkopeninit` (char), `wordindexfl` (logi) [m], `rowpointer` (char) [i], `bacsfrmt` (char), `transdttmz` (datetm-tz) [i], `batchno` (inte), `modifier` (inte), `companyid` (char), `moddate` (date), `paymentty` (inte), `merchantuserid` (char), `merchantuserpw` (char), `lastachno` (inte), `lastachdt` (date), `merchantid` (char), `pospaytype` (char), `pospayvoid` (char), `pospayurl` (char), `lastachdttz` (datetm-tz), `lastbaldttz` (datetm-tz), `lastchkdttz` (datetm-tz)

### `crsr`
**Bank Reconciliation Matching Rules**
Fields: `cono` (inte) [im], `bankno` (inte) [im], `rulename` (char) [im], `seqno` (inte) [im], `matchtext1` (char), `matchtext2` (char), `matchtext3` (char), `matchtext4` (char), `matchtext5` (char), `matchtype` (char), `checkpos` (inte), `ckrectype` (inte), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `refer` (char), `offsetbank` (inte), `offsettype` (inte), `transdttmz` (datetm-tz), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `usewordfl` (logi) [m], `checkcolumn` (char), `usefilereferfl` (logi) [m], `id` (inte) [im], `co_num` (char) [im], `wh_num` (char) [im], `cycle_type` (char) [im], `cycle_string` (char) [i], `requested` (char), `started` (char), `completed` (char), `task_id` (inte), `emp_num` (char), `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `completedtz` (datetm-tz), `requestedtz` (datetm-tz), `startedtz` (datetm-tz), `trans_datetz` (datetm-tz)

### `cycle_cnt`
**Table used by the warehouse administrator to set up automatic cycle counts**

### `dealgd`
**Price Discounting Deal Group Detail Setup**
Fields: `cono` (inte) [i], `groupnm` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `gdtype` (char) [i], `gdentity` (char) [i]

### `dealgh`
**Price Discounting Deal Group Header Setup**
Fields: `cono` (inte) [i], `descrip` (char), `groupnm` (char) [i], `grouptype` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `openinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `dealpd`
**Price Discounting Deal Product Setup Detail**
Fields: `cono` (inte) [i], `dealrecno` (inte) [i], `pdtype` (char) [i], `pdentity` (char) [i], `pricemeth` (char), `pricedisc` (deci-5), `quantity` (deci-2), `varfl` (logi) [im], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `dealph`
**Price Discounting Deal Product Setup Header**
Fields: `cono` (inte) [i], `qualtype` (char) [i], `autodealfl` (logi) [m], `autodealty` (char), `dealamt` (deci-2), `dealcom` (char[10]), `dealcomprtfl` (logi) [m], `dealmethfl` (logi) [m], `dealrecno` (inte) [i], `descrip` (char), `enddt` (date), `freedealfl` (logi) [m], `multfl` (logi) [m], `operinit` (char), `pricelvlfl` (logi[10]) [m], `pricetype` (char) [i], `qualamt` (deci-2), `qualcom` (char[10]), `qualcomprtfl` (logi) [m], `qualentity` (char) [i], `qualmethfl` (logi) [m], `qualprice` (deci-2), `showdiscfl` (logi) [m], `startdt` (date) [i], `whse` (char) [i], `transdt` (date), `transtm` (char), `transproc` (char), `openinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `depmst`
**All departments**
Fields: `co_num` (char) [i], `wh_num` (char) [im], `dept_num` (inte) [im], `dept_name` (char), `dept_type` (char), `stage_in` (char) [m], `stage_out` (char) [m], `custom_data` (char[5]), `pick_bin` (char) [m], `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `srcrowid` (char) [i], `srctable` (char) [i], `eventtype` (char) [i], `transdtms` (int6) [i], `sentstatus` (char) [i], `srcrowpointer` (char), `callingguid` (char) [i], `epochtimesent` (int6) [i], `co_num` (char) [i], `wh_num` (char) [im], `dock_id` (char) [im], `name` (char), `carrier_default` (char) [m], `carrier_now` (char) [m], `route_default` (char), `route_now` (char), `stage` (char), `current_trailer_id` (char), `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [im], `rule_code` (char) [i], `log_seq` (inte) [i], `log_text` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [im], `rule_code` (char) [i], `drop_date` (date) [i], `drop_time` (inte) [im], `batch` (inte) [i], `order` (char) [im], `order_suffix` (char) [i], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `comment` (char), `drop_datetz` (datetm-tz), `trans_datetz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [i], `rule_code` (char) [i], `active` (logi) [i], `priority` (inte) [i], `criteria` (char), `date_time` (char), `drop_sec_time` (inte), `proc_created` (char), `custom_data` (char[5]), `row_status` (char), `drp_days` (logi[8]), `drp_now` (logi), `spec_tm` (inte[6]), `every_num` (inte), `every_what` (char), `starttm` (inte), `stoptm` (inte), `criteria_list` (char), `undo_list` (char), `redo_list` (char), `redo_criteria` (char), `lastrundt` (date), `lastruntm` (inte), `nextrundt` (date) [i], `nextruntm` (inte) [i], `employee` (char), `createby` (char), `modifydt` (date), `modifytm` (inte), `modifyby` (char), `processing` (inte) [i], `drp_query` (char), `printer_id` (char), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `lastrundttz` (datetm-tz), `modifydttz` (datetm-tz), `nextrundttz` (datetm-tz), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `vocollect` (logi) [m]

### `dlqueue`

### `dockmstr`
**Has information about shipping docks.**

### `drp_log`

### `drp_ord`
**This table is a transactions file for all orders dropped using the Auto Drop programs**

### `drp_rules`
**Table contains rules used to determine automatic order dropping**

### `edia`
**EDI Audit/Inquiry File.  Purpose of the file is to monitor when EDI transactions are created in Trend and written to the EDI flat files or read into Trend from the EDI flat files**
Fields: `cono` (inte) [i], `statustype` (char) [i], `editype` (char) [i], `keyfielda` (char) [i], `keyfieldb` (char) [i], `keyfieldc` (char) [i], `keyfieldd` (char) [i], `keyfielde` (char) [i], `isanno` (deci-0) [i], `fgno` (deci-0) [i], `stno` (deci-0) [i], `seqno` (inte) [i], `createdt` (date) [i], `createtm` (char), `createinit` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `createdttz` (datetm-tz), `cono` (inte) [i], `docid` (inte) [i], `edifilename` (char) [i], `section` (char) [i], `secseq` (inte) [i], `transdata` (char), `ovrddata` (char), `origdata` (char), `xdatatrans` (char), `xdataovrd` (char), `xdataorig` (char), `approvty` (char) [i], `stagecd` (inte) [i], `createdt` (date), `createtm` (char), `canceldt` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `docseq` (inte) [i], `canceldttz` (datetm-tz), `createdttz` (datetm-tz)

### `edidata`
**EDI Data table. Used to store data associated with EDI or any other Electronic Transaction**

### `edie`
**EDI Error File.  Used to store error records associated to EDIH and EDIL records, based upon errors found EDI Data Translated.**
Fields: `cono` (inte) [i], `batchnm` (char) [i], `seqno` (inte) [i], `level` (logi) [im], `lineno` (inte) [i], `errseqno` (inte) [i], `docty` (char) [i], `fieldty` (char), `fieldvalue` (char), `errty` (char) [i], `statusty` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `whse` (char) [i], `custno` (deci-0) [i], `shipto` (char), `fieldvalueorig` (char), `dataid` (char), `edilineno` (char) [i]

### `edih`
**EDI header file.  Used to store incoming edi purchase order information**
Fields: `cono` (inte) [i], `batchnm` (char) [i], `seqno` (inte) [i], `custpo` (char) [i], `custno` (deci-0) [i], `doctype` (char) [i], `reqshipdt` (date), `canceldt` (date), `refer` (char), `transtype` (char), `nolineitem` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `taxablety` (char), `errstatusty` (char), `transproc` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `docid` (inte), `errcnt` (inte), `exccnt` (inte), `whse` (char), `shipto` (char), `canceldttz` (datetm-tz), `reqshipdttz` (datetm-tz)

### `edil`
**EDI Line File. Contains the edi incoming purchase order line information**
Fields: `cono` (inte) [i], `batchnm` (char) [i], `seqno` (inte) [i], `lineno` (inte) [i], `qtyord` (deci-2), `unit` (char), `price` (deci-5), `reqprod` (char), `shipprod` (char), `xrefprodty` (char), `proddesc` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `proddesc2` (char), `transproc` (char), `edilineno` (char), `custprod` (char), `manfl` (logi), `extlncom` (char), `errcnt` (inte), `exccnt` (inte), `taxablety` (char), `icspecrecno` (inte), `extdesc` (char)

### `edsbwc`
**EDI Service Bench Warranty - Claim (Custom for Project)**
Fields: `cono` (inte) [im], `orderno` (inte) [i], `ordersuf` (inte) [i], `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `installdt` (date), `claimno` (char) [im], `pono` (inte) [i], `posuf` (inte) [i], `stagecd` (char) [i], `warrstatus` (char), `statusty` (char), `contractno` (char), `compbrand` (logi) [m], `repairdt` (date), `bullno` (char), `faileddt` (date), `rooftop` (logi) [m], `labhr` (deci-2), `labrate` (deci-2), `labper` (deci-2), `pndrefr` (deci-2), `dollpnd` (deci-2), `servmate` (deci-2), `repairty` (char), `mesg1` (char), `mesg2` (char), `model` (char), `qty` (deci-2), `distrbno` (char), `modelqty` (deci-2), `serialno` (char[25]), `failno` (char[10]), `failqty` (deci-2[10]), `failsno` (char[10]), `faildt` (date[10]), `failact` (char[10]), `replno` (char[10]), `replqty` (deci-2[10]), `replsno` (char[10]), `repldt` (date[10]), `replact` (char[10]), `dlrprice` (deci-2[10]), `errorcd` (char[10]), `oelineno` (inte[10]), `polineno` (inte[10]), `faultcd` (char)

### `edsbwd`
**EDI Service Bench Warranty - Details (Custom for Project)**
Fields: `cono` (inte) [im], `clmdistno` (char) [im], `clmclaimno` (char) [im], `claimno` (char), `claimtype` (char), `seqno` (inte), `defepartno` (char), `defeserno` (char), `defeqty` (deci-2), `defeinstalldt` (date), `replpartno` (char), `replserno` (char), `replqty` (deci-2), `replinstalldt` (date), `dispcode` (char), `partstatus` (char), `partcredit` (deci-2), `freightpaid` (deci-2), `adminallowance` (deci-2), `penaltypaid` (deci-2), `partadjust` (deci-2), `saletype` (char), `dcamuser` (char), `distxref` (char), `partmarkup` (deci-2), `linestatus` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `edsbwh`
**EDI Service Bench Warranty - Header (Custom for Project)**
Fields: `cono` (inte) [im], `clmdistno` (char) [im], `clmclaimno` (char) [im], `claimno` (char), `distno` (char), `dealerno` (char), `claimdt` (date) [i], `wtystatus` (char), `contractno` (char), `claimfault` (char), `faildt` (date), `repairdt` (date), `claimstatus` (char), `claimclosedt` (date), `accountno` (char), `unitqty` (deci-2), `laborflag` (char), `bulletinno` (char), `totalparts` (deci-2), `totallabor` (deci-2), `totalcredit` (deci-2), `totalclaim` (deci-2), `totalpenalty` (deci-2), `dcamapproval` (deci-2), `tpartadjust` (deci-2), `laboradjust` (deci-2), `distxref` (char), `memoflag` (char), `claimpaiddt` (date), `creditmemono` (char), `claimref` (char), `histdt` (date), `message1` (char), `message2` (char), `userident` (char), `changedt` (date), `claimtype` (char), `edifile` (char), `createdt` (date), `pmtstatus` (char), `freightpaid` (deci-2), `adminallowance` (deci-2), `taxamount` (deci-2), `handlingfee` (deci-2), `driveup` (deci-2), `diagnostic` (deci-2), `origclaimno` (char), `holdb` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `edsbwl`
**EDI Service Bench Warranty - Labor (Custom for Project)**
Fields: `cono` (inte) [im], `clmdistno` (char) [im], `clmclaimno` (char) [im], `claimno` (char), `claimtype` (char), `rooftop` (char), `repairtype` (char), `laborhour` (deci-2), `laboradjhour` (deci-2), `laborrate` (deci-2), `laboradjrate` (deci-2), `laborper` (deci-2), `laboradjper` (deci-2), `poundref` (deci-2), `poundadjref` (deci-2), `dollarpound` (deci-2), `dollaradjpound` (deci-2), `servmate` (deci-2), `adjservmate` (deci-2), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `edsbwm`
**EDI Service Bench Warranty - Model (Custom for Project)**
Fields: `cono` (inte) [im], `clmdistno` (char) [im], `clmclaimno` (char) [im], `modelno` (char), `modelserno` (char), `claimno` (char), `claimtype` (char), `seqno` (inte), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `edsc`
**EDI Cross Reference File**
Fields: `docno` (deci-0) [i], `version` (char) [i], `segment` (char) [i], `element` (deci-0) [i], `loop` (char) [i], `xrefvalue` (char), `transdt` (date), `transtm` (char), `operinit` (char), `partnerid` (char) [i], `transmitty` (logi) [im], `condfield` (char) [i], `condvalue` (char) [i], `xreffield` (char), `elementty` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `edsd`
**EDI Document File**
Fields: `transmitty` (logi) [im], `docno` (deci-0) [i], `version` (char) [i], `segment` (char) [i], `seqno` (deci-6), `maxelem` (inte) [i], `loop` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `edss`
**EDI Segment File**
Fields: `version` (char) [i], `segment` (char) [i], `element` (deci-0) [i], `descrip` (char), `size` (inte), `type` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `edsv`
**EDI Setup Vendor User ID**
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `contractno` (char) [i], `vendorid` (char) [i], `typecd` (char), `custno` (deci-0) [i], `shipto` (char) [i], `custrebty` (char), `custtype` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user9` (date), `user8` (date), `keyindex` (char) [i], `rowpointer` (char) [i], `wordindexfl` (logi) [m], `whse` (char) [i]

### `edsx`
Fields: `docno` (deci-0) [i], `pseudo` (char) [i], `trfield` (char), `transmitty` (logi) [im], `version` (char) [i], `size` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `co_num` (char) [im], `wh_num` (char) [im], `ei_type` (char) [i], `ei_desc` (char), `ei_activefl` (logi) [i], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `cono` (inte) [i], `contactid` (deci-0) [im], `primarykey` (char) [i], `secondarykey` (char) [i], `doctype` (char) [i], `subtype` (char), `user1` (char), `user2` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `ei_type`
**Extended Information Types Table**

### `email-links`
**email-link table to provide reports going out via email with valid email address for the shipto or customer/vendor address**

### `empmst`
**Contains information and access permissions for all employees (operators)**
*Employee/operator master — user accounts, initials, permissions.*
**Operators call this:** "Employee Code" (TWL), "Employee Name" (TWL), "RF Logon" (TWL)
Fields: `co_num` (char), `wh_num` (char), `emp_num` (char) [i], `card_key` (char), `password` (char), `emp_name` (char), `dept_num` (inte), `shf_num` (inte), `emp_title` (char), `rf_logon` (logi) [m], `rf_receipt` (logi) [m], `rf_putaway` (logi) [m], `rf_move` (logi) [m], `rf_stk_move` (logi) [m], `rf_stk_adj` (logi) [m], `rf_pick` (logi) [m], `rf_pack` (logi) [m], `rf_ship` (logi) [m], `rf_inventory` (logi) [m], `rpt_mst` (logi) [m], `cmp_mst` (logi) [m], `wh_mst` (logi) [m], `dep_mst` (logi) [m], `shf_mst` (logi) [m], `emp_mst` (char) [m], `bin_mst` (logi) [m], `itm_mst` (logi) [m], `inv_mst` (logi) [m], `vnd_mst` (logi) [m], `param_mst` (logi) [m], `stn_mst` (logi) [m], `adj_mst` (logi) [m], `cyc_num` (char), `uom_mst` (logi) [m], `cyc_mst` (logi) [m], `physical` (logi), `carrier_mst` (logi) [m], `cust_mst` (logi) [m], `ord_mst` (logi) [m], `stg_mst` (logi) [m], `sys_setup` (logi) [m], `inventory_control` (logi), `custom_data` (char[5]), `row_status` (logi) [m], `util_mst` (char) [m], `zone_pick_fl` (logi) [m], `rush_wh_zone` (char), `emp_printer` (char), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `rf_picksort` (logi) [m], `compile` (logi), `disc_mastfl` (logi) [m], `repl_mastfl` (logi) [m], `packlist_mastfl` (logi) [m], `online_logonfl` (logi) [m], `rf_login_cnt` (inte), `online_adminfl` (logi) [m], `rf_adminfl` (logi) [m], `rfnotesfl` (logi) [m], `pwlastchgdt` (date), `pwprevious` (char[10]), `pwchangefl` (logi) [m], `rfdelorddtlfl` (logi) [m], `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `pwlastchgdttz` (datetm-tz), `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `emp_num` (char) [i], `ei_type` (char) [i], `ei_id` (char) [i], `ei_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `emp_num` (char) [m], `task_id` (char) [i], `trans_id` (char) [i], `task_value` (char), `seqno` (inte), `start_date` (date), `stop_date` (date), `start_time` (char), `stop_time` (char), `task_status` (logi), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `co_num` (char) [i], `wh_num` (char) [im], `rec_type` (char) [i], `date_time` (char) [i], `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `transrptfl` (logi) [m], `fileretfl` (logi) [m], `allocfxfl` (logi) [m], `cyclecntfl` (logi) [m], `custom_data` (char[5]), `commentclrfl` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `disc_cyclefl` (logi) [m], `item_histfl` (logi) [m], `trans_datetz` (datetm-tz), `cono` (inte) [im], `cartid` (char) [im], `section` (char) [im], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `linenumber` (inte) [im], `originallinenumber` (inte) [im], `scope` (inte), `type` (inte), `subtype` (inte), `code` (char), `amount` (deci-5), `description` (char), `breakpointid` (inte), `promotionid` (char), `rejectionsource` (char), `rejectioncode` (char), `rejectiondescrip` (char), `rejecteditems` (char), `descrip` (char), `upgradefee` (deci-5), `sellingprice` (deci-5), `sellingpricetype` (inte), `financialsellingprice` (deci-5), `qtyord` (deci-2), `qtyreturn` (deci-2), `coupon` (char[100]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz), `rowpointer` (char) [i], `cono` (inte) [im], `formattype` (char) [im], `extradatalevel1` (char), `extradatalevel2` (char), `extradatalevel3` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `noun` (char) [i], `showbodfl` (logi) [m], `syncbodfl` (logi) [m], `showmaxcnt` (inte), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `showmaxbodsize` (deci-2), `processbodfl` (logi) [m], `extradatalevel1` (char), `extradatalevel2` (char), `extradatalevel3` (char), `extradataenablefl` (logi) [m], `edenablelev1` (char), `edenablelev2` (char), `noun` (char) [i], `sequence` (inte) [i], `bodname` (char), `dbrowid` (char) [i], `afterdataset` (clob), `wipstatus` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `actioncode` (char), `tenant` (char), `logicalid` (char), `showtologicalid` (char), `acktologicalid` (char), `cono` (inte) [im], `whse` (char) [im], `ordertype` (char) [im], `orderno` (inte) [im], `ordersuf` (inte) [im], `vaseqno` (inte) [im], `lineno` (inte) [im], `palletid` (char) [im], `cartonid` (char) [im], `cartonqty` (deci-2), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `whse` (char) [i], `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `seqno` (inte) [i], `wlstagecd` (inte), `wlstage` (char), `wlstagedt` (date), `carrier` (char), `nolineitem` (inte), `enterdt` (date), `wave` (inte), `transproc` (char), `transtype` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `enterdttz` (datetm-tz), `wlstagedttz` (datetm-tz), `cono` (inte) [i], `whse` (char) [i], `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `seqno` (inte) [i], `wlstagecd` (inte), `wlstage` (char), `wlstagedt` (date), `lineno` (inte) [i], `line_sequence` (inte), `shipprod` (char) [m], `stkqtyord` (deci-2), `stkqtyship` (deci-2), `specnstype` (char), `binloc` (char), `unit` (char), `unitconv` (deci-5), `transproc` (char), `wlemployee` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `wlstagedttz` (datetm-tz), `c_id` (int6) [m], `c_message_id` (char) [im], `c_created_date_time` (datetm), `cono` (inte) [i], `eventname` (char) [im], `triggername` (char) [im], `sourcename` (char), `keyindex` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `purgetransfl` (logi) [m], `eventname` (char) [im], `shortdesc` (char), `longdesc` (char), `sourcename` (char) [i], `whseactionfl` (logi) [m], `custnoactionfl` (logi) [m], `vendnoactionfl` (logi) [m], `prodactionfl` (logi) [m], `standardty` (char), `triggername` (char) [im], `regionactionfl` (logi) [m], `keyindex` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `eventname` (char) [im], `actionseqno` (inte) [i], `whserangety` (char), `whsebeg` (char), `whseend` (char), `custnorangety` (char), `custnobeg` (deci-0), `custnoend` (deci-0), `vendnorangety` (char), `vendnobeg` (deci-0), `vendnoend` (deci-0), `prodrangety` (char), `prodbeg` (char), `prodend` (char), `actiontype` (char), `actionsubjectty` (char), `actionsubjectval` (char), `emailsubject` (char), `emailtext` (char), `contactid` (deci-0), `camactivitycd` (char), `cmactivitycd` (char), `prosno` (deci-0), `comment` (char), `regionrangety` (char), `regionbeg` (char), `regionend` (char), `slctamountty` (char), `slctamountval` (deci-2), `slctamountary` (inte), `slctpricety` (char), `slctpriceval` (deci-5), `slctpriceary` (inte), `slctdatety` (char), `slctdateval` (inte), `slctdateary` (inte), `slctcharty` (char), `slctcharval` (char), `slctcharary` (inte), `programtorun` (char), `prodcatrangety` (char), `prodcatbeg` (char), `prodcatend` (char), `keyindex` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `statustype` (char), `expiredt` (date), `expiredttz` (datetm-tz), `eventname` (char) [im], `dataty` (char) [i], `arraypos` (inte) [i], `fieldlabel` (char), `fieldlength` (inte), `fieldname` (char) [i], `allowblankfl` (logi) [m], `validatelist` (char), `pricecostty` (char), `keyindex` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `eventname` (char) [im], `actionseqno` (inte) [i], `listvalue` (char) [i], `listtype` (char) [i], `keyindex` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `eventname` (char) [im], `eventdt` (date) [im], `eventtm` (char) [im], `recordno` (deci-0) [i], `whse` (char) [i], `prod` (char) [i], `vendno` (deci-0) [i], `lineno` (inte), `custno` (deci-0) [i], `proddesc` (char), `proddesc2` (char), `refer` (char), `jrnlno` (inte), `doctype` (char) [i], `docorderno` (inte) [i], `docordersuf` (inte) [i], `unit` (char), `shipto` (char), `transtype` (char), `qtyord` (deci-2), `stkqtyord` (deci-2), `qtyship` (deci-2), `stkqtyship` (deci-2), `unitconv` (deci-5), `icspecrecno` (inte), `prodcost` (deci-5), `price` (deci-5), `stagecd` (inte), `slsrepin` (char), `slsrepout` (char), `shipfmno` (inte), `amount` (deci-2), `oper2` (char), `region` (char), `slctamountflds` (deci-2[16]), `slctpriceflds` (deci-5[4]), `slctcharflds` (char[16]), `slctdateflds` (date[6]), `takenby` (char), `contactid` (deci-0), `prodcat` (char), `keyindex` (char) [i], `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `docjobid` (char), `eventdttz` (datetm-tz), `slctdatefldstz` (datetm-tz), `cono` (inte) [i], `eventname` (char) [im], `eventdt` (date) [im], `eventtm` (char) [im], `recordno` (deci-0) [i], `actionseqno` (inte) [i], `actionmess` (char), `emailaddr` (char), `emailsubject` (char), `prosno` (deci-0), `sequenceno` (inte), `activityid` (deci-0), `keyindex` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `eventdttz` (datetm-tz), `cono` (inte) [i], `eventname` (char) [im], `eventdt` (date) [im], `eventtm` (char) [im], `recordno` (deci-0) [i], `subseqno` (inte) [i], `fieldname` (char), `fieldlabel` (char), `fieldvalue` (char), `pricecostty` (char), `keyindex` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `eventdttz` (datetm-tz), `file_name` (char) [im], `file_path` (char), `description` (char), `timeframe` (char) [m], `retention_period` (inte) [m], `timestamp` (char), `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `rowpointer` (char) [im], `srcrowpointer` (char) [i], `recordty` (char) [i], `fieldnm` (char) [i], `gdprty` (char) [i], `expiredt` (date) [i], `updatefl` (logi) [m], `operinit` (char), `transdttmz` (datetm-tz) [i], `sourcecd` (char), `expiredttz` (datetm-tz)

### `empmstei`
**Employee Extended Information Table**

### `empproddet`
**Employee Productivity Detail**

### `end_of_day`
**End of Day process setup**

### `eod_setup`
**This table has to do with End of Day Setup by company/warehouse**

### `equatecart`
**Equate Pricing Cart Data**

### `esb_inbound_du`

### `esbextradata`
**ESB - Extra Data Output**

### `esbnoun`
**ESB - Administrative Option (Nouns Being Processed)**

### `esbsingle`
**ESB - Single BOD Noun**

### `esbwlcontainer`
**ESB - WL Containers**

### `esbwlstath`
**Warehouse Logistics ESB Header Information**

### `esbwlstatl`
**Warehouse Logistics ESB Line Information**

### `event_activate`
**Event Manager - Event Activation**

### `event_setup`
**Event Manager - Event Setup**

### `event_setup_ac`
**Event Manager - Event Action Definition**

### `event_setup_fl`
**Event Manager - Event Setup Selection Fields**

### `event_setup_ls`
**Event Manager - Event Action Definition - List**

### `event_trans`
**Event Manager - Event Transactions**

### `event_trans_ac`
**Event Manager - Event Transactions Action**

### `event_trans_su`
**Event Manager - Event Transactions Additional Fields**

### `file_retent`

### `gdprctrl`
**GDPR Control**

### `glar`
**Revaluations**
Fields: `revaldt` (date) [i], `cono` (inte) [im], `currencyty` (char) [im], `revalno` (inte) [im], `jrnlno` (inte) [i], `newexrate` (deci-7), `operinit` (char), `setno` (inte) [i], `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `revaldttz` (datetm-tz)

### `gleb`
**General Ledger Balance Information**
Fields: `cono` (inte) [i], `function` (char) [i], `reportnm` (char) [i], `yr` (inte) [i], `gldivno` (inte) [i], `gldeptno` (inte) [i], `glacctno` (inte) [i], `glsubno` (inte) [i], `asofdt` (date) [i], `glbal` (deci-2), `subbal` (deci-2), `variance` (deci-2), `operinit` (char), `transdt` (date), `transtm` (char), `notesfl` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `asofdttz` (datetm-tz)

### `gleba`
**GL Batch Transactions for AR & AP**
Fields: `cono` (inte) [i], `batchnm` (char) [i], `setno` (inte) [i], `transno` (inte) [i], `amount` (deci-2), `transcd` (inte), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `glebt`
**General Ledger Batch Transactions**
Fields: `cono` (inte) [i], `batchnm` (char) [i], `setno` (inte), `transno` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `amount` (deci-2), `vendno` (deci-0) [m], `custno` (deci-0) [m], `apinvno` (char), `invno` (inte), `invsuf` (inte), `checkno` (deci-0), `bankno` (inte), `transcd` (inte), `refer` (char), `postdt` (date), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `yr` (inte), `seqno` (inte) [i], `crtype` (inte), `statuscd` (char), `clearfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `fixjrnlno` (inte), `fixsetno` (inte), `postdttz` (datetm-tz), `yrtz` (datetm-tz)

### `glee`
**Extended General Ledger References**
Fields: `keyno` (char) [i], `transno` (inte) [i], `setno` (inte) [i], `reference` (char[10]), `operinit` (char), `transdt` (date), `transtm` (char), `cono` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `rowpointer` (char) [i]

### `glet`
**GL Transactions**
Fields: `cono` (inte) [i], `gldivno` (inte) [i], `gldeptno` (inte) [i], `glacctno` (inte) [i], `glsubno` (inte) [i], `jrnlno` (inte) [i], `perfisc` (inte) [i], `postdt` (date) [i], `refer` (char), `percal` (inte), `extendfl` (logi) [m], `amount` (deci-2), `transno` (inte) [i], `transcd` (inte), `operinit` (char), `custno` (deci-0) [m], `checkno` (deci-0), `invno` (inte) [i], `invsuf` (inte) [i], `currproc` (char) [i], `setno` (inte) [i], `transdt` (date) [i], `transtm` (char) [i], `updglty` (char), `yr` (inte), `disputefl` (logi) [m], `hashfl` (logi) [m], `apinvno` (char), `vendno` (deci-0) [m], `referfl` (logi) [m], `exchgrate` (deci-7), `mediacd` (inte), `mediaauth` (inte), `coamount` (deci-2), `charmediaauth` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `transdttmz` (datetm-tz) [i], `postdttz` (datetm-tz), `percaltz` (datetm-tz), `perfisctz` (datetm-tz), `yrtz` (datetm-tz), `rowpointer` (char) [i], `bankno` (inte)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `gldivno` (Div#) — Set to Zero - 0 if using x-ref; Valid values/xref: Numeric Only
- `gldeptno` (Dept#) — Leave blank if using x-ref; Valid values/xref: Numeric Only
- `glacctno` (Acct#) — Legacy System Account Number if using Xref. Can be CHAR(24) if using Xref.; Valid values/xref: Numeric Only if not using Xref; Required
- `glsubno` (Sub#) — Leave blank if using x-ref; Valid values/xref: Numeric Only
- `jrnlno` (Legacy Journal #) — Assign the same value to all records that should be included in the same SASJ journal number; Required
- `setno` (Set #) — Balanced entry sets within the same journal.; Required
- `transno` (Transaction #) — Line number within the Set; Required
- `amount` (Amount) — Debit - positive, Credit - negative; Required
- `transcd` (Transaction Type) — Indicator for amount to display on reports in debit or credit column; Valid values/xref: 1 - Debit; Default: positive amts - 1
- `refer` (Reference) — Reference information from legacy system
- `user5` (User5) — Used for Conversion Import ID

### `gletv`
**Revaluation Transactions**
Fields: `cono` (inte) [im], `docno` (char) [i], `docsuf` (inte) [i], `docseqno` (inte) [i], `glacctno` (inte) [i], `gldeptno` (inte) [i], `gldivno` (inte) [i], `glsubno` (inte) [i], `glexrate` (deci-7), `idno` (deci-0) [i], `sourcecd` (char) [i], `revalno` (inte) [im], `jrnlno` (inte) [i], `newexrate` (deci-7), `oldexrate` (deci-7), `operinit` (char), `setno` (inte) [i], `seqno` (inte) [im], `transcd` (inte) [i], `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `wordindexfl` (logi) [m], `rowpointer` (char) [i], `revaldt` (date), `revaldttz` (datetm-tz)

### `glif`
**General Ledger Inquiry Financial Statement**
Fields: `cono` (inte) [i], `groupnm` (char) [i], `reportnm` (char) [i], `prtlineno` (inte) [i], `recordty` (char), `yr` (inte) [i], `period` (inte) [i], `prtline` (char), `stmtty` (char), `seqlineno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `glifa`
**General Ledger Inquiry Financial Statement Accounts**
Fields: `cono` (inte) [i], `groupnm` (char) [i], `reportnm` (char) [i], `seqlineno` (inte) [i], `columnno` (inte) [i], `gldivno` (inte) [i], `gldeptno` (inte) [i], `glacctno` (inte) [i], `glsubno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `glsa`
**GL Setup Accounts**
Fields: `yr` (inte) [i], `gldivno` (inte) [i], `gldeptno` (inte) [i], `glacctno` (inte) [i], `glsubno` (inte) [i], `gltitle` (char) [m], `lookupnm` (char) [i], `accttype` (char), `baltype` (logi) [m], `printtype` (logi) [m], `fwdbal` (deci-2), `peramt` (deci-2[13]), `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `yrcn` (inte), `acctsub` (deci-0) [i], `glrptgroup` (char) [i], `currencyty` (char), `user1` (char), `user2` (char), `notesfl` (char), `manpostfl` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `cofwdbal` (deci-2), `keyindex` (char) [i], `coperamt` (deci-2[13]), `keywords` (char), `acctgrp` (char), `totamt` (deci-2), `cototamt` (deci-2), `avgexratefl` (logi) [m], `esbfwdfl` (logi) [m], `esbupdtfl` (logi) [im], `esbperfl` (logi[13]) [m], `rowpointer` (char) [i], `wordindexfl` (logi) [m], `esbactioncode` (char), `transdttmz` (datetm-tz) [i], `yrtz` (datetm-tz), `yrcntz` (datetm-tz), `objectid` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `gldivno` (Div#) — Leave blank if using x-ref; Valid values/xref: Numeric Only
- `gldeptno` (Dept#) — Leave blank if using x-ref; Valid values/xref: Numeric Only
- `glacctno` (Acct#) — Legacy System Account Number if using Xref. Can be CHAR(24) if using Xref.; Valid values/xref: Numeric Only if not using Xref; Required
- `glsubno` (Sub#) — Leave blank if using x-ref; Valid values/xref: Numeric Only
- `keywords` (Key Words) — Available Starting 4.0
- `accttype` (Account Type) — Only Profit Clearing should use type C; Valid values/xref: (A)sset, (L)iability, (I)ncome, (E)xpense, (C)learing; Required
- `baltype` (Normal Balance) — Valid values/xref: (D)ebit, (C)redit; Default: Based on Accttype
- `printtype` (Print Type) — Valid values/xref: (D)etail, (S)ummary; Default: D
- `glrptgroup` (Report Group) — Used with GLRD Daily Changes Report; Valid values/xref: SASTT-G
- `manpostfl` (Manual Posting) — If no, users in non-GL modules cannot post to this account; Valid values/xref: Y or N; Default: Y
- `fwdbal` (Forward Balance) — Beginning of year balance for Assets & Liabilities only, all accounts should sum to zero
- `peramt1` (Fiscal Period 1 Net Activity) — Consolidated net activity for the period.
- `peramt2` (Fiscal Period 2 Net Activity) — Consolidated net activity for the period.
- `peramt3` (Fiscal Period 3 Net Activity) — Consolidated net activity for the period.
- `peramt4` (Fiscal Period 4 Net Activity) — Consolidated net activity for the period.
- `peramt5` (Fiscal Period 5 Net Activity) — Consolidated net activity for the period.
- `peramt6` (Fiscal Period 6 Net Activity) — Consolidated net activity for the period.
- `peramt7` (Fiscal Period 7 Net Activity) — Consolidated net activity for the period.
- `peramt8` (Fiscal Period 8 Net Activity) — Consolidated net activity for the period.
- `peramt9` (Fiscal Period 9 Net Activity) — Consolidated net activity for the period.
- `peramt10` (Fiscal Period 10 Net Activity) — Consolidated net activity for the period.
- `peramt11` (Fiscal Period 11 Net Activity) — Consolidated net activity for the period.
- `peramt12` (Fiscal Period 12 Net Activity) — Consolidated net activity for the period.
- `peramt13` (Fiscal Period 13 Net Activity) — Must have AO setup for 13 periods
- `currencyty` (Currency) — Used only if account is a foreign currency for SASC company; Valid values/xref: SASTC
- `user5` (user5) — Used for Conversion Import ID

### `glsb`
**GL Budget**
Fields: `cono` (inte) [i], `gldivno` (inte) [i], `gldeptno` (inte) [i], `glacctno` (inte) [i], `glsubno` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `revno` (inte) [i], `yr` (inte) [i], `frozenfl` (logi) [m], `frozendt` (date), `annbud` (deci-2), `budgettype` (logi) [m], `peramt` (deci-2[13]), `budpct` (deci-2[13]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `frozendttz` (datetm-tz), `yrtz` (datetm-tz), `rowpointer` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `yr` (Year) — Fiscal Year; Required
- `revno` (Revision #) — Revision # beginning with 0; Default: 1
- `gldivno` (Div#) — Leave blank if using x-ref
- `gldeptno` (Dept#) — Leave blank if using x-ref
- `glacctno` (Acct#) — Can be Legacy System GL Account Number CHAR(24) if using Xref; Required
- `glsubno` (Sub#) — Leave blank if using x-ref
- `budgettype` (Entry Type) — $ or % for period amounts; Valid values/xref: $ or %; Required
- `annbud` (Annual Budget) — Total Annual Budget in Dollars; Required
- `budpct/peramt1` (Budget% or Period Amount) — Percents 1 thru 13 = 100 or $ Amounts 1 thru 13 = Annual Budget; Required
- `budpct/peramt2` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt3` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt4` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt5` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt6` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt7` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt8` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt9` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt10` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt11` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt12` (Budget% or Period Amount) — see notes in peramt1
- `budpct/peramt13` (Budget% or Period Amount) — see notes in peramt1
- `user5` (user5) — Used for Conversion Import ID

### `glsd`
**GL Automatic Distributions**
Fields: `groupnm` (char) [i], `setno` (inte) [i], `transno` (inte) [i], `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `percent` (deci-2), `maxamount` (deci-2), `oppositefl` (logi) [m], `refer` (char), `reversefl` (logi) [m], `transdt` (date), `transtm` (char), `operinit` (char), `cono` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `groupnm` (Group Name) — GLED posts entry by group name; Required
- `setno` (Set #) — Sequential number of Master accounts in one group; Required
- `transno` (Transaction #) — Master account always 0 Transactions sequentially numbered starting at 1; Required
- `reversefl` (Group Type) — All trans in one set must be the same type; Valid values/xref: (R)everse or (O)ffset; Default: R
- `refer` (Description/Refer) — Appears as GLET reference
- `gldivno` (Div#) — Enter GL Accounts for Master and Transaction records Leave blank if using x-ref; Valid values/xref: Numeric Only
- `gldeptno` (Dept#) — Leave blank if using x-ref; Valid values/xref: Numeric Only
- `glacctno` (Acct#) — Legacy System Account Number if using Xref. Can be CHAR(24) if using Xref.; Valid values/xref: Numeric Only if not using Xref; Required
- `glsubno` (Sub#) — Leave blank if using x-ref; Valid values/xref: Numeric Only
- `maxamount` (Max Amount) — Optional field for Maximum to post for this distribution. Only set on Trans 0 Master records
- `percent` (Percent of Master Balance) — Zero on Trans 0 Master records. All Trans for one Set must add up to 100.; Required
- `oppositefl` (Opposite Flag) — Only set to Y for Reverse Type sets. For Offset type sets, enter 'Y' if the distribution account code is to have a sign opposite of the posting made to the master account code.; Valid values/xref: Y or N; Default: Y
- `user5` (user5) — Used for Conversion Import ID

### `glsf`
**GL Financial Designs**
Fields: `groupnm` (char) [i], `swseqno` (inte) [i], `rectype` (char), `transdt` (date), `transtm` (char), `begacctno` (inte[15]), `begsubno` (inte[15]), `endacctno` (inte[15]), `endsubno` (inte[15]), `sumfl` (logi) [m], `gltitle` (char), `lookupnm` (char), `addtype` (char), `advtolnno` (inte), `advlnno` (inte), `comment` (char), `printtype` (char), `dollarfl` (logi) [m], `zerotype` (char), `undlntype` (char), `prtcolno` (inte[4]), `prtstrno` (inte[4]), `strcolno` (inte[4]), `user3` (char), `strno` (inte[4]), `user4` (char), `colfl` (logi[15]) [m], `user5` (char), `revfl` (logi[15]) [m], `user6` (deci-5), `totno` (inte), `user7` (deci-5), `clearfl` (logi) [m], `user8` (date), `pagelngth` (inte), `user9` (date), `Pagecntr` (inte), `topmarg` (inte), `botmarg` (inte), `negtype` (char), `decchar` (logi) [m], `headerfl` (logi) [m], `headerno` (inte), `footerfl` (logi) [m], `footerno` (inte), `heading` (char[2]), `pgposno` (inte), `pagectrfl` (logi) [m], `backcol` (inte[15]), `selcol` (char[15]), `selcol2` (char[15]), `posno` (inte[15]), `size` (inte[15]), `printfl` (logi) [m], `ftype` (char), `ftype2` (char), `allcofl` (logi) [m], `alldivfl` (logi) [m], `alldeptfl` (logi) [m], `cono` (inte[20]), `divno` (inte[20]), `deptno` (inte[20]), `begcono` (inte), `endcono` (inte), `begdivno` (inte), `enddivno` (inte), `begdeptno` (inte), `enddeptno` (inte), `sumdtlsel` (inte), `dtlordsel` (inte), `revno` (inte[15]), `cosumfl` (logi) [m], `cohorfl` (logi) [m], `divsumfl` (logi) [m], `divhorfl` (logi) [m], `dpsumfl` (logi) [m], `dphorfl` (logi) [m], `backcol2` (inte[15]), `fieldno` (inte), `oper` (char[15]), `operinit` (char), `val` (deci-2[15]), `seprtor` (char), `storno` (inte[15]), `prtstorno` (inte[15]), `storintotal` (inte), `totaccumfl` (logi) [m], `user1` (char), `user2` (char), `memoryloc` (char), `percal` (inte), `dtposno` (inte), `tmposno` (inte), `transproc` (char), `percaltz` (datetm-tz)

### `glsfm`
**Memory Storage for Statements**
Fields: `memoryloc` (char) [i], `percal` (inte) [i], `groupnm` (char), `operinit` (char), `transdt` (date), `transtm` (char), `totlvl` (deci-2[15]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `percaltz` (datetm-tz)

### `glsfw`
**GLSF Work File**
Fields: `oper2` (char) [im], `reportnm` (char) [i], `rowno` (inte), `cono` (inte), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `yr` (inte), `runcono` (inte) [i], `sortorder` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `yrtz` (datetm-tz)

### `glss`
**GL Distribution**
Fields: `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `accttype` (logi) [m], `disttype` (inte), `key1` (char) [i], `key2` (char) [i], `gldivno` (inte[20]), `gldeptno` (inte[20]), `glacctno` (inte[20]), `glsubno` (inte[20]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `key3` (char) [i], `key4` (char) [i], `Subledger` (char) [i], `seqno` (inte) [i]

### `glsx`
**GL Monthly Exchange Rate**
Fields: `yr` (inte) [i], `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `cono` (inte) [i], `transdt` (date), `transtm` (char), `currencyty` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `acctgrp` (char) [i], `exchgrate` (deci-7[13]), `budexrate` (deci-7[13]), `operinit` (char), `yrtz` (datetm-tz)

### `hlp`
**Help File**
Fields: `fieldnm` (char) [i], `ourproc` (char) [i], `helptext` (char[10]), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char)

### `ibao`
**IB Admin Options**
Fields: `cono` (inte) [im], `shiplabelfl` (logi) [m], `unibardir` (char), `unibarcfg` (char), `transdt` (date), `transtm` (char), `operinit` (char), `screenposfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `unibarexec` (char), `unibardelim` (char), `unibarlog` (char), `unibardebug` (logi) [m]

### `icama`
**ICAM - Analyze Usage Rate - Run Number Table**
Fields: `cono` (inte) [i], `reportno` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `whses` (char[10]), `noprods` (inte), `transproc` (char)

### `icamap`
**ICAM - Analyze Usage Rate - Product Table**
Fields: `cono` (inte) [i], `reportno` (inte) [i], `whse` (char) [i], `prod` (char) [im], `usagectrl` (char), `usgmths` (inte), `usagerate` (deci-2), `orderpt` (deci-0), `linept` (deci-0), `safeallamt` (deci-0), `safeallpct` (deci-0), `ordqtyout` (deci-0), `ordqtyin` (deci-0), `overreasout` (char), `overreasin` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `safeallty` (char) [m], `cono` (inte) [i], `reportno` (inte) [i], `whse` (char) [i], `prod` (char) [im], `usagectrl` (char) [i], `usgmths` (inte) [i], `usagerate` (deci-2), `orderpt` (deci-0), `linept` (deci-0), `safeallamt` (deci-0), `safeallpct` (deci-0), `ordqtyout` (deci-0), `ordqtyin` (deci-0), `overreasout` (char), `overreasin` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `newmethodfl` (logi) [im], `transproc` (char), `safeallty` (char) [m]

### `icamapm`
**ICAM - Analyze Usage Rate - Methods Table**

### `icaml`
**Low Usage Parameters**
Fields: `cono` (inte) [i], `whse` (char) [i], `arpvendno` (deci-0) [i], `prodline` (char) [im], `subrecordfl` (logi) [m], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `icamld`
**Low Usage Parameter Detail**
Fields: `cono` (inte) [i], `whse` (char) [i], `arpvendno` (deci-0) [i], `prodline` (char) [im], `recordtype` (char) [i], `urcvalue` (deci-5) [i], `ordcalcty` (char), `statustype` (char) [m], `minval` (inte), `maxval` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `icamu`
**ICAM Update file. Holds information loaded from ICAM. Used by buyer to update ICSW ordering and usage information**
Fields: `cono` (inte) [i], `whse` (char) [im], `prod` (char) [im], `buyer` (char) [i], `frozentype` (char) [i], `vendno` (deci-0) [im], `prodline` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `activefl` (logi) [im], `prodcat` (char), `class` (inte), `frozenmmyy` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `updatefl` (logi) [m], `transproc` (char), `countryoforigin` (char), `tariffcd` (char)

### `icamue`
**ICAMU exceptions file.  Holds exception information for warehouse products.  Used by the buyer to adjust ordering quantities.**
Fields: `cono` (inte) [i], `whse` (char) [im], `prod` (char) [im], `buyer` (char) [i], `frozentype` (char) [i], `frozenmmyy` (char) [i], `activefl` (logi) [im], `exctype` (char) [i], `excdesc` (char), `excmsg` (char), `excde1` (deci-2), `excde2` (deci-2), `excde3` (deci-2), `excde4` (deci-2), `excde5` (deci-2), `excde6` (deci-2), `excde7` (deci-2), `excde8` (deci-2), `excde9` (deci-2), `excde10` (deci-2), `exci1` (inte), `exci2` (inte), `exci3` (inte), `exci4` (inte), `exci5` (inte), `exci6` (inte), `excda1` (date), `excda2` (date), `excda3` (date), `excda4` (date), `excda5` (date), `excda6` (date), `excc1` (char), `excc2` (char), `excc3` (char), `excc4` (char), `excc5` (char), `excc6` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `excc7` (char), `excc8` (char), `excc9` (char), `excc10` (char), `excc11` (char), `excc12` (char), `exci7` (inte), `exci8` (inte), `exci9` (inte), `exci10` (inte), `excda1tz` (datetm-tz), `excda2tz` (datetm-tz), `excda3tz` (datetm-tz), `excda4tz` (datetm-tz), `excda5tz` (datetm-tz), `excda6tz` (datetm-tz)

### `iceaa`
**Core allocation table**
Fields: `cono` (inte) [i], `transty` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `retorderno` (inte) [i], `retordersuf` (inte) [i], `retlineno` (inte) [i], `qty` (deci-0), `whse` (char), `prod` (char) [i], `subfl` (logi) [m], `transdt` (date), `transtm` (char), `operinit` (char), `manadjfl` (logi) [m], `manoper` (char), `mandt` (date), `mantm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `mandttz` (datetm-tz)

### `iceab`
**Stores core information on cores to be applied to orders not yet received.**
Fields: `cono` (inte) [i], `custno` (deci-0) [i], `shipto` (char) [i], `coreprod` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `qtybank` (deci-0), `transdt` (date), `transtm` (char), `operinit` (char), `manadjfl` (logi) [m], `manoper` (char), `mandt` (date), `mantm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `mandttz` (datetm-tz)

### `iceam`
**Tracks PO, OE and WT line total transactions for cores.**
Fields: `cono` (inte) [i], `transty` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `whse` (char), `origprod` (char) [i], `coreprod` (char) [i], `vendno` (deci-0) [i], `custno` (deci-0) [i], `statusfl` (logi) [im], `pfpfl` (logi) [m], `qty` (deci-0), `qtybank` (deci-0), `qtywarr` (deci-0), `qtyalloc` (deci-0), `intclaimno` (inte), `vendclaimno` (char), `repairordno` (inte), `repairordsuf` (inte), `repairlineno` (inte), `corechg` (deci-2), `corevalue` (deci-2), `coreduedt` (date) [i], `invoicedt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `manadjfl` (logi) [m], `manoper` (char), `mandt` (date), `mantm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `implyqty` (inte), `transproc` (char), `implylineno` (inte) [i], `implyprod` (char) [i], `price` (deci-2), `implyreplineno` (inte), `seqno` (inte) [i], `coreduedttz` (datetm-tz), `invoicedttz` (datetm-tz), `mandttz` (datetm-tz)

### `iceat`
**Tracks PO, OE and WT line detail transactions for cores.**
Fields: `cono` (inte) [i], `transty` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `whse` (char) [i], `warrchfl` (logi) [im], `vendno` (deci-0), `claimpdfl` (logi) [im], `claimpddt` (date) [i], `repairordno` (inte), `repairordsuf` (inte), `repairlineno` (inte), `prod` (char) [i], `subfl` (logi) [im], `retorderno` (inte) [i], `retordersuf` (inte) [i], `retlineno` (inte) [i], `qty` (deci-0), `qtybank` (deci-0), `qtywarr` (deci-0), `qtyalloc` (deci-0), `intclaimno` (inte), `vendclaimno` (char), `snsold` (char), `snreturn` (char), `expiredt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `manadjfl` (logi) [m], `manoper` (char), `mandt` (date), `mantm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `implylineno` (inte) [i], `implyprod` (char) [i], `implyreplineno` (inte), `compseqno` (inte) [i], `claimpddttz` (datetm-tz), `expiredttz` (datetm-tz)

### `iceav`
**Tracks implied quantity and dirty cores.**
Fields: `cono` (inte) [i], `whse` (char) [i], `origprod` (char) [i], `coreprod` (char) [i], `vendno` (deci-0) [i], `qtyimply` (deci-0), `qtyoh` (deci-0), `qtywarr` (deci-0), `transdt` (date), `transtm` (char), `operinit` (char), `manadjfl` (logi) [m], `manoper` (char), `mandt` (date), `mantm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `mandttz` (datetm-tz), `cono` (inte) [im], `whse` (char) [im], `cartonid` (char) [im], `icecnhdrrowpointer` (char) [i], `ordrowpointer` (char) [im], `lineno` (inte) [im], `seqno` (inte) [im], `prod` (char) [i], `itmcubesize` (deci-5), `itemqty` (deci-5), `itemunit` (char), `width` (deci-5), `height` (deci-5), `length` (deci-5), `weight` (deci-5), `cube` (deci-5), `exceptmsg` (char), `instructions` (char), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `ordertype` (char) [im], `cono` (inte) [im], `whse` (char) [im], `cartonid` (char) [im], `cartonno` (inte) [i], `rowpointer` (char) [i], `pkgno` (inte) [i], `shippingid` (char) [i], `pkgid` (char), `pkgtype` (char), `pkggroupty` (char), `sizemeaspkg` (char), `pkgcubesize` (deci-5), `pkgweight` (deci-2), `dimweight` (deci-2), `actweight` (deci-2), `dimdivsor` (inte), `freightamt` (deci-2), `statusty` (char), `updatety` (char), `updateoper` (char), `updatetrans` (char), `transdttmz` (datetm-tz) [i], `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `instructions` (char), `trackerid` (char), `freefreightfl` (logi) [m], `cono` (inte) [i], `whse` (char) [i], `icecndtlrowpointer` (char) [im], `serlotty` (char) [im], `serlotno` (char) [im], `quantity` (deci-2), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icecndtl`
**Cartonization Package Detail**

### `icecnhdr`
**Cartonization Package Header**

### `icecnserlot`
**Cartonization Package Detail - Serial/Lot**

### `iceh`
**Temporary File to Hold Handheld Device Data**
Fields: `keyno` (deci-2) [i], `dataid` (inte), `indata` (char), `labelfl` (logi) [m], `updfl` (logi) [m], `lineno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icenh`
**Headers For Non-stocks & Drops**
Fields: `cono` (inte) [i], `prod` (char) [im], `whse` (char) [im], `prodcat` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `jrnlno` (inte) [i], `setno` (inte) [i], `typecd` (char) [i], `seqnoh` (inte) [i], `receiptno` (inte), `receiptsuf` (inte), `receiptty` (char), `opendt` (date) [i], `closedt` (date), `closety` (char), `activefl` (logi) [im], `unit` (char), `descrip` (char[2]), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `binloc` (char[2]), `icswprod` (char), `icspprodcat` (char), `ncnr` (char), `eccnclasscd` (char), `icspaltprodgrp` (char), `altprodgrp` (char), `wordindexfl` (logi) [m], `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `closedttz` (datetm-tz), `opendttz` (datetm-tz)

### `icenl`
**Detail Lines For Non-Stocks & Drops**
Fields: `cono` (inte) [i], `prod` (char) [im], `whse` (char) [im], `prodcat` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `jrnlno` (inte) [i], `setno` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `typecd` (char) [i], `seqnod` (inte) [i], `ordtype` (char) [i], `entrytype` (logi) [m], `quantity` (deci-2), `amount` (deci-2), `lineno` (inte), `seqnoh` (inte) [i], `unit` (char), `unitconv` (deci-5), `postdt` (date), `binloc` (char[2]), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `ncnr` (char), `eccnclasscd` (char), `postdttz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `icer`
**Receipts File for Back Order Fill**
Fields: `cono` (inte) [i], `whse` (char) [i], `prod` (char) [im], `ordertype` (char) [i], `pono` (inte) [m], `qtyrcvd` (deci-2), `qtyleft` (deci-2), `qtyalloc` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `lineno` (inte), `posuf` (inte), `botype` (char), `proddesc` (char), `proddesc2` (char), `qtypicked` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `processinit` (char) [im], `transproc` (char), `cqtyrcvd` (deci-2), `cqtyleft` (deci-2), `cqtyalloc` (deci-2)

### `icet`
**IC Transaction Entry**
Fields: `cono` (inte) [i], `whse` (char) [im], `prod` (char) [im], `transtype` (char) [i], `module` (char) [i], `postdt` (date) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `stkqtyship` (deci-2), `divno` (inte), `lineno` (inte) [i], `cost` (deci-5), `reasunavty` (char), `transdt` (date), `transtm` (char), `operinit` (char), `mergedfl` (logi) [im], `ticketno` (char), `phyadjexcp` (char), `usageprod` (char) [i], `usagefl` (logi) [im], `jrnlno` (inte) [i], `setno` (inte) [i], `seqno` (inte), `custno` (char), `refer` (char), `icswcost` (deci-5), `qtyunavail` (deci-2), `icspecrecno` (deci-0), `origcost` (deci-5), `usageqty` (deci-2), `apinvno` (char), `usagewhse` (char) [i], `enterdt` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `exchgrate` (deci-7), `notesfl` (char), `notesid` (inte), `srpacklistno` (char), `icspcrowpointer` (char), `enterdttz` (datetm-tz), `postdttz` (datetm-tz), `rowpointer` (char) [i]

### `icetc`
**IC Customer Inventory Transaction Entry**
Fields: `cono` (inte) [i], `whse` (char) [im], `prod` (char) [im], `transtype` (char) [i], `module` (char) [i], `postdt` (date) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `stkqtyship` (deci-2), `divno` (inte), `lineno` (inte) [i], `cost` (deci-5), `reasunavty` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `mergedfl` (logi) [im], `ticketno` (char), `phyadjexcp` (char), `usageprod` (char) [i], `usagefl` (logi) [im], `jrnlno` (inte) [i], `setno` (inte) [i], `seqno` (inte), `icseqno` (inte) [i], `custno` (char), `custprod` (char) [i], `refer` (char), `icswcost` (deci-5), `qtyunavail` (deci-2), `icspecrecno` (deci-0), `origcost` (deci-5), `usageqty` (deci-2), `apinvno` (char), `usagewhse` (char) [i], `enterdt` (date), `exchgrate` (deci-7), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `srpacklistno` (char), `enterdttz` (datetm-tz), `postdttz` (datetm-tz)

### `icetf`
**Inventory Issues**
Fields: `cono` (inte) [i], `prod` (char) [i], `whse` (char) [i], `seqno` (inte) [i], `orderno` (inte), `ordersuf` (inte), `lineno` (inte), `ordertype` (char), `qtyship` (deci-2), `receiptdt` (date), `issuedt` (date) [i], `taxrateau` (deci-2), `taxratepdau` (deci-2), `taxablety` (char), `taxissuedau` (deci-2), `icspecrecno` (deci-0), `creditvalau` (deci-2), `salescostau` (deci-2), `taxpaid` (deci-2), `returncostau` (deci-2), `kitseqno` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `stagecdau` (inte), `user2` (char), `pono` (inte) [im], `user3` (char), `posuf` (inte) [i], `user4` (char), `polineno` (inte) [i], `user5` (char), `src` (char), `user6` (deci-5), `qtycost` (deci-2), `user7` (deci-5), `oeelcost` (deci-5), `user8` (date), `bpfl` (logi) [im], `user9` (date), `transproc` (char), `issuedttz` (datetm-tz), `receiptdttz` (datetm-tz)

### `iceti`
**ImportID Issues**
Fields: `cono` (inte) [i], `prod` (char) [i], `whse` (char) [i], `nonstockty` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `ordertype` (char) [i], `qtyship` (deci-2), `qtyreturn` (deci-2), `compseqno` (inte) [i], `transtype` (char), `importid` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `icseirowpointer` (char) [i], `seqno` (inte) [i], `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icetl`
**IC Lots Transaction**
Fields: `prod` (char) [im], `cono` (inte) [i], `whse` (char) [i], `lotno` (char) [i], `quantity` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `prodcost` (deci-5), `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `qtyunavail` (deci-2), `reasunavty` (char), `returnfl` (logi) [m], `postdt` (date) [i], `price` (deci-5), `whseto` (char), `whsefm` (char), `custno` (deci-0) [m], `slsrepin` (char), `slsrepout` (char), `ictype` (char), `shipto` (char) [m], `qtycosted` (deci-2), `icspecrecno` (deci-0), `updinvfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `postdttz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `icets`
**IC Serial # Transaction File**
**Operators call this:** "Serial Number" (Sales)
Fields: `cono` (inte) [i], `prod` (char) [im], `whse` (char) [i], `serialno` (char) [i], `postdt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `custno` (deci-0) [m], `price` (deci-5), `reasunavty` (char), `seqno` (inte) [i], `whsefm` (char), `whseto` (char), `ordertype` (char) [i], `returnfl` (logi) [m], `prodcost` (deci-5), `ictype` (char), `shipto` (char) [m], `costfl` (logi) [m], `icspecrecno` (deci-0), `updinvfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `postdttz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `icsabc`
**ABC Stratification**
Fields: `cono` (inte) [i], `whse` (char) [i], `stkoan` (char) [i], `relwtsales` (deci-2), `relwtgmroi` (deci-2), `relwthits` (deci-2), `relimpa` (deci-2), `relimpb` (deci-2), `relimpc` (deci-2), `relimpd` (deci-2), `relsprda` (deci-2), `relsprdb` (deci-2), `relsprdc` (deci-2), `relsprdd` (deci-2), `salespcta` (deci-2), `salespctb` (deci-2), `salespctc` (deci-2), `gmroipcta` (deci-2), `gmroipctb` (deci-2), `gmroipctc` (deci-2), `hitspcta` (deci-2), `hitspctb` (deci-2), `hitspctc` (deci-2), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icsc`
**Catalog**
Fields: `vendno` (deci-0) [im], `catalog` (char) [i], `baseprice` (deci-5), `listprice` (deci-5), `prodcost` (deci-5), `unitstock` (char), `prodcat` (char), `prodline` (char) [im], `autotype` (char), `descrip` (char[2]), `weight` (deci-5), `pricetype` (char), `priceonty` (char), `user1` (char), `user2` (char), `notesfl` (char), `cubes` (deci-5), `transdt` (date), `desckey` (char) [i], `prccostper` (char), `speccostty` (char), `csunperstk` (deci-8), `length` (deci-5), `width` (deci-5), `webpageext` (char), `rebsubty` (char), `rebatety` (char), `serlottype` (char), `slgroup` (char), `pbseqno` (inte), `msdschgdt` (date), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `msdssheetno` (char), `termsdiscfl` (logi) [m], `termspct` (deci-2), `stndcost` (deci-5), `transtm` (char), `operinit` (char), `rebatecost` (deci-5), `pctcode` (char), `msdsfl` (logi) [m], `autoupcd` (char), `height` (deci-5), `webpage` (char), `icspecrecno` (inte), `keyindex` (char), `transproc` (char), `longdescrip` (char), `Model` (char), `ThumbnailPic` (char), `catkeyindex` (char[4]) [i], `AuthGrpList` (char), `vendprod` (char), `unitstnd` (char), `documentdescrip` (char), `unspsc` (char), `extprod` (char) [i], `tradename` (char), `corpid` (inte), `param-list` (char), `statustype` (char), `statusdt` (date), `storeid` (inte), `mfg-no` (inte), `node-list` (char), `ecbatchnm` (char) [i], `slchgdt` (date), `descrip3` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `commoditycd` (char), `netmassamt` (deci-5), `usesuppunits` (deci-5), `mfgprod` (char), `brandcode` (char), `acceptoefl` (logi) [m], `inventorystatus` (char), `ncnr` (char), `eccnclasscd` (char), `countryoforigin` (char), `tariffcd` (char), `prodtier` (char), `altprodgrp` (char), `altprodprccd` (char), `prodpreference` (char), `prodtiergrp` (char), `transdttmz` (datetm-tz) [i], `modelcode` (char), `taxweight` (deci-5), `msdschgdttz` (datetm-tz), `slchgdttz` (datetm-tz), `cnpkgtype` (char), `exporepricefl` (logi) [m], `cnmanpackfl` (logi) [m], `cnpckinstruct` (char), `cnpkgrestrictty` (char), `cnpkggrouplist` (char), `cnsizemeasitm` (char), `cnpkgshelfshpfl` (logi) [m]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `catalog` (Catalog Product) — Old Cross Ref length 50 available starting in 6.1.040 Catalog can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Required
- `descrip3` (Extended Description) — Available starting 6.1.040
- `vendno` (Vendor #) — Can be CHAR(24) if using xref; Valid values/xref: APSV
- `prodline` (Product Line) — Can be CHAR(24) if using xref; Valid values/xref: ICSL
- `vendprod` (Vendor Product #) — Vendor Product Number used for Cross Referencing Vendprod can be 50 long only if AO for Expanded Vendor Product is activated starting in 10.3.1
- `unspsc` (UNSPSC Code) — Available Starting 4.0
- `ncnr` (Non Cancellable/ Non Returnable Flag) — Available Starting in 10.0 (Y)es or Blank (means no); Valid values/xref: Y or <blank>
- `prodcat` (Product Category) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-C; Default: DCAOI Default
- `slgroup` (Supplier Group) — Valid values/xref: SLST - SG
- `serlottype` (Extended Type) — (S)erial , (L)ot, or Blank.; Valid values/xref: <Blank>, S or L
- `termsdiscfl` (Terms Discount Flag) — (Y)es for Default Cash Terms or (N)o for Product Specific Cash Terms; Valid values/xref: Y or N; Default: Y
- `termspct` (Terms Discount Percent) — Required if Terms Discount Flag is NO
- `unitstock` (Stocking Unit) — Label for Quantity Units; Default: each
- `unitstnd` (Standard Pack) — See Notes Below. Available Starting 4.0; Valid values/xref: SASTT-U or ICSEU
- `unitconv` (# Units Standard) — See Notes Below
- `unitediuom` (EDI Units Stnd.) — See Notes Below
- `acceptoefl` (Accept OE flag) — Set to Yes to accept catalog use in OE automatically Available Starting in 6.1.080; Valid values/xref: Y or N; Default: N
- `inventorystatus` (Inventory Status) — Allow OE Inventory Creation as (O)AN Stock Only, OAN (N)onstock Only, (X) Neither or blank for Both Available Starting in 6.1.080; Valid values/xref: O, N, X or blank
- `mfgprod` (Manufacturer's Product #) — Available Starting in 6.1.060
- `brandcode` (Brand Code) — Available Starting in 6.1.060; Valid values/xref: SASTT-BC
- `altprodgrp` (Alternate Product Group Code) — Available Starting in 10.2.1.0; Valid values/xref: SASTT-AG
- `eccnclasscd` (Export Control Classification Number) — Available starting in 10.0; Valid values/xref: SASTT-EC
- `prodtier` (Product Tier) — Available starting in 10.1; Valid values/xref: SASTT-TR
- `prodpreference` (Product Preference) — Available starting in 10.3; Valid values/xref: SASTT-PR
- `prodtiergrp` (Product Tier Group) — Available starting in 10.3
- `msdsfl` (MSDS Product) — Valid values/xref: Y or N; Default: N
- `weight` (Weight) — Per Stocking Unit
- `cubes` (Cube) — Per Stocking Unit
- `length` (Length) — Per Stocking Unit
- `width` (Width) — Per Stocking Unit
- `height` (Height) — Per Stocking Unit
- `autotype` (Auto Pricing Type) — Used with PDSA to update price/cost; Valid values/xref: PDSA
- `pricetype` (Product Price Type) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-K
- `priceonty` (Multiplier) — (B)ase, (L)ist or (C)ost; Valid values/xref: B, L or C; Default: B
- `pbseqno` (Price Book Seq#) — Controls Sort of PDRC and PDRP
- `slchgdt` (SL Last Update) — Available Starting 4.1
- `altprodprccd` (Alternate Product Price code) — Available starting 10.2.0
- `speccostty` (Special Price/Cost) — (Y)es, (T)housand, (H)undred or Blank Recommend either "Y" or Blank; Valid values/xref: <Blank>, Y, T or H
- `prccostper` (Price/Cost Unit) — Label for Price/Cost Units. Only required if Speccostty is not blank
- `csunperstk` (Units Per Stk Unit) — Price/Cost Unit Conversion Factor. For example if priced per hunderd 0.01. Only required if Speccostty is not blank
- `rebatety` (Rebate Type) — Valid values/xref: PDST-PT
- `rebsubty` (Rebate Sub Type) — Valid values/xref: PDST-ST
- `countryoforigin` (Country of Origin) — Available Starting in 10.0.1; Valid values/xref: SASTT - W
- `tariffcd` (HS Code) — Available Starting in 10.0.1; Valid values/xref: SASGT
- `commoditycd` (Intrastat Commodity Code) — Used with VAT Only Available Starting 10.0; Valid values/xref: SASTT - CD
- `netmassamt` (Intrastat Net Mass) — Used with VAT Only Available Starting 10.0; Valid values/xref: Required if Commodity code NOT setup in SASTT to use Supp Units
- `usesuppunits` (Intrastat Supplementary Units) — Used with VAT Only Available Starting 10.0; Valid values/xref: Required if Commodity code setup in SASTT to use Supp Units
- `user5` (User5) — Used for Conversion Import ID
- `user10` (User10) — Available starting 6.1.040
- `user11` (User11) — Available starting 6.1.040
- `user12` (User12) — Available starting 6.1.040
- `user13` (User13) — Available starting 6.1.040
- `user14` (User14) — Available starting 6.1.040
- `user15` (User15) — Available starting 6.1.040
- `user16` (User16) — Available starting 6.1.040
- `user17` (User17) — Available starting 6.1.040
- `user18` (User18) — Available starting 6.1.040
- `user19` (User19) — Available starting 6.1.040
- `user20` (User20) — Available starting 6.1.040
- `user21` (User21) — Available starting 6.1.040
- `user22` (User22) — Available starting 6.1.040
- `user23` (User23) — Available starting 6.1.040
- `user24` (User24) — Available starting 6.1.040
- `modelcode` (Model Number) — Valid values/xref: SASTT - Type 'PM'
- `exporepricefl` (Exclude from Auto Vendor Reprice) — Available Starting 11.20.2; Valid values/xref: Y or N; Default: N
- `cnpkgtype` (Package Type) — Available Starting 11.20.6
- `cnmanpackfl` (Manually Pack Item) — Available Starting 11.20.6; Valid values/xref: Y or N; Default: N
- `cnpckinstruct` (Packing Instructions) — Available Starting 11.20.6
- `cnpkgrestrictty` (Packing Restriction) — Available Starting 11.20.6
- `cnpkggrouplist` (Packing Group Type List) — Available Starting 11.20.6
- `cnsizemeasitm` (Size Measurement of Item) — Available Starting 11.20.6
- `cnpkgshelfshpfl` (Self-Ship Unit of Measure) — Available Starting 11.20.6; Valid values/xref: Y or N; Default: N
- `tmsfreightclass` (Transportation Freight Class) — Available Starting 11.21.9

### `icsca`
**Authorization Groups per Product**
Fields: `Cono` (inte) [i], `catalog` (char) [i], `authgrp` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `ecbatchnm` (char) [i]

### `icscg`
**Group Attributes per Product**
Fields: `catalog` (char) [i], `attrno` (inte) [i], `groupno` (inte) [i], `valueno` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `ecbatchnm` (char) [i]

### `icscm`
Fields: `operinit` (char), `transdt` (date), `transtm` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `user1` (char), `user2` (char), `name` (char) [im], `mfgno` (deci-0) [im], `transproc` (char), `mfgnm` (char) [i], `keyindex` (char), `corpid` (inte) [i], `storeid` (inte) [i], `ecbatchnm` (char) [i]

### `icscn`
**Cartonization Setup Packages**
Fields: `cono` (inte) [im], `whse` (char) [im], `pkgid` (char) [im], `descrip` (char), `activefl` (logi) [m], `pkgtype` (char) [i], `pkggroupty` (char), `instructions` (char), `sizemeaspkg` (char), `height` (deci-5), `width` (deci-5), `length` (deci-5), `pkgtarewght` (deci-5), `heightchkfillfl` (logi) [m], `widthchkfillfl` (logi) [m], `lengthchkfillfl` (logi) [m], `nondimenfl` (logi) [m], `minweight` (deci-2), `mincubepct` (deci-2), `maxcubepct` (deci-2), `maxweight` (deci-2), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icscr`
**This table contains catalog restriction profiles that are used by eSales to limit the products that a particular user can view/buy**
Fields: `vendno` (deci-0) [im], `prodline` (char) [m], `cono` (inte) [i], `catalog` (char) [i], `prodcat` (char) [i], `resno` (inte) [i], `resdesc` (char) [i], `shipstate` (char), `custtype` (char), `custno` (deci-0) [im], `activefl` (logi) [im], `operrole` (char), `login` (char), `restype` (char), `shipto` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char)

### `icsd`
**IC Warehouse Master File**
**Operators call this:** "Warehouse Code" (Inventory), "Warehouse Name" (Inventory), "Warehouse Code" (Purchasing), "Warehouse Name" (Purchasing), "Warehouse Code" (Sales), "Warehouse Name" (Sales), "Warehouse Code" (TWL), "Warehouse Name" (TWL), "Warehouse Code" (Warehouse Transfers), "Warehouse Name" (Warehouse Transfers)
Fields: `cono` (inte) [i], `whse` (char) [im], `name` (char) [m], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `divno` (inte), `phoneno` (char), `faxphoneno` (char), `modphoneno` (char), `custno` (deci-0), `zone` (char), `salesfl` (logi) [m], `bondedfl` (logi) [m], `billtowhse` (char), `shipviaty` (char), `shipinstr` (char), `resaleno` (char), `arpvendno` (char), `begpono` (inte), `nextpono` (inte), `endpono` (inte), `begordno` (inte), `nextordno` (inte), `endordno` (inte), `begwono` (inte), `endwono` (inte), `nextwono` (inte), `bofl` (logi) [m], `addondist` (char), `wtkcost` (deci-2), `gldivno` (inte[4]), `wtrcost` (deci-2), `gldeptno` (inte[4]), `invprinternm` (char), `glacctno` (inte[4]), `pkprinternm` (char), `glsubno` (inte[4]), `wllivecd` (char), `transdt` (date), `wlloc` (char), `transtm` (char), `dunsno` (char), `operinit` (char), `region` (char), `vminwks` (inte), `cyccntloc` (char), `reservedays` (inte), `arptype` (char), `arppushfl` (logi) [m], `icrcost` (deci-2), `prinvfl` (logi) [m], `ickcost` (deci-2), `prpickfl` (logi) [m], `approvety` (char), `user3` (char), `site` (char), `user4` (char), `printernm` (char[4]), `user5` (char), `buygroup` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `lastmergedt` (date), `user9` (date), `cyccntprod` (char), `addonamt` (deci-2[2]), `addontype` (char[2]), `oeepboper` (char), `langcd` (char), `enddaycut` (inte), `satfl` (logi) [m], `sunfl` (logi) [m], `statecd` (char), `taxauth` (char), `user1` (char), `user2` (char), `icpcrange` (char), `icpctickfl` (logi[2]) [m], `icpctprtfl` (logi[2]) [m], `icpccprtfl` (logi[2]) [m], `icpcautofl` (logi[2]) [m], `icpctfrmt` (inte[2]), `icpccfrmt` (inte[2]), `icpcshowfl` (logi[2]) [m], `jitdays` (inte), `geocd` (inte), `begrcvno` (inte), `endrcvno` (inte), `nextrcvno` (inte), `bankno` (inte), `gldivno2` (inte[9]), `gldeptno2` (inte[9]), `glsubno2` (inte[9]), `glacctno2` (inte[9]), `location` (char), `countycd` (char), `citycd` (char), `other1cd` (char), `other2cd` (char), `begvano` (inte), `endvano` (inte), `nextvano` (inte), `xxc1` (char), `exclecomm` (char), `xxc6` (char), `autoselwhsefl` (logi) [m], `kitsplbillfl` (logi) [m], `transproc` (char), `branchmgr` (char), `operationsmgr` (char), `regionalmgr` (char), `currencyty` (char), `xxiext9` (inte[9]), `revcycldays` (inte), `partnerid` (char), `esourcebyty` (char), `ecommercety` (char), `reservwknd` (char), `wtrndonlyfl` (logi) [m], `vmaxwks` (inte), `tminwks` (inte), `tmaxwks` (inte), `xxi15` (inte), `addr3` (char), `swaddonno` (inte[4]), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `icpccbinord` (char[2]), `exclmdd` (char), `shipto` (char) [m], `managedfl` (logi) [m], `adjbillablefl` (logi) [m], `custcosttype` (char), `custglcost` (char), `integrityloc` (char), `criticaldays` (inte), `licenseedays` (inte), `custdays` (inte), `shelfdays` (inte), `lotdays` (inte), `sremployee` (char), `srdept` (char), `srproject` (char), `srworkorder` (char), `srmachine` (char), `srchargeno` (char), `printcustlinesfl` (logi) [m], `altwhsefillty` (char), `altwhsebotype` (char), `srprinternm` (char), `autorcvfabwtfl` (logi) [m], `vabacktiefl` (logi) [m], `fabwhsecd` (char), `icnsprodcat` (char), `srautoinv` (char), `srshipbo` (char), `srnoteprnt` (char), `srautorcvwtfl` (logi) [m], `srapprovety` (char), `srwtarpwhse` (char), `srbobillrcptcd` (char), `sremployeename` (char), `spectaxcd` (char), `oebostage` (inte), `boshipcompfl` (logi) [m], `outofcityfl` (logi) [m], `rowpointer` (char) [i], `wordindexfl` (logi) [m], `esbactioncode` (char), `countryoforigin` (char), `priceregion` (char), `srautortninv` (char), `srsaspgroup` (char), `dlvprinternm` (char), `ptxwhsefl` (logi), `holdforintlrvwfl` (logi) [m], `usagemovety` (char), `ibcoeshipdoc` (char), `ibcscanworkflow` (logi) [m], `transdttmz` (datetm-tz) [i], `rentalfl` (logi) [m], `addonmarkupcost` (char), `automrgfl` (logi) [m], `sigreqtype` (char), `cenpossigfl` (logi) [m], `lastmergedttz` (datetm-tz), `taxapplicationid` (char), `addressoverfl` (logi) [m], `cncartonty` (char), `cntrackdtlfl` (logi) [m], `cntrackserlotty` (char), `cninvprintty` (char), `cnasnprintfl` (logi) [m], `cnmixbyshiptofl` (logi) [m], `cnmincubepct` (deci-2), `cnmaxcubepct` (deci-2), `cnsizemeaspkg` (char), `cnusecartonidfl` (logi) [m], `cnctnidpkgtyfl` (logi) [m], `cnctnletterfl` (logi) [m], `cnctnlettercd` (char), `cnctnwhsefl` (logi) [m], `cnctnposwhse` (inte), `cnctnposletter` (inte), `cnctnposctnno` (inte), `cnctnpospkgty` (inte), `cnconfirmshipfl` (logi) [m], `icpcquickfl` (logi) [m], `taxadminname` (char), `taxadminpassword` (char), `taxauthorization` (char), `cnwtdoonlyfl` (logi) [m]

### `icsdd`
**IC Cash Drawers for Warehouse**
Fields: `cono` (inte) [im], `whse` (char) [im], `drawerid` (char) [im], `bankno` (inte), `asgnedopers` (char), `lastrecdttmz` (datetm-tz), `lastamt` (deci-2), `transdttmz` (datetm-tz), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `recinuseoper` (char), `recinusefl` (logi) [m]

### `icsdp`
**IC Warehouse Payment Type**
Fields: `cono` (inte) [i], `whse` (char) [i], `mediacd` (inte) [i], `paybankno` (inte), `merchantid` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `merchantuserid` (char), `merchantuserpw` (char), `allowreloadgiftfl` (logi) [m]

### `icseb`
**Inventory Bundle Status**
Fields: `cono` (inte) [i], `whse` (char) [i], `prod` (char) [im], `bundleid` (char) [i], `bundlestatus` (char) [i], `intype` (char), `pono` (inte), `posuf` (inte), `polineno` (inte), `outtype` (char), `orderno` (inte), `ordersuf` (inte), `oelineno` (inte), `oeseqno` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icsec`
**IC Product Cross Reference**
Fields: `cono` (inte) [i], `rectype` (char) [i], `prod` (char) [im], `altprod` (char) [i], `keyno` (deci-0) [i], `orderqty` (deci-2), `unitsell` (char), `transdt` (date), `transtm` (char), `operinit` (char), `leadtm` (inte), `price` (deci-5), `lastchgdt` (date), `unitbuy` (char), `unitstnd` (char), `custno` (deci-0) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `extprod` (char) [c], `extproddescrip` (char[2]), `addprtinfo` (char), `shipto` (char), `custglacctno` (char), `wordindexfl` (logi) [m], `rowpointer` (char) [i], `sellfirsttype` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `transdttmz` (datetm-tz) [i], `lastchgdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `rectype` (Type) — See Chart Below; Valid values/xref: B, C, H, I, O, P, S, T, U, or V; Required
- `prod` (Product) — See Chart Below Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Required
- `catalog1` — (Y)es if prod is a catalog product setup in ICSC and not setup in ICSP; Valid values/xref: Y or N; Default: Y
- `altprod` (Our Product) — See Chart Below Old Cross Ref length 50 available starting in 6.1.040 Alt Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Required
- `catalog2` — (Y)es if altprod is a catalog product setup in ICSC and not setup in ICSP; Valid values/xref: Y or N; Default: Y
- `keyno` (Key #) — See Chart Below. Can be CHAR(24) for Vendor number if using Vendor Cross Reference; Required
- `custno` (Customer #) — Required For (C)ustomer Prod. Can be CHAR(24) if using Customer Cross Reference; Valid values/xref: ARSC
- `shipto` (Shipto) — Only used with type H; Valid values/xref: ARSS
- `orderqty` (Order Quantity) — For (C)ustomer and S(H)ipto Prod; Default: 1
- `unitsell` (Unit Buy) — For (C)ustomer and S(H)ipto Prod; Valid values/xref: ICSEU or SASTT-U; Default: Stock or Sell Unit
- `unitbuy` (Buying Unit) — For (V)Alt Vendor; Valid values/xref: ICSEU or SASTT-U
- `unitstnd` (Standard Pack) — For (V)Alt Vendor and (B)arcode if using TWL Only; Valid values/xref: ICSEU or SASTT-U
- `price` (Price) — For (V)Alt Vendor, (C)ustomer and S(H)ipto Prod
- `lastchgdt` (Last Change) — For (V)Alt Vendor
- `leadtm` (Lead Time) — For (V)Alt Vendor
- `extprod` (Extended Prod) — Available Starting 4.0
- `extproddescrip1` (Extended Description1) — Available Starting 4.0
- `extproddescrip2` (Extended Description2) — Available Starting 4.0
- `addprtinfo` (Additional Print Info) — Customer Product Information to print on documents. Available Starting 4.1
- `custglacctno` (Customer GL Acct #) — Used for recty C and H only Used with Storeroom Module
- `opposite` (Create Opposite Substitute) — (Y)es to also create opposite Substitute; Valid values/xref: Y or N; Default: N
- `user5` (user5) — Used for Conversion Import ID
- `sellfirsttype` (Sell First Type) — For (S)ubstitute and Su(P)ercede Prod; Valid values/xref: blank,C,R or W
- `Record Type` (Alt Product) — Notes; Valid values/xref: Key# Required?
- `B - Barcode` (SX.e Product ICSP/ICSC) — only one barcode allowed; Valid values/xref: No
- `C - Customer Product` (SX.e Product ICSP/ICSC) — only one customer prod (icsec.prod) per keyno; Valid values/xref: No, Program will assign
- `H - Cust/Shipto Product` (SX.e Product ICSP/ICSC) — only one customer/shipto prod per keyno; Valid values/xref: No, Program will assign
- `I - Interchange` (SX.e Product ICSP/ICSC) — unlimited; Valid values/xref: No, Program will assign
- `O - Options` (Optional Product ICSP/ICSC) — unlimited; Valid values/xref: No, Program will assign
- `P - Superseded` (New Product ICSP/ICSC) — only one per superceded product; Valid values/xref: No, Program will assign
- `S - Substitute` (Substitute Product ICSP/ICSC) — unlimited; Valid values/xref: No, Program will assign
- `T - Auto Pricing` (SX.e Product ICSP/ICSC) — Used with Supplier Link Module; Valid values/xref: Can be zero or must match SLSI record #
- `U - Upgrade` (Upgrade Product ICSP/ICSC) — unlimited; Valid values/xref: No, Program will assign
- `V - Alt Vendor` (Vendor's Product Number) — only one per prod per vendor; Valid values/xref: Yes

### `icsecw`
**IC Vendor Product Warehouse**
Fields: `cono` (inte) [im], `rectype` (char) [im], `operinit` (char), `transdttmz` (datetm-tz), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `icsecrowpointer` (char) [im], `srcrowpointer` (char) [im]

### `icsee`
**Extended product info exceptions**
Fields: `cono` (inte) [im], `custno` (deci-0) [im], `shipto` (char) [im], `prod` (char) [im], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icsef`
**Fifo Master**
Fields: `cono` (inte) [i], `whse` (char) [i], `prod` (char) [i], `availfl` (logi) [im], `seqno` (inte) [i], `quantity` (deci-2), `prodcost` (deci-5), `transdt` (date), `transtm` (char), `operinit` (char), `receiptdt` (date) [i], `pono` (inte) [im], `posuf` (inte) [i], `lineno` (inte) [i], `costedfl` (logi), `taxamt` (deci-2), `statustype` (char) [i], `ordertype` (char), `origqty` (deci-2), `kitseqno` (inte), `origcost` (deci-5), `addoncost` (deci-5), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `receiptdttz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `whse` (Warehouse) — Can be CHAR(24) if using xref; Valid values/xref: ICSD; Required
- `availfl` (Available for Sale) — (Y)es or (N)o; Valid values/xref: Y or N; Required
- `seqno` (Seq#) — See Notes Below; Required; Default: 001
- `quantity` (Quantity Available) — All Available FIFO Qty for Prod/Whse should sum to the ICSW Qty On Hand; Required
- `addoncost` (Addon Cost) — Only used with Capitalized Addons
- `costedfl` (Costed) — Processed in AP (Y)es or (N)o; Valid values/xref: Y or N; Default: No
- `taxamt` (Tax Amount) — Only used in Austraila
- `statustype` (Status Type) — (A)ctive if Qty > 0 or (I)nactive if Qty = 0; Valid values/xref: A or I; Default: A
- `pono` (PO #) — Order # of Receipt that created Layer
- `posuf` (PO Suffix) — Suffix for Receipt
- `lineno` (Line#) — Line # for Receipt
- `ordertype` (Order Type) — (I)nv Control,(O)rder Entry, (P)urchase Order, Whse (T)ransfer
- `origqty` (Original Quantity) — Original Receipt Qty; Default: Qty Avail
- `origcost` (Original Cost) — Original Receipt Cost; Default: Cost
- `kitseqno` (Kit Seq#) — Kit Seq for Receipt
- `user5` (user5) — Used for Conversion Import ID

### `icseg`
**IC GL Distribution**
Fields: `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `accttype` (logi) [im], `disttype` (inte) [i], `key1` (char) [i], `key2` (char) [i], `gldivno` (inte[20]), `gldeptno` (inte[20]), `glacctno` (inte[20]), `glsubno` (inte[20]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `rowpointer` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `accttype` (Account Type) — (B)alance or (I)ncome; Valid values/xref: B or I; Required
- `key1` (Key1) — See chart below
- `key2` (Key2) — See chart below
- `gldivno1 - 20` (GL Division #) — See chart 2 below; Valid values/xref: GLSA
- `gldeptno1 - 20` (GL Department #) — See chart 2 below; Valid values/xref: GLSA
- `glacctno1 - 20` (GL Account #) — See chart 2 below; Valid values/xref: GLSA
- `glsubno1 - 20` (GL Sub Acct #) — See chart 2 below; Valid values/xref: GLSA
- `user5` (user5) — Used for Conversion Import ID
- `GL #` (Columns) — Balance Contents; Valid values/xref: Income Contents
- `1` (D-G) — Inventory
- `2` (H-K) — Uninvoiced Inventory
- `3` (L-O) — Core Charge
- `4` (P-S) — WIP inventory; Valid values/xref: Gross Sales
- `5` (T-W) — WIP Write-off; Valid values/xref: Line Discount
- `6` (X-AA) — Valid values/xref: Order Discount
- `7` (AB-AE) — Customer Core Due; Valid values/xref: Cost of Goods
- `8` (AF-AI) — Valid values/xref: Restock Charge
- `9` (AJ-AM) — Direct Inventory
- `10` (AN-AQ) — Valid values/xref: Direct Sales
- `11` (AR-AU) — Tally Variance; Valid values/xref: Direct Cost of Sales
- `12` (AV-AY) — Customer Core Liab; Valid values/xref: COG Adjustment
- `13` (AZ-BC) — Core Variance; Valid values/xref: WT Cost Adjust
- `14` (BD-BG) — IC Cost Adjustment; Valid values/xref: Core Conversion
- `15` (BH-BK) — Non-Stock Inventory
- `16` (BL-BO) — Physical Adjustment
- `17` (BP-BS) — Vendor Core Liab; Valid values/xref: Rebate Cost Adjust
- `18` (BT-BW) — Rebate Due
- `19` (BX-CA) — Valid values/xref: Sales Returns
- `20` (1) — 1200; Valid values/xref: 20; Default: 2010

### `icseh`
**Hazardous Materials Sheet Info**
Fields: `msdssheetno` (char) [i], `hazardrank` (inte), `operinit` (char), `transdt` (date), `transtm` (char), `langcd` (char) [i], `noteln1` (char[16]), `noteln2` (char[16]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `icsei`
**Import Master**
*Inventory extended information per item.*
Fields: `cono` (inte) [i], `whse` (char) [i], `prod` (char) [i], `importid` (char), `primarykeydt` (date) [i], `secondarykeydt` (date) [i], `seqno` (inte) [i], `importidpos1` (char), `importidpos2` (char), `importidpos3` (char), `importiddelim` (char), `nonstockty` (char) [i], `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `quantity` (deci-2), `origquantity` (deci-2), `statustype` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `wordindexfl` (logi) [m], `rowpointer` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `primarykeydttz` (datetm-tz), `secondarykeydttz` (datetm-tz)

### `icsel`
**Lot Master**
Fields: `prod` (char) [im], `cono` (inte) [i], `whse` (char) [i], `lotno` (char) [i], `opendt` (date) [i], `closedt` (date), `qtyavail` (deci-2), `binloc` (char[2]), `transdt` (date), `transtm` (char), `operinit` (char), `prodcost` (deci-5), `expiredt` (date), `qtyunavail` (deci-2), `statustype` (char) [i], `jrnlno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `rowpointer` (char) [i], `closedttz` (datetm-tz), `expiredttz` (datetm-tz), `opendttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSW; Required
- `whse` (Warehouse) — Can be CHAR(24) if using xref; Valid values/xref: ICSD; Required
- `lotno` (Lot ID) — One Record per Lot ID per Product per Warehouse; Required
- `statustype` (Status) — (A)ctive, (I)nactive or (H)old; Valid values/xref: A, I or H; Default: A
- `qtyavail` (Qty Available) — All Lots for Prod/Whs should sum to ICSW Qty On Hand
- `qtyunavail` (Qty Unavailable) — All Lots for Prod/Whs should sum to ICSW Qty Unavailable
- `prodcost` (Product Cost) — Must include if using AO Roll SN/Lot = Yes
- `user5` (user5) — Used for Conversion Import ID

### `icselc`
**Lot Cut Pieces**
Fields: `cono` (inte) [im], `srcrowpointer` (char) [im], `seqno` (inte) [im], `statustype` (char) [i], `conditioncd` (char), `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `ordseqno` (inte) [i], `quantity` (deci-2), `length1` (deci-5), `length2` (deci-5), `length3` (deci-5), `width1` (deci-5), `width2` (deci-5), `width3` (deci-5), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `srcorderty` (char) [i], `srcorderno` (inte) [i], `srcordersuf` (inte) [i], `srclineno` (inte) [i], `reasunavty` (char)

### `icsep`
**Inventory levels for Physical Count**
Fields: `cono` (inte) [i], `whse` (char) [i], `prod` (char) [im], `qtyexp` (deci-2), `qtycnt` (deci-2), `serlotfl` (logi) [m], `binloc` (char) [i], `runno` (inte) [i], `createdt` (date), `operinit` (char), `transdt` (date), `transtm` (char), `seqno` (inte), `cost` (deci-5), `wmfl` (logi) [m], `refer` (char), `unit` (char), `entfl` (logi) [m], `phyfl` (logi) [m], `icspecrecno` (inte), `createfl` (logi) [m], `lastcntdt` (date), `rectype` (char), `mustcntfl` (logi) [m], `serlotty` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `custcost` (deci-5), `custqty` (deci-2), `custqtyunavail` (deci-2), `esbcountfl` (logi) [m], `inventoryty` (char), `createdttz` (datetm-tz), `lastcntdttz` (datetm-tz)

### `icsepa`
**Physical Count Archive**
Fields: `cono` (inte) [i], `whse` (char) [i], `runno` (inte) [i], `binloc` (char) [i], `cost` (deci-5), `createdt` (date), `custcost` (deci-5), `custqty` (deci-2), `custunavail` (deci-2), `custprod` (char), `icspecrecno` (inte), `invadjustty` (char) [i], `jrnlno` (inte), `orderno` (inte), `phyfl` (logi) [m], `prod` (char) [i], `qtycnt` (deci-2), `qtyexp` (deci-2), `rectype` (char), `refer` (char), `seqno` (inte), `serlotty` (char), `setno` (inte), `unit` (char), `updatedt` (date) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `createdttz` (datetm-tz), `updatedttz` (datetm-tz)

### `icseps`
**Serial/Lot File For Physical Count**
Fields: `cono` (inte) [i], `whse` (char) [i], `runno` (inte) [i], `serlotty` (char), `serialno` (char) [i], `prod` (char) [i], `quantity` (deci-2), `incfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `unavailfl` (logi) [im], `opendt` (date), `expiredt` (date), `binloc` (char), `comment` (char), `expiredttz` (datetm-tz), `opendttz` (datetm-tz)

### `icses`
**IC Serial # Master**
Fields: `cono` (inte) [i], `prod` (char) [im], `whse` (char) [i], `serialno` (char) [i], `receiptdt` (date) [i], `vendno` (deci-0) [m], `invoicedt` (date), `unavaildt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `orderno` (inte), `ordersuf` (inte), `lineno` (inte), `custno` (deci-0) [m], `price` (deci-5), `user1` (char), `ordertype` (char), `user2` (char), `user3` (char), `currstatus` (char) [i], `user4` (char), `comment` (char), `user5` (char), `reasunavty` (char), `user6` (deci-5), `cost` (deci-5), `user7` (deci-5), `seqno` (inte), `user8` (date), `user9` (date), `whsefm` (char), `whseto` (char), `binloc` (char), `reservefl` (logi) [m], `retindt` (date), `jrnlno` (inte), `shipto` (char) [m], `wexpdt` (date), `invno` (inte), `invsuf` (inte), `invlineno` (inte), `fppaidfl` (logi) [m], `transproc` (char), `rettransty` (char), `retorderno` (inte), `retordersuf` (inte), `retlineno` (inte), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `invoicedttz` (datetm-tz), `receiptdttz` (datetm-tz), `retindttz` (datetm-tz), `unavaildttz` (datetm-tz), `wexpdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSW; Required
- `whse` (Warehouse) — Can be CHAR(24) if using xref; Valid values/xref: ICSD; Required
- `serialno` (Serial #) — One Record per Serial Number per Product per Warehouse. Need same number of serial records as ICSW Qty on Hand and Qty Unavailable.; Required
- `currstatus` (Stage) — (A)vailable, (U)navailable, (S)old, (R)etired, or (D)O; Valid values/xref: A, U, S, R or D; Required
- `vendno` (Vendor #) — Received from Vendor. Can be CHAR(24) if using Vendor Cross Reference; Valid values/xref: APSV
- `fppaidfl` (FloorPlan Vendor Paid) — Valid values/xref: Y or N; Default: N
- `custno` (Customer #) — Sold To Customer, only used if Stage is Sold. Can be CHAR(24) if using Customer Cross Reference; Valid values/xref: ARSC
- `shipto` (Ship to) — Sold To Shipto, only used if Stage is Sold; Valid values/xref: ARSS
- `invno` (Invoice #) — Sold to Invoice #, only used if Stage is Sold Uses DCAOO Closed Order # Prefix
- `invsuf` (Suffix) — Sold to Suffix #, only used if Stage is Sold
- `invlineno` (Line #) — Sold to Line #, only used if Stage is Sold
- `invoicedt` (Invoice Date) — Only used if Stage is Sold
- `price` (Invoice Price) — Only used if Stage is Sold
- `wexpdt` (Warranty Expiration Date) — Only used if Stage is Sold
- `user5` (user5) — Used for Conversion Import ID

### `icsesf`
**Inventory Control Serial Formatting Table**
Fields: `cono` (inte) [im], `vendno` (int6) [im], `rectype` (char) [im], `position` (inte) [im], `data` (char) [im], `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icsess`
**Inventory Control Setup Extended Serial Structure**
Fields: `cono` (inte) [im], `vendno` (deci) [im], `rectype` (char) [im], `position` (inte) [im], `data` (char) [im], `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icset`
**Inventory Ticket file**
Fields: `cono` (inte) [i], `whse` (char) [i], `prod` (char) [im], `qtycnt` (deci-2), `cntoper` (char), `runno` (inte) [i], `binloc` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `ticketno` (inte) [i], `wmfl` (logi) [m], `entfl` (logi) [m], `unit` (char), `createfl` (logi) [m], `rectype` (char), `uticketno` (inte) [i], `ibcntupdtfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `uncounttype` (char)

### `icseu`
**IC Unit Conversions**
Fields: `cono` (inte) [i], `prod` (char) [im], `units` (char) [i], `unitconv` (deci-5), `transdt` (date), `transtm` (char), `operinit` (char), `descrip` (char), `unitediuom` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `wordindexfl` (logi) [m], `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `cncalcpkgsizefl` (logi) [m], `cnsizemeasuom` (char), `cnpkgtype` (char), `cnpkgheight` (deci-5), `cnpkgwidth` (deci-5), `cnpkglength` (deci-5), `cnpkgtareweight` (deci-5), `cnpkgcube` (deci-5), `cnpkgshelfshpfl` (logi) [m]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `units` (Unit of Measure) — Label for Unit (i.e. CRTN); Required
- `descrip` (Description) — Description of Unit (i.e. CARTON of 24); Required
- `unitconv` (Unit Conversion Factor) — # Stocking Units in this Unit (i.e. 24); Required
- `user5` (user5) — Used for Conversion Import ID

### `icsev`
**IC Lifo Valuation**
Fields: `cono` (inte) [i], `lifocat` (char) [i], `layer` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `lifoindex` (deci-2), `yr` (inte) [i], `currval` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `yrtz` (datetm-tz)

### `icsew`
**IC Warehouse Auto Transfer**
Fields: `cono` (inte) [i], `whse` (char) [i], `whse2` (char) [i], `transdt` (date), `transtm` (char), `comment` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `icsg`
**Catalog Groups**
Fields: `descrip` (char) [i], `hierarchyfl` (logi), `unspcfl` (logi), `unspcno` (inte), `langcd` (char) [i], `groupno` (inte) [i], `link` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `authgrplist` (char), `corpid` (inte) [i], `storeid` (inte) [i], `statustype` (char), `statusdt` (date), `ecbatchnm` (char) [i], `statusdttz` (datetm-tz)

### `icsga`
**Catalog Group Attributes**
Fields: `attrno` (inte) [i], `descrip` (char) [i], `groupno` (inte) [i], `link` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `ecbatchnm` (char) [i]

### `icsgk`
**Catalog Group Keys - This table serves a dual purpose. The first purpose is to create an environment in which a store can easily add products to a branch of a tree or create a branch without having to know the specific nodeid for that node on the tree. This will be accomplished by using a tag that is specific to each store or by using a product which has already been placed on the tree as a reference product. The second purpose is to allow us to report on and manage the store specific tree structure.**
Fields: `corpid` (inte) [i], `storeid` (inte) [i], `tag` (char) [i], `tag-type` (char) [i], `tagno` (inte) [i], `reference-prod` (char) [i], `reference-pcat` (char) [i], `level1` (char) [i], `level2` (char) [i], `level3` (char) [i], `level4` (char) [i], `level5` (char) [i], `level6` (char) [i], `level7` (char) [i], `level8` (char) [i], `level9` (char) [i], `level10` (char) [i], `gav` (char) [i], `nodeid` (inte) [i], `link` (char), `authgrplist` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `statustype` (char), `statusdt` (date), `ecbatchnm` (char) [i], `statusdttz` (datetm-tz)

### `icsgn`
**Catalog Group Nodes - This table is used to sequence and store each individual catalog node id. Each catalog level or branch is represented via a unique node id.**
Fields: `corpid` (inte) [i], `storeid` (inte) [i], `nodeid` (inte) [i], `groupno` (inte) [i], `gav` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `statustype` (char), `statusdt` (date), `ecbatchnm` (char) [i], `nodekey` (char) [i], `statusdttz` (datetm-tz)

### `icsgr`
**Catalog Group Rules**
Fields: `groupno` (inte) [i], `parentattrno` (inte) [i], `childattrno` (inte) [i], `parentvalueno` (inte) [i], `childvalueno` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `ecbatchnm` (char) [i]

### `icsgs`
**Catalog Synonyms**
Fields: `wordfrom` (char) [i], `wordto` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `ecbatchnm` (char) [i]

### `icsgv`
**Catalog Group Values**
Fields: `attrno` (inte) [i], `descrip` (char) [i], `unspcno` (inte) [i], `groupno` (inte) [i], `valueno` (inte) [i], `link` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `nodeid` (inte) [i], `key-literal` (char) [i], `ecbatchnm` (char) [i], `prodlevel` (logi)

### `icsl`
**IC Prod Line Master**
*Inventory stock ledger. Quantities on hand by warehouse and product. Key for availability queries.*
**Operators call this:** "Product Line Code" (Inventory), "Product Line Name" (Inventory), "Product Line Code" (Sales), "Product Line Name" (Sales)
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `prodline` (char) [i], `descrip` (char), `shipfmno` (inte), `minbuy` (deci-2), `minbuytype` (char), `tarbuytype` (char), `tarlevel` (inte), `operinit` (char), `transdt` (date), `transtm` (char), `discmult` (deci-4[9]), `whse` (char) [i], `buyer` (char), `revcyclin` (inte), `revcyclout` (inte), `frozenfl` (logi) [m], `lastpowtdt` (date), `rcvtolpct` (deci-2), `tarbuyamt` (deci-2[9]), `seasbegmm` (inte), `seasendmm` (inte), `class` (inte), `frozenmos` (inte), `frozentype` (char), `nodaysseas` (inte), `icrcost` (deci-2), `ordcalcty` (char), `trendpct` (deci-2), `orderpt` (deci-0), `ordqtyin` (deci-0), `ordqtyout` (deci-0), `xxc3` (char), `overreasin` (char), `frtconsldtcd` (char), `overreasout` (char), `unitwt` (char), `safeallamt` (deci-0), `updtsrc` (char), `troqfl` (logi) [m], `vminwks` (inte), `unitbuy` (char), `vmaxwks` (inte), `unitstnd` (char), `linept` (deci-0), `leadtmavg` (inte), `usgmths` (inte), `vroqfl` (logi) [m], `safeallpct` (deci-0), `automrgfl` (logi) [m], `termsdiscfl` (logi) [m], `user1` (char), `termspct` (deci-2), `user2` (char), `warrlength` (inte), `user3` (char), `warrtype` (char), `user4` (char), `arptype` (char), `user5` (char), `arppushfl` (logi) [m], `user6` (deci-5), `nontaxtype` (char), `user7` (deci-5), `tariffcd` (char), `user8` (date), `taxablety` (char), `user9` (date), `taxgroup` (inte), `taxtype` (char), `arpwhse` (char), `conslinefl` (logi) [m], `conswhsefl` (logi) [m], `transproc` (char), `safeallty` (char) [m], `vendcorechgfl` (logi) [m], `zerocstcorefl` (logi) [m], `zerocstgldivno` (inte), `zerocstgldeptno` (inte), `zerocstglacctno` (inte), `zerocstglsubno` (inte), `esourcety` (char), `esspecnsty` (char), `rrarunitrnd` (char), `ickcost` (deci-2), `wtrcost` (deci-2), `wtkcost` (deci-2), `rolloanusagefl` (logi) [m], `tminwks` (inte), `tmaxwks` (inte), `wtrevcycle` (inte), `usagerate` (deci-2), `belowlpfl` (logi) [m], `freightexpectedty` (char), `surplusty` (char), `countryoforigin` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `usagectrl` (char), `prodpreference` (char), `transdttmz` (datetm-tz) [i], `lastpowtdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `vendno` (Vendor #) — Can be CHAR(24) if Using Vendor Cross Reference; Valid values/xref: APSV; Required
- `whse` (Warehouse) — Can be CHAR(24) if using xref; Valid values/xref: ICSD; Required
- `prodline` (Product Line) — Can be CHAR(24) if using xref; Valid values/xref: Not Blank; Required
- `shipfmno` (Ship From) — Default PO Address Info for Product Line; Valid values/xref: APSS
- `buyer` (Buyer) — Can be CHAR(24) if using xref; Valid values/xref: SASTT - B; Required; Default: DCAOI
- `rcvtolpct` (Remaining Quantity on PO) — Cancel PO Line Quantities not received if below this Pecrentage. Ex 2.00 for 2%.
- `belowlpfl` (Order Below Line Point) — (Y)es or (N)o, Available Starting 4.3; Valid values/xref: Y or N; Default: N
- `conslinefl` (Consolidate Lines) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `conswhsefl` (Consolidate Warehouses) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `automrgfl` (Auto Merge Flag) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `frozenfl` (Frozen Review) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `rrarunitrnd` (RRAR Unit Rounding Flag) — Blank for 1/2 Standard Pack Rule, (U)p to always round up to next Standard Pack. Available Starting 4.1; Valid values/xref: <Blank> or U
- `seasbegmm` (Season Begin) — Period that begins Season; Valid values/xref: 0 - 12; Default: 0
- `seasendmm` (Season End) — Period that ends Season; Valid values/xref: 0 - 12; Default: 0
- `wtrevcycle` (WT Review Cycle Days) — Available Starting 4.1
- `lastpowtdt` (Last Review Date) — Last Date of PO for Product Line
- `minbuy` (Minimum Buy Amount) — Min Order Required by Vendor
- `minbuytype` (Minimum Buy Type) — (Q)uantity,(W)eight,(D)ollars,(C)ubes; Valid values/xref: Q, W, D or C; Default: D
- `trendpct` (Trend Percentage) — Used with Trend % Usage Method
- `tarbuytype` (Target Type) — (Q)uantity,(W)eight,(D)ollars,(C)ubes; Valid values/xref: Q, W, D or C; Default: D
- `tarlevel` (Target Buy Level) — Target Level to Buy in RRAR; Valid values/xref: 1-9; Default: 1
- `frtconsldtcd` (Freight Conolidation) — Available Starting 4.0; Valid values/xref: SASTT FC
- `vendcorechgfl` (Vendor Core Charge) — (Y)es or (N)o. Available Starting 3.2; Valid values/xref: Y or N; Default: N
- `zerocstcorefl` (Zero Cost Core) — (Y)es or (N)o. Available Starting 3.2; Valid values/xref: Y or N; Default: N
- `zerocstgldivno` (Zero Cost Core Div#) — Available Starting 3.2; Valid values/xref: GLSA
- `zerocstglacctno` (Zero Cost Core Acct#) — Available Starting 3.2; Valid values/xref: GLSA
- `zerocstgldeptno` (Zero Cost Core Dept#) — Available Starting 3.2; Valid values/xref: GLSA
- `zerocstglsubno` (Zero Cost Core Sub#) — Available Starting 3.2; Valid values/xref: GLSA
- `esourcety` (eSource) — Type products sent to eSource: (S)pecial Only, (N)on-stock Only, (B)oth special & non-stock, st(O)ck Only, (A)ll or blank for None. Available Starting 4.0; Valid values/xref: <Blank>, S, N, B, O or A
- `tarbuyamt1` (Target Buy 1) — Enter as Dollar, Weight, Cube or Unit based on Target Buy Type
- `discmult1` (Discount 1) — Enter as Discount Percent Earned for Reaching Target Buy Level. Ex. 10.00 for 10% discount
- `ickcost` (Vendor Carrying Cost) — K Value for ARP Vendor. Available Starting 4.1
- `icrcost` (Vendor Replenishment Cost) — R Value for ARP Vendor. Available Starting 4.1
- `vminwks` (Vendor Min Weeks Supply) — For EOQ. Available Starting 4.1
- `vmaxwks` (Vendor Max Weeks Supply) — For EOQ. Available Starting 4.1
- `vroqfl` (Use ROQ for Vendor ARP) — Always Order Up to Line Point. Available Starting 4.1; Valid values/xref: Y or N; Default: N
- `wtkcost` (Warehouse Carrying Cost) — K Value for ARP Whse. Available Starting 4.1
- `wtrcost` (Warehouse Replenishment Cost) — R Value for ARP Whse. Available Starting 4.1
- `tminwks` (Warehous Min Weeks Supply) — For EOQ. Available Starting 4.1
- `tmaxwks` (Warehouse Max Weeks Supply) — For EOQ. Available Starting 4.1
- `troqfl` (Use ROQ for Warehouse ARP) — Always Order Up to Line Point. Available Starting 4.1; Valid values/xref: Y or N; Default: N
- `unitbuy` (Buying Unit) — New Product Defaults
- `unitstnd` (Standard Pack) — New Product Defaults
- `unitwt` (Transfer Unit) — New Product Defaults
- `class` (Product Class) — New Product Defaults; Valid values/xref: 1-13; Default: 1
- `safeallty` (Safety Allowance Type) — New Product Defaults; Valid values/xref: %,(Q)ty,(D)ays; Default: %
- `safeallamt` (Safety Allowance Qty) — New Product Defaults; Default: 50
- `ordcalcty` (Order Method) — New Product Defaults; Valid values/xref: (E)OQ,(C)lass,(M)in/Max,(Q)uantity Break,(B)lanket Order or (H)uman; Default: C
- `orderpt` (Order Point/Min) — New Product Defaults
- `ordqtyin` (Order Qty) — New Product Defaults
- `linept` (Line Point/Max) — New Product Defaults
- `overreasin` (Override Reason) — New Product Defaults; Valid values/xref: SASTT O
- `usgmths` (Usage Months) — New Product Defaults; Valid values/xref: 1-12; Default: 6
- `surplusty` (Surplus Type) — Available Starting 6.1; Valid values/xref: (I)CSW Usage Rate, (A)ctual Monthly Usage or <Blank>
- `freightexpectedty` (Freight Expected Type) — Available Starting 6.1; Valid values/xref: (Y)es or (N)o; Default: Y
- `rolloanusagefl` (Roll Up OAN Usage) — Available Starting 6.0; Valid values/xref: (Y)es or (N)o; Default: N
- `usagectrl` (Usage Calculation Method) — Available Starting 10.2.1.0 (F)orward, (B)ackward, (T)rend %, (D)emand Planning, (1)-(9) Alpha Factor, or Blank; Valid values/xref: <Blank>, F, B, T, D,1, 2, 3, 4, 5, 6, 7, 8, or 9 D requires License Key for Demand Planning
- `frozentype` (Frozen Reason) — New Product Defaults; Valid values/xref: SASTT F; Default: DCAOI
- `frozenmos` (Frozen Months) — New Product Defaults; Default: DCAOI
- `arptype` (Authorized Replenishment Path) — New Product Defaults; Valid values/xref: (V)endor,(W)arehouse,(C)entral,(K)it,Vendor (M)anaged,(F)abrication or <Blank>
- `arppushfl` (Push) — New Product Defaults; Valid values/xref: (Y)es or (N)o; Default: N
- `arpwhse` (ARP Whse) — New Product Defaults. Can be CHAR(24) if using xref; Valid values/xref: ICSD
- `prodpreference` (Product Preference) — Available starting 10.3; Valid values/xref: SASTT - PR
- `warrlength` (Length of Warranty) — New Product Defaults
- `warrtype` (Warranty Period) — New Product Defaults; Valid values/xref: (M)onths,(D)ays or (Y)ears; Default: M
- `ordqtyout` (Order Qty) — New Product Defaults
- `overreasout` (Override Reason) — New Product Defaults; Valid values/xref: SASTT O
- `nodaysseas` (Review Days) — New Product Defaults
- `leadtmavg` (Avg Lead Time) — New Product Defaults
- `termsdiscfl` (Terms Disc) — Valid values/xref: (Y)es or (N)o; Default: Y
- `taxtype` (Tax Exempt Type) — New Product Defaults - Used with SASGE for Variable Customers
- `taxgroup` (Tax Group) — Valid values/xref: 1-5 or SASTN-TG Record; Default: 1
- `taxablety` (Taxable Type) — Valid values/xref: (Y)es,(N) or (V)ariable; Default: V
- `nontaxtype` (Non Tax Reason) — Valid values/xref: SASTT N; Default: DCAOI
- `tariffcd` (HS Code) — Valid values/xref: SASGT
- `countryoforigin` (Country of Origin) — Available Starting in 10.0.1; Valid values/xref: SASTT W
- `user5` (User5) — Used for Conversion Import ID

### `icsoc`
**Customer Core Expiration Table**
Fields: `cono` (inte) [i], `levelcd` (inte) [i], `custno` (deci-0) [i], `custtype` (char) [i], `pricetype` (char) [i], `whse` (char) [i], `daymo` (inte), `daymofl` (logi) [m], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `begindt` (date), `enddt` (date), `shipto` (char) [i], `transproc` (char), `begindttz` (datetm-tz)

### `icsoe`
**Environmental Handling Fee Exemptions**
Fields: `cono` (inte) [im], `arsrcrowpointer` (char) [im], `state` (char) [im], `addonno` (inte) [im], `icsrcrowpointer` (char) [im], `startdt` (date) [im], `enddt` (date) [i], `certificate` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icsou`
**Warehouse Products Unavailable**
Fields: `cono` (inte) [i], `whse` (char) [im], `prod` (char) [im], `reasunavty` (char) [i], `qtyunavail` (deci-2), `enterdt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user5` (char), `user4` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `custqtyunavail` (deci-2), `enterdttz` (datetm-tz)

### `icsp`
**R&D Products**
**Operators call this:** "Product Name" (Inventory), "Description 2" (Inventory), "Description 3" (Inventory), "Product Category" (Inventory), "Product Code" (Inventory), "Product Name" (Purchasing), "Description 2" (Purchasing), "Product Category" (Purchasing), "Product Name" (Sales), "Description 2" (Sales), "Product Category" (Sales), "Product Code" (Sales), "Product Name" (Warehouse Transfers), "Description 2" (Warehouse Transfers), "Product Category" (Warehouse Transfers)
Fields: `cono` (inte) [i], `prod` (char) [im], `lookupnm` (char) [i], `prodcat` (char), `transdt` (date), `transtm` (char), `operinit` (char), `unitsell` (char), `unitcnt` (char), `unitstock` (char), `weight` (deci-5), `cubes` (deci-5), `corecharge` (deci-2), `msdsfl` (logi) [m], `msdschgdt` (date), `webpageext` (char), `webpage` (char), `warrlength` (inte), `warrtype` (char), `unitconvfl` (logi) [m], `descrip` (char[2]), `enterdt` (date), `statustype` (char) [i], `notesfl` (char), `kittype` (char) [i], `kitrollty` (char), `exponinvfl` (logi) [m], `nospecrecno` (inte), `lifocat` (char), `msdssheetno` (char), `pbseqno` (inte), `sellmult` (inte), `seqno` (inte) [i], `length` (deci-5), `termsdiscfl` (logi) [m], `termspct` (deci-2), `user1` (char), `user2` (char), `tiedcompprt` (char), `bolclass` (char), `edicd` (char), `slgroup` (char), `priceonty` (char), `icspecrecno` (inte), `width` (deci-5), `oespecrecno` (inte), `height` (deci-5), `kitnsreqfl` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `autoupcd` (char), `keyindex` (char), `transproc` (char), `reqbundleidfl` (logi) [m], `randommixfl` (logi) [m], `memomixfl` (logi) [m], `implyqty` (inte), `bodtransferty` (char), `prodtype` (char), `impliedcoreprod` (char) [i], `dirtycoreprod` (char) [i], `vendcoregrcfl` (logi) [m], `custcoregrcfl` (logi) [m], `vendgraceper` (inte), `custgraceper` (inte), `certifiedtype` (char), `xxc14` (char), `volinfofl` (logi) [m], `slchgdt` (date), `tallyunit` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `cfgkitfl` (logi) [m], `cfgruleset` (char), `cfgapplicationid` (char), `cfgnamespace` (char), `cutnumparts` (inte), `cutparttype1` (logi) [m], `cutpartunit1` (char), `cutparttype2` (logi) [m], `cutpartunit2` (char), `cutpartincr2` (inte), `descrip3` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `commoditycd` (char), `netmassamt` (deci-5), `usesuppunits` (deci-5), `mfgprod` (char), `brandcode` (char), `vaassemblyty` (char), `vacutofflength` (deci-5), `unitvaassembly` (char), `ncnr` (char), `countryoforigin` (char), `eccnclasscd` (char), `esbactioncode` (char), `tariffcd` (char), `prodtier` (char), `altprodgrp` (char), `unspsc` (char), `altprodprccd` (char), `cuttype` (char), `dimlengthparts` (inte), `dimlengthty1` (char), `dimlengthty2` (char), `dimlengthunit1` (char), `dimlengthunit2` (char), `dimlengthincr` (deci-5), `dimwidthparts` (inte), `dimwidthty1` (char), `dimwidthty2` (char), `dimwidthunit1` (char), `dimwidthunit2` (char), `dimwidthincr` (deci-5), `prodtiergrp` (char), `prodpreference` (char), `transdttmz` (datetm-tz) [i], `rentprodcat` (char), `modelcode` (char), `taxweight` (deci-5), `enterdttz` (datetm-tz), `msdschgdttz` (datetm-tz), `slchgdttz` (datetm-tz), `cnpkgtype` (char), `exporepricefl` (logi) [m], `catchweightfl` (logi) [m], `cnmanpackfl` (logi) [m], `oecatchweightfl` (logi) [m], `cnpckinstruct` (char), `pocatchweightfl` (logi) [m], `cnpkgrestrictty` (char), `catchtolpct` (deci-2), `cnpkggrouplist` (char), `catchtolamt` (deci-5), `cnsizemeasitm` (char), `cnpkgshelfshpfl` (logi) [m], `srtprodcode` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Required
- `descrip3` (Extended Description) — Available starting in 6.1.040
- `seqno` (Lookup Name Seq No) — Controls Character Lookup sequence only
- `enterdt` (Entered Date) — Does not display in the application.; Default: Today's Date
- `statustype` (Status) — (A)ctive, (I)nactive, (L)abor or (S)uperceded; Valid values/xref: A, I, L or S; Default: A
- `weight` (Weight) — Per Stocking Unit
- `cubes` (Cube) — Per Stocking Unit
- `length` (Length) — Per Stocking Unit
- `width` (Width) — Per Stocking Unit
- `height` (Height) — Per Stocking Unit
- `unitstock` (Stocking Unit) — Label for Quantity Units; Default: each
- `unitsell` (Selling) — See Notes Below; Valid values/xref: ICSEU or SASTT U
- `unitcnt` (Counting) — See Notes Below; Valid values/xref: ICSEU or SASTT U
- `kittype` (Kit Type) — (P)rebuilt, (B)uild on demand or (M)ixed or Blank; Valid values/xref: <Blank>, P, B or M
- `kitrollty` (OE/BP Kit Rollup) — (C)ost, (P)rice, (B)oth or Blank PreBuilt = P or Blank, BOD = P, C, B or Blank; Valid values/xref: <Blank>, C, P or B
- `bodtransferty` (Allow Transfer) — T= transfer allowed (Fabricated Kit), else blank; Valid values/xref: <Blank> or T
- `tiedcompprt` (Component Print Transfer) — Print Fabricated Kit Components on: O=OE Pick, T= WT Pick, B=both,N=neither, or blank; Valid values/xref: <Blank>, O, T, B or N
- `randommixfl` (Random Mix) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `memomixfl` (Memo Mix) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `reqbundleidfl` (Req Bundle ID) — Typically used for lumber yard operations; Valid values/xref: Y or N; Default: N
- `kitnsreqfl` (Non-Stk Component) — Is a Non-Stock Component Required on Kit; Valid values/xref: Y or N; Default: N
- `exponinvfl` (Print on Invoice) — Print BOD Components on Invoice & Acknowledgement; Valid values/xref: Y or N; Default: N
- `vaassemblyty` (VA Assembly Type) — Available Starting 6.1.081; Valid values/xref: (P)reset, (C)onfigurable, (F)-Configure IPC or Blank if not an Assembly
- `vacutofflength` (VA Cutoff Length) — Available Starting 6.1.081
- `unitvaassembly` (VA Assembly Unit) — See Notes Below Available Starting 6.1.081; Valid values/xref: ICSEU or SASTT, will default to unitstock of cut off length provided with no unit
- `prodcat` (Product Category) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-C; Default: DCAOI Default
- `lifocat` (LIFO Cat) — Valid values/xref: SASTT-Q
- `mfgprod` (Manufacturer's Product #) — Available Starting in 6.1.060
- `brandcode` (Brand Code) — Available Starting in 6.1.060; Valid values/xref: SASTT-BC
- `altprodgrp` (Alternate Product Group Code) — Available Starting in 10.2.1.0; Valid values/xref: SASTT-AG
- `unspsc` (UNSPSC Code) — Available Starting in 10.2.1.0
- `msdsfl` (MSDS Product) — Valid values/xref: Y or N; Default: N
- `ncnr` (Non Cancellable/ Non Returnable Flag) — Available Starting in 10.0 (Y)es or Blank (means no); Valid values/xref: Y or <blank>
- `eccnclasscd` (Export Control Classification Number) — Available starting in 10.0; Valid values/xref: SASTT-EC
- `prodtier` (Product Tier) — Available starting in 10.1; Valid values/xref: SASTT-TR
- `prodpreference` (Product Preference) — Available starting in 10.3; Valid values/xref: SASTT-PR
- `prodtiergrp` (Product Tier Group) — Available starting in 10.3
- `countryoforigin` (Country of Origin) — Available starting in 10.0; Valid values/xref: SASTT-W
- `tariffcd` (HS Code) — Available Starting in 10.0.1; Valid values/xref: SASGT
- `priceonty` (Multiplier) — (B)ase, (L)ist or (C)ost; Valid values/xref: B, L or C; Default: B
- `termsdiscfl` (Terms Discount Flag) — (Y)es for Default Cash Terms or (N)o for Product Specific Cash Terms; Valid values/xref: Y or N; Default: Y
- `termspct` (Terms Discount Percent) — Required if Terms Discount Flag is NO
- `sellmult` (Round By) — Rounds quantities in order entry to the next whole figure if entered.
- `slgroup` (Supplier Group) — Valid values/xref: SLST - SG
- `pbseqno` (Price Book Seq#) — Controls Sort of PDRC and PDRP
- `slchgdt` (SL Last Update) — Available Starting 4.1
- `altprodprccd` (Alternate Product Price Code) — Available Starting 10.2.0
- `speccostty` (Special Price/Cost) — (Y)es, (T)housand, (H)undred or Blank Recommend either "Y" or Blank; Valid values/xref: <Blank>, Y, T or H
- `prccostper` (Price/Cost Unit) — Label for Price/Cost Units. Only required if Speccostty is not blank
- `csunperstk` (Units Per Stk Unit) — Price/Cost Unit Conversion Factor. For example if priced per hunderd 0.01. Only required if Speccostty is not blank
- `warrlength` (Length of Warranty) — For Service Warranty Module. Item must be a serialized product to use this information.; Default: 0
- `warrtype` (Type) — Item must be a serialized product to use this information.; Valid values/xref: (M)onth, (D)ay or (Y)ear; Default: M
- `prodtype` (Cores Product Type) — Only applies if CORES module is purchased. Available Starting 3.2; Valid values/xref: <blank>,(S)tandard, (R)eman, (I)mplied,(C)ore
- `impliedcoreprod` (Implied Core Product) — Only applies if CORES module is purchased. Available Starting 3.2; Valid values/xref: ICSP
- `implyqty` (Implied Core Quantity) — Only applies if CORES module is purchased. Available Starting 4.0
- `dirtycoreprod` (Dirty Core Product) — Only applies if CORES module is purchased. Available Starting 3.2; Valid values/xref: ICSP
- `vendcoregrcfl` (Vendor Core Grace Period Flag) — Y = Grace Period in Days or N = Grace Period in Months Available Starting 3.2; Valid values/xref: Y = Days N = Months; Default: N
- `vendgraceper` (Vendor Core Grace Period) — Grace period number of months or days. Available Starting 3.2
- `custcoregrcfl` (Customer Core Grace Period Flag) — Y = Grace Period in Days or N = Grace Period in Months Available Starting 3.2; Valid values/xref: Y = Days N = Months; Default: N
- `custgraceper` (Customer Core Grace Period) — Grace period number of months or days. Available Starting 3.2
- `cfgkitfl` (Configure Kit Flag) — Only used on BOD Kit Products Available Starting 6.1; Valid values/xref: (Y)es or (N)o; Default: N
- `cfgruleset` (Rule Set) — Used with Configurator Only Available Starting 6.0; Valid values/xref: Required for Configured Kits
- `cfgapplicationid` (Application ID) — Used with Configurator Only Available Starting 6.0
- `cfgnamespace` (Namespace) — Used with Configurator Only Available Starting 6.0
- `commoditycd` (Intrastat Commodity Code) — Used with VAT Only Available Starting 6.1.080; Valid values/xref: SASTT - CD
- `netmassamt` (Intrastat Net Mass) — Used with VAT Only Available Starting 6.1.080; Valid values/xref: Required if Commodity code NOT setup in SASTT to use Supp Units
- `usesuppunits` (Intrastat Supplementary Units) — Used with VAT Only Available Starting 6.1.080; Valid values/xref: Required if Commodity code setup in SASTT to use Supp Units
- `cuttype` (Cut Type) — Available Starting 10.3; Valid values/xref: (N)o Cut, (L)inear Cut or (D)imensional Cut; Default: N
- `cutnumparts` (Number of Cut Parts) — Number of Entry Fields for Cut Allocation Entry, Enter 0 When Not a Cut Part Available Starting 6.1.040; Valid values/xref: 0, 1 or 2; Default: 0
- `cutparttype1` (1st Cut Part Ty) — Enter the 1st Part Entry Type - (D)ecimal or (I)nteger Available starting 6.1.040; Valid values/xref: D or I Only used when cutnumparts 1 or 2; Default: I
- `cutpartunit1` (Cut Part1 Unit) — Enter the 1st Part Unit Available starting 6.1.040; Valid values/xref: ICSEU or SASTT U Only used when cutnumparts 1 or 2; Default: Stocking Unit
- `unitconv3` (# Units Cut Part 1) — See Notes Below Available starting 6.1.040; Valid values/xref: Required if using a cutpartunit1 not equal to stocking unit
- `unitediuom3` (EDI Units Cut Part 1) — Available starting 6.1.040
- `cutparttype2` (2nd Cut Part Ty) — Enter the 2nd Part Entry Type - (D)ecimal or (I)nteger Available starting 6.1.040; Valid values/xref: D or I Only used when cutnumparts 2; Default: D
- `cutpartunit2` (Cut Part2 Unit) — Enter the 2nd Part Unit Available starting 6.1.040; Valid values/xref: Only used when cutnumparts 2
- `unitconv5` (# Units Cut Part 2) — See Notes Below Available starting 10.3; Valid values/xref: Required if using a cutpartunit2 not equal to stocking unit
- `unitediuom5` (EDI Units Cut Part 2) — Available starting 10.3
- `cutpartincr2` (2nd Cut Part Incr) — Enter the 2nd Part Increment - How Many 2nd Part Units in Each 1st Part Available starting 6.1.040; Valid values/xref: Only used when cutnumparts 2
- `dimlengthparts` (Dimensional Length Parts) — Available Starting 10.3; Valid values/xref: 1 or 2; Default: 1
- `dimlengthty1` (Length Type 1) — (I)nteger or (D)ecimal Available Starting 10.3; Valid values/xref: D or I, Must be I if two part; Default: I
- `dimlengthty2` (Length Type 2) — (I)nteger or (D)ecimal Available Starting 10.3; Valid values/xref: D or I; Default: I
- `dimlengthunit1` (Length 1 Unit) — Available Starting 10.3; Valid values/xref: ICSEU or SASTT; Default: Stocking Unit
- `unitconv6` (# Units Length 1) — Available Starting 10.3; Valid values/xref: Required if using dimlengthunit1 not equal to stocking unit
- `unitediuom6` (EDI Units Length 1) — Available Starting 10.3
- `dimlengthunit2` (Length 2 Unit) — Available Starting 10.3; Valid values/xref: ICSEU or SASTT
- `unitconv7` (# Units Length 2) — Available Starting 10.3; Valid values/xref: Required if using dimlengthunit2 not equal to stocking unit
- `unitediuom7` (EDI Units Length 2) — Available Starting 10.3
- `dimlengthincr` (Length Increment) — Available Starting 10.3; Valid values/xref: Required if using 2 part Length
- `dimwidthparts` (Dimensional Width Parts) — Available Starting 10.3; Valid values/xref: 1 or 2; Default: 1
- `dimwidthty1` (Width Type 1) — (I)nteger or (D)ecimal Available Starting 10.3; Valid values/xref: D or I, Must be I if two part; Default: I
- `dimwidthty2` (Width Type 2) — (I)nteger or (D)ecimal Available Starting 10.3; Valid values/xref: D or I; Default: I
- `dimwidthunit1` (Width 1 Unit) — Available Starting 10.3; Valid values/xref: ICSEU or SASTT; Default: Stocking Unit
- `unitconv8` (# Units Width 1) — Available Starting 10.3; Valid values/xref: Required if using dimwidthunit1 not equal to stocking unit
- `unitediuom8` (EDI Units Width 1) — Available Starting 10.3
- `dimwidthunit2` (Width 2 Unit) — Available Starting 10.3; Valid values/xref: ICSEU or SASTT
- `unitconv9` (# Units Width 2) — Available Starting 10.3; Valid values/xref: Required if using dimwidthunit2 not equal to stocking unit
- `unitediuom9` (EDI Units Width 2) — Available Starting 10.3
- `dimwidthincr` (Width Increment) — Available Starting 10.3; Valid values/xref: Required if using 2 part Width
- `user5` (User5) — Used for Conversion Import ID
- `user10` (User10) — Available Starting 4.2
- `user11` (User11) — Available Starting 4.2
- `user12` (User12) — Available Starting 4.2
- `user13` (User13) — Available Starting 4.2
- `user14` (User14) — Available Starting 4.2
- `user15` (User15) — Available Starting 4.2
- `user16` (User16) — Available Starting 4.2
- `user17` (User17) — Available Starting 4.2
- `user18` (User18) — Available Starting 4.2
- `user19` (User19) — Available Starting 4.2
- `user20` (User20) — Available Starting 4.2
- `user21` (User21) — Available Starting 4.2
- `user22` (User22) — Available Starting 4.2
- `user23` (User23) — Available Starting 4.2
- `user24` (User24) — Available Starting 4.2
- `nospecrecno` (No SPC Default) — Special Price/Cost Record for Customers Setup for NO Special Price/Cost; Default: 0
- `oespecrecno` (OE SPC Defautlt) — Special Price/Cost Record for Customers setup to use OE Default; Default: 0
- `modelcode` (Model Number) — Valid values/xref: SASTT - Type 'PM'
- `rentprodcat` (Rental Product Category) — Rental Product Category; Valid values/xref: SASTT-C
- `exporepricefl` (Exclude from Auto Vendor Reprice) — Available Starting 11.20.2; Valid values/xref: Y or N; Default: N
- `catchweightfl` (Catch Weight Product) — Available Starting 11.20.5; Valid values/xref: Y or N; Default: N
- `oecatchweightfl` (Allow Sales Order Tracking) — Available Starting 11.20.5; Valid values/xref: Y or N; Default: Y
- `pocatchweightfl` (Allow Purchase Order Tracking) — Available Starting 11.20.5; Valid values/xref: Y or N; Default: Y
- `catchtolpct` (Max Tolerance Percent) — Available Starting 11.20.5
- `catchtolamt` (Max Tolerance Amount) — Available Starting 11.20.5
- `cnpkgtype` (Package Type) — Available Starting 11.20.6
- `cnmanpackfl` (Manually Pack Item) — Available Starting 11.20.6; Valid values/xref: Y or N; Default: N
- `cnpckinstruct` (Packing Instructions) — Available Starting 11.20.6
- `cnpkgrestrictty` (Packing Restriction) — Available Starting 11.20.6
- `cnpkggrouplist` (Packing Group Type List) — Available Starting 11.20.6
- `cnsizemeasitm` (Size Measurement of Item) — Available Starting 11.20.6
- `cnpkgshelfshpfl` (Self-Ship Unit of Measure) — Available Starting 11.20.6; Valid values/xref: Y or N; Default: N
- `tmsfreightclass` (Self-Ship Unit of Measure) — Available Starting 11.21.9
- `shopifyfl` (Third Party eCommerce integration with Shopify) — Available starting 2022.04.00; Valid values/xref: Y or N; Default: N
- `tmsnmfccode` (Infor TM Integration - NMFC code) — Available starting 2022.09.00
- `recalcprodcostinv` (Recalculate Product Cost at Invoice Processing) — Available starting 2022.09.00
- `recalcommcostinv` (Recalculate Comm Cost at Invoice Processing) — Available starting 2022.09.00
- `cntnrtype` (Container Type) — Available starting 2022.11.00
- `cntnrdimension1` (Container Dimension 1) — Available starting 2022.11.00
- `cntnrdimension2` (Container Dimension 2) — Available starting 2022.11.00
- `cntnrdimension3` (Container Dimension 3) — Available starting 2022.11.00
- `cntnrdimension4` (Container Dimension 4) — Available starting 2022.11.00
- `cntnrfactor` (Container Volume Factor) — Available starting 2022.11.00
- `cutdiameter` (Cut Product Diameter) — Available starting 2022.11.00

### `icspc`
**Product Customer Reservations**
Fields: `cono` (inte) [im], `recordtype` (char) [im], `srcrowpointer` (char) [im], `whse` (char) [im], `startdt` (date) [im], `expiredt` (date) [i], `activefl` (logi) [im], `rowpointer` (char) [i], `createdt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `refer` (char) [i], `contractno` (char) [i], `fillpriority` (inte) [i], `expectedratepct` (inte), `expiredusagetype` (char), `createdttz` (datetm-tz)

### `icspcd`
**Product Customer Reservations Detail**
Fields: `cono` (inte) [im], `srcrowpointer` (char) [im], `createdt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `icsprowpointer` (char) [im], `allowpullqtyfl` (logi) [im], `replenishfl` (logi) [m], `qtyrequired` (deci-2), `qtyreserved` (deci-2), `qtyexpected` (deci-2), `qtysold` (deci-2), `lastinvdt` (date), `expectedratepct` (inte), `qtyforecast` (deci-2[12]), `qtyactual` (deci-2[12]), `stkqtytopurchase` (deci-2), `rrarreportno` (inte), `rrarupddt` (date), `rrarupdtm` (char), `rrartype` (char), `stkqtyonorder` (deci-2), `createdttz` (datetm-tz), `lastinvdttz` (datetm-tz), `rrarupddttz` (datetm-tz)

### `icspe`
**Product Environmental Handling Fees**
Fields: `cono` (inte) [im], `srcrowpointer` (char) [im], `state` (char) [im], `startdt` (date) [im], `enddt` (date), `amount` (deci-2), `addonno` (inte) [i], `ehftype` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `icspl`
**Inventory Control Setup Product List - List**
Fields: `cono` (inte) [i], `type` (char) [i], `descrip` (char) [i], `operinit` (char), `transproc` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `custno` (deci-0) [i], `login` (char) [i], `listid` (char)

### `icsplp`
**Inventory Control Setup Product List - Products**
Fields: `cono` (inte) [i], `type` (char) [i], `prod` (char) [im], `qtyord` (deci-2), `unit` (char), `price` (deci-5), `operinit` (char), `transproc` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `binloc` (char), `lastcountqty` (deci-2), `mincountqty` (inte), `maxcountqty` (inte), `lastcountdt` (date), `listid` (char) [i], `lastcountdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `type` (Type) — Unique shopping list name. Will be created if needed.; Valid values/xref: ICSPL; Required
- `descrip` (Description) — Unique shopping list description. Used if creating new list type.; Default: Type
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `mincountqty` (Min Count Qty) — Not Available until 3.2
- `maxcountqty` (Max Count Qty) — Not Available until 3.3
- `binloc` (Bin Location) — Not Available until 3.4
- `user5` (user5) — Used for Conversion Import ID

### `icspr`
**Product Restrictions**
Fields: `cono` (inte) [im], `recordtype` (char) [im], `restricttype` (char) [im], `srcrowpointer` (char) [im], `whse` (char) [im], `startdt` (date) [im], `statuscd` (char), `expiredt` (date) [i], `activefl` (logi) [m], `restrictcd` (char) [i], `certrequiredfl` (logi) [m], `rowpointer` (char) [i], `createdt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `restrictovrfl` (logi) [m], `descrip` (char), `module` (char), `vendno` (deci-0) [i], `shiptowhse` (char), `createdttz` (datetm-tz)

### `icsprc`
**Product Restriction Certificate/License**
Fields: `cono` (inte) [im], `recordtype` (char) [im], `srcrowpointer` (char) [im], `restrictcd` (char) [im], `startdt` (date) [im], `certcode` (char) [im], `expiredt` (date) [i], `activefl` (logi) [m], `certaccptdt` (date), `certaccptuser` (char), `certauthuser` (char), `createdt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `createdttz` (datetm-tz)

### `icsprt`
**Product Restriction Specific Territory**
Fields: `cono` (inte) [im], `srcrowpointer` (char) [im], `territorycd` (char) [im], `seqno` (inte) [im], `city` (char), `state` (char) [i], `zipcd` (char) [i], `countrycd` (char) [i], `custno` (deci-0) [i], `shipto` (char) [i], `custtype` (char) [i], `pricetype` (char) [i], `certcode` (char) [i], `salesterr` (char) [i], `createdt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `createdttz` (datetm-tz)

### `icsr`
**Inventory Control Setup Replenishment**
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `prodline` (char) [i], `whse` (char) [im], `ranks` (inte), `pcthitfl` (logi) [m], `newprodrank` (char), `monthshistory` (inte), `tminmonths` (inte), `tminhits` (inte), `frozenhits` (inte), `frozenmonths` (inte), `icusage` (char), `ltexcminpct` (deci-2), `newprodmonths` (inte), `rankpct` (deci-2[26]), `minhits` (inte[26]), `maxleadtime` (inte[26]), `minleadtime` (inte[26]), `safewhsemin` (deci-2[26]), `safevendmin` (deci-2[26]), `maxltarpwhse` (inte), `minltarpwhse` (inte), `ltrcpts` (inte), `excusemths` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `seastrendmax` (deci-2), `seastrendmin` (deci-2), `seastrendexpdt` (date), `seastrend` (deci-2), `xfercostnew` (deci-2), `xfercostold` (deci-2), `xferusagehist` (inte), `wtunitrnd` (char), `vendunitrnd` (char), `rushpriority` (inte), `critrank` (char), `critpriority` (inte), `beloppriority` (inte), `docpriority` (inte), `otherpriority` (inte), `excessusereas` (char), `lowusereas` (char), `stockoutreas` (char), `overusemult` (deci-2), `lowusemax` (inte), `seastrendtyu` (inte), `seastrendlyu` (inte), `bopriority` (inte), `belowrank` (char), `rushcolor` (char), `critcolor` (char), `belowcolor` (char), `backcolor` (char), `doccolor` (char), `othercolor` (char), `asqminhits` (inte), `hi5minhits` (inte), `safetyrcpts` (inte[26]), `usgmths` (inte[26]), `asqdiff` (deci-2), `hi5diff` (deci-2), `maxleadtimewhse` (inte[26]), `minleadtimewhse` (inte[26]), `safetymajority` (inte[26]), `safewhsemid` (deci-2[26]), `safevendmid` (deci-2[26]), `safewhsemax` (deci-2[26]), `safevendmax` (deci-2[26]), `minsafety` (deci-2[26]), `maxsafety` (deci-2[26]), `safetymonths` (inte[26]), `minltdays` (inte), `maxltdays` (inte), `minltvenddays` (inte), `minltwhsedays` (inte), `maxltvenddays` (inte), `maxltwhsedays` (inte), `ltmths` (inte), `ltexcmaxpct` (deci-2), `ltexcmths` (inte), `rankty` (char), `oversoty` (char), `overexcusety` (char), `overlowusety` (char), `seasusenewty` (char), `frzexceptty` (char), `frzpermexcty` (char), `frzoanexcty` (char), `frzdnrexcty` (char), `invvalchgty` (char), `asqtrsfty` (char), `asqdiffty` (char), `hi5trsfty` (char), `hi5diffty` (char), `minsafevendty` (char[26]), `maxsafevendty` (char[26]), `midsafevendty` (char[26]), `minsafewhsety` (char[26]), `maxsafewhsety` (char[26]), `midsafewhsety` (char[26]), `seastrendexpdttz` (datetm-tz)

### `icsru`
**IC Replenishment Usage Matrix**
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `prodline` (char) [i], `whse` (char) [im], `usagelevel` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `costge` (deci-2[10]), `newop` (inte[10]), `newlp` (inte[10]), `newqty` (inte[10]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `usagerate` (deci-2)

### `icss`
**Inventory Control Setup Special Price Costing**
Fields: `cono` (inte) [i], `prod` (char) [im], `icspecrecno` (inte) [i], `speccostty` (char), `csunperstk` (deci-8), `prccostper` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `statusfl` (logi) [im], `transproc` (char), `transdttmz` (datetm-tz) [i], `rowpointer` (char) [i]

### `icsv`
**UPC# Setup**
Fields: `cono` (inte) [i], `type` (char) [i], `prod` (char) [im], `section1` (deci-0) [i], `section2` (deci-0) [i], `section3` (deci-0) [i], `section4` (deci-0) [i], `section5` (deci-0) [i], `section6` (deci-0) [i], `scc14packdet` (char), `unspsc` (char), `pcctype` (char), `scc14nrsubpack` (inte), `scc14totunits` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `vendno` (deci-0) [im], `vendprod` (char) [i], `transproc` (char), `ecbatchnm` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `vendno` (Vendor #) — Can be CHAR(24) if using Cross Reference. Should be the ICSW ARP Vendor #.; Valid values/xref: APSV; Required
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP/ICSC; Required
- `vendprod` (Vendor Product #) — Only used by SL IDW
- `user5` (user5) — Used for Conversion Import ID

### `icsw`
**Warehouse Product Master**
*Warehouse setup master.*
**Operators call this:** "Company" (Inventory), "Warehouse" (Inventory), "On-Hand Value (Average Cost)" (Inventory), "Average Cost (Each)" (Inventory), "On-Hand Quantity" (Inventory), "Backorder Quantity" (Inventory), "Committed Quantity" (Inventory), "Demand Quantity" (Inventory), "In-Transit Quantity" (Inventory), "On-Order Quantity" (Inventory), "Reserved Quantity" (Inventory), "Unavailable Quantity" (Inventory), "On-Hand Value (Last Cost)" (Inventory), "Last Cost (Each)" (Inventory), "On-Hand Value (Replacement Cost)" (Inventory), "Replacement Cost (Each)" (Inventory), "On-Hand Value (Standard Cost)" (Inventory), "Standard Cost (Each)" (Inventory), "Bin Location 1" (Inventory), "Bin Location 2" (Inventory), "Product" (Inventory), "Product Line" (Inventory), "Stocking Status" (Inventory), "Inventory Class" (Inventory), "Replenishment Type" (Inventory), "Push Flag" (Inventory), "Replenishment Vendor" (Inventory), "Replenishment Warehouse" (Inventory), "Override In Reason" (Inventory), "Override Out Reason" (Inventory), "Order Calculation Type" (Inventory), "Warehouse Rank" (Inventory), "Company Rank" (Inventory), "ABC Quantity Class" (Inventory), "Obsolete Flag (UDF)" (Inventory), "Average Lead Time" (Inventory), "Line Point" (Inventory), "Order Point" (Inventory), "Last Invoice Date" (Inventory), "Last PO Date" (Inventory), "Last Receipt Date" (Inventory), "Last Sales Order Date" (Inventory), "Created Date" (Inventory), "Average Cost" (Inventory), "Base Price" (Inventory), "Last Cost" (Inventory), "List Price" (Inventory), "Replacement Cost" (Inventory), "Standard Cost" (Inventory), "ARP Usage" (Inventory), "Usage Control" (Inventory), "Usage Rate" (Inventory), "Product" (Purchasing), "Product Line" (Purchasing), "Stocking Status" (Purchasing), "Replenishment Type" (Purchasing), "Prime Supplier" (Purchasing), "Warehouse Rank" (Purchasing), "Company Rank" (Purchasing), "ABC Quantity Class" (Purchasing), "Average Lead Time" (Purchasing), "Line Point" (Purchasing), "Order Point" (Purchasing), "Average Cost" (Purchasing), "Base Price" (Purchasing), "Last Cost" (Purchasing), "List Price" (Purchasing), "Replacement Cost" (Purchasing), "Standard Cost" (Purchasing), "Company" (Sales), "Warehouse" (Sales), "On-Hand Quantity" (Sales), "On-Hand Value (Average Cost)" (Sales), "Product" (Sales), "Product Line" (Sales), "Stocking Status" (Sales), "Inventory Class" (Sales), "Replenishment Type" (Sales), "Vendor" (Sales), "Warehouse Rank" (Sales), "Company Rank" (Sales), "ABC Quantity Class" (Sales), "Average Cost" (Sales), "Base Price" (Sales), "Last Cost" (Sales), "List Price" (Sales), "Replacement Cost" (Sales), "Standard Cost" (Sales), "Product" (Warehouse Transfers), "Product Line" (Warehouse Transfers), "Stocking Status" (Warehouse Transfers), "Inventory Class" (Warehouse Transfers), "Replenishment Type" (Warehouse Transfers), "Supplier" (Warehouse Transfers), "Warehouse Rank" (Warehouse Transfers), "Company Rank" (Warehouse Transfers), "ABC Quantity Class" (Warehouse Transfers), "Average Cost" (Warehouse Transfers), "Base Price" (Warehouse Transfers), "Last Cost" (Warehouse Transfers), "List Price" (Warehouse Transfers), "Replacement Cost" (Warehouse Transfers), "Standard Cost" (Warehouse Transfers)
Fields: `cono` (inte) [i], `whse` (char) [im], `prod` (char) [im], `qtyonhand` (deci-2), `statustype` (char), `serlottype` (char), `baseprice` (deci-5), `pricetype` (char), `smanalfl` (logi) [m], `nontaxtype` (char), `taxablety` (char), `arptype` (char) [i], `arppushfl` (logi) [im], `prodline` (char) [i], `famgrptype` (char), `vendprod` (char) [i], `unitbuy` (char), `unitstnd` (char), `usmthsfrzfl` (logi) [m], `safeallamt` (deci-0), `safeallpct` (deci-0), `orderpt` (deci-0), `linept` (deci-0), `overreasin` (char), `ordqtyout` (deci-0), `overreasout` (char), `ordcalcty` (char), `class` (inte), `last852onord` (deci-2), `last852avail` (deci-2), `frozentype` (char), `unitwt` (char), `frozenmmyy` (char), `updtsrc` (char), `frozenmos` (inte), `rebatety` (char), `avgcost` (deci-5), `rebsubty` (char), `replcost` (deci-5), `transunit` (char), `lastcost` (deci-5), `usagectrl` (char), `stndcost` (deci-5), `frozenltty` (inte), `addoncost` (deci-5), `abcoverexpdt` (date), `qtyreservd` (deci-2), `qtycommit` (deci-2), `rpt852dt` (date), `qtybo` (deci-2), `rolloanusagefl` (logi) [m], `qtyintrans` (deci-2), `qtyonorder` (deci-2), `qtyrcvd` (deci-2), `qtyunavail` (deci-2), `user3` (char), `enterdt` (date), `user4` (char), `lastinvdt` (date), `user5` (char), `lastrcptdt` (date), `user6` (deci-5), `lastcntdt` (date) [i], `user7` (deci-5), `lastpowtdt` (date), `user8` (date), `transdt` (date), `user9` (date), `priceupddt` (date), `operinit` (char), `transtm` (char), `countfl` (logi) [im], `exout30fl` (logi) [m], `exlssfalfl` (logi) [m], `arpwhse` (char) [i], `arpvendno` (deci-0) [i], `usagerate` (deci-2), `lastsodt` (date), `ordqtyin` (deci-0), `availsodt` (date), `leadtmavg` (inte), `avgltdt` (date), `lastltdt` (date), `priorltdt` (date), `leadtmlast` (inte), `leadtmprio` (inte), `frozenbyty` (logi) [m], `issueunytd` (deci-2), `rcptunytd` (deci-2), `retinunytd` (deci-2), `retouunytd` (deci-2), `datccost` (deci-5), `qtyreqshp` (deci-2), `qtyreqrcv` (deci-2), `binloc1` (char) [i], `binloc2` (char), `so15fl` (logi) [m], `nodaysso` (inte), `notimesso` (inte), `stndcostdt` (date), `replcostdt` (date), `autofillfl` (logi) [m], `seasbegmm` (inte), `seasendmm` (inte), `exbozerofl` (logi) [m], `classfrzfl` (logi) [m], `boshortfl` (logi) [m], `usgmths` (inte), `nodaysseas` (inte), `taxgroup` (inte), `taxtype` (char), `lastcostfor` (deci-5), `tariffcd` (char), `gststatus` (logi) [m], `qtydemand` (deci-2), `user1` (char), `user2` (char), `baseyrcost` (deci-5), `listprice` (deci-5), `wmfl` (logi) [m], `wmpriority` (char), `bintype` (char), `wmallocty` (char), `wmrestrict` (char), `taxprice` (deci-5), `taxexbuyfl` (logi) [m], `rebatecost` (deci-5), `keyindex` (char), `transproc` (char), `reservety` (char), `arpusage` (char), `snpocd` (char), `slchgdt` (date), `frtextra1` (deci-5), `reservedays` (inte), `autoesrcbofl` (logi) [m], `seasonfrzfl` (logi) [m], `safealldays` (inte), `companyrank` (char), `whserank` (char), `safetyfrzfl` (logi) [m], `asqfl` (logi) [m], `hi5fl` (logi) [m], `ordptadjty` (char), `frtextra2` (deci-5), `minhits` (deci-0), `minthreshold` (deci-0), `minthreshexpdt` (date), `oorderpt` (deci-0), `olinept` (deci-0), `seastrendmax` (deci-2), `seastrendmin` (deci-2), `seastrendexpdt` (date), `seastrend` (deci-2), `safeallty` (char) [m], `seastrendtyu` (inte), `seastrendlyu` (inte), `asqdiff` (deci-2), `hi5diff` (deci-2), `asqdifffl` (logi) [m], `hi5difffl` (logi) [m], `rankfreezefl` (logi) [m], `threshrefer` (char), `replcostfor` (deci-5), `frtfreefl` (logi) [m], `abcsalesclass` (char), `abcqtyclass` (char), `abccustclass` (char), `abcgmroiclass` (char), `abcfinalclass` (char), `abcclassdt` (date), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `nonstockty` (char), `rcvunavailfl` (logi) [m], `inclunavqty` (char), `custavgcost` (deci-5), `custlastcost` (deci-5), `custfixedcost` (deci-5), `custqtyonhand` (deci-2), `custqtyonorder` (deci-2), `custqtyunavail` (deci-2), `srcommcode1` (char), `srcommcode2` (char), `srmachine` (char), `regrindfl` (logi) [m], `laborprod` (char), `linkedprod` (char), `billonrcptfl` (logi) [m], `custonlyfl` (logi) [m], `criticalfl` (logi) [m], `shelflifefl` (logi) [m], `acquiredt` (date), `surplusty` (char), `custqtyrcvd` (deci-2), `srunitcnt` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `ncnr` (char), `countryoforigin` (char), `prodpreference` (char), `valevel` (inte), `excludemovefl` (logi) [m], `totusagerate` (deci-2), `transdttmz` (datetm-tz) [i], `edi852statuschgfl` (logi) [m], `abcclassdttz` (datetm-tz), `abcoverexpdttz` (datetm-tz), `acquiredttz` (datetm-tz), `availsodttz` (datetm-tz), `avgltdttz` (datetm-tz), `enterdttz` (datetm-tz), `lastcntdttz` (datetm-tz), `lastinvdttz` (datetm-tz), `lastltdttz` (datetm-tz), `lastpowtdttz` (datetm-tz), `lastrcptdttz` (datetm-tz), `lastsodttz` (datetm-tz), `minthreshexpdttz` (datetm-tz), `priceupddttz` (datetm-tz), `priorltdttz` (datetm-tz), `replcostdttz` (datetm-tz), `rpt852dttz` (datetm-tz), `seastrendexpdttz` (datetm-tz), `slchgdttz` (datetm-tz), `stndcostdttz` (datetm-tz), `suppwarrallowfl` (logi) [m], `nondiscountablefl` (logi) [m], `nopromofl` (logi) [m], `prclblunit` (char), `prclblprice` (deci-5), `prclbldttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `whse` (Whse) — Can be CHAR(24) if using xref; Valid values/xref: ICSD; Required
- `enterdt` ((does not display)) — Date the Item was setup in the Whse; Default: Today's Date
- `statustype` (Status) — (D)irect Ship, (O)rder as needed, (S)tock, (X)-Do not reorder or (N)-OAN-Nonstock (available starting in 6.0) BOD Kits must be S; Valid values/xref: D, O, S, X or N; Default: S
- `serlottype` (Extended Type) — (S)erial , (L)ot, or Blank. Use additional conversion for ICSES-Serial or ICSEL-Lot; Valid values/xref: <Blank>, S or L
- `snpocd` (Serial/Lot AO Override) — Blank for AO Default, (R)eceiving or (S)ales. Available Starting 4.1; Valid values/xref: <Blank>, R or S
- `reservety` (Reservation Type) — (D)elay, (R)eceipts, (A)lways or Blank; Valid values/xref: <Blank>, A, D or R
- `prodpreference` (Product Preference) — Available Starting 10.1 ICSP default starting 10.3; Valid values/xref: SASTT-PR; Default: ICSP
- `pricetype` (Product Price Type) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-K
- `smanalfl` (Sales Manager) — Update Sales Manager Tables; Valid values/xref: Y or N; Default: Y
- `autofillfl` (Auto BO Fill) — Valid values/xref: Y or N; Default: Y
- `boshortfl` (BO All if Short) — Valid values/xref: Y or N; Default: N
- `countfl` (Count Required) — Valid values/xref: Y or N; Default: N
- `arptype` (ARP) — (V)endor, (W)arehouse , (C)entral Whse, (K)it, V(M)I or (F)ab VA; Valid values/xref: V, W, C, K, M or F; Default: V
- `arppushfl` (Push or Pull ARP Warehouse) — Y = Push, N = Pull; Valid values/xref: Y or N; Default: N
- `arpvendno` (ARP Vendor#) — Required if ARP type is V, recommended for all others. Can be CHAR(24) if using Vendor Cross Reference.; Valid values/xref: APSV; Required
- `arpwhse` (ARP Whse) — Supplying Whse, Used only if ARP type is W or C. Can be CHAR(24) if using xref; Valid values/xref: ICSD
- `prodline` (Product Line) — Can be CHAR(24) if using xref; Valid values/xref: ICSL; Required
- `vendprod` (Vendor Product) — Vendor Product Number used for Cross Referencing Vendor Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1
- `famgrptype` (Family Group) — Valid values/xref: SASTT-I
- `ncnr` (Non Cancellable/ Non Returnable Flag) — Available Starting in 10.0 (Y)es or Blank (means no); Valid values/xref: Y or <blank>
- `rebatety` (Rebate Type) — Valid values/xref: PDST-PT
- `rebsubty` (Rebate Sub Type) — Valid values/xref: PDST-ST
- `autoesrcbofl` (Auto eSource BO Flag) — (Y)es or (N)o. Available Starting 4.1; Valid values/xref: Y or N; Default: N
- `binloc1` (Bin Loc#1 /xx/xx/xxx/xxx) — Enter Characters Left Justified with no Slashes. Add'l Bins can be converted with separate program.
- `binloc2` (Bin Loc#2 /xx/xx/xxx/xxx) — Enter Characters Left Justified with no Slashes
- `wmfl` (Warehouse Manager) — Product Controlled by WM Module?; Valid values/xref: Y or N; Default: N
- `wmallocty` (WM Allocate) — (C)ube Capacity, (S)ize Type or Blank; Valid values/xref: <Blank>, Cor S
- `bintype` (WM Bin Type) — Valid values/xref: WMST-BT
- `wmpriority` (WM Priority) — Valid values/xref: (F)ifo, (P)ick Priority or Blank
- `frtfreefl` (Free Freight Flag) — Available Starting 4.1
- `frtextra1` (Extra Freight 1) — Available Starting 4.1
- `frtextra2` (Extra Freight 2) — Available Starting 4.1
- `unitbuy` (Buying Unit) — See Notes Below; Valid values/xref: SASTT-U or ICSEU
- `unitconv1` (# Units Buying) — See Notes Below
- `unitediuom1` (EDI Units Buying) — See Notes Below
- `unitstnd` (Standard Pack) — See Notes Below; Valid values/xref: SASTT-U or ICSEU
- `unitconv2` (# Units Standard) — See Notes Below
- `unitediuom2` (EDI Units Stnd.) — See Notes Below
- `unitwt` (Transfer Unit) — See Notes Below; Valid values/xref: SASTT-U or ICSEU
- `unitconv3` (# Units Transfer) — See Notes Below
- `unitediuom3` (EDI UnitsTransfer) — See Notes Below
- `safeallty` (Safety Allowance) — Valid values/xref: (Q)ty, (D)ays or %; Default: %
- `safetyfrzfl` (Safety Freeze Flag) — Freeze Safety from Updating in ICAMM. Available Starting 4.0; Valid values/xref: Y or N; Default: N
- `usagerate` (Usage Rate) — Average Qty Sold per Month. Can be populated by ICAMM after conversion.
- `usgmths` (Usage Months) — # of Months History to compute usage rate; Valid values/xref: 1 to 12; Default: 6
- `usmthsfrzfl` (Usage Months Frozen Flag) — Freeze Usage Months from Updating in ICAMM. Available Starting 4.0; Valid values/xref: Y or N; Default: N
- `usagectrl` (Usage Calculation Method) — (F)orward, (B)ackward, (T)rend %, (D)emand Planning, (1)-(9) Alpha Factor, or Blank D Available starting 10.2.1.0; Valid values/xref: <Blank>, F, B, T, D,1, 2, 3, 4, 5, 6, 7, 8, or 9 D requires License Key for Demand Planning
- `excludemovefl` (Exclude from Usage Move) — Used with Tiers and Preferences to exclude product from usage move Available starting in 10.3.1; Valid values/xref: Y or N; Default: N
- `orderpt` (Order Point/Min) — Can be computed by ICAMM
- `linept` (Line Point/Max) — Can be computed by ICAMM
- `ordqtyin` (Order Qty) — Can be computed by ICAMM
- `ordcalcty` (Order Calculation Method) — (E)oq, (C)lass, (M)in-Max, (Q)uantity Break, (B)lanket Order, or (H)uman; Valid values/xref: E, C, M, Q, B or H; Default: C
- `overreasin` (Override Reason) — Order Qty Override Reason if not Computed by ICAMM; Valid values/xref: SASTT-O
- `surplusty` (Surplus Type) — Available Starting 6.1; Valid values/xref: (I)CSW Usage Rate, (A)ctual Monthly Usage or <Blank>
- `inclunavqty` (Incl Unavail Reason Qty) — Include Unavail in (P)O, W(T),(B)oth or <Blank> Available Starting 6.1; Valid values/xref: P, T, B or blank
- `rolloanusagefl` (Roll Up OAN Usage Flag) — Only used when ARP type is C or W, Status is OAN and ICSR uses Rolled up Usage Method Available Starting in 6.0; Valid values/xref: Y or N; Default: N
- `companyrank` (Company Rank) — Can be computed by ICAI
- `whserank` (Warehouse Rank) — Can be computed by ICAI
- `rankfreezefl` (Freeze Ranks) — Freeze Ranks from Updating in ICAI; Valid values/xref: Y or N; Default: N
- `asqfl` (Allow Average Sales Quantity Calculation) — Valid values/xref: Y or N; Default: N
- `asqdifffl` (Use ASQ Max $) — Valid values/xref: Y or N; Default: N
- `hi5fl` (Allow Five High Calculation) — Valid values/xref: Y or N; Default: N
- `hi5difffl` (Use 5Hi Max $) — Valid values/xref: Y or N; Default: N
- `leadtmavg` (Average Lead Tm) — Required for ICAMM Calculations; Default: 14
- `lastltdt` (Date of Last Lead time Calc) — Valid values/xref: Required if Last LT is not 0
- `priorltdt` (Date of Prior Lead Time Calc) — Valid values/xref: Required if Prior LT is not 0
- `frozenltty` (Lead Time Frozen Code) — Freeze Lead Time from Updating in Receiving
- `class` (Product Class) — Can be computed by ICAI; Valid values/xref: 1 to 13; Default: 1
- `classfrzfl` (Class Frozen Flag) — Freeze Class from Updating in ICAI; Valid values/xref: Y or N; Default: N
- `abcgmroiclass` (ABC GMROI Class) — Can be computed by ICAE. Available Starting 4.0; Valid values/xref: Blank, A, B, C, D, X or Y
- `abcsalesclass` (ABC Sales Class) — Can be computed by ICAE. Available Starting 4.0; Valid values/xref: Blank, A, B, C or D
- `abcqtyclass` (ABC Quantity Class) — Can be computed by ICAE. Available Starting 4.0; Valid values/xref: Blank, A, B, C or D
- `abccustclass` (ABC Customer Class) — Available Starting 4.0; Valid values/xref: Blank, A, B, C or D
- `abcoverexpdt` (ABC Override Expiration Date) — Available Starting in 6.0 Expiration date for abccustclass value
- `abcfinalclass` (ABC Final Class) — Can be computed by ICAE. Available Starting 4.0; Valid values/xref: Blank, A, B, C or D
- `abcclassdt` (ABC Classification Date) — Can be computed by ICAE. Available Starting 4.0
- `seasbegmm` (Season Begin) — Only valid with Usage Method <Blank>
- `seasendmm` (Season End) — Only valid with Usage Method <Blank>
- `nodaysseas` (Review Days) — Only valid with Usage Method <Blank>; Default: 30
- `ordqtyout` (Order Qty) — Only valid with Usage Method <Blank>
- `overreasout` (Override Reason) — Valid values/xref: SASTT-O
- `seastrendmax` (Seasonal Trend Max %) — Only valid with Usage Method (T)rend %
- `seastrendmin` (Seasonal Trend Min %) — Only valid with Usage Method (T)rend %
- `seastrendexpdt` (Seasonal Trend Exp Date) — Only valid with Usage Method (T)rend %
- `seastrendtyu` (This Year Min Units) — Only valid with Usage Method (T)rend %
- `seastrendlyu` (Last Year Min Units) — Only valid with Usage Method (T)rend %
- `seasonfrzfl` (Seasonal Frozen Flag) — Only valid with Usage Method (T)rend %. Available Starting 4.0; Valid values/xref: Y or N; Default: N
- `taxtype` (Tax Exempt Type) — Used with SASGE for Variable Customers
- `taxgroup` (Tax Group) — Valid values/xref: 1 through 5 or SASTA-TG record; Default: 1
- `taxablety` (Taxable Type) — (Y)es, (N)o, or (V)ariable Recommend Variable; Valid values/xref: Y, N or V; Required; Default: N
- `nontaxtype` (Non Tax Reason) — Valid values/xref: SASTT-N; Default: Admin Option
- `tariffcd` (Tariff Code) — Valid values/xref: SASGT
- `countryoforigin` (Country of Origin) — Available starting in 10.0; Valid values/xref: SASTT-W
- `gststatus` (G.S.T. Status (Canada Only)) — (T)axable, (E)xempt; Valid values/xref: <Blank>, T or E; Default: T, if company country = 'CA'
- `frozenmmyy` (Frozen Date) — See Notes Below; Valid values/xref: Required mmyy if # of Months frozen not 0
- `frozentype` (Frozen Reason) — See Notes Below; Valid values/xref: SASTT-F
- `frozenmos` (# of Months Frozn) — See Notes Below
- `acquiredt` (Acquired Date) — First date product was acquired
- `so15fl` (Stock Out 15 Days) — Is Product Stocked Out over 15 days?; Valid values/xref: Y or N; Default: N
- `lastsodt` (Last Stock Out) — Last Date when Stocked Out over 15 Days; Valid values/xref: mmddyy
- `nodaysso` (Days) — # of Days Currently Stocked Out this Month; Valid values/xref: Cannot be greater than 31
- `notimesso` (Stock Out Times) — # of Times Item as been Stocked Out
- `availsodt` (Stock Available) — Date stock became available after last stock out
- `replcostfor` (Foreign Replacement Cost) — Available Starting 4.1
- `qtyunavail` (Qty Unavailable) — See Notes Below
- `reasunavty` (Reason Unavailable) — See Notes Below; Valid values/xref: SASTT - L; Default: **
- `custavgcost` (Customer Avg Cost) — Storeroom Whses Only
- `custlastcost` (Customer Last Cost) — Storeroom Whses Only
- `custfixedcost` (Customer Fixed Cost) — Storeroom Whses Only
- `custqtyonhand` (Customer Qty on Hand) — Storeroom Whses Only - See Notes Below
- `custqtyonorder` (Customer Qty on Order) — Storeroom Whses Only
- `custqtyunavail` (Customer Qty Unavail) — Storeroom Whses Only
- `custqtyrcvd` (Customer Qty Received) — Storeroom Whse Only available starting 6.1.040
- `custqtyburnoff` (Customer Burn off Qty) — Storeroom Whses Only
- `custavgcostburnoff` (Customer Burn off Cost) — Storeroom Whses Only
- `slchgdt` (Last SL Update Date) — Available Starting 4.1
- `buyer` (Buyer) — Required if ICSL not already converted. Can be CHAR(24) if using xref; Valid values/xref: SASTT-B; Default: DCAOI
- `user5` (User5) — Used for Conversion Import ID
- `user10` (User10) — Available Starting 4.2
- `user11` (User11) — Available Starting 4.2
- `user12` (User12) — Available Starting 4.2
- `user13` (User13) — Available Starting 4.2
- `user14` (User14) — Available Starting 4.2
- `user15` (User15) — Available Starting 4.2
- `user16` (User16) — Available Starting 4.2
- `user17` (User17) — Available Starting 4.2
- `user18` (User18) — Available Starting 4.2
- `user19` (User19) — Available Starting 4.2
- `user20` (User20) — Available Starting 4.2
- `user21` (User21) — Available Starting 4.2
- `user22` (User22) — Available Starting 4.2
- `user23` (User23) — Available Starting 4.2
- `user24` (User24) — Available Starting 4.2
- `boxqty` (Inner Pack) — Use in TWL Whses Only; Default: 1
- `caseqty` (Case Quantity) — Use in TWL Whses Only; Default: 1
- `palletqty` (Pallet Quantity) — Use in TWL Whses Only; Default: 1
- `whzone` (Warehouse Zone) — Use in TWL Whses Only; Default: WLAO
- `bincntr` (Counter Bin) — Use in TWL Whses Only
- `kitbuild` (Kit Build Dept) — Use in TWL Whses Only
- `srcommcode1` (Commodity Code 1) — Use in Storerooms Only
- `srcommcode2` (Commodity Code 2) — Use in Storerooms Only
- `srmachine` (Machine) — Use in Storerooms Only
- `srunitcnt` (Storeroom Count Unit) — Use in Storerooms Only Available starting 6.1.040; Valid values/xref: SASTT-U or ICSEU
- `unitconv4` (# Units SR Counting) — See Notes Below Available starting 6.1.040
- `unitediuom4` (EDI UnitsCounting) — See Notes Below Available starting 6.1.040
- `regrindfl` (Regrind Flag) — Use in Storerooms Only; Valid values/xref: Y or N; Default: N
- `laborprod` (Regrind Labor Product) — Use in Storerooms Only; Valid values/xref: ICSP, ICSW
- `linkedprod` (Linked Regrind Product) — Use in Storerooms Only; Valid values/xref: ICSP, ICSW
- `billonrcptfl` (Bill on Receipt Flag) — Use in Storerooms Only; Valid values/xref: Y or N; Default: N
- `custonlyfl` (Customer Owned Flag) — Use in Storerooms Only; Valid values/xref: Y or N; Default: N
- `rcvunavailfl` (Rcv as Unavail Flag) — Use in Storerooms Only; Valid values/xref: Y or N; Default: N
- `criticalfl` (Critical Product Flag) — Use in Storerooms Only; Valid values/xref: Y or N; Default: N
- `shelflifefl` (Shelf Life Product Flag) — Use in Storerooms Only; Valid values/xref: Y or N; Default: N
- `edi852statuschgfl` (EDI 852 Status Change Flag) — Available Starting 11.18.9; Valid values/xref: Y or N; Default: N
- `recalcprodcostinv` (Recalculate Product Cost at Invoice Processing) — Available Starting 2022.09
- `recalcommcostinv` (Recalculate Comm Cost at Invoice Processing) — Available Starting 2022.09
- `cutminlength` (Cut Minimum Sellable Length) — Available Starting 2022.09
- `cutminty` (Cut Minimum Action Type) — Available Starting 2022.09
- `cutminoutput` (Cut Minimum Action Output) — Available Starting 2022.09

### `icswb`
**Additional Bin Locations**
Fields: `cono` (inte) [i], `prod` (char) [im], `whse` (char) [im], `binloc` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSW; Required
- `whse` (Warehouse) — Can be CHAR(24) if using xref; Valid values/xref: ICSD; Required
- `binloc` (Bin Location) — Format xx/xx/xxx/xxx. Data should be Left Justifed with no slashes.; Required
- `user5` (user5) — Used for Conversion Import ID

### `icswu`
**IC Whse Product Usage**
Fields: `cono` (inte) [i], `prod` (char) [im], `whse` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `lastmergedt` (date), `firstmergedt` (date), `normusage` (deci-2[25]), `overreasty` (char[25]), `overusage` (deci-2[25]), `nodaysso` (inte[25]), `user1` (char), `notimesso` (inte[25]), `user2` (char), `avginvval` (deci-2[25]), `user3` (char), `transusage` (deci-2[25]), `user4` (char), `unitcost` (deci-5[25]), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `linehits` (inte[25]), `linehitswt` (inte[25]), `linehitslb` (inte[25]), `highsales` (char[25]), `highsaleswt` (char[25]), `highsaleswtdt` (char[25]), `highsalesdt` (char[25]), `highsalesno` (char[25]), `highsaleswtno` (char[25]), `xxc15` (char), `xxde13` (deci-2), `xxde14` (deci-2), `xxde15` (deci-2), `lastavginvdt` (date), `normusage26` (deci-2), `transusage26` (deci-2), `overusage26` (deci-2), `overreasty26` (char), `transdttmz` (datetm-tz) [i], `firstmergedttz` (datetm-tz), `lastavginvdttz` (datetm-tz), `lastmergedttz` (datetm-tz), `rowpointer` (char) [i], `id` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `pallet_id` (char) [i], `abs_num` (char) [im], `ns_comment` (char), `uom` (char), `bin_num` (char) [im], `date_time` (char) [i], `expiration` (date) [i], `total_qty` (deci-2) [i], `reserved_qty` (deci-2), `truck_id` (char), `lot` (char) [i], `cycle_flag` (logi) [im], `cycle_level` (char), `cycle_emp_num` (char), `cycle_id` (inte) [i], `rtn_category` (char) [i], `rtn_pallet_full` (logi) [i], `attributes` (char), `task_id` (inte) [i], `suggested_bin` (char), `emp_num` (char), `vendor_id` (char) [m], `po_number` (char), `po_suffix` (char), `item_cost` (deci-2), `country_code` (char), `order` (char), `order_suffix` (char), `cargo_control` (char) [i], `custom_data` (char[5]), `stock_stat` (char) [im], `cross_dock_order` (char), `cross_dock_order_suffix` (char), `case_quantity` (deci-4), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `expirationtz` (datetm-tz), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `abs_num` (char) [i], `ei_type` (char) [i], `ei_id` (char) [i], `ei_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `adj_code` (char) [im], `adj_desc` (char) [m], `enter_loc` (logi) [m], `tran_types` (char), `valid_status_1` (logi), `valid_status_2` (logi), `status_1` (char), `status_2` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `inv_prob_id` (inte) [im], `trans_num` (inte) [im], `trans_type` (char) [i], `co_num` (char) [i], `wh_num` (char) [im], `bin_num` (char) [i], `exp_bin` (char), `pallet_id` (char), `exp_pallet` (char), `abs_num` (char) [im], `lot` (char), `item_num` (char) [m], `actual_qty` (deci-2), `exp_qty` (deci-2), `printed` (logi) [m], `custom_data` (char[5]), `case_quantity` (deci-4), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `lot_before` (char), `trans_datetz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP/ICSW; Required
- `whse` (Whse) — Can be CHAR(24) if using xref; Valid values/xref: ICSD; Required
- `overreasty1` (Override Reason Current Month) — Valid values/xref: SASTT -O
- `overreasty2` (Override Reason Prior Month) — Valid values/xref: SASTT -O
- `overreasty3` (Override Reason Prior Month 2) — Valid values/xref: SASTT -O
- `overreasty4` (Override Reason Prior Month 3) — Valid values/xref: SASTT -O
- `overreasty5` (Override Reason Prior Month 4) — Valid values/xref: SASTT -O
- `overreasty6` (Override Reason Prior Month 5) — Valid values/xref: SASTT -O
- `overreasty7` (Override Reason Prior Month 6) — Valid values/xref: SASTT -O
- `overreasty8` (Override Reason Prior Month 7) — Valid values/xref: SASTT -O
- `overreasty9` (Override Reason Prior Month 8) — Valid values/xref: SASTT -O
- `overreasty10` (Override Reason Prior Month 9) — Valid values/xref: SASTT -O
- `overreasty11` (Override Reason Prior Month 10) — Valid values/xref: SASTT -O
- `overreasty12` (Override Reason Prior Month 11) — Valid values/xref: SASTT -O
- `overreasty13` (Override Reason Prior Month 12) — Valid values/xref: SASTT -O
- `overreasty14` (Override Reason Prior Month 13) — Valid values/xref: SASTT -O
- `overreasty15` (Override Reason Prior Month 14) — Valid values/xref: SASTT -O
- `overreasty16` (Override Reason Prior Month 15) — Valid values/xref: SASTT -O
- `overreasty17` (Override Reason Prior Month 16) — Valid values/xref: SASTT -O
- `overreasty18` (Override Reason Prior Month 17) — Valid values/xref: SASTT -O
- `overreasty19` (Override Reason Prior Month 18) — Valid values/xref: SASTT -O
- `overreasty20` (Override Reason Prior Month 19) — Valid values/xref: SASTT -O
- `overreasty21` (Override Reason Prior Month 20) — Valid values/xref: SASTT -O
- `overreasty22` (Override Reason Prior Month 21) — Valid values/xref: SASTT -O
- `overreasty23` (Override Reason Prior Month 22) — Valid values/xref: SASTT -O
- `overreasty24` (Override Reason Prior Month 23) — Valid values/xref: SASTT -O
- `overreasty25` (Override Reason Prior Month 24) — Valid values/xref: SASTT -O
- `overreasty26` (Override Reason Prior Month 25) — Valid values/xref: SASTT -O
- `user5` (user5) — Used for Conversion Import ID

### `inv_adj`
**Holds adjustments/corrections to inventory**

### `inv_prob`
**Contains discrepancy records**

### `inventory`
**Contains all active inventory**
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `wh_num` (Warehouse) — Can be CHAR(24) if Using Whse Cross Reference; Valid values/xref: ICSD, TWL-WHMST; Required
- `bin_num` (Location ID) — Do not include dashes or slashes; Valid values/xref: TWL-BINMST; Required
- `abs_num` (Item Number) — Can use Product Cross Reference; Valid values/xref: ICSW, TWL-ITEM or ICEAN for Nonstock; Required
- `pallet_id` (Pallet ID See notes below) — Required if binmst loc_type is P, B, or T.; Valid values/xref: Requires format of "P" plus 9 digits
- `lot` (Lot Number) — Required if item.lot_ctrl = true. One record per whse/bin/product/lot; Valid values/xref: ICSEL
- `stock_stat` (Stock Status) — (O)verage, (I)nv. Hold / Damage, (T)rans. Hold / Damage, (S)crap, (L)iquidation, (R)eturn to Vendor, (Q)A Hold, (W)ork in Process, Return (H)old, (C)ustomer Hold or Blank; Valid values/xref: O, I, T, S, L, R, Q, W, H, C or Blank; Default: Blank
- `total_qty` (Total Quantity) — Total quantity of this item in this bin
- `uom` (Unit of Measure) — Valid values/xref: TWL-UOM; Default: ITEM uom
- `vendor_id` (Vendor) — Valid values/xref: APSV, TWL-VENMST; Default: ICSW arpvendno
- `custom_data5` (Custom User Field 5) — Used for Import ID

### `inventoryei`
**Inventory Extended Information**

### `item`
**The master item table**
**Operators call this:** "Product Code (UPC)" (TWL), "Product Item" (TWL), "Product Name" (TWL), "Product Group" (TWL), "Warehouse Zone (of Product)" (TWL)
Fields: `co_num` (char) [i], `wh_num` (char) [im], `prod_grp` (char) [i], `prod_line` (char) [i], `prod_subline` (char) [i], `rtn_category` (char), `abs_num` (char) [im], `item_num` (char) [i], `upc_num` (char) [i], `item_desc` (char), `item_sec_desc` (char), `item_long_desc` (char), `uom` (char), `box_qty` (inte), `max_lvl` (deci-2), `min_lvl` (deci-2), `reo_qty` (deci-2), `wh_zone` (char), `aisle` (inte), `last_count` (char), `abc` (char) [i], `item_type` (char) [m], `pilferage_flag` (logi) [m], `rot_count` (inte), `gl_num` (char), `tracking_num` (inte), `msds_flag` (logi), `serial_flag` (logi) [m], `serial_by_location` (logi), `serial_outbound` (logi) [m], `serial_inbound` (logi), `lot_ctrl` (logi), `kit_flag` (logi) [m], `shelf_life_flag` (logi), `shelf_life` (inte), `length` (deci-5), `height` (deci-5), `width` (deci-5), `cube` (deci-5), `weight` (deci-5), `dim_weight` (deci-5), `ytd_cc_unit_var` (deci-2), `ytd_cc_dollar_var` (deci-2), `ytd_phy_unit_var` (deci-2), `ytd_phy_dollar_var` (deci-2), `item_cost` (deci-4), `sell_price` (deci-4), `acceptable_over` (inte), `self_ship` (logi) [m], `qa_inspection` (logi), `qa_instructions` (char), `customs_hold` (logi), `drop_ship` (logi), `force_ship` (logi) [m], `expiration_from` (char), `rcv_threshold` (inte), `shp_threshold` (inte), `unavailable_at` (char), `same_lot` (logi), `freight_class` (char), `oversized` (logi) [m], `plt_block` (inte), `plt_high` (inte), `counter_zone` (char), `kit_build_zone` (char), `msds_sheet` (char), `msds_sheet_bin` (char) [m], `msds_send_always` (logi) [m], `country_of_origin` (logi), `cust_code` (char) [m], `bo_qty` (deci-2), `package_code` (char), `stack_height` (inte), `custom_data` (char[5]), `row_status` (logi) [m], `labor_auto_ship` (char), `case_quantity` (deci-4), `pallet_quantity` (deci-4), `trans_user` (char), `abc_pending` (char) [i], `trans_date` (char), `trans_proc` (char), `putaway_group` (char) [i], `keyindex` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `transdttmz` (datetm-tz) [i], `whole_ship_flag` (logi) [m], `last_counttz` (datetm-tz), `trans_datetz` (datetm-tz)

### `item_alloc`
**Reserves allocated inventory (i.e.: makes it unavailable)**

### `item_history`
**Holds the history of an item (receipts, adjustments, shipments, returns) for trending**

### `itemei`
**Item Extended Information**
Fields: `co_num` (char) [im], `wh_num` (char) [im], `abs_num` (char) [i], `ei_type` (char) [i], `ei_id` (char) [i], `ei_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `id` (inte) [im], `date_time` (char) [im], `co_num` (char) [i], `wh_num` (char) [im], `type` (char) [im], `key1` (inte) [i], `key2` (inte) [i], `key3` (inte) [i], `abs_num` (char) [im], `lot` (char) [i], `quantity` (deci-2) [m], `emp_num` (char), `trans_num` (inte), `comment` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `altparentwhse` (char), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [im], `rec_date` (date) [i], `rec_type` (char) [i], `stock_stat` (char) [im], `abs_num` (char) [im], `lot` (char) [i], `start_bal` (deci-2), `receipts` (deci-2), `returns` (deci-2), `adjustments` (deci-2), `shipments` (deci-2), `shipments_unsent` (deci-2), `end_bal` (deci-2), `rec_id` (inte) [i], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `rec_datetz` (datetm-tz), `trans_datetz` (datetm-tz)

### `jmec`
**Job Management Entry Change Order Request**
Fields: `cono` (inte) [i], `jobid` (char) [im], `jobrevno` (inte) [im], `changereqno` (inte) [i], `statustype` (char), `openinit` (char), `createdt` (date), `canceldt` (date), `apprdt` (date), `completedt` (date), `apprcustname` (char), `apprintrname` (char), `apprdesc` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `jmech`
**Job Management Entry Change Order Request - Header**
Fields: `cono` (inte) [im], `jobid` (char) [im], `jobrevno` (inte) [im], `quoteno` (inte) [m], `custno` (deci-0), `shipto` (char), `whse` (char) [m], `stagecd` (inte) [m], `enterdt` (date) [m], `entertm` (char) [m], `duedt` (date), `begindt` (date), `expiredt` (date), `awarddt` (date), `reqshipdt` (date), `promisedt` (date), `descrip` (char[2]), `takenby` (char) [m], `awardnm` (char), `awarddesc` (char), `custpo` (char), `contact` (char), `contactphno` (char), `notesfl` (char), `lostbusty` (char), `openinit` (char), `commtype` (char), `termstype` (char), `slsrepin` (char), `slsrepout` (char), `pricetype` (char), `pricecd` (inte), `disccd` (inte), `relprocessfl` (logi) [m], `relcompfl` (logi) [m], `relinit` (char), `refer` (char) [m], `transtype` (char) [m], `restrictty` (char), `orderdisp` (char), `opentorelfl` (logi) [m], `shipviaty` (char), `lumpbillamt` (deci-2), `lumpbillfl` (logi) [m], `lumppricefl` (logi) [m], `arpwhse` (char), `approvty` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `vendno` (deci-0), `totprice` (deci-2), `totcost` (deci-2), `totmargin` (deci-2), `prodline` (char), `printtype` (char), `minmargin` (deci-2), `changereqno` (inte) [i], `totextprice` (deci-2), `totextcost` (deci-2), `shiptoaddr` (char[2]), `shiptoaddr3` (char), `shiptocity` (char), `shiptonm` (char) [m], `shiptost` (char), `shiptozip` (char), `shiptofaxphoneno` (char), `shiptophoneno` (char), `canceldt` (date), `costapprovfl` (logi) [m], `prcapprovfl` (logi) [m], `relpricefl` (logi) [m]

### `jmecl`
**Job Management Line Item**
Fields: `cono` (inte) [im], `jobid` (char) [im], `jobrevno` (inte) [im], `lineno` (inte) [im], `whse` (char) [m], `linetype` (char) [m], `prod` (char) [m], `qtyord` (deci-2), `reqprod` (char), `price` (deci-5), `xrefprodty` (char), `cost` (deci-5), `icspecrecno` (inte), `marginpct` (deci-2), `extprice` (deci-2), `vendno` (deci-0), `extcost` (deci-2), `prodline` (char), `extmargin` (deci-2), `taxablety` (char), `lastcost` (deci-5), `lastprice` (deci-5), `prodcat` (char), `lastmarginpct` (deci-2), `commtype` (char), `lastextprc` (deci-2), `kitfl` (logi) [m], `lastextcst` (deci-2), `kitrollty` (char), `lastextmrgn` (deci-2), `qtybreakty` (char), `descrip` (char[2]), `promofl` (logi) [m], `linestat` (char), `printtype` (char), `notimeschg` (inte), `awardty` (char), `commentfl` (logi) [m], `relprocessfl` (logi) [m], `unit` (char), `relaccepttype` (char), `unitconv` (deci-5), `pdrecno` (inte), `priceoverfl` (logi) [m], `pricetype` (char), `baseprice` (deci-5), `listprice` (deci-5), `awardprice` (deci-5), `pdcost` (deci-5), `prodcost` (deci-5), `costoverfl` (logi) [m], `lockprfl` (logi) [m], `lockcsfl` (logi) [m], `lockvnfl` (logi) [m], `lastcstovfl` (logi) [m], `lastprcovfl` (logi) [m], `lastvendno` (deci-0), `lastlockfl` (char), `ordertype` (char), `cataddfl` (logi) [m], `reqshipdt` (date), `promisedt` (date), `duedt` (date), `shipfmno` (inte), `arpwhse` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `transtype` (char), `autoreceiptfl` (logi) [m], `compupdtfl` (logi) [m], `origlineno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `qtyrel` (deci-2), `specnstype` (char), `lostbusty` (char), `netord` (deci-2), `minmargin` (deci-2), `orderaltno` (inte), `linealtno` (inte), `disccd` (inte), `changereqno` (inte) [i], `discamt` (deci-5), `changetype` (char), `discpct` (deci-5), `disctype` (logi) [m], `pricecd` (deci-2), `priceclty` (char), `groupnm` (char), `canceldt` (date), `custno` (deci-0), `pricetypefl` (logi) [m], `pdsvcrecno` (inte)

### `jmeh`
**Job Management Entry Header**
Fields: `cono` (inte) [im], `jobid` (char) [im], `jobrevno` (inte) [im], `quoteno` (inte) [im], `custno` (deci-0), `shipto` (char), `whse` (char) [m], `stagecd` (inte) [m], `enterdt` (date) [im], `entertm` (char) [m], `duedt` (date), `begindt` (date), `expiredt` (date), `awarddt` (date), `reqshipdt` (date), `promisedt` (date), `descrip` (char[2]), `takenby` (char) [m], `awardnm` (char), `awarddesc` (char), `custpo` (char), `contact` (char), `contactphno` (char), `notesfl` (char), `lostbusty` (char), `openinit` (char), `commtype` (char), `termstype` (char), `slsrepin` (char), `slsrepout` (char), `pricetype` (char), `pricecd` (inte), `disccd` (inte), `relprocessfl` (logi) [m], `relcompfl` (logi) [m], `relinit` (char), `refer` (char) [m], `transtype` (char) [m], `restrictty` (char), `orderdisp` (char), `opentorelfl` (logi) [m], `shipviaty` (char), `lumpbillamt` (deci-2), `lumpbillfl` (logi) [m], `lumppricefl` (logi) [m], `arpwhse` (char), `approvty` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `vendno` (deci-0), `totprice` (deci-2), `totcost` (deci-2), `totmargin` (deci-2), `prodline` (char), `printtype` (char), `minmargin` (deci-2), `totextprice` (deci-2), `totextcost` (deci-2), `shiptoaddr` (char[2]), `shiptoaddr3` (char), `shiptocity` (char), `shiptonm` (char) [m], `shiptost` (char), `shiptozip` (char), `shiptofaxphoneno` (char), `shiptophoneno` (char), `canceldt` (date), `costapprovfl` (logi) [m], `prcapprovfl` (logi) [m], `relpricefl` (logi) [m]

### `jmehc`
**Job Management Entry Header Customers**
Fields: `cono` (inte) [im], `jobid` (char) [im], `jobrevno` (inte) [im], `custno` (deci-0) [i], `sentdt` (date), `sentby` (char), `name` (char) [i], `contact` (char), `contactphno` (char), `slsrepin` (char), `slsrepout` (char), `notesfl` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `faxphoneno` (char), `addr3` (char), `prosno` (deci-0)

### `jmel`
**Job Management Line Item**
Fields: `cono` (inte) [im], `jobid` (char) [im], `jobrevno` (inte) [im], `lineno` (inte) [im], `whse` (char) [im], `linetype` (char) [im], `prod` (char) [im], `qtyord` (deci-2), `reqprod` (char), `price` (deci-5), `xrefprodty` (char), `cost` (deci-5), `icspecrecno` (inte), `marginpct` (deci-2), `extprice` (deci-2), `vendno` (deci-0), `extcost` (deci-2), `prodline` (char), `extmargin` (deci-2), `taxablety` (char), `lastcost` (deci-5), `lastprice` (deci-5), `prodcat` (char), `lastmarginpct` (deci-2), `commtype` (char), `lastextprc` (deci-2), `kitfl` (logi) [m], `lastextcst` (deci-2), `kitrollty` (char), `lastextmrgn` (deci-2), `qtybreakty` (char), `descrip` (char[2]), `promofl` (logi) [m], `linestat` (char) [i], `printtype` (char), `notimeschg` (inte), `awardty` (char), `commentfl` (logi) [m], `relprocessfl` (logi) [m], `unit` (char), `relaccepttype` (char) [i], `unitconv` (deci-5), `pdrecno` (inte), `priceoverfl` (logi) [m], `pricetype` (char), `baseprice` (deci-5), `listprice` (deci-5), `awardprice` (deci-5), `pdcost` (deci-5), `prodcost` (deci-5), `costoverfl` (logi) [m], `lockprfl` (logi) [m], `lockcsfl` (logi) [m], `lockvnfl` (logi) [m], `lastcstovfl` (logi) [m], `lastprcovfl` (logi) [m], `lastvendno` (deci-0), `lastlockfl` (char), `ordertype` (char), `cataddfl` (logi) [m], `reqshipdt` (date), `promisedt` (date), `duedt` (date), `shipfmno` (inte), `arpwhse` (char), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `origlineno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `qtyrel` (deci-2), `specnstype` (char) [i], `lostbusty` (char), `netord` (deci-2), `minmargin` (deci-2), `orderaltno` (inte), `linealtno` (inte), `disccd` (inte), `discamt` (deci-5), `discpct` (deci-5), `disctype` (logi) [m], `pricecd` (deci-2), `priceclty` (char), `groupnm` (char), `canceldt` (date) [i], `custno` (deci-0), `pricetypefl` (logi) [m], `pdsvcrecno` (inte)

### `jmelc`
**Job Management Line Customer Quote Detail**
Fields: `cono` (inte) [im], `jobid` (char) [im], `jobrevno` (inte) [im], `lineno` (inte) [im], `custno` (deci-0) [i], `name` (char) [i], `cstform` (deci-2[15]), `quote` (char), `quotedt` (date), `expiredt` (date), `cstformty` (char), `cost` (deci-5), `prod` (char) [im], `prodcost` (deci-5), `notesfl` (char), `pdcost` (deci-5), `transdt` (date) [m], `transtm` (char) [m], `operinit` (char) [m], `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `jmelk`
**Job Management Complimentary Products**
Fields: `cono` (inte) [i], `jobid` (char) [im], `jobrevno` (inte) [im], `lineno` (inte) [i], `seqno` (inte) [i], `shipprod` (char) [im], `serlottype` (char), `qtyneeded` (deci-2), `unit` (char), `transdt` (date), `transtm` (char), `operinit` (char), `whse` (char) [i], `price` (deci-5), `prodcost` (deci-5), `stkqtyord` (deci-2), `statustype` (char) [i], `specnstype` (char) [i], `qtyord` (deci-2), `user1` (char), `user2` (char), `conv` (deci-5), `pdrecno` (inte), `icspecrecno` (inte), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `proddesc` (char), `orderalttype` (char), `orderaltno` (inte), `linealtno` (inte), `transproc` (char)

### `jmelo`
**Job Management Line Order Ties**
Fields: `cono` (inte) [i], `jobid` (char) [i], `jobrevno` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `ordertype` (char) [i], `orderaltno` (inte) [i], `linealtno` (inte) [i], `orderaltsuf` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `jmelp`
**Job Management Line Customer Price Detail**
Fields: `cono` (inte) [im], `jobid` (char) [im], `jobrevno` (inte) [im], `lineno` (inte) [im], `defaultfl` (logi) [m], `prod` (char) [i], `enddt` (date), `hardmaxqtyfl` (logi) [m], `maxqty` (deci-2), `maxqtytype` (char), `notesfl` (char), `price` (deci-5), `startdt` (date) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `unit` (char), `unitconv` (deci-5), `pdrecno` (inte), `qtytype` (char), `qtyyymm` (char)

### `jmelv`
**Job Management Line Vendor Quote Detail**
Fields: `cono` (inte) [im], `jobid` (char) [im], `jobrevno` (inte) [im], `lineno` (inte) [im], `vendno` (deci-0) [i], `leadtime` (inte), `cstform` (deci-2[15]), `vendquote` (char), `quotedt` (date), `expiredt` (date), `linedisp` (char), `cstformty` (char), `cost` (deci-5), `prod` (char) [im], `prodcost` (deci-5), `notesfl` (char), `pdcost` (deci-5), `vendorprod` (char), `transdt` (date) [m], `transtm` (char) [m], `operinit` (char) [m], `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `unit` (char), `unitconv` (deci-5), `defaultfl` (logi) [m], `hardmaxqtyfl` (logi) [m], `maxqtytype` (char), `maxqty` (deci-2), `startdt` (date) [i], `pdsvcrecno` (inte), `qtytype` (char), `qtyyymm` (char)

### `jurtax`
**Tax jurisdiction totals**
Fields: `cono` (inte) [im], `rowpointer` (char) [i], `srcrowpointer` (char) [im], `jurtype` (char) [im], `baseamt` (deci-2), `twetaxamt` (deci-2), `disttaxamt` (deci-2), `vendtaxamt` (deci-2), `settamt` (deci-2), `settpct` (deci-4), `docid` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [im], `dispjurtype` (char) [i], `jurid` (inte) [im], `jurty` (inte), `jurname` (char), `exemptamt` (deci-2), `taxableamt` (deci-2), `disttaxamt` (deci-2), `taxamt` (deci-2), `taxrate` (deci-5), `taxid` (inte), `taxtype` (inte), `taxname` (char), `districtty` (inte), `shipfrgeocd` (inte), `shiptogeocd` (inte), `srcrowpointer` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `jurtaxdet`
**Jurisdiction tax detail**

### `kitdtl`
**Detail for the Kitmst table**
Fields: `id` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `abs_num` (char) [im], `qty` (deci-2) [m], `same_lot` (logi), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `kitmst`
**Table contains items which make up a kit and their quantities**
Fields: `id` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `kit_num` (char) [im], `pre_built` (logi), `assembly_required` (logi) [m], `assembly_instructions` (char), `dept_num` (inte), `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `kpet`
**Kit Production - Enter Transactions**
Fields: `seqaltno` (inte), `stagecd` (inte), `wono` (inte) [i], `stkqtyord` (deci-2), `whse` (char) [i], `stkqtyship` (deci-2), `refer` (char), `shipprod` (char) [im], `enterdt` (date) [m], `statustype` (logi) [im], `transdt` (date), `operinit` (char), `transtm` (char), `cono` (inte) [i], `requestprod` (char), `notimesprt` (inte), `unit` (char), `notesfl` (char), `prodcost` (deci-5), `qtyord` (deci-2), `prodcat` (char), `reqoptfl` (logi) [m], `serlottype` (char), `conv` (deci-5), `rrarinit` (char) [i], `ordertype` (char), `orderaltno` (inte), `orderaltsuf` (inte), `linealtno` (inte), `jrnlno` (inte), `statuscd` (char), `wmqtyship` (deci-2), `setno` (inte), `user1` (char), `user2` (char), `icspecrecno` (inte), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `wosuf` (inte) [i], `bostage` (inte), `boexistsfl` (logi) [m], `bofl` (logi) [m], `borelfl` (logi) [m], `bono` (inte), `qtyship` (deci-2), `openinit` (char), `transproc` (char), `custcost` (deci-5), `custqty` (deci-2), `esbprocessfl` (logi) [m], `verno` (inte) [i], `wordindexfl` (logi) [m], `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `enterdttz` (datetm-tz)

### `kpsg`
**Kit Production Setup - Groups**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `groupname` (char) [im], `seqno` (inte) [i], `comprod` (char) [i], `qtyneeded` (deci-2), `unit` (char), `reqfl` (logi) [m], `kitrollty` (char), `variablefl` (logi) [m], `subfl` (logi) [m], `compboty` (char), `sublistfl` (logi) [m], `refer` (char), `pricefl` (logi) [m], `printfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `npfl` (logi) [m], `rowpointer` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `type` (Record type) — G for KPSG Group or O for KPSO Option; Valid values/xref: G or O; Required
- `seqno` (Seq #) — Sequence number for components; Required
- `comprod` (Component Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `qtyneeded` (Qty Needed) — Qty of Component to Build 1 kit; Default: 1
- `unit` (Units) — Component Unit of Measure; Default: ICSP Stock Unit
- `reqfl` (Required Flag) — Only Used on Groups - Component is Required on Kit; Valid values/xref: Y or N; Default: Y
- `variablefl` (Variable Quantity Flag) — Component can have Variable Quantity; Valid values/xref: Y or N; Default: N
- `subfl` (Substitute Flag) — Only Used on Groups - Allow Substitution of Component from KPSS; Valid values/xref: Y or N; Default: N
- `sublistfl` (Sub From List) — Allow Substitution of Component from ICSEC; Valid values/xref: Y or N; Default: N
- `pricefl` (Price Flag) — Inlcude Component in Price Roll-Up; Valid values/xref: Y or N; Default: Y
- `printfl` (Print Flag) — Print Component on Invoice; Valid values/xref: Y or N; Default: Y
- `compboty` (Comp BO Type) — Component can be Back Ordered in OEET. B to allow BO or Blank to not allow. Available Starting 4.0; Valid values/xref: <Blank> or B
- `user5` (user5) — Used for Conversion Import ID
- `npfl` (National Program Flag) — Valid values/xref: Y or N; Default: N

### `kpsk`
**KP Kits**
Fields: `cono` (inte) [i], `prod` (char) [im], `seqno` (inte) [im], `comprod` (char) [i], `qtyneeded` (deci-2), `variablefl` (logi) [m], `subfl` (logi) [m], `refer` (char), `transdt` (date), `transtm` (char), `operinit` (char), `reqfl` (logi) [m], `compfl` (logi) [m], `unit` (char), `kitrollty` (char), `compboty` (char), `sublistfl` (logi) [m], `requestprod` (char), `comptype` (char) [im], `qtyfl` (logi) [m], `printfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `pricefl` (logi) [m], `user5` (char), `serlotfl` (logi) [m], `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `npfl` (logi) [m], `rowpointer` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — ICSP must be Kit Type P or B Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `seqno` (Seq #) — Sequence number for components; Required
- `comptype` (Component Type) — (C)omponent, (G)roup, (K)eyword, (O)ption or (R)eference; Valid values/xref: C, G, K, O, R or <Blank>; Default: C
- `comprod` (Component) — See Notes Below; Valid values/xref: ICSP; Required
- `qtyneeded` (Qty Needed) — Qty of Component to Build 1 kit; Default: 1
- `unit` (Units) — Component Unit of Measure; Default: ICSP unit stock
- `reqfl` (Required Flag) — Component is Required on Kit; Valid values/xref: Y or N; Default: Y
- `variablefl` (Variable Quantity Flag) — Component can have Variable Quantity; Valid values/xref: Y or N; Default: N
- `subfl` (Substitute Flag) — Allow Substitution of Component from KPSS; Valid values/xref: Y or N; Default: N
- `sublistfl` (Sub From List) — Allow Substitution of Component from ICSEC; Valid values/xref: Y or N; Default: N
- `pricefl` (Price Flag) — Inlcude Component in Price Roll-Up; Valid values/xref: Y or N; Default: Y
- `printfl` (Print Flag) — Print Component on Invoice; Valid values/xref: Y or N; Default: Y
- `compboty` (Comp BO Type) — Component can be Back Ordered in OEET. B to allow BO or Blank to not allow. Available Starting 4.0; Valid values/xref: <Blank> or B
- `user5` (user5) — Used for Conversion Import ID
- `npfl` (National Program Flag) — Valid values/xref: Y or N; Default: N

### `kpskv`
**KP Kits**
Fields: `cono` (inte) [im], `prod` (char) [im], `verno` (inte) [im], `seqno` (inte) [im], `comprod` (char) [i], `verrefer` (char), `vercrtdt` (date), `qtyneeded` (deci-2), `variablefl` (logi) [m], `subfl` (logi) [m], `refer` (char), `transdt` (date), `transtm` (char), `operinit` (char), `reqfl` (logi) [m], `compfl` (logi) [m], `unit` (char), `kitrollty` (char), `compboty` (char), `sublistfl` (logi) [m], `requestprod` (char), `comptype` (char) [im], `qtyfl` (logi) [m], `printfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `pricefl` (logi) [m], `user5` (char), `serlotfl` (logi) [m], `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `npfl` (logi) [m], `vercrtdttz` (datetm-tz)

### `kpsm`
**Tally Mix File**
Fields: `cono` (inte) [i], `prod` (char) [im], `whse` (char) [i], `comprod` (char) [im], `length` (inte), `pomixpct` (inte), `oemixpct` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `dlength` (deci-2)

### `kpso`
**Kit Production Setup - Options**
Fields: `cono` (inte) [i], `seqno` (inte) [i], `comprod` (char) [i], `qtyneeded` (deci-2), `variablefl` (logi) [m], `refer` (char), `transdt` (date), `transtm` (char), `operinit` (char), `unit` (char), `kitrollty` (char), `compboty` (char), `sublistfl` (logi) [m], `oneonlyfl` (logi) [m], `optionname` (char) [i], `pricefl` (logi) [m], `user1` (char), `printfl` (logi) [m], `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `rowpointer` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `type` (Record type) — G for KPSG Group or O for KPSO Option; Valid values/xref: G or O; Required
- `seqno` (Seq #) — Sequence number for components; Required
- `comprod` (Component Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `qtyneeded` (Qty Needed) — Qty of Component to Build 1 kit; Default: 1
- `unit` (Units) — Component Unit of Measure; Default: ICSP Stock Unit
- `reqfl` (Required Flag) — Only Used on Groups - Component is Required on Kit; Valid values/xref: Y or N; Default: Y
- `variablefl` (Variable Quantity Flag) — Component can have Variable Quantity; Valid values/xref: Y or N; Default: N
- `subfl` (Substitute Flag) — Only Used on Groups - Allow Substitution of Component from KPSS; Valid values/xref: Y or N; Default: N
- `sublistfl` (Sub From List) — Allow Substitution of Component from ICSEC; Valid values/xref: Y or N; Default: N
- `pricefl` (Price Flag) — Inlcude Component in Price Roll-Up; Valid values/xref: Y or N; Default: Y
- `printfl` (Print Flag) — Print Component on Invoice; Valid values/xref: Y or N; Default: Y
- `compboty` (Comp BO Type) — Component can be Back Ordered in OEET. B to allow BO or Blank to not allow. Available Starting 4.0; Valid values/xref: <Blank> or B
- `user5` (user5) — Used for Conversion Import ID
- `npfl` (National Program Flag) — Valid values/xref: Y or N; Default: N

### `kpss`
**Kit Production - Setup Substitutes**
Fields: `cono` (inte) [i], `prod` (char) [im], `seqno` (inte) [i], `comprod` (char) [i], `qtyneeded` (deci-2), `variablefl` (logi) [m], `subfl` (logi) [m], `refer` (char), `transdt` (date), `transtm` (char), `operinit` (char), `unit` (char), `kitrollty` (char), `compboty` (char), `sublistfl` (logi) [m], `oneonlyfl` (logi) [m], `printfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `co_num` (char) [im], `wh_num` (char) [im], `label_id` (char) [i], `ei_type` (char) [i], `ei_id` (char) [i], `ei_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `sys_name` (char) [i], `program_name` (char) [i], `proc_name` (char) [i], `label_id` (char) [i], `dd_file` (char), `label_file` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `labelei`
**Label Extended Information Table**

### `labelmst`
**Label Table**

### `links`
**File Links**
Fields: `cono` (inte) [i], `type` (char) [i], `primarykey` (char) [i], `secondarykey` (char) [i], `seqno` (inte) [i], `descrip` (char), `link` (char), `linkty` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `lrgimgnm` (char), `ecbatchnm` (char) [i], `cono` (inte) [im], `whse` (char) [im], `seq` (deci-0) [i], `custno` (deci-0) [im], `orderno` (inte), `ordersuf` (inte), `prod` (char) [im], `lineno` (inte), `price` (deci-5), `prodcost` (deci-5), `stkqtylost` (deci-2), `refer` (char), `lostbusty` (char) [i], `usagefl` (logi) [im], `transdt` (date), `module` (char), `operinit` (char), `mergedfl` (logi) [im], `transtm` (char), `enterdt` (date), `postdt` (date) [i], `transtype` (char) [im], `extractfl` (logi), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `enterdttz` (datetm-tz), `postdttz` (datetm-tz), `cono` (inte) [im], `setname` (char) [im], `colseqno` (inte) [im], `fieldname` (char) [i], `schemafieldname` (char), `datatype` (char), `fmt` (char), `fmtlength` (inte), `ext` (char), `extentnum` (inte), `lbl` (char), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz), `cono` (inte) [im], `setname` (char) [im], `critseqno` (inte) [im], `fieldname` (char), `schemafieldname` (char), `datatype` (char), `fmt` (char), `ext` (char), `extentnum` (inte), `lbl` (char), `fromvalue` (char), `tovalue` (char), `shortlist` (char), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz), `cono` (inte) [im], `setname` (char) [im], `seqno` (inte) [im], `rowpointer` (char), `key1` (char) [i], `key2` (char) [i], `key3` (char) [i], `key4` (char), `key5` (char), `descrip` (char), `statusoperation` (char) [i], `statustype` (char) [i], `errors` (char), `stalefl` (logi) [m], `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz), `key6` (char), `key7` (char), `key8` (char), `cono` (inte) [im], `setname` (char) [im], `seqno` (inte) [im], `colseqno` (inte) [im], `ofld` (char), `nfld` (char), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz)

### `lostbus`
**Lost Business**

### `mmcolumn`
**Mass Maintenance Columns**

### `mmcriteria`
**Mass Maintenance Criteria**

### `mmextract`
**Mass Maintenance Extraction Data**

### `mmextractcol`
**Mass Maintenance Extract Column Data**

### `mmhdr`
**Mass Maintenance Header**
Fields: `cono` (inte) [im], `setname` (char) [im], `descrip` (char), `tablename` (char) [i], `statustype` (char), `whereclause` (char), `recordlimit` (inte), `origrecordcnt` (inte), `createdt` (date), `openinit` (char), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz), `createdttz` (datetm-tz), `id` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `task_id` (inte) [i], `machine` (char), `pallet_id` (char), `abs_num` (char) [im], `lot` (char), `quantity` (deci-2), `bin_from` (char) [im], `bin_to` (char) [im], `zone_to` (char), `to_wh_num` (char) [m], `urgent` (logi), `movement_type` (char) [m], `prod_id` (inte), `prod_line` (inte), `batch` (inte) [i], `wh_zone` (char) [m], `dept_num` (inte) [m], `truck_id` (char) [i], `date_time` (char), `doc_id` (char), `custom_data` (char[5]), `row_status` (char) [im], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `order` (char) [i], `order_suffix` (char) [i], `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz)

### `movemst`
**Table contains movement requests (for replenishments,production scheduling, etc.)**

### `notes`
**Notes**
Fields: `cono` (inte) [i], `notestype` (char) [i], `primarykey` (char) [im], `printfl` (logi) [m], `transdt` (date) [i], `transtm` (char), `operinit` (char), `requirefl` (logi) [m], `noteln` (char[16]), `pageno` (inte) [i], `secondarykey` (char) [i], `securefl` (logi) [m], `origpageno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `printfl2` (logi) [m], `printfl3` (logi) [m], `printfl4` (logi) [m], `printfl5` (logi) [m], `notecategory` (char), `headerfl` (logi) [m], `transdttmz` (datetm-tz) [i], `rowpointer` (char) [i], `notestype` (char) [i], `primarykey` (char) [im], `printfl` (logi) [m], `transdt` (date) [i], `transtm` (char), `operinit` (char), `requirefl` (logi) [m], `noteln` (char[16]), `pageno` (inte) [i], `secondarykey` (char) [i], `securefl` (logi) [m], `origpageno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `notestype` (Type of Note) — (C)ustomer, (V)endor, (P)roduct, (G)Catalog, (O)rder, (CS)ShipTO, (AR)Invoice,(X)PO,(XP)PO RRAR, (BA)Batch Order, (CT)Contact; Valid values/xref: C, V, P, G, O, CS, AR, X,XP, BA or CT; Required
- `primarykey` (Primary Key) — See Chart Below Old Cross Ref length 50 for ICSP and ICSC available starting in 6.1.040 Product/Catalog can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: See Chart Below; Required
- `pageno` (Page #) — Up to 999 pages per Primary/Secondary Key; Default: Next Page #
- `printfl` (Printed) — See Chart Below; Valid values/xref: (Y)es or (N)o; Default: N
- `printfl2` (Printed Flag 2) — See Chart Below; Valid values/xref: (Y)es or (N)o; Default: N
- `printfl3` (Printed Flag 3) — See Chart Below; Valid values/xref: (Y)es or (N)o; Default: N
- `printfl4` (Printed Flag 4) — See Chart Below; Valid values/xref: (Y)es or (N)o; Default: N
- `printfl5` (Printed Flag 5) — See Chart Below; Valid values/xref: (Y)es or (N)o; Default: N
- `requirefl` (Required) — Require Note to display on screen. Required Notes should be Page 1.; Valid values/xref: (Y)es or (N)o; Default: N
- `securefl` (Secured) — Secure Note for only certain users; Valid values/xref: (Y)es or (N)o; Default: N
- `noteln[2]` (Note Line 2) — Can be length 255 if noteln3 is setup for file or URL
- `secondarykey` (Secondary Key) — See Chart Below
- `user5` (user5) — Used for Conversion Import ID
- `notecategory` (Note Category) — Valid values/xref: SASTA
- `printexpiredt` (Print Expire Date) — Product Notes Only
- `documentlist` (Print Documents) — Product Notes Only. See Chart Below
- `printallcustfl` (Print All Customers) — Product Notes Only; Valid values/xref: (Y)es or (N)o; Default: Y
- `restrictcustno` (Restrict to Customer) — Product Notes Only
- `printallvendfl` (Print All Vendors) — Product Notes Only; Valid values/xref: (Y)es or (N)o; Default: Y
- `restrictvendno` (Restrict to Vendor) — Product Notes Only
- `Notes Type` (Primary Key) — Secondary Key; Valid values/xref: Validation
- `C` (Customer Number) — Blank; Valid values/xref: ARSC
- `CS` (Customer Number) — Shipto; Valid values/xref: ARSS
- `AR` (Customer Number) — Invoice-Suffix; Valid values/xref: ARET
- `V` (Vendor Number) — Blank; Valid values/xref: APSV
- `P` (Product Number) — Blank; Valid values/xref: ICSP
- `G` (Catalog Product Number) — Blank; Valid values/xref: ICSG
- `O` (Order Number Uses DCAOO Closed Order # Prefix) — Blank; Valid values/xref: OEEH
- `X **` (PO Number) — Blank; Valid values/xref: POEH
- `XP *` (PO Reference) — Blank; Valid values/xref: POERAH
- `BA` (Batch Name) — Sequence # in Batch; Valid values/xref: OEEHB
- `CT ***` (First Name^Last Name Contact ID #) — Customer Number OR "ContactID#"; Valid values/xref: Contacts
- `X` (PO) — Pre-Receiver; Valid values/xref: N/A
- `CT` (N/A) — N/A; Valid values/xref: N/A

### `notescm`
**R&D Notes for TB's**

### `oeai`
**Operator Inquiries**
Fields: `oper2` (char) [i], `currproc` (char[20]), `transdt` (date), `transtm` (char), `operinit` (char), `cono` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `oeao`
**Contains order number ranges for entire company.**
Fields: `cono` (inte) [i], `oeassnty` (char), `begordno` (inte), `nextordno` (inte), `endordno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `ebuyoutdir` (char), `promoprcdflt` (char), `credduedtfl` (logi) [m], `lndtentfl` (logi) [m], `operinit` (char), `transdt` (date), `transtm` (char), `incval` (inte), `transproc` (char), `ccholdauthcd` (char), `ccholdfailcd` (char), `ccholdaddrcd` (char), `ccseconds` (inte), `ccsecondsbp` (inte), `ccretries` (inte), `ccretriesbp` (inte), `ccbatchminutes` (inte), `ccbatchsize` (inte), `shiptender` (char), `certifiedprompt` (char), `certifiedprint` (logi) [m], `authdefaultfl` (logi) [m], `promptcreatecardfl` (logi) [m], `lostbusreasonfl` (logi) [m], `synccrmarscfl` (logi) [m], `synccrmarssfl` (logi) [m], `synccrmapssfl` (logi) [m], `synccrmapsvfl` (logi) [m], `synccrmcontactsfl` (logi) [m], `synccrmcmspfl` (logi) [m], `synccrmsmsnfl` (logi) [m], `syncmddarscfl` (logi) [m], `syncmddicscfl` (logi) [m], `syncmddarssfl` (logi) [m], `syncmddicspfl` (logi) [m], `syncmddcontactsfl` (logi) [m], `syncmddcmspfl` (logi) [m], `syncmddoeehfl` (logi) [m], `oedolholdty` (char), `oemrgholdty` (char), `apinvtolminamt` (deci-2), `emoemarginty` (char), `dnrwttiety` (char), `multlvlcntrfl` (logi) [m], `multlvlprcfl` (logi) [m], `multlvlrebty` (char), `multlvlprodfl` (logi) [m]

### `oedc`
**Order Entry Direct Route Customer**
Fields: `cono` (inte) [i], `typecd` (char) [im], `key1` (char) [im], `key2` (char) [im], `longitude` (deci-4), `latitude` (deci-4), `fixedlocfl` (logi) [m], `equipcd` (char), `dstarttm` (char) [m], `dendtm` (char) [m], `fixedtm` (inte), `symbol` (inte), `drsize` (inte), `drcolor` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `manoverfl` (logi) [m], `user9` (date), `unloadrate` (deci-0)

### `oeds`
**Order Entry Direct Route Setup**
Fields: `cono` (inte) [i], `equipcd` (char) [i], `dstarttm` (char) [m], `dendtm` (char) [m], `fixedtm` (inte), `symbol` (inte), `size` (inte), `dcolor` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user9` (date), `whse` (char) [i], `unloadrate` (deci-0)

### `oeeda`
**Cash Drawers Reconcile Audit Records**
Fields: `cono` (inte) [im], `whse` (char) [im], `drawerid` (char) [im], `enterdttmz` (datetm-tz) [im], `updtfl` (logi) [im], `oper2` (char) [im], `startamt` (deci-2) [i], `totamt` (deci-2) [i], `cntamt` (deci-2) [i], `discamt` (deci-2) [i], `transdttmz` (datetm-tz), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oeede`
**Petty Cash Transactions**
Fields: `cono` (inte) [im], `whse` (char) [im], `drawerid` (char) [im], `jrnlno` (inte) [im], `setno` (inte) [im], `recfl` (logi) [im], `transty` (inte), `amount` (deci-2), `inoutfl` (logi) [m], `descrip` (char), `comment` (char), `gletfl` (logi) [m], `toinit` (char), `recdttmz` (datetm-tz), `transdttmz` (datetm-tz), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oeedj`
**Cash Drawers Daily Journal Records**
Fields: `cono` (inte) [im], `whse` (char) [im], `drawerid` (char) [im], `openfl` (logi) [im], `jrnlno` (inte) [im], `oper2` (char) [im], `recdttmz` (datetm-tz), `transdttmz` (datetm-tz), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oeeh`
**Order Entry Header**
**Operators call this:** "Customer" (Sales), "Ship Via" (Sales), "Stage" (Sales), "Taken By" (Sales), "Amount Tendered" (Sales), "Customer PO" (Sales), "Reference" (Sales), "Invoice Date" (Sales)
Fields: `orderno` (inte) [i], `ordersuf` (inte) [i], `transtype` (char) [m], `custno` (deci-0) [im], `shipto` (char), `custpo` (char) [i], `shiptonm` (char) [m], `shiptost` (char), `shiptozip` (char), `whse` (char) [im], `shipinstr` (char), `refer` (char), `shipviaty` (char), `placedby` (char), `reqshipdt` (date), `takenby` (char), `orderdisp` (char), `bofl` (logi) [m], `subfl` (logi) [m], `cono` (inte) [i], `invno` (inte), `invsuf` (inte), `stagecd` (inte) [i], `approvty` (char), `outbndfrtfl` (logi) [m], `inbndfrtfl` (logi) [m], `termstype` (char), `canceldt` (date), `billdt` (date), `storddays` (inte), `statecd` (char), `operinit` (char), `transdt` (date), `invoicedt` (date) [i], `paiddt` (date), `vendrebord` (deci-2), `vendrebamt` (deci-2), `pickeddt` (date), `totcommcost` (deci-2), `enterdt` (date), `setno2` (deci-0) [i], `drdeltm` (char), `countrycd` (char), `transtm` (char), `wletsetno` (char), `taxovercd` (char), `shiptoaddr` (char[2]), `nontaxtype` (char), `shiptocity` (char), `bpquoteno` (char), `norushln` (inte), `asndt` (date), `nolineitem` (inte), `ackdt` (date), `addonamt` (deci-2[4]), `poissdt` (date), `addontype` (logi[4]) [m], `createdt` (date), `addonno` (inte[4]), `usestepfl` (logi) [m], `drexpfl` (logi) [m], `totinvamt` (deci-2), `user3` (char), `totweight` (deci-5), `user4` (char), `totcubes` (deci-5), `user5` (char), `totqtyshp` (deci-2), `user6` (deci-5), `totqtyord` (deci-2), `user7` (deci-5), `user8` (date), `totlineamt` (deci-2), `user9` (date), `wodiscamt` (deci-2), `wodisctype` (logi) [m], `totcost` (deci-2), `slsrepin` (char), `slsrepout` (char), `taxauth` (char), `stagearea` (char), `totcommin` (deci-2), `termsdiscamt` (deci-2), `dwnpmtamt` (deci-2), `payamt` (deci-2[3]), `apprinit` (char), `termspct` (deci-2), `jrnlno` (inte) [i], `nosnlots` (deci-2), `notimeschg` (inte), `pickprno` (inte), `setno` (inte) [i], `stordty` (logi) [m], `wodiscoverfl` (logi) [m], `notesfl` (char), `nextlineno` (inte), `dwnpmttype` (logi) [m], `linefl` (logi) [m], `taxsaleamt` (deci-2[5]), `taxablefl` (logi) [m], `codfl` (logi) [m], `crreasonty` (char), `origorderno` (inte), `totcommout` (deci-2), `lumpbillfl` (logi) [m], `lumpbillamt` (deci-2), `borelfl` (logi) [m], `borelno` (inte), `lockfl` (logi) [m], `shipdt` (date), `totcorechg` (deci-2), `totordamt` (deci-2), `printpckfl` (logi) [m], `wodeftype` (char), `wodiscpct` (deci-2), `longltdays` (inte), `arpvendno` (deci-0), `arpwhse` (char), `totdatccost` (deci-2), `datcoverfl` (logi) [m], `bolinefl` (logi) [m], `totlineord` (deci-2), `totcostord` (deci-2), `specdiscamt` (deci-2), `totprice` (deci-2), `credoverfl` (logi) [m], `jobno` (char), `jrnlno2` (inte) [i], `prosno` (deci-0) [m], `proposalno` (deci-0), `lostbusty` (char), `pricecd` (inte), `totlineret` (deci-2), `taxamt` (deci-2[4]), `updtype` (char) [i], `pickprtfl` (logi) [m], `lumppricefl` (logi) [m], `boexistsfl` (logi) [m], `discdt` (date), `divno` (inte), `totqtyret` (deci-2), `pickinit` (char), `pkgid` (char), `openinit` (char), `nocatwght` (inte), `wtauth` (inte), `pickcnt` (inte), `addoverfl` (logi[4]) [m], `addonnet` (deci-2[4]), `addtaxgroup` (inte[4]), `termslinefl` (logi) [m], `termsdiscln` (deci-2), `langcd` (char), `invcnt` (inte), `nolnnotbo` (inte), `nopackages` (inte), `pstlicenseno` (char), `totinvord` (deci-2), `gsttype` (char), `origcanfl` (logi) [m], `psttaxamt` (deci-2), `user1` (char), `user2` (char), `pickedtm` (char), `shiptm` (char), `taxoverfl` (logi) [m], `route` (char), `entertm` (char) [m], `manzonefl` (logi) [m], `shippingpt` (char) [m], `pkglabel` (char), `actfreight` (deci-2), `promisedt` (date), `fpcustno` (deci-0), `dexfl` (logi) [m], `taxtypeau` (char), `codcollamt` (deci-2) [m], `zone` (char), `totrestkamt` (deci-2), `pmfl` (logi) [m], `bostage` (inte), `totqtyshpp` (deci-2), `prevaddamt` (deci-2), `prevaddtype` (logi) [m], `geocd` (inte), `arpcono` (inte), `tottendamt` (deci-2), `writeoffamt` (deci-2), `tendamt` (deci-2), `sourcepros` (char), `arpshipfmno` (inte), `nodolines` (inte), `taxsaleamt2` (deci-2[5]), `taxdefltty` (char), `totdatccost2` (deci-2), `totcorechg2` (deci-2), `restrictty` (char), `transproc` (char), `keyindex` (char), `currencyty` (char), `jmjobid` (char), `drholdfl` (logi) [m], `salesexrate` (deci-7), `extracted` (deci-2), `drdeldt` (date), `repairordno` (inte), `repairordsuf` (inte), `jmjobrevno` (inte), `contactid` (deci-0), `printpricefl` (logi) [m], `xxc11` (char), `xxc12` (char), `consolinvdt` (date), `shiptoaddr3` (char), `termsdisconpst` (deci-2), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `consolorderno` (inte), `email` (char), `contactnm` (char), `esbshipmentfl` (logi) [m], `esbinvoicefl` (logi) [m], `esbsalesorderfl` (logi) [m], `ccnonrefundfl` (logi) [m], `jrnlno3` (inte), `esbquotefl` (logi) [m], `recoveryfl` (logi) [m], `billonrcptfl` (logi) [m], `autoaltwhsefl` (logi) [m], `domtaxamt1` (deci-2), `domtaxamt2` (deci-2), `domtaxamt3` (deci-2), `domtaxamt4` (deci-2), `saleswhse` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `vatamt` (deci-2[5]), `outofcityfl` (logi) [m], `settdiscamt` (deci-2[5]), `spectaxcd` (char), `btprintfl` (logi) [m], `billdirectaddon` (char), `frttermscd` (char), `transferloc` (char), `origpromisedt` (date), `origpromisedtlockedfl` (logi) [m], `extshipinstr` (char), `frtbillacct` (char), `autoapplycreditfl` (logi) [m], `frtbillnm` (char), `frtbillst` (char), `frtbillzip` (char), `frtbilladdr` (char[2]), `frtbillcity` (char), `frtbilladdr3` (char), `frtbillcountrycd` (char), `frtbillcd` (char), `origincd` (char), `dlvprintty` (char), `origincopyty` (char), `dlvcnt` (inte), `originorderno` (inte), `originordersuf` (inte), `approvintlty` (char), `sfuser` (char), `noinvoicefl` (logi) [m], `shipmentnotice` (char), `servicekey` (char), `esbserviceordervarid` (int6), `esbediasnfl` (logi) [m], `esbediinvfl` (logi) [m], `esbedicustpoackfl` (logi) [m], `vendretauth` (char), `transdttmz` (datetm-tz) [i], `fulfillmentordfl` (logi) [m], `fulfillmenttiedfl` (logi) [m], `fulfillmentstgcd` (char), `fulfillmentbillcd` (char), `nplinecount` (inte), `nptotshipamt` (deci-2), `fulfillmentordno` (inte), `fulfillmentordsuf` (inte), `ordersource` (char), `relateddocument` (char), `ackdttz` (datetm-tz), `asndttz` (datetm-tz), `billdttz` (datetm-tz), `canceldttz` (datetm-tz), `consolinvdttz` (datetm-tz), `createdttz` (datetm-tz), `discdttz` (datetm-tz), `drdeldttz` (datetm-tz), `enterdttz` (datetm-tz), `invoicedttz` (datetm-tz), `origpromisedttz` (datetm-tz), `paiddttz` (datetm-tz), `pickeddttz` (datetm-tz), `poissdttz` (datetm-tz), `promisedttz` (datetm-tz), `reqshipdttz` (datetm-tz), `shipdttz` (datetm-tz), `lspinvregstatus` (char), `lspuuid` (char), `lspinvregstatdttmz` (datetm-tz), `arrevdttmz` (datetm-tz), `cartid` (char), `lspidentifier` (char[10]), `addressoverfl` (logi) [m], `confirmctnfl` (logi) [m], `bolimit` (inte), `ordrep1` (char), `ordrep2` (char), `ordrep3` (char), `ordrep4` (char), `ordrep5` (char), `orderreppct1` (deci-2), `orderreppct2` (deci-2), `orderreppct3` (deci-2), `orderreppct4` (deci-2), `orderreppct5` (deci-2)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `orderno` (Order #) — Order / Invoice Number. Length 7 digits prior to SX.e 4.0 Uses DCAOO Closed Order # Prefix; Required
- `ordersuf` (Order Suffix) — All orders numbers must start with a suffix 00 order. Backorders can use Suffix 01 - 98.; Valid values/xref: 00 to 98; Required; Default: 00
- `transtype` (Transaction Type) — (SO)Stock Order, (RM)Return, (DO)Direct, (CR)Correction, (CS)Counter Sale. See Chart Below.; Valid values/xref: SO, RM, DO, CR or CS; Required
- `custno` (Customer #) — If the Customer # is not valid in ARSC, the Admin Option Customer # will be used. Can be CHAR(24) if Customer Cross Reference used.; Valid values/xref: ARSC; Required; Default: DCAOO Default
- `shipto` (Ship To) — Valid values/xref: ARSS
- `whse` (Whse) — If the Whse is not valid in ICSD the Admin Option Warehouse will be used. Can be CHAR(24) if using xref.; Valid values/xref: ICSD; Required; Default: DCAOO Default
- `shiptonm` (Shipto Name) — Include if override name; Default: ARSC or ARSS
- `shiptoaddr1` (Ship Address1) — Include if override address; Default: ARSC or ARSS
- `shiptoaddr2` (Ship Address2) — Include if override address; Default: ARSC or ARSS
- `shiptoaddr3` (Ship Address 3) — Available starting with version 6.1.040. Include if override address; Default: ARSC or ARSS
- `shiptocity` (Shipto City) — Length 20 prior to 6.1.040 Include if override name & address; Default: ARSC or ARSS
- `shiptost` (Shipto State) — Not used with Freeform Style Address AO option starting in 6.1.040. Include if override address; Default: ARSC or ARSS
- `shiptozip` (Shipto Zip) — Include if override address; Default: ARSC or ARSS
- `countrycd` (Country) — Available Starting 10.0 Include if override address; Valid values/xref: SASTT-W; Default: ARSC or ARSS
- `shipviaty` (Ship Via) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-V; Default: ARSC or ARSS
- `termstype` (Terms) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-T; Default: ARSC or ARSS
- `slsrepout` (Outside Sales) — Can be CHAR(24) if using xref; Valid values/xref: SMSN; Default: ARSC or ARSS
- `slsrepin` (Inside Sales) — Can be CHAR(24) if using xref; Valid values/xref: SMSN; Default: ARSC or ARSS
- `invoicedt` (Invoiced Date) — Must include Invoice Date; Required
- `invno` (Invoice #) — See Chart Below
- `invsuf` (Invsuf) — Suffix for field above
- `divno` (Divno) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-V; Required; Default: ARSC or ICSD
- `actfreight` (Actual Freight) — Actual Freight Paid if different than Freight charged to customer. Always Positive
- `addonno1` (Addon No 1) — Addon Code from SASTO; Valid values/xref: SASTO
- `addonno2` (Addon No 2) — Addon Code from SASTO. Required if Addonnet is not 0.; Valid values/xref: SASTO
- `addonno3` (Addon No 3) — Addon Code from SASTO. Required if Addonnet is not 0.; Valid values/xref: SASTO
- `addonno4` (Addon No 4) — Addon Code from SASTO. Required if Addonnet is not 0.; Valid values/xref: SASTO
- `addonno5` (Addon No 5) — Addon Code from SASTO. Required if Addonnet is not 0. Available Starting 4.0; Valid values/xref: SASTO
- `addonno6` (Addon No 6) — Addon Code from SASTO. Required if Addonnet is not 0. Available Starting 4.0; Valid values/xref: SASTO
- `addonno7` (Addon No 7) — Addon Code from SASTO. Required if Addonnet is not 0. Available Starting 4.0; Valid values/xref: SASTO
- `addonno8` (Addon No 8) — Addon Code from SASTO. Required if Addonnet is not 0. Available Starting 4.0; Valid values/xref: SASTO
- `addonnet1` (Net Addon Amount 1) — Amount of Addon Charged to Customer. Negative is Credit to Customer.
- `addonnet2` (Net Addon Amount 2) — Amount of Addon Charged to Customer. Negative is Credit to Customer.
- `addonnet3` (Net Addon Amount 3) — Amount of Addon Charged to Customer. Negative is Credit to Customer.
- `addonnet4` (Net Addon Amount 4) — Amount of Addon Charged to Customer. Negative is Credit to Customer.
- `addonnet5` (Net Addon Amount 5) — Amount of Addon Charged to Customer. Negative is Credit to Customer. Available Starting 4.0
- `addonnet6` (Net Addon Amount 6) — Amount of Addon Charged to Customer. Negative is Credit to Customer. Available Starting 4.0
- `addonnet7` (Net Addon Amount 7) — Amount of Addon Charged to Customer. Negative is Credit to Customer. Available Starting 4.0
- `addonnet8` (Net Addon Amount 8) — Amount of Addon Charged to Customer. Negative is Credit to Customer. Available Starting 4.0
- `taxablefl` (Taxable) — Must be Yes if Tax Amounts > 0; Valid values/xref: Y or N; Default: N
- `nontaxtype` (No Tax Reason) — Required if TaxableFL is No.; Valid values/xref: SASTT-N; Default: ARSC
- `taxamt1` (Tax Amount (for Canada this is PST)) — State Tax Amount
- `taxamt2` (Tax Amount) — County Tax Amount
- `taxamt3` (Tax Amount) — City Tax Amount
- `taxamt4` (Tax Amount (For Canada this is GST)) — Other Tax Amount
- `taxsaleamt1` (Taxable Sale Amount) — State Taxable Sales Amount
- `taxsaleamt2` (Taxable Sale Amount) — County Taxable Sales Amount
- `taxsaleamt3` (Taxable Sale Amount) — City Taxable Sales Amount
- `taxsaleamt4` (Taxable Sale Amount) — Other 1 Taxable Sales Amount
- `taxsaleamt5` (Taxable Sale Amount) — Other 2 Taxable Sales Amount
- `domtaxamt1` (Domestic Tax Amt 1) — Available Starting 6.1
- `domtaxamt2` (Domestic Tax Amt 2) — Available Starting 6.1
- `domtaxamt3` (Domestic Tax Amt 3) — Available Starting 6.1
- `domtaxamt4` (Domestic Tax Amt 4) — Available Starting 6.1
- `saleswhse` (Sales Whse) — Added in 6.1 but never included in OEET so not used; Valid values/xref: ICSD; Default: Whse
- `frttermscd` (Freight Terms Code) — Available Starting 10.0; Valid values/xref: SASTT - FT
- `transferloc` (Transfer Location) — Available Starting 10.0
- `currencyty` (Currency Type) — Valid values/xref: SASTC
- `billonrcptfl` (Bill on Receipt Flag) — For storeroom orders only; Valid values/xref: Y or N; Default: N
- `recoveryfl` (Recovery Order Flag) — For storeroom orders only; Valid values/xref: Y or N; Default: N
- `employeeid` (Employee ID) — OEEHEXTRA table for storeroom orders only
- `employeename` (Employee Name) — OEEHEXTRA table for storeroom orders only
- `department` (Department) — OEEHEXTRA table for storeroom orders only
- `project` (Project) — OEEHEXTRA table for storeroom orders only
- `workordernum` (Work Order #) — OEEHEXTRA table for storeroom orders only
- `machinenum` (Machine #) — OEEHEXTRA table for storeroom orders only
- `origincopyty` (Origin Copy Type) — Blank - Not a copied order C - Sales Order Copy Q - Quote Order Copy F - Future Order Conversion S - Standing Order Conversion Available starting 10.2.0; Valid values/xref: Blank , C, Q, F, or S
- `originorderno` (Original Order Number) — Order number this order was copied from for reference Available starting 10.2.0
- `originordersuf` (Original Order Suf) — Order suffix this order was copied from for reference Available starting 10.2.0
- `origincd` (Origin Code) — Origin Code to indicate how the order originated; Valid values/xref: SASTT - OO
- `user5` (user5) — Used for Conversion Import ID and special Fix Flag for DCOCF
- `user10` (User10) — Available Starting 4.1
- `user11` (User11) — Available Starting 4.1
- `user12` (User12) — Available Starting 4.1
- `user13` (User13) — Available Starting 4.1
- `user14` (User14) — Available Starting 4.1
- `user15` (User15) — Available Starting 4.1
- `user16` (User16) — Available Starting 4.1
- `user17` (User17) — Available Starting 4.1
- `user18` (User18) — Available Starting 4.1
- `user19` (User19) — Available Starting 4.1
- `user20` (User20) — Available Starting 4.1
- `user21` (User21) — Available Starting 4.1
- `user22` (User22) — Available Starting 4.1
- `user23` (User23) — Available Starting 4.1
- `user24` (User24) — Available Starting 4.1
- `confirmctnfl` (All Packages Shipped) — Available starting 11.20.6; Valid values/xref: Y or N; Default: N
- `wodiscamt` (Whole Order Discount Amount) — Dollar or Percent based on wodisctype
- `wodisctype` (Whole Order Discount Type) — ($) - Dollar Amount (%) - Percentage; Valid values/xref: $ or %; Default: $
- `invverifyty` (Invoice Verification Type) — Available Starting 11.21.8; Valid values/xref: Y or N; Default: N

### `oeeha`
**Credit Card Transaction File**
Fields: `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `mediacd` (inte) [i], `cardno` (char) [i], `transcd` (char) [i], `seqno` (inte) [i], `processcd` (inte) [i], `commcd` (inte) [i], `processno` (inte) [i], `amount` (deci-2), `authamt` (deci-2), `saleamt` (deci-2), `preauthno` (inte), `category` (char), `response` (char), `mediaauth` (inte), `createdt` (date) [i], `createtm` (char) [i], `submitdt` (date) [i], `submittm` (char), `respdt` (date), `resptm` (char), `transdt` (date), `transtm` (char), `operinit` (char), `bankno` (inte), `statustype` (logi) [im], `currproc` (char), `avadd` (char), `avzip` (char), `destzip` (char), `taxamt` (deci-2), `cardid` (inte), `cmc` (char), `cmm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `charpreauth` (char), `charmediaauth` (char), `origamt` (deci-2), `bosuf` (inte), `origproccd` (inte), `exp` (char), `transproc` (char), `xxi15` (inte), `ccholdbofl` (logi) [m], `merchantid` (char), `createdttz` (datetm-tz), `respdttz` (datetm-tz), `submitdttz` (datetm-tz), `rowpointer` (char) [i]

### `oeehb`
**OE Batch Header**
Fields: `transtype` (char), `custno` (deci-0) [i], `shipto` (char), `custpo` (char), `shiptonm` (char), `shiptost` (char), `shiptozip` (char), `whse` (char), `shipinstr` (char), `refer` (char), `shipviaty` (char), `placedby` (char), `reqshipdt` (date), `takenby` (char), `orderdisp` (char), `bofl` (logi), `subfl` (logi), `cono` (inte) [i], `invno` (inte), `invsuf` (inte), `stagecd` (inte), `approvty` (char), `outbndfrtfl` (logi), `inbndfrtfl` (logi), `termstype` (char), `canceldt` (date), `billdt` (date), `statecd` (char), `operinit` (char), `transdt` (date), `enterdt` (date), `bpquoteno` (char), `restrictty` (char), `transtm` (char), `sourcepros` (char), `countrycd` (char), `shiptoaddr` (char[2]), `taxovercd` (char), `shiptocity` (char), `nontaxtype` (char), `addonamt` (deci-2[4]), `addontype` (logi[4]), `poissdt` (date), `addonno` (inte[4]), `usestepfl` (logi) [m], `totinvamt` (deci-2), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `totlineamt` (deci-2), `user9` (date), `wodiscamt` (deci-2), `wodisctype` (logi), `slsrepin` (char), `slsrepout` (char), `taxauth` (char), `dwnpmtamt` (deci-2), `payamt` (deci-2[3]), `wodiscoverfl` (logi), `notesfl` (char), `dwnpmttype` (logi), `taxsaleamt` (deci-2[5]), `taxablefl` (logi), `codfl` (logi), `crreasonty` (char), `wodiscpct` (deci-2), `datcoverfl` (logi), `specdiscamt` (deci-2), `credoverfl` (logi), `jobno` (char), `pricecd` (inte), `taxamt` (deci-2[4]), `divno` (inte), `addoverfl` (logi[4]), `addtaxgroup` (inte[4]), `langcd` (char), `gsttaxable` (deci-2), `gsttype` (char), `batchnm` (char) [i], `taxoverfl` (logi), `seqno` (inte) [i], `route` (char), `entertm` (char) [m], `shipdt` (date), `shiptm` (char), `promisedt` (date), `user1` (char), `user2` (char), `holdfl` (logi) [m], `dexfl` (logi), `orderno` (inte) [i], `pstlicenseno` (char), `totdatccost` (deci-2), `totcorechg` (deci-2), `totlineret` (deci-2), `totrestkamt` (deci-2), `inprocessfl` (logi), `geocd` (inte), `checkno` (deci-0), `taxdefltty` (char), `transproc` (char), `mediaauth` (inte[3]), `media` (char[3]), `mediacd` (inte[3]), `bankno` (inte), `charpreauth` (char), `charmediaauth` (char), `preauthno` (inte[3]), `avadd` (char[3]), `avzip` (char[3]), `destzip` (char[3]), `cardid` (inte[3]), `cmc` (char[3]), `cmm` (char[3]), `expdt` (char[3]), `shiptoaddr3` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `origincd` (char), `billdttz` (datetm-tz), `canceldttz` (datetm-tz), `enterdttz` (datetm-tz), `poissdttz` (datetm-tz), `promisedttz` (datetm-tz), `reqshipdttz` (datetm-tz), `shipdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `batchnm` (Batch Name) — Used to update the batch in OEEBU; Required
- `seqno` (Seq #) — Sequential number for transactions in a Batch; Required
- `custno` (Customer #) — Can be CHAR(24) if using xref; Valid values/xref: ARSC; Required
- `shipto` (Ship To) — Valid values/xref: ARSS
- `whse` (Whse) — Can be CHAR(24) if using xref; Valid values/xref: ICSD; Required
- `divno` (Division) — Determines GL Postings at Invoicing. Can be CHAR(24) if using xref; Valid values/xref: SASTT - V; Default: ICSD
- `transtype` (Transaction Type) — SO - Stock Order QU - Quote FO - Future Order RM - Return Material CR - Correction; Valid values/xref: SO,QU,FO,RM,CR; Required
- `placedby` (Placed By) — Name of customer placing order
- `shipviaty` (Ship Via) — Can be CHAR(24) if using xref; Valid values/xref: SASTT-S
- `inbndfrtfl` (Freight In Required) — Valid values/xref: Y or N; Default: N
- `outbndfrtfl` (Freight Out Required) — Valid values/xref: Y or N; Default: N
- `orderdisp` (Disposition) — S - Ship Complete T - Tag and Hold W - Will Call J - Just in Time Blank; Valid values/xref: <Blank>, S,T,W, or J
- `approvty` (Approval Type) — Y indicates Order is Approved, all other Letters indicate Order is on Credit Hold. If Blank, SX.e will perform standard credit check process.
- `termstype` (Terms) — Can be CHAR(24) if using xref; Valid values/xref: SASTT - T; Default: ARSC / ARSS
- `codfl` (COD Flag) — Y - COD Order; Valid values/xref: Y or N; Default: N
- `slsrepout` (Outside Salesrep) — Can be CHAR(24) if using xref; Valid values/xref: SMSN; Default: ARSC / ARSS
- `slsrepin` (Inside Salesrep) — Can be CHAR(24) if using xref Inside Salesrep is required on OEEHB, if ARSC/ARSS does not have assigned salesrep In then must be provided here or in takenby; Valid values/xref: SMSN; Default: ARSC /ARSS or takenby
- `canceldt` (Cancel Date) — For FO, SO and QU
- `takenby` (Taken By) — Operator who entered order Will be used as inside salesrep if that field is left blank
- `orderno` (Order #) — Can be blank and system will assign next number. If order already exists with this number, no order will be created.
- `addonno1` (Addon No 1) — Valid values/xref: SASTO
- `addontype1` (Addon Type 1) — $ or % for Amount; Valid values/xref: $ or %; Default: $
- `addonno2` (Addon No 2) — Valid values/xref: SASTO
- `addontype2` (Addon Type 2) — $ or % for Amount; Valid values/xref: $ or %; Default: $
- `addonno3` (Addon No 3) — Valid values/xref: SASTO
- `addontype3` (Addon Type 3) — $ or % for Amount; Valid values/xref: $ or %; Default: $
- `addonno4` (Addon No 4) — Valid values/xref: SASTO
- `addontype4` (Addon Type 4) — $ or % for Amount; Valid values/xref: $ or %; Default: $
- `wodiscamt` (Whole Order Discount) — Only used if WO Disc type is $
- `wodiscpct` (Whole Order Disc%) — Only used if WO Disc type is %
- `wodisctype` (Whole Order Disc Type) — $ or % for Whole Order Discount; Valid values/xref: $ or %; Default: %
- `shiptonm` (Ship To Name) — Include if override name & address; Default: ARSC / ARSS
- `shiptoaddr1` (Ship To Addr 1) — Include if override name & address; Default: ARSC / ARSS
- `shiptoaddr2` (Ship To Addr 2) — Include if override name & address; Default: ARSC / ARSS
- `shiptoaddr3` (Shipt To Addr 3) — Available starting with version 6.1.040.; Default: ARSC / ARSS
- `shiptocity` (Shipt To City) — Length 20 prior to 6.1.040; Default: ARSC / ARSS
- `shiptost` (Ship To State) — Not used with Freeform Style Address AO option starting in 6.1.040.; Default: ARSC / ARSS
- `shiptozip` (Ship To Zip) — Include if override name & address; Default: ARSC / ARSS
- `countrycd` (Country Code) — Blank for US; Valid values/xref: SASTT - W; Default: ARSC / ARSS
- `statecd` (Taxing State) — Blank if using Tax Cross Reference; Valid values/xref: SASGM; Required; Default: ARSC / ARSS
- `countycd` (County) — Blank if using Tax Cross Reference; Valid values/xref: SASGM; Default: ARSC / ARSS
- `citycd` (City) — Blank if using Tax Cross Reference; Valid values/xref: SASGM; Default: ARSC / ARSS
- `other1cd` (Other) — Blank if using Tax Cross Reference; Valid values/xref: SASGM; Default: ARSC / ARSS
- `other2cd` (Other) — Blank if using Tax Cross Reference; Valid values/xref: SASGM; Default: ARSC / ARSS
- `nontaxtype` (Non Tax Reason) — Can Use Tax Cross Reference; Valid values/xref: SASTT-N; Default: ARSC / ARSS
- `taxablefl` (Taxable Flag) — Can Use Tax Cross Reference; Valid values/xref: (Y)es or (N)o; Default: ARSC / ARSS
- `taxauth` (Taxing Entity) — Old Code for Use with Tax Cross Reference; Valid values/xref: Tax Cross Reference
- `dwnpmtamt` (Down Payment Amount) — Amount of Tendered Payment. Recommend re-entering tendering info in OEET manually.
- `dwnpmttype` (Down Payment Type) — Required for Tendered Payment. Down Payment amount is $ or %; Valid values/xref: $ or %; Default: $
- `bankno` (Bank #) — Required for Tendered Payment. Recommend re-entering tendering info in OEET manually.; Valid values/xref: CRSB
- `mediacd` (Payment Type) — Required for Tendered Payment. Recommend re-entering tendering info in OEET manually. Expanded to 2 digits in SX.e 6.0; Valid values/xref: SASTT - P
- `checkno` (Check #) — Optional for Tendered Payment, check number. Recommend re-entering tendering info in OEET manually.
- `media` (Payment Number) — Optional for Tendered Payment, credit card or other number. Recommend re-entering tendering info in OEET manually.
- `mediaauth` (Authorization) — Optional for Tendered Payment, credit card or other authorization number. Recommend re-entering tendering info in OEET manually.
- `origincd` (Origin Code) — Origin Code to indicate how the order originated; Valid values/xref: SASTT - OO
- `user5` (user5) — Used for Conversion Import ID
- `user10` (User10) — Available Starting 4.1
- `user11` (User11) — Available Starting 4.1
- `user12` (User12) — Available Starting 4.1
- `user13` (User13) — Available Starting 4.1
- `user14` (User14) — Available Starting 4.1
- `user15` (User15) — Available Starting 4.1
- `user16` (User16) — Available Starting 4.1
- `user17` (User17) — Available Starting 4.1
- `user18` (User18) — Available Starting 4.1
- `user19` (User19) — Available Starting 4.1
- `user20` (User20) — Available Starting 4.1
- `user21` (User21) — Available Starting 4.1
- `user22` (User22) — Available Starting 4.1
- `user23` (User23) — Available Starting 4.1
- `user24` (User24) — Available Starting 4.1

### `oeehbr`
**Order Entry Blanket Release Header**
Fields: `orderno` (inte) [i], `ordersuf` (inte) [i], `custno` (deci-0) [m], `shipto` (char), `shiptonm` (char) [m], `shiptost` (char), `shiptozip` (char), `shipinstr` (char), `shipviaty` (char), `reqshipdt` (date), `cono` (inte) [i], `billdt` (date), `operinit` (char), `transdt` (date), `transtm` (char), `shiptoaddr` (char[2]), `shiptocity` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `lumpbillfl` (logi) [m], `lumpbillamt` (deci-2), `lumppricefl` (logi) [m], `batchnm` (char) [i], `user1` (char), `seqno` (inte) [i], `promisedt` (date), `user2` (char), `transproc` (char), `shiptoaddr3` (char)

### `oeehc`
**Credit Hold Orders**
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `statustype` (logi) [im], `creditmgr` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `ourproc` (char), `approveinit` (char), `approvedt` (date), `approvetm` (char), `priority` (inte) [i], `comment` (char[2]), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `holdcnt` (inte), `transproc` (char), `approvedttz` (datetm-tz), `rowpointer` (char) [i]

### `oeehch`
**Order Entry Header Credit Hold Codes**
Fields: `cono` (inte) [im], `rowpointer` (char) [i], `orderno` (inte) [im], `ordersuf` (inte) [im], `statusfl` (logi) [im], `holdcd` (char) [im], `seqno` (inte) [im], `holddttz` (datetm-tz), `holdinit` (char), `approvedttz` (datetm-tz), `approvedinit` (char), `transdttmz` (datetm-tz) [i], `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `comment` (char)

### `oeehcx`
**Order Entry Certifications**
Fields: `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `certifiedtype` (char) [i], `certifiedname` (char) [i], `certifiednbr` (char), `certifiedorg` (char), `expiredt` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `employeeid` (char), `employeename` (char), `department` (char), `project` (char), `workordernum` (char), `machinenum` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `sruserdefined` (char[10]), `routetopartner` (char), `exchgtransty` (char), `shipmentnoticelist` (char)

### `oeehextra`
**Order Entry Header Extra**

### `oeehgc`
**Order Entry Gift Card Transactions**
Fields: `cono` (inte) [im], `orderno` (inte) [im], `ordersuf` (inte) [im], `seqno` (inte) [im], `amount` (deci-2), `cardno` (char) [i], `whse` (char) [im], `custno` (deci-0) [im], `mediacd` (inte), `statustype` (char) [im], `createoperinit` (char), `createdtz` (datetm-tz), `activationoperinit` (char), `activatedatetz` (datetm-tz), `lastreloadoperinit` (char), `lastreloaddtz` (datetm-tz), `transdttmz` (datetm-tz), `transproc` (char), `rowpointer` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `lastuseddatetz` (datetm-tz) [i]

### `oeehp`
**This table contains information about shipped packages**
Fields: `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `orderty` (char) [i], `statusty` (char) [i], `transty` (char), `pkgno` (inte), `trackerno` (char) [i], `addonamt` (deci-2), `freightamt` (deci-2), `shipviaty` (char) [i], `printernm` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cartonlist` (char), `actweight` (deci-5), `orgcodamt` (deci-2), `codaddchg` (deci-2), `actcodamt` (deci-2), `chgfrghtfl` (logi) [m], `shippedfl` (logi) [m], `transproc` (char), `resultmsg` (char), `whse` (char) [im], `carrierurl` (char), `rowpointer` (char) [i]

### `oeehqp`
**Order Entry Quote Order Pricing Records**
Fields: `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `type` (char) [i], `typekey` (char) [i], `vendno` (deci-0) [i], `lineno` (inte) [i], `startdt` (date), `enddt` (date), `jobno` (char), `useshiptofl` (logi) [m], `usewhsefl` (logi) [m], `overpdscfl` (logi) [m], `price` (deci-5), `prcform` (deci-2), `refer` (char), `pdrecno` (inte), `priceonty` (char), `termsdiscfl` (logi) [m], `termspct` (deci-2), `minqty` (deci-2), `commtype` (char), `operinit` (char), `transproc` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oeehs`
**Order Entry Header - Special Pricing**
Fields: `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `pricetype` (char) [i], `netamt` (deci-2), `nolineitem` (inte), `specdiscamt` (deci-2), `origdiscamt` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `discpct` (deci-3), `user1` (char), `user2` (char), `nextnet` (deci-2), `nextpct` (deci-3), `disctype` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `oeehta`
**Order Header Tendering Adjustments**
Fields: `cono` (inte) [im], `orderno` (inte) [im], `ordersuf` (inte) [im], `seqno` (inte) [im], `amount` (deci-2), `mediacd` (inte), `refer` (char), `gljrnlno` (inte), `glsetno` (inte), `gltransno` (inte), `postdt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oeel`
**Order Entry Line Items**
**Operators call this:** "Company" (Sales), "Warehouse" (Sales), "Order Outside Rep" (Sales), "Order Inside Rep" (Sales), "Transaction Type" (Sales), "Stock Status" (Sales), "Returned Flag" (Sales), "Price Override Flag" (Sales), "Credit Reason" (Sales), "Sales Value (Net)" (Sales), "Quantity Shipped" (Sales), "Cost of Goods Sold" (Sales), "Cost (Each)" (Sales), "Commission Cost" (Sales), "GL Cost" (Sales), "Whole-Order Discount Amount" (Sales), "Order Value" (Sales), "Order Quantity" (Sales), "Backorder Value" (Sales), "Invoice Number" (Sales), "Order Number" (Sales), "Order Suffix" (Sales), "Related Order Number" (Sales), "Vendor RMA" (Sales), "Line Number" (Sales), "Unit of Measure" (Sales), "Entered Date" (Sales), "Promise Date" (Sales), "Requested Ship Date" (Sales), "Lost Business Type" (Sales), "Transaction Type Name" (Sales), "Stage Name" (Sales), "Stock Status Name" (Sales)
Fields: `orderno` (inte) [i], `ordersuf` (inte) [i], `whse` (char) [im], `transtype` (char) [i], `shipto` (char), `lineno` (inte) [i], `custno` (deci-0) [i], `qtyord` (deci-2), `cono` (inte) [i], `proddesc` (char), `unit` (char), `price` (deci-5), `transdt` (date), `enterdt` (date) [i], `operinit` (char), `reqshipdt` (date), `discamt` (deci-5), `shipprod` (char) [im], `transtm` (char), `stkqtyship` (deci-2), `commamtin` (deci-2), `prodcost` (deci-5), `prodcat` (char), `arpprodline` (char) [i], `arpvendno` (deci-0) [i], `usagefl` (logi) [m], `orderaltno` (inte), `ordertype` (char) [i], `botype` (char), `netamt` (deci-2), `corechgty` (char), `specnstype` (char) [i], `commrate` (deci-2), `leadtm` (inte), `commratein` (deci-2), `reqprod` (char), `glcost` (deci-5), `xrefprodty` (char), `vendno` (deci-0), `wlpicktype` (char), `advertisingcode` (char), `weight` (deci-5), `ftcnote` (char), `cubes` (deci-5), `costtype` (char), `priceoverfl` (logi) [m], `discoverfl` (logi) [m], `prodline` (char), `shpqtyoverfl` (logi) [m], `icspecrecno` (inte), `tallyfl` (logi) [m], `notimeschg` (inte), `sxextractdt` (date), `statustype` (char) [i], `delayresrvfl` (logi) [m], `pdrecno` (inte), `ptlkitbofl` (logi) [m], `user3` (char), `printpckfl` (logi) [m], `user4` (char), `user5` (char), `chrgqty` (deci-2), `user6` (deci-5), `user7` (deci-5), `bono` (inte) [i], `user8` (date), `user9` (date), `commcost` (deci-5), `qtyfmrcvs` (deci-2), `salesterr` (char), `nosnlots` (deci-2), `returnfl` (logi) [m], `prevqtyshp` (deci-2), `commentfl` (logi) [m], `catwtfl` (logi) [m], `discpct` (deci-5), `qtyship` (deci-2), `taxablefl` (logi) [m], `linealtno` (inte), `promofl` (logi) [m], `disccd` (inte), `pricetype` (char), `lostbusty` (char), `priceclty` (char), `pricecd` (deci-2), `commamtout` (deci-2), `disctype` (logi) [m], `wtcono` (inte), `altwhse` (char), `corecharge` (deci-2), `nosnlotsk` (deci-2), `reasunavty` (char), `qtyrel` (deci-2), `datccost` (deci-5), `netord` (deci-2), `stkqtyord` (deci-2), `binloc` (char), `slsrepin` (char), `slsrepout` (char), `kitfl` (logi) [m], `qtyunavail` (deci-2), `jobno` (char), `discamtoth` (deci-2), `proddesc2` (char), `pricecostty` (char), `commtype` (char), `commpaidfl` (logi) [m], `kitrollty` (char), `printpricefl` (logi) [m], `subtotalfl` (logi) [m], `costoverfl` (logi) [m], `wodiscamt` (deci-2), `invoicedt` (date) [i], `crreasonty` (char), `commmanfl` (logi) [m], `taxgroup` (inte), `nontaxtype` (char), `termspct` (deci-2), `gststatus` (logi) [m], `tariffcd` (char), `commpaidinfl` (logi) [m], `user1` (char), `user2` (char), `wmqtyship` (deci-2), `taxablety` (char), `taxamount` (deci-2[4]), `warrtag` (char), `warrstagecd` (inte), `restockamt` (deci-2), `restockfl` (logi) [m], `returnty` (char), `qtyreturn` (deci-2), `retorderno` (inte), `retordersuf` (inte), `retlineno` (inte), `ostkqtyship` (deci-2), `warrexchgfl` (logi) [m], `promisedt` (date), `jitpickfl` (logi) [m], `cataddfl` (logi) [m], `dobotype` (char), `shipfmno` (inte), `unitconv` (deci-5), `restrictty` (char), `rushfl` (logi) [m], `transproc` (char), `keyindex` (char), `canceldt` (date), `chgtolineno` (inte), `restktaxgrp` (inte), `subtotaldesc` (char), `kitsplitamt` (deci-2), `priceorigcd` (char), `bonoptl` (inte), `corertnty` (char), `certifiednbr` (char), `certifiedorg` (char), `certifiedname` (char), `chgqtyfl` (logi) [m], `origcore` (char), `origlineno` (inte), `esrqstid` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `nonstkrevfl` (logi) [m], `nonstkaddfl` (logi) [m], `inventoryty` (char), `custcost` (deci-5), `cfgkitfl` (logi) [m], `hardpricefl` (logi) [m], `cutfl` (logi) [m], `cutlossamt` (deci-2), `scraplossamt` (deci-2), `crinvno` (inte), `crinvsuf` (inte), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `taxadjfl` (logi) [m], `contractno` (char), `contrstartdt` (date), `contrenddt` (date), `vendquote` (char), `replcost` (deci-5), `vabaseassembly` (char), `vaassemlgth` (deci-5), `quoteshipviaty` (char), `ncnr` (char), `verno` (inte), `eccnclasscd` (char), `countryoforigin` (char), `origpromisedt` (date), `systempdscrecid` (inte), `systemprice` (deci-5), `systemrefer` (char), `systemcontractno` (char), `systempricesheet` (char), `systemeffectivedate` (date), `systempriceonty` (char), `systempriceonamount` (deci-5), `systempdcostamt` (deci-5), `systempdcostty` (char), `hiprcorderno` (inte), `hiprcordersuf` (inte), `hiprclineno` (inte), `overridetype` (char), `hightolprice` (deci-5), `lowtolprice` (deci-5), `ehfamt` (deci-5), `ehfexemptamt` (deci-5), `ehfnetamt` (deci-2), `ehfaddonno` (inte), `pickmsds` (char), `altprodgrp` (char), `servicelinekey` (char), `vendretauth` (char), `npfl` (logi) [m], `pdsnrecno` (inte), `ehfinaddonfl` (logi) [m], `taxweight` (deci-5), `upcid` (char), `transdttmz` (datetm-tz) [i], `canceldttz` (datetm-tz), `enterdttz` (datetm-tz), `invoicedttz` (datetm-tz), `origpromisedttz` (datetm-tz), `promisedttz` (datetm-tz), `reqshipdttz` (datetm-tz), `sxextractdttz` (datetm-tz), `shipcompfl` (logi) [m], `arrevdttmz` (datetm-tz), `cartid` (char), `confirmctnfl` (logi) [m], `catchweightfl` (logi) [m], `totcatchweight` (deci-5), `ordrep1` (char), `ordrep2` (char), `ordrep3` (char), `ordrep4` (char), `ordrep5` (char), `orderreppct1` (deci-2), `orderreppct2` (deci-2), `orderreppct3` (deci-2), `orderreppct4` (deci-2), `orderreppct5` (deci-2)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `orderno` (Order #) — Uses DCAOO Closed Order # Prefix; Valid values/xref: OEEH; Required
- `ordersuf` (Order Suffix) — All orders numbers must start with a suffix 00 order. Backorders can use Suffix 01 - 98.; Valid values/xref: OEEH; Required
- `shipprod` (Shipped Product) — Will be setup as Non-stock if not found in ICSP/ICSW Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP/ICSW; Required
- `qtyord` (Quantity Ordered) — Enter as Negative if Return/Credit Line (allowed on SO, RM and CR); Required
- `qtyship` (Quantity Shipped) — Enter as Negative if Return/Credit Line (allowed on SO, RM and CR); Required
- `unit` (Selling Unit) — Only if different than ICSP stocking unit. Non-stocks will default to "EACH" if blank.; Valid values/xref: ICSEU or SASTT; Default: ICSP Stocking Unit
- `price` (Price) — per unit; Required
- `discamt` (Line Discount Amount) — per unit discount $ for line item
- `prodcost` (SM Cost) — per unit - No Cost on CR type; Required
- `glcost` (G/L Cost) — per unit - No Cost on CR type
- `commamtin` (Inside Commission) — Commission Amount Paid to Inside Salesrep
- `commamtout` (Oustside Commissn) — Commission Amount Paid to Outside Salesrep
- `commcost` (Commission Cost) — per unit - No Cost on CR type
- `taxablefl` (Tax Flag) — (Y)es or (N)o, was this line item taxed; Valid values/xref: Y or N; Default: N
- `taxamount1` (Tax Amount1) — State Tax Charged for Line
- `taxamount2` (Tax Amount2) — County Tax Charged for Line
- `taxamount3` (Tax Amount3) — City Tax Charged for Line
- `taxamount4` (Tax Amount4) — Other Tax Charged for Line
- `netord` (Net Line Ordered) — Ordered Qty Extended Price less Discount; Required
- `netamt` (Net Line Shipped) — Shipped Qty Extended Price less Discount; Required
- `reqprod` (Ordered Product) — Only used if different than shipped product. Must complete xrefprodty also. Supercede, Substitute and Upgrade will use produc xref. Old Cross Ref length 50 available starting in 6.1.040
- `xrefprodty` (ICSEC Type) — Type of Requested product: (C)ustomer, (I)nterchange, Su(P)erced, (S)ubstitute, (U)pgrade; Valid values/xref: C, I, P, S or U
- `proddesc` (Description) — Should only be used for non-stock products, stock products will default from ICSP.; Default: ICSP
- `proddesc2` (Description2) — Should only be used for non-stock products, stock products will default from ICSP.; Default: ICSP
- `prodcat` (Category) — Should only be used for non-stock products, stock products will default from ICSP. The Admin Option will be used if product category is blank or invalid. Can be CHAR(24) if using xref.; Valid values/xref: SASTT - C; Default: ICSP or DCAOO Default
- `vendno` (Vendor) — For Sales Analysis by Vendor, should be filled in for Non-stocks Only. Can be CHAR(24) if using xref.; Valid values/xref: APSV; Default: Stock Products - ICSW ARP Vendor
- `prodline` (Product Line) — For Sales Analysis by Product Line, should be filled in for Non-stocks Only. Can be CHAR(24) if using xref.; Valid values/xref: ICSL; Default: Stock Products - ICSW Prod Line
- `specnstype` (Special/Non-Stock Flag) — (S)pecial Order Product, (N)on-Stock Product, (L)ost Business Canelled Line or <Blank>. Will be set to (N) if no ICSW found. Note - Cancelled Lines (L) are NOT included in order totals.; Valid values/xref: <Blank>, S, N, or L
- `reqshipdt` (Requested Date) — Will default from header if blank.; Default: OEEH
- `promisedt` (Promise Date) — Will default from header if blank.; Default: OEEH
- `slsrepin` (Inside Sales Rep) — Will be pulled from the header if blank. Can be CHAR(24) if using xref.; Valid values/xref: SMSN; Default: OEEH
- `slsrepout` (Outside Sales Rep) — Will be pulled from the header if blank. Can be CHAR(24) if using xref.; Valid values/xref: SMSN; Default: OEEH
- `ncnr` (Non Cancellable/ Non Returnable Flag) — Available Starting 10.0 (Y)es or Blank (means no); Valid values/xref: Y or <blank>; Default: Stock Products - ICSW ncnr
- `eccnclasscd` (Export Control Classification Number) — Available starting in 10.0; Valid values/xref: SASTT-EC; Default: Stock Products - ICSP ECCN
- `countryoforigin` (Country of Origin) — Available Starting in 10.0.1; Valid values/xref: SASTT - W; Default: Stock Products - ICSW country of origin
- `tariffcd` (HS Code) — Available Starting in 10.0.1; Valid values/xref: SASGT; Default: Stock Products - ICSW HS Code
- `tallyfl` (Tally Flag) — (Y)es if this is a Tally Product.; Valid values/xref: Y or N; Default: N
- `custcost` (Customer Cost) — For Storeroom orders only
- `inventoryty` (Inventory Type) — For Storeroom orders only; Valid values/xref: (C) ustomer, (D)istributor or Blank
- `department` (Department) — OEELEXTRA table for Storeroom orders only
- `custglno` (Customer GL#) — OEELEXTRA table for Storeroom orders only
- `chargeno` (Charge #) — OEELEXTRA table for Storeroom orders only
- `lastpricepd` (Last Price Paid) — OEELEXTRA table for Storeroom orders only
- `origdt` (Origination Date) — OEELEXTRA table for Storeroom orders only
- `approvedt` (Approval Date) — OEELEXTRA table for Storeroom orders only
- `machinenum` (Machine #) — OEELEXTRA table for Storeroom orders only Available starting 10.1.1
- `user5` (user5) — Used for Conversion Import ID
- `user10` (User10) — Available Starting 4.1
- `user11` (User11) — Available Starting 4.1
- `user12` (User12) — Available Starting 4.1
- `user13` (User13) — Available Starting 4.1
- `user14` (User14) — Available Starting 4.1
- `user15` (User15) — Available Starting 4.1
- `user16` (User16) — Available Starting 4.1
- `user17` (User17) — Available Starting 4.1
- `user18` (User18) — Available Starting 4.1
- `user19` (User19) — Available Starting 4.1
- `user20` (User20) — Available Starting 4.1
- `user21` (User21) — Available Starting 4.1
- `user22` (User22) — Available Starting 4.1
- `user23` (User23) — Available Starting 4.1
- `user24` (User24) — Available Starting 4.1
- `shipcompfl` (OE Line Ship Complete) — Available starting 11.19.6; Valid values/xref: Y,N; Default: N
- `confirmctnfl` (All Packages Shipped) — Available starting 11.20.6; Valid values/xref: Y,N; Default: N

### `oeelb`
**OE Batch Line Items**
Fields: `lineno` (inte) [i], `qtyord` (deci-2), `cono` (inte) [i], `proddesc` (char), `unit` (char), `price` (deci-5), `transdt` (date), `enterdt` (date), `operinit` (char), `reqshipdt` (date), `discamt` (deci-5), `shipprod` (char), `transtm` (char), `prodcost` (deci-5), `prodcat` (char), `prodline` (char), `vendno` (deci-0), `usagefl` (logi), `ordertype` (char), `botype` (char), `netamt` (deci-2), `corechgty` (char), `specnstype` (char), `user1` (char), `user2` (char), `leadtm` (inte), `proddesc2` (char), `pricetype` (char), `priceoverfl` (logi), `xrefprodty` (char), `reqprod` (char), `bplineno` (inte), `commentfl` (logi), `rushfl` (logi), `user3` (char), `user4` (char), `user5` (char), `chrgqty` (deci-2), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `returnfl` (logi), `taxablefl` (logi), `disctype` (logi), `corecharge` (deci-2), `reasunavty` (char), `datccost` (deci-5), `stkqtyord` (deci-2), `slsrepin` (char), `slsrepout` (char), `jobno` (char), `commtype` (char), `printpricefl` (logi), `subtotalfl` (logi), `costoverfl` (logi), `crreasonty` (char), `taxgroup` (inte), `nontaxtype` (char), `termspct` (deci-2), `gststatus` (logi), `qtyunavail` (deci-2), `batchnm` (char) [i], `seqno` (inte) [i], `restockamt` (deci-2), `promisedt` (date), `jitpickfl` (logi), `cataddfl` (logi) [m], `shipfmno` (inte), `arpprodline` (char), `arpvendno` (deci-0), `icspecrecno` (inte), `transproc` (char), `restktaxgrp` (inte), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `quoteshipviaty` (char), `enterdttz` (datetm-tz), `promisedttz` (datetm-tz), `reqshipdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `batchnm` (Batch) — Same as Header Batch Name; Valid values/xref: OEEHB; Required
- `seqno` (Seq #) — Same as Header Seq; Valid values/xref: OEEHB; Required
- `lineno` (Line #) — Line # in this order; Required
- `shipprod` (Ship Product) — If not found in ICSP/ICSW, will be set to Non-Stock Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP/ICSW; Required
- `qtyord` (Quantity Ordered) — Negative allowed for Transaction Types SO, RM and CR only.; Required
- `unit` (Selling Unit) — Only if different than stocking unit; Valid values/xref: ICSEU
- `price` (Price) — per unit Price Leave blank for current OE pricing logic; Default: Current Pricing
- `priceoverfl` (Price Override Flag) — (Y)es or (N)o. Set to Yes to prevent any changes to price.; Valid values/xref: Y or N; Default: N
- `prodcost` (SM Cost) — per unit Cost Leave blank for current OE cost logic; Default: Current Cost
- `costoverfl` (Cost Override Flag) — (Y)es or (N)o. Set to Yes to prevent any changes to SM cost.; Valid values/xref: Y or N; Default: N
- `discamt` (Discount Amount) — Line Discount Amount in $ or % based on type.
- `disctype` (Discount Type) — $ or %; Valid values/xref: $ or %; Default: %
- `netamt` (Net Line Ordered) — Extended Price for Ordered Qty less Discount
- `slsrepin` (Inside Sales Rep) — Can be CHAR(24) if using xref.; Valid values/xref: SMSN; Default: OEEHB
- `slsrepout` (Outside Sales Rep) — Can be CHAR(24) if using xref.; Valid values/xref: SMSN; Default: OEEHB
- `commtype` (Commission Type) — If using SX.e Commission Reporting; Valid values/xref: SMSM; Default: SMSN Outside
- `corechgty` (Core Type) — Y = this line is eligible for a core charge N = this product does not have a core R = this is a core return line; Valid values/xref: <Blank>, Y, N, or R
- `prodcat` (Product Category) — Required for Non-Stock Products. Leave blank to use ICSP Product Category where available. Can be CHAR(24) if using xref.; Valid values/xref: SASTT - C
- `proddesc` (Description 1) — Required for Non-Stock Products. Leave blank to use ICSP Description where available.
- `proddesc2` (Description 2) — Required for Non-Stock Products. Leave blank to use ICSP Description where available.
- `vendno` (ARP Vendor) — Required for Non-Stock Products. If this field is blank, will use ICSW ARP Vendor if available. Can be CHAR(24) if using xref.; Valid values/xref: APSV
- `prodline` (Product Line) — Required for Non-Stock Products. If this field is blank, will use ICSW Product Line if available.; Valid values/xref: ICSL
- `reqprod` (Requested Prod) — Only used if different than shipped product. Must complete xrefprodty also. Standard Length 24. Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSEC
- `xrefprodty` (ICSEC Type) — Type of Requested product: (C)ustomer, (I)nterchange, Su(P)erced, (S)ubstitute, (U)pgrade; Valid values/xref: C, I, P, S, or U
- `taxablefl` (Tax Flag) — (Y)es or (N)o, is this line item taxed Leave Blank to execute current OE taxing logic; Valid values/xref: Y, N, or blank; Default: Current Taxing
- `taxgroup` (Tax Group) — Required for Non-Stock Products. If this field is blank, will use ICSW Tax Group if available.; Valid values/xref: SASC; Default: ICSW or 1 for non-stock
- `rushfl` (Rush Flag) — Valid values/xref: Y or N; Default: N
- `crreasonty` (Credit Memo Reason) — For Return Lines and CR Lines Only; Valid values/xref: SASTT - M
- `botype` (Back Order Type) — (Y)es backorder, (N)o don't backorder or (D)irect Ship Line Item - see notes below; Valid values/xref: Y, N or D; Default: Y
- `ordertype` (Order Type) — See Notes Below. (P)O, W(T), KP (W)O or VA (F)ab Order; Valid values/xref: <Blank>, P, T, W, or F
- `specnstype` (Special/Non-Stock type) — Must be N for Non-stock. If field is blank, will change to S for special if ICSW Status is Order As Needed.; Valid values/xref: <Blank>, N or S
- `reqshipdt` (Requested Ship Date for JIT) — Only used if OEEHB Disposition is J for JIT
- `promisedt` (Promise Date for JIT) — Only used if OEEHB Disposition is J for JIT
- `pricetype` (Pricetype) — Product Price Type; Valid values/xref: SASTT-K; Default: ICSW pricetype
- `user5` (user5) — Used for Conversion Import ID
- `user10` (User10) — Available Starting 4.1
- `user11` (User11) — Available Starting 4.1
- `user12` (User12) — Available Starting 4.1
- `user13` (User13) — Available Starting 4.1
- `user14` (User14) — Available Starting 4.1
- `user15` (User15) — Available Starting 4.1
- `user16` (User16) — Available Starting 4.1
- `user17` (User17) — Available Starting 4.1
- `user18` (User18) — Available Starting 4.1
- `user19` (User19) — Available Starting 4.1
- `user20` (User20) — Available Starting 4.1
- `user21` (User21) — Available Starting 4.1
- `user22` (User22) — Available Starting 4.1
- `user23` (User23) — Available Starting 4.1
- `user24` (User24) — Available Starting 4.1

### `oeelbr`
**Order Entry Blanket Release Line Items**
Fields: `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `qtyord` (deci-2), `cono` (inte) [i], `transdt` (date), `operinit` (char), `shipprod` (char) [m], `transtm` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `batchnm` (char) [i], `user1` (char), `seqno` (inte) [i], `user2` (char), `transproc` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char)

### `oeelc`
Fields: `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `linetype` (char) [im], `seqno` (inte) [i], `dspllineno` (inte) [i], `transproc` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `descrip` (char), `descrip1` (char), `intseqno` (inte) [i]

### `oeelcr`
**Correction and Return lines tied to Origintal order line**
Fields: `cono` (inte) [im], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `jrnlno` (int6), `setno` (int6), `transtype` (char) [i], `crrmorderno` (inte) [im], `crrmordersuf` (inte) [im], `crrmlineno` (inte) [im], `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `department` (char), `custglno` (char), `chargeno` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `lastpricepd` (deci-5), `promisedt` (date), `origdt` (date), `approvedt` (date), `machinenum` (char), `restrictdesc` (char), `certcode` (char), `certexpdt` (date), `certaccptdt` (date), `certaccptuser` (char), `certsaledt` (date), `restrictcd` (char), `certauthuser` (char), `restrictovrfl` (logi) [m], `restrictovrcom` (char), `sruserdefined` (char[10]), `srnsuserdefined` (char[10]), `custreserveovrfl` (logi) [m], `custreservecontractno` (char), `custreserverowpointer` (char), `custreserveovrpointer` (char), `approvedttz` (datetm-tz), `certaccptdttz` (datetm-tz), `certexpdttz` (datetm-tz), `certsaledttz` (datetm-tz), `origdttz` (datetm-tz)

### `oeelextra`
**Order Entry Line Extra**

### `oeelk`
**Order Entry Kit Components**
Fields: `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `shipprod` (char) [im], `stkqtyship` (deci-2), `subfl` (logi) [m], `variablefl` (logi) [m], `serlottype` (char), `qtyneeded` (deci-2), `unit` (char), `custno` (deci-0) [m], `transdt` (date), `transtm` (char), `operinit` (char), `shipto` (char) [m], `transtype` (char), `whse` (char) [i], `altwhse` (char), `price` (deci-5), `prodcat` (char), `prodcost` (deci-5), `stkqtyord` (deci-2), `prevprod` (char), `prevqtyship` (deci-2), `salesterr` (char), `statustype` (char) [i], `specnstype` (char) [i], `prevqtyord` (deci-2), `commcost` (deci-5), `comptype` (char) [m], `groupoptname` (char), `ordertype` (char) [i], `prevunit` (char), `pricefl` (logi) [m], `printfl` (logi) [m], `processtatfl` (logi) [m], `qtyord` (deci-2), `user1` (char), `qtyship` (deci-2), `user2` (char), `refer` (char), `glcost` (deci-5), `reqfl` (logi) [m], `reqprod` (char), `prevqtyrsv` (deci-2), `conv` (deci-5), `qtyreservd` (deci-2), `pdrecno` (inte), `compboty` (char), `wmqtyship` (deci-2), `prevspecns` (char), `prevconv` (deci-5), `instructions` (char), `wlpicktype` (char), `retseqno` (inte), `rbcparm` (char), `proddesc2` (char), `icspecrecno` (inte), `ovshipfl` (logi) [m], `delayresrvfl` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `arpvendno` (deci-0) [i], `arpprodline` (char) [i], `arpwhse` (char) [i], `proddesc` (char), `pricetype` (char), `orderalttype` (char), `orderaltno` (inte), `linealtno` (inte), `cataddfl` (logi) [m], `qtyfmrcvs` (deci-2), `costoverfl` (logi) [m], `transproc` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `custcost` (deci-5), `custqty` (deci-2), `cfgcompfl` (logi) [m], `cfgcompmodfl` (logi) [m], `leadtm` (inte), `countryoforigin` (char), `tariffcd` (char), `npfl` (logi) [m], `pdsnrecno` (inte), `rowpointer` (char) [i]

### `oeelm`
**Order Entry Tally Kit Components**
Fields: `cono` (inte) [i], `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `bundleid` (char) [i], `compseqno` (inte) [i], `shipprod` (char) [im], `unit` (char), `qtyord` (deci-2), `pomixpct` (inte), `oemixpct` (inte), `qtyship` (deci-2), `stkqtyord` (deci-2), `stkqtyship` (deci-2), `netord` (deci-2), `netamt` (deci-2), `netcostord` (deci-2), `netcostamt` (deci-2), `length` (inte), `custno` (deci-0) [m], `shipto` (char) [m], `transtype` (char) [i], `whse` (char) [i], `invcost` (deci-5), `price` (deci-5), `prodcost` (deci-5), `statustype` (char) [i], `commcost` (deci-5), `pricefl` (logi) [m], `glcost` (deci-5), `reqprod` (char), `conv` (deci-5), `pdrecno` (inte), `icspecrecno` (inte), `prevprod` (char), `prevqtyship` (deci-2), `prevqtyshp` (deci-2), `prevqtyord` (deci-2), `prevunit` (char), `prevconv` (deci-5), `shpqtyoverfl` (logi) [m], `qtycosted` (deci-2), `stkqtycosted` (deci-2), `netcostedamt` (deci-5), `compaddonamt` (deci-2), `compdiscount` (deci-2), `adjfactor` (deci-5), `adjcost` (deci-5), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `delayresrvfl` (logi) [m], `qtybundle` (deci-2), `qtyprevbundle` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `glcostrcv` (deci-2), `addonamt` (deci-2[4]), `dlength` (deci-2), `countryoforigin` (char), `tariffcd` (char), `rowpointer` (char) [i]

### `oeelo`
**Order Entry Line Order Fulfillment**
Fields: `cono` (inte) [im], `mstordrowpointer` (char) [im], `lineno` (inte) [im], `seqno` (inte) [im], `selectedfl` (logi) [m], `icsdrowpointer` (char) [im], `tiedordrowpointer` (char) [im], `tiedlineno` (inte) [im], `sourcedqty` (deci-2), `origsurplus` (deci-2), `icsprowpointer` (char) [im], `nonstockfl` (logi) [m], `reqshipdt` (date), `tiedlinetype` (char), `tiedlinevendno` (deci-0), `tiedlinewhse` (char), `origruleused` (char), `overruleused` (char), `orignetavail` (deci-2), `whsegroup` (char), `region` (char), `arpvendno` (deci-0), `arpwhse` (char), `transdttmz` (datetm-tz), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `reqshipdttz` (datetm-tz)

### `oefill`
**OEEPB Work File**
Fields: `cono` (inte) [i], `oper2` (char) [im], `reportnm` (char) [i], `processty` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `prod` (char) [i], `specnstype` (char), `pickprno` (inte) [i], `notesfl` (char), `transtype` (char), `orderdisp` (char), `reqshipdt` (date) [i], `qtyord` (deci-2), `unit` (char), `price` (deci-5), `lookupnm` (char), `seqno` (inte), `qtyship` (deci-2), `qtyalloc` (deci-2), `adddesc` (char), `filltype` (char), `descrip` (char), `subty` (char), `dolinefl` (logi) [m], `ordertype` (char) [i], `compseqno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oeinvp`
**OE Invoice Processing - Exception Report**
Fields: `cono` (inte) [i], `oper2` (char) [im], `reportnm` (char) [i], `etype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `notesfl` (char), `custno` (deci-0) [m], `transtype` (char), `stagecd` (inte), `lineno` (inte) [i], `prod` (char) [m], `descrip` (char), `ordertype` (char), `orderaltno` (inte), `wtcono` (inte), `bofl` (logi) [m], `specnstype` (char), `promisedt` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oeix`
**Invoicing Exception Errors**
Fields: `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `whse` (char) [i], `errcd` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `errmsg` (char), `invdt` (date) [i], `errseqno` (inte) [i]

### `oemem`
**OE Memory**
Fields: `postdt` (date) [i], `custno` (deci-0) [im], `cono` (inte) [i], `prod` (char), `unit` (char), `qtyord` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oepick`
**Pick Ticket Bulk Work File**
Fields: `cono` (inte) [i], `reportnm` (char) [i], `oper2` (char) [im], `prod` (char) [im], `qtyship` (deci-2), `binloc` (char), `serlotno` (char) [i], `serlottype` (char) [i], `whse` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `qtyfmrcvs` (deci-2)

### `oerbt`
**Bill Trust Log**
Fields: `cono` (inte) [im], `type` (char) [im], `filedt` (char) [im], `filetm` (char) [im], `custno` (deci-0) [im], `orderno` (inte) [im], `ordersuf` (inte) [im], `docdt` (date), `totamt` (deci-2), `method` (char), `match` (char), `copies` (inte), `invcnt` (inte), `optioncnt` (inte[20]), `optvalue` (char[20]), `openinit` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci), `user7` (deci), `user8` (date), `user9` (date)

### `oerc`
**Consolidated Invoice**
Fields: `cono` (inte) [im], `invno` (inte) [i], `invsuf` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `termstype` (char) [m], `orderno` (inte) [i], `operinit` (char), `ordersuf` (inte) [i], `printcnt` (inte), `custpo` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oesfc`
**Order Entry Fulfillment Customer List**
Fields: `cono` (inte) [im], `recordtype` (char) [im], `srcrowpointer` (char) [im], `transdttmz` (datetm-tz), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oesfr`
**Order Entry Fulfillment Rules List**
Fields: `cono` (inte) [im], `recordtype` (char) [im], `srcrowpointer` (char) [im], `seqno` (inte) [im], `rulename` (char) [im], `rulevalue` (char), `transdttmz` (datetm-tz), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oesfw`
**Order Entry Fulfillment Warehouse List**
Fields: `cono` (inte) [im], `recordtype` (char) [im], `icsdrowpointer` (char) [im], `seqno` (inte), `srcrowpointer` (char) [im], `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oessd`
**Sales Rep by Product Category**
Fields: `cono` (inte) [im], `arrowpointer` (char) [im], `srcrowpointer` (char) [im], `rectype` (char) [im], `slsrepin` (char) [i], `slsrepout` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oessre`
**Order Entry Setup Sales Rep Exceptions**
Fields: `cono` (inte) [im], `recordtype` (char) [im], `custrowpointer` (char) [im], `srcrowpointer` (char) [im], `slsrepin` (char) [i], `slsrepout` (char) [i], `operinit` (char), `transdttmz` (datetm-tz), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci), `user7` (deci), `user8` (date), `user9` (date), `srcrowpointerend` (char)

### `oimea`
**R&D Office Interface Manager - Appointments**
Fields: `person` (char) [i], `person2` (char[10]), `apptdt` (date) [i], `appttm` (inte) [i], `apptlength` (inte), `name` (char) [m], `descrip` (char), `phoneno` (char), `outfl` (logi) [im], `outmsg` (char), `descripx` (char[10]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oimem`
**R&D Message Transactions**
Fields: `seqno` (inte) [i], `person` (char) [i], `fromcono` (inte), `prosno` (deci-0) [im], `phoneno` (char), `msg` (char), `priority` (inte), `returnfl` (logi) [m], `calldt` (date) [i], `operinit` (char), `transdt` (date), `transtm` (char), `name` (char) [m], `perdept` (char) [i], `statustype` (logi) [im], `calltm` (inte) [i], `company` (char), `pickupfl` (logi) [im], `oper2` (char) [im], `prosactcd` (char), `pickupby` (char), `pickupdt` (date), `pickuptm` (inte), `sequenceno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `oimes`
**Sign In/Out Audit Fiel**
Fields: `person` (char) [i], `perdept` (char) [i], `statusfl` (logi) [m], `backdt` (date), `outcomment` (char), `operinit` (char), `transdt` (date) [i], `transtm` (char) [i], `backtm` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `oimet`
**R&D Time Transactions (Check In & Out)**
Fields: `person` (char) [i], `inactdt` (date), `inentdt` (date) [i], `outactdt` (date), `outentdt` (date), `inacttm` (inte), `inenttm` (inte) [i], `outacttm` (inte), `oimpaycd` (char), `outenttm` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `oimsf`
**R&D Office Interface - Manager, Setup Future Plans**
Fields: `person` (char) [i], `itinerary` (char[10]), `itbegdt` (date) [i], `itenddt` (date), `outcomment` (char), `backdt` (date), `backtm` (inte), `rephoneno` (char), `itbegtm` (inte) [i], `itendtm` (inte), `itname` (char) [i], `payfl` (logi) [m], `oimpaycd` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `oimsg`
**R&D Message Group**
Fields: `pergroup` (char) [i], `person` (char[70]), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `oimsp`
**R&D Personnel**
Fields: `person` (char) [i], `name` (char) [m], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `slstitle` (char), `perdept` (char) [i], `responsible` (char), `comment` (char), `boardfl` (logi) [im], `proscono` (inte), `prosno` (deci-0) [m], `phoneno` (char), `faxphoneno` (char), `carphoneno` (char), `modphoneno` (char), `statusfl` (logi) [m], `backdt` (date), `outcomment` (char), `rephoneno` (char), `operinit` (char), `transdt` (date), `transtm` (char), `homphoneno` (char), `backtm` (inte), `prosactcd` (char), `slsrep` (char), `itinerary` (char[10]), `itbegdt` (date), `itenddt` (date), `itbegtm` (inte), `itendtm` (inte), `itname` (char), `miscdata` (char[6]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `addr3` (char)

### `oimst`
**R&D Tables for Message System**
Fields: `codeiden` (char) [im], `codeval` (char) [im], `descrip` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `orddtl`
**Order Detail (Line) Table**
Fields: `id` (inte) [im], `co_num` (char) [im], `wh_num` (char) [im], `work_center` (char), `line` (inte) [im], `line_sequence` (inte) [i], `pick_line` (logi), `abs_num` (char) [i], `stock_stat` (char) [m], `lot` (char), `same_lot` (logi), `serial_num` (char), `bin_num` (char) [m], `fl_zone` (char), `ordered_qty` (deci-2), `orig_req_qty` (deci-2), `req_qty` (deci-2), `act_qty` (deci-2), `ret_qty` (deci-2), `discount` (deci-2), `tax` (deci-2), `charges` (deci-2), `comment` (char), `assigned` (logi) [i], `msds_required` (logi), `msds_packed` (logi), `msds_employee` (char), `msds_sheet` (char), `order_alt_num` (inte), `order_alt_suf` (inte), `line_alt_number` (inte), `orig_weight` (deci-2), `drop_weight` (deci-2), `ship_weight` (deci-2), `orig_cube` (deci-2), `drop_cube` (deci-2), `ship_cube` (deci-2), `rt_num` (char), `vendor_id` (char), `po_number` (char), `po_suffix` (char), `po_line` (inte), `po_line_sequence` (inte), `package_code` (char), `custom_data` (char[5]), `line_status` (char) [im], `sale_uom` (char), `sale_uom_conv` (deci-5), `kit_required` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `wlpicktype` (char), `origvaseqno` (inte), `origvalineno` (inte), `lostbusty` (char), `altwhse` (char), `trans_datetz` (datetm-tz), `shipcompfl` (logi) [m], `name` (char) [im], `code` (char) [im], `sequence` (inte) [im], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `code` (char) [im], `name` (char) [im], `priority` (inte), `custom_data` (char[5]), `row_status` (logi), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `code` (char) [im], `name` (char) [im], `priority` (inte), `custom_data` (char[5]), `row_status` (logi), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `orddtl_status`
**A double lookup table with all the legal status values for order lines**

### `order_class`
**Order classes**

### `order_type`
**Order types**

### `ordhdr`
**Has header information for all orders known to the system**
Fields: `id` (inte) [im], `co_num` (char) [im], `wh_num` (char) [im], `order` (char) [im], `order_suffix` (char) [i], `order_date` (date) [i], `ship_date` (date) [i], `orig_order_date` (date), `exp_ship_date` (date) [i], `cust_code` (char) [m], `bill_name` (char), `bill_addr` (char[2]), `bill_addr_ext` (char[3]), `bill_city` (char), `bill_state` (char), `bill_zip` (char), `bill_country` (char), `ship_cust_code` (char) [im], `ship_name` (char) [i], `ship_addr` (char[2]), `ship_addr_ext` (char[3]), `ship_city` (char), `ship_state` (char), `ship_zip` (char) [i], `ship_country` (char), `cod_flag` (logi), `cod_amount` (deci-2), `cod_charge` (char), `cod_name` (char), `cod_addr` (char[5]), `cod_city` (char), `cod_state` (char), `cod_zip` (char), `cod_country` (char), `customer_po` (char), `branch_id` (char) [i], `carrier` (char) [i], `service` (char) [i], `pro_number` (char), `customer_freight` (deci-2), `actual_freight` (deci-2), `discount` (deci-2), `tax` (deci-2), `charges` (deci-2), `line_count` (inte) [i], `partial` (logi), `type` (char) [im], `class` (char) [im], `drop_type` (char), `kit_build_type` (char), `international` (logi), `priority` (inte) [i], `assigned` (logi) [i], `printed` (logi) [i], `batch` (inte) [i], `host_batch` (char) [i], `host_sequence` (inte) [i], `comment` (char), `del_route` (char), `rate_type` (char), `freight_terms` (char), `hold_reason` (char), `product` (char) [i], `lot` (char), `product_qty` (deci-2), `orig_weight` (deci-2), `drop_weight` (deci-2), `ship_weight` (deci-2), `orig_cube` (deci-2), `drop_cube` (deci-2), `ship_cube` (deci-2), `shp_by_irms` (logi), `host_selector` (char) [i], `custom_selector` (char) [i], `pay_method` (char), `max_days` (inte), `guaranteed_del_time` (char), `custom_data` (char[5]), `cancel_flag` (logi), `clearance_required` (logi) [i], `clearance_code` (char) [i], `order_status` (char) [im], `row_status` (logi) [m], `ship_to_code` (char) [im], `pallet_drop_fl` (logi) [m], `route` (char) [i], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `takenby` (char), `slsrepin` (char), `slsrepout` (char), `memo` (char), `total_line_cnt` (inte), `total_line_qty` (deci-2), `exp_ship_datetz` (datetm-tz), `order_datetz` (datetm-tz), `orig_order_datetz` (datetm-tz), `ship_datetz` (datetm-tz), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `name` (char) [im], `code` (char) [im], `sequence` (inte) [im], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `ordhdr_status`
**Order Header Status Table**

### `oteh`
**Tracking Document Header Table**
Fields: `cono` (inte) [im], `trackno` (inte) [im], `contno` (char), `bolno` (char), `shipid` (char), `shipco` (char), `vesselnm` (char), `voyageno` (char), `countryorgcd` (char), `countrydestcd` (char), `portno` (inte), `portnm` (char), `ltofcreditno` (char), `contsize` (inte), `estdeptdt` (date), `revdeptdt` (date), `actdeptdt` (date), `estdockarrdt` (date), `actdockarrdt` (date), `estdockreddt` (date), `actdockreddt` (date), `estdockdemurdt` (date), `actdockdemurdt` (date), `estlastfreedt` (date), `actlastfreedt` (date), `estwhseunldt` (date), `actwhseunldt` (date), `estempdt` (date), `actempdt` (date), `estretdt` (date), `actretdt` (date), `trackbusyfl` (logi) [m], `stagecd` (inte) [i], `vendno` (deci-0) [i], `contactnm` (char), `addonno` (inte[4]), `addonamt` (deci-2[4]), `addonnet` (deci-2[4]), `addontype` (logi[4]) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `openinit` (char), `whse` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `estatwhsedt` (date), `actatwhsedt` (date), `shipfmno` (inte), `manname` (char), `manaddr` (char[2]), `mancity` (char), `manstate` (char), `manzipcd` (char), `mancountrycd` (char), `manphoneno` (char), `totamt` (deci-2), `estprodstdt` (date), `revprodstdt` (date), `actprodstdt` (date), `estprodcompdt` (date), `revprodcompdt` (date), `actprodcompdt` (date), `revdockdemurdt` (date), `revlastfreedt` (date), `revatwhsedt` (date), `revempdt` (date), `revdockarrdt` (date), `revdockreddt` (date), `revretdt` (date), `revwhseunldt` (date), `notesfl` (char), `manaddr3` (char), `jrnlnoin` (inte), `jrnlnoout` (inte), `actatwhsedttz` (datetm-tz), `actdeptdttz` (datetm-tz), `actdockarrdttz` (datetm-tz), `actdockdemurdttz` (datetm-tz), `actdockreddttz` (datetm-tz), `actempdttz` (datetm-tz), `actlastfreedttz` (datetm-tz), `actprodcompdttz` (datetm-tz), `actprodstdttz` (datetm-tz), `actretdttz` (datetm-tz), `actwhseunldttz` (datetm-tz)

### `oteph`
**PO header data for each PO in Tracking Doc**
Fields: `cono` (inte) [i], `trackno` (inte) [im], `pono` (inte) [i], `posuf` (inte) [i], `totlineamt` (deci-2), `totcubes` (deci-5), `totweight` (deci-5), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `totqtyord` (deci-2), `vendno` (deci-0), `statustype` (char) [i]

### `otepl`
**PO lines in the Tracking Document**
Fields: `cono` (inte) [i], `trackno` (inte) [im], `pono` (inte) [i], `posuf` (inte) [i], `lineno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `polineno` (inte) [i], `transproc` (char), `statustype` (logi) [im], `lineamt` (deci-2), `commentfl` (logi) [m], `qtyord` (deci-2)

### `otevh`
**Overseas Trade Entry Vessel Header**
Fields: `cono` (inte) [i], `vesselno` (inte) [im], `shipid` (char), `shipco` (char), `vessnm` (char), `voyageno` (char), `countryorgcd` (char), `countrydestcd` (char), `estdeptdt` (date), `revdeptdt` (date), `actdeptdt` (date), `estarrdt` (date), `actarrdt` (date), `stagecd` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `estunldt` (date), `actunldt` (date), `revarrdt` (date), `revunldt` (date), `actarrdttz` (datetm-tz), `actdeptdttz` (datetm-tz), `actunldttz` (datetm-tz)

### `otevl`
**Overseas Trade Entry Vessel Lines**
Fields: `cono` (inte) [i], `vesselno` (inte) [i], `lineno` (inte) [i], `trackno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `statustype` (logi) [im], `pallet_num` (inte) [im], `pick_id` (char) [i], `abs_num` (char) [im], `lot` (char), `ns_comment` (char), `quantity` (deci-4), `date_time` (char), `emp_num` (char) [m], `bin_num` (char), `stock_stat` (char), `uom` (char), `custom_data` (char[5]), `truck_id` (char), `row_status` (char) [m], `case_quantity` (deci-4), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `pallet_num` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `pallet_id` (char) [i], `tracking_id` (char) [i], `wh_zone` (char), `full` (logi) [m], `pallet_type` (char) [im], `cart_id` (char) [i], `cart_bin` (char) [i], `custom_data` (char[5]), `row_status` (char) [im], `carrier_id` (char) [i], `cust_code` (char) [i], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `co_num` (char) [im], `wh_num` (char) [im], `wh_type` (char) [m], `rcv_pallet_id_flag` (char) [m], `rcv_qty_check` (char) [m], `rcv_back_orders` (char) [m], `rcv_rma_prefix` (char), `mat_put_away` (char) [m], `mat_repl_flag` (char) [m], `pic_release_flag` (char), `pic_release_time` (char), `pic_hold_lines` (inte), `pic_hold_types` (char), `pic_label_flag` (char) [m], `pic_from_dock` (char) [m], `pac_type` (char) [m], `pac_list_flag` (char) [m], `shp_hold_flag` (char) [m], `shp_force_flag` (char) [m], `physical_flag` (logi), `comments` (char), `row_status` (logi) [m], `emp_num` (char), `display_cycle_qty` (logi), `display_phys_qty` (logi), `cycle_adj` (logi), `phys_adj` (logi), `cycle_adj_code_in` (char), `cycle_adj_code_out` (char), `phys_adj_code_in` (char), `phys_adj_code_out` (char), `date_time` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `label_print_type` (char), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz)

### `palletdet`
**Pallet Detail**

### `palletmst`
**Pallets**

### `parameters`
**This table has parameters for system level (co_num eq 0, wh_num eq 0) and warehouse level (co_num ne 0, wh_num ne 0) TWL will be installed with only the system level defaults set**

### `pdar`
**Price Discounting Administrator Rebate Settings**
Fields: `cono` (inte) [im], `methodno` (inte) [im], `descrip` (char), `contractno` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `pdenh`
**National Program Transaction Header**
Fields: `cono` (inte) [im], `orderno` (inte) [im], `ordersuf` (inte) [im], `seqno` (inte) [im], `origorderno` (inte) [i], `origordersuf` (inte) [i], `apinvno` (char) [i], `archeckno` (inte), `paidjrnlno` (inte), `apsvrowpointer` (char) [i], `npclaimno` (char) [i], `totalpaidamt` (deci-2), `paidgstamt` (deci-2), `paidpstamt` (deci-2), `paidaddonamt` (deci-2), `statustype` (char) [i], `invoicedt` (date) [i], `paiddt` (date), `tolexceptionfl` (logi) [m], `rowpointer` (char) [i], `operinit` (char), `transdttmz` (datetm-tz), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `invoicedttz` (datetm-tz), `paiddttz` (datetm-tz)

### `pdenl`
**National Program Transaction Line**
Fields: `cono` (inte) [i], `srcrowpointer` (char) [im], `lineno` (inte) [im], `origlineno` (inte) [i], `oeelrowpointer` (char) [i], `origoeelrowpointer` (char) [i], `pdsnrecno` (inte) [i], `returnfl` (logi) [m], `paidstkqty` (deci-2), `paidqty` (deci-2), `paidunit` (char), `paidprice` (deci-5), `paidextamt` (deci-2), `paidpstamt` (deci-2), `paidgstamt` (deci-2), `paidehfamt` (deci-2), `unitconv` (deci-5), `icspecrecno` (inte), `tolexceptionfl` (logi) [m], `rowpointer` (char), `operinit` (char), `transdttmz` (datetm-tz), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `pder`
**Transaction File for Rebates**
Fields: `cono` (inte) [i], `statustype` (char) [i], `rebatecd` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `icspecrecno` (inte), `rebrecno` (deci-0) [i], `rebcost` (deci-5), `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `stkqtyship` (deci-2), `actcost` (deci-5), `actstkqty` (deci-2), `whse` (char), `vendno` (deci-0) [im], `contractno` (char) [i], `custno` (deci-0) [i], `shipto` (char) [im], `dropshipty` (char), `seqno` (inte) [i], `frzrebty` (char), `rptexrate` (deci-7), `reconexrate` (deci-7), `shipprod` (char) [m], `unitconv` (deci-5), `qtyship` (deci-2), `invpodt` (date), `speccostty` (char), `csunperstk` (deci-8), `specconv` (inte), `prccostper` (char), `rebateamt` (deci-5), `rptrebamt` (deci-5), `postdt` (date), `refer` (char), `slsrepin` (char), `slsrepout` (char), `actcostto` (deci-5), `rebcostto` (deci-5), `rebcalcty` (char), `rebatepct` (deci-2), `returnfl` (logi) [m], `commexcpty` (char) [i], `intclaimno` (inte) [i], `srcupdtty` (char), `unit` (char), `netamt` (deci-2), `jrnlno` (inte) [i], `setno` (inte) [i], `pdersuf` (inte) [i], `divno` (inte), `prodcat` (char), `transproc` (char), `altrebrecno` (inte), `currencyty` (char), `revalno` (inte), `rebamtfor` (deci-5), `rptrebfor` (deci-5), `netbillfl` (logi) [m], `netbillamt` (deci-5), `netbillfor` (deci-5), `origrebamt` (deci-5), `origrebfor` (deci-5), `transdttmz` (datetm-tz) [i], `invpodttz` (datetm-tz), `postdttz` (datetm-tz), `rowpointer` (char) [i]

### `pderc`
**Rebate Header Claim File**
Fields: `cono` (inte) [i], `intclaimno` (inte) [i], `claimdt` (date), `vendno` (deci-0) [im], `custno` (deci-0), `claimamt` (deci-2), `reconamt` (deci-2), `statusfl` (logi) [im], `rebatecd` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `openinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `currencyty` (char), `claimdttz` (datetm-tz)

### `pderv`
**Rebate Header Claim Sequence Receipt File**
Fields: `cono` (inte) [i], `apinvno` (char), `jrnlno` (inte) [i], `setno` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `divno` (inte), `receiptdt` (date), `postdt` (date), `claimseqno` (inte) [i], `receiptamt` (deci-2), `intclaimno` (inte) [i], `sourcepros` (char), `srcupdtty` (char), `refer` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `statustype` (char) [i], `vendno` (deci-0) [m], `transproc` (char), `rowpointer` (char) [i], `currencyty` (char), `reconexrate` (deci-7), `vatamt` (deci-2), `postdttz` (datetm-tz), `receiptdttz` (datetm-tz)

### `pdsa`
**Automatic Pricing**
Fields: `autotype` (char) [i], `databegin` (inte[30]), `datalength` (inte[30]), `xrefprodfl` (logi) [m], `pricety` (char), `pdcreatefl` (logi) [m], `operinit` (char), `transdt` (date), `transtm` (char), `costty` (char), `decimalfl` (logi) [m], `listty` (char), `stndty` (char), `vendno` (deci-0) [m], `prodline` (char) [m], `prodcat` (char), `addtype` (char), `pricetype` (char), `user1` (char), `priceonty` (char), `user2` (char), `basefactor` (deci-2), `user3` (char), `listfactor` (deci-2), `user4` (char), `prodprefix` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `pdsc`
**PD Customer Pricing**
*PRIMARY price/cost record table. Holds list prices, cost overrides, and pricing rules by product and price type. Key table for any pricing query.*
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `custtype` (char) [i], `whse` (char) [i], `units` (char) [i], `startdt` (date) [i], `enddt` (date) [i], `statustype` (logi) [im], `refer` (char), `commtype` (char), `minqty` (deci-2), `maxqty` (deci-2), `actqty` (deci-2), `pround` (char), `qtytype` (char), `ptarget` (inte), `pexactrnd` (deci-2), `prctype` (logi) [m], `operinit` (char), `transdt` (date), `transtm` (char), `qtyyymm` (char), `prod` (char) [im], `pdrecno` (inte) [i], `disctype` (char), `levelcd` (inte) [i], `prcdisc` (deci-3[9]), `prcmult` (deci-5[9]), `quotefl` (logi) [m], `pricecostty` (char), `qtybrk` (inte[8]), `ContractNo` (char), `promofl` (logi) [im], `PriceSheet` (char), `qtybreakty` (char), `quoteno` (char), `jobno` (char), `prodcost` (deci-5), `PriceEffectiveDate` (date), `termsdiscfl` (logi) [m], `termspct` (deci-2), `user1` (char), `user2` (char), `pricety` (char), `user3` (char), `priceonty` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `slchgdt` (date), `keyindex` (char), `modifiernm` (char), `modifierrebfl` (logi) [m], `hardmaxqtyfl` (logi) [m], `maxqtytype` (char), `hardpricefl` (logi) [m], `rowpointer` (char) [i], `wordindexfl` (logi) [m], `lastuseddt` (date), `ovrridepctup` (deci-2), `ovrridepctdown` (deci-2), `costmult` (deci-5), `costtype` (logi) [m], `costbasedon` (char), `transdttmz` (datetm-tz) [i], `lastuseddttz` (datetm-tz), `slchgdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `levelcd` (Record Type) — See Chart Below; Valid values/xref: 1 - 8; Required
- `pdlevelty` (Level Type) — See Chart Below; Valid values/xref: <Blank>, P, R, L, or C
- `custno` (Customer #) — Can be CHAR(24) if Customer Cross Reference used.; Valid values/xref: ARSC
- `custtype` (Ship-to/Job or Cust Price Type) — See Chart Below
- `jobno` (Line Reference) — Comment for PD Record
- `prod` (Product or Pricetype) — See Chart Below Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1
- `vendno` (Vendor #) — Required if Type 2 and PDLevelty is L for Product Line, otherwise <Blank>. Can be CHAR(24) if Vendor Cross Reference used.; Valid values/xref: APSV
- `units` (Unit) — Only used for special pricing tied to a certain unit used in OE.; Valid values/xref: ICSEU or SASTT U, Used on Types 1, 3 and 7 Only
- `whse` (Whse or Region) — Region Available starting 10.1.1.0. Region must begin with "RGN-". Division Group available starting 11.19.9. Division Group must begin with "DVG-". Leave Blank for Use in all Warehouses. Can be CHAR(24) if using Whse Xref.; Valid values/xref: Whse - ICSD or Region SASTT-RG or Division Group SASTT-DG
- `startdt` (Start Date) — Most Recent Start Date used for Pricing; Required
- `enddt` (End Date) — Suggested for later purging of records
- `statustype` (Active/Inactive) — Valid values/xref: A or I; Default: A
- `refer` (Reference) — Comment for PD Record
- `promofl` (Promotional) — Only Allowed on Type 7 or 8; Valid values/xref: Y or N; Default: N
- `termsdiscfl` (Terms Discount Flag) — (Y)es for Default Cash Terms or (N)o for Product Specific Cash Terms; Valid values/xref: Y or N; Default: Y
- `termspct` (Terms Discount Percent) — Required if Terms Discount Flag is NO
- `commtype` (Commission Type) — Commission Plan tied to Pricing record; Valid values/xref: SMSM
- `prctype` (Price Level) — $ for Fixed Price or % for Percent Multiplier; Valid values/xref: $ or %; Default: %
- `pricesheet` (Price Sheet) — Price Sheet to use for Price/Cost instead of ICSW; Valid values/xref: PDSPS
- `price effectivedate` (Date of Price Sheet) — Effective date on Price Sheet in PDSPS; Valid values/xref: PDSPS
- `priceonty` (Price Based On) — See Chart Below; Default: B
- `qtytype` (Qty Break Per) — <Blank> for Per Order, (M)onth or (Y)ear. Used with Max Qty only.; Valid values/xref: <Blank>, M or Y
- `qtybreakty` (Qty Break On) — <Blank> if no Qty Break (P)rice Multiplier or Line (D)iscount; Valid values/xref: <Blank>, (D)iscount or (P)rice
- `modifiernm` (Modifier Name) — Used with Modifiers setup in PDSPM Available starting 6.0; Valid values/xref: PDSCM
- `modifierrebfl` (Allow with Vendor on Sale Rebates) — Only applies to pricing records with modifier attached Available starting 6.0; Valid values/xref: Y or N; Default: N
- `prcmult1` (Price Multiplier 1) — Multiplier for all PriceOnTy Types
- `prcdisc1` (Discount % 1) — Line Discount % off Base or List Price
- `qtybrk1` (Qty Break 1) — Qty Break On Must be P or D
- `minqty` (Mininum Qty) — Min Qty to get this price based on Qty Break Per Order, Month, or Year
- `maxqty` (Maxinum Qty) — Only Allowed on Type 1. Max Qty gets this price based on Qty Break Per Order, Month or Year
- `actqty` (Actual Qty) — Actual Quantity shipped to date for Min or Max Qty
- `qtyyymm` (Last CCYYMM for Qty) — Date of Last Actual Qty Sold. Example format 200601 for Jan-2006
- `maxqtytype` (Max Based On) — Quantities are (C)ube, S(p)ecial Prc Cost, (S)tocking Quantity, or (W)eight Available starting 6.1.040; Valid values/xref: C, P, S, W or <blank>; Default: S
- `hardmaxqtyfl` (Hard Max Qty Flag) — Available starting 6.1.040; Valid values/xref: Y or N; Default: N
- `pround` (Pricing Round) — (U)p, (D)own or (N)earest; Valid values/xref: U, D or N; Default: N
- `ptarget` (Target) — See Chart Below; Valid values/xref: 1 - 9; Default: 5
- `pexactrnd` (User Tgt.) — Only used with Target 9 User Defined
- `hardpricefl` (Hard Price flag) — PDSP System Price Record is a Hard Set Price Available starting 6.1.040; Valid values/xref: Y or N Cannot be Y with Override Tol up and down; Default: N
- `lastuseddt` (Last Used Date) — Available starting 10.2.1 Last date when PD record was used to price an order
- `ovrridepctup` (Override Percent Up) — Available starting 10.2.1; Valid values/xref: Must be zero if Hard Price Flag is yes
- `ovrridepctdown` (Override Percent Down) — Available starting 10.2.1; Valid values/xref: Must be zero if Hard Price Flag is yes
- `quotefl` (Quote Flag) — (Y)es price generated from a Quote - only used on Type 1 and 2; Valid values/xref: Y or N; Default: N
- `quoteno` (Quote Number) — Reference to Original Quote that generated Price Record
- `slchgdt` (Supplier Link Update Date) — Last Date Supplier Link Updated Record. Available Starting 4.1
- `user5` (user5) — Used for Conversion Import ID
- `costbasedon` (Sales Cost Based On) — Select base to be used to caculate the OE cost. This is only needed if using a % in the calculation.; Valid values/xref: Blank, (B)ase, (L)ist, (R)eplacement or (S)tandard; Default: Blank
- `costmult` (Sales Cost Amount) — Amount to be used to calculate the sales amount (if %) or actual amount; Valid values/xref: "; Default: 0
- `costtype` (Sales Cost Type (Actual or % - logical field)) — % (No) or Actual Amount (Yes); Valid values/xref: Y or N; Default: No or false
- `Type` (Description) — CustType Field; Valid values/xref: Prod Field
- `1` (Customer / Product) — Shipto - ARSS, Optional; Valid values/xref: Product - ICSP/ICSC; Required
- `2` (Customer / Product Price Type) — Shipto - ARSS, Optional; Valid values/xref: Product Price Type - SASTT K; Required
- `3` (Customer Price Type / Product) — Customer Price Type - SASTT J, Required; Valid values/xref: Product - ICSP/ICSC; Required
- `4` (Customer Price Type / Product Price Type) — Customer Price Type - SASTT J, Required; Valid values/xref: Product Price Type - SASTT K; Required
- `5` (Customer) — Shipto - ARSS, Optional; Valid values/xref: <Blank>
- `6` (Customer Price Type) — Customer Price Type - SASTT J, Required; Valid values/xref: <Blank>
- `7` (Product) — <Blank>; Valid values/xref: Product - ICSP/ICSC; Required
- `8` (Product Price Type) — <Blank>; Valid values/xref: Product Price Type - SASTT K; Required

### `pdscc`
**Price Discounting Customer Channel Setup**
Fields: `cono` (inte) [i], `pdrecno` (inte) [im], `channel` (char) [im], `multiplier` (deci-5), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char)

### `pdscm`
**PD Customer Pricing Modifiers**
Fields: `cono` (inte) [i], `modifiernm` (char) [i], `whse` (char) [i], `rankty` (char), `pct` (deci-2[26]), `nonstockpct` (deci-2), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `pdsf`
**Base Price Update**
Fields: `cono` (inte) [i], `prod` (char) [im], `whse` (char) [i], `baseprice` (deci-5), `pricetype` (char), `effectdt` (date) [i], `operinit` (char), `transdt` (date), `transtm` (char), `pricepct` (deci-5), `pctfl` (logi) [m], `replcost` (deci-5), `stndcost` (deci-5), `basetype` (char), `stndtype` (char), `repltype` (char), `pround` (char), `ptarget` (inte), `pexactrnd` (deci-2), `listprice` (deci-5), `listtype` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `effectdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `whse` (Warehouse) — If Blank, change will be made in all warehouse ICSW records for this product. Can be CHAR(24) if using xref; Valid values/xref: Blank or ICSD
- `basetype` (Base Price Change Type) — See Chart Below; Valid values/xref: Blank, N, D, P, I, S, R or L
- `baseprice` (Base Price Change Amount) — See Chart Below
- `listtype` (List Price Change Type) — See Chart Below; Valid values/xref: Blank, N, D, P, B, S, R or L
- `listprice` (List Price Change Amount) — See Chart Below
- `repltype` (Replacement Cost Change Type) — See Chart Below; Valid values/xref: Blank, N, D, P, I, S, B or L
- `replcost` (Replacement Cost Change Amount) — See Chart Below
- `stndtype` (Standard Cost Change Type) — See Chart Below; Valid values/xref: Blank, N, D, P, I, B, R or L
- `stndcost` (Standard Cost Change Amount) — See Chart Below
- `pround` (Pricing Round Method) — Up, Down or Nearest method of rounding; Valid values/xref: U, D or N; Default: N
- `ptarget` (Pricing Target) — See Chart Below; Valid values/xref: 1 - 9; Default: 5
- `pexactrnd` (User Defined Rounding Target) — Used if ptarget is 9
- `pricetype` (Price Type) — Enter new value if changing ICSW, blank for no change. Can be CHAR(24) if using xref; Valid values/xref: SASTT-K
- `user5` (user5) — Used for Conversion Import ID
- `Change Type Code` (Price/Cost Change Amount) — Price/Cost Change Amount Example
- `Blank` (Leave Blank or Zero) — No change to the current ICSW value
- `N` (Enter actual $ amount) — If new value should be $5.05, enter 5.05
- `D` (Enter +/- amount to change current price/cost.) — If current value is $4.95 and new value should be + $1.05 for new value of $6.00, enter 1.05
- `P` (Enter +/- percentage to change current price/cost) — If new value should be 5% higher then current value, enter 5
- `I` (Enter Percent of List Price based on 100%) — If price/cost should be 10% off of List price, enter 90.
- `S` (Enter Percent of Standard Cost based on 100%) — If price/cost should be 120% of Standard Cost, enter 120.
- `R` (Enter Percent of Replacement Cost based on 100%) — If price/cost should be 100% of Replacement Cost, enter 100.
- `B` (Enter Percent of Base Price based on 100%) — If price/cost should be 90% of Base Price, enter 90
- `L` (Enter Percent of Last Cost based on 100%) — if price/cost should be 85% of Last Cost, enter 85

### `pdsn`
**Price Discount Setup National Program**
Fields: `cono` (inte) [im], `pdsnrecno` (inte) [i], `levelcd` (inte) [im], `statustype` (logi) [m], `apsvrowpointer` (char) [im], `custrowpointer` (char) [im], `prodrowpointer` (char) [im], `whse` (char) [im], `transtype` (char) [im], `startdt` (date) [im], `transdttmz` (datetm-tz), `enddt` (date) [i], `npcd` (char) [i], `descrip` (char), `allowretfl` (logi) [m], `programonlyfl` (logi) [m], `npcomcalctype` (char), `npcombasedon` (char), `npcomamt` (deci-2), `npcomprodrowpointer` (char), `seqno` (inte) [im], `rowpointer` (char) [i], `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `npcommtype` (char), `rebsubty` (char) [im]

### `pdsr`
**PD Rebates**
**Operators call this:** "Rebate Amount" (Sales)
Fields: `cono` (inte) [i], `levelkey` (char) [im], `custno` (deci-0) [i], `rebatecostty` (char), `rebateamt` (deci-5), `sharefl` (logi) [m], `sharepct` (deci-2), `capsellamount` (deci-5), `capselltypefl` (logi) [m], `manualfl` (logi) [m], `contractlineno` (inte), `operinit` (char), `transdt` (date), `transtm` (char), `startdt` (date) [i], `enddt` (date) [i], `rebrecno` (deci-0) [i], `refer` (char), `vendno` (deci-0) [im], `pricesheet` (char), `whse` (char) [i], `codeid` (char) [i], `levelcd` (inte), `priceeffectivedate` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `dropshipty` (char), `rebsubty` (char) [i], `contractno` (char) [i], `shipto` (char) [im], `rebcalcty` (char), `custrebty` (char) [i], `rebatepct` (deci-5), `rebatecd` (char), `rebdowntoty` (char), `caprebfl` (logi) [m], `margincostty` (char), `transproc` (char), `priceeffectivedateto` (date), `pricesheetto` (char), `contractcostfl` (logi) [m], `rowpointer` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `levelcd` (Level) — See Chart Below; Valid values/xref: 1 - 5; Required
- `rebatecd` (Rebate For) — Vendor Based on (P)urchase, Vendor Based on (S)ale or (C)ustomer; Valid values/xref: P, S or C; Required; Default: S
- `levelkey` (Rebate Level Key) — See Chart Below Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: See Chart Below; Required
- `vendno` (Vendor #) — Must match ICSW ARP Vendor to record Rebate. May be CHAR(24) if using Vendor Cross Reference.; Valid values/xref: APSV; Required
- `custno` (Customer #) — If Blank will apply to All Customers or a Customer Rebate Type. May be CHAR(24) if using Customer Cross Reference.; Valid values/xref: ARSC
- `shipto` (Shipto/Job) — Only used if Customer # is used.; Valid values/xref: ARSS
- `custrebty` (Customer Rebate Type) — If Blank will apply to All customers or one Customer if supplied.; Valid values/xref: PDST - CT
- `dropshipty` (Shipment Type) — (D)rop or (W)hse; Valid values/xref: D or W; Default: W
- `whse` (Whse or Region) — Region Available starting 10.1.1.0. Region must begin with "RGN-". Leave Blank for Use in all Warehouses. Can be CHAR(24) if using Whse Xref.; Valid values/xref: Whse - ICSD or Region SASTT-RG
- `contractno` (Contract #) — Included on Vendor Claim report. Required if Contract Cost flag set to yes.
- `contractcostfl` (Contact Cost Flag) — Available Starting 6.1.080 Used for Short Term SPA contracts only, on Vendor Based on Sale records only; Valid values/xref: Y or N; Default: N
- `enddt` (End Date) — If blank records will never expire
- `sharefl` (Share Rebate) — Used for Vendor Based on Sale Rebates to indicate there is a Shared rebate arrangement with the vendor. Not allowed with rebate calc type Margin. Available starting 10.3.1; Valid values/xref: Y or N; Default: N
- `caprebfl` (Cap Rebate) — Used for Vendor Based on Purchase only. Is Rebate Capitalized into value of Inventory on Hand.; Valid values/xref: Y or N; Default: Y
- `rebcalcty` (Rebate Calc Type) — $ - Amount, % - Percent of Rebate From Value, (N)et, (M)argin; Valid values/xref: $, %, N or M; Default: $
- `rebatecostty` (Rebate From/On) — B = Base Price L = List Price P = PDSC Price A = Avg cost T = Last cost R = Replacement cost S = Standard cost E = Rebate cost O = Last Foreign cost C = Actual cost C1 to C9 = Customer Column 1 to 9 on Price Sheet V1 to V9 = Vendor Column 1 to 9 on Price Sheet; Valid values/xref: Required for Type % and N: B, L, P, A, T, R, S, E, O or C Must Enter Price Sheet To if using C1 - C9 or V1 - V9; Default: S
- `rebdowntoty` (Rebate Down To) — F = Flat Amount B = Base Price L = List Price P = PDSC Price A = Avg Cost T = Last Cost R = Replacement Cost S = Standard Cost E = Rebate Cost O = Last Foreign Cost C = Actual Cost C1 to C9 = Customer Column 1 to 9 on Price Sheet V1 to V9 = Vendor Column 1 to 9 on Price Sheet; Valid values/xref: Required for Type N: F, B, L, P, A, T, R, S, E, O or C Must Enter Price Sheet To if using C1 - C9 or V1 - V10; Default: F
- `margincostty` (Margin Cost Type) — A = Avg Cost T = Last Cost R = Replacement Cost S = Standard Cost E = Rebate Cost O = Last Foreign Cost C = Actual Cost; Valid values/xref: Required for Type M: A, T, R, S, E, O or C; Default: A
- `rebateamt` (Rebate Amount) — Dollar Amount for Rebate Calc Type $ and for Rebate Down To Flat Amount; Valid values/xref: Required for Type $ and N with Rebated Down to Flat
- `rebatepct` (Rebate Percent) — Percent Amount for Rebate Calc Type %, N and M; Valid values/xref: Required for Type %, M and N with Rebate Down to anything other than Flat
- `rebsubty` (Rebate Sub Type) — Optional Sub Type for Level 2 records only; Valid values/xref: PDST - ST
- `pricesheet` (Price Sheet) — Price Sheet Value Used for Rebate From/On; Valid values/xref: PDSPS
- `priceeffectivedate` (Price Sheet Effective Date) — Must enter sheet date as found on PDSPS - can be blank if PDSPS date is blank; Valid values/xref: PDSPS
- `pricesheetto` (Price Sheet Down To) — Price Sheet Value Used for Rebate Down To; Valid values/xref: PDSPS
- `priceeffectivedateto` (Price Sheet Down To Effective Date) — Must enter sheet date as found on PDSPS - can be blank if PDSPS date is blank; Valid values/xref: PDSPS
- `sharepct` (Share Percent) — Used with Vendor On Sale Rebates that are Shared Available starting 10.3.1
- `capsellamount` (Cap Sell Amount) — Used with Vendor On Sale Rebates that are Shared Available starting 10.3.1
- `capselltypefl` (Cap Sell Type) — Used with Vendor On Sale Rebates that are Shared Available starting 10.3.1; Valid values/xref: $ or %; Default: %
- `user5` (user5) — Used for Conversion Import ID

### `pdsra`
**Price Discounting Alternate Rebate Calculations Setup**
Fields: `cono` (inte) [im], `methodno` (inte) [im], `vendno` (int6) [im], `altprodgrp` (char) [im], `custrebty` (char) [im], `whse` (char) [im], `startdt` (date) [im], `enddt` (date), `statustype` (logi) [m], `altrebrecno` (inte) [i], `begmultiplier1` (deci-5), `begmultiplier2` (deci-5), `begmultiplier3` (deci-5), `begmultiplier4` (deci-5), `begmultiplier5` (deci-5), `endmultiplier1` (deci-5), `endmultiplier2` (deci-5), `endmultiplier3` (deci-5), `endmultiplier4` (deci-5), `endmultiplier5` (deci-5), `splitratio1` (deci-5), `splitratio2` (deci-5), `splitratio3` (deci-5), `splitratio4` (deci-5), `splitratio5` (deci-5), `percentage1` (deci-5), `percentage2` (deci-5), `percentage3` (deci-5), `percentage4` (deci-5), `percentage5` (deci-5), `multiplier1` (deci-5), `multiplier2` (deci-5), `multiplier3` (deci-5), `multiplier4` (deci-5), `multiplier5` (deci-5), `calculatortype1` (char), `calculatortype2` (char), `calculatortype3` (char), `calculatortype4` (char), `calculatortype5` (char), `sellertype1` (char), `sellertype2` (char), `sellertype3` (char), `sellertype4` (char), `sellertype5` (char), `distrtype1` (char), `distrtype2` (char), `distrtype3` (char), `distrtype4` (char), `distrtype5` (char), `rowpointer` (char) [i], `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `wordindexfl` (logi) [m]

### `pdss`
**PD Special Category Pricing**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `pricetype` (char) [im], `startdt` (date) [i], `enddt` (date), `disctype` (logi) [m], `whse` (char) [i], `statustype` (logi) [im], `refer` (char), `qtybrk` (inte[8]), `prcdisc` (deci-3[9]), `custptype` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `pdst`
**Price Discounting Setup Table Values**
Fields: `codeiden` (char) [im], `codeval` (char) [im], `cono` (inte) [i], `descrip` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `vendno` (deci-0) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `rowpointer` (char) [i]

### `pdsv`
**PD Vendor Product Pricing**
Fields: `cono` (inte) [i], `prod` (char) [im], `startdt` (date) [i], `enddt` (date), `statustype` (logi) [m], `refer` (char), `vendorprice` (deci-2), `buytype` (char), `transdt` (date), `transtm` (char), `operinit` (char), `qtybrk` (inte[8]), `prcmult` (deci-5[9]), `prcdisc` (deci-3[9]), `user1` (char), `vendno` (deci-0) [im], `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `slchgdt` (date), `slchgdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `vendno` (Vendor #) — Can be CHAR(24) if using xref; Valid values/xref: APSV; Required
- `vendorprice` (Vendor Price) — Required if using Discounts 1 - 9
- `buytype` (Qty Brk On) — (Q)uantity, (W)eight, or (C)ubes; Valid values/xref: Q, W or C; Default: Q
- `user5` (user5) — Used for Conversion Import ID

### `pdsvc`
**PD Contract Cost**
Fields: `actqty` (deci-2), `cono` (inte) [i], `contractno` (char) [im], `custno` (deci) [i], `enddt` (date), `hardmaxqtyfl` (logi) [m], `price` (deci-5), `levelcd` (inte) [i], `maxqty` (deci-2), `maxqtytype` (char), `operinit` (char), `prod` (char) [im], `refer` (char), `shipto` (char), `slchgdt` (date), `startdt` (date) [i], `statustype` (logi) [im], `transproc` (char), `transdt` (date), `transtm` (char), `vendno` (deci-0) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `unit` (char) [i], `vendquote` (char), `whse` (char) [i], `pdsvcrecno` (inte) [i], `qtytype` (char), `qtyyymm` (char), `slchgdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `levelcd` (Record Type) — See Chart Below Product Rebate Type available starting 6.1.080; Valid values/xref: 1-5; Required
- `vendno` (Vendor #) — Can be CHAR(24) if Customer Cross Reference used.; Valid values/xref: APSV; Required
- `prod` (Product or Price Type or Rebate type or Product Line) — See Chart Below Old Product Cross Ref length 50 available starting in 6.1.040 Product Rebate Type available starting 6.1.080 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: See chart below; Required
- `unit` (Unit) — Only used for special pricing tied to a certain unit used in PO; Valid values/xref: Only used for level 1 - Product records. ICSEU or SASTT - U
- `whse` (Whse) — Leave Blank for Use in all Warehouses Can be CHAR(24) if Whse Cross Reference used.; Valid values/xref: ICSD
- `startdt` (Start Date) — Most Recent Start Date used for Pricing; Required
- `enddt` (End Date) — Suggested for later purging of records
- `statustype` (Active/Inactive) — Valid values/xref: A or I; Default: A
- `refer` (Reference) — Comment for Record
- `vendquote` (Vendor Quote #) — Prints on purchase order
- `custno` (Customer #) — Can be CHAR(24) if Customer Cross Reference used.; Valid values/xref: ARSC
- `shipto` (Shipto/Job) — Valid values/xref: ARSS
- `maxqty` (Maximum Qty) — Max Qty to get this price based on max qty type
- `actqty` (Actual Qty) — Actual Quantity shipped to date for Max Qty
- `maxqtytype` (Max Qty Type) — (C)ube, S(p)ecial Prc Cost, (S)tocking Quantity, or (W)eight; Valid values/xref: C, P, S or W; Default: S
- `hardmaxqtyfl` (Hard Max Qty Flag) — Prohibt use of this price after max qty is reached; Valid values/xref: Y or N; Default: N
- `qtytype` (Qty Break Per) — Max Qty applied per (C)ontract, (M)onthly, (Y)early or Blank if per Order; Valid values/xref: C, M, Y or Blank
- `qtyyymm` (Last CCYYMM for Qty) — Date of Last Actual Qty Sold. Example format 200601 for Jan-2006; Valid values/xref: Required if Actual Qty provided
- `slchgdt` (Supplier Link Update Date) — Last Date Supplier Link Updated Record
- `user5` (user5) — Used for Conversion Import ID
- `contracttype` (Contract Type) — (P)urchase Order Only, (O)rder Entry Only or (B)oth. Blank defaults to (B)oth.; Valid values/xref: P, O, B or Blank; Default: B
- `custrebatety` (Customer Rebate Type) — Customer Rebate Type from PDST codeiden = 'CT'; Valid values/xref: PDST
- `pricepercentfl` (Is Price a Percent) — Indicates if vendor price is a percentage or amount; Valid values/xref: Y or N; Default: N
- `pricepercenton` (Percent Based On) — (B)ase Price, List (P)rice, (S)tandard Cost, (L)ast Cost or (R)eplacement Cost; Valid values/xref: B, P, S, L or R
- `producttype` (Product Type) — (K)it Product Only, (B)oth Kit and Product or Blank for Product Only (Default); Valid values/xref: K, B or Blank
- `allowrebatety` (Allow Rebates) — Apply (R)ebate, Apply (L)owest or Blank for Contract Only (Default); Valid values/xref: R, L or Blank

### `pdsvcd`
**PD Expanded Vendor Product Pricing**
Fields: `cono` (inte) [i], `whse` (char) [im], `vendpdrecno` (inte) [i], `prod` (char) [im], `prodline` (char) [i], `startdt` (date) [i], `enddt` (date), `statustype` (logi) [m], `refer` (char), `vendorprice` (deci-2), `buytype` (char), `transdt` (date), `transtm` (char), `operinit` (char), `qtybrk` (inte[8]), `prcmult` (deci-5[9]), `prcdisc` (deci-3[9]), `prcdisc2` (deci-3[9]), `prcdisc3` (deci-3[9]), `prcdisc4` (deci-3[9]), `prcdisc5` (deci-3[9]), `prcdisc6` (deci-3[9]), `user1` (char), `vendno` (deci-0) [im], `shipfmno` (inte) [im], `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `chainedfl` (logi) [m]

### `pdsvtr`
**PO Transaction Line Discounts**
Fields: `orderno` (inte) [i], `ordersuf` (inte) [i], `whse` (char) [m], `lineno` (inte) [i], `cono` (inte) [i], `vendpdrecno` (inte), `typecd` (char) [i], `prcmult` (deci-5[9]), `prcdisc` (deci-3[9]), `prcdisc2` (deci-3[9]), `prcdisc3` (deci-3[9]), `prcdisc4` (deci-3[9]), `prcdisc5` (deci-3[9]), `prcdisc6` (deci-3[9]), `chainedfl` (logi) [m], `vendorprice` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `qtybrk` (inte[8]), `buytype` (char), `refer` (char), `prod` (char) [im]

### `pick`
**This is used to generate and maintain pick labels**
Fields: `id` (inte) [i], `co_num` (char) [im], `wh_num` (char) [im], `batch` (inte) [i], `order` (char) [i], `order_suffix` (char) [i], `line` (inte) [im], `line_sequence` (inte) [i], `carton_id` (char) [i], `abs_num` (char) [i], `serial_num` (char), `lot` (char), `pick_sequence` (inte) [i], `wh_zone` (char) [im], `aisle` (inte) [im], `bin_num` (char) [im], `qty` (deci-2), `orig_qty` (deci-2), `date_time` (char), `reserved` (logi) [m], `printed` (logi) [m], `pallet_num` (inte), `pallet_id` (char), `stock_stat` (char) [m], `custom_data` (char[5]), `pick_status` (char) [i], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `pick_seq2` (inte), `pick_seq3` (inte), `weight` (deci-2), `altwhse` (char) [i], `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `extpick` (logi) [m], `extuser` (char), `extshortuser` (char), `extskipusers` (char)

### `pmep`
**Parcel Management Packing Record**
Fields: `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `pkgno` (char), `actweight` (deci-2), `boxtype` (char), `packinit` (char), `noitems` (inte), `pkgvalue` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `custno` (deci-0) [im], `ordertype` (char) [i], `shipdt` (date) [i], `carrierid` (char) [im], `servtype` (char) [i], `whse` (char), `whseto` (char), `shipto` (char) [m], `manifestno` (char) [i], `shippingpt` (char) [im], `charges` (deci-2), `zone` (char), `billamt` (deci-2), `codamt` (deci-2), `shipreqno` (inte), `shpkgno` (inte) [i], `extra` (logi[20]) [m], `freight` (deci-2), `inschg` (deci-2), `user1` (char), `user2` (char), `valunit` (inte), `active` (logi) [m], `manifestype` (char) [i], `flatord` (deci-2), `orgcodamt` (deci-2), `addcod` (deci-2), `orgarsa` (deci-2), `openinit` (char), `ltr` (logi) [m], `cwtfreight` (deci-2), `origweight` (deci-2), `orgaddon2` (deci-2), `dwtype` (char), `shiptoadd1` (char) [i], `shiptoadd2` (char) [i], `pmcashfl` (logi) [m], `zipcd` (char) [i], `ltr2` (logi) [m], `pmcwtfl` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `dwheight` (deci-2), `dwwidth` (deci-2), `dwlength` (deci-2), `trackerno` (char), `transproc` (char)

### `pmes`
**Parcel Management Shipping Request**
Fields: `shipreqno` (inte) [i], `name` (char) [im], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `reqinit` (char) [i], `apprinit` (char), `shipviaty` (char), `descrip` (char[2]), `shipdt` (date) [i], `shipinit` (char), `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `shippedfl` (logi) [m], `notesfl` (char), `nopackages` (inte), `carrierid` (char) [m], `servtype` (char), `zone` (char), `user1` (char), `manzonefl` (logi) [m], `user2` (char), `totweight` (deci-2), `user3` (char), `totfreight` (deci-2), `user4` (char), `shippingpt` (char) [m], `user5` (char), `sendtype` (char) [i], `user6` (deci-5), `sendno` (deci-0) [i], `user7` (deci-5), `openinit` (char), `user8` (date), `user9` (date), `transproc` (char), `addr3` (char), `shipdttz` (datetm-tz)

### `pmsb`
**Parcel Management Billing File**
Fields: `carrierid` (char) [im], `type` (logi) [im], `specific` (char) [i], `chargefrght` (logi) [m], `flatordamt` (deci-2), `flatpkgamt` (deci-2), `freightpct` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `cono` (inte) [i], `chargebofl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `pmsc`
**Parcel Management Carrier**
Fields: `carrierid` (char) [im], `name` (char) [m], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `manifestno` (inte), `roundtype` (char), `extrahdr` (char[20]), `extraamt` (deci-2[20]), `inssource` (char), `inspkgchg` (deci-2), `insminval` (deci-2), `insrate` (deci-2), `insperamt` (deci-2), `endpkgno` (char), `printvalfl` (logi) [m], `begpkgno` (char), `nomaxpkg` (inte), `hundredwtfl` (logi) [m], `specsvcfl` (logi[3]) [m], `codchg` (deci-2), `user1` (char), `pkgcom` (logi) [m], `user2` (char), `transdt` (date), `user3` (char), `transtm` (char), `user4` (char), `operinit` (char), `user5` (char), `maxwght` (inte), `user6` (deci-5), `maxdimen` (inte), `user7` (deci-5), `nextpkgno` (char), `user8` (date), `insroundty` (char), `user9` (date), `standardty` (char), `effdate` (date), `preferred` (char), `transproc` (char), `addr3` (char), `effdatetz` (datetm-tz)

### `pmsd`
**Parcel UPS Destination**
Fields: `dest` (char) [i], `begzipcd` (char) [i], `endzipcd` (char), `loctblno` (inte), `exttblno` (inte), `maxweight` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `standardty` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `intramaxwght` (deci-2), `transproc` (char)

### `pmsdz`
**UPS Rural Zip Codes**
Fields: `dest` (char) [i], `zipcd` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `pmsg`
**PM Ground Saver Discount File**
Fields: `gsind` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `gsindfl` (logi) [m], `standardty` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `pmsr`
**Parcel Management Rate table**
Fields: `ratetblno` (inte) [i], `ratedescr` (char), `rateovr100` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `wtunit` (char), `zone` (char) [i], `ltrrate` (deci-2), `twodayltr` (deci-2), `standardty` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `rate` (deci-2[500]), `transproc` (char)

### `pmss`
**Parcel Management Shipping Point**
Fields: `shippingpt` (char) [i], `name` (char) [m], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `origzipcd` (char) [m], `disppostfl` (logi) [m], `frghtcodfl` (logi) [m], `prpickfl` (logi) [m], `pkprinternm` (char), `prinvfl` (logi) [m], `invprinternm` (char), `prbolfl` (logi) [m], `bolprinternm` (char), `prlabelfl` (logi) [m], `labprinternm` (char), `scaledriver` (char), `labelstyle` (char), `scalecomm` (char), `prcodenfl` (logi) [m], `codprinternm` (char), `codstyle` (char), `autoretfl` (logi) [m], `scaledev` (char), `user1` (char), `user2` (char), `cono` (inte) [i], `user3` (char), `transdt` (date), `user4` (char), `transtm` (char), `user5` (char), `operinit` (char), `user6` (deci-5), `shipperid` (char), `user7` (deci-5), `groundsvfl` (logi) [m], `user8` (date), `shipperid1` (char), `user9` (date), `tier` (char), `intracwtfl` (logi) [m], `intragsfl` (logi) [m], `transproc` (char), `addr3` (char)

### `pmst`
**Parcel Management Setup Tier**
Fields: `tier` (char) [i], `zone` (char) [i], `tierrate` (deci-2), `tiernm` (char), `transdt` (date), `transtm` (char), `operinit` (char), `standardty` (char), `tierrate500` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `minchrg` (deci-2), `avglbspkg` (deci-2), `transproc` (char)

### `pmsub`
**Table setup for box names and dimensions. Length, width, height. Used in PMEP for the dimensional weight calculation for UPS**
Fields: `cono` (inte) [i], `boxname` (char) [i], `descrip` (char), `dwwidth` (deci-2), `dwlength` (deci-2), `dwheight` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char)

### `pmsv`
**Parcel Management Services**
Fields: `servdesc` (char), `zonetblno` (inte), `ratetblno` (inte), `ratefactor` (deci-2), `deliveryty` (char), `shipviaty` (char) [i], `servtype` (char) [i], `carrierid` (char) [im], `transdt` (date), `transtm` (char), `operinit` (char), `standardty` (char), `endpkgno` (char), `nextpkgno` (char), `begpkgno` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `pmsz`
**Parcel Management Setup - Zones**
Fields: `service` (char) [i], `begorgzip` (char) [i], `endorgzip` (char) [i], `begdestzip` (char) [i], `enddestzip` (char) [i], `zone` (char), `carrierid` (char) [im], `transdt` (date), `transtm` (char), `operinit` (char), `standardty` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `poao`
**Contains PO # ranges for entire company.**
Fields: `cono` (inte) [i], `poassgnty` (char), `begpono` (inte), `nextpono` (inte), `endpono` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `pormglcostfl` (logi) [m], `operinit` (char), `transdt` (date), `transtm` (char), `incval` (inte), `transproc` (char), `reqpobatchfl` (logi) [m], `podolholdty` (char), `ponsovrfillty` (char)

### `poeh`
**PO Header**
*Purchase order header.*
**Operators call this:** "Supplier" (Purchasing), "Transaction Type" (Purchasing), "Stage" (Purchasing), "Receipt Date" (Purchasing), "Transaction Type Name" (Purchasing), "Stage Name" (Purchasing)
Fields: `cono` (inte) [i], `pono` (inte) [im], `posuf` (inte) [i], `stagecd` (inte) [i], `shiptonm` (char) [m], `notesfl` (char), `orderaltno` (inte), `orderaltsuf` (inte), `transtype` (char) [im], `shiptost` (char), `shiptozip` (char), `shipinstr` (char), `refer` (char), `shipviaty` (char), `operinit` (char), `transdt` (date), `orderdt` (date), `printeddt` (date), `enterdt` (date), `receiptdt` (date), `transtm` (char), `shiptoaddr` (char[2]), `shiptocity` (char), `nolineitem` (inte), `totlineamt` (deci-2), `totweight` (deci-5), `totcubes` (deci-5), `buyer` (char), `jrnlno` (inte) [i], `nosnlots` (deci-2), `notimeschg` (inte), `nextlineno` (inte), `linefl` (logi) [m], `printfl` (logi) [m], `ignoreltfl` (logi) [m], `totqtyord` (deci-2), `createdby` (char), `totqtyrcv` (deci-2), `addondistr` (char), `whse` (char) [i], `nonotresln` (inte), `totrcvamt` (deci-2), `expshipdt` (date), `vendno` (deci-0) [i], `expoverfl` (logi) [m], `prodline` (char), `reqoverfl` (logi) [m], `billtowhse` (char), `user3` (char), `termstype` (char) [m], `user4` (char), `resalefl` (logi) [m], `user5` (char), `orderdisp` (char), `user6` (deci-5), `resaleno` (char), `user7` (deci-5), `confirmfl` (logi) [m], `user8` (date), `subfl` (logi) [m], `user9` (date), `bofl` (logi) [m], `duedt` (date), `costeddt` (date), `paiddt` (date), `totinvamt` (deci-2), `apinvno` (char), `shipfmno` (inte), `crreasonty` (char), `borelfl` (logi) [m], `brbono` (inte), `actionty` (char), `rcvoperinit` (char), `jrnlno2` (inte), `manname` (char), `manaddr` (char[2]), `mancity` (char), `manstate` (char), `manzipcd` (char), `fobfl` (logi) [m], `setno2` (inte), `cstoperinit` (char), `dueoverfl` (logi) [m], `contactid` (deci-0), `totuinvamt` (deci-2), `wodiscamt` (deci-2), `wodiscdist` (deci-2), `laststagecd` (inte), `openinit` (char), `nocatwght` (inte), `glupdfl` (logi) [m], `currencyty` (char), `rcvexrate` (deci-7), `invexrate` (deci-7), `addonno` (inte[4]), `addonamt` (deci-2[4]), `addonnet` (deci-2[4]), `addontype` (logi[4]) [m], `wodisctype` (logi) [m], `pocnt` (inte), `addondist` (deci-2[4]), `wodiscnet` (deci-2), `totexprcv` (deci-2), `totexpinv` (deci-2), `user1` (char), `user2` (char), `wodiscres` (deci-2), `tottaxamtau` (deci-2), `rcvtaxamtau` (deci-2), `reqshipdt` (date), `totqtycost` (deci-2), `receiverno` (char) [i], `totqtyrcvb` (deci-2), `costaddist` (deci-2), `divno` (inte), `rushfl` (logi) [m], `trhistfl` (logi) [m], `transproc` (char), `keyindex` (char), `origduedt` (date), `apholdfl` (logi) [m], `jmjobid` (char), `jmjobrevno` (inte), `correctionty` (char), `correctionsuf` (char), `countrycd` (char), `manaddr3` (char), `addoncapfl` (logi[4]) [m], `shiptoaddr3` (char), `user10` (char), `user11` (char), `printprfl` (logi) [m], `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `closedapbatchfl` (logi) [m], `approvty` (char), `orgtotlineamt` (deci-2), `esbpurchaseorderfl` (logi) [m], `esbshipmentfl` (logi) [m], `contractno` (char) [m], `esbquotefl` (logi) [m], `esbreceivedeliveryfl` (logi) [m], `ackdt` (date), `ackrsn` (char), `freightexpectedty` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `revalno` (inte), `geocd` (inte), `outofcityfl` (logi) [m], `commtype` (char), `acktype` (char), `ackoper` (char), `frttermscd` (char), `frtbillacct` (char), `transferloc` (char), `extshipinstr` (char), `vendordno` (char), `esbedipofl` (logi) [m], `vendretauth` (char), `transdttmz` (datetm-tz) [i], `netbillty` (char), `esblostbusrsn` (char), `podoshipdt` (date), `ackdttz` (datetm-tz), `costeddttz` (datetm-tz), `duedttz` (datetm-tz), `enterdttz` (datetm-tz), `expshipdttz` (datetm-tz), `orderdttz` (datetm-tz), `paiddttz` (datetm-tz), `podoshipdttz` (datetm-tz), `printeddttz` (datetm-tz), `receiptdttz` (datetm-tz), `reqshipdttz` (datetm-tz), `suppwarrallownet` (deci-2), `addressoverfl` (logi) [m], `repricepct` (deci-2), `repricefl` (logi) [m]

### `poehb`
**PO Batch Receiving Header**
Fields: `cono` (inte) [i], `pono` (inte) [im], `posuf` (inte) [i], `vendno` (deci-0) [i], `whse` (char) [i], `actionty` (char), `openinit` (char), `operinit` (char), `transdt` (date), `transtm` (char), `receiptdt` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `receivefl` (logi) [im], `shipmentid` (char) [i], `updtfl` (logi) [m], `transproc` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `edishipmentid` (char), `edipackageid` (char), `receiptdttz` (datetm-tz)

### `poehe`
**PO Header EDI Specific Audit File**
Fields: `cono` (inte) [i], `pono` (inte) [im], `posuf` (inte) [i], `edicd` (char) [i], `seqno` (inte) [i], `vendno` (deci-0) [i], `duedtold` (date), `duedtupdfl` (logi) [m], `vendpono` (inte) [i], `vendposuf` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `duedtoldtz` (datetm-tz)

### `poei`
**PO Inventory Receipts Work File**
Fields: `cono` (inte) [i], `jrnlno` (inte) [i], `pono` (inte) [im], `posuf` (inte) [i], `seqno` (inte) [i], `lineno` (inte) [i], `shipprod` (char) [im], `reqprod` (char) [m], `price` (deci-5), `nosnlots` (deci-2), `qtyrcv` (deci-2), `stkqtyrcv` (deci-2), `vendprod` (char) [i], `eachfl` (logi) [m], `unit` (char), `qtyunavail` (deci-2), `reasunavty` (char), `corewarrty` (char), `cancelfl` (logi) [m], `whse` (char), `chrgqty` (deci-2), `nonstockty` (char), `tallyfl` (logi) [m], `serlottype` (char), `user1` (char), `speccostty` (char), `user2` (char), `notesfl` (char), `user3` (char), `conv` (deci-5), `user4` (char), `postfl` (logi) [m], `user5` (char), `stkadj` (deci-2), `user6` (deci-5), `qtyassign` (deci-2), `user7` (deci-5), `wmfl` (logi) [m], `user8` (date), `wmqtyrcv` (deci-2), `user9` (date), `trackfl` (logi) [m], `binloc` (char[2]), `upcid` (char), `catchweightfl` (logi) [m], `totcatchweight` (deci-5)

### `poel`
**PO Line Items**
*Purchase order line items.*
**Operators call this:** "Company" (Purchasing), "Warehouse" (Purchasing), "Order Status" (Purchasing), "Buyer" (Purchasing), "Received Cost" (Purchasing), "Received Quantity" (Purchasing), "Ordered Cost (Each)" (Purchasing), "Ordered Quantity" (Purchasing), "Weight" (Purchasing), "Purchase Order Number" (Purchasing), "PO Suffix" (Purchasing), "Line Number" (Purchasing), "Due Date" (Purchasing), "Order Date" (Purchasing)
Fields: `pono` (inte) [i], `posuf` (inte) [i], `whse` (char) [im], `transtype` (char) [i], `lineno` (inte) [i], `stkqtyord` (deci-2), `cono` (inte) [i], `proddesc` (char), `unit` (char), `buyer` (char), `transdt` (date), `enterdt` (date), `operinit` (char), `shipprod` (char) [im], `transtm` (char), `stkqtyrcv` (deci-2), `price` (deci-5), `prodline` (char), `vendno` (deci-0), `botype` (char), `netamt` (deci-2), `reqprod` (char), `weight` (deci-5), `cubes` (deci-5), `origcubes` (deci-5), `origweight` (deci-5), `notimeschg` (inte), `statustype` (char) [i], `leadoverty` (char), `icspecrecno` (inte), `printfl` (logi) [m], `sxextractdt` (date), `chrgqty` (deci-2), `origduedt` (date), `expshipdt` (date), `bono` (inte), `vafakeprodfl` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `nosnlots` (deci-2), `user7` (deci-5), `user8` (date), `user9` (date), `prevqtyord` (deci-2), `commentfl` (logi) [m], `duedt` (date), `invcost` (deci-5), `unitoverfl` (logi) [m], `priceoverfl` (logi) [m], `stkqtyoverfl` (logi) [m], `qtyord` (deci-2), `qtyrcv` (deci-2), `shipfmno` (inte), `qtyrel` (deci-2), `costoverfl` (logi) [m], `nonstockty` (char), `rcvcost` (deci-5), `qtyunavail` (deci-2), `reasunavty` (char), `eachfl` (logi) [m], `proddesc2` (char), `prodcat` (char), `tallyfl` (logi) [m], `glcostrcv` (deci-2), `glcostinv` (deci-2), `wodiscamt` (deci-2), `catwtfl` (logi) [m], `netrcv` (deci-2), `exlatefl` (logi) [m], `tariffamt` (deci-2), `domrcvcost` (deci-5), `dominvcost` (deci-5), `landedcost` (deci-5), `addonamt` (deci-2[4]), `user1` (char), `user2` (char), `costeachfl` (logi) [m], `wmqtyrcv` (deci-2), `taxabletyau` (char), `taxoverideau` (logi) [m], `taxgroup` (inte), `taxrateau` (deci-2), `taxamt` (deci-2), `unitchgfl` (logi) [m], `reqshipdt` (date), `qtycosted` (deci-2), `stkqtybilled` (deci-2), `origtrf` (deci-2), `unitconv` (deci-5), `transproc` (char), `keyindex` (char), `ignoreltfl` (logi) [m], `rcvsafety` (deci-2), `rcvnetavl` (deci-2), `leadtime` (inte), `recvaddfl` (logi) [m], `contno` (char), `usetrackfl` (logi) [m], `trackno` (inte) [m], `tracklineno` (inte), `orgpono` (inte), `orgposuf` (inte), `warrantyfl` (logi) [m], `correctionty` (char), `countrycd` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `contractno` (char) [m], `pdsvcrecno` (inte), `ackdt` (date), `ackrsn` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `ncnr` (char), `countryoforigin` (char), `tariffcd` (char), `srcrestrictovrfl` (logi) [m], `vendretauth` (char), `transdttmz` (datetm-tz) [i], `netbillty` (char), `upcid` (char), `esblostbusrsn` (char), `dlvrydatecd` (char), `ackdttz` (datetm-tz), `duedttz` (datetm-tz), `enterdttz` (datetm-tz), `expshipdttz` (datetm-tz), `reqshipdttz` (datetm-tz), `sxextractdttz` (datetm-tz), `suppwarrallowpct` (deci-5), `suppwarrallownet` (deci-2), `catchweightfl` (logi) [m], `totcatchweight` (deci-5)

### `poela`
**PO Costing Addons**
Fields: `cono` (inte) [i], `vendno` (deci-0) [m], `addonno` (inte) [i], `pono` (inte) [im], `posuf` (inte) [i], `lineno` (inte) [i], `jrnlno` (inte) [i], `setno` (inte) [i], `currencyty` (char), `addonamt` (deci-2), `updatefl` (logi) [m], `transdt` (date), `transtm` (char), `operinit` (char), `bundleid` (char) [i], `src` (char), `exchgrate` (deci-7[2]), `alloctype` (char), `uninvamt` (deci-2), `compseqno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `apetjrnlno` (inte), `apetsetno` (inte), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `poelb`
**PO Batch Receiving Line Items**
Fields: `pono` (inte) [i], `posuf` (inte) [i], `lineno` (inte) [i], `cono` (inte) [i], `transdt` (date), `operinit` (char), `transtm` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cancelfl` (logi) [m], `user1` (char), `user2` (char), `shipmentid` (char) [i], `qtyrcv` (deci-2), `stkqtyrcv` (deci-2), `shipprod` (char) [i], `reqprod` (char), `unit` (char), `unitconv` (deci-5), `qtyunavail` (deci-2), `reasunavty` (char), `transproc` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `edishipmentid` (char), `edipackageid` (char)

### `poelc`
**PO Costing Lines**
Fields: `cono` (inte) [i], `vendno` (deci-0) [m], `pono` (inte) [im], `posuf` (inte) [i], `lineno` (inte) [i], `whse` (char), `prod` (char), `qtycost` (deci-2), `cost` (deci-5), `eachfl` (logi) [m], `jrnlno` (inte) [i], `setno` (inte) [i], `currencyty` (char), `exchgrate` (deci-7[2]), `paidfl` (logi) [m], `batchnm` (char), `checkno` (deci-0), `bupdcompty` (char), `qtyissued` (deci-2), `bundleid` (char) [i], `qtycharged` (deci-2), `compseqno` (inte) [i], `updatefl` (logi) [m], `transdt` (date), `transtm` (char), `user1` (char), `operinit` (char), `user2` (char), `unitconv` (deci-5), `user3` (char), `user4` (char), `srcost` (deci-5), `user5` (char), `qtyfppd` (deci-2), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `stkcost` (deci-5), `transproc` (char), `apetjrnlno` (inte), `apetsetno` (inte), `costeddt` (date), `transdttmz` (datetm-tz) [i], `costeddttz` (datetm-tz), `lastcostupdtfl` (logi) [m], `rowpointer` (char) [i]

### `poele`
**PO Line EDI Specific Audit File**
Fields: `cono` (inte) [i], `duedtold` (date), `duedtupdfl` (logi) [m], `edicd` (char) [i], `operinit` (char), `pono` (inte) [im], `posuf` (inte) [i], `seqno` (inte) [i], `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `lineno` (inte) [i], `priceold` (deci-5), `priceupdfl` (logi) [m], `prodold` (char), `produpdfl` (logi) [m], `qtyold` (deci-2), `qtyupdfl` (logi) [m], `uomold` (char), `uomupdfl` (logi) [m], `vendno` (deci-0) [i], `vendpono` (inte) [i], `vendposuf` (inte) [i], `vendlineno` (char) [i], `vendpriceuom` (char), `asnshipid` (char) [i], `asnqtyrcv` (deci-2), `asnuom` (char), `asnprod` (char), `poeiqtyrcv` (deci-2), `poeiuom` (char), `poeireasunav` (char), `poeiqtyunav` (deci-2), `rpt861fl` (logi) [im], `rpt861dt` (date), `transproc` (char), `asnpkgid` (char), `duedtoldtz` (datetm-tz), `rpt861dttz` (datetm-tz)

### `poelo`
**PO Line Item Order file**
Fields: `cono` (inte) [i], `pono` (inte) [im], `lineno` (inte) [i], `ordertype` (char) [i], `orderaltno` (inte) [i], `orderaltsuf` (inte) [i], `linealtno` (inte) [i], `seqno` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `oordertype` (char), `oorderaltno` (inte), `oorderaltsuf` (inte), `oseqaltno` (deci-0), `olinealtno` (inte), `wtcono` (inte), `owtcono` (inte), `seqaltno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `posuf` (inte) [i], `transproc` (char), `rowpointer` (char) [i]

### `poer`
**PO Receiver**
Fields: `cono` (inte) [im], `whse` (char) [im], `operinit` (char), `transdt` (date), `transtm` (char), `enterdt` (date), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `receiverno` (char) [i], `proofline` (inte), `totline` (inte), `proofqty` (deci-2), `totqty` (deci-2), `urecno` (deci-0) [i], `location` (char) [i], `transproc` (char), `enterdttz` (datetm-tz), `rowpointer` (char) [i]

### `poerad`
**Purchase Order Acceptance Warehouse Detail**
Fields: `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `reportno` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `whse` (char) [i], `stkqtyord` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `prodline` (char), `qtyord` (deci-2), `frcstamt1` (deci-2), `frcstamt2` (deci-2), `frcstamt3` (deci-2), `frcstamt4` (deci-2), `frcstamt5` (deci-2), `frcstamt6` (deci-2), `frcstamt7` (deci-2), `frcstamt8` (deci-2), `frcstamt9` (deci-2), `frcstamt10` (deci-2), `frcstamt11` (deci-2), `frcstamt12` (deci-2), `startmth` (inte), `transproc` (char)

### `poerah`
**PO RRAR Header Acceptance**
Fields: `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `reportno` (inte) [i], `vendno` (deci-0) [im], `prodline` (char) [im], `shipfmno` (inte), `billtowhse` (char), `whse` (char) [i], `buyer` (char) [i], `shiptonm` (char) [m], `shiptoaddr` (char[2]), `shiptocity` (char), `shiptost` (char), `shiptozip` (char), `shipinstr` (char), `refer` (char), `duedt` (date), `shipviaty` (char), `termstype` (char) [m], `ignoreltfl` (logi) [m], `subfl` (logi) [m], `bofl` (logi) [m], `resalefl` (logi) [m], `resaleno` (char), `orderdisp` (char), `totlineamt` (deci-2), `totweight` (deci-5), `totcubes` (deci-5), `totqtyord` (deci-2), `transtype` (char), `oper2` (char) [im], `reportnm` (char) [i], `nextlineno` (inte), `fobfl` (logi) [m], `linerevfl` (logi) [m], `currencyty` (char), `user1` (char), `user2` (char), `addlcarrycost` (deci-2), `tarbuyamt` (deci-2), `notesfl` (char), `rpterr` (char), `tarbuytype` (char), `sourcety` (char), `frtconsldtcd` (char), `openinit` (char), `reqshipdt` (date), `createdt` (date), `dueoverfl` (logi) [m], `rushfl` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `conslinefl` (logi) [m], `user6` (deci-5), `conswhsefl` (logi) [m], `user7` (deci-5), `user8` (date), `user9` (date), `wodiscoverfl` (logi) [m], `wodiscamt` (deci-2), `wodisctype` (logi) [m], `automrgfl` (logi) [m], `reqoverfl` (logi) [m], `mergefl` (logi) [m], `orderptfl` (logi) [m], `transproc` (char), `reportpri` (inte), `totcritical` (inte), `totbelowop` (inte), `totrush` (inte), `totnpna` (inte), `pridesc` (char), `reviewcycle` (inte), `totdoc` (inte), `rpterrfl` (logi) [m], `blno` (inte), `blsuf` (inte), `esrqstid` (char), `shiptoaddr3` (char), `addonamt` (deci-2[4]), `addoncapfl` (logi[4]) [m], `addondistr` (char), `addonnet` (deci-2[4]), `addonno` (inte[4]), `addontype` (logi[4]) [m], `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `contractno` (char) [m], `freightexpectedty` (char), `totsuper` (inte), `countrycd` (char), `geocd` (inte), `outofcityfl` (logi) [m], `rowpointer` (char) [i], `frttermscd` (char), `frtbillacct` (char), `transferloc` (char), `createdttz` (datetm-tz), `duedttz` (datetm-tz), `reqshipdttz` (datetm-tz), `suppwarrallownet` (deci-2), `addressoverfl` (logi) [m], `repricepct` (deci-2), `repricefl` (logi) [m]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `buyer` (Buyer) — Can be CHAR(24) if using xref; Valid values/xref: SASTT - B; Required
- `whse` (Ship to Whse) — Warehouse Receiving PO. Can be CHAR(24) if using xref.; Valid values/xref: ICSD; Required
- `vendno` (Vendor #) — Can be CHAR(24) if using xref; Valid values/xref: APSV; Required
- `prodline` (Product Line) — Valid values/xref: ICSL
- `shipfmno` (Ship From) — Valid values/xref: APSS
- `billtowhse` (Bill to Whse) — Warehouse for Billing Address. Can be CHAR(24) if using xref.; Valid values/xref: ICSD; Default: whse
- `createdt` (Created Date) — When the PO Renumbering process is used, this date will be moved into PO Order date, used to calculate lead time when the PO is received; Required
- `nextlineno` (Next Line #) — Enter total number of lines to be converted in POERAL for this PO; Required
- `shiptonm` (Shipto Name) — Receiving Warehouse Name; Default: ICSD
- `shiptoaddr1` (Shipto Addr1) — Receiving Warehouse Addr1; Default: ICSD
- `shiptoaddr2` (Shipto Addr2) — Receiving Warehouse Addr2; Default: ICSD
- `shiptoaddr3` (Shipto Addr3) — Receiving Warehouse Addr3; Default: ICSD
- `shiptocity` (Shipto city) — Receiving Warehouse City; Default: ICSD
- `shiptost` (Shipto State) — Receiving Warehouse State; Default: ICSD
- `shiptozip` (Shipto Zip) — Receiving Warehouse Zip; Default: ICSD
- `shipviaty` (Ship Via) — Can be CHAR(24) if using xref; Valid values/xref: SASTT - S; Required
- `frttermscd` (Freight Terms Code) — Available Starting 10.0; Valid values/xref: SASTT - FT
- `transferloc` (Transfer Location) — Available Starting 10.0
- `frtbillacct` (Frt Bill Account) — Available Starting 10.0
- `orderdisp` (Order Disposition) — (S)hip Complete, (T)ag & Hold, (W)ill Call or blank; Valid values/xref: S, T, W or blank
- `refer` (Reference - Old PO #) — If using option to assign PO Number from Old Number, Refer must be INT(7) PO # format.; Valid values/xref: See Note Below; Required
- `countrycd` (Country Code) — Available starting in 6.1.060; Valid values/xref: SASTT - W
- `geocd` (Geo Code) — Used with TaxWare only Available starting in 6.10.60
- `outofcityfl` (Outside City Limits Flag) — Used with TaxWare Enterprise only Available starting in 6.10.61; Valid values/xref: Y or N; Default: N
- `termstype` (Terms) — Can be CHAR(24) if using xref; Valid values/xref: SASTT - T; Required; Default: APSV Terms
- `resalefl` (Resale Flag) — Valid values/xref: Y or N; Default: Y
- `wodiscamt` (Whole Order Discount Amount) — Dollar or Percent based on wodisctype
- `wodisctype` (Whole Order Discount Type) — ($) - Dollar Amount (%) - Percentage; Valid values/xref: $ or %; Default: %
- `addonno1` (Addon No 1) — Available Starting 4.1; Valid values/xref: SASTT - X
- `addonamt1` (Addon Amount 1) — Either $ Amount or Percentage. Available Starting 4.1
- `addontype1` (Addon Amount Type) — ($) - Dollar Amount (%) - Percentage Available Starting 4.1; Valid values/xref: $ or %; Default: $
- `addoncapfl1` (Addon Cap Flag 1) — (C)apitalized (E)xpensed Available Starting 4.1; Valid values/xref: C or E; Default: E
- `addondist1` (Cap Addon Distribution Method 1) — (D)ollar,(C)ube, (W)eight or (U)nit. Required if Cap Addon Flag is Yes. Available Starting 4.1; Valid values/xref: <Blank>, D, C, W or U; Default: D
- `addonno2` (Addon No 2) — Available Starting 4.1; Valid values/xref: SASTT - X
- `addonamt2` (Addon Amount 2) — Either $ Amount or Percentage. Available Starting 4.1
- `addontype2` (Addon Amount Type) — ($) - Dollar Amount (%) - Percentage Available Starting 4.1; Valid values/xref: $ or %; Default: $
- `addoncapfl2` (Addon Cap Flag 2) — (C)apitalized (E)xpensed Available Starting 4.1; Valid values/xref: C or E; Default: E
- `addondist2` (Cap Addon Distribution Method 2) — (D)ollar,(C)ube, (W)eight or (U)nit. Required if Cap Addon Flag is Yes. Available Starting 4.1; Valid values/xref: <Blank>, D, C, W or U; Default: D
- `addonno3` (Addon No 3) — Available Starting 4.1; Valid values/xref: SASTT - X
- `addonamt3` (Addon Amount 3) — Either $ Amount or Percentage. Available Starting 4.1
- `addontype3` (Addon Amount Type) — ($) - Dollar Amount (%) - Percentage Available Starting 4.1; Valid values/xref: $ or %; Default: $
- `addoncapfl3` (Addon Cap Flag 3) — (C)apitalized (E)xpensed Available Starting 4.1; Valid values/xref: C or E; Default: E
- `addondist3` (Cap Addon Distribution Method 3) — (D)ollar,(C)ube, (W)eight or (U)nit. Required if Cap Addon Flag is Yes. Available Starting 4.1; Valid values/xref: <Blank>, D, C, W or U; Default: D
- `addonno4` (Addon No 4) — Available Starting 4.1; Valid values/xref: SASTT - X
- `addonamt4` (Addon Amount 4) — Either $ Amount or Percentage. Available Starting 4.1
- `addontype4` (Addon Amount Type) — ($) - Dollar Amount (%) - Percentage Available Starting 4.1; Valid values/xref: $ or %; Default: $
- `addoncapfl4` (Addon Cap Flag 4) — (C)apitalized (E)xpensed Available Starting 4.1; Valid values/xref: C or E; Default: E
- `addondist4` (Cap Addon Distribution Method 4) — (D)ollar,(C)ube, (W)eight or (U)nit. Required if Cap Addon Flag is Yes. Available Starting 4.1; Valid values/xref: <Blank>, D, C, W or U; Default: D
- `freightexpectedty` (Freighted Expected Type) — (Y)es or (N)o; Valid values/xref: Y or N; Default: Y
- `subfl` (Substitutes allowed) — (Y)es or (N)o; Valid values/xref: Y or N; Default: Y
- `bofl` (Allow Back Orders) — (Y)es or (N)o; Valid values/xref: Y or N; Default: Y
- `fobfl` (Free on Boad) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `ignoreltfl` (Ignore Leadtime) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `conslinefl` (Consolidate Lines) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `conswhsefl` (Consolidate Whses) — (Y)es or (N)o; Valid values/xref: Y or N; Default: N
- `frtconsldtcd` (Freight Consolidation code) — Valid values/xref: SASTT - FC
- `currencyty` (Currency Type) — For Foreign Currency Vendors only; Valid values/xref: SASTC
- `user5` (user5) — Used for Conversion Import ID
- `user10` (User10) — Available Starting 4.1
- `user11` (User11) — Available Starting 4.1
- `user12` (User12) — Available Starting 4.1
- `user13` (User13) — Available Starting 4.1
- `user14` (User14) — Available Starting 4.1
- `user15` (User15) — Available Starting 4.1
- `user16` (User16) — Available Starting 4.1
- `user17` (User17) — Available Starting 4.1
- `user18` (User18) — Available Starting 4.1
- `user19` (User19) — Available Starting 4.1
- `user20` (User20) — Available Starting 4.1
- `user21` (User21) — Available Starting 4.1
- `user22` (User22) — Available Starting 4.1
- `user23` (User23) — Available Starting 4.1
- `user24` (User24) — Available Starting 4.1
- `repricepct` (Auto Vendor Reprice Percent) — Available Starting in 11.20.2
- `repricefl` (Reprice) — Available Starting in 11.20.2; Valid values/xref: Y or N; Default: N

### `poeral`
**PO RRAR Line Item Acceptance**
Fields: `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `reportno` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `shipprod` (char) [im], `whse` (char), `vendfl` (logi) [m], `accepttype` (char), `qtyord` (deci-2), `unit` (char), `price` (deci-5), `ordertype` (char), `orderaltno` (inte), `orderaltsuf` (inte), `linealtno` (inte), `duedt` (date), `cubes` (deci-5), `weight` (deci-5), `netamt` (deci-2), `proddesc` (char), `wtcono` (inte), `pdsvfl` (logi) [m], `nonstockty` (char), `seasontype` (char), `famgrptype` (char), `stkqtyord` (deci-2), `priceoverfl` (logi) [m], `qtysurplus` (deci-2), `prodcat` (char), `unitconv` (deci-5), `user1` (char), `user2` (char), `addlcarrycost` (deci-2), `orignetamt` (deci-2), `rpterr` (char), `proddesc2` (char), `seqaltno` (inte), `reqshipdt` (date), `commentfl` (logi) [m], `rushfl` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `lockfl` (logi) [m], `npnafl` (logi) [m], `ignoreltfl` (logi) [m], `icspecrecno` (inte), `transproc` (char), `reportpri` (inte), `belowopfl` (logi), `criticalfl` (logi) [m], `blno` (inte), `blsuf` (inte), `esrqstid` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `companyrank` (char) [i], `whserank` (char) [i], `contractno` (char) [m], `pdsvcrecno` (inte), `superfl` (logi) [m], `countryoforigin` (char), `tariffcd` (char), `custreservefoundfl` (logi) [m], `custreserveqty` (deci-2), `srcrestrictovrfl` (logi) [m], `custforecastfoundfl` (logi) [m], `custforecastqty` (deci-2), `duedttz` (datetm-tz), `reqshipdttz` (datetm-tz), `suppwarrallowpct` (deci-5), `suppwarrallownet` (deci-2), `rowpointer` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `refer` (Reference) — Purchase Order Number, must match corresponding POERAH record; Valid values/xref: POERAH; Required
- `whse` (Whse) — Must be same warehouse as POERAH . Can be CHAR(24) if using xref.; Valid values/xref: ICSD; Required
- `shipprod` (Ship Product) — If not found in ICSW, will create a non-stock line item with no Tie to OE, this will have to be manually added in POET. Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP/ICSW; Required
- `unit` (Unit) — Qty Unit of Measure, only used if not ICSP Stocking Unit Must be EACH for non-stocks.; Valid values/xref: ICSEU or SASTT-U; Default: ICSP Stocking or EACH
- `unitconv` (Unit Conversion Factor to Stocking Units) — Number of stocking units in this unit of measure. Required if using unit other than stocking unit. Must be 1 for non-stocks.; Valid values/xref: ICSEU or SASTT-U; Default: 1
- `price` (Price) — per unit cost charged by Vendor
- `netamt` (Net Amount) — Extended Line Total for quantity ordered
- `duedt` (Due Date) — Will use POERAH Due Date if Blank; Default: POERAH
- `prodcat` (Product Category) — Only used for non-stocks. Leave Blank to use ICSP Product Category. Can be CHAR(24) if using xref. Non-stocks will use DCAOI default if blank or invalid.; Valid values/xref: SASTT - C; Default: ICSP or DCAOI Default
- `proddesc` (Product Description) — Only used for non-stocks. Leave Blank to use ICSP Product Description.; Default: ICSP
- `proddesc2` (Product Description 2) — Only used for non-stocks. Leave Blank to use ICSP Product Description.; Default: ICSP
- `countryoforigin` (Country of Origin) — Available Starting in 10.0.1; Valid values/xref: SASTT - W; Default: Stock Products - ICSW country of origin
- `tariffcd` (HS Code) — Available Starting in 10.0.1; Valid values/xref: SASGT; Default: Stock Products - ICSW HS Code
- `user5` (user5) — Used for Conversion Import ID
- `user10` (User10) — Available Starting 4.1
- `user11` (User11) — Available Starting 4.1
- `user12` (User12) — Available Starting 4.1
- `user13` (User13) — Available Starting 4.1
- `user14` (User14) — Available Starting 4.1
- `user15` (User15) — Available Starting 4.1
- `user16` (User16) — Available Starting 4.1
- `user17` (User17) — Available Starting 4.1
- `user18` (User18) — Available Starting 4.1
- `user19` (User19) — Available Starting 4.1
- `user20` (User20) — Available Starting 4.1
- `user21` (User21) — Available Starting 4.1
- `user22` (User22) — Available Starting 4.1
- `user23` (User23) — Available Starting 4.1
- `user24` (User24) — Available Starting 4.1

### `poerao`
**PO RRAR Alternate Order**
Fields: `cono` (inte) [i], `lineno` (inte) [i], `ordertype` (char), `orderaltno` (inte), `orderaltsuf` (inte), `linealtno` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `reportno` (inte) [i], `wtcono` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `co_num` (char) [i], `wh_num` (char) [im], `printer_id` (char) [im], `printer` (char) [c], `description` (char), `type` (logi) [m], `print_form` (char), `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [im], `prodcat` (char) [i], `addfl` (logi), `changefl` (logi), `restrictfl` (logi), `custom_data` (char[5]), `pick_sequence` (inte) [i], `description` (char), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `id` (inte) [im], `line` (inte) [im], `abs_num` (char) [m], `lot` (char), `from_bin` (char), `to_bin` (char) [m], `allocation_status` (logi), `line_status` (char), `item_qty` (deci-2), `act_qty` (deci-2), `kit_qty` (deci-2), `kit_num` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `id` (inte) [im], `co_num` (char) [im], `wh_num` (char) [im], `dept_num` (inte) [im], `name` (char) [im], `date_time` (char) [i], `staging_status` (char) [i], `allocation_status` (logi), `type_id` (char), `batch` (inte), `order_line` (inte) [i], `kit_build_type` (char), `custom_data` (char[5]), `wo_done` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `docty` (char) [i], `auditallfl` (logi) [m], `hardstopfl` (logi) [m], `warnfl` (logi) [m], `level` (inte), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `edifilename` (char) [i], `section` (char) [i], `secseq` (inte) [i], `olddata` (char), `newdata` (char), `docid` (inte) [i], `releasefl` (char) [i], `cono` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `docty` (char) [i], `docid` (inte) [i], `section` (char) [i], `secseq` (inte) [i], `level` (inte) [i], `msgno` (inte) [i], `extmsg` (char) [i], `overridefl` (logi) [m], `hardstopfl` (logi) [im], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `printmst`
**Table contains all printer queues**

### `prod_stg_dtl`
**Contains the detail for production staging**

### `prod_stg_mst`
**Has information about production stages**

### `prodcat`
**Table contains product categories and information on what to do with products with these categories**

### `ptxediao`
**PTX EDI Admin Options**

### `ptxedidata`
**ptx edi data**

### `ptxedimsg`
**PTX Document Message File.  Used to store messages associated to a specific document.**

### `ptxet`
**PTX Transactions**
Fields: `cono` (inte) [i], `stagecd` (inte) [i], `custorderno` (inte) [i], `custordersuf` (inte) [i], `vendno` (deci-0) [im], `vendshipfmno` (inte) [i], `pono` (inte) [im], `posuf` (inte) [i], `vendcustno` (deci-0) [m], `vendorderno` (inte) [i], `vendordersuf` (inte) [i], `vendordamt` (deci-2), `vendinvno` (char), `vendinvamt` (deci-2), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `jrnlno` (inte), `setno` (inte), `custno` (deci-0) [m], `shipto` (char) [m], `cono` (inte) [i], `ptxfeeid` (inte), `vendorderno` (inte) [i], `vendordersuf` (inte) [i], `vendorderln` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `ptxetdet`
**PTX Transaction Fee Detail**

### `ptxfee`
**PTX Fee Table**
Fields: `cono` (inte) [i], `ptxfeeid` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `prodcat` (char) [i], `prod` (char) [im], `vendno` (deci-0) [im], `shipfmno` (inte) [i], `feetype` (char) [i], `basedon` (char), `basedonamt` (char), `feeamt` (deci-2), `descrip` (char), `startdt` (date) [i], `enddt` (date) [i], `lasttransdt` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `rowpointer` (char) [im], `cono` (inte) [im], `type` (char), `statusty` (char) [im], `transdttmz` (datetm-tz) [im], `orderno` (inte) [i], `ordersuf` (inte) [i], `processmsg` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `srcrowpointer` (char) [im], `seqno` (inte) [im], `cono` (inte) [im], `orderno` (inte) [im], `ordersuf` (inte) [im], `type` (char) [im], `createproc` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [im], `srcrowpointer` (char) [im], `shiptorowpointer` (char) [im], `custrowpointer` (char) [im], `vendno` (deci-0) [im], `shipfmno` (inte) [im], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `hierarchy` (inte) [i], `nodaysmin` (inte), `nodaysmax` (inte), `vendordflt` (logi) [m], `keytype` (char) [im], `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `prod` (char) [im], `vendno` (deci-0) [im], `shipfmno` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `prodcat` (char) [i], `hierarchy` (inte) [i], `msgno` (inte) [i], `msgtext` (char), `level` (inte), `docty` (char), `warnfl` (logi) [m], `errfl` (logi) [m], `hardstopfl` (logi) [m], `activefl` (logi) [m], `trmgrlang` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [im], `distpartnerid` (char) [i], `distinvno` (inte) [i], `distinvsuf` (inte) [i], `distinvseqno` (inte) [i], `seqno` (inte) [i], `descrip` (char), `specservcd` (char), `specchrgcd` (char), `addonnet` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [im], `distpartnerid` (char) [i], `distinvno` (inte) [i], `distinvsuf` (inte) [i], `distinvseqno` (inte) [i], `addrtype` (char) [i], `name` (char), `addr1` (char), `addr2` (char), `addr3` (char), `city` (char), `state` (char), `zipcd` (char), `phone` (char), `countrycd` (char), `partnerid` (char), `dunsno` (char), `fedtaxid` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [im], `whse` (char) [m], `docid` (inte), `enterdt` (date), `statustype` (char) [i], `exchgtransty` (char), `stagecd` (inte), `distpartnerid` (char) [im], `vendno` (deci-0) [m], `shipfmno` (inte), `distinvno` (inte) [im], `distinvsuf` (inte) [im], `distinvseqno` (inte) [im], `distinvtype` (char), `distinvdt` (date), `altpo` (char), `rlypono` (inte) [m], `rlyposuf` (inte), `recpono` (inte) [m], `recposuf` (inte), `custpartnerid` (char) [i], `custno` (deci-0) [m], `shipto` (char) [m], `custinvno` (char), `custinvsuf` (char), `altorder` (char), `transtype` (char) [m], `rlyorderno` (inte), `rlyordersuf` (inte), `recorderno` (inte) [i], `recordersuf` (inte) [i], `custpo` (char), `refer` (char), `placedby` (char), `totinvamt` (deci-2), `totln` (inte), `totqtyord` (deci-2), `termscd` (char), `termspct` (char), `termsdtcd` (char), `termsdiscdt` (char), `termsdiscdays` (char), `termsduedt` (char), `termsduedays` (char), `termsdescr` (char), `termsdiscproxday` (char), `currencyty` (char), `recondt` (date), `reportcd` (char), `reporteddt` (date), `keyindex` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `distinvdttz` (datetm-tz), `recondttz` (datetm-tz), `reporteddttz` (datetm-tz), `cono` (inte) [im], `distpartnerid` (char) [i], `vendno` (deci-0) [m], `shipfmno` (inte), `distinvno` (inte) [i], `distinvsuf` (inte) [i], `distinvseqno` (inte) [i], `distinvlineno` (inte) [i], `custpartnerid` (char), `custno` (deci-0) [m], `shipto` (char) [m], `whse` (char) [m], `specnstype` (char), `shipprod` (char) [m], `sellerprod` (char) [m], `buyerprod` (char) [m], `qtyord` (deci-2), `proddesc` (char), `unit` (char), `price` (deci-5), `prcunit` (char), `netord` (deci-2), `netamt` (deci-2), `keyindex` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `statustype` (char), `cono` (inte) [im], `distpartnerid` (char) [i], `distinvno` (inte) [i], `distinvsuf` (inte) [i], `distinvseqno` (inte) [i], `distinvlineno` (inte) [i], `noteseqno` (inte) [i], `notetxt` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `operinit` (char), `name` (char) [i], `type` (char) [i], `description` (char), `public` (logi) [m], `tbheight` (deci-2), `tbwidth` (deci-2), `outlinestart` (char), `outlinetitle` (char), `oper2` (char) [i], `outlinemodule` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `operinit` (char), `name` (char) [i], `objectid` (char) [i], `type` (char), `action` (char), `objtooltip` (char), `objlabel` (char), `objbitmap` (char), `objseq` (inte), `objstatusmsg` (char), `oper2` (char) [i], `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `Oper` (char) [i], `Section` (char) [i], `SubSection` (char) [i], `Object` (char) [i], `Keyname` (char) [i], `KeyValue` (char), `pvfunction` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `menuset` (char) [i], `functionname` (char) [i], `trmgrlang` (char) [i], `attrname` (char) [i], `attrvalue` (char), `objid` (inte) [i], `attrid` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `menuset` (char) [i], `functionname` (char) [i], `trmgrlang` (char) [i], `objid` (inte) [i], `linkid` (inte) [i], `source` (inte), `target` (inte), `linktype` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `menuset` (char) [i], `functionname` (char) [i], `trmgrlang` (char) [i], `parentid` (inte) [i], `objid` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `objfile` (char), `objname` (char), `objrow` (deci-2), `objcol` (deci-2), `objheight` (deci-2), `objwidth` (deci-2), `objpage` (inte) [i], `oper2` (char), `changedt` (date), `changetm` (inte), `subject` (char) [i], `function` (char) [i], `setting` (char), `note` (char), `cono` (inte) [i], `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `changedttz` (datetm-tz), `subject` (char) [i], `installnote` (char), `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `cono` (inte) [i], `batchnm` (char) [i], `setno` (inte) [i], `addonno` (inte) [i], `vendno` (deci-0) [im], `apinvno` (char) [i], `transdt` (date), `transtm` (char), `origamt` (deci-2), `applyamt` (deci-2), `updatefl` (logi) [m], `currencyty` (char), `exchgrate` (deci-7[2]), `statustype` (logi) [im], `pono` (inte) [im], `operinit` (char), `alloctype` (char), `posuf` (deci-0) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `vendno` (deci-0) [i], `apinvno` (char) [i], `pono` (inte) [i], `costord` (deci-5), `statustype` (logi) [im], `proddesc` (char), `qtycost` (deci-2), `cost` (deci-5), `currencyty` (char), `exchgrate` (deci-7[2]), `batchnm` (char) [i], `setno` (inte) [i], `whse` (char), `costrcv` (deci-5), `qtyord` (deci-2), `qtyrcv` (deci-2), `unitconv` (deci-5), `eachfl` (logi) [m], `shipprod` (char) [m], `operinit` (char), `transdt` (date), `transtm` (char), `posuf` (deci-0) [i], `lineno` (deci-0) [i], `autorecfl` (char), `proddesc2` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `updatefl` (logi) [m], `revalno` (inte), `DocID` (inte) [i], `DocKey` (char), `DocType` (char), `DocTitle` (char), `KeyType` (char), `FullName` (char), `ShortName` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `changedt` (date) [i], `changetm` (inte) [i], `ratefield` (char) [i], `setting` (char), `cono` (inte) [i], `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `currencyty` (char) [i], `oper2` (char), `cono` (inte) [i], `keyvalue1` (char) [i], `keyvalue2` (char) [i], `keytype` (char) [i], `descrip` (char), `chunk` (inte) [i], `imageblob` (raw), `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `jobrevno` (inte) [i], `lineno` (inte) [i], `prod` (char), `prodcat` (char), `proddesc` (char), `prodline` (char), `prline` (char), `linetype` (char), `unit` (char), `frzrebty` (char), `qtyord` (deci-2), `scrndiscamt` (deci-5), `price` (deci-5), `scrnprodcost` (deci-5), `scrnpdcost` (deci-5), `vendno` (deci-0), `prvendno` (deci-0), `kitfl` (logi) [m], `disctype` (logi) [m], `maint-l` (char), `prodtype` (char), `reqprod` (char), `xrefprodty` (char), `crprod` (char), `linefl` (logi) [m], `cataddfl` (logi) [m], `pricereset` (logi) [m], `costoverfl` (logi) [m], `stkqtyord` (deci-2), `unitconv` (deci-5), `priceover` (deci-5), `calcdiscamt` (deci-6), `rebamt` (deci-5), `calcprodcost` (deci-6), `calcpdcost` (deci-6), `idicsp` (reci), `idicsw1` (reci), `idicsw2` (reci), `idjmel` (reci), `speccostty` (char), `csunperstk` (deci-6), `specconv` (inte), `prccostper` (char), `icspecrecno` (inte), `ordertype` (char), `arpwhse` (char), `qtytype` (char), `manprice` (logi) [m], `priceroll` (logi) [m], `promofl` (logi) [m], `pdrecno` (inte), `idpdsc` (reci), `lostbustyl` (char), `slsrepin` (char), `slsrepout` (char), `commtype` (char), `priceclty` (char), `printpricefl` (logi) [m], `subtotalfl` (logi) [m], `disccd` (inte), `prodpricecd` (deci-2), `pricelevel` (inte), `scrncost` (deci-5), `stkunit` (char), `commentfl` (logi) [m], `totlinefl` (logi) [m], `nosnlots` (deci-2), `nosnlotsk` (deci-2), `baseprice` (deci-5), `listprice` (deci-5), `orgdiscamt` (deci-5), `orgnetord` (deci-2), `orgnosnlots` (deci-2), `orgnosnlotsk` (deci-2), `orgpdrecno` (inte), `orgprice` (deci-5), `orgprod` (char), `orgprodcat` (char), `orgprodcost` (deci-5), `orglinetype` (char), `orgstkqtyord` (deci-2), `orgqtyord` (deci-2), `orgtotprice` (deci-5), `orgtotqtyord` (deci-2), `orgunit` (char), `orgunitchg` (char), `orgidicsp` (reci), `orgidicsw1` (reci), `orgidicsw2` (reci), `orgweight` (deci-2), `orgrebamt` (deci-5), `firstmarginwarnfl` (logi) [m], `firstsuperwarnfl` (logi) [m], `filler-1` (char), `filler-2` (char), `filler-3` (char), `filler-4` (char), `filler-5` (char), `reqshipdt` (date), `promisedt` (date), `filler-7` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `jmelrecid` (reci), `jmelrowid` (char), `priceonty` (char), `qtybreakty` (char), `serlottype` (char), `proddesc2` (char), `vcspeccostty` (char), `vccsunperstk` (deci-6), `vcspecconv` (inte), `vcprccostper` (char), `vcspecrecno` (inte), `spcconvertfl` (logi) [m], `jobid` (char) [i], `specnstype` (char), `orgspecnstype` (char), `priceoverfl` (logi) [m], `netord` (deci-2), `pricetype` (char), `duedt` (date), `linestat` (char), `printtype` (char), `taxablety` (char), `marginpct` (deci-2), `minmargin` (deci-2), `groupnm` (char), `userchr1` (char), `userchr2` (char), `userchr3` (char), `userchr4` (char), `userdec1` (deci-5), `userdec2` (deci-5), `userdt1` (date), `userdt2` (date), `pricetypefl` (logi) [m], `custno` (deci-0), `cono` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `prod` (char), `kitrollty` (char), `prodcat` (char), `proddesc` (char), `prodline` (char), `prline` (char), `specnstype` (char), `unit` (char), `frzrebty` (char), `qtyord` (deci-2), `qtyship` (deci-2), `netavail` (deci-2), `scrndiscamt` (deci-5), `price` (deci-5), `scrnprodcost` (deci-5), `scrnpdcost` (deci-5), `scrndatccost` (deci-5), `netamt` (deci-2), `vendno` (deci-0), `prvendno` (deci-0), `kitfl` (logi) [m], `tallyfl` (logi) [m], `disctype` (logi) [m], `maint-l` (char), `prodtype` (char), `reqprod` (char), `xrefprodty` (char), `crprod` (char), `linefl` (logi) [m], `corechgfl` (logi) [m], `cataddfl` (logi) [m], `pricereset` (logi) [m], `costoverfl` (logi) [m], `kitcostfl` (logi) [m], `stkqtyord` (deci-2), `stkqtyship` (deci-2), `unitconv` (deci-5), `priceover` (deci-5), `calcdatccost` (deci-5), `calcdiscamt` (deci-6), `rebamt` (deci-5), `buildqty` (deci-2), `calcprodcost` (deci-6), `calcpdcost` (deci-6), `idicsp` (reci), `idicsw1` (reci), `idicsw2` (reci), `idoeel` (reci), `speccostty` (char), `csunperstk` (deci-8), `specconv` (inte), `prccostper` (char), `icspecrecno` (inte), `kit-keyfl` (logi) [m], `kit-optfl` (logi) [m], `kit-reqfl` (logi) [m], `returnty` (char), `reasunavty` (char), `crreasonty` (char), `warrtag` (char), `returnfl` (logi) [m], `warrexchgfl` (logi) [m], `qtyunavail` (deci-2), `restockamt` (deci-2), `restockfl` (logi) [m], `warrstagecd` (inte), `retorderno` (inte), `retordersuf` (inte), `retlineno` (inte), `ordertype` (char), `wwhse` (char), `arpwhse` (char), `vawhse` (char), `wshipviaty` (char), `vshipviaty` (char), `mvname` (char), `vaddr` (char[2]), `vcity` (char), `vstate` (char), `vzipcd` (char), `createpofl` (logi) [m], `vfobfl` (logi) [m], `vconfirmfl` (logi) [m], `powtintfl` (logi) [m], `vacreatewtfl` (logi) [m], `orderaltno` (inte), `wcono` (inte), `vvendno` (deci-0), `vshipfmno` (inte), `wduedt` (date), `vduedt` (date), `qtytype` (char), `manprice` (logi) [m], `priceroll` (logi) [m], `promofl` (logi) [m], `pdrecno` (inte), `idpdsc` (reci), `botype` (char), `gststatus` (logi) [m], `jobno` (char), `lostbustyl` (char), `nontaxtype` (char), `slsrepin` (char), `slsrepout` (char), `commtype` (char), `priceclty` (char), `rushfl` (logi) [m], `printpricefl` (logi) [m], `subtotalfl` (logi) [m], `taxablefl` (logi) [m], `usagefl` (logi) [m], `corecharge` (deci-2), `leadtm` (inte), `disccd` (inte), `prodpricecd` (deci-2), `pricelevel` (inte), `taxgroup` (inte), `termspct` (deci-2), `chrgqty` (deci-2), `scrncost` (deci-5), `altwhse` (char), `stkunit` (char), `commentfl` (logi) [m], `totlinefl` (logi) [m], `countfl` (logi) [m], `nosnlots` (deci-2), `nosnlotsk` (deci-2), `wmqtyship` (deci-2), `baseprice` (deci-5), `listprice` (deci-5), `orgbotype` (char), `orgdobotype` (char), `orgcatwtfl` (logi) [m], `orgchrgqty` (deci-2), `orgcorecharge` (deci-2), `orgrestockamt` (deci-2), `orgcubes` (deci-2), `orgdatccost` (deci-5), `orgdiscamt` (deci-5), `orgnetamt` (deci-2), `orgnetord` (deci-2), `orgnosnlots` (deci-2), `orgnosnlotsk` (deci-2), `orgpdrecno` (inte), `orgprice` (deci-5), `orgprod` (char), `orgprodcat` (char), `orgprodcost` (deci-5), `orgspecnstype` (char), `orgstkqtyord` (deci-2), `orgstkqtyship` (deci-2), `orgqtyord` (deci-2), `orgqtyship` (deci-2), `orgrushfl` (logi) [m], `orgtaxablefl` (logi) [m], `orggststatus` (logi) [m], `orgtaxgroup` (inte), `orgtermspct` (deci-2), `orgtotprice` (deci-5), `orgtotqtyord` (deci-2), `orgtotqtyship` (deci-2), `orgunit` (char), `orgunitchg` (char), `orgidicsp` (reci), `orgidicsw1` (reci), `orgidicsw2` (reci), `orgweight` (deci-5), `orgrebamt` (deci-5), `firstmarginwarnfl` (logi) [m], `firstsuperwarnfl` (logi) [m], `filler-1` (char), `filler-2` (char), `filler-3` (char), `filler-4` (char), `filler-5` (char), `filler-6` (char), `reqshipdt` (date), `promisedt` (date), `filler-7` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `oeelrecid` (reci), `oeelrowid` (char), `priceonty` (char), `qtybreakty` (char), `serlottype` (char), `filler-8` (char), `dotype` (char), `dovendno` (deci-0), `doshipfmno` (inte), `doshipviaty` (char), `doduedt` (date), `dofobfl` (logi) [m], `doconfirmfl` (logi) [m], `docono` (inte), `dowhse` (char), `doauth` (logi) [m], `powtnew` (logi) [m], `firsttiewarnfl` (logi) [m], `proddesc2` (char), `launchtallyfl` (logi), `vcspeccostty` (char), `vccsunperstk` (deci-6), `vcspecconv` (inte), `vcprccostper` (char), `vcspecrecno` (inte), `spcconvertfl` (logi) [m], `backorder` (deci-2), `onorder` (deci-2), `delayresrvfl` (logi) [m], `restktaxgrp` (inte), `orgrestktaxgrp` (inte), `bodtransferty` (char), `bodfabwhse` (char), `corertnty` (char), `batchnm` (char) [i], `priceorigcd` (char), `bonoptl` (inte), `kitsplitamt` (deci-2), `ptlkitbofl` (logi) [m], `maxbuildqty` (deci-2), `edilineno` (char), `origcore` (char), `custprod` (char), `vaddr3` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `advertisingcode` (char), `userchr1` (char), `userchr2` (char), `userchr3` (char), `userchr4` (char), `userdec1` (deci-5), `userdec2` (deci-5), `userdt1` (date), `userdt2` (date), `origvano` (inte), `origvasuf` (inte), `nonstkrevfl` (logi) [m], `nonstkaddfl` (logi) [m], `inventoryty` (char), `custcost` (deci-5), `cubes` (deci-2), `cfgkitfl` (logi) [m], `weight` (deci-2), `hardpricefl` (logi) [m], `crinvno` (inte), `crinvsuf` (inte), `taxadjfl` (logi) [m], `contractno` (char), `contrstartdt` (date), `contrenddt` (date), `vendquote` (char), `replcost` (deci-5), `vabaseassembly` (char), `vaassemlgth` (deci-5), `ncnr` (char), `verno` (inte), `vfrtbillacct` (char), `vfrttermscd` (char), `dofrtbillacct` (char), `dofrttermscd` (char), `vtransferloc` (char), `dotransferloc` (char), `eccnclasscd` (char), `countryoforigin` (char), `tariffcd` (char), `origpromisedt` (date), `restrictcd` (char), `idicsprc` (reci), `restrictovrfl` (logi) [m], `restrictovrcom` (char), `hiprcorderno` (inte), `hiprcordersuf` (inte), `hiprclineno` (inte), `overridetype` (char), `hightolprice` (deci-5), `lowtolprice` (deci-5), `custreserverowpointer` (char), `custreserveovrfl` (logi) [m], `custreserveovrpointer` (char), `ehfamt` (deci-5), `ehfexemptamt` (deci-5), `ehfnetamt` (deci-2), `ehfaddonno` (inte), `vendretauth` (char), `npfl` (logi) [m], `pdsnrecno` (inte), `ehfinaddonfl` (logi) [m], `npcd` (char), `taxweight` (deci-5), `upcid` (char), `doduedttz` (datetm-tz), `origpromisedttz` (datetm-tz), `promisedttz` (datetm-tz), `reqshipdttz` (datetm-tz), `vduedttz` (datetm-tz), `wduedttz` (datetm-tz), `shipcompfl` (logi) [m], `confirmctnfl` (logi) [m], `catchweightfl` (logi) [m], `ordrep1` (char), `ordrep2` (char), `ordrep3` (char), `ordrep4` (char), `ordrep5` (char), `orderreppct1` (deci-2), `orderreppct2` (deci-2), `orderreppct3` (deci-2), `orderreppct4` (deci-2), `orderreppct5` (deci-2), `SetID` (char) [i], `Source` (char), `Destination` (char), `CreateDt` (date), `OperInit` (char), `LastSeqNo` (deci-0), `VendType` (char), `PTypeSource` (char), `Line` (char), `ProdPrcTy` (char), `Family` (char), `Class` (char), `RebateTy` (char), `RebSubTy` (char), `RebateCd` (char), `dropshipty` (char), `Cono` (inte) [i], `Description` (char), `RebCalcTy` (char), `RebBasedOn` (char), `RebDownTo` (char), `ProdCat` (char), `Whse` (char), `ShipTo` (char), `CustType` (char), `Prod` (char), `DefPrice` (char), `DefWhse` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `vendno` (deci-0), `RebateCap` (logi) [m], `RebPercent` (deci-5), `RebAmount` (deci-5), `custno` (deci-0), `StartFrom` (date), `StartTo` (date), `EndFrom` (date), `EndTo` (date), `AddCode` (inte), `UpdType` (inte), `DefStart` (date), `defend` (date), `ExcludePDSC` (logi[8]) [m], `delduringupd` (logi) [m], `acctupdfl` (logi) [m], `sortselection` (char), `stagecd` (inte) [m], `reportnm` (char) [m], `contractno` (char), `begprod` (char), `endprod` (char), `prodline` (char), `custrebty` (char), `modifiernm` (char), `modifierrebfl` (logi) [m], `lastuseddt` (date), `begwhse` (char), `endwhse` (char), `begregion` (char), `endregion` (char), `begcustno` (deci-0), `endcustno` (deci-0), `begshipto` (char), `endshipto` (char), `begcusttype` (char), `endcusttype` (char), `begcustrebty` (char), `endcustrebty` (char), `begvendno` (deci-0), `endvendno` (deci-0), `begprodcat` (char), `endprodcat` (char), `begprodline` (char), `endprodline` (char), `begprodprcty` (char), `endprodprcty` (char), `begrebatety` (char), `endrebatety` (char), `begrebsubty` (char), `endrebsubty` (char), `begcontractno` (char), `endcontractno` (char), `sharefl` (logi) [m], `sharepct` (deci-2), `capsellamount` (deci-5), `capselltypefl` (logi) [m], `contractlineno` (inte), `contractcostfl` (logi) [m], `hardpricefl` (logi) [m], `hardmaxqtyfl` (logi) [m], `maxqtytype` (char), `overridepctdown` (deci-2), `overridepctup` (deci-2), `totallines` (inte), `totalerrors` (inte), `totalfatal` (inte), `totalduplicates` (inte), `manualty` (char), `pricerebfl` (logi) [m], `CreateDttz` (datetm-tz), `defendtz` (datetm-tz), `DefStarttz` (datetm-tz), `lastuseddttz` (datetm-tz), `begdivnogroup` (char), `enddivnogroup` (char), `cono` (inte) [i], `custno` (deci-0) [m], `custtype` (char), `whse` (char), `units` (char), `startdt` (date) [i], `enddt` (date) [i], `statustype` (char), `refer` (char), `commtype` (char), `minqty` (deci-2), `maxqty` (deci-2), `actqty` (deci-2), `pround` (char), `qtytype` (char), `ptarget` (inte), `pexactrnd` (deci-2), `operinit` (char), `transdt` (date), `transtm` (char), `qtyyymm` (char), `prod` (char) [m], `pdrecno` (inte), `disctype` (char), `prcdisc` (deci-3[9]), `prodcat` (char), `prcmult` (deci-5[9]), `quotefl` (logi) [m], `qtybrk` (inte[8]), `promofl` (logi) [m], `qtybreakty` (char), `quoteno` (char), `jobno` (char), `prodcost` (deci-5), `termsdiscfl` (logi) [m], `termspct` (deci-2), `user1` (char), `rebatecd` (char), `user2` (char), `pricety` (char), `priceonty` (char), `rebcalcty` (char), `vendquote` (char), `PriceSheetTo` (char), `ContractNo` (char), `PriceSheet` (char), `PriceEffectiveDateTo` (date), `PriceEffectiveDate` (date), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `pd_rowid` (char), `touchedfl` (logi) [m], `BatchNm` (char), `line_rowid` (char), `SetID` (char) [i], `SeqNo` (deci-0) [i], `arptype` (char), `arppushfl` (logi) [m], `prodline` (char), `famgrptype` (char), `vendprod` (char), `class` (inte), `avgcost` (deci-5), `replcost` (deci-5), `lastcost` (deci-5), `stndcost` (deci-5), `addoncost` (deci-2), `arpwhse` (char), `listprice` (deci-5), `taxprice` (deci-5), `rebateamt` (deci-5), `rebatety` (char), `rebatepct` (deci-5), `rebsubty` (char), `rebdowntoty` (char), `rebatecost` (deci-5), `margincostty` (char), `baseprice` (deci-5), `vendno` (deci-0), `Origwhse` (char), `OrigCust` (deci-0), `OrigStartDt` (date), `Typecode` (char), `prctype` (logi) [m], `prodprcty` (char), `levelcd` (char), `source` (char), `transproc` (char), `dropshipty` (char), `rebatecostty` (char), `caprebfl` (logi), `rebrecno` (deci-0), `custrebty` (char), `levelkey` (char) [m], `modified` (logi) [m], `buytype` (char), `vendorprice` (deci-2), `vendnotesfl` (char), `custnotesfl` (char), `prodnotesfl` (char), `shiptonotesfl` (char), `filter1` (char) [im], `filter2` (char) [im], `filter3` (char) [im], `filter4` (char) [im], `filter5` (char) [im], `filter6` (char) [im], `filter7` (char) [im], `sortkey` (char) [im], `updttype` (logi) [im], `primarykey` (char) [i], `xrefprod` (char), `proddesc` (char), `proddesc2` (char), `prcdisc2` (deci-3[9]), `prcdisc3` (deci-3[9]), `prcdisc4` (deci-3[9]), `prcdisc5` (deci-3[9]), `prcdisc6` (deci-3[9]), `chainedfl` (logi) [m], `shipfmno` (inte), `cdlink` (char), `modifiernm` (char), `modifierrebfl` (logi) [m], `hardmaxqtyfl` (logi) [m], `maxqtytype` (char), `hardpricefl` (logi) [m], `contractcostfl` (logi) [m], `lastuseddt` (date), `ovrridepctup` (deci-2), `ovrridepctdown` (deci-2), `costmult` (deci-5), `costtype` (logi) [m], `costbasedon` (char), `shipto` (char), `sharefl` (logi) [m], `sharepct` (deci-2), `capsellamount` (deci-2), `capselltypefl` (logi) [m], `contractlineno` (inte), `region` (char), `errormsg` (char), `usecontractlineno` (logi) [m], `manualfl` (logi) [m], `price` (deci-5), `prccurrencyty` (char), `usepricerebfl` (logi) [m], `lastuseddttz` (datetm-tz), `pricecostty` (char), `divnogroup` (char), `Source` (char) [i], `Destination` (char) [i], `pages` (char), `required` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `baseprice` (deci-5), `cono` (inte) [i], `effectivedt` (date) [i], `listprice` (deci-5), `custmatrix` (deci-5[9]), `version` (char), `prod` (char) [im], `rebatecost` (deci-5), `replcost` (deci-5), `pricesheet` (char) [i], `stndcost` (deci-5), `vendmatrix` (deci-5[9]), `whse` (char) [i], `zone` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `slchgdt` (date), `effectivedttz` (datetm-tz), `slchgdttz` (datetm-tz), `rowpointer` (char) [i], `baseprice` (deci-5), `cono` (inte) [im], `effectivedt` (date) [i], `listprice` (deci-5), `custmatrix` (deci-5[9]), `version` (char), `prod` (char) [im], `rebatecost` (deci-5), `replcost` (deci-5), `pricesheet` (char) [im], `stndcost` (deci-5), `vendmatrix` (deci-5[9]), `whse` (char) [im], `zone` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `slchgdt` (date), `effectivedttz` (datetm-tz), `slchgdttz` (datetm-tz), `rowpointer` (char) [i], `unit` (char) [im], `cono` (inte) [i], `pono` (inte) [i], `posuf` (inte) [i], `lineno` (inte) [i], `filler-1` (char), `orgcatwtfl` (logi) [m], `orgcubes` (deci-5), `orgnetamt` (deci-2), `orgnonstockty` (char), `orgnosnlots` (deci-2), `orgprod` (char), `orgprice` (deci-5), `orgsqtyord` (deci-2), `orgstkqtyord` (deci-2), `orgqtyord` (deci-2), `orgqtyrcv` (deci-2), `orgunit` (char), `orgidicsp` (reci), `orgidicsw` (reci), `orgweight` (deci-5), `filler-2` (char), `cubes` (deci-5), `duedt` (date), `nonstockty` (char), `prod` (char), `scrnprice` (deci-5), `prodcat` (char), `proddesc` (char), `qtyord` (deci-2), `stkqtyord` (deci-2), `unit` (char), `weight` (deci-5), `reasunavty` (char), `filler-3` (char), `commentfl` (logi) [m], `unitconv` (deci-5), `idpoel` (reci), `idicsp` (reci), `idicsw` (reci), `linefl` (logi) [m], `maint-l` (char), `nosnlots` (deci-2), `priceover` (deci-5), `filler-4` (char), `speccostty` (char), `csunperstk` (deci-8), `specconv` (inte), `prccostper` (char), `icspecrecno` (inte), `serlottype` (char), `netavail` (deci-2), `proddesc1` (char), `netamt` (deci-2), `proddesc2` (char), `calcprice` (deci-5), `poelrecid` (reci), `manprice` (logi) [m], `poelrowid` (char), `stkunit` (char), `tallyfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `orgreasunavty` (char), `expshipdt` (date), `reqshipdt` (date), `launchtallyfl` (logi), `backorder` (deci-2), `onorder` (deci-2), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `userchr1` (char), `userchr2` (char), `userchr3` (char), `userchr4` (char), `userdec1` (deci-5), `userdec2` (deci-5), `userdt1` (date), `userdt2` (date), `contractno` (char) [m], `pdsvcrecno` (inte), `orgpdsvcrecno` (inte), `ackdt` (date), `ackrsn` (char), `ncnr` (char), `countryoforigin` (char), `tariffcd` (char), `vendretauth` (char), `upcid` (char), `ackdttz` (datetm-tz), `duedttz` (datetm-tz), `expshipdttz` (datetm-tz), `reqshipdttz` (datetm-tz), `suppwarrallowpct` (deci-5), `suppwarrallownet` (deci-2), `catchweightfl` (logi) [m], `cono` (inte) [i], `oper2` (char) [i], `functionname` (char) [i], `jrnlno` (inte) [i], `recoverydata` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `cono` (inte) [i], `functionname` (char) [i], `primarykey` (char) [im], `enterdt` (date) [im], `entertm` (char) [im], `secondarykey` (char) [i], `operinit` (char), `fieldchanged` (char), `oldvalue` (char), `newvalue` (char), `reason` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `enterdttz` (datetm-tz), `queue_name` (char) [i], `RptsProcessed` (inte), `transtm` (char), `queue_status` (char), `queue_no` (inte) [i], `StartDt` (date), `StartTm` (inte), `LastRptStartDt` (date), `LastRptStartTm` (inte), `LastRptName` (char), `Daily_Stop_Time` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transproc` (char), `PID` (inte) [m], `patch-level` (char[10]), `file-name` (char[10]), `file-create-date` (date[10]), `file-create-time` (inte[10]), `file-mod-date` (date[10]), `file-mod-time` (inte[10]), `full-pathname` (char[10]), `pathname` (char[10]), `file-size` (inte[10]), `file-type` (char[10]), `parameters` (char), `startup-propath` (char), `queue_name` (char) [i], `RunningFl` (logi) [m], `Description` (char), `queue_status` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `user1` (char), `user2` (char), `demand_only` (logi) [m], `operinit` (char), `transdt` (date), `transtm` (char), `LastRptStartDt` (date), `LastRptStartTm` (inte), `LastRptName` (char), `Daily_Stop_Time` (inte), `transproc` (char), `FunctionName` (char) [i], `FolderLabels` (char), `FolderFunctionNames` (char), `FolderViewerName` (char), `KeyViewer` (char), `BrowseName` (char), `WindowTitle` (char), `FunctionProcedure` (char), `FolderDelimiter` (char), `MenuSet` (char) [i], `ParentMenu` (char), `ParentPos` (inte), `menutitle` (char), `buttontitle` (char), `tiptext` (char), `recordtype` (char) [i], `FunctionDirectory` (char), `FolderFunctionType` (char), `OtherLinks` (char), `CanExecute` (logi) [m], `FolderInstructions` (char), `Nxtrend_ourproc` (char), `Min_Security_Level` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `CRMSubject` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `trmgrlang` (char) [i], `standardty` (char), `type_code` (char) [i], `Name` (char), `Key_Label` (char), `Browse_Label` (char), `Proc_Label` (char), `Run_Name` (char), `Param_Flag` (logi) [m], `type_dialog` (char), `origin` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `Browse_Label_ReqFL` (logi), `standardty` (char), `Key_Label_ReqFL` (logi), `Proc_Label_ReqFL` (logi), `cono` (inte) [i], `operinit` (char), `FunctionName` (char) [i], `FolderSecurity` (char), `FolderDelimiter` (char), `FunctionSecurity` (inte), `oper2` (char) [i], `transdt` (date), `transtm` (char), `MenuSet` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `origname` (char), `cono` (inte) [i], `oper2` (char) [i], `prod` (char) [i], `dsplprod` (char) [i], `addswoptprodfl` (logi) [m], `chrg` (char), `cubes` (deci-5), `descrip` (char), `descrip2` (char), `icspecrecno` (inte), `speccostty` (char), `csunperstk` (deci-8), `prccostper` (char), `discamt` (deci-5), `discoverfl` (logi) [m], `disctype` (logi) [m], `extra-1` (char), `extra-2` (char), `keyindex` (char) [i], `lastpurdt` (date), `lastprice` (deci-5), `lookupnm` (char), `marginamt` (deci-5), `marginpct` (deci-2), `netord` (deci-2), `netrecommend` (deci-2), `notesfl` (char), `pdrecno` (inte), `pdsvfl` (logi) [m], `arpprodline` (char), `price` (deci-5), `priceoverfl` (logi) [m], `prodcat` (char), `prodcost` (deci-5), `qtyavail` (deci-2), `qtybreakty` (char), `qtyord` (deci-2), `qtyrecommend` (deci-2), `seasontype` (char), `specnstype` (char), `specconv` (deci), `statmessage` (char), `stkqtyord` (deci-2), `stkqtyrecommend` (deci-2), `totalstkqty` (deci-2), `unit` (char), `unitconv` (deci-5), `weight` (deci-5), `whse` (char), `seqno` (inte) [i], `optionalwords` (char), `arpvendno` (deci-0), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `contractno` (char), `pdsvcrecno` (inte), `dsplqtyavail` (char), `cono` (inte) [i], `repairordno` (inte) [i], `repairordsuf` (inte) [i], `price` (deci-5), `warrantycd` (char), `invclaimcd` (char), `srtqty` (deci-2), `srtoverfl` (logi) [m], `damagecd` (char), `orderno` (inte) [i], `ordersuf` (inte) [i], `prodcat` (char), `prodline` (char), `specnstype` (char), `vendno` (deci-0), `vvendno` (deci-0), `orgprod` (char), `orgprodcat` (char), `orgprodcost` (deci-5), `orgspecnstype` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `maint-l` (char), `swlnno` (inte), `workperfdt` (date), `lineno` (inte) [i], `orgprice` (deci-5), `orgprodline` (char), `prodcost` (deci-5), `srtfl` (logi) [m], `srthrs` (deci-2), `swertrecid` (reci), `swertrowid` (char), `swpriceoverfl` (logi) [m], `typecd` (char), `unit` (char), `orgvendno` (deci-0), `orgvvendno` (deci-0), `orgtypecd` (char), `orgvendnosw` (deci-0), `orgwarrantycd` (char), `prod` (char), `vendnosw` (deci-0), `userchr1` (char), `userchr2` (char), `userchr3` (char), `userchr4` (char), `userdec1` (deci-5), `userdec2` (deci-5), `userdt1` (date), `userdt2` (date), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `printpricefl` (logi) [m], `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `xxc3` (char), `xxc4` (char), `selldt` (date), `faildt` (date), `vendno` (deci-0) [i], `repairordno` (inte), `vendclaimno` (char), `claimstage` (inte), `disputefl` (logi) [m], `totclaimamt` (deci-2), `totcreditamt` (deci-2), `printdt` (date), `vendname` (char), `vendaddr` (char[2]), `vendcity` (char), `vendstate` (char), `vendzipcd` (char), `name` (char), `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `recjrnlno` (inte) [i], `subjrnlno` (inte), `orderno` (inte), `ordersuf` (inte), `repairordsuf` (inte), `prod` (char), `serialno` (char), `lotno` (char), `bulletinno` (char), `createdt` (date), `intclaimno` (inte) [i], `prodcat` (char), `failcd` (char), `probfailcd` (char), `qty` (deci-2), `custno` (deci-0), `subsetno` (inte), `recsetno` (inte), `equiptype` (char), `authservno` (char), `woamt` (deci-2), `whse` (char), `claimtype` (char), `manualfl` (logi) [m], `notesfl` (char), `problemtxt` (char), `causetxt` (char), `workperftxt` (char), `textfl` (logi) [m], `printcnt` (inte), `printfl` (logi) [m], `resubamt` (deci-2), `transproc` (char), `intclaimnox` (char), `transtype` (char), `enterdt` (date), `duedt` (date), `printeddt` (date), `vendnox` (char), `vendNotes` (char), `custNotes` (char), `custname` (char), `proddesc` (char[2]), `prodNotes` (char), `batchdatfl` (logi) [m], `statusinfo` (char), `sortfld` (char), `amounti` (inte), `pstatusfl` (char), `swsuf` (inte) [i], `glamount` (deci-2), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `addr3` (char), `vendaddr3` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `userchr1` (char), `userchr2` (char), `userchr3` (char), `userchr4` (char), `userdec1` (deci-5), `userdec2` (deci-5), `userdt1` (date), `userdt2` (date), `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `proddesc2` (char), `proddesc` (char), `lineno` (inte) [i], `claimamt` (deci-5), `creditamt` (deci-5), `linecomment` (char), `printcommentfl` (logi) [m], `qty` (deci-2), `extclaimamt` (deci-2), `prod` (char) [i], `intclaimno` (inte) [i], `extcramt` (deci-2), `srtqty` (deci-2), `srtoverfl` (logi) [m], `damagecd` (char), `unitconv` (deci-5), `icspecrecno` (inte), `origclaimno` (inte), `subjrnlno` (inte), `subsetno` (inte), `resubamt` (deci-2), `transproc` (char), `recjrnlno` (inte) [i], `origamt` (deci-5), `resubqty` (deci-2), `totresubamt` (deci-2), `prodnotes` (char), `swewlrecid` (reci), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `userchr1` (char), `userchr2` (char), `userchr3` (char), `userchr4` (char), `userdec1` (deci-5), `userdec2` (deci-5), `userdt1` (date), `userdt2` (date), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `proddesc2` (char), `proddesc` (char), `lineno` (inte) [i], `claimamt` (deci-5), `creditamt` (deci-5), `linecomment` (char), `printcommentfl` (logi) [m], `qty` (deci-2), `extclaimamt` (deci-2), `prod` (char), `intclaimno` (inte) [i], `extcramt` (deci-2), `srtqty` (deci-2), `srtoverfl` (logi) [m], `damagecd` (char), `unitconv` (deci-5), `icspecrecno` (inte), `origclaimno` (inte), `subjrnlno` (inte), `subsetno` (inte), `resubamt` (deci-2), `transproc` (char), `maint-l` (char), `swewlrecid` (reci), `swewlrowid` (char), `csunperstk` (deci-6), `specconv` (inte), `prccostper` (char), `netamt` (deci-2), `speccostty` (char), `cono` (inte) [i], `orgprod` (char), `orgclaimamt` (deci-5), `totclaimamt` (deci-5), `userchr1` (char), `userchr2` (char), `userchr3` (char), `userchr4` (char), `userdec1` (deci-5), `userdec2` (deci-5), `userdt1` (date), `userdt2` (date), `_Userid` (char) [i], `ProfileName` (char), `ArrangeCols` (logi) [m], `AddFavorites` (logi) [m], `EntryLayout` (logi) [m], `NavLayout` (logi) [m], `ToolbarLayout` (logi) [m], `ChangeProfiles` (logi) [m], `ChangeAppServer` (logi) [m], `AutoJournalClose` (logi) [m], `addr` (char[2]), `UnlimitedWebAccess` (logi) [m], `LoginSource` (char), `city` (char), `state` (char), `_Password` (char), `_User-Name` (char) [i], `zipcd` (char), `cono` (inte) [im], `operinit` (char), `Disabled` (logi) [m], `MustChange` (logi) [m], `CannotChange` (logi) [m], `oper2` (char) [i], `homeph` (char), `workph` (char), `cellph` (char), `faxph` (char), `Dept` (char), `JobTitle` (char), `transdt` (date), `email` (char), `pagerph` (char), `transtm` (char), `maxwindows` (inte), `MaxUsers` (inte), `MenuSet` (char), `AOSecurity` (char), `seccredmgrfl` (logi) [m], `queue-s` (char), `queue-d` (char), `queuefl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `updategltrans` (logi) [m], `updateaptrans` (logi) [m], `updateartrans` (logi) [m], `ActivityOtherOperFl` (logi) [m], `CreditCardDisplayFl` (logi) [m], `ActivitySecrLev` (inte), `ContactMgmntSecrLev` (inte), `CRMUserType` (char), `apeitradefl` (logi) [m], `apeiexpensefl` (logi) [m], `apeiaddonfl` (logi) [m], `apeiusecostfl` (logi) [m], `apeiovertolfl` (logi) [m], `starttoolbar` (char), `addr3` (char), `etsecurity` (char), `profileuserset` (logi) [m], `webprofilename` (char), `websettingaccesslevel` (char), `webmodificationaccesslevel` (char), `twlwhse` (char), `twlrestrictwhsefl` (logi) [m], `twllastuseddt` (date), `sessionid` (char) [i], `webextensiontype` (char), `rowpointer` (char) [i], `dropboxauthkey` (char), `transdttmz` (datetm-tz) [i], `oereassignarfl` (logi) [m], `divnorestrictapfl` (logi) [m], `divnorestrictarfl` (logi) [m], `divnorestrictcrfl` (logi) [m], `divnorestrictglfl` (logi) [m], `divnorestricticfl` (logi) [m], `divnorestrictoefl` (logi) [m], `divnorestrictpofl` (logi) [m], `divnorestrictwtfl` (logi) [m], `divnorestrictwtallfl` (logi) [m], `divnoallowlist` (char), `restricteditarfl` (logi) [m], `restricteditapfl` (logi) [m], `twllastuseddttz` (datetm-tz), `clienttzoffset` (char), `reqdraweridfl` (logi) [m], `lastdrawerid` (char), `divnogroup` (char) [i], `pdrestrictty` (inte), `nsfoverfl` (logi) [m], `allowactivategiftfl` (logi) [m], `allowbalancegiftfl` (logi) [m], `ohallowlist` (char), `tablename` (char) [i], `fieldname` (char) [i], `transdt` (date), `userlabel` (char), `transtm` (char), `userinuse` (logi) [m], `operinit` (char), `usercando` (char), `usermin` (inte), `usermax` (inte), `userdatemin` (date), `userdatemax` (date), `userhelp` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `userdatemaxtz` (datetm-tz), `userdatemintz` (datetm-tz), `wtno` (inte) [i], `wtsuf` (inte) [i], `lineno` (inte) [i], `filler-1` (char), `filler-2` (char), `cubes` (deci-5), `duedt` (date), `nonstockty` (char), `prod` (char), `prodcati` (char), `proddesc` (char), `qtyord` (deci-2), `stkqtyord` (deci-2), `unit` (char), `weight` (deci-5), `filler-3` (char), `commentfl` (logi) [m], `unitconv` (deci-5), `idwtel` (reci), `idicsp` (reci), `idicsw` (reci), `linefl` (logi) [m], `maint-l` (char), `nosnlots` (deci-2), `filler-4` (char), `speccostty` (char), `csunperstk` (deci-8), `specconv` (inte), `prccostper` (char), `icspecrecno` (inte), `serlottype` (char), `netavail` (deci-2), `proddesc1` (char), `netamt` (deci-2), `proddesc2` (char), `wtelrecid` (reci), `wtelrowid` (char), `stkunit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `prodinrcvfl` (logi) [m], `prodcost` (deci-5), `approvety` (char), `usagefl` (logi) [m], `bofl` (logi) [m], `ordertype` (char), `orderaltno` (inte), `stkqtyship` (deci-2), `qtyship` (deci-2), `vendno` (deci-0), `prodline` (char), `prodcato` (char), `arpwhse` (char), `reqprod` (char), `xrefprodty` (char), `orgweight` (deci-5), `orgcubes` (deci-5), `orgnetamt` (deci-2), `orgcatwtfl` (logi) [m], `orgnetord` (deci-2), `orgnosnlots` (deci-2), `orgnonstockty` (char), `orgprod` (char), `orgstkqtyord` (deci-2), `orgunit` (char), `orgidicsp` (reci), `orgidicsw` (reci), `orgidicsp2` (reci), `orgidicsw2` (reci), `orgprodcati` (char), `orgprodcato` (char), `orgqtyord` (deci-2), `orgprodcost` (deci-5), `orgstkqtyship` (deci-2), `orgqtyship` (deci-2), `orgtotqtyship` (deci-2), `orgtotqtyord` (deci-2), `idicsp2` (reci), `idicsw2` (reci), `orgapprovety` (char), `orgbofl` (logi) [m], `orgunitchg` (char), `crprod` (char), `firstsuperwarnfl` (logi), `reasunavty` (char), `qtyunavail` (deci-2), `delayresrvfl` (logi) [m], `userchr1` (char), `userchr2` (char), `userchr3` (char), `userchr4` (char), `userdec1` (deci-5), `userdec2` (deci-5), `userdt1` (date), `userdt2` (date), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `addonamt` (deci-2), `addonmarkuptype` (char), `addonmarkupcost` (deci-5), `addonpct` (deci-2), `addontype` (char), `orgaddonamt` (deci-2), `duedttz` (datetm-tz), `confirmctnfl` (logi) [m], `type` (char) [im], `tablename` (char) [im], `srcrowpointer` (char) [im], `keyfield` (char), `transdttmz` (datetm-tz) [i], `cono` (inte) [i], `synctype` (char) [i], `tablenm` (char) [i], `key1` (char) [i], `key2` (char) [i], `key3` (char) [i], `updatetype` (char) [i], `statustype` (char) [i], `newrecordfl` (logi) [m], `updatetm` (char) [i], `updatedt` (date) [i], `prevkey1` (char), `prevkey2` (char), `prevkey3` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `extradata` (char), `prevextradata` (char), `GroupID` (char) [im], `CodeID` (char) [im], `CodeVal1` (char) [i], `CodeVal2` (char) [i], `CodeVal3` (char), `SrcDB` (char) [m], `SrcTable` (char) [m], `CustName` (char) [m], `CustDefType` (char) [m], `CustMisc` (char) [m], `SrcDB` (char) [m], `SrcTable` (char) [m], `FldName` (char) [m], `FldDataType` (char) [m], `FldWidth` (inte), `FldDec` (inte), `FldMand` (logi), `SrcDB` (char) [im], `SchHldr` (char) [m], `SchImg` (char) [m], `TgtType` (char) [im], `TgtConnName` (char) [m], `TgtPhysName` (char), `GenQRec` (logi) [m], `ProcQRec` (logi) [m], `SrcPhysName` (char), `SchPhysName` (char), `SrcDB` (char) [im], `SrcTable` (char) [im], `SrcField` (char) [im], `SrcDataType` (char) [m], `SrcOrder` (inte) [i], `SchField` (char) [m], `SchDataType` (char), `TgtField` (char) [m], `TgtDataType` (char) [m], `TgtPrec` (inte), `TgtScale` (inte), `SrcExtent` (inte), `TgtExtent` (inte), `OverrideDefs` (logi), `tablenm` (char) [i], `newrecord` (raw), `oldrecord` (raw), `createdt` (date), `createtm` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `dumpnm` (char), `PropertyName` (char) [im], `PropertyValue` (char) [m], `Sequence` (int6) [i], `EventType` (char) [m], `SrcDB` (char) [m], `SrcTable` (char) [im], `SrcRecord` (char) [im], `EventDate` (date) [m], `EventTime` (char) [m], `SrcTransID` (inte), `Username` (char), `Applied` (logi) [im], `ApplDate` (date), `ApplTime` (char), `Audited` (logi) [i], `AudDate` (date), `AudTime` (char), `UserCust` (char), `RawData` (raw), `QThread` (inte) [im], `SrcDB` (char) [im], `SrcTable` (char) [im], `SchTable` (char), `TgtTable` (char) [m], `GenQRec` (logi) [m], `ProcQRec` (logi) [m], `QThread` (inte) [im], `UseInDiff` (logi) [im], `TrigInst` (logi) [m], `MrgdTrig` (logi), `OrigDTrigProc` (char), `OrigWTrigProc` (char), `co_num` (char) [im], `wh_num` (char) [im], `rtn_category` (char) [i], `description` (char), `row_status` (logi) [m], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `type` (char) [im], `code` (char) [im], `description` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `ptxqueue`
**PTX Queue**

### `ptxqueuedet`
**PTX Queue Detail**

### `ptxrouterule`
**PTX Routing rules**

### `ptxrouting`
**PTX Routing rules**

### `ptxsamsg`
**PTX System Administrator Setup System Messages**

### `ptxtransaddon`
**Exchange Transaction Addon**

### `ptxtransaddr`
**Exchange Transaction Address**

### `ptxtranshdr`
**Exchange Transaction Header**

### `ptxtransln`
**Exchange Transaction Lines**

### `ptxtransnotes`
**Exchange Transaction Notes/Comments**

### `pv_adminlog`

### `pv_adminnotes`

### `pv_apeba`
**AP Batch Addons**

### `pv_apebc`
**AP Batch Costing**

### `pv_attachments`

### `pv_exratelog`
**Exchange Rate Log**

### `pv_images`
**SX.enterprise Image Table**

### `pv_jmln`
**JM line item creation storage table**

### `pv_oeln`
**OE line item creation storage table**

### `pv_pdmhdr`

### `pv_pdmline`

### `pv_pdmmatrix`
**Contains references to sources and destinations for pd maintenance.**

### `pv_pdsps`

### `pv_pdspsu`

### `pv_poln`
**PO line item creation storage table**

### `pv_recovery`
**Powervue recovery table**

### `pv_samb`

### `pv_sapbm`

### `pv_sapbq`

### `pv_sassm`
**SX Enterprise GUI Menu Function Setup**

### `pv_sassm_types`
**A list of the type of container records defined**

### `pv_secure`
**Security settings to match pv_sassm**

### `pv_shoplist`
**Product Shopping List**

### `pv_sroln`
**SW part/labor line item creation storage table**

### `pv_swewh`
**Header Table for processing of SW claims**

### `pv_swewl`
**Line detail Table for processing of SW claims**

### `pv_swln`
**Service Warranty Enter Warranty Claim Detail Line**

### `pv_user`
**SX Enterprise GUI Operator Setup**
**Operators call this:** "Created By" (Accounts Payable), "Created By Code" (Accounts Payable), "Created By Name" (Accounts Payable), "Buyer Code" (Purchasing), "Buyer Name" (Purchasing), "Taken By Code" (Sales), "Taken By Name" (Sales), "Entered/Approved By Code" (Warehouse Transfers), "Entered/Approved By Name" (Warehouse Transfers)

### `pv_userfields`
**user field settings for all user fields on all tables**

### `pv_wtln`
**WT line item creation storage table**

### `pvcontainers`
**Navigation Containers**

### `pvobjects`
**Navigation objects**

### `pvregistry`
**Holds all persistent settings for users**

### `pvsassmattr`
**PV SASSM Attributes**

### `pvsassmlink`
**PV Sassm Links**

### `pvsassmobj`
**PV SASSM Objects**

### `recorddelete`
**Record Deletions**

### `recordsync`
**Record Syncchronization Table**

### `replcontrol`

### `replcustdefs`

### `replcustflds`
**Custom Fields for the SQL Schema - can be global or table specific**

### `repldbxref`

### `replfieldxref`
**Cross-Reference Table containing names and datatypes of source DB Tables and Fields, and their associated replication counterparts**

### `replicte`
**Replication Trigger Log**

### `replproperties`

### `replqueue`

### `repltablexref`

### `return_categor`
**Holds the valid return categories**

### `return_reason`
**Holds information about return reason codes**

### `rptdet`
**Report Detail Information**
Fields: `co_num` (char) [i], `wh_num` (char) [im], `reportid` (inte) [i], `reportname` (char) [i], `reporttypeid` (char) [i], `reportlocation` (char), `filterscreen` (char), `rowstatus` (logi), `description` (char), `reportrule` (char), `tablename` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `rptmst`
**Report types and type information**
Fields: `reporttype` (char), `reporttypeid` (char) [i], `graphic` (char), `description` (char), `rowstatus` (logi), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `rsad`
**Queue Defaults for Trend Reports**
Fields: `queuenm` (char) [i], `procmatch` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `rsao`
**Report Scheduler Administrative Options**
Fields: `maxsysjobs` (inte[24]), `logfl` (logi) [m], `rngoptfl` (logi) [m], `logdir` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `interval` (inte), `activefl` (logi) [m], `rsoper` (char) [i], `rspasswd` (char), `rspid` (inte) [m], `timeout` (inte), `sessionid` (char), `lastrdcleandt` (date), `rowpointer` (char), `pausefl` (logi) [m]

### `rses`
**Scheduled Reports, Job Groups**
Fields: `inusety` (char) [i], `jobnm` (char) [i], `pidno` (inte), `startdt` (date) [i], `starttm` (inte) [i], `startty` (char), `queuenm` (char) [i], `schedpri` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte), `reportfl` (logi) [m], `printernm` (char), `seqno` (inte) [i], `transproc` (char), `dbconnectid` (int6), `dbconnectusr` (inte), `dbconnectdevice` (char), `dbconnecttime` (char), `dbconnecttenant` (inte), `dbcancelpid` (inte), `dbcancelid` (int6), `dbcancelusr` (inte), `dbcanceldevice` (char), `dbcanceltime` (char), `dbcanceltenant` (inte), `dbconnectname` (char), `dbcancelname` (char), `clienttzoffset` (inte)

### `rssj`
**Job Group Header File**
Fields: `groupnm` (char) [i], `jobdesc` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `startdt` (date), `starttm` (inte), `starttype` (char), `runty` (char), `interval` (inte), `lastrundt` (date), `lastruntm` (char), `transproc` (char), `jobstarttm` (inte)

### `rssjc`
**Job Setup Task File (detail component of rssj)**
Fields: `cono` (inte) [i], `groupnm` (char) [i], `componentnm` (char) [i], `reportfl` (logi) [m], `posno` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `priority` (inte) [i], `inusety` (char) [i], `pidno` (inte), `transproc` (char)

### `rssq`
**Queue Setup File**
Fields: `queuenm` (char) [i], `statustype` (logi) [im], `nomaxjobs` (inte), `queuepri` (inte) [i], `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `begintm` (inte), `endtm` (inte), `descrip` (char), `operinit` (char), `logdir` (char), `rngoptfl` (logi) [m], `transproc` (char)

### `rt_type`
**C = corporate PO, D = departmental order, R = customer return, T = warehouse transfer**

### `rtdet`
**Receipt transaction detail**
Fields: `rt_id` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `line_num` (inte) [i], `vendor_id` (char) [i], `abs_num` (char) [im], `item_num` (char) [im], `vend_item` (char) [m], `quantity` (deci-2), `act_quantity` (deci-2), `exp_quantity` (deci-2), `ordered_qty` (deci-2), `bo_count` (inte), `bo_quantity` (deci-2), `special_handling` (char), `item_cost` (deci-2), `uom` (char), `lot` (char), `comments` (char), `item_desc` (char) [i], `po_number` (char) [i], `po_suffix` (char) [i], `po_type` (char), `po_line` (inte) [i], `line_sequence` (inte) [i], `asn_flag` (logi) [m], `packer` (char), `delivery` (date), `rtn_order` (char) [m], `rtn_order_suffix` (char), `ret_line` (inte) [m], `ret_line_sequence` (inte), `return_fl` (char), `qty_unavail` (deci-2), `rd_po_type` (char), `line_indicator` (char), `receiver_num` (char), `prod_desc` (char), `packing_list` (logi) [m], `percent_fill` (deci-2), `custom_data` (char[5]), `row_status` (char) [im], `stock_stat` (char), `case_quantity` (deci-4), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `deliverytz` (datetm-tz), `trans_datetz` (datetm-tz), `code` (char) [im], `name` (char) [im], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `rtdet_status`
**All the statuses allowed for the rtdet table**

### `rtmst`
**R/Ts are receipt transactions - Purchase Orders are one type of receipt transaction**
Fields: `rt_id` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `rt_num` (char) [im], `task_id` (inte), `type` (char) [im], `vendor_id` (char), `comments` (char), `delivery` (date) [i], `order` (char) [i], `order_suffix` (char) [i], `packing_list` (logi) [m], `truck_id` (char), `carrier` (char), `clearance_code` (char) [i], `cargo_control` (char) [i], `clearance_required` (logi) [i], `release_id` (char) [i], `unplanned` (logi), `created_by` (char), `num_cartons` (inte), `percent_fill` (deci-2), `custom_data` (char[5]), `row_status` (char) [im], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `deliverytz` (datetm-tz), `trans_datetz` (datetm-tz), `code` (char) [im], `name` (char) [im], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `carton_num` (inte) [im], `abs_num` (char) [im], `lot` (char), `qty` (deci-2), `uom` (char), `custom_data` (char[5]), `row_status` (char) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `carton_num` (inte) [im], `co_num` (char) [im], `wh_num` (char) [im], `carton_id` (char) [i], `rtn_category` (char) [i], `custom_data` (char[5]), `row_status` (char) [i], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `code` (char) [im], `name` (char) [im], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `rtmst_status`
**All the status codes allowed for the rtmst table**

### `rtn_ctn_det`
**Returns cartons (detail)**

### `rtn_ctn_mst`
**Return cartons (master)**

### `sabgl`
**General Ledger Batch Setup Additional information**
Fields: `cono` (inte) [i], `batchnm` (char) [i], `holdpostings` (inte), `holddr` (deci-2), `holdcr` (deci-2), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `exchgrate` (deci-7), `currencyty` (char)

### `sabs`
**System Administrator Batch Header**
Fields: `cono` (inte) [i], `batchnm` (char) [i], `modulenm` (char), `freqtype` (char), `descrip` (char), `securinit` (char), `proofdr` (deci-2), `proofcr` (deci-2), `createdt` (date), `createinit` (char), `lastmtdt` (date), `lastmtinit` (char), `lastupdt` (date), `lastupinit` (char), `transdt` (date), `transtm` (char), `operinit` (char), `inuseby` (char), `totdr` (deci-2), `totcr` (deci-2), `nopostings` (inte), `statustype` (logi) [m], `jrnlno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `groupseqno` (inte), `sequencedt` (date), `wordindexfl` (logi) [m], `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `createdttz` (datetm-tz), `lastmtdttz` (datetm-tz), `lastupdttz` (datetm-tz), `sequencedttz` (datetm-tz), `divno` (inte), `runid` (inte) [im], `record_type` (char) [im], `record_value` (char) [im], `pid` (inte) [i], `state` (char), `start_tm` (int6), `lastupt_tm` (int6) [m], `tot_records` (int6), `curr_records` (int6), `uimessage` (char), `hostname` (char), `ipaddress` (char), `cono` (inte) [i], `prod` (char) [i], `crossref` (char) [i], `xtype` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [i], `xtype` (char) [i], `crossref` (char) [i], `totrecords` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `sadataload`
**SA Table for tracking data loads**

### `saindex`
**Index Cross References for ARSC, ICSP, CMSP**

### `sakeytot`
**Keyword summary total records for saindex performance**

### `sals`
**Language Cross Reference Setup**
Fields: `cono` (inte) [i], `langcd` (char) [i], `codeiden` (char) [im], `codeval` (char) [im], `descrip` (char[2]), `operinit` (char), `transdt` (date), `transtm` (char), `editpcd` (char), `edidtcd` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `descrip3` (char), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `sapb`
**SA Parameter Collection**
Fields: `currproc` (char) [i], `rpttitle` (char), `printernm` (char), `rangecnt` (inte), `optioncnt` (inte), `startdta` (char), `startdtt` (date), `faxtag1` (char), `printoptfl` (logi) [m], `faxtag2` (char), `reportnm` (char) [i], `starttype` (char), `operinit` (char), `transdt` (date), `transtm` (char), `demandfl` (logi) [im], `lastrundt` (date), `user1` (char), `lastruntm` (char), `user2` (char), `batchnm` (char) [i], `user3` (char), `user4` (char), `user5` (char), `statustype` (char), `user6` (deci-5), `rangebeg` (char[20]), `user7` (deci-5), `rangeend` (char[20]), `user8` (date), `optvalue` (char[20]), `user9` (date), `priority` (inte) [i], `startdt` (date) [i], `cono` (inte) [i], `Queue_name` (char) [i], `starttm` (inte) [i], `faxphoneno` (char), `whse` (char), `faxfrom` (char), `faxto1` (char), `faxto2` (char), `runnowfl` (logi) [m], `faxpriority` (logi) [m], `faxcom` (char[10]), `jobnm` (char), `xjobnm` (char[5]), `delfl` (logi) [m], `xprinternm` (char[5]), `starttm2` (inte), `filefl` (logi) [m], `xfilefl` (logi[5]) [m], `inusecd` (char) [i], `startdt2` (date), `backfl` (logi) [m], `oreqfl` (logi[20]) [m], `storefl` (logi) [m], `transproc` (char), `xfaxphoneno` (char[5]), `xfaxto1` (char[5]), `xfaxto2` (char[5]), `xfaxfrom` (char[5]), `xfaxpriority` (logi[5]) [m], `xfaxcom` (char[5]), `xfaxtag1` (char[5]), `xfaxtag2` (char[5]), `clienttzoffset` (inte), `outputover` (char), `xoutputover` (char[5])

### `sapbc`
**List processing for customer**
Fields: `reportnm` (char) [i], `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `seqno` (inte) [i], `custno` (deci-0) [im], `amount` (deci-2), `checkno` (deci-0), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `listproc` (char)

### `sapbj`
**List processing for journals**
Fields: `jrnlno` (inte) [i], `reportnm` (char) [i], `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `seqno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `listproc` (char)

### `sapbo`
**List processing for order entry**
Fields: `orderno` (inte) [i], `ordersuf` (inte) [i], `reportnm` (char) [i], `cono` (inte) [i], `operinit` (char), `transdt` (date) [i], `transtm` (char) [i], `route` (char), `reprintfl` (logi) [m], `seqno` (inte), `outputty` (char) [i], `custno` (deci-0) [m], `shipto` (char) [m], `operator` (char), `prodcat` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `listproc` (char)

### `sapbv`
**List processinf for Vendor/Invoice**
Fields: `reportnm` (char) [i], `cono` (inte) [i], `operinit` (char) [i], `transdt` (date), `transtm` (char), `vendno` (deci-0) [im], `apinvno` (char) [i], `type` (logi) [im], `allfl` (logi) [m], `seqno` (inte) [i], `seqno2` (deci-2), `name` (char), `selecttype` (char), `transtype` (char), `sortno` (inte) [i], `payallfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `listproc` (char)

### `sasa`
**All System Information**
Fields: `licensedt` (date), `secure` (inte), `timeout` (inte), `begwtno` (inte), `endwtno` (inte), `nextwtno` (inte), `checkdig` (inte), `modapfl` (logi) [m], `modarfl` (logi) [m], `modibfl` (logi) [m], `modcmfl` (logi) [m], `modglfl` (logi) [m], `modicfl` (logi) [m], `modkpfl` (logi) [m], `modoefl` (logi) [m], `modoifl` (logi) [m], `modpofl` (logi) [m], `colddir` (char), `modvtfl` (logi) [m], `randdproduct` (char), `modwtfl` (logi) [m], `modwmfl` (logi) [m], `modedfl` (logi) [m], `monitorfl` (logi) [m], `operinit` (char), `user1` (char), `transdt` (date), `user2` (char), `transtm` (char), `user3` (char), `user4` (char), `modsvfl` (logi) [m], `user5` (char), `oimcmfl` (logi) [m], `user6` (deci-5), `oimcmreqfl` (logi) [m], `user7` (deci-5), `licenseto` (char), `user8` (date), `rdcustno` (deci-0) [im], `user9` (date), `licenseno` (char), `cmupdarfl` (logi) [m], `cmupdcmfl` (logi) [m], `cmtbcontact` (inte), `cmprostype` (char), `cmcreatefmar` (logi) [m], `oimpyfl` (logi) [m], `docdir` (char), `modpmfl` (logi) [m], `nousers` (inte), `modbpfl` (logi) [m], `sysdir` (char), `custnofl` (logi) [m], `modprfl` (logi) [m], `modtqfl` (logi) [m], `modslfl` (logi) [m], `modisfl` (logi) [m], `modvafl` (logi) [m], `modbafl` (logi) [m], `modswfl` (logi) [m], `modrsfl` (logi) [m], `forcelogin` (logi) [m], `modwlfl` (logi) [m], `modogfl` (logi) [m], `transproc` (char), `modjmfl` (logi) [m], `graceperiod` (inte), `modotfl` (logi) [m], `ptxwhse` (char) [m], `ptxcono` (inte), `pwmaxdays` (inte), `pwmindays` (inte), `pwmaxlength` (inte), `pwminlength` (inte), `pwminnumeric` (inte), `pwminspecial` (inte), `pwminprev` (inte), `pwmaxattempt` (inte), `pwmaxlogins` (inte), `pwminalpha` (inte), `ptxfeewhse` (char) [m], `forceconosepfl` (logi) [m], `ccenccodeold` (raw), `ccenccodenew` (raw), `ccmstrseqold` (inte), `ccmstrseqnew` (inte)

### `sasapi`
**System Administrator Setup API Keys**
Fields: `applicationid` (char) [im], `applogicalid` (char), `applicationname` (char), `baseurl` (char), `securitytype` (char), `consumerkey` (char) [i], `secretkey` (char) [m], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `granttype` (char), `oauthsaak` (char), `oauthsask` (char)

### `sasb`
**System Administrator Setup Balance Changes**
Fields: `cono` (inte) [i], `currproc` (char) [im], `enterdt` (date) [im], `entertm` (char) [im], `primarykey` (char) [im], `secondkey` (char), `operinit` (char), `operinit2` (char), `transdt` (date), `transtm` (char), `chgbal` (deci-5[20]), `errorno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `enterdttz` (datetm-tz)

### `sasc`
**Company Master**
**Operators call this:** "Company Code" (Accounts Payable), "Company Name" (Accounts Payable), "Company Code" (Accounts Receivable), "Company Name" (Accounts Receivable), "Company Code" (Inventory), "Company Name" (Inventory), "Company Code" (Purchasing), "Company Name" (Purchasing), "Company Code" (Sales), "Company Name" (Sales), "Company Code" (TWL), "Company Name" (TWL), "Company Code" (Warehouse Transfers), "Company Name" (Warehouse Transfers)
Fields: `cono` (inte) [im], `conm` (char), `arminblamt` (deci-2), `arminscamt` (deci-2), `arperdays` (inte[4]) [m], `arscpct` (deci-2[4]), `arfutdays` (inte) [m], `transtm` (char), `transdt` (date), `operinit` (char), `name` (char), `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `phoneno` (char), `fedtaxid` (char), `propttype` (char), `intercofl` (logi) [m], `glsize` (inte[4]), `gldelim` (char[3]), `glcurfisc` (inte), `gl13perfl` (logi) [m], `gldefper` (inte), `glperahd` (inte), `glperbck` (inte), `glbegfisc` (inte), `glbegfl` (logi) [m], `glenddt` (date[13]), `glbegper` (inte), `glendper` (inte), `crglfl` (logi) [m], `croefl` (logi) [m], `crarfl` (logi) [m], `icaltvndfl` (logi) [m], `icbarcdfl` (logi) [m], `iccstprdfl` (logi) [m], `icintchgfl` (logi) [m], `icoptionfl` (logi) [m], `icsubfl` (logi) [m], `icsupcedfl` (logi) [m], `ictrdsrvfl` (logi) [m], `icupgrfl` (logi) [m], `iclookupnm` (char), `icsnpofl` (logi) [m], `icmsdsprt` (logi) [m], `icdeadstk` (deci-2), `icsgnuscst` (deci-2), `icphyadjam` (deci-2), `icglcost` (char), `iccosttype` (char), `iccommcost` (char), `icincaddsm` (logi) [m], `icincaddcp` (logi) [m], `icincaddcm` (logi) [m], `apimmedfl` (logi) [m], `apminbuy` (inte), `apholdfl` (logi) [m], `apclspct` (deci-2[12]), `oedupfl` (logi) [m], `oeapprty` (char), `oefutdays` (inte), `oemninvamt` (inte), `oecostsale` (logi) [m], `oelinefl` (logi) [m], `oebulkpickfl` (logi) [m], `pdvenqtyfl` (logi) [m], `pdnxtquote` (inte), `pdpround` (char), `pdptarget` (inte), `smcustrebfl` (logi) [m], `smstorety` (logi) [m], `smwodiscfl` (logi) [m], `smcommtype` (logi) [m], `smtaxtype` (logi) [m], `smordcost` (deci-2), `smdeadmin` (deci-2), `smnsfl` (logi) [m], `smclass` (deci-1[12]), `porraraccp` (inte), `pononstkfl` (logi) [m], `poqtyrcvfl` (logi) [m], `oeautofity` (char), `pomrgrptfl` (logi) [m], `poadddist` (char), `ponxtrepno` (inte), `poavgcspct` (deci-2), `pdlevelfl` (logi[8]) [m], `wtnonstkfl` (logi) [m], `wtrraraccp` (inte), `wtmrgrptfl` (logi) [m], `wtnxtrepno` (inte), `pdwhsefl` (logi) [m], `smvendrebfl` (logi) [m], `arminbalsc` (deci-2), `arscpc2` (deci-2[4]), `arscbal` (deci-2[4]), `glcurrfl` (logi) [m], `arpiflimit` (deci-2), `pocostfl` (logi) [m], `oewtfl` (logi) [m], `oepofl` (logi) [m], `pdpromofl` (logi) [m], `oealtwhsefl` (logi) [m], `printdir` (char), `gldivno` (inte[9]), `gldeptno` (inte[9]), `glacctno` (inte[9]), `glsubno` (inte[9]), `glprofpct` (deci-2[4]), `dunsno` (char), `upcvno` (inte), `oepckheadfl` (logi) [m], `oeinvheadfl` (logi) [m], `oeackheadfl` (logi) [m], `oesplabel` (char), `icglbsty` (inte), `icglincty` (inte), `arstmtheadfl` (logi) [m], `apchkheadfl` (logi) [m], `popoheadfl` (logi) [m], `arstmtfrmt` (inte), `apchkfrmt` (inte), `popofrmt` (inte), `site` (char), `polabelfrmt` (inte), `polabelprnt` (char), `oereqdays` (inte), `wtleadtm` (inte), `poapfl` (logi) [m], `pomrgpricefl` (logi) [m], `powodist` (char), `oeautometh` (char), `wtqtyrcvfl` (logi) [m], `oepickfl` (logi) [m], `glbalhistfl` (logi) [m], `oercpttop` (char[4]), `oercptbot` (char[2]), `oebofillfl` (logi) [m], `oeautosubfl` (logi) [m], `arshipfl` (logi) [m], `authcd` (inte), `oeminchgamt` (deci-2), `oemvdelty` (char), `icnsprodcat` (char), `iclotrcptty` (char), `ap1099frmt` (inte), `wtpushlev` (char), `oeforcefl` (logi) [m], `ardiscdays` (inte), `oifaxpreno` (char), `oifaxsufno` (char), `country` (char), `taxgroupnm` (char[5]), `itcfl` (logi) [m], `icrollcostfl` (logi) [m], `pocapaddfl` (logi) [m], `pocapdiscfl` (logi) [m], `pocapfl` (logi) [m], `smmergefl` (logi[6]) [m], `smshiptofl` (logi[3]) [m], `smcompfl` (logi) [m], `smwhsefl` (logi[4]) [m], `apordcost` (deci-2), `oebolheadfl` (logi) [m], `oepickordty` (char), `pdspecialfl` (logi) [m], `oeprtfrmt` (inte[6]), `oefaxfrmt` (inte[6]), `oeedifrmt` (inte[6]), `poedifrmt` (inte), `pofaxfrmt` (inte), `tenderfl` (logi) [m], `csbofl` (logi) [m], `sventnl` (logi) [m], `svforcesn` (logi) [m], `sventflt` (logi) [m], `svforcelir` (logi) [m], `svdefoper` (char), `svcrbofl` (logi) [m], `svlnaccfl` (logi) [m], `icfifofl` (logi) [m], `poallfl` (logi) [m], `oealtfillfl` (logi) [m], `oeslentryty` (char[2]), `wtslentryty` (char[2]), `cshldbckty` (char), `oecommitfl` (logi) [m], `oedivfl` (logi) [m], `wtpickfrmt` (inte), `wtpickheadfl` (logi) [m], `wmmultfl` (logi) [m], `wmputfl` (logi) [m], `wmsboefl` (logi) [m], `wmsbpofl` (logi) [m], `kpdelfl` (logi) [m], `wmprfillfl` (logi) [m], `wmexfillfl` (logi) [m], `oecntrsbase` (char), `smdoincl` (char), `smspordincl` (char), `smpickupincl` (char), `arfpaddonfl` (logi) [m], `wmdelfl` (logi) [m], `icrmfifofl` (logi) [m], `wmqtyfl` (logi) [m], `oifgb` (char), `oeretapprty` (char), `artermscd` (char), `wmpprimfl` (logi) [m], `svcchgshipfl` (logi) [m], `pmalloc` (char), `pmscalfl` (logi) [m], `wmintfl` (logi) [m], `kpprtfmt` (inte), `pminsfl` (logi) [m], `pmpkgfl` (logi) [m], `iccatstockfl` (logi) [m], `iccatkeyfl` (logi) [m], `oebostage` (inte), `oepctfillty` (char), `oepctfillqty` (inte), `iccogsadjfl` (logi) [m], `oepkbofl` (logi) [m], `pdjobfl` (logi) [m], `wmprrmfl` (logi) [m], `pmcwtfl` (logi) [m], `prpremrate` (deci-3), `prdblrate` (deci-3), `prstdwrkwk` (deci-2), `prrptqtr` (inte), `prpostqtr` (inte), `prrptyr` (inte), `prorigname` (char), `prdestname` (char), `prdestmodemno` (char), `prglsumfl` (logi) [m], `prchinesefl` (logi) [m], `prpostyr` (inte), `geocdfl` (logi) [m], `bpvqfrmt` (inte), `bpvqedifrmt` (inte), `bpvqfaxfrmt` (inte), `bpvqheadfl` (logi) [m], `bpbpfrmt` (inte), `bpbpheadfl` (logi) [m], `bpcmfl` (logi) [m], `bpaddpropfl` (logi) [m], `bplettercd` (char[6]), `bpbidtype` (char), `bpslsrepcd` (char), `bpminmargin` (deci-2), `bpcommtype` (char), `bpaltvendfl` (logi) [m], `bpdaystoexp` (inte), `bpnostkpopfl` (logi) [m], `bplockstgcd` (char), `bphistoryfl` (logi) [m], `pdrebhierty` (char), `bpaddarssfl` (logi) [m], `oewriteamt` (deci-2), `porcvnofl` (logi) [m], `geoindxty` (char), `icchaindisc` (char), `pdlevelpl` (logi) [m], `pdlevelpc` (logi) [m], `prunionhdg` (char), `bpbpfaxfrmt` (inte), `bpenfphasefl` (logi) [m], `arrollcd` (char), `gldivfl` (logi) [m], `gldivno2` (inte[9]), `gldeptno2` (inte[9]), `glacctno2` (inte[9]), `glsubno2` (inte[9]), `arcrdiscfl` (logi) [m], `ediindir` (char), `edioutdir` (char), `bppround` (char), `slimportdir` (char), `tqdbnm` (char), `tqdirnm` (char), `creditmgr` (char), `credalertty` (char), `tqsupdirnm` (char), `bpptarget` (inte), `pmpause` (inte), `svcchgdivfl` (logi) [m], `icbackpstfl` (logi) [m], `tqcyclebpfl` (logi) [m], `tqcyclewtfl` (logi) [m], `tqcyclepofl` (logi) [m], `tqcycleoefl` (logi) [m], `geotxrgfl` (logi) [m], `arcodinbalfl` (logi) [m], `aragebydayfl` (logi) [m], `icpartialfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `icdatclabel` (char), `icdatcty` (char), `icdatccost` (deci-5), `oifaxattnfl` (logi[10]) [m], `oifaxdev` (char[10]), `oifaxhardfl` (logi[10]) [m], `prdirdepfl` (logi) [m], `prdestrtno` (inte), `prorigrtno` (inte), `prorigacctno` (char), `prsetrtno` (inte), `prsetname` (char), `prsetacctno` (char), `icnsdofl` (logi) [m], `apdisputefl` (logi) [m], `lookupwildfl` (logi) [m], `oensinzerofl` (logi) [m], `oedomovefl` (logi) [m], `kwexclwords` (char[20]), `kwdelim` (char[20]), `wtbostage` (inte), `prachcoid` (inte), `kpbostage` (inte), `icexcpqty` (inte), `iclowusage` (deci-5), `oeborsvfl` (logi) [m], `apbatchdel` (logi) [m], `aplntolpct` (deci-2), `apinvtolpct` (deci-2), `apuser1pct` (deci-2), `apuser2pct` (deci-2), `apmatchfmt` (inte), `apinvtolamt` (deci-2), `aplntolamt` (deci-2), `apuser1amt` (deci-2), `apuser2amt` (deci-2), `apqtytolamt` (deci-2), `apqtytolpct` (deci-2), `pdlevelrt` (logi) [m], `apmcdiscfl` (logi) [m], `oasactivitiesfl` (logi) [m], `icclasspct1` (deci-2), `icclasspct2` (deci-2), `icclasspct3` (deci-2), `icclasspct4` (deci-2), `icclasspct5` (deci-2), `icclasspct6` (deci-2), `icclasspct7` (deci-2), `icclasspct8` (deci-2), `icclasspct9` (deci-2), `icclasspct10` (deci-2), `icclasspct11` (deci-2), `icclasspct12` (deci-2), `oevrebcalcty` (char), `oefrzrebty` (char), `pdreblevlfl1` (logi) [m], `pdreblevlfl2` (logi) [m], `pdreblevlfl3` (logi) [m], `pdreblevlfl4` (logi) [m], `pdreblevlfl5` (logi) [m], `pdrebwhsefl` (logi) [m], `pdrebjobfl` (logi) [m], `pdrebsubtyfl` (logi) [m], `pdcustrebfl` (logi) [m], `pdnextclmno` (inte), `icupclength1` (inte), `icupclength2` (inte), `icupclength3` (inte), `icupclength4` (inte), `icupclength5` (inte), `icupclength6` (inte), `icupclabel1` (char), `icupclabel2` (char), `icupclabel3` (char), `icupclabel4` (char), `icupclabel5` (char), `icupclabel6` (char), `icupcdelim` (char), `smsvfl` (logi) [m], `smsvpfl` (logi) [m], `smsvpwhsefl` (logi) [m], `smsvwfl` (logi) [m], `smsvwwhsefl` (logi) [m], `icincaddadjfl` (logi) [m], `vapckfrmt` (inte), `vaintrnfrmt` (inte), `vapckheadfl` (logi) [m], `vaintrnheadfl` (logi) [m], `vaextrncstty` (char), `vaintrncstty` (char), `langcd` (char), `transproc` (char), `icincaddgl` (logi) [m], `icsmcost` (char), `icvalidatemixfl` (logi) [m], `rxsignaturefl` (logi) [m], `usestep` (inte), `tqappsrvdirnm` (char), `pdlevel4pl` (logi) [m], `pdlevel4pc` (logi) [m], `pdlevel4rt` (logi) [m], `apusecost` (char) [m], `apeichgpartialfl` (logi) [m], `iccoredflt` (char), `icimplcorepre` (char), `icdirtycorepre` (char), `icgracefl` (logi[9]) [m], `icvendcost` (char) [m], `arcustcoregrcfl` (logi) [m], `apvendcoregrcfl` (logi) [m], `arcustgraceper` (inte), `apvendgraceper` (inte), `pocostcorechyes` (char), `pocostcorechno` (char), `bpovpricefl` (logi) [m], `pocrctreason` (char), `currencyty` (char), `potallyadjfl` (logi) [m], `vaautoboty` (char), `vastkadjty` (char), `arshiptosvc` (char), `sminvcost` (char), `comminvcost` (char), `sequcfl` (logi) [m], `addr3` (char), `jmcprtfrmt` (inte), `freeformaddr` (logi) [m], `jmvprtfrmt` (inte), `jmcfaxfrmt` (inte), `phonemask` (char), `jmvfaxfrmt` (inte), `jmcheadfl` (logi) [m], `jmvheadfl` (logi) [m], `oeesrcnsfl` (logi) [m], `iccommcatfl` (logi) [m], `iccommcaticscfl` (logi) [m], `oebocredchkfl` (logi) [m], `poataxty` (char), `pootaxty` (char), `geocd` (inte), `currsymbol` (char), `icnsdowriteamt` (deci-2), `wtnsovrfillty` (char), `wtuseroqfl` (logi) [m], `jmapprovfl` (logi) [m], `dfltscraprsn` (char), `outofcityfl` (logi) [m], `esbactioncode` (char), `rowpointer` (char) [i], `addressoverfl` (logi) [m]

### `sasga`
**Addon Tax Group**
Fields: `cono` (inte) [i], `tablety` (char) [i], `recty` (inte) [i], `statecd` (char) [i], `addontaxgroup` (inte), `countycd` (char) [i], `citycd` (char) [i], `othercd` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `taxgroup` (inte) [i], `addonno` (inte) [i], `taxablety` (char)

### `sasge`
**Exemptions To Taxes**
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `state` (char) [i], `taxtype` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `comment` (char), `certno` (char), `taxgroup` (inte), `taxdt` (date), `taxfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `taxdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `custno` (Customer) — Can be CHAR(24) if using xref; Valid values/xref: ARSC
- `shipto` (Shipto) — Valid values/xref: ARSS
- `state` (State/Province) — Valid values/xref: SASGM SASGS-Canada
- `taxtype` (Tax Exempt Type) — Same as found in ICSW
- `user5` (User 5) — Used for Conversion Import ID

### `sasgl`
**Gov't, Local**
Fields: `cono` (inte) [i], `state` (char) [im], `taxauth` (char) [im], `descrip` (char), `gldivno` (inte[4]), `gldeptno` (inte[4]), `glacctno` (inte[4]), `glsubno` (inte[4]), `saletaxn` (deci-3[5]), `saletaxc` (deci-3[5]), `saletaxo` (deci-3[5]), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `sasgm`
**Master Sales Tax Rate File**
Fields: `cono` (inte) [i], `recty` (inte) [i], `taxgroup` (inte) [i], `statecd` (char) [i], `countycd` (char) [i], `citycd` (char) [i], `othercd` (char) [i], `operinit` (char), `taxsalert` (deci-5), `transtm` (char), `taxusert` (deci-5), `maxtaxty` (char) [m], `taxtransrt` (deci-5), `user1` (char), `taxexcrt` (deci-5), `taxexcflat` (deci-2), `taxexcflatfl` (logi) [m], `countytaxfl` (logi) [m], `citytaxfl` (logi) [m], `othertaxfl` (logi) [m], `maxtaxamt` (deci-2), `orgdestcd` (char), `taxrptfl` (logi) [m], `glacctno` (inte[10]), `gldeptno` (inte[10]), `gldivno` (inte[10]), `glsubno` (inte[10]), `transdt` (date), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `descrip` (char), `taxid` (char), `addontaxgroup` (inte[9]), `addontaxfl` (logi[9]) [m], `transproc` (char), `taxexcflatty` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `recty` (Rec Type) — 1-fed, 2-state, 3- county, 4-city, 5-other; Valid values/xref: 1, 2, 3, 4, or 5; Required
- `taxgroup` (Tax Group) — From SASC Tax Groups or SASTN-TG records; Valid values/xref: SASC, SASTN-TG; Required; Default: 1
- `descrip` (Description) — All must be Unique; Required
- `orgdestcd` (Origin/Destination Code) — 1 - Origin 2 - Destination 3 - Other; Valid values/xref: 1, 2, 3; Required; Default: 2
- `taxexcflatty` (Excise Flat Type) — Valid values/xref: U, L or W; Default: U
- `maxtaxty` (Max Tax Type) — Invoice, Line Amount or Line Unit Availabe Starting 4.0; Valid values/xref: A, I or U; Default: I
- `gldivno1` (Sales Tax Pay - Div) — Valid values/xref: GLSA
- `gldeptno1` (Sales Tax Pay - Dept) — Valid values/xref: GLSA
- `glacctno1` (Sales Tax Pay - Acct) — Valid values/xref: GLSA
- `glsubno 1` (Sales Tax Pay - Sub) — Valid values/xref: GLSA
- `gldivno2` (Use Tax Pay - Div) — Valid values/xref: GLSA
- `gldeptno2` (Use Tax Pay - Dept) — Valid values/xref: GLSA
- `glacctno2` (Use Tax Pay - Acct) — Valid values/xref: GLSA
- `glsubno2` (Use Tax Pay - Sub) — Valid values/xref: GLSA
- `gldivno3` (Tansit Tax Pay - Div) — Valid values/xref: GLSA
- `gldeptno3` (Tansit Tax Pay - Dept) — Valid values/xref: GLSA
- `glacctno3` (Tansit Tax Pay - Acct) — Valid values/xref: GLSA
- `glsubno3` (Tansit Tax Pay - Sub) — Valid values/xref: GLSA
- `gldivno4` (Excise Tax Pay - Div) — Valid values/xref: GLSA
- `gldeptno4` (Excise Tax Pay - Dept) — Valid values/xref: GLSA
- `glacctno4` (Excise Tax Pay - Acct) — Valid values/xref: GLSA
- `glsubno4` (Excise Tax Pay - Sub) — Valid values/xref: GLSA
- `gldivno5` (Sales Tax Cash Basis - Div) — Cash Basis Only; Valid values/xref: GLSA
- `gldeptno5` (Sales Tax Cash Basis - Dept) — Cash Basis Only; Valid values/xref: GLSA
- `glacctno5` (Sales Tax Cash Basis - Acct) — Cash Basis Only; Valid values/xref: GLSA
- `glsubno 5` (Sales Tax Cash Basis - Sub) — Cash Basis Only; Valid values/xref: GLSA
- `gldivno6` (Use Tax Cash Basis - Div) — Cash Basis Only; Valid values/xref: GLSA
- `gldeptno6` (Use Tax Cash Basis - Dept) — Cash Basis Only; Valid values/xref: GLSA
- `glacctno6` (Use Tax Cash Basis - Acct) — Cash Basis Only; Valid values/xref: GLSA
- `glsubno6` (Use Tax Cash Basis - Sub) — Cash Basis Only; Valid values/xref: GLSA
- `gldivno7` (Tansit Tax Cash Basis - Div) — Cash Basis Only; Valid values/xref: GLSA
- `gldeptno7` (Tansit Tax Cash Basis - Dept) — Cash Basis Only; Valid values/xref: GLSA
- `glacctno7` (Tansit Tax Cash Basis - Acct) — Cash Basis Only; Valid values/xref: GLSA
- `glsubno7` (Tansit Tax Cash Basis - Sub) — Cash Basis Only; Valid values/xref: GLSA
- `gldivno8` (Excise Tax Cash Basis - Div) — Cash Basis Only; Valid values/xref: GLSA
- `gldeptno8` (Excise Tax Cash Basis - Dept) — Cash Basis Only; Valid values/xref: GLSA
- `glacctno8` (Excise Tax Cash Basis - Acct) — Cash Basis Only; Valid values/xref: GLSA
- `glsubno8` (Excise Tax Cash Basis - Sub) — Cash Basis Only; Valid values/xref: GLSA
- `user5` (user5) — Used for Conversion Import ID

### `sasgs`
**System Admin, Gov't State**
Fields: `cono` (inte) [i], `state` (char) [im], `descrip` (char), `taxid` (char), `saletax` (deci-3[5]), `glacctno` (inte), `gldivno` (inte), `gldeptno` (inte), `glsubno` (inte), `operinit` (char), `transdt` (date), `transtm` (char), `taxgroup` (inte[9]), `pstgstfl` (logi) [m], `addontaxfl` (logi[9]) [m], `harmonizedfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `termsdisconpstfl` (logi) [m], `ecsalesfl` (logi) [m], `dsplvatbrkdwnfl` (logi) [m], `glacctno2` (inte), `gldivno2` (inte), `gldeptno2` (inte), `glsubno2` (inte)

### `sasgt`
**Tariff Table**
Fields: `tariffcd` (char) [im], `dutyrate` (deci-2), `operinit` (char), `transdt` (date), `transtm` (char), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `cono` (inte) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `wordindexfl` (logi) [m], `rowpointer` (char) [i], `countryoforigin` (char) [im], `transdttmz` (datetm-tz) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `countryoforigin` (Country of Origin) — Valid values/xref: SASTT-W
- `gldivno` (GL Division # - Zero for fully divisionalized company otherwise, specific division #) — Valid values/xref: GLSA
- `gldeptno` (GL Department #) — Valid values/xref: GLSA
- `glacctno` (GL Account#) — Can be CHAR(24) if using the Xref.; Valid values/xref: GLSA
- `glsubno` (GL Subaccount #) — Valid values/xref: GLSA
- `user5` (user5) — Used for Conversion Import ID

### `sasj`
**Journal Assignment**
Fields: `cono` (inte) [i], `jrnlno` (inte) [im], `nopostings` (inte), `totcr` (deci-2), `totdr` (deci-2), `tothash` (deci-0), `opendt` (date) [i], `opentm` (char), `closedt` (date), `closetm` (char), `operinit` (char), `oper2` (char) [im], `transtm` (char), `transdt` (date), `ourproc` (char) [i], `printfl` (logi) [im], `closefl` (logi) [im], `frxinterface` (char), `proofdr` (deci-2), `currproc` (char) [i], `proofcr` (deci-2), `period` (inte), `intellexdt` (date) [i], `postdt` (date), `batchnm` (char), `user1` (char), `balancefl` (logi) [im], `user2` (char), `smmergedfl` (logi) [im], `user3` (char), `perfisc` (inte), `user4` (char), `batchfl` (logi) [im], `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `esbprocessfl` (logi) [m], `transdttmz` (datetm-tz) [i], `closedttz` (datetm-tz), `intellexdttz` (datetm-tz), `opendttz` (datetm-tz), `postdttz` (datetm-tz), `perfisctz` (datetm-tz), `periodtz` (datetm-tz), `rowpointer` (char) [i]

### `sasjj`
**journal/cash drawer in use**
Fields: `cono` (inte) [i], `jrnlno` (inte) [i], `apinm` (char) [i], `whse` (char), `drawerid` (char), `batchnm` (char), `transdttmz` (datetm-tz), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-2), `user7` (deci-2), `user8` (date), `user9` (date)

### `sasog`
**System Admin Operators - Group Names**
Fields: `cono` (inte) [im], `oper2` (char) [im], `groupnm` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `sasogh`
**System Admin Operators - Group Headers**
Fields: `cono` (inte) [im], `groupnm` (char) [i], `descrip` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `groupseqno` (inte)

### `sasoo`
**System Admin, Operators**
Fields: `cono` (inte) [im], `operinit` (char), `printernm` (char), `oper2` (char) [im], `password` (char), `currproc` (char), `whse` (char), `oetrntype` (char), `homewhsefl` (logi) [m], `seecostfl` (logi) [m], `seecommfl` (logi) [m], `chgbalfl` (logi) [m], `credpostfl` (logi) [m], `holdoverfl` (logi) [m], `termsoverfl` (logi) [m], `temp` (char), `intercofl` (logi) [m], `nonstockfl` (logi) [m], `resalefl` (logi) [m], `extendfl` (logi) [m], `shiptofl` (logi) [m], `transdt` (date), `transtm` (char), `oephonefl` (logi) [m], `updglarty` (char), `updglapty` (char), `updglicty` (char), `updglpoty` (char), `updgloety` (char), `updglwtty` (char), `updglkpty` (char), `arwrtofflim` (deci-2), `tqprosno` (deci-0), `oeqtyshipty` (char), `loginfl` (logi) [im], `tqemailaddr` (char), `logindt` (date), `tqposition` (char), `logintm` (char), `tqdelvrmeth` (char), `oerebty` (char), `notesfl` (logi) [m], `vendlutype` (char), `ringfl` (logi) [m], `slsrep` (char), `useprevnsfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `oecostoverty` (char), `user4` (char), `openordno` (inte), `user5` (char), `openordsuf` (inte), `user6` (deci-5), `oeheaderfl` (logi) [m], `user7` (deci-5), `user8` (date), `oelineno` (inte), `user9` (date), `oeonlyfl` (logi) [m], `wtapprwhse` (char), `gldivno` (inte[28]), `gldeptno` (inte[28]), `glacctno` (inte[28]), `glsubno` (inte[28]), `helpfl` (logi) [m], `rprinternm` (char), `reqtakenfl` (logi) [m], `valtakenfl` (logi) [m], `superfl` (logi) [m], `custlutype` (char), `secnotefl` (logi) [m], `custno` (deci-0) [m], `securevno` (inte), `person` (char), `prodlutype` (char), `oeoptionfl` (logi) [m], `oebuylistfl` (logi) [m], `shippingpt` (char), `backfl` (logi) [m], `catconvertfl` (logi) [m], `oepricefl` (char), `arecedbfl` (logi) [m], `chgglcostfl` (logi) [m], `oetietype` (char), `tenderty` (char), `glacctno2` (inte[28]), `gldeptno2` (inte[28]), `gldivno2` (inte[28]), `glsubno2` (inte[28]), `bprvunlkfl` (logi) [m], `bpdeftype` (char), `ourproc` (char) [i], `startdt` (date), `starttm` (inte), `secdivno` (inte), `secdeptno` (inte), `secsubno` (inte), `verrcvchgfl` (logi) [m], `apsuperfl` (logi) [m], `nscommfl` (logi) [m], `gloverfl` (logi) [m], `spcchngfl` (logi) [m], `taxoverfl` (logi) [m], `usagewarnfl` (logi) [m], `oimailfl` (logi) [m], `oiphonefl` (logi) [m], `cmactfl` (logi) [m], `openpono` (inte), `openposuf` (inte), `openwtno` (inte), `openwtsuf` (inte), `loginnm` (char), `devicenm` (char), `sysadminfl` (logi) [m], `langcd` (char), `transproc` (char), `oeslsrepfl` (char) [m], `unmaskccty` (char), `promoprcwin` (char), `pcpassword` (char), `pcusername` (char), `emdelvrmeth` (char), `oeextlfl` (char), `pocrctfl` (logi) [m], `pwlastchgdt` (date), `pwprevious` (char[10]), `pwloginattempts` (inte), `vaautoshipty` (char), `autologpasswd` (char), `jmupdprtpofl` (logi) [m], `userclearfl` (logi) [m], `vaheaderty` (char), `vaautolnentryty` (char), `whsegroup` (char), `popotyamtmin` (deci-2), `popotyamtmax` (deci-2), `podotyamtmin` (deci-2), `podotyamtmax` (deci-2), `oesotyamtmin` (deci-2), `oesotyamtmax` (deci-2), `oedotyamtmin` (deci-2), `oedotyamtmax` (deci-2), `oesotymrgpctmin` (deci-2), `oesotymrgpctmax` (deci-2), `oedotymrgpctmin` (deci-2), `oedotymrgpctmax` (deci-2), `oesotymrgamtmin` (deci-2), `oesotymrgamtmax` (deci-2), `oedotymrgamtmin` (deci-2), `oedotymrgamtmax` (deci-2), `formprinternm` (char), `usergroup` (char), `saspgroup` (char), `nsbinlocfl` (logi) [m], `oensqtyshpty` (char), `vendpostfl` (logi) [m], `returnpostfl` (logi) [m], `nscrtoanty` (char), `icswstchgfl` (logi) [m], `jmapprvty` (char), `autobillwhsefl` (logi) [m], `oeupdtcustpofl` (logi) [m], `icacquiredtfl` (logi) [m], `storefrontuserid` (char), `limitholdcds` (char), `limittakenbyfl` (logi) [m], `limitslsrepfl` (logi) [m], `showroomuserfl` (logi) [m], `wlpicktype` (char), `oehardprcovrfl` (logi) [m], `icmanlistty` (char), `icmassmaintfl` (logi) [m], `icmanlistoverfl` (logi) [m], `prodnotesfl` (logi) [m], `custnotesfl` (logi) [m], `valinecancelfl` (logi) [m], `iccatcrtty` (char), `ncnrfl` (logi) [m], `kpverchg` (char), `vaverchg` (char), `kpveruse` (char), `oechglntypefl` (logi) [m], `vaveruse` (char), `oeorigpromisefl` (logi) [m], `oeautoapplyovrfl` (logi) [m], `originchangefl` (logi) [m], `devloc` (char), `holdforauthdefault` (char), `oetoleranceovrfl` (logi) [m], `holdintlfl` (logi) [m], `cfgaccesscd` (char), `kptietype` (char), `xconocostfl` (logi) [m], `altoperinit` (char), `ifsuser` (char) [i], `caticcrtty` (char), `esbactioncode` (char), `oenoinvoicefl` (logi) [m], `oetokenmodifyfl` (logi) [m], `allowfulfillmentty` (char), `oesaleswhsety` (char), `nsquoteoanty` (char), `contactnotety` (char), `logindttz` (datetm-tz), `pwlastchgdttz` (datetm-tz), `rowpointer` (char) [i]

### `sasos`
**Operator Security**
Fields: `cono` (inte) [i], `operinit` (char) [m], `menuproc` (char) [im], `securcd` (inte[16]) [m], `transdt` (date), `transtm` (char), `oper2` (char) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `sasp`
**SA Printer Setup**
Fields: `printernm` (char) [im], `descrip` (char), `wide` (logi) [m], `ptype` (char) [m], `pcommand` (char), `operinit` (char), `transtm` (char), `transdt` (date), `pclose` (inte[10]), `pcompress` (inte[10]), `pnormal` (inte[10]), `pinit` (inte[10]), `user1` (inte[10]), `user2` (inte[10]), `user3` (inte[10]), `user4` (inte[10]), `user5` (inte[10]), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `armaillbl` (char), `cmmaillbl` (char), `prodlbl` (char), `shiplbl` (char), `binloclbl` (char), `edilbl` (char), `picklbl` (char), `rxsprinter` (char), `transproc` (char), `cono` (inte), `cartonlbl` (char), `rcvlbl` (char), `rcvwtlbl` (char), `maxlabels` (inte), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `saspgroup` (char), `altsizeprinter` (char), `labelsize` (char), `pricelbl` (char), `cnoeshiplbl` (char), `cnwtshiplbl` (char), `cncartonlbl` (char), `cnproductlbl` (char), `cnoepkglbl` (char), `cnwtpkglbl` (char)

### `saspg`
**System Administrator Setup Printer Groups**
Fields: `saspgroup` (char) [im], `descrip` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `sasr`
**Freight Rate Table**
Fields: `cono` (inte) [i], `whse` (char) [im], `shipvia` (char) [i], `zone` (char) [i], `overmaxrate` (deci-2), `weightlimit` (deci-5[500]), `rate` (deci-2[500]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transcd` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `delvdays` (inte), `delvdesc` (char)

### `sasse`
**System Administrator Setup System Error Messages**
Fields: `errorno` (inte) [im], `errormsg` (char), `transdt` (date), `transtm` (char), `operinit` (char), `bellfl` (logi) [m], `standardty` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `trmgrlang` (char) [i], `transproc` (char)

### `sassi`
**System Administrator Setup System Initial Values**
Fields: `File` (char) [i], `Field-nam` (char) [i], `Init-Val` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `sassm`
**System Admin Menu Setup**
Fields: `currproc` (char) [i], `frametitle` (char), `menutitle` (char), `callproc` (char), `exitproc` (char), `menuproc` (char) [im], `menupos` (inte) [i], `securpos` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `ringtitle` (char), `osproc` (char), `ourproc` (char), `standardty` (char), `gginfo` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `functy` (char), `inqproc` (char[7]), `inqtitle` (char[7]), `inqtype` (char[7]), `trmgrlang` (char) [i], `transproc` (char)

### `sassp`
**Time Zone Cross Reference**
Fields: `areacd` (char) [im], `timezone` (char), `state` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `sassr`
**SA Report Setup**
Fields: `currproc` (char) [im], `rpttitle` (char), `reportid` (char) [m], `recaloptno` (inte), `listproc` (char), `pausebeg` (char), `printoptfl` (logi) [m], `rangenm` (char[20]), `requirefl` (logi[20]) [m], `edittype1` (char[20]), `optionnm` (char[20]), `optdef` (char[20]), `optvaluea` (char[20]), `optvalueb` (char[20]), `optvaluec` (char[20]), `optvalued` (char[20]), `optvaluee` (char[20]), `edittype2` (char[20]), `operinit` (char), `transdt` (date), `transtm` (char), `rangecnt` (inte), `user1` (char), `optioncnt` (inte), `user2` (char), `wide` (logi) [m], `user3` (char), `jrnlfl` (logi) [m], `user4` (char), `whseprtno` (inte), `user5` (char), `standardty` (char), `user6` (deci-5), `pglength` (inte), `user7` (deci-5), `xpglength` (inte[5]), `user8` (date), `openprfl` (logi) [m], `user9` (date), `openprno` (inte), `headerprfl` (logi) [m], `xheaderprfl` (logi[5]) [m], `optpgfl` (logi) [m], `xoptpgfl` (logi[5]) [m], `titletype` (logi) [m], `xtitletype` (logi[5]) [m], `rflength` (inte[20]), `oflength` (inte[20]), `pagedfl` (logi) [m], `xpagedfl` (logi[5]) [m], `xwide` (logi[5]) [m], `orequirefl` (logi[20]) [m], `coldfl` (logi) [m], `xcoldfl` (logi[5]) [m], `backfl` (logi) [m], `trmgrlang` (char) [i], `transproc` (char), `recaloptno2` (inte), `recaloptno3` (inte), `listproc2` (char), `listproc3` (char)

### `sasst`
**System Tax Table**
Fields: `zipcd` (char) [i], `statecd` (char), `taxauth` (char), `transdt` (date), `operinit` (char), `transtm` (char), `whse` (char), `citycd` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `countycd` (char), `other1cd` (char), `other2cd` (char), `transproc` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `zipcd` (Zip code) — Can be 5 digit or including the dash and 4 additional digits; Valid values/xref: SASST is not unique to a company in SX.e so it is shared across the database; Required
- `statecd` (State code) — Only supports Sales/Use SASGM; Valid values/xref: SASGM
- `countycd` (County Code) — Valid values/xref: SASGM
- `citycd` (City Code) — Valid values/xref: SASGM
- `other1cd` (Other 1 Code) — Valid values/xref: SASGM
- `other2cd` (Other 2 Code) — Valid values/xref: SASGM
- `whse` (Warehouse) — Can be CHAR(24) if using the Xref.; Valid values/xref: ICSD
- `taxauth` (Taxing Entity) — Old Code for Use with Tax Xref; Valid values/xref: Used for DC Xref only
- `user5` (user5) — Used for Conversion Import ID

### `sasta`
**System Admin Tables, Alpha**
**Operators call this:** "Supplier Type Code" (Accounts Payable), "Supplier Type Name" (Accounts Payable), "Customer Type Code" (Accounts Receivable), "Customer Type Name" (Accounts Receivable), "Customer Price Type Code" (Accounts Receivable), "Customer Price Type Name" (Accounts Receivable), "Product Category Code" (Inventory), "Product Category Name" (Inventory), "Override Reason Code" (Inventory), "Override Reason Name" (Inventory), "Supplier Type Code" (Purchasing), "Supplier Type Name" (Purchasing), "Product Category Code" (Sales), "Product Category Name" (Sales), "Customer Type Code" (Sales), "Customer Type Name" (Sales), "Customer Price Type Code" (Sales), "Customer Price Type Name" (Sales), "Credit Reason Code" (Sales), "Credit Reason Name" (Sales)
Fields: `cono` (inte) [i], `codeiden` (char) [im], `codeval` (char) [im], `descrip` (char) [i], `unitconv` (deci-5), `minmarpct` (deci-2), `maxmarpct` (deci-2), `whse` (char), `editpcd` (char), `edidtcd` (char), `ediunavty` (char), `operinit` (char), `transtm` (char), `transdt` (date), `termspct` (deci-2), `user1` (char), `discdays` (inte), `user2` (char), `duedays` (inte), `user3` (char), `proxcutday` (inte), `user4` (char), `nopaymts` (inte), `user5` (char), `termsfreq` (inte), `user6` (deci-5), `pcatdiscfl` (logi) [m], `user7` (deci-5), `lostbususagefl` (logi) [m], `user8` (date), `user9` (date), `termslinefl` (logi) [m], `termscodfl` (logi) [m], `unitediuom` (char), `returnty` (char), `restockfl` (logi) [m], `restockamt` (deci-2), `reqwarrfl` (logi) [m], `reqauthfl` (logi) [m], `disctype` (char), `duetype` (char), `discdt` (date), `duedt` (date), `disccutday` (inte), `dueproxday` (inte[2]), `discproxday` (inte[2]), `splitfl` (logi) [m], `discsplitfl` (logi) [m], `proxmonths` (inte[2]), `duecutday` (inte), `reasunavty` (char), `reqinvfl` (logi) [m], `usagefl` (logi) [m], `warrexchgfl` (logi) [m], `schedmm` (char), `scheddd` (char), `schedyy` (char), `schedwd` (char), `trmgrlang` (char), `transproc` (char), `exclecomm` (char), `restktaxgrp` (inte), `ptxfeeprod` (char), `ptxfeecat` (char), `ptxfeeduration` (char), `ptxfeenodays` (inte), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `exclmdd` (char), `vendprodgrouptype` (char), `vendprodgroupref` (char), `vendprodgroupsubref` (char), `jmdescrip` (char), `jmunit` (char), `jmspeccostty` (char), `jmcsunperstk` (deci-6), `jmprccostper` (char), `cconlyfl` (logi) [m], `wordindexfl` (logi) [m], `extdescrip` (char), `rulesettings` (char), `rowpointer` (char) [i], `categorylist` (char), `reporttovendorfl` (logi) [m], `securitysettings` (char), `vendno` (int6), `edistkprccd` (char), `shipfmno` (inte), `edistkprcadj` (deci-5), `prodcat` (char), `prodline` (char), `unavailtype` (char), `pricetype` (char), `intracountrycd` (char), `intraeslrptfl` (logi) [m], `usesuppunitsfl` (logi) [m], `billacctcd` (char), `dnbiinterfacefl` (logi) [m], `dnbicredlim` (deci-0), `esbactioncode` (char), `reqinvcrfl` (logi) [m], `creditrebillfl` (logi) [m], `crserialfl` (logi) [m], `crrebatesfl` (logi) [m], `transdttmz` (datetm-tz) [i], `divno` (inte), `cndimdivisor` (inte), `cnpkgtyusedcd` (char), `cnstndpkgtyfl` (logi) [m]

### `sastae`
**System Admin Tables, Extended Data**
Fields: `cono` (inte) [i], `codeiden` (char) [im], `codeval` (char) [im], `codedata` (char) [i], `operinit` (char), `transdt` (date), `transproc` (char), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `codedata2` (char)

### `sastaz`
**Custom Table Values**
Fields: `cono` (inte) [i], `codeiden` (char) [im], `primarykey` (char) [i], `secondarykey` (char) [i], `codeval` (char[16]) [m], `labelfl` (logi) [i], `transproc` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `rowpointer` (char) [i]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `codeiden` (Table identifier) — Table; Valid values/xref: SASTAZ label record; Required
- `primarykey` (Primary Key) — Unique Record Identifier; Valid values/xref: SASTAZ label record; Required
- `seconardykey` (Secondary Key) — Unique Record Identifier; Valid values/xref: SASTAZ label record
- `user5` (user5) — Used for Conversion Import ID

### `sastc`
**Currency Tables**
Fields: `currencyty` (char) [i], `shortdesc` (char), `descrip` (char), `bankno` (inte), `draftfl` (logi) [m], `vouchexrate` (deci-7), `purchexrate` (deci-7), `gldivno` (inte), `gldeptno` (inte), `glacctno` (inte), `glsubno` (inte), `operinit` (char), `transdt` (date), `transtm` (char), `decimalfl` (logi) [m], `cono` (inte) [i], `edicurrency` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `salesexrate` (deci-7), `arexrate` (deci-7), `wtinvexrate` (deci-7[2]), `wtexpaddexrate` (deci-7[2]), `wtcapaddexrate` (deci-7[2]), `glexrate` (deci-7[2]), `icexrate` (deci-7[2]), `budgetexrate` (deci-7), `stndcurrcd` (char), `currsymbol` (char), `rvglacctno` (inte), `rvgldeptno` (inte), `rvgldivno` (inte), `rvglexchrate` (deci-7), `rvglsubno` (inte)

### `sastch`
**Currency History**
Fields: `changedt` (date) [im], `changent` (char), `changety` (char) [im], `cono` (inte) [im], `currencyty` (char) [im], `draftfl` (logi) [m], `edicurrency` (char), `glacctno` (inte), `gldeptno` (inte), `gldivno` (inte), `glsubno` (inte), `newexrate` (deci-7), `oldexrate` (deci-7), `operinit` (char), `ratesource` (char), `rvglacctno` (inte), `rvgldeptno` (inte), `rvgldivno` (inte), `rvglsubno` (inte), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `glexrate` (deci-7), `changetm` (char) [i], `transproc` (char), `changedttz` (datetm-tz)

### `sastf`
**System Admin Table, Frt Account**
Fields: `cono` (inte) [im], `billlevelcd` (char) [im], `srcrowpointer` (char) [im], `carrierid` (char) [im], `billaccount` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `billlevelcd` (Bill Level) — (A)ll, (W)arehouse, (C)ustomer or (S)hipto; Valid values/xref: A, W, C or S; Required
- `whse` (Warehouse) — Can be CHAR(24) if using xref; Valid values/xref: ICSD
- `carrierid` (Carrier ID) — Uses the first 3 char of Ship Via, see Note Below; Valid values/xref: SASTT-S (3 char)
- `shipvia` (Ship via) — Can be CHAR(24) if using xref, see Note Below; Valid values/xref: SASTT-S
- `user5` (user5) — Used for Conversion Import ID
- `custno` (Customer #) — Can be CHAR(24) if using xref; Valid values/xref: ARSC
- `shipto` (Shipto) — Valid values/xref: ARSS

### `sastn`
**System Admin Tables, Numeric**
Fields: `cono` (inte) [i], `codeiden` (char) [im], `codeval` (inte) [im], `descrip` (char) [i], `addtaxfl` (logi) [m], `addontype` (logi) [m], `operinit` (char), `transdt` (date), `transtm` (char), `addonamt` (deci-2), `gldivno` (inte), `gldeptno` (inte), `ediaddoncd` (char), `glacctno` (inte), `frghtcalcty` (char), `glsubno` (inte), `refundtype` (inte), `fedtaxid` (char), `addr` (char[2]), `ccaddontype` (logi) [m], `name` (char) [m], `user1` (char), `city` (char), `user2` (char), `state` (char), `user3` (char), `zipcd` (char), `user4` (char), `addonmin` (deci-2), `user5` (char), `addonzero` (deci-2), `user6` (deci-5), `taxgroup` (inte), `user7` (deci-5), `gldivno2` (inte), `user8` (date), `gldeptno2` (inte), `user9` (date), `glacctno2` (inte), `glsubno2` (inte), `cctendfl` (logi) [m], `processor` (char), `ccaddon` (deci-2), `cccustnm` (char), `authmin` (deci-2), `chgcat` (char), `ccedit` (inte), `boappdays` (inte), `chkauthty` (char), `arpost` (logi) [m], `preauthppt` (logi) [m], `catppt` (logi) [m], `ccidppt` (logi) [m], `addveri` (logi) [m], `chkauth` (logi) [m], `transproc` (char), `bankno` (inte), `currencyty` (char), `addr3` (char), `glimpactfl` (logi) [m], `frtaddonfl` (logi) [m], `merchantid` (char), `addonmax` (deci-2), `tiedoeaddonno` (inte), `ehffl` (logi) [m], `divnogroup` (char), `rowpointer` (char) [i], `giftcardfl` (logi) [m], `allowreloadgiftfl` (logi) [m]

### `sastp`
**Credit Card Processor Master File**
Fields: `cono` (inte) [i], `processno` (inte) [i], `name` (char), `prefix` (char), `tempsfx` (char), `reqsfx` (char), `anssfx` (char), `bkusfx` (char), `directory` (char), `unixrun` (char), `delay` (inte), `timeout` (inte), `prauthcd` (char), `salecd` (char), `forcecd` (char), `retncd` (char), `setlcd` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `webauthfl` (logi) [m], `numusers` (inte), `lastuser` (inte), `chkdlcd` (char), `chkactcd` (char), `chkothcd` (char), `transproc` (char), `purlevelno` (inte), `ipaddress` (char), `portnum` (char), `processortype` (char), `processorhostsite` (char), `processorhostport` (char), `processorpartnerid` (char), `processorvendorid` (char), `processoruserid` (char), `processoruserpw` (char), `flatfileencrypt` (logi) [m], `callingURL` (char), `responseURL` (char), `callingURLH5` (char), `responseURLH5` (char)

### `sastpd`
**System Administration Setup Third Party Devices**
Fields: `deviceid` (char) [i], `appuserid` (char) [i], `appname` (char) [i], `descrip` (char), `statusfl` (logi) [i], `lastuseddt` (date), `lastusedtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `keyindex` (char), `numtimesused` (inte)

### `sastpl`
**System Administration Setup Third Party Licenses**
Fields: `appname` (char) [i], `apptype` (char), `statusfl` (logi), `secure` (char), `numusers` (inte), `numusertype` (char), `licensedt` (date), `licexpdt` (date), `lastuseddt` (date), `lastusedtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `msgdt` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `descrip` (char) [i], `codeid` (char) [im], `fieldlabel` (char), `fieldtype` (char), `fieldlabel2` (char), `fieldtype2` (char), `desclabel` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `extendedfl` (char), `multlangfl` (char), `codeval2fl` (char), `vendfl` (char), `pricefl` (char), `fieldsize` (char), `descsize` (char), `fieldsize2` (char), `filename` (char), `allowdupdescfl` (char)

### `sasttcodes`
**SASTT Codes**
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `Code ID` (See Below) — See Below; Valid values/xref: See Below; Required
- `Code Value` (See Below) — See Below; Valid values/xref: See Below; Required
- `Description` (See Below) — See Below; Valid values/xref: See Below; Required
- `Optional Data1` (See Below) — See Below; Valid values/xref: See Below
- `Optional Data2` (See Below) — See Below; Valid values/xref: See Below
- `Optional Data3` (See Below) — See Below Available Starting 10.0; Valid values/xref: See Below
- `user5` (user5) — Used for Conversion Import ID
- `Table Description` (Setup Function) — SX.E Table
- `OE Addons` (SASTO) — SASTN
- `CAM Activity Codes` (SASTT) — SASTA
- `CAM Result Codes` (SASTT) — SASTA
- `CAM Contact Method` (SASTT) — SASTA
- `CAM Contact Type` (SASTT) — SASTA
- `Report Schedules` (SASTT) — SASTA
- `Return Reasons` (SASTT) — SASTA
- `Payment Types` (SASTT) — SASTN
- `Order Origin Codes (10.2.0)` (SASTT) — SASTA
- `Terms` (SASTT) — SASTA
- `Divisions` (SASTT) — SASTN
- `PO Addons` (SASTT) — SASTN
- `Tax Override` (SASTA) — CHAR(2)
- `Alternate Product Group` (SASTA) — CHAR(8); Valid values/xref: Report to Supplier: Y or N
- `Buyer` (SASTA) — CHAR(4); Valid values/xref: Central Whse, CHAR(4)
- `Brand Code (v6.1.060)` (SASTA) — CHAR(6)
- `Product Category` (SASTA) — CHAR(4); Valid values/xref: Exclude from E-sales: Y or N
- `Intrastat Commodity Code (V6.1.080)` (SASTA) — CHAR(8); Valid values/xref: Use Supp Units Flag: Y or N
- `Storefront Corporate Groups (v6.1.060)` (SASTA) — CHAR(10)
- `Package Type` (SASTA) — CHAR(8); Valid values/xref: Package Type Used for Carton ID: CHAR(2)
- `Customer Rebate Type` (PDST) — CHAR(8)
- `Customer Type` (SASTA) — CHAR(3)
- `Department` (SASTN) — INT(4)
- `Lost Business Reason` (SASTA) — CHAR(2); Valid values/xref: Record Usage: Y or N
- `ECCN Classification Code (v10.0)` (SASTA) — CHAR(15)
- `Frozen Reason` (SASTA) — CHAR(1)
- `Freight Consolidation` (SASTA) — CHAR(8)
- `Freight Terms Code` (SASTA) — CHAR(10); Valid values/xref: Bill Account: (D)istributor or <blank>
- `G/L Report Groups` (SASTA) — CHAR(4); Valid values/xref: Subtotal, Y or N
- `Family Group` (SASTA) — CHAR(2)
- `Ion GL Account Conversion 
(10.3.1)` (SASTA) — CHAR(32)
- `Ion Unit Conversion
(10.3.1)` (SASTA) — CHAR(4)
- `Customer Price Type` (SASTA) — CHAR(4)
- `Product Price Type` (SASTA) — CHAR(4); Valid values/xref: Margin Min DEC(6,2)
- `Reason Unavailable` (SASTA) — CHAR(2); Valid values/xref: EDI Reason, CHAR(2)
- `Non-Tax Reason` (SASTA) — CHAR(2)
- `Note Category` (SASTA) — CHAR(6); Valid values/xref: Restricted Flag: Y or N
- `Usage Override Reason` (SASTA) — CHAR(2)
- `Product Preference (10.1.0.0)` (SASTA) — CHAR(8); Valid values/xref: Priority INT(2) 0 thru 99
- `Product Rebate Type` (PDST) — CHAR(8); Valid values/xref: Vendor # INT(12) (v10.3.1)
- `LIFO Category` (SASTA) — CHAR(4)
- `Reference` (SASTA) — INT(4)
- `Pricing/Rebate Region (10.1.1.0)` (SASTA) — CHAR(4)
- `Ship Via` (SASTA) — CHAR(4)
- `Product Rebate SubType` (PDST) — CHAR(8); Valid values/xref: Vendor # INT(12)
- `Transportation Standard Carrier` (SASTA) — CHAR(4); Valid values/xref: Dimensional Weight Divisor INT(3)
- `Intrastat Terms of Delivery (V6.1.080)` (SASTN) — INT(2)
- `Product Tier (10.1.0.0)` (SASTA) — CHAR(8)
- `Unit Conversion` (SASTA) — CHAR(4); Valid values/xref: EDI Unit, CHAR(2)
- `Vendor Type` (SASTA) — CHAR(3)
- `Country` (SASTA) — CHAR(2); Valid values/xref: Intrastat Country Code CHAR(2) (V6.1.080)
- `WM Bin type` (WMST) — CHAR(6)
- `WM Size type` (WMST) — CHAR(6)
- `Language` (SASTA) — CHAR(2)
- `Territory` (SASTA) — CHAR(4)

### `sasz`
**Freight Zones by Zip Code**
Fields: `cono` (inte) [i], `whse` (char) [im], `shipvia` (char) [i], `begdestzip` (char) [i], `enddestzip` (char) [i], `zone` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transcd` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `co_num` (char) [im], `wh_num` (char) [im], `sc_type` (char) [im], `sc_table` (char) [im], `sc_id` (char) [im], `sc_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `seq_control`
**Sequence Order Drop Types by Warehouse, Carrier, Product group, etc**

### `serial`
**Track serial numbers for items that have the serial id flag set**
Fields: `co_num` (char) [i], `wh_num` (char) [im], `abs_num` (char) [im], `serial_num` (char) [i], `bin_num` (char) [im], `date_time` (char), `adjust_type` (char) [i], `cycle_flag` (logi) [m], `cycle_level` (char), `cycle_emp_num` (char), `cycle_id` (inte) [i], `pallet_id` (char) [i], `order` (char) [m], `order_suffix` (char), `order_line` (inte) [m], `order_line_sequence` (inte), `po_number` (char), `po_suffix` (char), `po_line` (inte), `po_line_sequence` (inte), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [im], `order` (char) [im], `order_suffix` (char) [i], `type` (char), `line` (inte) [im], `line_sequence` (inte) [i], `abs_num` (char) [im], `serial_num` (char) [i], `rma` (char) [i], `pick_id` (inte), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `cono` (inte) [im], `groupid` (char) [im], `custno` (deci-0) [im], `operinit` (char), `transdt` (date), `transproc` (char), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `wh_num` (Warehouse) — Can be CHAR(24) if Using Whse Cross Reference; Valid values/xref: ICSD, TWL-WHMST; Required
- `bin_num` (Location ID) — Do not include dashes or slashes; Valid values/xref: TWL-BINMST; Required
- `abs_num` (Item Number) — Can use Product Cross Reference; Valid values/xref: ICSW, TWL-ITEM, TWL-INVENTORY; Required
- `serial_num` (Serial Number) — Valid values/xref: ICSES; Required
- `custom_data5` (Custom User Field 5) — Used for Import ID

### `serial_history`
**Cross-reference of serial numbers to order detail**

### `sfcorpgrp`
**Storefront AR Corporate Group**

### `shfmst`
**Contains all shifts**
Fields: `co_num` (char) [i], `wh_num` (char) [im], `shf_num` (inte) [im], `time_start` (char), `time_end` (char), `shf_desc` (char), `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `shpdtl`
**Shipping Detail Table used for generation of shipping manifests**
Fields: `manifest_id` (inte) [im], `pro_num_id` (char), `invoice_num` (char), `tracking_id` (char) [i], `void` (logi), `package_type` (char), `consignee_name` (char), `addr` (char[2]), `city` (char), `state` (char), `zip` (char), `zone` (inte), `weight` (deci-2), `actual_weight` (deci-2), `residential_flag` (logi), `charges` (deci-2), `cod_amt` (deci-2), `declared_value` (deci-2), `ups_ground_track` (logi), `add_on_handling` (logi), `add_on_cost` (deci-2), `call_tag_issued` (logi), `oversized` (logi) [m], `shp_by_irms` (logi), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `route` (char), `ship_cust_code` (char), `addr_ext` (char[3]), `trans_datetz` (datetm-tz)

### `shpmst`
**Table used for generation of shipping manifests**
Fields: `manifest_id` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `dock_id` (char) [i], `carrier_id` (char) [im], `trailer_num` (char) [i], `manifest_num` (inte), `date_time` (char) [i], `custom_data` (char[5]), `row_status` (logi) [im], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz)

### `sled`
**Supplier Link Edit/Detail History**
Fields: `baseprice` (deci-5), `cono` (inte) [i], `cubes` (deci-5), `descrip` (char[2]), `icscfl` (logi) [m], `icspfl` (logi) [m], `icswfl` (logi) [m], `imptype` (char) [i], `listprice` (deci-5), `lookupnm` (char), `notesfl` (char), `operinit` (char), `priceonty` (char), `pricetype` (char), `prod` (char) [im], `prodcat` (char), `prodline` (char), `replcost` (deci-5), `seqno` (inte), `slaltprod` (char), `slcat` (char), `slcost` (deci-5), `slcsunperstk` (deci-6), `slcurrencyty` (char), `sldescrip` (char[2]), `sleditfl` (logi) [m], `slexchgrate` (deci-7[2]), `slgroup` (char), `sllinecd` (char), `sllist` (deci-5), `slmsdsfl` (logi) [m], `slmsdssheetno` (char), `sloriginty` (char), `slpbseqno` (inte) [i], `slprccostper` (char), `slproduct` (char), `slspeccostty` (char), `slunit` (char), `slupdtno` (char) [i], `slupdttype` (char), `slvendcd` (char), `slxref1` (char), `slxref2` (char), `statuscd` (char) [i], `statustype` (logi) [im], `stndcost` (deci-5), `termspct` (deci-2), `transdt` (date), `transtm` (char), `unitstock` (char), `user1` (char), `user2` (char), `whse` (char) [i], `weight` (deci-5), `slsupersede` (char), `effectdt` (date), `slcostbrk` (deci-5[9]), `slpricebrk` (deci-5[9]), `slqtybrk` (inte[8]), `slxref3` (char), `slxref4` (char), `user3` (char), `user4` (char), `user5` (char), `vendno` (deci-0) [m], `idwdatapos` (char), `slunspsc` (char), `rebsubty` (char), `rebatety` (char), `errorcd` (char), `holdcd` (char), `slprceffdt` (date), `slprcexpdt` (date), `lastcostfor` (deci-5), `rebatecost` (deci-5), `pdscfl` (logi) [m], `pdsvfl` (logi) [m], `transproc` (char), `unitstnd` (char), `unitconv` (deci-5), `keyindex` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `descrip3` (char), `sldescrip3` (char), `effectdttz` (datetm-tz), `replcostfor` (deci-5)

### `sledn`
**Supplier Link Part Number Change File**
Fields: `cono` (inte) [i], `imptype` (char) [i], `slupdtno` (char) [i], `newpartno` (char) [im], `oldpartno` (char) [m], `prod` (char) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char)

### `sledv`
**UPC Numbers for Supplier Link Products**
Fields: `cono` (inte) [i], `imptype` (char) [i], `slupdtno` (char) [i], `prod` (char) [im], `whse` (char) [i], `section1` (deci-0), `section2` (deci-0), `section3` (deci-0), `section4` (deci-0), `section5` (deci-0), `section6` (deci-0), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `slunspsc` (char), `transproc` (char)

### `sleh`
**Supplier Link History**
Fields: `amountcr` (deci-2), `amountdr` (deci-2), `imptype` (char) [i], `issuedt` (date), `jrnlno` (inte) [i], `noadded` (inte), `nochanged` (inte), `nodecreases` (inte), `nodeleted` (inte), `nodiscontinued` (inte), `noerrors` (inte), `noincreases` (inte), `noreviews` (inte), `norevisions` (inte), `nounlisted` (inte), `operinit` (char), `percal` (inte), `perfisc` (inte), `slupdtno` (char) [i], `readdt` (date), `transdt` (date), `transtm` (char), `updatedt` (date), `cono` (inte) [i], `reportdt` (date), `seqno` (inte) [i], `statustype` (logi) [im], `setno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `issuedttz` (datetm-tz), `readdttz` (datetm-tz), `reportdttz` (datetm-tz), `updatedttz` (datetm-tz), `percaltz` (datetm-tz), `perfisctz` (datetm-tz)

### `slsi`
**Supplier Link Setup Import**
Fields: `decimalpos` (inte), `sldelim` (char), `filetype` (char), `importproc` (char), `impdescrip` (char), `imptype` (char) [i], `lastupdatedt` (date), `lastupdateno` (char), `operinit` (char), `transdt` (date), `transtm` (char), `bvendcd` (inte), `lvendcd` (inte), `blinecd` (inte), `bprod` (inte), `bdescrip1` (inte), `bdescrip2` (inte), `bunit` (inte), `bweight` (inte), `bcubes` (inte), `bdiscount` (inte), `bsupersede` (inte), `blist` (inte), `bnotes` (inte), `bmsdsno` (inte), `bcrossref1` (inte), `bcrossref2` (inte), `bcrossref3` (inte), `bcrossref4` (inte), `bupcpno4` (inte), `buser1` (inte), `buser2` (inte), `bfree1` (inte), `bfree2` (inte), `bfree3` (inte), `llinecd` (inte), `lprod` (inte), `ldescrip1` (inte), `ldescrip2` (inte), `lunit` (inte), `lweight` (inte), `lcubes` (inte), `ldiscount` (inte), `lsupersede` (inte), `llist` (inte), `lnotes` (inte), `lmsdsno` (inte), `lcrossref1` (inte), `lcrossref2` (inte), `lcrossref3` (inte), `lcrossref4` (inte), `lupcpno4` (inte), `lfree1` (inte), `lfree2` (inte), `lfree3` (inte), `luser1` (inte), `luser2` (inte), `bcostbrk` (inte[9]), `lcostbrk` (inte[9]), `bpricebrk` (inte[9]), `lpricebrk` (inte[9]), `bqtybrk` (inte[8]), `lqtybrk` (inte[8]), `buser3` (inte), `buser4` (inte), `buser5` (inte), `luser3` (inte), `luser4` (inte), `luser5` (inte), `bvendate` (inte), `lvendate` (inte), `transfersh` (char), `bcost` (inte), `lcost` (inte), `slrecno` (deci-0), `bmsdsfl` (inte), `lmsdsfl` (inte), `idwdatapos` (char), `filesubtype` (char), `supersedefl` (logi) [m], `naedlength` (inte), `bupcpno1` (inte), `bupcpno2` (inte), `bupcpno3` (inte), `bupcpno5` (inte), `bupcpno6` (inte), `lupcpno1` (inte), `lupcpno2` (inte), `lupcpno3` (inte), `lupcpno5` (inte), `lupcpno6` (inte), `bprcdisc` (inte[9]), `lprcdisc` (inte[9]), `custno` (deci-0) [m], `vendno` (deci-0) [m], `pdscrefer` (char), `pdsvrefer` (char), `pdscjobno` (char), `pdscenddt` (date), `pdsvenddt` (date), `pdscstartdt` (date), `pdsvstartdt` (date), `pdsccommtype` (char), `pdscminqty` (deci-2), `pdscmaxqty` (deci-2), `pdscactqty` (deci-2), `pdscqtybreakty` (char), `pdscpriceonty` (char), `pdsvbuytype` (char), `datefrmt` (char) [m], `bspcunit` (inte), `lspcunit` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `bwhse` (inte), `lwhse` (inte), `brebsubty` (inte), `lrebsubty` (inte), `brebatety` (inte), `lrebatety` (inte), `brebatecost` (inte), `lrebatecost` (inte), `transproc` (char), `bunitstnd` (inte), `lunitstnd` (inte), `bunitmult` (inte), `lunitmult` (inte), `sorttype` (char), `bdescrip3` (inte), `ldescrip3` (inte), `lastupdatedttz` (datetm-tz)

### `slsn`
**Supplier Link Setup New Item Defaults**
Fields: `charactionty` (char[6]), `charfind` (char[6]), `charfieldty` (char[6]), `charrepl` (char[6]), `cono` (inte) [i], `descrip2txt` (char), `descrip2cd` (char), `icscfl` (logi) [m], `icspfl` (logi) [m], `icswfl` (logi) [m], `imptype` (char) [i], `linecd` (char) [i], `operinit` (char), `priceonty` (char), `pricetype` (char), `prodcat` (char), `prodline` (char) [m], `prodpreffl` (logi) [m], `prodprefix` (char), `prodsuffl` (logi) [m], `prodsuffix` (char), `slgroup` (char), `transdt` (date), `transtm` (char), `vendcd` (char) [i], `vendno` (deci-0) [im], `descrip1cd` (char), `descrip1txt` (char), `lookupcd` (char), `lookuptxt` (char), `pgrpty` (char), `pdspsty` (char), `pdsvty` (char), `pdscfl` (logi) [m], `pcatlinecdfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `rebatety` (char), `rebsubty` (char), `transproc` (char), `descrip3txt` (char), `descrip3cd` (char)

### `slsp`
**Supplier Link Setup Price/Cost Multipliers**
Fields: `barcodecd` (char), `cprcdisc` (deci-3[9]), `cono` (inte) [i], `cpexactrnd` (deci-2[9]), `cpricecd` (char[9]), `cpricemt` (deci-5[9]), `cpround` (char[9]), `cptarget` (inte[9]), `cqtybrk` (inte[8]), `deletecd` (char), `discountcd` (char), `imptype` (char) [i], `msdscd` (char), `operinit` (char), `prodcd` (char), `prodlinecd` (char), `qtybrkcd` (char), `slgroup` (char) [i], `supercd` (char), `transdt` (date), `transtm` (char), `upccd` (char), `updatecd` (char), `vcd` (char), `vdisc` (deci-3[9]), `vactivedays` (inte), `vpexactrnd` (deci-2[9]), `vpricecd` (char[9]), `vpround` (char[9]), `vptarget` (inte[9]), `vqtybrk` (inte[8]), `vbuytype` (char), `weightcd` (char), `whse` (char) [i], `interchgcd` (char), `unitcd` (char), `descripcd` (char[2]), `ccd` (char), `cactivedays` (inte), `cqtybreakty` (char), `vpricemt` (deci-5[9]), `notety` (char), `notereqfl` (logi) [m], `notepg` (inte), `cqtybrkfl` (logi) [m], `vqtybrkfl` (logi) [m], `vendpartcd` (char), `noteupdtcd` (char), `cenddt` (date), `venddt` (date), `caddon` (deci-5[9]), `vaddon` (deci-5[9]), `rptpricecd` (char[7]), `rptdeclim` (inte[7]), `rptinclim` (inte[7]), `autopricecd` (char), `detailcd` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `addon` (deci-5[5]), `calccd` (char[5]), `calcorder` (inte[5]), `holddeclim` (inte[5]), `holdinclim` (inte[5]), `pexactrnd` (deci-2[5]), `pricemult` (deci-5[5]), `ptarget` (inte[5]), `pround` (char[5]), `holdzerofl` (logi[5]) [m], `descrip3cd` (char), `addonfr` (deci-5), `calccdfr` (char), `calcorderfr` (inte), `holddeclimfr` (inte), `holdinclimfr` (inte), `holdzerofrfl` (logi) [m], `pexactrndfr` (deci-2), `pricemultfr` (deci-5), `proundfr` (char), `ptargetfr` (inte)

### `slst`
**Supplier Link Setup Table**
Fields: `codeiden` (char) [im], `codeval` (char) [im], `cono` (inte) [i], `csunperstk` (deci-8), `descrip` (char) [i], `imptype` (char), `operinit` (char), `prccostper` (char), `speccostty` (char), `transdt` (date), `transtm` (char), `unitediuom` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `unitfl` (logi) [m]

### `smsc`
**SM Customer History**
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [i], `yr` (inte) [i], `noinvbill` (inte), `nolinebill` (inte), `qtysold` (deci-2[13]), `salesamt` (deci-2[13]), `discamt` (deci-2[13]), `transdt` (date), `transtm` (char), `operinit` (char), `cogamt` (deci-2[13]), `budgetamt` (deci-2[13]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `yrtz` (datetm-tz)

### `smseh`
**SM Sales History**
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [i], `prod` (char) [im], `lastpurdt` (date) [i], `msdssentdt` (date), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `lastpurdttz` (datetm-tz), `msdssentdttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `custno` (Customer) — Can be CHAR(24) if using the Xref.; Valid values/xref: ARSC; Required
- `shipto` (Shipto) — Valid values/xref: ARSS
- `prod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `user5` (user5) — Used for Conversion Import ID

### `smsep`
**Sales by Customer by Category**
Fields: `cono` (inte) [i], `yr` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `prodcat` (char) [i], `whse` (char) [i], `salesamt` (deci-2[12]), `discamt` (deci-2[12]), `qtysold` (deci-2[12]), `cogamt` (deci-2[12]), `operinit` (char), `transdt` (date), `transtm` (char), `nolinebill` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `yrtz` (datetm-tz)

### `smsew`
**SM Customer by Product**
Fields: `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `prod` (char) [i], `whse` (char) [i], `yr` (inte) [i], `salesamt` (deci-2[12]), `qtysold` (deci-2[12]), `cogamt` (deci-2[12]), `discamt` (deci-2[12]), `lastpurdt` (date), `lastpurqty` (deci-2), `lastprice` (deci-5), `unit` (char), `operinit` (char), `transdt` (date), `transtm` (char), `nolinebill` (inte), `stockfl` (logi) [im], `componentfl` (logi) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `lastpurdttz` (datetm-tz), `yrtz` (datetm-tz)

### `smsm`
**Sales Manager Commission Setup**
Fields: `cono` (inte) [i], `commtype` (char) [i], `slsrep` (char) [i], `targettype` (char), `interval` (char), `commbasedon` (char), `lastupddt` (date), `saleamt` (deci-2[3]), `commamt` (deci-2[3]), `transdt` (date), `transtm` (char), `operinit` (char), `refer` (char), `steprate` (logi) [m], `targetamt` (deci-2[49]), `commpctin` (deci-2[50]), `commpctout` (deci-2[50]), `commpctouto` (deci-2[50]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `lastupddttz` (datetm-tz)

### `smsn`
**Sales Rep Setup**
**Operators call this:** "Sales Rep Code" (Accounts Receivable), "Sales Rep Name" (Accounts Receivable), "Sales Rep Code" (Sales), "Sales Rep Name" (Sales)
Fields: `cono` (inte) [i], `slsrep` (char) [i], `name` (char) [im], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `phoneno` (char), `slstype` (char), `operinit` (char), `oper2` (char), `transdt` (date), `email` (char), `transtm` (char), `autocmfl` (logi) [m], `synccrmfl` (logi) [m], `user1` (char), `mgr` (char), `user2` (char), `slstitle` (char), `user3` (char), `user4` (char), `letterdir` (char), `user5` (char), `lettercd` (char[6]) [m], `user6` (deci-5), `commtype` (char), `user7` (deci-5), `site` (char), `user8` (date), `securefl` (logi) [m], `user9` (date), `sysname` (char), `beglastdt` (date), `endlastdt` (date), `modphoneno` (char), `commfl` (logi) [m], `phonesuf` (char), `begprosno` (deci-0) [m], `endprosno` (deci-0) [m], `transproc` (char), `laborprod` (char), `listprice` (deci-5), `addr3` (char), `geocd` (inte), `countrycd` (char), `outofcityfl` (logi) [m], `rowpointer` (char) [i], `wordindexfl` (logi) [m], `esbactioncode` (char), `transdttmz` (datetm-tz) [i], `beglastdttz` (datetm-tz), `endlastdttz` (datetm-tz), `divno` (inte), `addressoverfl` (logi) [m]
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `slsrep` (Salesrep) — Can be CHAR(24) if using xref; Required
- `addr3` (Address) — Available for all companies starting in 6.1.040. Only accessible for Int'l companies in versions 4.2.002 - 6.1.030.
- `city` (City) — Length 20 prior to 6.1.040
- `state` (State) — Not used with Freeform Style Address AO option starting in 6.1.040.
- `countrycd` (Country Code) — Valid values/xref: SASTT-W
- `phoneno` (Phone) — Enter number with no spaces or punctuation
- `mgr` (Manager) — Valid values/xref: SMSN
- `commfl` (Pay Commission) — Yes or No; Valid values/xref: Y, N; Default: Y
- `commtype` (Commission) — Setup in OESC; Valid values/xref: SMSM
- `phonesuf` (Phone Suffix) — Enter number with no spaces or punctuation
- `modphoneno` (Modem Phone) — Enter number with no spaces or punctuation
- `oper2` (Operator) — Available Starting 4.0; Valid values/xref: SASO
- `synccrmfl` (Sync To CRM) — Yes or No. Available Starting 4.1; Valid values/xref: Y, N; Default: Y
- `geocd` (Geo Code) — Used only with TaxWare Available starting in 6.1.060
- `outofcityfl` (Outside City Limits Flag) — Used only with TaxWare Enterprise Available starting in 6.1.061; Valid values/xref: Y, N; Default: N
- `securefl` (Open Security) — Yes or No; Valid values/xref: Y, N; Default: Y
- `laborprod` (Labor Product) — Used with Service Warranty Module. Available Starting 4.1; Valid values/xref: ICSP
- `listprice` (List Price) — Used with Service Warranty Module. Available Starting 4.1
- `user5` (User 5) — Used for Conversion Import ID

### `smsp`
**SM Product Category**
Fields: `cono` (inte) [i], `prodcat` (char) [i], `yr` (inte) [i], `nolinebill` (inte), `qtysold` (deci-2[13]), `salesamt` (deci-2[13]), `discamt` (deci-2[13]), `cogamt` (deci-2[13]), `transdt` (date), `transtm` (char), `operinit` (char), `budgetamt` (deci-2[13]), `whse` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `yrtz` (datetm-tz)

### `smss`
**SM Salesrep History**
Fields: `cono` (inte) [i], `slsrep` (char) [i], `yr` (inte) [i], `nolinebill` (inte), `qtysold` (deci-2[13]), `salesamt` (deci-2[13]), `discamt` (deci-2[13]), `cogamt` (deci-2[13]), `transdt` (date), `transtm` (char), `operinit` (char), `slsreptype` (logi) [im], `quotaamt` (deci-2[12]), `commamt` (deci-2[12]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `yrtz` (datetm-tz)

### `smsv`
**SM Vendor History**
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `yr` (inte) [i], `noinvbill` (inte), `nolinebill` (inte), `qtysold` (deci-2[13]), `salesamt` (deci-2[13]), `discamt` (deci-2[13]), `transdt` (date), `transtm` (char), `operinit` (char), `cogamt` (deci-2[13]), `budgetamt` (deci-2[13]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `yrtz` (datetm-tz)

### `smsvp`
**Sales by Vendor by Category**
Fields: `cono` (inte) [i], `yr` (inte) [i], `vendno` (deci-0) [im], `prodcat` (char) [i], `whse` (char) [i], `salesamt` (deci-2[12]), `discamt` (deci-2[12]), `qtysold` (deci-2[12]), `cogamt` (deci-2[12]), `operinit` (char), `transdt` (date), `transtm` (char), `nolinebill` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `yrtz` (datetm-tz)

### `smsvw`
**SM Vendor by Product**
Fields: `cono` (inte) [i], `vendno` (deci-0) [im], `prod` (char) [i], `whse` (char) [i], `yr` (inte) [i], `salesamt` (deci-2[12]), `qtysold` (deci-2[12]), `cogamt` (deci-2[12]), `discamt` (deci-2[12]), `lastpurdt` (date), `lastpurqty` (deci-2), `lastprice` (deci-5), `unit` (char), `operinit` (char), `transdt` (date), `transtm` (char), `nolinebill` (inte), `stockfl` (logi) [im], `componentfl` (logi) [im], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `lastpurdttz` (datetm-tz), `yrtz` (datetm-tz)

### `smsw`
**SM Warehouse Product**
Fields: `cono` (inte) [i], `prod` (char) [im], `whse` (char) [i], `yr` (inte) [i], `stockfl` (logi) [im], `nolinebill` (inte), `qtylost` (deci-2[13]), `salesamt` (deci-2[13]), `cogamt` (deci-2[13]), `transdt` (date), `transtm` (char), `operinit` (char), `discamt` (deci-2[13]), `qtysold` (deci-2[13]), `componentfl` (logi) [im], `budgetamt` (deci-2[13]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `yrtz` (datetm-tz)

### `stgmst`
Fields: `co_num` (char) [i], `wh_num` (char) [im], `container_id` (char) [i], `order` (char) [im], `order_suffix` (char) [i], `bin_num` (char) [im], `emp_num` (char), `date_time` (char), `container_type` (char) [m], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz)

### `stntbl`
**Data about all RF stations + console**
Fields: `co_num` (char) [i], `row_status` (logi) [m], `wh_num` (char) [im], `stn_num` (char) [im], `stn_type` (char) [m], `label_printer` (char) [m], `label_queue` (char) [m], `line_printer` (char) [m], `line_queue` (char) [m], `last_pid` (inte) [m], `last_activation` (char), `last_emp_num` (char) [m], `last_login` (char), `last_logout` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `last_activationtz` (datetm-tz), `last_logintz` (datetm-tz), `last_logouttz` (datetm-tz), `trans_datetz` (datetm-tz), `id` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `task_id` (inte) [i], `machine` (char), `pallet_id` (char), `abs_num` (char) [im], `lot` (char), `quantity` (deci-2), `bin_from` (char) [im], `bin_to` (char) [im], `zone_to` (char), `to_wh_num` (char) [m], `urgent` (logi), `movement_type` (char) [m], `prod_id` (inte), `prod_line` (inte), `batch` (inte) [i], `wh_zone` (char) [m], `dept_num` (inte) [m], `truck_id` (char) [i], `date_time` (char), `custom_data` (char[5]), `row_status` (char) [im], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `rowpointer` (char) [im], `cono` (inte) [im], `orderno` (inte) [im], `ordersuf` (inte) [im], `lineno` (inte) [im], `module` (char), `statustype` (char), `errormessage` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `srcrowpointer` (char) [im], `vendno` (deci-0) [im], `shipprod` (char) [im], `whse` (char) [im], `qtyavail` (deci-2), `stkqtyavail` (deci-2), `unit` (char), `unitconv` (deci-5), `dateavailable` (date), `timeavailable` (char), `vendorlocationid` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `seqno` (inte) [im], `shipfmno` (inte) [im], `interchangeprod` (char), `begintime` (int6), `endtime` (int6), `dateavailabletz` (datetm-tz), `srcrowpointer` (char) [im], `vendno` (deci-0) [im], `shipprod` (char) [im], `whse` (char) [im], `qtyord` (deci-2), `stkqtyord` (deci-2), `unit` (char), `unitconv` (deci-5), `statustype` (char), `errormessage` (char), `recordtype` (char), `altprod` (char) [m], `specnstype` (char), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `suggested_move`
**Table contains movement requests (for replenishments, production scheduling, etc)**

### `supplieraccess`
**Supplier Access Vendors**

### `swao`
**Service Warranty Administrative Options**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `nextorderno` (inte), `nextclaimno` (inte), `setup` (logi) [m], `billtype` (logi) [m], `prodcat` (char) [m], `glacctno` (inte), `gldivno` (inte), `gldeptno` (inte), `glsubno` (inte), `wolimit` (deci-2), `claimtype` (char), `claimform` (char), `jobtype` (char), `reqdays` (inte), `promdays` (inte), `reldate` (date), `origcustfl` (logi) [m], `prtfrmt` (inte), `repairheadfl` (logi) [m], `bomtype` (char), `dtratemult` (deci-3), `transproc` (char), `otratemult` (deci-3), `prcyclebegdy` (char), `prcyclebegtm` (char), `prfiledir` (char), `prfilefrmt` (inte), `probationdys` (inte), `rqrsrofl` (char), `overtendfl` (logi) [m]

### `swapet`
**Service Warranty - Shadow file for APET**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `jrnlno` (inte) [i], `setno` (inte) [i], `intclaimno` (inte), `transproc` (char), `cono` (inte) [i], `operinit` (char) [i], `transdt` (date) [i], `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `statustype` (char), `whse` (char) [i], `repairordno` (inte) [i], `ordtype` (logi) [m], `custno` (deci-0), `cancelcd` (char), `roqty` (deci-2), `stagecd` (inte), `repairordsuf` (inte) [i], `orderno` (inte), `ordersuf` (inte), `rolineno` (inte) [i], `roprod` (char), `printfl` (logi) [im], `soprod` (char), `soqty` (deci-2), `solineno` (inte) [i], `delorigin` (char), `transproc` (char)

### `swaudit`
**Service Warranty Delete Audit File**

### `sweh`
**Service Warranty Enter Service Repair Header**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `openinit` (char), `whse` (char) [i], `repairordno` (inte) [i], `ordtype` (logi) [m], `custno` (deci-0) [i], `shipto` (char), `typecd` (char), `pickupfl` (logi) [m], `schdpickupdt` (date) [i], `pickupdt` (date), `pickuptech` (char) [i], `cancelcd` (char), `quotereqfl` (logi) [m], `quoteamt` (deci-2), `prioritycd` (char), `stagecd` (inte) [i], `svcloccd` (char), `contactname` (char), `contactphone` (char), `compdt` (date), `vendno` (deci-0) [m], `statcomment` (char), `schdstartdt` (date), `srttotminutes` (inte), `esttotminutes` (inte), `mstrtickno` (inte), `leadtech` (char) [i], `slsrep` (char), `svcprintdt` (date), `startdt` (date), `repairordsuf` (inte) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `billtype` (logi) [m], `bulletinno` (char) [m], `jobtype` (char), `setupfl` (char), `splitfl` (logi) [m], `printdt` (date), `delivertech` (char) [i], `deliverdt` (date), `deliverfl` (logi) [m], `schddeliverdt` (date) [i], `assigntech` (char), `assigndt` (date), `user10` (date), `user11` (date), `user12` (date), `user13` (date), `user14` (date), `user15` (date), `schdcompdt` (date), `comptech` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `acttotminutes` (inte), `notesfl` (char), `oeprintfl` (logi) [m], `textfl` (logi) [m], `problemtxt` (char), `causetxt` (char), `workperftxt` (char), `transproc` (char), `vehicleid` (char), `canceldt` (date), `swexaddfl` (logi[4]) [m], `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char)

### `sweht`
**Multiple technicians that are assigned to a specific SRO.**
Fields: `cono` (inte) [i], `repairordno` (inte) [i], `repairordsuf` (inte) [i], `tech` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `swej`
**Service Activity**
Fields: `prosno` (deci-0) [m], `leadtech` (char) [i], `workdt` (date) [i], `activitycd` (char), `jobcd` (char), `operinit` (char), `transdt` (date), `transtm` (char), `repairordno` (inte) [i], `comment` (char), `sequenceno` (inte), `billfl` (logi) [m], `elapsedtm` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `repairordsuf` (inte) [i], `cono` (inte) [i], `transproc` (char)

### `swel`
**Service Warranty Enter Detail Lines**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `warrexpdt` (date), `prod` (char) [i], `repairordno` (inte) [i], `serialno` (char), `disposition` (char), `binloc` (char), `totservmin` (deci-2), `dispositioncom` (char), `soldby` (char), `faildt` (date), `howused` (char), `equiptype` (char), `selldt` (date), `lotno` (char), `qty` (deci-2), `compdt` (date), `repairordsuf` (inte) [i], `orderno` (inte), `ordersuf` (inte), `lineno` (inte) [i], `vendno` (deci-0) [m], `jobtype` (char), `unit` (char), `failcd` (char), `probfailcd` (char), `splitfl` (logi) [m], `origorderno` (inte), `origordersuf` (inte), `engineno` (char), `specno` (char), `solineno` (inte), `textfl` (logi) [m], `notesfl` (char), `problemtxt` (char), `causetxt` (char), `workperftxt` (char), `transproc` (char), `vinno` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char)

### `swelj`
**Labor Job Time entries, both active and inactive.  The inactive entries serve as a transaction file for auditability of time entries, and the corresponding changes performed on these entries over time.**
Fields: `activefl` (logi) [im], `closedfl` (logi) [im], `comment` (char), `cono` (inte) [i], `deptno` (inte) [i], `dthrs` (deci-1), `emptype` (char) [i], `endofdayfl` (logi) [m], `errortype` (char[20]), `fromseqno` (inte), `hrstype` (char), `indt` (date) [i], `intjobtype` (char), `intm` (char) [i], `lineno` (inte) [i], `mileage` (inte), `origtech` (char) [i], `othrs` (deci-1), `ourproc` (char), `outdt` (date) [i], `outtm` (char) [i], `overridehrs` (deci-1), `payrollcost` (deci-5), `prsentdt` (date), `rateerrorty` (char[9]), `ratetype` (char[9]), `ratetypefl` (logi[9]) [m], `reasontype` (char), `reghrs` (deci-1), `repairordno` (inte) [i], `repairordsuf` (inte) [i], `schedopttype` (char) [i], `seqno` (inte) [i], `shift` (inte), `statustype` (char) [i], `svcloc` (char), `systemindt` (date) [i], `systemintm` (char) [i], `systemoutdt` (date), `systemouttm` (char), `tech` (char) [i], `tolunchfl` (logi) [m], `tothrs` (deci-1), `transseqno` (inte) [i], `travelhrs` (deci-1), `truckno` (inte), `whse` (char) [i], `writeofffl` (logi) [m], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `billedtm` (char), `solineno` (inte), `transproc` (char)

### `swert`
**Service Warranty Enter Repair Time**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `wkperformdt` (date), `repairordno` (inte) [i], `wkperformedby` (char), `activitycd` (char), `comment` (char), `qty` (deci-2), `repairordsuf` (inte) [i], `lineno` (inte) [i], `prod` (char), `jobtype` (char), `price` (deci-5), `unit` (char), `solineno` (inte), `warrantycd` (char), `invclaimcd` (char), `vendno` (deci-0) [m], `priceoverfl` (logi) [m], `srtqty` (deci-2), `srtoverfl` (logi) [m], `damagecd` (char), `transproc` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `printpricefl` (logi) [m]

### `swewh`
**Service Warranty Enter Warranty Claim Header**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `enginedetail` (char), `selldt` (date), `faildt` (date), `vendno` (deci-0) [im], `repairordno` (inte), `vendclaimno` (char), `claimstage` (inte), `disputefl` (logi) [m], `totclaimamt` (deci-2), `totcreditamt` (deci-2), `printdt` (date), `vendname` (char) [m], `vendaddr` (char[2]), `vendcity` (char), `vendstate` (char), `vendzipcd` (char), `name` (char), `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `recjrnlno` (inte), `subjrnlno` (inte), `orderno` (inte), `ordersuf` (inte), `repairordsuf` (inte), `prod` (char), `serialno` (char), `lotno` (char), `bulletinno` (char) [m], `createdt` (date), `intclaimno` (inte) [i], `prodcat` (char) [m], `failcd` (char), `probfailcd` (char), `qty` (deci-2), `custno` (deci-0), `subsetno` (inte), `recsetno` (inte), `equiptype` (char), `authservno` (char), `woamt` (deci-2), `whse` (char), `claimtype` (char), `manualfl` (logi) [m], `notesfl` (char), `problemtxt` (char), `causetxt` (char), `workperftxt` (char), `textfl` (logi) [m], `printcnt` (inte), `printfl` (logi) [m], `resubamt` (deci-2), `transproc` (char), `vendaddr3` (char), `addr3` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char)

### `swewl`
**Service Warranty Enter Warranty Claim Detail Line**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `proddesc2` (char), `proddesc` (char), `lineno` (inte) [i], `claimamt` (deci-5), `creditamt` (deci-5), `linecomment` (char), `printcommentfl` (logi) [m], `qty` (deci-2), `extclaimamt` (deci-2), `prod` (char), `intclaimno` (inte) [i], `extcramt` (deci-2), `srtqty` (deci-2), `srtoverfl` (logi) [m], `damagecd` (char), `unitconv` (deci-5), `icspecrecno` (inte), `origclaimno` (inte), `subjrnlno` (inte), `subsetno` (inte), `resubamt` (deci-2), `transproc` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char)

### `swicsd`
**Service Warranty Warehouse Description File**
Fields: `cono` (inte) [i], `whse` (char) [im], `begsrono` (inte), `nextsrono` (inte), `endsrono` (inte), `begclmno` (inte), `nextclmno` (inte), `endclmno` (inte), `transdt` (date), `transtm` (char), `operinit` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `user1` (char), `user2` (char), `dthrs` (deci-0), `transproc` (char), `dthrsperfl` (logi) [m], `othrsperfl` (logi) [m], `othrs` (deci-0), `inoutgrcmin` (inte), `levelerrorfl` (logi) [m], `lunchgrcmin` (inte), `nonshiftotfl` (logi) [m], `rateamt` (deci-2[9]), `rateimpactfl` (logi[9]) [m], `ratetype` (char[9]), `rqrtechsrofl` (logi) [m], `tmzoneadjhrs` (inte), `unionfl` (logi) [m], `shiftamt` (deci-2[6])

### `swicsp`
**Service Warranty - Shadow file for ICSP**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `setuphrs` (inte), `deliverto` (char), `prod` (char) [i], `typecd` (char), `setupfl` (char), `srtfl` (logi) [m], `srthrs` (deci-2), `transproc` (char), `user1` (char)

### `swoeeh`
**Service Warranty - Shadow file for OEEH**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `repairordno` (inte), `orderno` (inte) [i], `ordersuf` (inte) [i], `repairordsuf` (inte), `transproc` (char)

### `swoeel`
**Service Warranty - Shadow file for OEEL**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `linecnt` (char), `jobtype` (char), `lineno` (inte) [i], `vendclaimno` (char), `orderno` (inte) [i], `ordersuf` (inte) [i], `solineno` (inte) [i], `vendno` (deci-0) [m], `repairordno` (inte) [i], `repairordsuf` (inte) [i], `stagecd` (inte), `intclaimno` (inte), `warrantycd` (char), `invclaimcd` (char), `swlineno` (inte), `srtqty` (deci-2), `srtoverfl` (logi) [m], `damagecd` (char), `transproc` (char)

### `swsb`
**Service Warranty Setup Bulletin**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `prod` (char) [im], `vendno` (deci-0) [im], `vendrepairhrs` (inte), `shoprepairhrs` (inte), `issuedt` (date), `campaigncd` (char), `subject` (char), `failcd` (char), `campdt` (date), `ordcreatedt` (date), `situationtxt` (char[17]), `correctiontxt` (char[17]), `intsvctxt` (char[17]), `begserialno` (char), `endserialno` (char), `salesordno` (inte), `salesordsuf` (inte), `bulletinno` (char) [im], `beglotno` (char), `endlotno` (char), `expiredt` (date), `probfailcd` (char), `srtcd` (char), `transproc` (char)

### `swscc`
**Service Warranty Setup Cancellation Code**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cancelcd` (char) [i], `descrip` (char), `class` (char), `transproc` (char)

### `swscf`
**Service Warranty Setup Codes - System Fail Codes**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `failcd` (char) [i], `vendno` (deci-0) [im], `failtype` (char), `failtxt` (char), `failtxtreqfl` (logi) [m], `severitycd` (deci-0), `class` (char), `mfgrepairhrs` (inte), `transproc` (char)

### `swscp`
**Service Warranty Setup Codes - Problem Fail Codes**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `probfailcd` (char) [i], `class` (char), `probfailtxt` (char), `failtxtreqfl` (logi) [m], `failtype` (char), `severitycd` (deci-0), `vendno` (deci-0) [im], `mfgrepairhrs` (inte), `transproc` (char)

### `swsct`
Fields: `cono` (inte) [i], `textno` (inte) [i], `descrip` (char), `problemtxt` (char), `causetxt` (char), `workperftxt` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `grouping` (char) [i], `usrid` (char), `transproc` (char)

### `swsj`
**Service Warranty Setup Job Type**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `claimtype` (char), `jobtype` (char) [i], `descrip` (char), `prodcat` (char), `classcd` (char), `activitycd` (char), `gentype` (logi) [m], `warrantycd` (char), `invclaimcd` (char), `approvty` (char), `transproc` (char), `printpricefl` (logi) [m]

### `swsmsn`
**Additional time entry and payroll-related information associated with a specific technician.**
Fields: `cono` (inte) [i], `deptno` (inte) [i], `empno` (deci-0), `emptype` (char) [i], `entertimefl` (logi) [m], `hiredt` (date), `paytype` (char), `rate` (deci-4), `slsrep` (char) [i], `statustype` (logi) [im], `unionno` (inte), `whse` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `swsr`
**Service Warranty Setup Product Vendor Rates**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `vendno` (deci-0) [im], `prodline` (char) [i], `ratetype` (logi) [m], `rate` (deci-2), `baseon` (char), `plusminus` (logi) [m], `prod` (char) [i], `whse` (char), `descrip` (char), `authservno` (char), `transproc` (char)

### `swsse`
**Service Warranty Setup Scheduling - Exceptions**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `technician` (char) [i], `startdt` (date) [i], `schdminutes` (inte), `comment` (char), `whse` (char) [i], `transproc` (char)

### `swsso`
**Schedule option information, such as vacation and sick time requests.**
Fields: `comment` (char), `cono` (inte) [i], `hours` (deci-1), `lineno` (inte), `repairordno` (inte), `repairordsuf` (inte), `schedopttype` (char) [i], `startdt` (date) [i], `tech` (char) [i], `whse` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `swsss`
**Weekly schedule information for a technician.**
Fields: `cono` (inte) [i], `lunchhrs` (deci-1), `ottype` (char), `ourproc` (char), `ratetype` (char[9]), `ratetypefl` (logi[9]) [m], `shift` (inte), `shiftday` (inte[7]), `shiftendtm` (char), `shifthrs` (deci-1), `shiftstarttm` (char), `tech` (char) [i], `whseday` (char[7]), `wkstartdt` (date) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `daystarttm` (char), `transproc` (char)

### `swsst`
**Service Warranty Setup Schedules - Technician Hours**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `technician` (char) [i], `hrsperwk` (inte), `firstwkday` (char), `lastwkday` (char), `whse` (char) [i], `hrsperday` (inte), `transproc` (char)

### `swstt`
Fields: `codeiden` (char) [i], `codeval` (char) [i], `cono` (inte) [i], `descrip` (char) [i], `dthrs` (inte), `dthrsperfl` (logi) [m], `indivempfl` (logi) [m], `mileagefl` (logi) [m], `nonshiftotfl` (logi) [m], `othrs` (inte), `othrsperfl` (logi) [m], `paystatusfl` (logi) [m], `probemppdfl` (logi) [m], `rateimpactfl` (logi) [m], `schedontype` (char), `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `swsv`
**Service Warranty Setup Vendor Warranty Address**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `vendno` (deci-0) [im], `name` (char) [m], `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `claimformno` (inte), `contactname` (char), `contactphone` (char), `transproc` (char), `addr3` (char)

### `swsw`
**Service Warranty Setup Warranty Claim Type**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `claimtype` (char) [i], `descrip` (char), `gldeptno` (inte[10]), `glacctno` (inte[10]), `gldivno` (inte[10]), `glsubno` (inte[10]), `transproc` (char), `docId` (inte) [i], `nodeId` (inte) [i], `attrNm` (char) [i], `attrText` (char), `createDt` (date), `createTm` (inte), `keyindex` (char) [i], `statmessage` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `docId` (inte) [i], `docNm` (char), `docFrom` (char), `docTo` (char), `docTxnId` (char), `docTxnType` (char), `createdt` (date) [i], `createtm` (inte) [i], `replyToDocId` (inte) [i], `docStatus` (char) [i], `keyindex` (char) [i], `statmessage` (char), `direction` (char) [i], `attrText` (char), `cono` (inte) [i], `keytype` (char) [i], `primarykey` (char) [i], `secondarykey` (char) [i], `sourceHub` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `batchnm` (char), `docTxnType` (char) [i], `docHandler` (char), `hndPersistentfl` (logi), `createDt` (date), `createTm` (inte), `docDescrip` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `docId` (inte) [i], `nodeId` (inte) [i], `nodeParentId` (inte) [i], `nodeType` (char) [i], `nodeNm` (char) [i], `nodePath` (char) [i], `nodeText` (char), `hasAttrsfl` (logi), `hasChildrenfl` (logi), `createdt` (date), `createtm` (inte), `keyindex` (char) [i], `statmessage` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `tradingpartner` (char) [i], `docHandler` (char) [i], `nodeNm` (char) [i], `attrNm` (char) [i], `direction` (char) [i], `ruletype` (char) [i], `rulevalue` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `extdescrip` (char), `type_id` (inte) [im], `parameter_id` (inte) [im], `user_settable` (logi) [m], `one_time` (logi) [m], `mandatory` (logi) [m], `data_type` (char) [m], `column_format` (char), `column_widget` (char), `column_text` (char), `text_values` (char), `default_value` (char), `name` (char), `description` (char), `options` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `type_id` (inte) [im], `type_name` (char) [im], `type_description` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `parameter_id` (inte) [im], `co_num` (char) [i], `wh_num` (char) [i], `parameter_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `sxxmlattr`
**XML Document - Node Attributes**

### `sxxmldoc`
**XML Document - Docment Header**

### `sxxmlhandler`
**XMl Document - Program Handler Crossreference**

### `sxxmlnode`
**XML Document - Node Information**

### `sxxmlrule`
**XML Document - Business Rules**

### `syspar_def`
**Parameter Defininition describing the purpose of the parameter**

### `syspar_type`
**Parameter Types by Module**

### `syspar_value`
**Parameter Value**

### `task`
**Contain information about tasks**
Fields: `co_num` (char) [im], `wh_num` (char) [im], `task_id` (inte) [i], `trans_type` (char) [i], `requested` (char) [i], `started` (char), `completed` (char), `emp_num` (char), `custom_data` (char[5]), `task_status` (char) [i], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `completedtz` (datetm-tz), `requestedtz` (datetm-tz), `startedtz` (datetm-tz), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `task_id` (inte) [i], `emp_num` (char) [i], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `cono` (inte) [i], `sourcecd` (char) [i], `accountno` (deci-0), `vatregno` (char), `invoicedt` (date) [i], `glpostdt` (date), `srcrowpointer` (char) [i], `documentty` (char), `exchgrate` (deci-7), `multigrpfl` (logi) [m], `documentref` (char), `form625fl` (logi) [m], `exceedstoln` (logi) [m], `returndt` (date) [i], `editrans` (logi) [m], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `currencyty` (char), `divno` (inte), `transcd` (inte), `countrycd` (char), `shipto` (char), `transtype` (char), `gldivno` (inte), `paiddt` (date) [i], `apinvno` (char), `custpo` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `rowpointer` (char) [i], `periodid` (char) [i], `glpostdttz` (datetm-tz), `invoicedttz` (datetm-tz), `paiddttz` (datetm-tz), `returndttz` (datetm-tz), `cono` (inte) [i], `taxgroupno` (inte) [i], `taxrowpointer` (char) [i], `grossamt` (deci-2), `grossamtcy` (deci-2), `netamt` (deci-2), `netamtcy` (deci-2), `taxamt` (deci-2), `taxamtcy` (deci-2), `addonnet` (deci-2), `addontaxamt` (deci-2), `addoncurrnet` (deci-2), `addoncurrtax` (deci-2), `taxpct` (deci-3), `exceedstolg` (logi) [m], `writeoffamt` (deci-2), `writeoffdt` (date) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `addongrossamt` (deci-2), `writeoffdttz` (datetm-tz), `cono` (inte) [i], `addr` (char) [i], `city` (char) [i], `countrycd` (char), `county` (char), `district` (char), `geocd` (inte) [i], `outofcityfl` (logi) [m], `state` (char), `zipcd` (char) [i], `srcrowpointer` (char) [i], `errorcd` (inte), `errortxt` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `district2` (char), `addr2` (char), `addr3` (char)

### `task_emp`
**Associates tasks to employees**

### `taxtable`
**Sales/Purchase Tax Processing**

### `taxtabledtl`
**Tax Table Detail Records**

### `tigeocd`
**Tax Interface Geocodes**

### `topic`
**This maps the names of help topics (displayed to users) with the context-id and help filename.**
Fields: `Topic-name` (char) [i], `Context-id` (inte) [i], `Help-file` (char) [i], `Window-Target` (char), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `Object-filename` (char) [i], `Topic-name` (char) [i], `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char)

### `topic-map`
**Maps a help topic to a PowerVue object**

### `tot`
**Totals held for batch posting**
Fields: `cono` (inte) [i], `jrnlno` (inte) [i], `primarykey` (char) [im], `secondkey` (char) [i], `amount` (deci-2), `keyno` (deci-0), `apinvno` (char), `creditfl` (logi) [m], `amounta` (deci-2[2]), `origtaxau` (deci-2), `custno` (deci-0) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `totgl`
**Totals for GL Posting - Temp File**
Fields: `cono` (inte) [i], `jrnlno` (inte) [i], `gldeptno` (inte) [i], `glacctno` (inte) [i], `glsubno` (inte) [i], `amount` (deci-2), `baltype` (logi) [im], `lastinvno` (inte), `lastinvsuf` (inte), `gldivno` (inte) [i], `glcono` (inte), `refer` (char), `orderno` (inte) [i], `ordersuf` (inte) [i], `exchgrate` (deci-7), `setno` (inte), `sumtype` (char), `domamount` (deci-2), `custno` (deci-0) [m], `kitamount` (deci-5), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date)

### `tqae`
**Event activation file. switch on creation of TQEE recs for the event**
Fields: `cono` (inte) [i], `eventnm` (char) [i], `triggernm` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `sourceno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `tqec`
**Cycle Information**
Fields: `cono` (inte) [i], `docty` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `oper2` (char) [i], `stagecd` (inte), `transtype` (char), `custno` (deci-0), `vendno` (deci-0), `whse` (char), `shipfmwhse` (char), `shiptowhse` (char), `cono2` (inte), `comment` (char), `operinit` (char), `transdt` (date), `transtm` (char), `cycledt` (date) [i], `cycletm` (inte) [i], `cptype` (char), `custpros` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `recordno` (deci-0) [i], `transproc` (char), `cycledttz` (datetm-tz)

### `tqee`
**Event Transaction File**
Fields: `cono` (inte) [i], `eventnm` (char) [i], `eventdt` (date) [i], `intflds` (inte[10]), `dtflds` (date[10]), `operinit` (char), `transdt` (date), `transtm` (char), `ourproc` (char), `logflds` (logi[10]) [m], `custno` (deci-0), `vendno` (deci-0), `whse` (char), `divno` (inte), `prod` (char), `orderno` (inte), `ordersuf` (inte), `lineno` (inte), `chflds` (char[20]), `decflds` (deci-5[20]), `recordno` (deci-0) [i], `stagecd` (inte), `transtype` (char), `notesfl` (char), `eventtm` (inte), `slsrepin` (char), `slsrepout` (char), `reasoncd` (char), `reasonty` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cost` (deci-2), `transproc` (char), `eventdttz` (datetm-tz)

### `tqse`
**Setup Event Definition**
Fields: `eventnm` (char) [i], `descrip` (char) [i], `sourceno` (inte) [i], `generatedfl` (logi) [m], `triggernm` (char), `standardty` (char), `operinit` (char), `transdt` (date), `transtm` (char), `category` (char) [i], `reasoncd` (char), `reasonty` (char), `autonotesfl` (logi) [m], `autocmetfl` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `deliveryty` (char), `receiver` (char), `receiverty` (char), `cost` (deci-2), `transproc` (char)

### `tqsf`
**Setup Filter Definition**
Fields: `filternm` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `filterty` (char) [i], `filter` (char[14]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `actiondata` (char), `selectdata` (char), `transproc` (char)

### `tqsg`
**Setup Trigger Definition**
Fields: `triggernm` (char) [i], `descrip` (char), `module` (char), `standardty` (char), `operinit` (char), `transdt` (date), `transtm` (char), `interactfl` (logi) [m], `procs` (char[20]), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `tqso`
**Setup Operator**
Fields: `codeiden` (char) [im], `codeval` (char) [im], `oper2` (char) [im], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `tqst`
**Setup Trend Quality Table Entries**
Fields: `codeval` (char) [i], `descrip` (char), `sourceno` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `analysisnm` (char), `generatedfl` (logi) [m], `codeiden` (char) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `standardty` (char), `transproc` (char)

### `tqsv`
**Setup View Definition**
Fields: `viewnm` (char) [i], `name` (char) [i], `class` (char), `dataty` (char) [i], `fmt` (char), `len` (inte), `lbl` (char), `operinit` (char), `transdt` (date), `transtm` (char), `filenm` (char) [i], `arrayno` (inte) [i], `viewty` (char) [i], `user3` (char), `inqselect` (char), `inqreptseq` (inte), `inqdetlseq` (inte), `rptselect` (char), `rptdetlseq` (inte), `rptbreakseq` (inte), `stdfldnm` (char), `val` (char[10]), `hlp` (char), `vlexp` (char), `vlmsg` (char), `rptrequirefl` (logi) [m], `rptreptnm` (char), `lufilenm` (char), `luparam` (char[10]), `lufield` (char[10]), `luname` (char), `idxseq` (inte), `idxprimfl` (logi) [m], `idxuniqfl` (logi) [m], `user1` (char), `user2` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `budgetfl` (logi) [m], `inqdetlfmt` (char), `inqdetllbl` (char), `inqreptfmt` (char), `inqreptlbl` (char), `rptdetllnno` (inte), `rpttotalfl` (logi) [m], `transproc` (char), `trans_num` (inte) [im], `transmission` (inte) [i], `memo` (char), `co_num` (char) [i], `wh_num` (char) [i], `task_id` (inte) [i], `pallet_id` (char) [i], `pallet_id_from` (char) [i], `carton_id` (char) [i], `date_time` (char) [i], `trans_sec_time` (inte) [im], `trans_type` (char) [im], `emp_num` (char) [i], `abs_num` (char) [i], `ns_comment` (char), `exp_abs` (char), `serial_num` (char) [i], `item_num` (char), `item_qty` (deci-2), `sugg_qty` (deci-2), `bin_num` (char) [i], `bin_from` (char), `bin_to` (char), `cc_type` (char) [i], `cc_string` (char) [i], `shf_num` (inte) [i], `adj_code` (char), `item_type` (char) [m], `uom` (char), `stock_stat` (char), `old_stock_stat` (char), `lot` (char) [i], `dept_num` (inte) [i], `mach_type` (char), `rt_num` (char) [i], `po_number` (char) [i], `po_suffix` (char) [i], `po_line` (inte), `line_sequence` (inte), `packer` (char), `action_code` (char), `result_code` (char), `result_msg` (char), `trans_link` (inte) [i], `record_type` (char), `comments` (char), `proc_created` (char), `truck_id` (char), `batch` (inte) [i], `cargo_control` (char) [i], `release_id` (char) [i], `void` (logi), `cancelled` (logi), `cancelled_by` (char), `cancelled_at` (char), `doc_id` (char) [i], `custom_data` (char[5]), `row_status` (char) [i], `lot_chg_type` (char), `case_quantity` (deci-4), `cc_id` (inte) [i], `order` (char), `order_suffix` (char), `order_type` (char), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `printer` (char), `lot_before` (char), `cancelled_attz` (datetm-tz), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `trans_type` (char) [im], `trans_name` (char) [m], `upload` (logi) [m], `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `triggername` (char) [im], `shortdesc` (char), `longdesc` (char), `module` (char), `proglist` (char[10]), `tablelist` (char[10]), `keyindex` (char) [i], `transdt` (date) [m], `transtm` (char) [m], `transproc` (char), `operinit` (char) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `co_num` (char) [i], `wh_num` (char) [i], `emp_num` (char) [i], `function` (char) [i], `section` (char) [i], `subsection` (char) [i], `object` (char) [i], `keyname` (char) [i], `keyvalue` (char), `trans_date` (char), `trans_proc` (char), `trans_user` (char), `trans_datetz` (datetm-tz), `cono` (inte) [im], `langcd` (char) [im], `seqno` (inte) [im], `break_name` (char) [m], `transdt` (date), `transtm` (char), `transdttmz` (datetm-tz), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `co_num` (char) [im], `wh_num` (char) [im], `func_num` (inte) [im], `transdt` (date), `transtm` (char), `transdttmz` (datetm-tz), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `co_num` (char) [im], `wh_num` (char) [im], `wh_zone` (char) [im], `breaks_enabled` (logi) [m], `interleave` (logi) [m], `auto_assign` (logi) [m], `num_assigns` (inte) [m], `skip_aisle` (logi) [m], `skip_slot` (logi) [m], `repick_skips` (logi) [m], `print_labels` (inte), `print_chase_lbl` (logi) [m], `pick_prompt` (inte), `signoff_allow` (logi) [m], `container_pick` (logi) [m], `container_delv` (logi) [m], `pass_allow` (logi) [m], `delv_prompt` (inte), `qty_verify` (logi) [m], `workid_len` (inte), `pick_shorts` (logi) [m], `rev_pick_allow` (logi) [m], `use_lut` (inte), `pre_prn_lbls` (logi) [m], `contain_prompt` (logi) [m], `multi_container` (logi) [m], `aisle_pre_len` (inte), `aisle_len` (inte), `aisle_post_len` (inte), `slot_len` (inte), `speak_cont_len` (inte), `pick_mode` (inte), `transdt` (date), `transtm` (char), `transdttmz` (datetm-tz), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `co_num` (char) [im], `wh_num` (char) [im], `emp_num` (char) [im], `fieldname` (char) [im], `seqno` (inte) [im], `fieldvalue` (char), `transdt` (date), `transtm` (char), `transdttmz` (datetm-tz), `transproc` (char), `operinit` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `co_num` (char) [im], `wh_num` (char) [im], `udc_type` (char) [i], `udc_desc` (char), `udc_activefl` (logi) [i], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `udc_type` (char) [i], `udc_activefl` (logi) [i], `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz), `co_num` (char) [im], `wh_num` (char) [im], `dept_num` (inte), `sys_name` (char), `program_name` (char) [i], `proc_name` (char) [i], `section_name` (char) [i], `subsection_name` (char) [i], `udc_type` (char) [i], `udc_id` (char) [i], `udc_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `trans_type`
**Contains information about all transaction types that can be entered into the transaction table**
**Operators call this:** "Transaction Type Code" (TWL), "Transaction Type Name" (TWL)

### `transactions`
**Everything important that happens in TWL is recorded in this table.  It can be purged through EOD, but it is one of the largest and most active tables in the database.**
**Operators call this:** "Company" (TWL), "Warehouse" (TWL), "Product (Item)" (TWL), "Employee" (TWL), "Transaction Type" (TWL), "Time of Day" (TWL), "Day of Week" (TWL), "Carton" (TWL), "Bin" (TWL), "Quantity" (TWL), "Adjusted Quantity" (TWL), "Transaction Number" (TWL), "Packer" (TWL), "Bin From" (TWL), "Bin To" (TWL), "Pallet" (TWL), "Pallet From" (TWL), "Cycle Count String" (TWL), "PO Number" (TWL), "Serial Number" (TWL), "Transaction Date" (TWL)

### `trigger_setup`
**Event Manager - Trigger Setup**

### `twlregistry`
**Holds all persistent settings for users**

### `twlvocbreaks`
**TWL VoCollect Breaks**

### `twlvocfuncs`
**TWL VoCollect Functions by Warehouse. Contains only active functions for the warehouse. Links to ao table twlvocfuncs.**

### `twlvocsettings`
**TWL VoCollect Settings**

### `twlvocuser`
**TWL VoCollect User Session Settings**

### `ud_calc`
**User-Defined Calculations Table**

### `ud_cfg`
**User-Defined Configuration Table**
Fields: `co_num` (char) [im], `wh_num` (char) [im], `dept_num` (inte) [i], `emp_title` (char), `emp_num` (char) [i], `sys_name` (char) [i], `udc_type` (char) [i], `udc_id` (char) [i], `udc_value` (char), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `legacy_labelfl` (logi) [m], `default_respfl` (logi) [m], `user_specificfl` (logi) [m], `auto_respfl` (logi) [m], `udc_desc` (char), `udc_alt_value` (char), `param_type` (char), `udc_level` (char), `trans_datetz` (datetm-tz)

### `udcalc_type`
**User-Defined Calculation Types Table**

### `udcfg_type`
**User-Defined Configuration Types Table**

### `uom`
Fields: `uom` (char) [im], `uom_desc` (char), `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `trans_datetz` (datetm-tz)

### `vaeh`
**Value Add Entry Header**
Fields: `cono` (inte) [i], `vano` (inte) [i], `vasuf` (inte) [i], `transtype` (char) [m], `whse` (char) [m], `refer` (char), `placedby` (char), `takenby` (char), `stagecd` (inte), `notesfl` (char), `reqshipdt` (date), `promisedt` (date), `canceldt` (date), `enterdt` (date), `entertm` (char) [m], `createdt` (date), `operinit` (char), `transdt` (date), `transtm` (char), `notimeschg` (inte), `setno` (inte) [i], `jrnlno` (inte) [i], `divno` (inte), `openinit` (char), `nonstockty` (char), `shipprod` (char) [im], `statustype` (logi) [im], `proddesc` (char), `qtyord` (deci-2), `qtyship` (deci-2), `stkqtyord` (deci-2), `stkqtyship` (deci-2), `unit` (char), `unitconv` (deci-5), `pndinvamt` (deci-2), `wipinvamt` (deci-2), `wipextrnamt` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `createdby` (char), `proddesc2` (char), `pndaddons` (deci-2), `wipaddons` (deci-2), `boexistsfl` (logi) [m], `createbofl` (logi) [m], `bono` (inte), `borelfl` (logi) [m], `custprod` (char), `estcost` (deci-5), `writeofffl` (logi) [m], `revno` (char), `prevvano` (inte), `approvty` (char), `pndextrnamt` (deci-2), `pndintrnamt` (deci-2), `pndintrnest` (deci-2), `pndinvinamt` (deci-2), `wipintrnamt` (deci-2), `wipinvinamt` (deci-2), `prodcost` (deci-5), `estcompdt` (date), `cubes` (deci-5), `weight` (deci-5), `extcubes` (deci-5), `extweight` (deci-5), `lostbusty` (char), `arpprodline` (char), `arpvendno` (deci-0), `arpwhse` (char), `prodcat` (char), `netglamt` (deci-2), `receiptdt` (date), `icspecrecno` (inte), `transproc` (char), `edi867compfl` (logi) [m], `keyindex` (char), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `assemlgth` (deci-5), `verno` (inte) [i], `vacfgfl` (logi) [m], `transdttmz` (datetm-tz) [i], `canceldttz` (datetm-tz), `createdttz` (datetm-tz), `enterdttz` (datetm-tz), `estcompdttz` (datetm-tz), `promisedttz` (datetm-tz), `receiptdttz` (datetm-tz), `reqshipdttz` (datetm-tz), `esbshipmentfl` (logi) [m]

### `vaehc`
**Value Add Entry Late Charge**
Fields: `cono` (inte) [i], `vano` (inte) [i], `vasuf` (inte) [i], `seqno` (inte) [i], `amount` (deci-2), `comment` (char), `enterdt` (date) [i], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `jrnlno` (inte), `whse` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `enterdttz` (datetm-tz)

### `vaelo`
**Value Add Transaction Tie File**
Fields: `cono` (inte) [i], `vano` (inte) [im], `lineno` (inte) [i], `ordertype` (char) [i], `orderaltno` (inte) [i], `orderaltsuf` (inte) [i], `linealtno` (inte) [i], `seqno` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `oordertype` (char), `oorderaltno` (inte), `oorderaltsuf` (inte), `oseqaltno` (deci-0), `olinealtno` (inte), `wtcono` (inte), `owtcono` (inte), `seqaltno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `vasuf` (inte) [i], `custno` (deci-0), `transproc` (char)

### `vaes`
**Value Add Entry Transaction Sections**
Fields: `cono` (inte) [i], `vano` (inte) [i], `vasuf` (inte) [i], `seqno` (inte) [i], `sctntype` (char) [i], `sctncode` (char), `destvendno` (deci-0), `stagearea` (char), `destwhse` (char), `destshipfmno` (inte), `destname` (char), `destaddr` (char[2]), `destcity` (char), `deststate` (char), `destzipcd` (char), `shipinstr` (char), `refer` (char), `shipviaty` (char), `reqshipdt` (date), `promisedt` (date), `extrvendno` (deci-0), `extrshipfmno` (inte), `intrwhse` (char), `goalprod` (char), `goaldesc` (char), `goalqtyord` (deci-2), `goalstkqtyord` (deci-2), `goalunit` (char), `goalunitconv` (deci-5), `user1` (char), `user2` (char), `wordindexfl` (logi) [m], `user3` (char), `user4` (char), `rowpointer` (char) [i], `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `wletsetno` (char), `norushln` (inte), `borelfl` (logi) [m], `transdt` (date), `transtm` (char), `operinit` (char), `specdata` (char), `specprtty` (char), `stagecd` (inte), `addonno` (inte[4]), `addonamt` (deci-2[4]), `desttype` (char), `jrnlno` (inte) [i], `duedt` (date), `specprtfl` (logi) [m], `setno` (inte) [i], `route` (char), `pickcnt` (inte), `pickeddt` (date), `pickedtm` (char), `pickinit` (char), `printpckfl` (logi) [m], `shipdt` (date), `shiptm` (char), `completefl` (logi) [im], `processfl` (logi) [im], `processinit` (char) [i], `processproc` (char) [i], `notesfl` (char), `orderdisp` (char), `zone` (char), `shippingpt` (char) [m], `nopackages` (inte), `pkglabel` (char), `manzonefl` (logi) [m], `totweight` (deci-2), `actfreight` (deci-2), `transproc` (char), `destaddr3` (char), `vacfgfl` (logi) [m], `transdttmz` (datetm-tz) [i], `duedttz` (datetm-tz), `pickeddttz` (datetm-tz), `promisedttz` (datetm-tz), `reqshipdttz` (datetm-tz), `shipdttz` (datetm-tz), `esbshipmentfl` (logi) [m]

### `vaesl`
**Value Add Entry Transaction Sections - Line Items**
Fields: `cono` (inte) [i], `vano` (inte) [i], `vasuf` (inte) [i], `seqno` (inte) [i], `lineno` (inte) [i], `nonstockty` (char) [i], `shipprod` (char) [i], `unit` (char), `unitconv` (deci-5), `qtyneeded` (deci-2), `qtyord` (deci-2), `qtyship` (deci-2), `stkqtyship` (deci-2), `stkqtyord` (deci-2), `arpvendno` (deci-0) [i], `arpprodline` (char) [i], `arpwhse` (char) [i], `proddesc` (char), `cataddfl` (logi) [m], `costoverfl` (logi) [m], `orderalttype` (char) [i], `orderaltno` (inte), `linealtno` (inte), `prodcat` (char), `prodcost` (deci-5), `netamt` (deci-2), `completefl` (logi) [im], `sctntype` (char) [i], `timeworkdt` (date), `timeelapsed` (inte), `timecomment` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `proddesc2` (char), `boseqno` (inte), `oqtybasetotfl` (logi) [m], `rushfl` (logi) [m], `transdt` (date), `transtm` (char), `operinit` (char), `laborflatrtfl` (logi) [m], `labortype` (char), `laborunits` (deci-2), `timeactty` (char), `qtybasetotfl` (logi) [m], `commentfl` (logi) [m], `whse` (char) [im], `usagefl` (logi) [m], `wipfl` (logi) [m], `timeslsrep` (char), `binloc` (char), `cubes` (deci-5), `weight` (deci-5), `notimeschg` (inte), `prevqtyship` (deci-2), `printpckfl` (logi) [m], `qtyunavail` (deci-2), `reasunavty` (char), `shpqtyoverfl` (logi) [m], `statustype` (logi) [m], `extcubes` (deci-5), `extweight` (deci-5), `intermprodfl` (logi) [m], `directfl` (logi) [m], `prevwipfl` (logi) [m], `netglamt` (deci-2), `icspecrecno` (inte), `transproc` (char), `keyindex` (char), `cancelty` (char), `oqtyneeded` (deci-2), `lgthcompfl` (logi) [m], `scrapfctr` (deci-2), `maxlaborcalcqty` (inte), `cutoffty` (char), `leadtm` (inte), `vacfgfl` (logi) [m], `timeworkdttz` (datetm-tz)

### `vasp`
**Value Add Setup Product Default Header**
Fields: `cono` (inte) [i], `shipprod` (char) [im], `whse` (char) [im], `operinit` (char), `transdt` (date), `transtm` (char), `refer` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `nodaysfab` (inte), `notesfl` (char), `transproc` (char)

### `vasps`
**Value Add Setup Product Defaults Sections**
Fields: `cono` (inte) [i], `shipprod` (char) [im], `whse` (char) [im], `seqno` (inte) [i], `sctntype` (char), `sctncode` (char), `destvendno` (deci-0), `stagearea` (char), `destwhse` (char), `destshipfmno` (inte), `extrvendno` (deci-0), `extrshipfmno` (inte), `shipinstr` (char), `refer` (char), `shipviaty` (char), `intrwhse` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `operinit` (char), `specdata` (char), `specprtty` (char), `desttype` (char), `goalprod` (char), `goaldesc` (char), `specprtfl` (logi) [m], `notesfl` (char), `orderdisp` (char), `route` (char), `transproc` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `shipprod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP; Required
- `whse` (Warehouse) — Can be 24 long if xref is used. Can be left blank if default for all warehouses. See Notes Below; Valid values/xref: ICSD
- `refer` (VASP Reference) — See Notes Below
- `nodaysfab` (# of Days to Fabricate) — See Notes Below; Default: 0
- `seqno` (Sequence) — Section Sequence number.; Required
- `sctntype` (Section type) — SP-Secifications, EX-External Process, II - Ivnentory In, IN - Inventory Components, IT- Internal Process IS - Inspection; Valid values/xref: sp, ex, ii, in, it or is; Required
- `sctncode` (Section Code) — Must be setup in VAST; Valid values/xref: VAST; Required
- `specdata` (Spec/Instructions Data) — Size is unlimited, field can be over-stuffed longer than 60. Text can be added to all section types
- `specprtfl` (Spec Print Flag) — Print flag for spec data; Valid values/xref: Y or N; Default: Based on specprtty
- `specprtty` (Spec Print Type) — E-External I-Internal B-Both N-Neither; Valid values/xref: E, I, B or N; Default: N
- `destvendno` (Destination Vendor # for IN, IS, IT and EX section) — Can be 24 long if xref is used. IN, IS, IT and EX Section must have either DestVendno or DestWhse; Valid values/xref: APSV
- `destshipfmno` (Destination Vendor Ship From for IN, IS, IT and EX Section) — Valid values/xref: APSS
- `destwhse` (Destination Warehouse for IN, IS, IT and EX Section) — Can be 24 long if xref is used. IN, IS, IT and EX Section must have either DestVendno or DestWhse; Valid values/xref: ICSD
- `extrvendno` (Vendor to Send External Process To in EX section) — Can be 24 long if xref is used. Used on EX section only, required on EX section.; Valid values/xref: APSV
- `extrshipfmno` (Vendor Ship From for External Process) — Used on EX Section only.; Valid values/xref: APSS
- `intrwhse` (Internal Warehouse for IT and IS section) — Used on IT and IS Section Only; Valid values/xref: ICSD
- `desttype` (Destination type required for EX, IS and IT Sections) — F-Final V-Vendor W-Warehouse Blank for other section types; Valid values/xref: F, V, W or Blank
- `goalprod` (Required on EX, IS and IT sections. Intermediate Product if desttype V or W. Final Product if desttype is Final.) — If blank, default will be "Non Stock" if V or W desttype. Shipprod if desttype F Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP if desttype F; Default: see notes
- `goaldesc` (Description for Intermediate or Final product) — If blank default will be "Non Stock" if V or W desttype. Shipprod description from ICSP if desttype F; Default: see notes
- `shipviaty` (Ship Via type) — Can be 24 long if using xref.; Valid values/xref: SASTT - S
- `stagearea` (Staging Area) — Do not include slashes
- `route` (Route/Day/Stop) — Do not include slashes. Used on IN section only
- `orderdisp` (Order Disposition) — Used on IN section only S for Ship Complete; Valid values/xref: S or Blank
- `user5` (user5) — Used for Conversion Import ID

### `vaspsa`
**Value Add Setup Product Defaults - Assembly**
Fields: `cono` (inte) [i], `shipprod` (char) [im], `whse` (char) [i], `segdelimiter` (char), `lengthseg` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `cono` (inte) [i], `shipprod` (char) [im], `whse` (char) [i], `segment` (inte) [i], `size` (inte), `type` (char), `validation` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `valdesc` (char), `cono` (inte) [i], `shipprod` (char) [im], `whse` (char) [i], `segment` (inte) [i], `sequence` (inte) [i], `ruleequality1` (char), `ruleunion1` (logi) [m], `rulesegment1` (inte), `rule1` (char), `ruleequality2` (char), `ruleunion2` (logi) [m], `rulesegment2` (inte), `rule2` (char), `ruleequality3` (char), `ruleunion3` (logi) [m], `rulesegment3` (inte), `rule3` (char), `ruleequality4` (char), `ruleunion4` (logi) [m], `rulesegment4` (inte), `rule4` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `rulevaliddata` (char), `ruleerrormsg` (char), `cono` (inte) [im], `shipprod` (char) [im], `whse` (char) [im], `verno` (inte) [im], `segment` (inte) [im], `sequence` (inte) [im], `ruleequality1` (char), `ruleunion1` (logi) [m], `rulesegment1` (inte), `rule1` (char), `ruleequality2` (char), `ruleunion2` (logi) [m], `rulesegment2` (inte), `rule2` (char), `ruleequality3` (char), `ruleunion3` (logi) [m], `rulesegment3` (inte), `rule3` (char), `ruleequality4` (char), `ruleunion4` (logi) [m], `rulesegment4` (inte), `rule4` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `rulevaliddata` (char), `ruleerrormsg` (char), `cono` (inte) [im], `shipprod` (char) [im], `whse` (char) [im], `verno` (inte) [im], `segment` (inte) [im], `size` (inte), `type` (char), `validation` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char), `valdesc` (char), `cono` (inte) [im], `shipprod` (char) [im], `whse` (char) [im], `verno` (inte) [im], `segdelimiter` (char), `lengthseg` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `transproc` (char), `operinit` (char)

### `vaspsas`
**Value Add Setup Product Defaults - Assembly Segments**
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `shipprod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: VASP; Required
- `whse` (Warehouse) — Can be 24 long if xref is used. Can be left blank if default for all warehouses.; Valid values/xref: VASP
- `segdelimiter` (Segment Delimiter) — Character used between segments such as a dash
- `lengthseg` (Length Segment) — Segment number which will contain the total length
- `segment` (Segment Number) — Can define up to 24 segments; Valid values/xref: 1 thru 24; Required
- `size` (Segment Size) — Total size for shipprod + all segments + delimiters cannot exceed 24; Required
- `type` (Segment Type) — (C)haracter, (I)nteger or (D)ecimal; Valid values/xref: C, I or D; Required
- `user5` (user5) — Used for Conversion Import ID

### `vaspsasr`
**Value Add Setup Product Defaults - Assembly Segment Rules**

### `vaspsasrv`
**Value Add Setup Product Defaults - Assembly Segment Rules**

### `vaspsasv`
**Value Add Setup Product Defaults - Assembly Segments**

### `vaspsav`
**Value Add Setup Product Defaults Versions - Assembly**

### `vaspsl`
**Value Add Setup Product Defaults - Line Items**
Fields: `cono` (inte) [i], `shipprod` (char) [im], `whse` (char) [im], `seqno` (inte) [i], `lineno` (inte) [i], `nonstockty` (char), `compprod` (char) [i], `unit` (char), `unitconv` (deci-5), `qtyneeded` (deci-2), `arpvendno` (deci-0), `arpprodline` (char), `arpwhse` (char), `proddesc` (char), `prodcat` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `proddesc2` (char), `transdt` (date), `transtm` (char), `operinit` (char), `prodcost` (deci-5), `laborflatrtfl` (logi) [m], `labortype` (char), `laborunits` (deci-2), `timeelapsed` (inte), `timeactty` (char), `qtybasetotfl` (logi) [m], `intermprodfl` (logi) [m], `commentfl` (logi) [m], `directfl` (logi) [m], `usagefl` (logi) [m], `timecomment` (char), `costoverfl` (logi) [m], `cubes` (deci-5), `weight` (deci-5), `transproc` (char), `lgthcompfl` (logi) [m], `scrapfctr` (deci-2), `maxlaborcalcqty` (inte), `cutoffty` (char), `leadtm` (inte), `cono` (inte) [im], `shipprod` (char) [im], `whse` (char) [im], `verno` (inte) [im], `seqno` (inte) [im], `lineno` (inte) [im], `qtybasetotfl` (logi) [m], `nonstockty` (char), `compprod` (char) [i], `unit` (char), `unitconv` (deci-5), `qtyneeded` (deci-2), `arpvendno` (deci-0), `arpprodline` (char), `arpwhse` (char), `proddesc` (char), `prodcat` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `proddesc2` (char), `transdt` (date), `transtm` (char), `operinit` (char), `prodcost` (deci-5), `laborflatrtfl` (logi) [m], `labortype` (char), `laborunits` (deci-2), `timeelapsed` (inte), `timeactty` (char), `costoverfl` (logi) [m], `intermprodfl` (logi) [m], `commentfl` (logi) [m], `directfl` (logi) [m], `usagefl` (logi) [m], `timecomment` (char), `cubes` (deci-5), `weight` (deci-5), `transproc` (char), `lgthcompfl` (logi) [m], `scrapfctr` (deci-2), `maxlaborcalcqty` (inte), `cutoffty` (char), `leadtm` (inte)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `shipprod` (Product) — Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: VASPS; Required
- `whse` (Warehouse) — Can be 24 long if xref is used. Can be left blank if default for all warehouses.; Valid values/xref: VASPS
- `seqno` (Sequence number of Section) — All sections except SP can have line items; Valid values/xref: VASPS; Required
- `compprod` (Component Product) — Can be non-stock in IN and II sections only. EX, IS and IT sections must be labor Items Old Cross Ref length 50 available starting in 6.1.040 Product can be 50 long only if AO for Expanded Product is activated starting in 10.3.1; Valid values/xref: ICSP & ICSW if not non-stock, VASPSAS for configuration; Required
- `qtybasetotfl` (Qty Based on Total Flag) — Yes if Total Qty For Line Item Based On Units Of Finished Product; Valid values/xref: Y or N; Default: N
- `unit` (Unit) — If not ICSP stocking unit then provide unitconv for validation in ICSEU or SASTT-U.; Valid values/xref: ICSEU, SASTT - U; Default: ICSP Stocking or EACH
- `unitconv` (Unit Conversion Factor) — Number of stocking units per unit; Default: 1
- `lgthcompfl` (Variable Length Component) — Always No on Labor product components Available Starting 6.1.080; Valid values/xref: Y or N; Default: N
- `scrapfctr` (Scrap Factor) — Always zero on Labor product components Available Starting 6.1.080
- `cutoffty` (Cutoff Type) — Add (+), Subtract (-) or Ignore (blank) Available Starting 6.1.080; Valid values/xref: +, - or blank
- `usagefl` (Usage flag) — Yes to count as usage; Valid values/xref: Y or N; Default: Y
- `prodcost` (Product Cost) — Defaults from ICSW if not a nonstock
- `nonstockty` (Line Type Indicator) — Blank for Stock, (S)pecial, (N)onstock or (C )onfiguration. Nonstocks only allowed in IN and II sections. Configuration available starting 6.1.080, requires setup of VASPSAS Assembly; Valid values/xref: Blank, S, N or C. Blank and S validated in ICSP. C validated in VASPSAS.
- `proddesc` (Product Description 1) — Only used for nonstock items
- `proddesc2` (Product Description 2) — Only used for nonstock items
- `cubes` (Cubes) — Only used for nonstock items
- `weight` (Weight) — Only used for nonstock items
- `arpvendno` (Vendor) — Only used for nonstock items; Valid values/xref: APSV
- `arpprodline` (Product Line) — Only used for nonstock items; Valid values/xref: ICSL
- `arpwhse` (Whse) — Only used for nonstock items; Valid values/xref: ICSD
- `prodcat` (Product Category) — Only used for nonstock items; Valid values/xref: SASTT - C; Default: ICSP or DCAOI
- `directfl` (Direct Flag) — Valid values/xref: Y or N; Default: N
- `intermprodfl` (Intermediate Product Flag) — Valid values/xref: Y or N; Default: N
- `laborflatrtfl` (Labor Flat Rate Flag) — If Yes, Rate Is Charged Regardless Of Units Produced. Used on EX sections only; Valid values/xref: Y or N; Default: N
- `labortype` (Labor Type) — (Q)ty, (W)eight, (C)ube Required for EX sections only, other sections use blank.; Valid values/xref: Q, W, C or blank; Default: Q
- `laborunits` (Labor Units) — Based On Finished Product Amount. Used on EX sections only; Default: 1
- `timeelapsed` (Estimated Time - enter as HH:MM) — Required on IT and IS sections only
- `timeactty` (Actual Type) — (E)stimated, (A)ctual Used on IT and IS sections only; Valid values/xref: E or A; Default: E
- `timecomment` (Time Comment) — Used on IT and IS sections only
- `maxlaborcalcqty` (Maximum Labor Calc Qty) — Only used with Estimated time type Available Starting 6.1.080
- `user5` (user5) — Used for Conversion Import ID

### `vaspslv`
**Value Add Setup Product Defaults - Line Items**

### `vaspsv`
**Value Add Setup Product Defaults Version Sections**
Fields: `cono` (inte) [im], `shipprod` (char) [im], `whse` (char) [im], `verno` (inte) [im], `seqno` (inte) [im], `sctntype` (char), `sctncode` (char), `destvendno` (deci-0), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transdt` (date), `transtm` (char), `operinit` (char), `stagearea` (char), `destwhse` (char), `destshipfmno` (inte), `shipinstr` (char), `refer` (char), `shipviaty` (char), `specdata` (char), `specprtty` (char), `extrvendno` (deci-0), `extrshipfmno` (inte), `intrwhse` (char), `orderdisp` (char), `desttype` (char), `goalprod` (char), `goaldesc` (char), `specprtfl` (logi) [m], `notesfl` (char), `route` (char), `transproc` (char)

### `vaspv`
**Value Add Setup Product Default Header**
Fields: `cono` (inte) [im], `shipprod` (char) [im], `whse` (char) [im], `verno` (inte) [im], `verrefer` (char), `vercrtdt` (date), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `refer` (char), `nodaysfab` (inte), `notesfl` (char), `transproc` (char), `vercrtdttz` (datetm-tz)

### `vast`
**Value Add Setup Table Values**
Fields: `codeiden` (char) [im], `codeval` (char) [im], `cono` (inte) [i], `descrip` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `destvendno` (deci-0) [i], `destwhse` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `extrvendno` (deci-0), `extrshipfmno` (inte), `destshipfmno` (inte), `intrwhse` (char), `transproc` (char), `cono` (inte) [i], `custno` (deci-0) [im], `shipto` (char) [im], `vehicleid` (char) [i], `descrip` (char), `vinno` (char) [i], `totservmin` (deci-2), `equiptype` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `totserupddt` (date), `pmaintfl` (logi) [im], `pmaintdays` (inte), `notesfl` (char), `pmaintdt` (date) [i], `jobtype` (char), `pmaintdttz` (datetm-tz), `totserupddttz` (datetm-tz), `vend_addr_num` (inte) [im], `co_num` (char) [i], `wh_num` (char) [im], `vendor_id` (char) [im], `addr_seq` (inte), `addr` (char[2]), `city` (char), `state` (char), `zip` (char), `country` (char), `contact_name` (char), `phone_number` (char), `fax_number` (char), `edi_code` (char), `duns_number` (char), `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `addr_ext` (char[3]), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `trans_datetz` (datetm-tz), `co_num` (char) [i], `wh_num` (char) [im], `vendor_id` (char) [im], `abs_num` (char) [im], `vend_item` (char) [im], `item_price` (deci-2) [m], `uom` (char), `box_qty` (inte), `plt_block` (inte), `plt_high` (inte), `country_code` (char), `custom_data` (char[5]), `stack_height` (inte), `ref_type` (char) [i], `date_time` (char), `case_quantity` (deci-4), `pallet_quantity` (deci-4), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `vehicle`
**Vehicle Setup Table**

### `vendaddr`
**This table stores addresses for a vendor**

### `venddetail`
**Vendor detail information**

### `venmst`
**The master vendor table**
Fields: `co_num` (char) [i], `wh_num` (char) [im], `vendor_id` (char) [im], `vend_name` (char), `addr` (char[2]), `city` (char), `state` (char), `zip` (char), `country` (char), `contact_name` (char), `phone_number` (char), `fax_number` (char), `edi_code` (char), `duns_number` (char), `qa_inspection` (logi), `qa_instructions` (char), `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `addr_ext` (char[3]), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `trans_datetz` (datetm-tz)

### `viewer`
**Tempory file for reports**
Fields: `cono` (inte) [i], `oper2` (char) [im], `reportnm` (char) [i], `c2` (char) [i], `c4` (char), `i7` (inte), `i2` (inte), `c1` (char), `dt` (date), `dt-2` (date), `c13` (char), `c15` (char), `c4-2` (char), `c2-2` (char), `de9d2s` (deci-2), `c2-3` (char), `de9d2s-2` (deci-2), `c6` (char), `l` (logi) [m], `c24` (char) [i], `c24-2` (char), `de12d0` (deci-0) [i], `de12d5` (deci-5), `i4` (inte), `i3` (inte), `de2d3` (deci-3), `c24-3` (char), `c20` (char) [i], `rid` (reci), `c20-2` (char), `dt-3` (date), `dt-4` (date), `de9d2s-3` (deci-2), `de2d3-2` (deci-3), `de2d3-3` (deci-3), `de2d3-4` (deci-3), `de2d3-5` (deci-3), `de12d5-2` (deci-5), `de12d5-3` (deci-5), `de12d5-4` (deci-5), `faxfl` (logi) [m], `outputty` (char) [i], `c12` (char) [i], `i8` (inte)

### `wave`
**Contain information about waves of orders released for picking together**
Fields: `co_num` (char) [im], `wh_num` (char) [im], `batch` (inte) [i], `task_id` (inte), `line_count` (inte), `order_count` (inte), `weight` (deci-2), `cube` (deci-2), `drop_date_time` (char), `active_date_time` (char), `ship_date_time` (char), `drop_price` (deci-2), `ship_price` (deci-2), `single_line_orders` (inte), `cart` (char) [i], `host_batch` (char) [i], `emp_num` (char), `ship_cube` (deci-2), `ship_weight` (deci-2), `custom_data` (char[5]), `wave_status` (char) [i], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `active_date_timetz` (datetm-tz), `drop_date_timetz` (datetm-tz), `ship_date_timetz` (datetm-tz), `trans_datetz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i], `cono` (inte) [i], `login` (char) [i], `oper2` (char), `usertype` (inte), `Statusfl` (logi), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `rowpointer` (char) [im], `cono` (inte) [im], `functionname` (char) [im], `screenname` (char) [im], `extensiontype` (char) [im], `settingvalue` (clob), `activefl` (logi) [im], `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `tag` (char), `descrip` (char), `revision` (inte) [im], `login` (char) [i], `name` (char), `company` (char), `phone` (char), `emailaddr` (char), `fax` (char), `password` (char), `statusfl` (logi), `transdt` (date), `transtm` (char), `operinit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `storeid` (char), `corpid` (char), `operrole` (char), `rowpointer` (char) [im], `cono` (inte) [i], `profile` (char) [i], `operator` (char) [i], `functionname` (char) [i], `screenname` (char) [i], `settingname` (char) [i], `settingvalue` (clob), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char), `rowpointer` (char) [im], `cono` (inte) [i], `notestype` (char), `tablename` (char) [i], `primarykey` (char) [i], `printfl` (logi) [m], `transdt` (date), `transtm` (char), `operinit` (char), `requirefl` (logi) [m], `noteln` (clob), `pageno` (inte) [i], `secondarykey` (char) [i], `securefl` (logi) [m], `origpageno` (inte), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `printfl2` (logi) [m], `printfl3` (logi) [m], `printfl4` (logi) [m], `printfl5` (logi) [m], `notecategory` (char), `headerfl` (logi) [m], `CoNo` (inte) [i], `login` (char) [i], `function` (char) [i], `section` (char) [i], `subsection` (char) [i], `keyname` (char) [i], `keyvalue` (char), `TransDt` (date), `TransTm` (char), `operInit` (char), `transproc` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `cono` (inte) [im], `profile` (char) [im], `operator` (char) [im], `functionname` (char) [im], `screenname` (char) [im], `settingname` (char) [im], `settingvalue` (char), `operinit` (char), `transdt` (date), `transtm` (char), `transproc` (char)

### `webcono`
**Web Company**

### `webextension`
**Web UI Extension**

### `weblogin`
**Web Login**

### `webmodificatio`
**Web Modifications**

### `webnote`
**Web Note**

### `webregestry`
**Web Registry**

### `websetting`
**WebUI Settings**

### `wh_zone`
**All warehouse zones**

### `whmst`
**Master warehouse table**
Fields: `co_num` (char) [i], `wh_num` (char) [im], `wh_desc` (char), `addr` (char[2]), `city` (char), `state` (char), `zip` (char), `country` (char), `region` (char), `rcv_zone_default` (char) [m], `rcv_zone_hold` (char) [m], `cs_stage` (char), `bo_bin` (char) [m], `last_physical` (date), `ytd_phy_unit_var` (deci-2), `ytd_phy_dollar_var` (deci-2), `qa_inspection` (logi), `qa_instructions` (char), `carrier_id` (char) [m], `consolidate` (logi), `consolidate_where` (char), `pm_irms` (char), `cod_name` (char), `cod_addr` (char[5]), `cod_city` (char), `cod_state` (char), `cod_zip` (char), `cod_country` (char), `net_host` (char), `net_addr` (char), `net_port` (inte), `custom_data` (char[5]), `row_status` (logi) [m], `trans_user` (char), `trans_date` (char), `trans_proc` (char), `addr_ext` (char[3]), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `transdttmz` (datetm-tz) [i], `last_physicaltz` (datetm-tz), `trans_datetz` (datetm-tz), `vocollect` (logi) [m], `co_num` (char) [i], `wh_num` (char) [im], `wh_zone` (char) [im], `first_aisle` (inte) [m], `last_aisle` (inte) [m], `zone_desc` (char), `zone_type` (char), `control_pick_area` (char), `pick_sequence` (inte) [i], `carousel_type` (char), `allow_putaway` (logi), `custom_data` (char[5]), `allow_eod_cycle` (logi), `putaway_sequence` (inte), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `allow_picking` (logi), `trans_datetz` (datetm-tz), `vocollect` (logi) [m], `vocregion` (inte), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `wlal`
**Warehouse Logistics Location and description file**
Fields: `cono` (inte), `wlloc` (char) [i], `descrip` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `wlmachine` (char), `wlservice` (char), `wlnetwork` (char), `wldbname` (char), `wldbpath` (char), `wlsndscript` (char), `wlrcvscript` (char), `wlstarttm` (inte), `wlstoptm` (inte), `wlpause` (inte), `wllogdir` (char), `transproc` (char), `wllocal` (logi) [m], `esbwlfl` (logi) [m]

### `wlao`
**WL Admin Options**
Fields: `cono` (inte) [im], `delinactfl` (logi) [m], `version` (char), `transdt` (date), `transtm` (char), `operinit` (char), `jrnloperinit` (char), `zeroapprty` (char), `whzone` (char), `holdoerm` (char), `holdoeapprty` (char), `custnotesfl` (logi) [m], `wlpmshipfl` (logi) [m], `zeroqtyfl` (logi) [m], `holdporm` (logi) [m], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `icspnotesfl` (logi) [m], `createshipfl` (logi), `icsp2notesfl` (logi) [m], `vastit` (char), `vastex` (char)

### `wleh`
**Warehouse Logistics Header Information**
Fields: `cono` (inte) [i], `whse` (char) [i], `function` (char), `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `priority` (inte), `statustype` (char) [i], `errormsg` (char), `vendno` (deci-0), `duedt` (date), `custno` (deci-0), `shiptonm` (char), `shiptoaddr` (char[2]), `shiptocity` (char), `shiptost` (char), `shiptozip` (char), `shipdate` (date), `shipviaty` (char), `custpo` (char), `transtype` (char), `shipinstr` (char), `addonnet` (deci-2), `nopackages` (inte), `actfreight` (deci-2), `updtype` (char), `setno` (char) [i], `shipmentid` (char), `edifl` (logi) [m], `kitbuildty` (char), `transid` (deci), `reply` (char), `errorno` (inte) [m], `receiverno` (char), `shipfmno` (inte), `transproc` (char), `shiptoaddr3` (char), `edishipmentid` (char), `edipackageid` (char), `duedttz` (datetm-tz), `shipdatetz` (datetm-tz)

### `wlel`
**Warehouse Logistics Line Information**
Fields: `cono` (inte) [i], `whse` (char) [i], `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `shipprod` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `statustype` (char), `specnstype` (char), `vendprod` (char), `stkqty` (deci-2), `duedt` (date), `retorderno` (inte), `retordersuf` (inte), `retlineno` (inte), `returnfl` (logi) [m], `returnty` (char), `msdssheetno` (char), `orderaltno` (inte), `orderaltsuf` (inte), `linealtno` (inte), `qtyunavail` (deci-2), `proddesc` (char), `upcno` (char), `receiverno` (char), `stkstatusty` (char), `linety` (char), `updtype` (char), `setno` (char) [i], `wlpicktype` (char), `transid` (deci), `errormsg` (char), `reply` (char), `crreasonty` (char), `stagingty` (char), `errorno` (inte) [m], `transproc` (char), `proddesc2` (char), `lostbusty` (char), `altwhse` (char), `duedttz` (datetm-tz)

### `wlelk`
**Warehouse Logistics Component Information**
Fields: `cono` (inte) [i], `whse` (char) [i], `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `shipprod` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `statustype` (char), `specnstype` (char), `vendprod` (char), `stkqty` (deci-2), `msdssheetno` (char), `proddesc` (char), `updtype` (char), `setno` (char) [i], `negcompfl` (logi) [m], `stkstatcomp` (char), `wlpicktype` (char), `reqfl` (logi) [m], `transid` (deci), `reply` (char), `transproc` (char), `origvalineno` (inte), `origvaseqno` (inte), `altwhse` (char)

### `wlels`
**Warehouse Logistics Serial/Lot Information**
Fields: `cono` (inte) [i], `whse` (char) [i], `ordertype` (char) [i], `orderno` (inte) [i], `ordersuf` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `serlottype` (char) [i], `serlotno` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `statustype` (char), `prod` (char) [i], `stkqty` (deci-2), `updtype` (char), `setno` (char) [i], `transid` (deci), `reasunavty` (char), `qtyunavail` (deci-2), `stkstatus` (char), `reply` (char), `transproc` (char)

### `wlem`
**Warehouse Logistics Master File Information**
Fields: `cono` (inte) [i], `whse` (char) [i], `prod` (char) [i], `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `function` (char), `field1` (char) [i], `field2` (char) [i], `name` (char), `addr` (char[2]), `city` (char), `state` (char), `zipcd` (char), `unitstock` (char), `icswstattype` (char), `kittype` (char), `msdsfl` (logi) [m], `cubes` (deci-5), `weight` (deci-5), `height` (deci-5), `width` (deci-5), `length` (deci-5), `serlottype` (char) [i], `binloc1` (char), `binloc2` (char), `specnstype` (char) [i], `adjusttype` (char), `expectqty` (deci-2), `actualqty` (deci-2), `adjustreas` (char), `statustype` (char) [i], `errormsg` (char), `updtype` (char), `setno` (char) [i], `whzone` (char), `boxqty` (inte), `abc` (char), `rotate` (deci-2), `pilferfl` (logi) [m], `country` (char), `descrip` (char), `upcno` (char), `vendprod` (char), `bincntr` (char), `kitbuild` (char), `icspstattype` (char), `adjlotstat` (char), `adjlottype` (char), `oreasunavty` (char), `prodcat` (char), `msdssheetno` (char), `adjlotqty` (deci), `icsouqty` (deci-2), `transid` (deci), `entrydt` (date), `runno` (deci-0), `reasunavty` (char) [i], `reply` (char), `binloc1updfl` (logi) [m], `binloc2updfl` (logi) [m], `bincntrupdfl` (logi) [m], `processty` (char) [i], `errorno` (inte) [m], `vendno` (deci-0) [m], `shipfmno` (inte), `contact` (char), `phoneno` (char), `faxphoneno` (char), `edicode` (char), `dunsno` (char), `transproc` (char), `descrip2` (char), `memo` (char), `casequantity` (deci-2), `palletquantity` (deci-2), `addr3` (char), `entrydttz` (datetm-tz)

### `wlet`
**Warehouse Logistics Transaction File**
Fields: `cono` (inte) [i], `whse` (char) [i], `priority` (inte), `processty` (char) [i], `transtype` (char) [i], `statustype` (char) [i], `createdt` (date), `createtm` (char), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `location` (char), `setno` (char) [i], `transid` (deci), `reply` (char), `transproc` (char), `createdttz` (datetm-tz)

### `wlicsw`
Fields: `cono` (inte) [i], `prod` (char) [i], `whse` (char) [i], `palletqty` (deci-0), `whzone` (char), `bincntr` (char), `kitbuild` (char), `boxqty` (deci-0), `caseqty` (deci-0), `pilferfl` (logi) [m], `rotate` (deci-0), `operinit` (char), `transdt` (date), `transtm` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `binloc1` (char), `binloc2` (char), `binloc1updfl` (logi) [m], `binloc2updfl` (logi) [m], `updatefl` (logi) [im], `transproc` (char), `appname` (char) [i], `apptype` (char), `licensedt` (date), `secure` (inte), `licenseto` (char), `custno` (deci-0) [m], `licenseno` (char), `numusers` (inte), `graceperiod` (inte), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `licensedttz` (datetm-tz), `trans_datetz` (datetm-tz), `pwmaxdays` (inte), `pwmindays` (inte), `pwmaxlength` (inte), `pwminlength` (inte), `pwminnumeric` (inte), `pwminspecial` (inte), `pwminprev` (inte), `pwminalpha` (inte), `custom_data` (char[5]), `trans_user` (char), `trans_date` (char), `trans_proc` (char), `emp_num` (char) [i], `trans_datetz` (datetm-tz)

### `wllicense`
**License Information**

### `wlpasswd`
**Password Security Compliance Table**

### `wmet`
**Warehouse Manager - Transactions**
Fields: `cono` (inte) [im], `whse` (char) [im], `prod` (char) [im], `orderno` (inte) [i], `ordersuf` (inte) [i], `ordertype` (char) [i], `transtype` (char), `stagecd` (inte) [i], `qtydirected` (deci-2), `qtyactual` (deci-2), `operinit` (char), `transdt` (date), `transtm` (char), `binloc` (char) [im], `pickinit` (char) [i], `recvinit` (char), `lineno` (inte) [i], `seqno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `wmsb`
**Warehouse Manager, Bin File**
Fields: `whse` (char) [i], `binloc` (char) [i], `bintype` (char), `sizetype` (char), `binlength` (deci-2), `binwidth` (deci-2), `binheight` (deci-2), `fstoredt` (date), `lstoredt` (date), `priority` (inte), `lpickdt` (date), `assigncode` (char) [i], `statuscode` (char) [i], `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `descrip` (char), `user2` (char), `cubes` (deci-2), `user3` (char), `pounittype` (char), `user4` (char), `building` (char) [i], `user5` (char), `tmstored` (inte), `user6` (deci-5), `tmpicked` (inte), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `fstoredttz` (datetm-tz), `lpickdttz` (datetm-tz), `lstoredttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `whse` (Warehouse) — Valid values/xref: ICSD; Required
- `assigncode` (Assignment) — Valid values/xref: O, P, S, A, X, U or Blank Assigncode X must have Statuscode X; Default: O
- `priority` (Priority) — Valid values/xref: 1 - 9 or blank; Default: 0
- `statuscode` (Status) — Valid values/xref: A, S, I, X or blank Assigncode X must have Statuscode X; Default: A
- `bintype` (Bin Type) — Valid values/xref: WMST - BT; Required
- `sizetype` (Size Type) — Valid values/xref: WMST - ST; Required
- `pounittype` (Unit Type) — Valid values/xref: S, B, P or Blank; Default: B

### `wmsbp`
**Warehouse Manager, Product by Bin**
Fields: `whse` (char) [i], `binloc` (char) [i], `qtyonhand` (deci-2), `qtycommitted` (deci-2), `qtyreceived` (deci-2), `fstoredt` (date), `lstoredt` (date) [i], `lpickdt` (date), `prod` (char) [i], `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `user1` (char), `minqty` (deci-2), `user2` (char), `maxqty` (deci-2), `user3` (char), `tmstored` (inte), `user4` (char), `tmpicked` (inte), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `fstoredttz` (datetm-tz), `lpickdttz` (datetm-tz), `lstoredttz` (datetm-tz)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `whse` (Warehouse) — Valid values/xref: ICSD; Required
- `binloc` (Bin Location) — Valid values/xref: WMSB; Required
- `prod` (Product) — Valid values/xref: ICSP/ICSW; Required

### `wmsc`
**WM Cross Ref By Size Setup**
Fields: `cono` (inte) [i], `operinit` (char), `transdt` (date), `transtm` (char), `whse` (char) [i], `sizetype` (char) [i], `prod` (char) [i], `maxqty` (deci-2), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)
**Field Notes** *(from CSD data-conversion field maps — purpose, expected values, and codes)*
- `whse` (Warehouse) — Valid values/xref: ICSD; Required
- `sizetype` (Size Type) — Valid values/xref: WMST - ST; Required
- `prod` (Product) — Valid values/xref: ICSP; Required

### `wmst`
**Warehouse Manager Setup Table Values**
Fields: `cono` (inte) [i], `codeiden` (char) [im], `codeval` (char) [im], `operinit` (char), `transdt` (date), `transtm` (char), `descrip` (char), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char)

### `wteh`
**Warehouse Transfer Header**
**Operators call this:** "Ship-From Warehouse" (Warehouse Transfers), "Stage" (Warehouse Transfers), "Ship Via Type" (Warehouse Transfers), "Printed Date" (Warehouse Transfers), "Requested Ship Date" (Warehouse Transfers), "Shipped Date" (Warehouse Transfers), "Receipt Date" (Warehouse Transfers), "Stage Name" (Warehouse Transfers)
Fields: `cono` (inte) [i], `wtno` (inte) [im], `wtsuf` (inte) [i], `stagecd` (inte), `shiptonm` (char) [m], `notesfl` (char), `orderaltno` (inte), `transtype` (char) [m], `shiptost` (char), `shiptozip` (char), `shipfmwhse` (char) [im], `shipinstr` (char), `refer` (char), `shipviaty` (char), `shipdt` (date), `immedwtfl` (logi) [m], `fminvexrate` (deci-7), `operinit` (char), `transdt` (date), `orderdt` (date), `printeddt` (date), `enterdt` (date), `receiptdt` (date), `transtm` (char), `ototqtyshp` (deci-2), `shiptoaddr` (char[2]), `totqtyact` (deci-2), `shiptocity` (char), `nolineitem` (inte), `drdeltm` (char), `createdby` (char), `totlineamt` (deci-2), `wletsetno` (char), `totweight` (deci-5), `bostage` (inte), `totcubes` (deci-5), `totqtyshp` (deci-2), `drdeldt` (date), `borelfl` (logi) [m], `boexistsfl` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `stagearea` (char), `user8` (date), `user9` (date), `jrnlno` (inte) [i], `nosnlotsi` (deci-2), `notimeschg` (inte), `nextlineno` (inte), `linefl` (logi) [m], `printfl` (logi) [m], `ignoreltfl` (logi) [m], `cono2` (inte) [i], `totqtyord` (deci-2), `totqtyrcv` (deci-2), `shiptowhse` (char) [i], `totshipamt` (deci-2), `totordamt` (deci-2), `totrcvamt` (deci-2), `duedt` (date), `nosnlotso` (deci-2), `dueoverfl` (logi) [m], `openinit` (char), `jrnlno2` (inte) [i], `nounappr` (inte), `pickedby` (char), `pkgid` (char), `wtauth` (inte), `addonamt` (deci-2[2]), `addontype` (char[2]), `rcvoperinit` (char), `jrnlno3` (inte) [i], `reqshipdt` (date), `orderaltsuf` (inte), `nocatwghti` (inte), `nocatwghto` (inte), `laststagecd` (inte), `noerrs` (inte), `pickcnt` (inte), `addonnet` (deci-2[2]), `langcd` (char), `user1` (char), `user2` (char), `nopackages` (inte), `addondist` (deci-2[2]), `actfreight` (deci-2), `shippingpt` (char) [m], `zone` (char), `divno` (inte), `rushfl` (logi) [m], `transproc` (char), `keyindex` (char), `drexpfl` (logi) [m], `fmcurrencyty` (char), `tocurrencyty` (char), `toinvexrate` (deci-7), `fmexpexrate` (deci-7), `toexpexrate` (deci-7), `fmcapexrate` (deci-7), `tocapexrate` (deci-7), `shiptoaddr3` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `esbshipmentfl` (logi) [m], `esbasnfl` (logi) [m], `autoaltwhsecd` (char), `autoaltordno` (inte), `autoaltordsuf` (inte), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `countrycd` (char), `extshipinstr` (char), `transdttmz` (datetm-tz) [i], `markupaddonfl` (logi) [m], `drdeldttz` (datetm-tz), `duedttz` (datetm-tz), `enterdttz` (datetm-tz), `orderdttz` (datetm-tz), `printeddttz` (datetm-tz), `receiptdttz` (datetm-tz), `reqshipdttz` (datetm-tz), `shipdttz` (datetm-tz), `reasoncode` (char), `lspinvregstatus` (char), `lspuuid` (char), `lspinvregstatdttmz` (datetm-tz), `lspidentifier` (char[10]), `confirmctnfl` (logi) [m]

### `wtel`
**WT Line Items**
**Operators call this:** "Company" (Warehouse Transfers), "Ship-To Warehouse" (Warehouse Transfers), "Transaction Type" (Warehouse Transfers), "Entered By" (Warehouse Transfers), "Approved By" (Warehouse Transfers), "Order Quantity" (Warehouse Transfers), "Ship Quantity" (Warehouse Transfers), "Net Amount" (Warehouse Transfers), "Cost" (Warehouse Transfers), "Transfer Number" (Warehouse Transfers), "Transfer Suffix" (Warehouse Transfers), "Transfer Line" (Warehouse Transfers), "Unit of Measure" (Warehouse Transfers), "Entered Date" (Warehouse Transfers), "Due Date" (Warehouse Transfers), "Approval Date" (Warehouse Transfers), "Transaction Type Name" (Warehouse Transfers)
Fields: `wtno` (inte) [i], `wtsuf` (inte) [i], `shipfmwhse` (char) [im], `transtype` (char) [i], `lineno` (inte) [i], `qtyord` (deci-2), `cono` (inte) [i], `unit` (char), `transdt` (date), `enterdt` (date), `operinit` (char), `shipprod` (char) [im], `transtm` (char), `stkqtyship` (deci-2), `prodcost` (deci-5), `prodcati` (char), `usagefl` (logi) [m], `ordertype` (char) [i], `weight` (deci-5), `cubes` (deci-5), `qtyfmrcvs` (deci-2), `ostkqtyship` (deci-2), `qtyactship` (deci-2), `notimeschg` (inte), `statustype` (char) [i], `proddesc2` (char), `leadoverty` (char), `icspecrecno` (inte), `printfl` (logi) [m], `chrgqtyi` (deci-2), `bono` (inte) [i], `costoverfl` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `nosnlotsi` (deci-2), `user7` (deci-5), `user8` (date), `user9` (date), `prevqtyshp` (deci-2), `commentfl` (logi) [m], `catwtfli` (logi) [m], `bofl` (logi) [m], `qtyship` (deci-2), `duedt` (date) [i], `arpoverfl` (logi) [m], `cono2` (inte) [i], `shiptowhse` (char) [i], `netamt` (deci-2), `proddesc` (char), `stkqtyord` (deci-2), `approvety` (char) [i], `approvedt` (date), `approveinit` (char), `chrgqtyo` (deci-2), `netrcv` (deci-2), `prodcato` (char), `qtyrcv` (deci-2), `stkqtyrcv` (deci-2), `catwtflo` (logi) [m], `linealtno` (inte), `orderaltno` (inte), `nosnlotso` (deci-2), `nonstockty` (char) [i], `binloc` (char), `reqprod` (char), `xrefprodty` (char), `vendno` (deci-0) [m], `prodline` (char) [m], `prodinrcvfl` (logi) [m], `netord` (deci-2), `qtyunavail` (deci-2), `reasunavty` (char), `delayresrvfl` (logi) [m], `glcostrcv` (deci-2), `lastbofl` (logi) [m], `glcostexc` (deci-2), `user1` (char), `user2` (char), `addonamt` (deci-2), `wmqtyship` (deci-2), `wmqtyrcv` (deci-2), `unitconv` (deci-5), `transproc` (char), `keyindex` (char), `user10` (char), `user11` (char), `user12` (char), `user13` (char), `user14` (char), `user15` (char), `user16` (char), `user17` (char), `user18` (char), `user19` (char), `user20` (char), `user21` (char), `user22` (char), `user23` (char), `user24` (char), `custstkqtyshp` (deci-2), `custprodcost` (deci-5), `cutfl` (logi) [m], `cutlossamt` (deci-2), `scraplossamt` (deci-2), `rowpointer` (char) [i], `wordindexfl` (logi) [m], `srcrestrictovrfl` (logi) [m], `transdttmz` (datetm-tz) [i], `addonmarkuptype` (char), `addonmarkupcost` (deci-5), `addonpct` (deci-2), `addontype` (char), `approvedttz` (datetm-tz), `duedttz` (datetm-tz), `enterdttz` (datetm-tz), `confirmctnfl` (logi) [m]

### `wtelo`
**WT Alternate Order #s**
Fields: `cono` (inte), `wtno` (inte) [im], `lineno` (inte) [i], `ordertype` (char) [i], `orderaltno` (inte) [i], `orderaltsuf` (inte) [i], `linealtno` (inte) [i], `seqno` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `oordertype` (char), `oorderaltno` (inte), `oorderaltsuf` (inte), `olinealtno` (inte), `oseqaltno` (deci-0), `wtcono` (inte) [i], `owtcono` (inte), `seqaltno` (inte) [i], `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `wtsuf` (inte) [i], `transproc` (char), `rowpointer` (char) [i]

### `wterah`
**WT RRAR Header**
Fields: `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `reportno` (inte) [i], `shiptonm` (char) [m], `shiptoaddr` (char[2]), `shiptocity` (char), `shiptost` (char), `shiptozip` (char), `shipinstr` (char), `refer` (char), `duedt` (date), `shipviaty` (char), `ignoreltfl` (logi) [m], `totlineamt` (deci-2), `totweight` (deci-5), `totcubes` (deci-5), `totqtyord` (deci-2), `transtype` (char), `oper2` (char) [im], `reportnm` (char) [i], `nextlineno` (inte), `cono2` (inte) [i], `reqshipdt` (date), `shipfmwhse` (char) [im], `shiptowhse` (char) [i], `wtauth` (inte), `addonamt` (deci-2[2]), `addontype` (char[2]), `pushfl` (logi) [m], `user1` (char), `user2` (char), `mergefl` (logi) [m], `rushfl` (logi) [im], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `transproc` (char), `shiptoaddr3` (char), `totsuper` (inte), `markupaddonfl` (logi) [m], `automrgfl` (logi) [m], `duedttz` (datetm-tz), `reqshipdttz` (datetm-tz), `reasoncode` (char), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `wteral`
**WT RRAR Acceptance Lines**
Fields: `cono` (inte) [i], `transdt` (date), `transtm` (char), `operinit` (char), `reportno` (inte) [i], `lineno` (inte) [i], `seqno` (inte) [i], `shipprod` (char) [im], `wtfl` (logi) [m], `accepttype` (char), `qtyord` (deci-2), `unit` (char), `prodcost` (deci-5), `ordertype` (char), `orderaltno` (inte), `orderaltsuf` (inte), `linealtno` (inte), `duedt` (date), `cubes` (deci-5), `weight` (deci-5), `netamt` (deci-2), `proddesc` (char), `wtcono` (inte), `nonstockty` (char), `stkqtyord` (deci-2), `qtysurplus` (deci-2), `prodcat` (char), `shipfmwhse` (char) [m], `shiptowhse` (char), `seasontype` (char), `bofl` (logi) [m], `usagefl` (logi) [m], `vendno` (deci-0) [m], `prodline` (char) [m], `unitconv` (deci-5), `user1` (char), `user2` (char), `proddesc2` (char), `seqaltno` (inte), `commentfl` (logi) [m], `rushfl` (logi) [m], `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `icspecrecno` (inte), `transproc` (char), `superfl` (logi) [m], `custreservefoundfl` (logi) [m], `custreserveqty` (deci-2), `srcrestrictovrfl` (logi) [m], `custforecastfoundfl` (logi) [m], `custforecastqty` (deci-2), `duedttz` (datetm-tz), `rowpointer` (char) [i], `transdttmz` (datetm-tz) [i]

### `wtsa`
**WT Setup Markup Addons**
Fields: `cono` (inte) [im], `cono2` (inte) [im], `shipfmrowpointer` (char) [im], `shiptorowpointer` (char) [im], `recordtype` (char) [im], `srcrowpointer` (char) [im], `addontype` (char), `addonamt` (deci-2), `operinit` (char), `transproc` (char), `transdttmz` (datetm-tz), `user1` (char), `user2` (char), `user3` (char), `user4` (char), `user5` (char), `user6` (deci-5), `user7` (deci-5), `user8` (date), `user9` (date), `sequence_num` (inte) [i], `instance_num` (inte) [i], `proc_name` (char) [i], `Num_Occurs` (inte), `last_change` (deci-5) [i], `Needs_Compile` (logi) [i], `MaxLength` (inte) [i], `Justification` (inte) [i], `Statement` (char), `Item` (char), `ObjectName` (char), `Line_Num` (inte), `lang_name` (char) [i], `GrowthFactor` (inte), `sequence_num` (inte) [i], `original_string` (char) [c], `last_change` (deci-5) [i], `Comment` (char), `KeyOfString` (char) [ci], `sequence_num` (inte) [i], `instance_num` (inte) [i], `lang_name` (char) [i], `trans_string` (char), `last_change` (deci-5)
