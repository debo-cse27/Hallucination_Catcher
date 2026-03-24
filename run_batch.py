import os
import csv
from src.server_manager import start_grobid_server, stop_grobid_server
from src.extract_references import process_pdf_with_grobid, parse_grobid_xml
from src.verify_citations import verify_citation
from src.report_generator import create_word_report

def process_batch_files(user_email):
    target_dir = "papers"
    output_csv = "batch_summary_report.csv"
    
    if not os.path.exists(target_dir):
        print(f"System: Directory '{target_dir}' not found.")
        return

    pdf_files = [f for f in os.listdir(target_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("System: No PDF files found in the target directory.")
        return

    print(f"System: Batch processing initialized for {len(pdf_files)} files.")

    if not start_grobid_server():
        return

    csv_data = []

    try:
        for index, pdf_file in enumerate(pdf_files, 1):
            pdf_path = os.path.join(target_dir, pdf_file)
            print(f"\n[{index}/{len(pdf_files)}] Processing: {pdf_file}")
            
            xml_result = process_pdf_with_grobid(pdf_path)
            if not xml_result:
                print(f"  -> Skipping {pdf_file}: Document extraction failed.")
                continue
                
            extracted_citations = parse_grobid_xml(xml_result)
            total_citations = len(extracted_citations)
            
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
            
            create_word_report(pdf_file, results_data, stats)
            
            csv_data.append({
                "Filename": pdf_file,
                "Total Citations": total_citations,
                "Verified": stats["Verified"],
                "Ghost Citations": stats["Ghost Citation"],
                "Mismatched Metadata": stats["Mismatched Metadata"],
                "Errors": stats["Other"],
                "Hallucination Rate (%)": stats["Rate"]
            })
            
        print("\nSystem: Generating master CSV summary...")
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ["Filename", "Total Citations", "Verified", "Ghost Citations", "Mismatched Metadata", "Errors", "Hallucination Rate (%)"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in csv_data:
                writer.writerow(row)
                
        print("System: Batch processing complete. Individual Word reports are located in the 'reports' folder.")

    finally:
        stop_grobid_server()

if __name__ == "__main__":
    print("\n--- Citation Verification Tool (Batch Mode) ---")
    user_email = input("System: Please enter your email address (required by Crossref API for polite pool access): ").strip()
    
    if not user_email or "@" not in user_email:
        print("System: Error - A valid email address is required to proceed.")
    else:
        process_batch_files(user_email)