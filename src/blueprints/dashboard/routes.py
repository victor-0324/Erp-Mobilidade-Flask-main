# pylint: disable=no-value-for-parameter,unused-variable
"""Rotas de Dashboard"""

import locale
from flask import Blueprint, render_template
from src.blueprints.revenues.invoices.invoice_company import CompanyInvoice

from src.database.querys import MotoristsQuerys

dashboard_app = Blueprint("/dashboard", __name__, url_prefix="/")


@dashboard_app.route("/", methods=["GET"])
def dashboard():
    """Main dashboard of application."""
    motorist_num = len(MotoristsQuerys.show())
    data = CompanyInvoice(("2022-01-01 00:00:00", "2023-12-31 23:59:59")).get_result()

    return render_template(
        "pages/dashboard/index.html",
        motorist_num=motorist_num,
        runs=data["runs_amount"],
        gross_value=locale.currency(data["gross_value"]),
        lucro=locale.currency(data["profit"]),
    )
