import os
from flask_admin import Admin, BaseView, form, expose
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from app.config import BASE_DIR

# Create directory for file fields to use
FILE_PATH = os.path.join(BASE_DIR, 'app', 'static', 'files')

try:
    os.mkdir(FILE_PATH)
except OSError:
    pass

######################
## Admin views
######################

class ProtectedModelView(ModelView):
    '''Check user has logged in for each admin view'''
    def is_accessible(self):
        return current_user.has_role('admin')

class FileView(ProtectedModelView):
    '''Override form field to use Flask-Admin FileUploadField'''
    form_overrides = {
        'path': form.FileUploadField
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'path': {
            'label': 'File',
            'base_path': FILE_PATH,
            'allow_overwrite': False
        }
    }

class RuleView(ProtectedModelView):
    '''Set the view options with displaying a Rule in the admin view'''
    form_excluded_columns = ('created_on', 'updated_on')
    column_searchable_list = ['identifier', 'name', 'description']
    column_default_sort = 'identifier'

class TermView(ProtectedModelView):
    '''Set the view options with displaying a Term in the admin view'''
    form_create_rules = ('name', 'short_description', 'long_description', 'abbreviation', 'owner',
                         'steward', 'status', 'categories', 'links', 'rules', 'documents')
    form_edit_rules = ('name', 'short_description', 'long_description', 'abbreviation', 'owner',
                       'steward', 'status', 'categories', 'links', 'rules', 'related_terms',
                       'documents', 'columns')
    column_list = ['name', 'short_description', 'abbreviation', 'status']
    form_excluded_columns = ('created_on', 'updated_on')
    column_searchable_list = ['name']

class TableView(ProtectedModelView):
    '''Set the view options with displaying a Table in the admin view'''
    column_default_sort = 'name'
    column_filters = ['location', 'name']
    form_excluded_columns = ('columns')

class ColumnView(ProtectedModelView):
    '''Set the view options with displaying a Column in the admin view'''
    column_filters = ['table', 'name']

class BackupView(BaseView):
    '''Add backup option to admin menu'''
    @expose('/')
    def index(self):
        return self.render('backup/backup_restore.html')