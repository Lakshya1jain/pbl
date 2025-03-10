from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
import base64
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
SCRIPT_FOLDER = 'blender_scripts'
API_KEY = 'AIzaSyAKUIqHZ-5Nk-QzS4QL0oaN5qFTDJ3nMUg'  # Replace with your actual API key

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SCRIPT_FOLDER, exist_ok=True)

# Function to process image with Gemini API using a detailed prompt
def process_with_gemini(image_path):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    # Convert image to Base64
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode('utf-8')

    headers = {"Content-Type": "application/json"}

    # Enhanced prompt for accurate 3D model generation
    detailed_prompt = """
    Generate a complete Blender Python script that creates a proportionally accurate 3D model based on the provided 2D blueprint. 
    
    CRITICALLY IMPORTANT REQUIREMENTS:
    1. All walls and structures must be positioned EXACTLY ON THE GROUND (z=0)
    2. Use realistic proportions - standard wall height should be 2.4m to 3m
    3. Wall thickness should be 0.15-0.2m (not too thin or thick)
    4. Use a consistent scale throughout the model (if using metric: meters, if imperial: feet)
    5. Any doors should be 2-2.2m high and positioned at floor level
    6. Any windows should be at a reasonable height (typically 1m from floor)
    7. Position the camera to provide a good overview of the completed model
    
    The script must:
    1. Clear the existing Blender scene
    2. Use properly scaled cubes/planes for walls and floors
    3. Add appropriate materials (simple colors are fine)
    4. Set up basic lighting for visibility
    5. Include export functionality to save as a .glb file
    6. ABSOLUTELY NO floating elements - everything must connect to the ground or other structures
    
    ONLY respond with the Python script code - no additional text, explanations, or commentary.
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": detailed_prompt
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/png",  # Adjust based on actual image format
                            "data": base64_image
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 4096,
            "temperature": 0.2
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            response_json = response.json()
            blender_script = response_json['candidates'][0]['content']['parts'][0]['text']
            
            # Clean up the script - extract just the Python code if there are markdown code blocks
            if "```python" in blender_script and "```" in blender_script:
                # Extract code between python code blocks
                code_block_pattern = r"```python\s*(.*?)\s*```"
                matches = re.findall(code_block_pattern, blender_script, re.DOTALL)
                if matches:
                    blender_script = matches[0]
            
            # Verify script has basic requirements
            if "bpy.ops.object.select_all" not in blender_script:
                print("Script is missing scene clearing. Regenerating...")
                return process_with_gemini_reflection(image_path, blender_script)
                
            return blender_script
        except Exception as e:
            print(f"Error extracting script: {e}")
            return None
    else:
        print(f"API Error: {response.status_code}")
        try:
            print(response.json())
        except:
            print("Could not parse error response")
        return None

# Function to refine the script using self-reflection
def process_with_gemini_reflection(image_path, previous_script):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    reflection_prompt = f"""
    The following Blender Python script has issues with proportions and placement. It should create a 3D model based on a 2D blueprint, but the objects are floating above the ground and have unrealistic proportions.
    
    Previous script:
    ```python
    {previous_script}
    ```
    
    Please improve this script with these specific corrections:
    1. ALL objects must be positioned at ground level (z=0) or connected to other structures
    2. Use standard wall heights of 2.4-3 meters
    3. Use realistic wall thickness (0.15-0.2m)
    4. Ensure consistent scaling throughout
    5. Add a simple floor plane beneath the structure
    6. Add basic lighting for better visibility
    7. Use a camera position that provides a good overview
    
    Only respond with the corrected Python script - no explanations or comments outside the code.
    """
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": reflection_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 4096,
            "temperature": 0.2
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        try:
            response_json = response.json()
            improved_script = response_json['candidates'][0]['content']['parts'][0]['text']
            
            # Clean up the script - extract just the Python code if there are markdown code blocks
            if "```python" in improved_script and "```" in improved_script:
                # Extract code between python code blocks
                code_block_pattern = r"```python\s*(.*?)\s*```"
                matches = re.findall(code_block_pattern, improved_script, re.DOTALL)
                if matches:
                    improved_script = matches[0]
            
            return improved_script
        except Exception as e:
            print(f"Error in reflection process: {e}")
            return previous_script
    else:
        print(f"API Error during reflection: {response.status_code}")
        return previous_script

# Route to handle image upload
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    print(f"Processing image: {filepath}")
    
    # Process image with Gemini API to get Blender script
    blender_script = process_with_gemini(filepath)
    
    if not blender_script:
        return jsonify({'error': 'Failed to generate Blender script'}), 500
    
    # Store the Blender script
    script_path = os.path.join(SCRIPT_FOLDER, f'{os.path.splitext(filename)[0]}_blender_script.py')
    with open(script_path, 'w') as script_file:
        script_file.write(blender_script)
    
    print(f"Blender script successfully stored at: {script_path}")
    
    return jsonify({
        'script_path': script_path,
        'message': 'Blender script generated and stored successfully'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')