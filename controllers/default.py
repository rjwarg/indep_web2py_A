# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    
    rows = db(db.case_master).select()
    return locals()

def get_members():
    members = db(db.members.last_name.startswith(request.args[0])).select()
    return locals()

def show_ajax():
    if request.vars.id:
       response.flash = "Now create a case for this person"
#        redirect(URL('get_member', vars={'id':request.vars.id}))
    return locals()

def edit_case():
    testing = "testing"
    case_number = request.args(1)
    if case_number == 'new':
        case_number = new_case_number()
        form = SQLFORM(db.case_master)
        form.vars.case_number = case_number
        form.vars.member_id = 1001
        
    else:
        case = db.case_master(request.args(0))
        form = SQLFORM(db.case_master, case)
        
    if form.process(session=None, formname='indep').accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill in the form'
        
    return locals()

def name_selector():
    
        
    if not request.vars.last_name: return ''
    
    pattern = request.vars.last_name.upper() + '%' 
    query = db.members.last_name.like(pattern)
    if request.vars.first_name:
         pattern = request.vars.first_name.upper() + '%' 
         query &= db.members.first_name.like(pattern)
            
    if request.vars.minst:
         pattern = request.vars.minst.upper() + '%' 
         query &= db.members.minst.like(pattern)
     
    selected = [{'last_name':row.last_name, 'first_name':row.first_name, 'minst':row.minst, 'id':str(row.id)}for row in
               db(query).select(orderby=db.members.last_name | db.members.first_name, limitby=(0,25))]
#    return "testing away"
    #db(db.member.name.like(pattern)).select(orderby=db.member.name, limitby=(0, 15))]
    return ''.join([DIV(k['last_name']+', '+k['first_name'] +', '+k['minst'],
                       _onclick="set_text('" +k['last_name']+"','"+k['first_name']+"','"+k['minst']+"','"+k['id']+"')",
                       _onmouseover="this.style.backgroundColor='yellow'",
                       _onmouseout="this.style.backgroundColor='white'"
                       ).xml() for k in selected])

     

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())