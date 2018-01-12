"""
Module to interact with SQLite DB for CSB Lab tools
"""
import sqlite3 as sql


def db_connect(dbfile):
    """
    connect to DB and return cursor and db connection.
    :param dbfile:
    :return: Database Cursor, Connection
    """
    conn = sql.connect(dbfile, detect_types=sql.PARSE_COLNAMES)
    curs = conn.cursor()

    return curs,conn


def __db_buildquery(search_terms):
    """
    Build query to find drug target interactions --- Should be renamed at some point
    :param search_terms:
    :return:
    """

    placeholder = '?'  # For SQLite. See DBAPI paramstyle.
    placeholders = ', '.join(placeholder for x in search_terms)

    query = 'WITH targetDrugs AS (SELECT d.Id drugId FROM Target t ' \
            'JOIN DrugTarget dt ON t.Id = dt.TargetId ' \
            'JOIN Drug d ON dt.DrugId = d.Id ' \
            'JOIN TargetSynonym TS ON t.Id = TS.TargetId ' \
            'WHERE TS.Synonym IN (%s) AND d.IsApproved = "1")' \
            'SELECT DISTINCT d.Name AS Drug, dt.Actions AS Action, t.Name AS Target ' \
            'FROM Target t ' \
            'JOIN DrugTarget dt ON t.Id = dt.TargetId ' \
            'JOIN Drug d ON dt.DrugId = d.Id ' \
            'JOIN targetDrugs td ' \
            'ON d.Id = td.drugId' % placeholders

    return query


def __splitterms(search_terms):
    """
    Internal function to split search term strings by ;
    :param search_terms:
    :return: list of search terms
    """
    return search_terms.split(';')


def db_findrelations(cursor, search_terms):
    """
    Find all the Drug Target relations, as well as off Target drug relations of
    relevant drugs
    :param cursor:
    :param search_terms:
    :return: List of drug relations
    """

    if isinstance(search_terms, str):
        search_terms = __splitterms(search_terms)

    q = __db_buildquery(search_terms)

    search_terms = tuple([i for i in search_terms])

    cursor.execute(q, search_terms)
    relations = cursor.fetchall()

    relations = [list(i) for i in relations]

    return relations


def db_findtarget_bysynonym():
    pass


def db_finddrug_bysynonym():
    pass


def db_addsynonymbylist():
    pass


def db_findtargetsynonyms(curs, target):
    """
    Finds all the synonyms of a given target.
    :param curs: Cursor
    :param target: Target to be searched
    :return: List of all the target's synonyms
    """
    query = 'SELECT Synonym FROM TargetSynonym JOIN Target T ON TargetSynonym.TargetId = T.Id WHERE T.Name = ?'
    target = (target,)
    curs.execute(query, target)
    synonyms = curs.fetchall()
    synonyms = [list(i) for i in synonyms]
    return synonyms


def closeconnections(conn, curs):
    """
    Closes DB cursor and connection
    :param conn:
    :param curs:
    :return:
    """

    curs.close()
    conn.close()

