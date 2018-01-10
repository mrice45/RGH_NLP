from DataTools import network_datatools as nw, ps_datatools as ps, DB_datatools as db

[curs, conn] = db.db_connect('drugbank_1_9.db')
alias_list = nw.findaliases(ps.ps_read_entitylist('CFS_entities.csv'))

print(type(alias_list[26]))

answers = db.db_findrelations(curs, alias_list[26])

print(answers)
