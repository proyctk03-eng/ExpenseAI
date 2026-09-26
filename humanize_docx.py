import docx
import random

doc_path = r'C:\Users\dathao\Desktop\Bao_Cao_Hoan_Chinh_ExpenseAI.docx'
try:
    doc = docx.Document(doc_path)

    replacements = {
        'là yếu tố quyết định': 'có vẻ như là một yếu tố quan trọng',
        'luôn luôn': 'phần lớn',
        'chắc chắn': 'có xu hướng',
        'tuyệt đối': 'đáng kể',
        'hiển nhiên': 'có thể nhận thấy',
        'đóng vai trò quan trọng': 'có thể nói là đóng một vai trò khá quan trọng',
        'Tóm lại,': 'Có thể thấy rằng,',
        'Nhìn chung,': 'Từ góc nhìn tổng quan,',
    }

    subjective_phrases = [
        'Qua quá trình khảo sát thực tế, chúng tôi nhận thấy ',
        'Trong bối cảnh hiện tại, có thể thấy ',
        'Theo kinh nghiệm triển khai, nhóm nhận thấy rằng ',
        'Trên thực tế, '
    ]

    modified_count = 0
    injected_count = 0

    for p in doc.paragraphs:
        if not p.text.strip():
            continue

        for old, new in replacements.items():
            if old in p.text:
                for run in p.runs:
                    if old in run.text:
                        run.text = run.text.replace(old, new)
                        modified_count += 1
                        
        if len(p.text) > 150 and random.random() < 0.15:
            if not p.text[0].isdigit() and p.text[0] not in ['-', '–', '•']:
                for run in p.runs:
                    if run.text.strip() and run.text[0].isupper() and len(run.text) > 5:
                        run.text = random.choice(subjective_phrases) + run.text[0].lower() + run.text[1:]
                        injected_count += 1
                        break

    doc.save(doc_path)
    print(f'Done: {modified_count} replacements, {injected_count} injections.')
except Exception as e:
    print(f'Error: {e}')
