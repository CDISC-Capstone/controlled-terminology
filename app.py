from flask import Flask, render_template, request
import query
from datetime import datetime
import json
import textwrap

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'

@app.route('/', methods=['GET', 'POST'])
def home():
    '''
    codelists: [(Code, Term Type, Standard, Submission Value, Name)]
    terms: [(Code, Term Type, Standard, Submission Value)]
    '''
    codelists = query.get_codelist_data()
    list_of_codes = [(c[0], c[4]) for c in codelists]

    codelist_terms_query = query.get_codelist_term()
    codelist_terms = {}
    for code in codelist_terms_query:
        if code[0] not in codelist_terms:
            codelist_terms[code[0]] = [code[2] + " - " + code[3]]
        else:
            codelist_terms[code[0]] += [code[2] + " - " + code[3]]
    submitted = False

    if request.method == 'POST':
        submitted = True
        codelist = request.form['codelist'].split()[0]
        startDate = request.form['start_date']
        endDate = request.form['end_date']
        startDate = datetime.strptime(startDate, '%B %d, %Y').strftime('%Y-%d-%m')
        endDate = datetime.strptime(endDate, '%B %d, %Y').strftime('%Y-%d-%m')

        CL_activeDates, CL_current, CL_changes = query.get_codelist_changes(codelist, startDate, endDate)

        CL_nodes = [{'id': 0, 'label': 'Start'}]
        for element in range(len(CL_changes)):

            original_CL = CL_changes[element][8].replace("'", "`")
            new_CL = CL_changes[element][9].replace("'", "`")

            if len(original_CL) > 60 and len(new_CL) > 60:

                original_lines = textwrap.TextWrapper(width=50)
                new_lines = textwrap.TextWrapper(width=50)
                original_list = original_lines.wrap(text=original_CL)
                new_list = new_lines.wrap(text=new_CL)

                original, new = "", ""
                for word in original_list:
                    original += word + "<br>"
                for word in new_list:
                    new += word + "<br>"

                CL_nodes.append({'id': element + 1, 'label': CL_changes[element][0],
                                   'title': 'Change made on ' + '<b><u>' + CL_changes[element][0] + '</b> </u>'
                                            + '<br>' + '<b>' + 'Original: ' + '</b>' + original +
                                            '<b>' + 'New: ' + '</b>' + new})

            elif len(original_CL) > 60:
                original_lines = textwrap.TextWrapper(width=50)
                original_list = original_lines.wrap(text=original_CL)

                original = ""
                for word in range(len(original_list)):
                    if word == len(original_list) - 1:
                        original += original_list[word]
                    else:
                        original += original_list[word] + "<br>"

                CL_nodes.append({'id': element + 1, 'label': CL_changes[element][0],
                                   'title': 'Change made on ' + '<b><u>' + CL_changes[element][0] + '</b> </u>'
                                            + '<br>' + '<b>' + 'Original: ' + '</b>' + original
                                            + '<br>' + '<b>' + 'New: ' + '</b>' + new_CL})

            elif len(new_CL) > 60:
                new_lines = textwrap.TextWrapper(width=50)
                new_list = new_lines.wrap(text=new_CL)

                new = ""
                for word in range(len(new_list)):
                    if word == len(new_list) - 1:
                        new += new_list[word]
                    else:
                        new += new_list[word] + "<br>"

                CL_nodes.append({'id': element + 1, 'label': CL_changes[element][0],
                                   'title': 'Change made on ' + '<b><u>' + CL_changes[element][0] + '</b> </u>'
                                            + '<br>' + '<b>' + 'Original: ' + '</b>' + original_CL
                                            + '<br>' + '<b>' + 'New: ' + '</b>' + new})

            else:
                CL_nodes.append({'id': element + 1, 'label': CL_changes[element][0],
                              'title': 'Change made on ' + '<b><u>' + CL_changes[element][0] + '</b></u>' + '<br>'
                               + '<b>' + 'Original: ' + '</b>' + original_CL + '<br>'
                               + '<b>' + 'New: ' + '</b>' + new_CL})

        CL_edges = []
        for element in range(len(CL_changes)):
            if CL_changes[element][6] == "Minor":
                color = "green"
            elif CL_changes[element][6] == "Moderate":
                color = "#fc8003"
            elif CL_changes[element][6] == "Major":
                color = "#fc0b03"
            else:
                color = "gray"

            CL_edges.append({'from': element, 'to': element + 1, 'arrows': 'to', 'color': color,
                          'title': '<b>' + 'Change Type: ' + '</b>' + CL_changes[element][5] + '<br>'
                           + '<b>' + 'Summary: ' + '</b>' + CL_changes[element][7] + '<br>'
                           + '<b>'+ 'Severity: ' + '</b>' + CL_changes[element][6]})

        CL_options = {
            'interaction': {
                'tooltipDelay': 3600000}
        }

        if request.form.get('terms') is not None:
            term = request.form['terms'].split(" ")[0]
            term_activeDates, term_current, term_changes = query.get_term_changes(term, startDate, endDate)

            term_nodes = [{'id': 0, 'label': 'Start'}]
            for element in range(len(term_changes)):

                original_term = term_changes[element][8].replace("'", "`")
                new_term = term_changes[element][9].replace("'", "`")

                if len(original_term) > 60 and len(new_term) > 60:

                    original_lines = textwrap.TextWrapper(width=50)
                    new_lines = textwrap.TextWrapper(width=50)
                    original_list = original_lines.wrap(text=original_term)
                    new_list = new_lines.wrap(text=new_term)

                    original, new = "", ""
                    for word in original_list:
                        original += word + "<br>"
                    for word in new_list:
                        new += word + "<br>"

                    term_nodes.append({'id': element + 1, 'label': term_changes[element][0],
                                       'title': 'Change made on ' + '<b><u>' + term_changes[element][0] + '</b> </u>'
                                                + '<br>' + '<b>' + 'Original: ' + '</b>' + original +
                                                '<b>' + 'New: ' + '</b>' + new})

                elif len(original_term) > 60:

                    original_lines = textwrap.TextWrapper(width=50)
                    original_list = original_lines.wrap(text=original_term)

                    original = ""
                    for word in range(len(original_list)):
                        if word == len(original_list) - 1:
                            original += original_list[word]
                        else:
                            original += original_list[word] + "<br>"

                    term_nodes.append({'id': element + 1, 'label': term_changes[element][0],
                                       'title': 'Change made on ' + '<b><u>' + term_changes[element][0] + '</b> </u>'
                                        + '<br>' + '<b>' + 'Original: ' + '</b>' + original
                                        + '<br>' + '<b>' + 'New: ' + '</b>' + new_term})

                elif len(new_term) > 60:

                    new_lines = textwrap.TextWrapper(width=50)
                    new_list = new_lines.wrap(text=new_term)

                    new = ""
                    for word in range(len(new_list)):
                        if word == len(new_list) - 1:
                            new += new_list[word]
                        else:
                            new += new_list[word] + "<br>"

                    term_nodes.append({'id': element + 1, 'label': term_changes[element][0],
                                       'title': 'Change made on ' + '<b><u>' + term_changes[element][0] + '</b> </u>'
                                        + '<br>' + '<b>' + 'Original: ' + '</b>' + original_term
                                        + '<br>' + '<b>' + 'New: ' + '</b>' + new})

                else:
                    term_nodes.append({"id": element + 1, "label": term_changes[element][0],
                                     "title": "Change made on " + "<b><u>" + term_changes[element][0] + "</b></u>" + "<br>"
                                      + "<b>" + "Original: " + "</b>" + original_term + "<br>"
                                      + "<b>" + "New: " + "</b>" + new_term})

            term_edges = []
            for element in range(len(term_changes)):
                if term_changes[element][6] == "Minor":
                    color = "green"
                elif term_changes[element][6] == "Moderate":
                    color = "#fc8003"
                elif term_changes[element][6] == "Major":
                    color = "#fc0b03"
                else:
                    color = "gray"

                term_edges.append({'from': element, 'to': element + 1, 'arrows': 'to', 'color': color,
                                 'title': '<b>' + 'Change Type: ' + '</b>' + term_changes[element][5] + '<br>'
                                          + '<b>' + 'Summary: ' + '</b>' + term_changes[element][7]+ '<br>'
                                          + '<b>' + 'Severity: ' + '</b>' + term_changes[element][6]})
            term_options = {
                'interaction': {
                    'tooltipDelay': 3600000}
            }

            return render_template('homepage.html', url=host, codelist=codelist, term=term, list_of_codes=list_of_codes,
                                   codelist_terms=codelist_terms, submitted=submitted, CL_activeDates=CL_activeDates,
                                   CL_current=CL_current, term_activeDates=term_activeDates, term_current=term_current,
                                   term_empty=False, CL_nodes=json.dumps(CL_nodes), CL_edges=json.dumps(CL_edges),
                                   term_nodes=json.dumps(term_nodes), term_edges=json.dumps(term_edges),
                                   CL_options=json.dumps(CL_options), term_options=json.dumps(term_options))

        else:
            return render_template('homepage.html', url=host, codelist=codelist, list_of_codes=list_of_codes,
                                   codelist_terms=codelist_terms, submitted=submitted, CL_activeDates=CL_activeDates,
                                   CL_current=CL_current, CL_nodes=json.dumps(CL_nodes), CL_edges=json.dumps(CL_edges),
                                   CL_options=json.dumps(CL_options), term_empty=True)

    return render_template('homepage.html', url=host, list_of_codes=list_of_codes, submitted=submitted,
                           codelist_terms=codelist_terms)


if __name__ == '__main__':
    app.run()
    # Test Case: Codelist: C101817; Term: C102067
