#!/usr/bin/env python3
"""
Gradio Web App Wrapper for PDF-to-HTML Converter
Provides drag-and-drop interface for the pdf2html CLI tool.

Features:
- Drag and drop PDF upload
- Folder selection (batch mode)
- Custom flags (body-only, no-toc, theme)
- Progress tracking
- Vercel one-click deploy button
- Live HTML preview
"""

import os
import subprocess
import sys
from pathlib import Path

try:
    import gradio as gr
except ImportError:
    print("Error: gradio not found. Install with: pip install gradio")
    sys.exit(1)

# Constants
DEFAULT_OUTPUT_DIR = "output"
PDF2HTML_SCRIPT = "/opt/pdf2html/pdf2html"

def convert_pdf(pdf_path, output_dir, body_only=False, no_toc=False, theme="modern"):
    """Run pdf2html CLI with custom options."""
    cmd = [PDF2HTML_SCRIPT, pdf_path]
    
    # Add output directory
    if output_dir:
        cmd.extend(["-o", output_dir])
    
    # Add custom flags
    if body_only:
        cmd.append("--body-only")
    if no_toc:
        cmd.append("--no-toc")
    
    # Add theme
    if theme:
        cmd.extend(["--theme", theme])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def convert_folder(folder_path, output_dir, body_only, no_toc, theme):
    """Convert all PDFs in a folder."""
    try:
        result = subprocess.run(
            [PDF2HTML_SCRIPT, folder_path, "-o", output_dir, "--batch"],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def deploy_to_vercel():
    """Show deployment instructions for Vercel."""
    return """
# 🚀 Deploy to Vercel

## Prerequisites
```bash
npm install -g vercel
```

## Quick Deploy
```bash
vercel --prod
```

## Access Your Site
```bash
vercel ls
```

Your site will be live at: https://your-project.vercel.app
"""

# Custom CSS
THEME_MODERN = """
body {{
    font-family: 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #ffffff;
    min-height: 100vh;
    padding: 40px 20px;
}}

header {{
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
}}

.logo {{
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 20px;
}}
"""

THEME_MINIMAL = """
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #ffffff;
    color: #333333;
}}

.container {{
    max-width: 800px;
    margin: 0 auto;
}}

.logo {{
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 15px;
}}
"""

def create_ui():
    """Create Gradio interface."""
    with gr.Blocks(theme=gr.themes.Soft) as demo:
        gr.Markdown(
            """
## 📄 PDF to HTML Converter
            
Drag and drop your PDF files or select a folder to convert.
            """
        )
        
        with gr.Tab("Convert"):
            with gr.Row():
                pdf_input = gr.File(
                    label="📄 Upload PDF",
                    file_types=[".pdf"],
                    file_count=1
                )
                
                output_name = gr.Textbox(
                    label="📁 Output name",
                    placeholder="converted",
                    value="index"
                )
                
                output_dir = gr.Textbox(
                    label="📁 Output directory",
                    placeholder="output/",
                    value="output/"
                )
            
            with gr.Row():
                body_only = gr.Checkbox(
                    label="🎯 Body content only",
                    value=False
                )
                
                no_toc = gr.Checkbox(
                    label="📋 Skip Table of Contents",
                    value=False
                )
                
                theme = gr.Radio(
                    label="🎨 Theme",
                    choices=["modern", "minimal"],
                    value="modern"
                )
        
        with gr.Tab("Batch Convert"):
            folder_input = gr.Textbox(
                    label="📁 Folder path",
                    placeholder="/path/to/pdfs",
                    info="Local path or drag and drop folder here"
                )
            
            with gr.Row():
                output_dir_batch = gr.Textbox(
                    label="📁 Output directory",
                    placeholder="output/",
                    value="output/"
                )
            
            with gr.Row():
                body_only_batch = gr.Checkbox(
                    label="🎯 Body content only",
                    value=False
                )
                
                no_toc_batch = gr.Checkbox(
                    label="📋 Skip Table of Contents",
                    value=False
                )
        
        with gr.Tab("Deploy"):
            gr.Markdown(
                """
## 🚀 Deploy to Vercel
            
Get a shareable link to your converted HTML file with one click.
            
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

Your site will be live at: https://your-project.vercel.app
            """
            )
        
        with gr.Row():
            convert_btn = gr.Button("🔄 Convert", variant="primary", size="lg")
            convert_batch_btn = gr.Button("📦 Batch Convert", variant="primary", size="lg")
            deploy_btn = gr.Button("🚀 Deploy to Vercel", variant="secondary", size="lg")
        
        with gr.Row():
            preview_output = gr.Code(
                label="👁 Live Preview",
                language="html",
                interactive=False
            )
            
            progress_output = gr.Textbox(
                label="⏳ Status",
                lines=3,
                max_lines=10
            )
        
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear", variant="secondary")
            copy_btn = gr.Button("📋 Copy Commands")
        
        # Event handlers
        convert_btn.click(
            fn=lambda f, on, d, b, nt, th: handle_convert(f, on, d, b, nt, th),
            inputs=[pdf_input, output_name, output_dir, body_only, no_toc, theme],
            outputs=[progress_output]
        )
        
        convert_batch_btn.click(
            fn=lambda f: handle_batch(f, d, b, nt, th),
            inputs=[folder_input, output_dir_batch, body_only_batch, no_toc_batch, theme],
            outputs=[progress_output]
        )
        
        deploy_btn.click(
            fn=show_deploy_instructions,
            outputs=[progress_output]
        )
        
        clear_btn.click(
            fn=lambda: "",
            outputs=[progress_output]
        )
        
        copy_btn.click(
            fn=generate_command,
            inputs=[pdf_input, output_name, output_dir, body_only, no_toc, theme],
            outputs=[progress_output]
        )

def handle_convert(pdf_file, output_dir, body_only, no_toc, theme):
    """Handle single PDF conversion."""
    if not pdf_file:
        return "❌ No PDF file selected"
    
    yield "⏳ Reading PDF..."
    
    # Get file path
    pdf_path = pdf_file.name
    
    result = convert_pdf(pdf_path, output_dir, body_only, no_toc, theme)
    
    if result.startswith("Error"):
        yield f"❌ {result}"
    else:
        # Find output file
        output_dir_path = output_dir.rstrip('/')
        output_file = Path(output_dir_path) / (output_dir_path if output_dir_path else "output") / f"{Path(pdf_path).stem}.html"
        
        yield f"""
✅ Conversion complete!

📄 Output: `{output_file}`
📊 File size: {output_file.stat().st_size / 1024:.1f} KB

Preview will appear below...
        """
        
        # Read and display preview
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                preview_content = f.read()
                yield f"\n👁 {preview_content}"

        except Exception as e:
            yield f"⚠️ Could not read preview: {e}"

def handle_batch(folder_path, output_dir, body_only, no_toc, theme):
    """Handle batch folder conversion."""
    if not folder_path:
        return "❌ No folder path provided"
    
    folder = folder_path.strip()
    
    if not os.path.isdir(folder):
        return f"❌ Folder not found: {folder}"
    
    yield "⏳ Scanning folder..."
    
    try:
        pdf_count = len([f for f in Path(folder).iterdir() if f.suffix.lower() == '.pdf'])
        
        yield f"📊 Found {pdf_count} PDF files"
        yield "⏳ Starting batch conversion..."
        
        result = convert_folder(folder, output_dir, body_only, no_toc, theme)
        
        if result.startswith("Error"):
            yield f"❌ {result}"
        else:
            output_dir_path = output_dir.rstrip('/')
            yield f"""
✅ Batch conversion complete!

📁 Folder: {folder}
📊 Processed: {pdf_count} files
📁 Output: {output_dir}/index.html

You can now deploy this directory to Vercel.
            """

    except Exception as e:
        yield f"❌ Batch error: {e}"

def show_deploy_instructions(*args):
    """Show Vercel deployment instructions."""
    return deploy_to_vercel()

def generate_command(pdf_file, output_dir, body_only, no_toc, theme):
    """Generate CLI command for users to copy."""
    parts = ["/opt/pdf2html/pdf2html"]
    
    if pdf_file:
        parts.append(pdf_file.name)
    
    if output_dir and output_dir != "output/":
        parts.extend(["-o", output_dir])
    
    if body_only:
        parts.append("--body-only")
    if no_toc:
        parts.append("--no-toc")
    if theme and theme != "modern":
        parts.extend(["--theme", theme])
    
    return "```bash\n" + " ".join(parts) + "\n```"

def verify_pdf2html():
    """Check if pdf2html is installed and accessible."""
    if os.path.exists(PDF2HTML_SCRIPT):
        return "✅ pdf2html found at: " + PDF2HTML_SCRIPT
    else:
        return "❌ pdf2html not found. Install with:\n\n```bash\nsudo mkdir -p /opt/pdf2html\nsudo cp pdf2html /opt/pdf2html/\nsudo chmod +x /opt/pdf2html/pdf2html\n\n```\n\nCheck system-wide PATH:\n```bash\nexport PATH=\"/opt/pdf2html:$PATH\"\n```\n"

if __name__ == "__main__":
    # Verify installation
    verify_result = verify_pdf2html()
    print(verify_result)
    
    # Create Gradio UI
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )
