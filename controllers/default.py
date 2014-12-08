# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
from datetime import date

@auth.requires_membership('indep')
def index():
    u = auth.user
    response.flash = "who is logged in? " + u.first_name + " " + u.last_name + " " +str( u.id)
    if request.args(0) == None:
        rows = db(db.case_master.date_closed == None and db.case_master.assigned_to == u.id).select()
        case_type = "Active"
    elif request.args(0) == 'C':
        rows = db(db.case_master.date_closed and db.case_master.assigned_to == u.id).select()      
        case_type = "Closed"
    else:
        rows = db(db.case_master and db.case_master.assigned_to == u.id).select()
        case_type = "All"
    return locals()
@auth.requires_login()
def get_members():
    members = db(db.members.last_name.startswith(request.args[0])).select()
    return locals()
@auth.requires_login()
def show_ajax():
    if request.vars.id:
       response.flash = "Now create a case for this person"
       redirect(URL('edit_case', args=(request.vars.id, 'new')))
    return locals()

def edit_action():
    db.case_action.action_id.requires = IS_IN_DB(db,'case_action_master.id', '%(action_name)s')
    action_id = request.args(1)
    if action_id == '0':
        form = SQLFORM(db.case_action)
        form.vars.case_id = request.args(0)
        case_id_name = db.case_master(request.args(0)).case_number
        form.vars.action_id = request.args(1)
        hold = [request.args(1), action_id, "new", case_id_name]
    else:
        action = db.case_action(action_id)
        case_id_name = db.case_master(action.case_id).case_number
        form = SQLFORM(db.case_action, action)
        hold = [request.args(1), action_id, "existing"]
    case_id_name         
    if form.process(session=None, formname='indep').accepted:
        response.flash = 'form accepted'
        if request.env.http_referrer:
            redirect(request.env.http_referrer)
        else:
            redirect(URL('edit_case', args=(request.args(0))))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill in the form'
    return locals()

def edit_case():
    testing = "testing"
    case_number = request.args(1)
    if case_number == 'new':
        case_number = new_case_number()
        form = SQLFORM(db.case_master)
        form.vars.case_number = case_number
        form.vars.member_id = request.args(0)
        form.vars.assigned_to = auth.user.id
        member = db.members(request.args(0))
        hold = 0
        # insert a new case_action record for the assignment
  
    else:
        case = db.case_master(request.args(0))
        member = db.members(case.member_id)
        form = SQLFORM(db.case_master, case)
        # get list of actions
        actions = db(db.case_action.case_id == case.id).select()
        hold = case.id
        
    if form.process(session=None, formname='indep').accepted:
        response.flash = 'form accepted'
        # if this is a new record then insert a new case_action
        if hold ==0:
              db.case_action.insert(case_id = form.vars.id, action_id = 1, date_performed = form.vars.date_assigned)
        redirect(URL('index'))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill in the form'
        
    return locals()

def load_db_members():
    rows = db2(db2.member.stat != 'R').select()
#    db.members.truncate()
    insert_count = 0
    read_count = 0
    for r in rows:
        if db(db.members.member_id == r.id_no).count() == 0:
            db.members.insert(last_name = r.name,
                          first_name = r.first_name,
                          minst = r.minst,
                          address = r.address,
                          zip = r.zip,
                          member_id = r.id_no,
                          stat = r.stat)
            insert_count += 1
        if read_count % 500 == 0:
            response.flash = "Progress Count = " + str(read_count)
            
    rows = insert_count
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
def new_case_number():
    
 
    suffix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    date_part = date.today().strftime("%Y%m%d")
    # howmany cases start with this date?
    count = db(db.case_master.case_number.like(date_part +'%')).count()
    return date_part + suffix[count:count+1]
