# High-Performance Data Folder Analyzer

A Python-based tool to analyze folder structures, calculate sizes, and generate detailed reports with tree visualizations.

## Features

*   **Efficient Scanning**: Scans directories without loading everything into RAM.
*   **Tree Visualization**: Generates a visual tree structure of your folders and files.
*   **Filtering**: Filter files by minimum size (e.g., 10MB) and extensions (e.g., .jpg, .mp4).
*   **Detailed Reports**: Saves analysis results to a text file.

## Project Structure

```
.
├── main.py                  # Entry point of the application
├── modules/                 # Core logic package
│   ├── __init__.py
│   ├── engine.py            # Scanning logic
│   ├── utils.py             # Helper functions (size parsing)
│   ├── validators.py        # Input validation
│   └── visualizer.py        # Tree generation
└── output/                  # Generated reports
```

## Usage

Run the script from the terminal using Python.

### Basic Usage

```bash
python main.py "C:/Path/To/Folder"
```

### With Filters

Filter by minimum file size, extensions, and send an email report:

```bash
python main.py "C:/Downloads" --min-size 50MB --ext .zip .exe --email recipient@example.com
```

### Arguments

*   `folder_path`: Path to the target directory (Required).
*   `--min-size`: Minimum file size to include (e.g., `10KB`, `5MB`, `1GB`). Default: `0`.
*   `--ext`: List of file extensions to include (e.g., `.jpg .png`). Default: All.
*   `--output`: Path for the output report file. Default: `output/report.txt`.
*   `--email`: Recipient email address to send the report automatically after analysis.

## Requirements

*   Python 3.6 or higher.

## Setup

1.  **Clone the repository** (if applicable) or download the source code.

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment**:
    *   Windows: `venv\Scripts\activate`
    *   Mac/Linux: `source venv/bin/activate`

4.  **Install dependencies**:
    This project uses `python-dotenv` to manage environment variables. Install the required packages using:
    ```bash
    pip install -r requirements.txt
    ```
    *Or manually:*
    ```bash
    pip install python-dotenv
    ```

## Configuration

1.  **Create a `.env` file** in the root directory of the project.
2.  **Add your email credentials** to the `.env` file as follows:

    ```env
    ANALYZER_EMAIL="your_email@gmail.com"
    ANALYZER_PASSWORD="your_app_password"
    ```

    > **Note:** If you are using Gmail, you must use an **App Password**, not your regular login password. You can generate one in your Google Account settings under Security > 2-Step Verification > App passwords.
