from flask import Flask, render_template, request
import query
from datetime import datetime
import json

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
            codelist_terms[code[0]] = [code[2]]
        else:
            codelist_terms[code[0]] += [code[2]]

    submitted = False

    if request.method == 'POST':
        submitted = True
        codelist = request.form['codelist'].split()[0]
        term = request.form['terms']
        startDate = request.form['start_date']
        endDate = request.form['end_date']

        startDate = datetime.strptime(startDate, '%B %d, %Y').strftime('%Y-%d-%m')
        endDate = datetime.strptime(endDate, '%B %d, %Y').strftime('%Y-%d-%m')

        CL_activeDates, CL_current, CL_changes = query.get_codelist_changes(codelist, startDate, endDate)
        CL_nodes = [{'id': 0, 'label': 'Start'}]
        for element in range(len(CL_changes)):
            CL_nodes.append({'id': element + 1, 'label': 'Stage ' + str(element + 1),
                          'title': 'Change made on ' + '<b><u>' + CL_changes[element][0] + '</b></u>' + '<br>'
                           + '<b>' + 'Original: ' + '</b>' + CL_changes[element][8] + '<br>'
                           + '<b>' + 'New: ' + '</b>' + CL_changes[element][9]})

        CL_edges = []
        for element in range(len(CL_changes)):
            CL_edges.append({'from': element, 'to': element + 1, 'arrows': 'to',
                          'title': '<b>' + 'Change Type: ' + '</b>' + CL_changes[element][5] + '<br>'
                           + '<b>' + 'Summary: ' + '</b>' + CL_changes[element][7] + '<br>'
                           + '<b>' + 'Severity: ' + '</b>' + CL_changes[element][6]})


        term_activeDates, term_current, term_changes = query.get_term_changes(term, startDate, endDate)
        term_nodes = [{'id': 0, 'label': 'Start'}]
        for element in range(len(term_changes)):
            term_nodes.append({'id': element + 1, 'label': 'Stage ' + str(element + 1),
                             'title': 'Change made on ' + '<b><u>' + term_changes[element][0] + '</b></u>' + '<br>'
                                      + '<b>' + 'Original: ' + '</b>' + term_changes[element][8] + '<br>'
                                      + '<b>' + 'New: ' + '</b>' + term_changes[element][9]})

        term_edges = []
        for element in range(len(term_changes)):
            term_edges.append({'from': element, 'to': element + 1, 'arrows': 'to',
                             'title': '<b>' + 'Change Type: ' + '</b>' + term_changes[element][5] + '<br>'
                                      + '<b>' + 'Summary: ' + '</b>' + term_changes[element][7] + '<br>'
                                      + '<b>' + 'Severity: ' + '</b>' + term_changes[element][6]})
        print(CL_edges)
        print(term_edges)
        return render_template('homepage.html', url=host, codelist=codelist, term=term, list_of_codes=list_of_codes,
                               codelist_terms=codelist_terms, submitted=submitted, CL_activeDates=CL_activeDates,
                               CL_current=CL_current, term_activeDates=term_activeDates, term_current=term_current,
                               CL_nodes=json.dumps(CL_nodes), CL_edges=json.dumps(CL_edges),
                               term_nodes=json.dumps(term_nodes), term_edges=json.dumps(term_edges))

    return render_template('homepage.html', url=host, list_of_codes=list_of_codes, submitted=submitted,
                           codelist_terms=codelist_terms)


if __name__ == '__main__':
    app.run()
    # Test Case: Codelist: C101817; Term: C102067
