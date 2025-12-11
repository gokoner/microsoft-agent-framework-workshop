"""
Notebook Presenter - A Streamlit app to present Jupyter notebooks as slides
with split-screen view (explanation + code)
"""

import streamlit as st
import json
import re
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Tutorial Presenter",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better presentation
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Slide container */
    .slide-container {
        min-height: 70vh;
        padding: 1rem;
    }
    
    /* Navigation buttons */
    .nav-button {
        font-size: 1.2rem;
        padding: 0.5rem 2rem;
    }
    
    /* Code blocks */
    .stCode {
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Progress bar */
    .progress-text {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Section header */
    .section-header {
        background: linear-gradient(90deg, #0078d4, #00bcf2);
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Output display */
    .output-box {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 4px;
        font-family: monospace;
        white-space: pre-wrap;
        max-height: 300px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)


def load_notebook(path: str) -> dict:
    """Load a Jupyter notebook from file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_cell_content(cell: dict) -> str:
    """Extract content from a cell."""
    source = cell.get('source', [])
    if isinstance(source, list):
        return ''.join(source)
    return source


def get_cell_output(cell: dict) -> str:
    """Extract output from a code cell."""
    outputs = cell.get('outputs', [])
    result = []
    
    for output in outputs:
        if output.get('output_type') == 'stream':
            text = output.get('text', [])
            if isinstance(text, list):
                result.append(''.join(text))
            else:
                result.append(text)
        elif output.get('output_type') in ['execute_result', 'display_data']:
            data = output.get('data', {})
            if 'text/plain' in data:
                text = data['text/plain']
                if isinstance(text, list):
                    result.append(''.join(text))
                else:
                    result.append(text)
    
    return '\n'.join(result)


def create_slides(notebook: dict) -> list:
    """
    Group cells into logical slides.
    
    Slide markers in markdown cells:
    - `<!-- SLIDE -->` - Force new slide
    - `<!-- SKIP -->` - Skip this cell
    - `---` at start - Section divider (new slide)
    - `## Part` or `# ` - Section header (new slide)
    
    Logic:
    - Each markdown cell with a header starts a new slide
    - Code cells are grouped with the preceding markdown
    - Multiple code cells stay together on one slide
    """
    cells = notebook.get('cells', [])
    slides = []
    current_slide = None
    
    for cell in cells:
        cell_type = cell.get('cell_type')
        content = get_cell_content(cell)
        
        # Skip empty cells
        if not content.strip():
            continue
        
        # Check for SKIP marker
        if '<!-- SKIP -->' in content:
            continue
        
        # Check for forced slide break
        force_new_slide = '<!-- SLIDE -->' in content
        content = content.replace('<!-- SLIDE -->', '').strip()
        
        # Check if this is a section header
        is_section_start = (
            cell_type == 'markdown' and 
            (content.strip().startswith('## Part') or 
             content.strip().startswith('### ') or
             content.strip().startswith('## ') or
             content.strip().startswith('# ') or
             (content.strip().startswith('---') and len(content.strip()) > 3))
        )
        
        # Skip standalone --- dividers
        if cell_type == 'markdown' and content.strip() == '---':
            continue
        
        if cell_type == 'markdown':
            # Save current slide if exists
            if current_slide and current_slide.get('markdown'):
                slides.append(current_slide)
            
            # Clean up the markdown - remove leading ---
            clean_content = content
            if clean_content.strip().startswith('---'):
                lines = clean_content.strip().split('\n')
                clean_content = '\n'.join(lines[1:]).strip()
            
            current_slide = {
                'markdown': clean_content,
                'code': [],
                'outputs': [],
                'is_section': is_section_start,
                'title': extract_title(clean_content)
            }
        
        elif cell_type == 'code':
            if current_slide is None:
                # Standalone code cell - create slide for it
                current_slide = {
                    'markdown': '### Code',
                    'code': [],
                    'outputs': [],
                    'is_section': False,
                    'title': 'Code'
                }
            
            # Add code to current slide
            current_slide['code'].append(content)
            output = get_cell_output(cell)
            current_slide['outputs'].append(output if output else '')
    
    # Don't forget the last slide
    if current_slide and (current_slide.get('markdown') or current_slide.get('code')):
        slides.append(current_slide)
    
    return slides


def extract_title(markdown: str) -> str:
    """Extract title from markdown content."""
    lines = markdown.strip().split('\n')
    for line in lines:
        if line.startswith('#'):
            return line.lstrip('#').strip()
    return "Slide"


def main():
    # File selector
    notebook_dir = Path("/Users/gk/AIFoundryProjects/agent-framework-tutorials")
    notebooks = list(notebook_dir.glob("*.ipynb"))
    
    # Sidebar for notebook selection
    with st.sidebar:
        st.header("📚 Notebook Selector")
        notebook_names = [nb.name for nb in notebooks]
        
        # Default to 19c if available
        default_idx = 0
        for i, name in enumerate(notebook_names):
            if "19c" in name:
                default_idx = i
                break
        
        selected_nb = st.selectbox(
            "Choose notebook:",
            notebook_names,
            index=default_idx
        )
        
        st.markdown("---")
        st.markdown("**Navigation:**")
        st.markdown("- Use ◀ ▶ buttons")
        st.markdown("- Or keyboard: ← →")
        st.markdown("- Jump to slide in sidebar")
    
    # Load notebook
    notebook_path = notebook_dir / selected_nb
    notebook = load_notebook(str(notebook_path))
    slides = create_slides(notebook)
    
    # Session state for slide index
    if 'slide_idx' not in st.session_state:
        st.session_state.slide_idx = 0
    
    # Sidebar slide list
    with st.sidebar:
        st.markdown("---")
        st.header("📑 Slides")
        for i, slide in enumerate(slides):
            title = slide.get('title', extract_title(slide['markdown']))[:35]
            is_current = i == st.session_state.slide_idx
            btn_label = f"{'→ ' if is_current else ''}{i+1}. {title}"
            if st.button(btn_label, key=f"slide_{i}", type="primary" if is_current else "secondary"):
                st.session_state.slide_idx = i
                st.rerun()
    
    # Navigation header
    col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
    
    with col1:
        if st.button("◀ Prev", disabled=st.session_state.slide_idx == 0):
            st.session_state.slide_idx -= 1
            st.rerun()
    
    with col2:
        if st.button("▶ Next", disabled=st.session_state.slide_idx >= len(slides) - 1):
            st.session_state.slide_idx += 1
            st.rerun()
    
    with col3:
        # Progress bar
        progress = (st.session_state.slide_idx + 1) / len(slides)
        st.progress(progress)
        st.markdown(
            f"<p class='progress-text'>Slide {st.session_state.slide_idx + 1} of {len(slides)}</p>",
            unsafe_allow_html=True
        )
    
    with col4:
        # Jump to slide
        jump_to = st.number_input(
            "Go to",
            min_value=1,
            max_value=len(slides),
            value=st.session_state.slide_idx + 1,
            label_visibility="collapsed"
        )
        if jump_to != st.session_state.slide_idx + 1:
            st.session_state.slide_idx = jump_to - 1
            st.rerun()
    
    with col5:
        # Fullscreen hint
        st.markdown("Press **F11**")
    
    st.markdown("---")
    
    # Current slide
    current_slide = slides[st.session_state.slide_idx]
    
    # Section header if applicable
    if current_slide.get('is_section'):
        title = current_slide.get('title', extract_title(current_slide['markdown']))
        st.markdown(
            f"<div class='section-header'><h2>{title}</h2></div>",
            unsafe_allow_html=True
        )
    
    # Split screen layout
    if current_slide['code']:
        # Has code - split screen
        left_col, right_col = st.columns([1, 1])
        
        with left_col:
            st.markdown("### 📖 Explanation")
            # Don't show title again if it's a section header
            markdown_content = current_slide['markdown']
            if current_slide.get('is_section'):
                # Remove the first header line to avoid duplication
                lines = markdown_content.split('\n')
                markdown_content = '\n'.join(
                    line for line in lines 
                    if not line.strip().startswith('#')
                ).strip()
                if not markdown_content:
                    markdown_content = "*See code on the right →*"
            st.markdown(markdown_content)
        
        with right_col:
            st.markdown("### 💻 Code")
            for i, code in enumerate(current_slide['code']):
                # Truncate very long code blocks
                if len(code) > 3000:
                    code = code[:3000] + "\n# ... (truncated)"
                st.code(code, language='python')
                
                # Show output if available
                if i < len(current_slide['outputs']) and current_slide['outputs'][i]:
                    with st.expander("📤 Output", expanded=False):
                        output_text = current_slide['outputs'][i][:1500]
                        st.markdown(
                            f"<div class='output-box'>{output_text}</div>",
                            unsafe_allow_html=True
                        )
    else:
        # Markdown only - full width centered
        st.markdown(current_slide['markdown'])
    
    # Footer with keyboard hint
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #888;'>"
        "💡 Tip: Click in the app and use keyboard arrows ← → to navigate"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
