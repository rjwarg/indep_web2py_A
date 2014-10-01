# coding: utf8
db.define_table('members',
                Field('last_name', 'string'),
                Field('first_name','string'),
                Field('minst', 'string'),
                Field('address', 'string'),
                Field('zip', 'string'),
                auth.signature)

db.define_table('case_action_master',
                Field('action_name'),
                Field('action_value'),
                auth.signature)



db.define_table('case_master',
                Field('case_number'),
                Field('member_id', 'reference members'),
                Field('description','text'),
                Field('date_assigned', 'date'),
                Field('date_closed','date'),
                Field('dead_file_box_number'),
                auth.signature)

db.define_table('case_action',
                Field('case_id', 'reference case_master'),
                Field('action_id', 'reference case_action_master'),
                Field('date_performed', 'date'),
                Field('remarks', 'text'),
                auth.signature)


from gluon.contrib.populate import populate
if db(db.auth_user).count() <2:
    populate(db.auth_user, 10)
    db.commit()
    

if db(db.members).count() < 2:
    populate(db.members, 500)
    db.commit()

if db(db.case_master).count()<2:
    populate(db.case_master, 10)
    db.commit()
