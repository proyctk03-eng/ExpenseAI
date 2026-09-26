import docx
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT

doc_path = r'C:\Users\dathao\Desktop\Bao_Cao_Hoan_Chinh_ExpenseAI.docx'
try:
    doc = docx.Document(doc_path)
    
    for table in doc.tables:
        table.autofit = True
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Force width to 100% (5000 in pct units = 100.0%)
        tbl_pr = table._tbl.tblPr
        tbl_w = tbl_pr.first_child_found_in("w:tblW")
        if tbl_w is None:
            tbl_w = OxmlElement('w:tblW')
            tbl_pr.append(tbl_w)
            
        tbl_w.set(qn('w:w'), '5000')
        tbl_w.set(qn('w:type'), 'pct')
            
    doc.save(doc_path)
    print("Tables adjusted successfully.")
except Exception as e:
    print('Error:', e)
