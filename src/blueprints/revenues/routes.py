# pylint: disable=no-value-for-parameter
"""Motorist Routes"""


import datetime
import os
import re



from flask import Blueprint, redirect, render_template, request, url_for, send_file, flash

from src.database.querys import RulesQuery, MotoristsQuerys

from .invoices import (
    AllDriverInvoice,
    DriverInvoice,
    CompanyInvoice,
)


revenues_app = Blueprint("revenues_app", __name__, url_prefix="/revenues/")


@revenues_app.route("/settings", methods=["GET"])
def show():
    """Get all porcent groups in database"""
    porcents = RulesQuery.get_all()
    return render_template("pages/revenues/show.html", porcents=porcents)


@revenues_app.route("/create", methods=["POST", "GET"])
def create():
    """Create a new settings rule in database."""
    if request.method == "POST":
        rule = {
            "name": request.form.get("rule_name"),
            "rule_type": request.form.get("rule_type"),
            "tag": request.form.get("tag"),
            "field": request.form.get("field"),
            "condition": request.form.get("condition"),
            "condition_value": request.form.get("condition_value"),
            "rule": request.form.get("rule"),
            "rule_value": request.form.get("rule_value"),
        }
        if rule["name"] == "":
            flash('Por favor, preencha todos os campos.', 'erro')
            return render_template("pages/revenues/create.html")

        RulesQuery.create(
            rule
        )

        return redirect(url_for("revenues_app.invoices"))

    return render_template("pages/revenues/create.html")


@revenues_app.route("/edit/<rule_id>", methods=["POST", "GET"])
def edit(rule_id):
    """Edit rules of a porcent groups"""
    if request.method == "POST":
        rule = {
            "name": request.form.get("rule_name"),
            "rule_type": request.form.get("rule_type"),
            "tag": request.form.get("tag"),
            "field": request.form.get("field"),
            "condition": request.form.get("condition"),
            "condition_value": request.form.get("condition_value"),
            "rule": request.form.get("rule"),
            "rule_value": request.form.get("rule_value"),
        }

        RulesQuery.update_porcent(
            rule_id, rule
        )

        return redirect(url_for("revenues_app.invoices"))
    
    
    rule = RulesQuery.get_group_by_id(rule_id)

    return render_template("pages/revenues/edit.html", rule=rule)


@revenues_app.route("/invoices", methods=["POST", "GET"])
def invoices():
    """Export  invoice from motorists"""

    motorists = list(map(lambda driver: driver.name, MotoristsQuerys.show()))

    if request.method == "POST":
        option = request.form.get("option")
        datetime_range = request.form.get("daterange")

        date_one = datetime_range[:10]
        date_two = datetime_range[11:-1]

        date_two = re.findall(r"\d+/\d+/\d+", date_two)[0]

        date_time_one = datetime.datetime.strptime(date_one, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        date_time_two = (
            datetime.datetime.strptime(date_two, "%m/%d/%Y")
            + datetime.timedelta(hours=23, minutes=59, seconds=59)
        ).strftime("%Y-%m-%d %H:%M:%S")

        match option:
            case "TODOS":
                return AllDriverInvoice((date_time_one, date_time_two)).send_image() # pylint: disable=line-too-long

            case "TOTAL":
                return CompanyInvoice((date_time_one, date_time_two)).get_image()

            case _:
                DriverInvoice((date_time_one, date_time_two), option).get_image()

                return send_file(
                    os.path.join(os.getcwd(), "midia", option.lower()+".png"),
                    mimetype='png',
                    as_attachment=True)
                    
               

    motorists.insert(0, "TOTAL")
    motorists.insert(0, "TODOS")
    rules = RulesQuery.get_all()

    return render_template("pages/revenues/invoices.html", motorists=motorists, rules=rules)


@revenues_app.route("/delete/<porcent_id>", methods=["POST", "GET"])
def delete(porcent_id):
    """Deletes a porcent from the database.

    Args:
        porcent_id (str): The ID of the porcent to be deleted.

    Returns:
        redirect: Redirects to the show route after the deletion.
    """
    # Delete the porcent using the porcent_id
    RulesQuery.delete(porcent_id)

    # Redirect to the show route
    return redirect(url_for("revenues_app.invoices"))
