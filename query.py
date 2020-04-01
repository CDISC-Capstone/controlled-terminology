import sqlite3 as sql


def get_basic_data():
    conn = sql.connect("CDISC.db")

    codes = conn.execute('SELECT c.Code, c.Term_Type, c.Standard, cl.Submission_Value, cl.Name '
                         'FROM Code c INNER JOIN Codelist cl ON c.Code = cl.Code;').fetchall()

    terms = conn.execute('SELECT c.Code, c.Term_Type, c.Standard, t.Submission_Value '
                         'FROM Code c INNER JOIN Term t ON c.Code = t.Code;').fetchall()
    conn.close()
    return codes, terms


def get_codelist_changes(code, startDate, endDate):
    conn = sql.connect("CDISC.db")

    current = conn.execute('SELECT * FROM Codelist '
                           'WHERE Code = ?;', (code,)).fetchall()

    changes = conn.execute('SELECT * FROM Changes '
                           'WHERE Code = ? AND DATE >= ? AND DATE <= ?;', (code, startDate, endDate)).fetchall()

    conn.close()
    return current, changes


def get_term_changes(code, startDate, endDate):
    conn = sql.connect("CDISC.db")

    current = conn.execute('SELECT * FROM Term '
                           'WHERE Code = ?;', (code,)).fetchall()

    changes = conn.execute('SELECT * FROM Changes '
                           'WHERE Code = ? AND AND DATE >= ? AND DATE <= ?;', (code, startDate, endDate)).fetchall()

    conn.close()
    return current, changes


if __name__ == "__main__":
    pass
