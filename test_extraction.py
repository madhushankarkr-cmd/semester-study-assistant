from pypdf import PdfReader

pdf_path = r"C:\Users\Hari Shankar Kumar\OneDrive\Desktop\semester-study-assistant\data\Computer_Network\syllabus.pdf"

reader = PdfReader(pdf_path)

print("Total Pages:", len(reader.pages))
print("=" * 50)

for i in range(min(2, len(reader.pages))):
    text = reader.pages[i].extract_text()
    
    print(f"\n----- Page {i+1} -----\n")
    if text:
        print(text[:1500])
    else:
        print("❌ No text found on this page")