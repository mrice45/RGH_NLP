"""
Module to interact with SQLite DB for CSB Lab tools
"""
import sqlite3 as sql


def db_connect(dbfile):
    """

    :param dbfile:
    :return:
    """
    conn = sql.connect(dbfile, detect_types=sql.PARSE_COLNAMES)
    curs = conn.cursor()

    return curs,conn


def __db_buildquery(search_terms):
    """

    :param search_terms:
    :return:
    """

    placeholder = '?'  # For SQLite. See DBAPI paramstyle.
    placeholders = ', '.join(placeholder for x in search_terms)

    query = 'WITH targetDrugs AS (SELECT d.Id drugId FROM Target t ' \
            'JOIN DrugTarget dt ON t.Id = dt.TargetId ' \
            'JOIN Drug d ON dt.DrugId = d.Id ' \
            'JOIN TargetSynonym TS ON t.Id = TS.TargetId ' \
            'WHERE TS.Synonym IN (%s))' \
            'SELECT DISTINCT d.Name AS Drug, dt.Actions AS Action, t.Name AS Target ' \
            'FROM Target t ' \
            'JOIN DrugTarget dt ON t.Id = dt.TargetId ' \
            'JOIN Drug d ON dt.DrugId = d.Id ' \
            'JOIN targetDrugs td ' \
            'ON d.Id = td.drugId' % placeholders

    return query


def db_findrelations(cursor, search_terms):
    """

    :param cursor:
    :param search_terms:
    :return:
    """
    q = __db_buildquery(search_terms)

    search_terms = tuple([i for i in search_terms])

    cursor.execute(q, search_terms)
    relations = cursor.fetchall()

    return relations


def db_findtarget_bysynonym():
    pass


def db_finddrug_bysynonym():
    pass


def db_addsynonymbylist():
    pass




