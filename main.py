import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Import modules
from modules.validators import get_args, validate_and_normalize_inputs
from modules.engine import analyze_folder_generator
from modules.visualizer import generate_tree
from modules.utils import format_size
from modules.notifier import send_report_email

def main():
    load_dotenv()
    # 1. Setup
    raw_args = get_args()
    # Unpack the 5 returned values (including email)
    folder_path, min_size_bytes, allowed_exts, output_file, recipient_email = validate_and_normalize_inputs(raw_args)

    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Capture Time (Start)
    start_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_timer = time.time()

    print(f"🚀 Starting Scan on: {folder_path}")
    print(f"   - Min Size Filter: {format_size(min_size_bytes)}")
    print(f"   - Extensions: {allowed_exts if allowed_exts else 'All'}")
    if recipient_email:
        print(f"   - Email Alert: Enabled -> {recipient_email}")
    print("-" * 50)

    # 3. Processing
    total_size = 0
    total_files = 0
    
    try:
        # Phase 1: Generate Tree
        progress_tracker = {'count': 0}
        tree_structure = generate_tree(folder_path, "", min_size_bytes, allowed_exts, progress_tracker)
        print(f"\r✅ Tree built! Scanned {progress_tracker['count']} items.            ")

        # Phase 2: Calculate Stats
        print("📊 Calculating Statistics...")
        
        for _, size, _ in analyze_folder_generator(folder_path, min_size_bytes, allowed_exts):
            total_files += 1
            total_size += size
            
            if total_files % 50 == 0:
                sys.stdout.write(f"\r🔍 Analyzing files... Found {total_files}")
                sys.stdout.flush()

        sys.stdout.write(f"\r✅ Analysis complete! Processed {total_files} matching files.      \n")

        # 4. Capture Time (End)
        end_timer = time.time()
        time_spent_seconds = end_timer - start_timer
        
        if time_spent_seconds < 60:
            time_spent_str = f"{time_spent_seconds:.2f} seconds"
        else:
            minutes = int(time_spent_seconds // 60)
            seconds = int(time_spent_seconds % 60)
            time_spent_str = f"{minutes}m {seconds}s"

        # 5. Write Report
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"📁 FOLDER ANALYSIS REPORT\n")
            f.write("="*50 + "\n")
            
            f.write(f"📍 Target Path:   {folder_path}\n")
            f.write(f"📅 Scan Time:     {start_timestamp}\n")
            f.write(f"⏱️ Duration:      {time_spent_str}\n")
            f.write("-" * 50 + "\n")
            f.write(f"🔍 APPLIED FILTERS:\n")
            f.write(f"   • Min File Size: {format_size(min_size_bytes)}\n")
            f.write(f"   • Extensions:    {', '.join(allowed_exts) if allowed_exts else 'All'}\n")
            f.write("="*50 + "\n\n")

            f.write("📊 SUMMARY STATISTICS\n")
            f.write("-" * 30 + "\n")
            f.write(f"📂 Total Files Found: {total_files}\n")
            f.write(f"💾 Total Size:        {format_size(total_size)}\n")
            f.write("\n" + "="*50 + "\n\n")

            f.write("🌳 DIRECTORY TREE STRUCTURE\n")
            f.write("-" * 30 + "\n")
            f.write(f"{os.path.basename(folder_path)}/\n")
            f.write(tree_structure)
            f.write("\n" + "="*50 + "\n")

        print(f"\n✨ Success! Report generated in {time_spent_str}.")
        print(f"📄 Saved to: {os.path.abspath(output_file)}")

        # 6. EMAIL NOTIFICATION LOGIC [NEW]
        if recipient_email:
            print("\n📧 Attempting to send email...")
            
            # Get Credentials from Environment Variables (Secure Way)
            sender_email = os.environ.get("ANALYZER_EMAIL")
            sender_password = os.environ.get("ANALYZER_PASSWORD")

            if not sender_email or not sender_password:
                print("❌ Error: Email credentials not found!")
                print("   Please set 'ANALYZER_EMAIL' and 'ANALYZER_PASSWORD' environment variables.")
            else:
                send_report_email(sender_email, sender_password, recipient_email, output_file, folder_path)

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()