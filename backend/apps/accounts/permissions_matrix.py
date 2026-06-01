"""
Canonical role → permission matrix.

Permission codes are ``"<module>.<verb>"`` where verb ∈
{view, add, change, delete}. The wildcard ``"*"`` grants everything;
``"<module>.*"`` grants all verbs within a module.

Modules align with the API/ViewSet ``module`` attributes.
"""

MODULES = [
    "dashboard", "patients", "appointments", "visits", "dental_charts",
    "treatments", "prescriptions", "billing", "payments", "installments",
    "expenses", "inventory", "documents", "reports", "followups",
    "users", "roles", "settings", "audit", "backup",
]

ALL_VERBS = ["view", "add", "change", "delete"]


def full(*modules):
    return [f"{m}.*" for m in modules]


def view_only(*modules):
    return [f"{m}.view" for m in modules]


# code -> (display name, permission list)
ROLE_DEFINITIONS = {
    "ADMIN": {
        "name": "System Administrator",
        "permissions": ["*"],
        "is_system": True,
    },
    "MANAGER": {
        "name": "Clinic Manager",
        "permissions": (
            view_only("dashboard")
            + full("appointments", "inventory", "expenses", "followups")
            + ["users.view", "users.add", "users.change"]
            + view_only("patients", "visits", "treatments", "billing",
                        "payments", "installments", "reports", "audit")
        ),
        "is_system": True,
    },
    "DOCTOR": {
        "name": "Doctor",
        "permissions": (
            view_only("dashboard", "patients", "appointments")
            + full("visits", "dental_charts", "treatments", "prescriptions")
            + view_only("documents", "followups")
            + ["documents.add"]
        ),
        "is_system": True,
    },
    "RECEPTIONIST": {
        "name": "Receptionist",
        "permissions": (
            view_only("dashboard")
            + full("patients", "appointments", "followups")
            + ["visits.view", "visits.add", "visits.change"]  # arrival/queue
            + full("billing", "payments")
            + view_only("installments", "documents")
            + ["documents.add"]
        ),
        "is_system": True,
    },
    "ACCOUNTANT": {
        "name": "Accountant",
        "permissions": (
            view_only("dashboard")
            + full("billing", "payments", "installments", "expenses")
            + view_only("patients", "reports")
        ),
        "is_system": True,
    },
    "INVENTORY_OFFICER": {
        "name": "Inventory Officer",
        "permissions": (
            view_only("dashboard")
            + full("inventory")
            + view_only("reports")
        ),
        "is_system": True,
    },
}
