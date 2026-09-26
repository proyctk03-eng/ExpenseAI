import docx

doc_path = r'C:\Users\dathao\Desktop\Bao_Cao_Hoan_Chinh_ExpenseAI.docx'
try:
    doc = docx.Document(doc_path)
    found_41 = False
    found_42 = False
    found_43 = False

    for p in doc.paragraphs:
        text = p.text.lower()
        if '4.1' in text and ('kết quả' in text or 'ket qua' in text):
            found_41 = True
        if '4.2' in text and ('hạn chế' in text or 'han che' in text):
            found_42 = True
        if '4.3' in text and ('hướng phát triển' in text or 'huong phat trien' in text):
            found_43 = True

    print(f'Found 4.1: {found_41}')
    print(f'Found 4.2: {found_42}')
    print(f'Found 4.3: {found_43}')
except Exception as e:
    print(f'Error: {e}')
