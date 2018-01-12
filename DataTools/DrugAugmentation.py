from DataTools import network_datatools as nw, ps_datatools as ps, DB_datatools as db

[curs, conn] = db.db_connect('drugbank_1_9.db')
alias_list = nw.findaliases(ps.ps_read_entitylist('CFS_entities.csv'))

answers = []
# for i in alias_list:
#     answers.append(db.db_findrelations(curs, i))
#     print(i)

test = db.db_findtargetsynonyms(curs, 'Adrenocorticotropic hormone receptor')
db.closeconnections(conn, curs)

answers
