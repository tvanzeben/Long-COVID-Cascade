import os
import subprocess
import glob

def main():
    os.makedirs('public', exist_ok=True)
    pdf_files = glob.glob('*.pdf')
    if not pdf_files:
        print("Error: No PDF file found in the root directory!")
        return
    pdf_path = pdf_files[0]
    print(f"Found PDF: {pdf_path}")
    # Convert PDF pages to PNG images
    print("Converting PDF to images...")
    subprocess.run([
        'pdftoppm', '-png', '-r', '150',
        pdf_path, 'public/page'
    ], check=True)
    page_images = sorted(glob.glob('public/page-*.png'))
    total_pages = len(page_images)
    print(f"Generated {total_pages} pages.")
    page_files = [os.path.basename(p) for p in page_images]
    # Extract full text from PDF for AI readability
    print("Extracting text from PDF...")
    result = subprocess.run(
        ['pdftotext', '-layout', pdf_path, '-'],
        capture_output=True, text=True, check=True
    )
    pdf_text = result.stdout
    # Escape for safe HTML embedding
    pdf_text_escaped = (
        pdf_text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flipbook - {pdf_path}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #1e1e24;
            color: #fff;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .container {{
            text-align: center;
            max-width: 90vw;
        }}
        .page-container {{
            background: #fff;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 20px;
            display: flex;
            justify-content: center;
        }}
        img {{
            max-width: 100%;
            max-height: 80vh;
            display: block;
        }}
        .controls {{
            display: flex;
            gap: 15px;
            align-items: center;
            justify-content: center;
        }}
        button {{
            background: #4f46e5;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        button:hover {{ background: #4338ca; }}
        button:disabled {{
            background: #4b5563;
            cursor: not-allowed;
        }}
        #page-info {{ font-size: 18px; font-weight: 500; }}
        #ai-text {{
            display: none;
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="page-container">
        <img id="flipbook-page" src="{page_files[0]}" alt="Page 1">
    </div>
    <div class="controls">
        <button id="prev-btn" onclick="changePage(-1)" disabled>Previous</button>
        <span id="page-info">Page <span id="current-page">1</span> of {total_pages}</span>
        <button id="next-btn" onclick="changePage(1)" {"disabled" if total_pages <= 1 else ""}>Next</button>
    </div>
</div>
<!-- Full manuscript text for AI/machine readability. Not displayed to human readers. -->
<div id="ai-text" aria-hidden="true">
<pre>{pdf_text_escaped}</pre>
</div>

<script>
    const pages = {page_files};
    let currentIndex = 0;
    const pageImg = document.getElementById('flipbook-page');
    const currentPageSpan = document.getElementById('current-page');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    function changePage(direction) {{
        currentIndex += direction;
        pageImg.src = pages[currentIndex];
        currentPageSpan.textContent = currentIndex + 1;
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex === pages.length - 1;
    }}
    document.addEventListener('keydown', (e) => {{
        if (e.key === 'ArrowLeft' && currentIndex > 0) changePage(-1);
        if (e.key === 'ArrowRight' && currentIndex < pages.length - 1) changePage(1);
    }});
</script>
</body>
</html>
"""
    with open('public/index.html', 'w') as f:
        f.write(html_content)
    print("Flipbook build complete! Saved to public/")

if __name__ == '__main__':
    main()
