import sqlite3 as sql


def get_basic_data():
    conn = sql.connect("CDISC.db")

    codes = conn.execute('SELECT c.Code, c.Term_Type, c.Standard, cl.Submission_Value, cl.Name '
                         'FROM Code c INNER JOIN Codelist cl ON c.Code = cl.Code;').fetchall()

    terms = conn.execute('SELECT c.Code, c.Term_Type, c.Standard, t.Submission_Value '
                         'FROM Code c INNER JOIN Term t ON c.Code = t.Code;').fetchall()
    conn.close()
    return codes, terms


if __name__ == "__main__":
    c, t = get_basic_data()