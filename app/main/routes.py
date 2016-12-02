from flask import render_template, request, flash, session, url_for, redirect, jsonify, send_from_directory
from app import app, db
from . import main
from ..models import Document, DocumentType, Term, Category, Person, Link, Location, Table, Column, Rule

from config import BASE_DIR
from flask_security import login_required, current_user
from sqlalchemy import func

import os
import os.path as op

from flask_admin import Admin, form
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules

# WTForms helpers
from ..utils import wtf
wtf.add_helpers(app)

# Create directory for file fields to use
file_path = op.join(BASE_DIR, 'app', 'static', 'files')

try:
    os.mkdir(file_path)
except OSError:
    pass

#####################
#### admin views ####
#####################

class ProtectedModelView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')

class FileView(ProtectedModelView):
	# Override form field to use Flask-Admin FileUploadField
	form_overrides = {
		'path': form.FileUploadField
	}

	# Pass additional parameters to 'path' to FileUploadField constructor
	form_args = {
		'path': {
			'label': 'File',
			'base_path': file_path,
			'allow_overwrite': False
		}
	}

class RuleView(ProtectedModelView):
    form_excluded_columns = ('created_on', 'updated_on')

class TermView(ProtectedModelView):
	form_create_rules = ('term', 'description', 'abbreviation', 'owner',
        'steward', 'status', 'categories', 'links', 'rules', 'documents')
	form_edit_rules = ('term', 'description', 'abbreviation', 'owner',
        'steward', 'status', 'categories', 'links', 'rules', 'related_terms',
        'documents', 'columns')
	column_list = ['term', 'description', 'abbreviation', 'status']
	form_excluded_columns = ('created_on', 'updated_on')
	column_searchable_list = ['term']

class TableView(ProtectedModelView):
	column_default_sort = 'name'
	column_filters = ['location']
	form_excluded_columns = ('columns')

class ColumnView(ProtectedModelView):
	column_filters = ['table', 'name']

admin = Admin(app, name='BUSINESS GLOSSARY', template_mode='bootstrap3', base_template='/admin/new_master.html')

admin.add_view(ProtectedModelView(Category, db.session))
admin.add_view(ProtectedModelView(Person, db.session))
admin.add_view(ProtectedModelView(Link, db.session))
admin.add_view(ProtectedModelView(Location, db.session))
admin.add_view(TableView(Table, db.session))
admin.add_view(ColumnView(Column, db.session))
admin.add_view(FileView(Document, db.session))
admin.add_view(ProtectedModelView(DocumentType, db.session))
admin.add_view(RuleView(Rule, db.session))

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
    admin.add_view(TermView(Term, db.session))

###########################
#### define the routes ####
###########################

@main.route('/about')
def about():
    '''Present the about page'''
    return render_template('about.html')


@main.route('/')
@main.route('/glossary/')
def glossary():
    glossary = Term.query.order_by(Term.term).all()
    return render_template('show_glossary.html', glossary=glossary)


@main.route('/abbreviations/')
def abbreviations():
    glossary = Term.query.filter(Term.abbreviation!="").order_by(Term.abbreviation).all()
    return render_template('show_abbreviations.html', glossary=glossary)

    
@main.route('/profile/')
def profile():
    '''Present the user profile'''
    return render_template('show_profile.html')  

    
@main.route('/term/<int:selected_term>')
@main.route('/term/<string:selected_term_name>')
def show_term(selected_term=None, selected_term_name=None):
    print ">>>>>", selected_term
    print ">>>>>", selected_term_name
    
    if selected_term is None:
        term = Term.query.filter(func.lower(Term.term) == func.lower(selected_term_name)).first()
        if not term:
            return render_template('errors/404.html')
        else:    
            return render_template('show_term.html', term=Term.query.filter(func.lower(Term.term) == func.lower(selected_term_name)).first())
    else:
        return render_template('show_term.html', term=Term.query.filter_by(id=selected_term).first())
    
@main.route('/documents/<int:selected_term>')
def show_documents(selected_term):
	documents = Document.query.order_by(Document.name).all()
	term = Term.query.filter_by(id=selected_term).first()
	documents = term.documents

	return render_template('show_documents.html', term=term, documents=documents)


@main.route('/assets/<int:selected_term>')
def show_assets(selected_term):

	term = Term.query.filter_by(id=selected_term).first()
	assets = term.columns

	return render_template('show_assets.html', term=term, assets=assets)


@main.route('/rules/<int:selected_term>')
def show_rules(selected_term):

	term = Term.query.filter_by(id=selected_term).first()
	rules = term.rules

	return render_template('show_rules.html', term=term, rules=rules)


@main.route('/rule/<int:selected_rule>')
def show_rule(selected_rule):

	rule = Rule.query.filter_by(id=selected_rule).first()

	return render_template('show_rule.html', rule=rule)


@main.route('/rule/documents/<int:selected_rule>')
def show_rule_documents(selected_rule):

    rule = Rule.query.filter_by(id=selected_rule).first()
    documents = rule.documents

    return render_template('show_rule_documents.html', rule=rule, documents=documents)


@main.route('/location/<selected_location>')
@main.route('/location/<selected_location>/details')
def show_location_details(selected_location):

	location = Location.query.filter_by(id=selected_location).first()

	return render_template('show_location_details.html', location=location)


@main.route('/location/<selected_location>/tables')
def show_location_tables(selected_location):

	location = Location.query.filter_by(id=selected_location).first()
	tables = location.tables

	return render_template('show_location_tables.html', location=location, tables=tables)


@main.route('/table/<selected_table>')
@main.route('/table/<selected_table>/details')
def show_table_details(selected_table):

	table = Table.query.filter_by(id=selected_table).first()
	columns = table.columns

	return render_template('show_table_details.html', table=table, columns=columns)


@main.route('/table/<selected_table>/columns')
def show_table_columns(selected_table):

	table = Table.query.filter_by(id=selected_table).first()
	columns = table.columns

	return render_template('show_table_columns.html', table=table, columns=columns)


@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search = request.form['search']

        from sqlalchemy import or_

        terms = Term.query.filter(or_(Term.term.ilike('%' + str(search) + '%'),
                                      Term.description.ilike('%' + str(search) + '%'),
                                      Term.abbreviation.ilike('%' + str(search) + '%'))).all()
        columns = Column.query.filter(Column.name.ilike('%' + str(search) + '%')).all()

        #print "terms=", terms.term

        return render_template("results.html", terms=terms, columns=columns)
    return render_template('search.html')


@main.route('/processes')
def processes():
	return render_template('show_processes.html')


@main.route('/source_code')
def source_code():
    """This is a proof-of-concept for return a position in source code to the browser"""
    filename = '05_ACCT HIST.sas'
    root_dir = os.path.dirname(os.getcwd())
    print root_dir
    return send_from_directory(os.path.join('.', 'static', 'source_code'), filename, as_attachment=False, mimetype='text/html')


@app.route('/graph2')
def graph2():
	return render_template('graph2.html')