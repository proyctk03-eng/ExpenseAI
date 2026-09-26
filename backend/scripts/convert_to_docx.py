import os
import pypandoc

docs_dir = r"C:\Users\Admin\Desktop\báo cáo thu chi\docs"
md_files = [f for f in os.listdir(docs_dir) if f.endswith(".md")]

for md in md_files:
    md_path = os.path.join(docs_dir, md)
    docx_path = os.path.join(docs_dir, md.replace(".md", ".docx"))
    pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
