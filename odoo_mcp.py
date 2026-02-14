# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Odoo MCP: JSON-RPC client for draft invoices, payments, and queries.
Usage: python odoo_mcp.py --action <action> [--data <json>] [--dry-run]"""
import argparse, json, os, sys
from log_utils import log_event

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

ACTIONS = ["create_invoice", "create_payment", "confirm_invoice",
           "confirm_payment", "cancel_invoice", "list_invoices",
           "list_payments", "get_partner"]


def get_odoo_connection():
    """Connect to Odoo via odoorpc (preferred) or xmlrpc.client fallback."""
    url = os.environ.get("ODOO_URL", "http://localhost:8069")
    db = os.environ.get("ODOO_DB", "odoo")
    user = os.environ.get("ODOO_USER", "admin")
    pwd = os.environ.get("ODOO_PASSWORD", "admin")
    try:
        import odoorpc
        host = url.replace("http://", "").replace("https://", "").split(":")[0]
        port = int(url.split(":")[-1]) if ":" in url.split("//")[-1] else 8069
        proto = "jsonrpc+ssl" if url.startswith("https") else "jsonrpc"
        odoo = odoorpc.ODOO(host, protocol=proto, port=port)
        odoo.login(db, user, pwd)
        return odoo, "odoorpc"
    except ImportError:
        import xmlrpc.client
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, user, pwd, {})
        if not uid:
            raise RuntimeError("Odoo authentication failed")
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        return (models, db, uid, pwd), "xmlrpc"


def execute_xmlrpc(conn, model, method, args=None, kwargs=None):
    """Execute an Odoo method via xmlrpc.client."""
    models, db, uid, pwd = conn
    return models.execute_kw(db, uid, pwd, model, method,
                             args or [], kwargs or {})


def create_invoice(conn, conn_type, data):
    partner = data.get("partner_name", "Unknown")
    lines = data.get("lines", [{"name": "Service", "quantity": 1, "price_unit": 0}])
    ref = data.get("reference", "")
    if conn_type == "odoorpc":
        Invoice = conn.env["account.move"]
        inv_lines = [(0, 0, {"name": l.get("name", "Item"),
                             "quantity": l.get("quantity", 1),
                             "price_unit": l.get("price_unit", 0)}) for l in lines]
        partner_ids = conn.env["res.partner"].search([("name", "ilike", partner)], limit=1)
        partner_id = partner_ids[0] if partner_ids else False
        inv_id = Invoice.create({"move_type": "out_invoice", "partner_id": partner_id,
                                 "ref": ref, "invoice_line_ids": inv_lines})
        return {"status": "created", "record_id": inv_id, "model": "account.move", "partner": partner}
    else:
        partner_ids = execute_xmlrpc(conn, "res.partner", "search",
                                     [[("name", "ilike", partner)]], {"limit": 1})
        partner_id = partner_ids[0] if partner_ids else False
        inv_lines = [(0, 0, {"name": l.get("name", "Item"),
                             "quantity": l.get("quantity", 1),
                             "price_unit": l.get("price_unit", 0)}) for l in lines]
        inv_id = execute_xmlrpc(conn, "account.move", "create",
                                [{"move_type": "out_invoice", "partner_id": partner_id,
                                  "ref": ref, "invoice_line_ids": inv_lines}])
        return {"status": "created", "record_id": inv_id, "model": "account.move", "partner": partner}


def create_payment(conn, conn_type, data):
    amount = data.get("amount", 0)
    partner = data.get("partner_name", "Unknown")
    ref = data.get("reference", "")
    if conn_type == "odoorpc":
        partner_ids = conn.env["res.partner"].search([("name", "ilike", partner)], limit=1)
        partner_id = partner_ids[0] if partner_ids else False
        pay_id = conn.env["account.payment"].create(
            {"payment_type": "inbound", "partner_type": "customer",
             "partner_id": partner_id, "amount": amount, "ref": ref})
        return {"status": "created", "record_id": pay_id, "model": "account.payment", "amount": amount}
    else:
        partner_ids = execute_xmlrpc(conn, "res.partner", "search",
                                     [[("name", "ilike", partner)]], {"limit": 1})
        partner_id = partner_ids[0] if partner_ids else False
        pay_id = execute_xmlrpc(conn, "account.payment", "create",
                                [{"payment_type": "inbound", "partner_type": "customer",
                                  "partner_id": partner_id, "amount": amount, "ref": ref}])
        return {"status": "created", "record_id": pay_id, "model": "account.payment", "amount": amount}


def confirm_invoice(conn, conn_type, data):
    record_id = data.get("record_id")
    if not record_id:
        return {"status": "error", "error": "record_id required"}
    if conn_type == "odoorpc":
        conn.env["account.move"].browse(record_id).action_post()
    else:
        execute_xmlrpc(conn, "account.move", "action_post", [[record_id]])
    return {"status": "confirmed", "record_id": record_id, "model": "account.move"}


def confirm_payment(conn, conn_type, data):
    record_id = data.get("record_id")
    if not record_id:
        return {"status": "error", "error": "record_id required"}
    if conn_type == "odoorpc":
        conn.env["account.payment"].browse(record_id).action_post()
    else:
        execute_xmlrpc(conn, "account.payment", "action_post", [[record_id]])
    return {"status": "confirmed", "record_id": record_id, "model": "account.payment"}


def cancel_invoice(conn, conn_type, data):
    record_id = data.get("record_id")
    if not record_id:
        return {"status": "error", "error": "record_id required"}
    if conn_type == "odoorpc":
        conn.env["account.move"].browse(record_id).button_draft()
    else:
        execute_xmlrpc(conn, "account.move", "button_draft", [[record_id]])
    return {"status": "cancelled", "record_id": record_id, "model": "account.move"}


def list_invoices(conn, conn_type, data):
    limit = data.get("limit", 20)
    days = data.get("days", 7)
    from datetime import datetime, timedelta
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    if conn_type == "odoorpc":
        ids = conn.env["account.move"].search(
            [("move_type", "=", "out_invoice"), ("create_date", ">=", date_from)], limit=limit)
        records = conn.env["account.move"].read(ids, ["name", "partner_id", "amount_total",
                                                       "amount_residual", "state", "create_date"])
    else:
        ids = execute_xmlrpc(conn, "account.move", "search",
                             [[("move_type", "=", "out_invoice"),
                               ("create_date", ">=", date_from)]], {"limit": limit})
        records = execute_xmlrpc(conn, "account.move", "read", [ids],
                                 {"fields": ["name", "partner_id", "amount_total",
                                             "amount_residual", "state", "create_date"]})
    return {"status": "success", "count": len(records), "invoices": records}


def list_payments(conn, conn_type, data):
    limit = data.get("limit", 20)
    days = data.get("days", 7)
    from datetime import datetime, timedelta
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    if conn_type == "odoorpc":
        ids = conn.env["account.payment"].search(
            [("create_date", ">=", date_from)], limit=limit)
        records = conn.env["account.payment"].read(ids, ["name", "partner_id", "amount",
                                                          "state", "create_date"])
    else:
        ids = execute_xmlrpc(conn, "account.payment", "search",
                             [[("create_date", ">=", date_from)]], {"limit": limit})
        records = execute_xmlrpc(conn, "account.payment", "read", [ids],
                                 {"fields": ["name", "partner_id", "amount",
                                             "state", "create_date"]})
    return {"status": "success", "count": len(records), "payments": records}


def get_partner(conn, conn_type, data):
    name = data.get("name", "")
    if conn_type == "odoorpc":
        ids = conn.env["res.partner"].search([("name", "ilike", name)], limit=5)
        records = conn.env["res.partner"].read(ids, ["name", "email", "phone", "city"])
    else:
        ids = execute_xmlrpc(conn, "res.partner", "search",
                             [[("name", "ilike", name)]], {"limit": 5})
        records = execute_xmlrpc(conn, "res.partner", "read", [ids],
                                 {"fields": ["name", "email", "phone", "city"]})
    return {"status": "success", "count": len(records), "partners": records}


ACTION_MAP = {
    "create_invoice": create_invoice, "create_payment": create_payment,
    "confirm_invoice": confirm_invoice, "confirm_payment": confirm_payment,
    "cancel_invoice": cancel_invoice, "list_invoices": list_invoices,
    "list_payments": list_payments, "get_partner": get_partner,
}


def main():
    ap = argparse.ArgumentParser(description="Odoo MCP – Gold Tier")
    ap.add_argument("--action", required=True, choices=ACTIONS)
    ap.add_argument("--data", default="{}", help="JSON data for the action")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true"
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    if dry_run:
        result = {"status": "dry_run", "action": args.action, "data": data}
        log_event(f"odoo_{args.action}", "odoo_mcp", "dry_run",
                  details={"action": args.action, "mcp_params": data})
        print(json.dumps(result))
        return

    try:
        conn, conn_type = get_odoo_connection()
        handler = ACTION_MAP[args.action]
        result = handler(conn, conn_type, data)
        log_event(f"odoo_{args.action}", "odoo_mcp", "success",
                  details={"action": args.action, "odoo_record_id": result.get("record_id"),
                           "mcp_params": data})
        print(json.dumps(result))
    except Exception as e:
        result = {"status": "error", "action": args.action, "error": str(e)}
        log_event(f"odoo_{args.action}", "odoo_mcp", "failure",
                  details={"action": args.action, "error": str(e)[:200]})
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
