# coding: utf8
# try something like
import html, datetime

def index(): return dict(message="hello from reports.py")

def cases_pdf():
    
    db_rows = db(db.case_master.assigned_to == auth.user.id).select()
    response.title = "Indep Counsel's Cases"
    
   
    rows = []
   
   

    
   

   
    from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # define our FPDF class (move to modules if it is reused  frequently)
    class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                self.set_font('Arial','B',15)
                self.cell(0,10, response.title ,1,0,'C')
                self.ln(20)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')
                    
    pdf=MyFPDF()
    pdf.add_page()
    pdf.set_font('arial')

    # change the font
    pdf.set_font('helvetica', size=9)
    pdf.set_fill_color(200)
    pdf.cell(25,5,'Case Number',1, fill=True)
    pdf.cell(35,5,'Member Name',1, fill=True)
    pdf.cell(25,5,'Date Assigned',1, fill=True)
    pdf.cell(95,5,'Description',border=1, fill=True )
    pdf.ln(5)
    pdf.ln(5)
    pdf.set_fill_color(255,200,200)
    filler = False
    for row in db_rows:
            pdf.cell(25,5,row.case_number,1, fill=filler)

            pdf.cell(35,5,row.member_id.last_name,1,fill=filler)
            pdf.cell(25,5,str(row.date_assigned),1,fill=filler)
            pdf.multi_cell(95,5,row.description,border=1,fill=filler )
            filler = not filler

       
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')
    

def case_rpt():
    rows = db().select(db.case_master.ALL)
    return dict(rows = rows)

def action_display():
    u = auth.user
    args = request.args
    from_date =args[0]
    to_date = args[1]
    t = type(from_date)
    fd = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
    td = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
    tt = type(fd)
    query = db.case_action.date_performed >= fd
    query &= db.case_action.date_performed <= td
    query &= (db.case_action.case_id == db.case_master.id) 
    query &= (db.case_master.assigned_to == u.id)
    rows =  db(query).select(db.case_action.ALL)# orderby=db.case_action.case_id)

#    rows = []
#    for r in rows_a:
#        if r.case_id.assigned_to == u.id:
#            rows.append(r)
            
    response.title = "Indep Counsel"
    return locals()

def action_rpt():
    u = auth.user
    rows = db(db.case_action.id ).select()
    form = FORM('From Date:', INPUT(_name='from_date', _class='date', widget=SQLFORM.widgets.date.widget, requires=IS_DATE()),
                'To Date:', INPUT( _name='to_date', _class='date', widget=SQLFORM.widgets.date.widget, requires=IS_DATE()),
                INPUT(_type ='submit'))  
    if form.accepts(request,session):
        response.flash = 'form accepted '
        redirect(URL('action_display', args=(request.vars.from_date, request.vars.to_date)))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
        
    response.title = "Indep Counsel"
    return locals()


def case_rtf():

    import gluon.contrib.pyrtf as q
    doc=q.Document()
    ss= doc.StyleSheet
    section=q.Section()
    doc.Sections.append(section)
    para_props = q.ParagraphPS(tabs = [q.TabPS(width= q.TabPS.DEFAULT_WIDTH *3),
                                       q.TabPS(width= q.TabPS.DEFAULT_WIDTH *6),
                                       q.TabPS(width=q.TabPS.DEFAULT_WIDTH *8)])
    p = q.Paragraph(ss.ParagraphStyles.Heading1, para_props)
    p.append('Independent Counsel Case Tracking')
    section.append(p)
    rows = db().select(db.case_master.ALL)
   
    p = q.Paragraph(ss.ParagraphStyles.Heading2, para_props)
    p.append("Case Number", q.TAB, "Member Name", q.TAB, "Assigned Date")
    section.append(p)   
    for row in rows:
        p = q.Paragraph(ss.ParagraphStyles.Normal, para_props)
        p.append(row.case_number,q.TAB, row.member_id.last_name, q.TAB, str(row.date_assigned) )
        section.append(p)
    response.headers['Content-Type']='text/rtf'
    return q.dumps(doc)
