import os
from src.server_manager import start_grobid_server, stop_grobid_server
from src.extract_references import process_pdf_with_grobid, parse_grobid_xml
from src.verify_citations import verify_citation
from src.report_generator import create_word_report

def process_single_file(user_email):
    target_dir = "papers"
    if not os.path.exists(target_dir):
        print(f"System: Directory '{target_dir}' not found. Please create it and add a PDF.")
        return

    pdf_files = [f for f in os.listdir(target_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("System: No PDF files found in the target directory.")
        return

    pdf_file = pdf_files[0]
    pdf_path = os.path.join(target_dir, pdf_file)
    print(f"System: Processing target file: {pdf_file}")

    if not start_grobid_server():
        return

    try:
        xml_result = process_pdf_with_grobid(pdf_path)
        if not xml_result:
            print("System: Extraction failed. Ensure the PDF contains readable text.")
            return
            
        extracted_citations = parse_grobid_xml(xml_result)
        total_citations = len(extracted_citations)
        print(f"System: Extracted {total_citations} citations. Initiating verification matrix...")
        
        stats = {"Verified": 0, "Ghost Citation": 0, "Mismatched Metadata": 0, "Other": 0, "Total": total_citations}
        results_data = []
        
        for ref in extracted_citations:
            # Pass the user's email into the verification engine
            ver_result = verify_citation(ref, user_email)
            status = ver_result.get('status', 'Other')
            
            if status in stats:
                stats[status] += 1
            else:
                stats["Other"] += 1
                
            results_data.append({"reference": ref, "verification": ver_result})
            
        rate = ((stats["Ghost Citation"] + stats["Mismatched Metadata"]) / total_citations) * 100 if total_citations > 0 else 0
        stats["Rate"] = round(rate, 2)
        
        print("System: Generating professional document report...")
        report_path = create_word_report(pdf_file, results_data, stats)
        print(f"System: Process complete. Report saved to: {report_path}")

    finally:
        stop_grobid_server()

if __name__ == "__main__":
    print("\n--- Citation Verification Tool (Single Mode) ---")
    user_email = input("System: Please enter your email address (required by Crossref API for polite pool access): ").strip()
    
    if not user_email or "@" not in user_email:
        print("System: Error - A valid email address is required to proceed.")
    else:
        process_single_file(user_email)