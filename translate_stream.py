# ISL Gemini Multimodal Stream Translator
import os
import time
import cv2
from PIL import Image
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Check for API Key
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please set it in a .env file.")

# Initialize the Gemini Client
client = genai.Client(api_key=API_KEY)

def capture_and_translate():
    print("Initializing Camera Capture...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
        
    print("Press 'c' to capture a sign segment (3 seconds) or 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        cv2.imshow("ISL Gemini Translator", frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c'):
            print("Recording gesture...")
            frames = []
            for _ in range(30): # capture 30 frames
                r, f = cap.read()
                if r:
                    frames.append(f)
                    cv2.imshow("ISL Gemini Translator", f)
                    cv2.waitKey(50)
            
            # Save temporary video or frames
            temp_path = "temp_gesture.gif"
            print("Processing video clip for Gemini...")
            pil_images = [Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)) for f in frames]
            pil_images[0].save(temp_path, save_all=True, append_images=pil_images[1:], duration=100, loop=0)
            
            # Send file to Gemini
            print("Sending to Gemini for analysis...")
            try:
                # Upload the gesture gif
                media_file = client.files.upload(file=temp_path)
                
                # Wait for upload processing if required
                while media_file.state.name == "PROCESSING":
                    time.sleep(1)
                    media_file = client.files.get(name=media_file.name)
                
                # Query Gemini
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        media_file,
                        "Translate this Indian Sign Language gesture video clip into English text. Just return the translated word or sentence."
                    ]
                )
                print(f"\nResult: {response.text.strip()}\n")
                
                # Cleanup remote file
                client.files.delete(name=media_file.name)
            except Exception as e:
                print(f"API Error: {e}")
                
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        elif key == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_translate()
