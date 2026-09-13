"""
Script cap nhat so do Sequence Diagram (Hinh 2.3 va Hinh 2.4) trong file Word:
- Thay the media/image9.png va media/image10.png bang file anh phan giai cuc cao 300 DPI, phong chu to, ro net.
- Dieu chinh kich thuoc wp:extent va a:ext len chuan 15.5 cm chieu rong (vua khit le in A4).
- Chen ngat trang (Page Break) giua Hinh 2.3 va Hinh 2.4 de 2 so do khong bi chen chuc, moi so do chiem tron 1 trang dep mat.
"""
import os
import sys
import zipfile
import shutil
import xml.etree.ElementTree as ET

DOCX_IN = r"c:\Users\dathao\Downloads\AI\Bao_Cao_3_Bai_Kiem_Tra_Backup_Da_Sua.docx"
DOCX_OUT = r"c:\Users\dathao\Downloads\AI\Bao_Cao_3_Bai_Kiem_Tra_Backup_Da_Sua.docx"
DOCX_FALLBACK = r"c:\Users\dathao\Downloads\AI\Bao_Cao_3_Bai_Kiem_Tra_Backup_Hoan_Thien.docx"

IMG_2_3 = r"c:\Users\dathao\Downloads\AI\ExpenseAI\scratch\sharp_hinh_2_3.png"
IMG_2_4 = r"c:\Users\dathao\Downloads\AI\ExpenseAI\scratch\sharp_hinh_2_4.png"

# Kich thuoc moi tinh theo EMU (1 cm = 360000 EMU)
# Chieu rong 15.5 cm = 5580000 EMU
# sharp_hinh_2_3: 4500 x 3150 -> ty le 1.42857 -> Chieu cao: 3906000 EMU (~10.85 cm)
# sharp_hinh_2_4: 4500 x 3000 -> ty le 1.5 -> Chieu cao: 3720000 EMU (~10.33 cm)

CX_NEW = "5580000"
CY_2_3 = "3906000"
CY_2_4 = "3720000"

def update_docx(docx_in, docx_out):
    print(f"Reading {docx_in}...")
    with open(IMG_2_3, "rb") as f:
        img_2_3_bytes = f.read()
    with open(IMG_2_4, "rb") as f:
        img_2_4_bytes = f.read()

    temp_zip_path = docx_in + ".tmp.zip"

    ns = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
    }

    # Dang ky namespace de khi ghi ra XML khong bi mat prefix
    for prefix, uri in ns.items():
        ET.register_namespace(prefix, uri)

    with zipfile.ZipFile(docx_in, 'r') as zin:
        doc_xml_bytes = zin.read('word/document.xml')
        rels_xml_bytes = zin.read('word/_rels/document.xml.rels')

        # Parse XML
        root = ET.fromstring(doc_xml_bytes)

        # 1. Tim cac drawing va cap nhat kich thuoc
        for drawing in root.findall('.//w:drawing', ns):
            blip = drawing.find('.//a:blip', ns)
            if blip is not None:
                embed_id = blip.attrib.get(f"{{{ns['r']}}}embed")
                extent = drawing.find('.//wp:extent', ns)
                xfrm_ext = drawing.find('.//a:xfrm/a:ext', ns)

                if embed_id == 'rId16':  # Hinh 2.3
                    print(f"Updating rId16 (Hinh 2.3) extent to {CX_NEW} x {CY_2_3}")
                    if extent is not None:
                        extent.attrib['cx'] = CX_NEW
                        extent.attrib['cy'] = CY_2_3
                    if xfrm_ext is not None:
                        xfrm_ext.attrib['cx'] = CX_NEW
                        xfrm_ext.attrib['cy'] = CY_2_3

                elif embed_id == 'rId17':  # Hinh 2.4
                    print(f"Updating rId17 (Hinh 2.4) extent to {CX_NEW} x {CY_2_4}")
                    if extent is not None:
                        extent.attrib['cx'] = CX_NEW
                        extent.attrib['cy'] = CY_2_4
                    if xfrm_ext is not None:
                        xfrm_ext.attrib['cx'] = CX_NEW
                        xfrm_ext.attrib['cy'] = CY_2_4
                        
                elif embed_id != 'rId8' and extent is not None:
                    # rId8 la logo ICTU (7x7 cm), giu nguyen
                    # Cac so do khac: tang do rong len toi da 15.0 - 15.2 cm neu chieu cao sau khi scale <= 17.5 cm
                    old_cx = int(extent.attrib.get('cx', 0))
                    old_cy = int(extent.attrib.get('cy', 0))
                    if old_cx > 0 and old_cy > 0:
                        target_cx = int(15.2 * 360000)  # 15.2 cm
                        scale = target_cx / old_cx
                        new_cy = int(old_cy * scale)
                        max_cy = int(17.5 * 360000)     # 17.5 cm
                        if new_cy <= max_cy and scale > 1.0:
                            print(f"Scaling up {embed_id}: {old_cx/360000:.2f}x{old_cy/360000:.2f} -> {target_cx/360000:.2f}x{new_cy/360000:.2f} cm")
                            extent.attrib['cx'] = str(target_cx)
                            extent.attrib['cy'] = str(new_cy)
                            if xfrm_ext is not None:
                                xfrm_ext.attrib['cx'] = str(target_cx)
                                xfrm_ext.attrib['cy'] = str(new_cy)

        # 2. Chen Page Break truoc doan van gioi thieu Hinh 2.4
        body = root.find('w:body', ns)
        page_break_added = False
        for p in body.findall('w:p', ns):
            txt = ''.join(p.itertext())
            if "Hình 2.4 mô tả sơ đồ tuần tự của nghiệp vụ Cố vấn tài chính" in txt:
                print("Found introduction paragraph for Hinh 2.4. Inserting Page Break before it...")
                # Tao element <w:r><w:br w:type="page"/></w:r>
                r_elem = ET.Element(f"{{{ns['w']}}}r")
                br_elem = ET.SubElement(r_elem, f"{{{ns['w']}}}br")
                br_elem.attrib[f"{{{ns['w']}}}type"] = "page"
                
                # Chen vao vi tri dau tien cua doan van
                p.insert(0, r_elem)
                page_break_added = True
                break

        print(f"Page break inserted: {page_break_added}")

        # Convert modified XML back to bytes
        new_doc_xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)

        # Ghi vao file zip tam
        with zipfile.ZipFile(temp_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == 'word/document.xml':
                    zout.writestr(item, new_doc_xml_bytes)
                elif item.filename == 'word/media/image9.png':
                    print("Replacing word/media/image9.png with sharp_hinh_2_3.png...")
                    zout.writestr(item, img_2_3_bytes)
                elif item.filename == 'word/media/image10.png':
                    print("Replacing word/media/image10.png with sharp_hinh_2_4.png...")
                    zout.writestr(item, img_2_4_bytes)
                else:
                    zout.writestr(item, zin.read(item.filename))

    # Ghi de vao file dich
    target = docx_out
    try:
        shutil.copy2(temp_zip_path, target)
        print(f"Successfully updated: {target}")
    except PermissionError:
        target = DOCX_FALLBACK
        shutil.copy2(temp_zip_path, target)
        print(f"Original file is locked by Word! Successfully saved to fallback: {target}")

    if os.path.exists(temp_zip_path):
        os.remove(temp_zip_path)
    return target

if __name__ == "__main__":
    out_path = update_docx(DOCX_IN, DOCX_OUT)
    print(f"DONE: {out_path}")
