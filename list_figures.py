import docx
doc_path = r'C:\Users\dathao\Desktop\Bao_Cao_Hoan_Chinh_ExpenseAI.docx'
try:
    doc = docx.Document(doc_path)
    with open('figures.txt', 'w', encoding='utf-8') as f:
        for p in doc.paragraphs:
            if 'Hình ' in p.text and ':' in p.text:
                f.write(p.text.strip() + '\n')
except Exception as e:
    pass
