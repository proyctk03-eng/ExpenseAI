import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    # Remove existing shd if any
    for shd in tcPr.findall(qn('w:shd')):
        tcPr.remove(shd)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_vAlign(cell, align="center"):
    tcPr = cell._element.get_or_add_tcPr()
    # Remove existing vAlign if any
    for vAlign in tcPr.findall(qn('w:vAlign')):
        tcPr.remove(vAlign)
    vAlign = OxmlElement('w:vAlign')
    vAlign.set(qn('w:val'), align)
    tcPr.append(vAlign)

doc_path = r'C:\Users\dathao\Desktop\nhom2test.docx'

try:
    doc = docx.Document(doc_path)
    print("Loaded document successfully.")
    
    for table in doc.tables:
        table.style = 'Table Grid'
        
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                # 1. Vertically center all cells
                set_cell_vAlign(cell, "center")
                
                # 2. Header row specifics
                if r_idx == 0:
                    set_cell_background(cell, "D9E2F3") # Light blue
                else:
                    # Ensure no blue background for body cells (transparent)
                    set_cell_background(cell, "FFFFFF")
                
                # 3. Paragraph alignment & font
                cell_text = cell.text.strip()
                for p in cell.paragraphs:
                    # Alignment
                    if r_idx == 0:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    else:
                        if c_idx == 0 or c_idx == 1:
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        else:
                            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                            
                    # Font settings
                    for run in p.runs:
                        run.font.name = 'Times New Roman'
                        rPr = run._element.get_or_add_rPr()
                        rFonts = rPr.get_or_add_rFonts()
                        rFonts.set(qn('w:eastAsia'), 'Times New Roman')
                        
                        if r_idx == 0:
                            run.bold = True
                        else:
                            run.bold = False

    doc.save(doc_path)
    print("Done formatting tables to match the new image perfectly.")

except Exception as e:
    print("Error:", e)
