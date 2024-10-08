# pylint: disable=unused-argument
"""Revenues Querys"""


from src.database.db_connection import db_connector
# from src.database.models import Rules


class RulesQuery:
    """Revenes Sql Querys"""

    @classmethod
    @db_connector
    def create(cls, connection, rule):
        """Create a driver rule"""
        new_rule = Rules(
            name=rule["name"],
            rule_type=rule["rule_type"],
            data_json={
                "tag": rule["tag"],
                "field": rule["field"],
                "condition": rule["condition"],
                "condition_value": int(rule["condition_value"]),
                "rule": rule["rule"],
                "rule_value": int(rule["rule_value"]),
                },
        )

        connection.session.add(new_rule)
        connection.session.commit()

        return new_rule.id

    @classmethod
    @db_connector
    def get_all(cls, connection):
        """Get all drives groups in database"""
        return connection.session.query(Rules).all()

    @classmethod
    @db_connector
    def update_porcent(cls, connection, rule_id,rule):
        """Update a porcent."""
        _rule: Rules = (
            connection.session.query(Rules).filter_by(id=rule_id).first()
        )

        _rule.name = rule["name"]
        _rule.data_json = rule

        connection.session.commit()


    @classmethod
    @db_connector
    def get_group_by_name(cls, connection, name):
        """Get a drive's groups with driver name."""
        return connection.session.query(Rules).filter_by(name=name).first()

    @classmethod
    @db_connector
    def get_group_by_id(cls, connection, driver_id):
        """Get a drive's groups with driver id."""
        return (
            connection.session.query(Rules).filter_by(id=driver_id).first()
        )

    @classmethod
    @db_connector
    def delete(cls, connection, group_id):
        """Delete a drive's groups with driver id."""
        driver = (
            connection.session.query(Rules).filter_by(id=group_id).first()
        )

        connection.session.delete(driver)
        connection.session.commit()
