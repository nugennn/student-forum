import os
import re

def remove_review_buttons():
    # Define the pattern to search for
    pattern = r'\s*{% if request\.user\.profile\.access_review_queues %}\s*<li class="-item review-button-item reviewSVGOuter revThisIsOuter">\s*<a href="#" class="-link svg-icon iconReviewQueue" onclick="openReviewInbox\(\);">\s*<i class="fa fa-tasks fa-2x iconReviewQueue reviewSVG" aria-hidden="true"></i>\s*</a>\s*</li>\s*{% endif %}' 
    
    # Directory to search in
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    # Walk through all files in the templates directory
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    # Read the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Remove the pattern
                    new_content = re.sub(pattern, '', content, flags=re.DOTALL)
                    
                    # If content changed, write it back
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    remove_review_buttons()
