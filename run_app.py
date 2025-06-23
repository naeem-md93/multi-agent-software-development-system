from masds.modules.masds import MultiAgentSoftwareDevelopmentSystem


def main():
    print("Multi-Agent Software Development System")
    print("=" * 50)

    project_description = """
    # AI-Powered Merchandise Template Generator
    
    ## Project Overview
    Create a Python script that automatically generates branded merchandise 
    templates (coffee mugs, business cards, etc.) by analyzing client websites.
    
    ## Core Requirements
    
    ### Website Analysis Module
    - Parse homepage HTML/CSS from provided URL
    - Extract and download logo assets (PNG, SVG, JPG)
    - Capture full-page screenshots
    - Extract brand colors from CSS/images
    - Identify typography and design patterns
    
    ### AI Integration
    - LLM Integration: Analyze website content and generate style descriptions
    - Vision AI: Process logos/screenshots to understand brand aesthetics
    - Generate design recommendations based on visual analysis
    
    ### Template Generation
    - Create merchandise templates (focus: coffee mugs)
    - Include text elements and photo placement areas
    - Apply extracted brand colors and styling
    - Output print-ready design files (PNG/PDF)
    
    ## Technical Stack
    - Python 3.8+
    - Web scraping (BeautifulSoup, Selenium)
    - Image processing (PIL/OpenCV)
    - AI APIs (OpenAI GPT-4V, Google Vision, or similar)
    - Design generation (Cairo, Pillow, or design libraries)
    
    ## Deliverables
    - Complete Python script with documentation
    - Sample outputs from 3 test websites
    - Setup instructions and requirements.txt
    - Error handling for edge cases
    
    ## Timeline: 7-14 days
    """
    project_dir = "mtg"
    ignore_dirs = [".venv", "test_env", "venv", ".idea", ".git", "__pycache__"]
    ignore_indexes = [".pyc"]
    system = MultiAgentSoftwareDevelopmentSystem(project_dir)
    system.develop_a_project(project_description, ignore_dirs, ignore_indexes)


if __name__ == "__main__":
    main()