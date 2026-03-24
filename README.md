# Hallucination Catcher: Privacy-Preserving Citation Verification Pipeline

An open-source, automated tool designed for academic journal editors, peer reviewers, and library professionals to verify the structural integrity of citations in submitted manuscripts.

As the use of Generative AI (LLMs) increases in academic writing, the risk of "hallucinated" (completely fabricated) and mismatched references has grown significantly. Unlike stylistic AI-detectors—which suffer from high false-positive rates and require uploading proprietary manuscripts to third-party cloud servers—this tool operates locally to deterministically fact-check bibliographies against the global Crossref database.

## Key Features
* **Privacy-First Processing:** Extracts text from PDFs locally using an automated GROBID Docker container. Your unpublished manuscripts are never uploaded to OpenAI, Claude, or any external AI company.
* **Deterministic Verification:** Queries the Crossref metadata registry to verify if claimed DOIs and Titles actually exist and correspond to each other.
* **Professional Reporting:** Automatically generates color-coded, easy-to-read Microsoft Word (`.docx`) reports for every processed PDF, highlighting exactly which references need manual editorial review.
* **Zero-Terminal Operation:** Built-in Python wrappers automatically start, monitor, and safely terminate the local AI extraction server in the background.

---

## Understanding the Terminology
When a report is generated, each citation is categorized into one of the following statuses:
1. **Verified:** The citation exists in the global registry, and the title in the PDF matches the registered metadata.
2. **Ghost Citation:** A completely fabricated reference. Neither the claimed DOI nor the Title exists in the academic registry.
3. **Mismatched Metadata:** Often called a "Frankenstein" citation. The Large Language Model provided a 100% real, clickable DOI, but attached it to a completely different (often fake) paper title or author list.

---

## Prerequisites
To run this tool on your local machine, you must have the following installed:
1. **Python (3.8 or higher):** [Download Python](https://www.python.org/downloads/)
2. **Docker Desktop:** This is required to run the local GROBID extraction engine. [Download Docker Desktop](https://www.docker.com/products/docker-desktop/).
   * *Note: Docker Desktop must be open and running in your system tray before you use this tool.*

---

## Installation & Setup

**1. Download the Project**
Clone this repository or download it as a ZIP file and extract it to your computer.

**2. Open your Terminal / Command Prompt**
Navigate to the extracted project folder.

**3. Set up a Virtual Environment (Recommended)**
This keeps the tool's dependencies isolated from your main computer.

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**4. Install Required Libraries**
Install the necessary Python packages using pip:
```bash
pip install requests beautifulsoup4 lxml rapidfuzz pandas python-docx
```

---

## How to Use the Tool

### Step 1: Prepare Your Documents

1. Ensure Docker Desktop is open and running in the background.
2. Inside the project folder, locate or create a folder named `papers`.
3. Place the PDF manuscript(s) you wish to verify into the `papers` folder.

### Step 2: Choose Your Execution Mode

Open your terminal (ensure your virtual environment is active) and run one of the following commands:

**Option A: Single Manuscript Mode**
If you just want to verify one paper rapidly, this mode automatically detects the first PDF in your `papers` folder and generates a Word report.
```bash
python run_single.py
```

**Option B: Batch Mode**
If you have an entire folder of submissions, this mode will process every PDF in the `papers` folder. It will generate individual Word reports for each manuscript, plus a master CSV spreadsheet summarizing the hallucination rates across all papers.
```bash
python run_batch.py
```

### Step 3: Provide Email for API Access

When you run the script, it will prompt you for your email address. This is strictly required by the Crossref API to place you in their "Polite Pool," which guarantees faster and more reliable metadata retrieval.

### Step 4: Review the Output

Once the system completes its run, navigate to the newly created `reports` folder. You will find a formal, color-coded Microsoft Word document detailing the status of every citation found in the manuscript.

---

## Project Structure
```text
Hallucination_Catcher/
│
├── papers/                  # User input directory (Place PDFs here)
├── reports/                 # Output directory (Word documents appear here)
│
├── src/                     # Core system modules
│   ├── __init__.py          
│   ├── server_manager.py    # Manages background Docker/GROBID processes
│   ├── extract_references.py# Parses PDF to XML via local GROBID
│   ├── verify_citations.py  # Crossref API and Fuzzy String Matching logic
│   └── report_generator.py  # Formats output into Microsoft Word
│
├── run_single.py            # Execution script for one document
└── run_batch.py             # Execution script for multiple documents
```

---

## Troubleshooting

* **Error: "Docker runtime not found" or "Failed to start the container"**
  Ensure that Docker Desktop is installed, open, and actively running on your machine. The Docker icon in your system tray should indicate "Engine running."
* **Error: "Service initialization timed out."**
  The first time you run this tool, Docker must download the GROBID image and load large machine-learning models into your computer's RAM. If you possess an older machine, this may take longer than the allotted 120 seconds.
* **Error: "Port is already allocated"**
  You have another program (or a crashed instance of GROBID) using port 8070. Open Docker Desktop, navigate to the "Containers" tab, and manually delete any running GROBID containers.
* **Missing Subtitles or Minor Match Errors**
  The Crossref registry is highly literal. While the tool uses fuzzy string matching to account for missing punctuation, significant discrepancies between how a journal published a title and how an author cited it may occasionally result in a False Positive. Always manually review flagged citations.

---

## License

This project is open-source and available for academic, editorial, and library use.