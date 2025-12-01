import os
import re

def remove_review_buttons():
    # Define the patterns to search for
    patterns = [
        # Pattern for most templates
        r'\s*{% if request\.user\.profile\.access_review_queues %}\s*<li class="-item review-button-item reviewSVGOuter revThisIsOuter">\s*<a href="#" class="-link svg-icon iconReviewQueue" onclick="openReviewInbox\(\);">\s*<i class="fa fa-tasks fa-2x iconReviewQueue reviewSVG" aria-hidden="true"></i>\s*</a>\s*</li>\s*{% endif%}',
        # Pattern for login/signup templates
        r'\s*{% if request\.user\.profile\.access_review_queues %}\s*<li class="-item review-button-item reviewSVGOuter revThisIsOuter">\s*<a href="#" class="-link svg-icon iconReviewQueue" onclick="openReviewInbox\(\);">\s*<i class="fa fa-tasks fa-2x iconReviewQueue reviewSVG" aria-hidden="true"></i>\s*</a>\s*</li>\s*{% endif %}' 
    ]
    
    # Files to process
    files_to_process = [
        os.path.join('users', 'templates', 'registration', 'login.html'),
        os.path.join('users', 'templates', 'registration', 'signup.html')
    ]
    
    # Process each file
    for file_path in files_to_process:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
        try:
            # Read the file
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove all patterns
            new_content = content
            for pattern in patterns:
                new_content = re.sub(pattern, '', new_content, flags=re.DOTALL)
            
            # If content changed, write it back
            if new_content != content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {full_path}")
        except Exception as e:
            print(f"Error processing {full_path}: {str(e)}")

if __name__ == "__main__":
    remove_review_buttons()
