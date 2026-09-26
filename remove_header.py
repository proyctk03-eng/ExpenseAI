import docx

doc_path = r'C:\Users\dathao\Desktop\Bao_Cao_Hoan_Chinh_ExpenseAI.docx'
try:
    doc = docx.Document(doc_path)
    removed_count = 0
    for section in doc.sections:
        header = section.header
        for paragraph in header.paragraphs:
            if paragraph.text.strip():
                removed_count += 1
                paragraph.text = ''
    doc.save(doc_path)
    print(f'Successfully removed {removed_count} header paragraphs.')
except Exception as e:
    print(f'Error: {e}')
