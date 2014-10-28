# coding: utf8
# try something like
import html, datetime

def index(): return dict(message="hello from reports.py")

def cases_pdf():
    
    db_rows = db(db.case_master).select()
    response.title = "Indep Counsel's Cases"
    
    # define header and footers:
    head = THEAD(TR(TH("case number",_width="20%"), 
                    TH("Descr",_width="50%"),
                    TH("Active date",_width="20%"), 
                    _bgcolor="#A0A0A0"))
    foot = TFOOT(TR(TH("Footer 1",_width="20%"), 
                    TH("Footer 2",_width="60%"),
                    TH("Footer 3",_width="20%"),
                    _bgcolor="#E0E0E0"))
    
    # create several rows:
    rows = []
    rows.append("Helloworld's best")
    for row in db_rows:
        rows.append(TR(TD(row.case_number, _width="20%"),
                          TD(row.description, _width="50%"),
                          TD(str(row.date_assigned)), _width="20%"  ))

    
    # make the table object
    body = TBODY(*rows)
    print body
    table = TABLE(*[head,foot, body], 
                  _border="1", _align="center", _width="100%")

    if request.extension=="pdf":
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
        data = "<table border='1' align='center' width='100%'> "
        data += "<tr bgcolor='#a0a0a0'><th width='20%'>case number</th><th width='50%'>Description<th width='20%'>Assigned</th> </tr>"
        data += "<tr><td width='20%'>Hollywood's Best</td><td width='50%'>&lt; &gt; &amp;</td><td width='20%'></td></tr>"
        for row in db_rows:
             data += "<tr><td width='20%'>"+row.case_number+"</td><td width='50%'>"+row.description+"</td><td width='20%'>"+str(row.date_assigned)+"</td></tr>"
                
        data += "</table>"
        f=open('tempdata.txt', 'w')
        f.write("\nDATA FROM XML\n")
        pdf.write_html(data)
        f.write(data)
        f.write('\nDATA FROM TABLE\n')
        pdf.write_html(str(XML(table, sanitize=False)))
        # inspect the html
       
        f.write(str(XML(table)))
        f.flush()
        response.headers['Content-Type']='application/pdf'
        return pdf.output(dest='S')
    else:
        # normal html view:
        return locals()

def case_rpt():
    rows = db().select(db.case_master.ALL)
    return dict(rows = rows)

def action_display():
    args = request.args
    from_date =args[0]
    to_date = args[1]
    t = type(from_date)
    fd = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
    td = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
    tt = type(fd)
    query = db.case_action.date_performed >= fd
    query &= db.case_action.date_performed <= td
    rows =  db(query).select(orderby=db.case_action.case_id)
    ttt = type(rows[0].date_performed)
    response.title = "Indep Counsel"
    return locals()

def action_rpt():
    rows = db().select(db.case_action.ALL)
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
