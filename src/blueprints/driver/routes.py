# pylint: disable=no-value-for-parameter
"""Motorist Routes"""


from flask import Blueprint, redirect, render_template, request, url_for

from src.database.querys import MotoristsQuerys, RunsQuerys
from src.database.querys.rules import RulesQuery

from .src.uploads import MotoristsDataParsing

drivers_app = Blueprint("drivers_app", __name__, url_prefix="/motorists/")


@drivers_app.route("/", methods=["GET"])
def get_motorits():
    """Get all motorists in database"""
    motorists = MotoristsQuerys.show()
    return render_template("pages/motorists/show.html", motorists=motorists)


@drivers_app.route("/create", methods=["POST", "GET"])
def create():
    """Create a new driver"""
    if request.method == "POST":
        name = request.form.get("name")
        data_json = {"comission": "default"}
        MotoristsQuerys.new(name, data_json)
        RunsQuerys.create_table(name)
        return redirect(url_for("drivers_app.get_motorits"))

    return render_template("pages/motorists/create.html")


@drivers_app.route("/delete/<int:motorist_id>", methods=["POST", "GET"])
def delete(motorist_id: int):
    """Delete a driver"""
    MotoristsQuerys.delete(motorist_id)
    return redirect(url_for("drivers_app.get_motorits"))


@drivers_app.route("/uploads", methods=["POST", "GET"])
def uploads():
    """Upload files"""
    if request.method == "POST":
        archives = request.files.getlist("image[]")
        if archives[0].filename == "":
            return render_template("pages/motorists/uploads.html")
        MotoristsDataParsing(archives)

        return redirect(url_for("drivers_app.uploads"))
    return render_template("pages/motorists/uploads.html")


@drivers_app.route("/edit/<motorist_id>", methods=["POST", "GET"])
def edit(motorist_id):
    """Create a new driver"""
    if request.method == "POST":
        tag = request.form.get("tag")
        MotoristsQuerys.update_tag(motorist_id, tag)
        return redirect(url_for("drivers_app.get_motorits"))

    driver = MotoristsQuerys.get_id(motorist_id)
    groups = RulesQuery.get_all()
    groups = tuple(map(lambda groups: groups.name, groups))

    return render_template("pages/motorists/edit.html", driver=driver, groups=groups)


@drivers_app.route("/revenues/show/<motorist_id>", methods=["POST", "GET"])
def revenues(motorist_id):
    """Create a new driver"""
    if request.method == "POST":
        name = request.form.get("name")
        data_json = {"comission": "default"}
        MotoristsQuerys.new(name, data_json)
        RunsQuerys.create_table(name)
        return redirect(url_for("drivers_app.create"))

    driver = MotoristsQuerys.get_id(motorist_id)

    return render_template("pages/motorists/edit.html", driver=driver)


@drivers_app.route("/delete_all_drivers", methods=["GET"])
def delete_all():
    """Create a new driver"""
    MotoristsQuerys.delete_all()

    return redirect(url_for("drivers_app.get_motorits"))
