import cv2
import numpy as np

def get_saliency_map(frame):
    # 1. Convert to grayscale and resize for faster processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (160, 120)) # Small scale is better for global saliency
    
    # 2. Spectral Residual Math (The "Lizard Brain" Logic)
    # Perform Fast Fourier Transform
    fft = np.fft.fft2(gray)
    log_amplitude = np.log(np.abs(fft) + 1e-9)
    phase = np.angle(fft)
    
    # Subtract the average "background noise" from the image
    avg_log_amp = cv2.blur(log_amplitude, (3, 3))
    spectral_residual = log_amplitude - avg_log_amp
    
    # Back to spatial domain to find the "Pop-out" features
    saliency = np.abs(np.fft.ifft2(np.exp(spectral_residual + 1j * phase)))
    
    # 3. Post-processing for the "Glow"
    saliency = cv2.GaussianBlur(saliency, (9, 9), 3)
    saliency = cv2.normalize(saliency, None, 0, 1, cv2.NORM_MINMAX)
    
    # Resize back to original frame size
    return cv2.resize(saliency, (frame.shape[1], frame.shape[0]))

# --- MAIN LOOP ---
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    # Calculate the saliency
    saliency_map = get_saliency_map(frame)
    
    # --- VISUALIZATION (Cinematic Aesthetic) ---
    # A. Create a B&W base of reality
    gray_reality = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_reality_bgr = cv2.cvtColor(gray_reality, cv2.COLOR_GRAY2BGR)
    
    # B. Create the Heatmap (Inferno gives that Deep Gold/Red look)
    heatmap_intensity = (saliency_map * 255).astype(np.uint8)
    heatmap_color = cv2.applyColorMap(heatmap_intensity, cv2.COLORMAP_INFERNO)
    
    # C. Blend: Only show color where saliency is high
    mask = cv2.threshold(heatmap_intensity, 50, 255, cv2.THRESH_BINARY)[1]
    mask_inv = cv2.bitwise_not(mask)
    mask_inv_3d = cv2.cvtColor(mask_inv, cv2.COLOR_GRAY2BGR) / 255.0
    mask_3d = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
    
    # Composite: Glowing distractions over a desaturated world
    result = (heatmap_color * mask_3d) + (gray_reality_bgr * mask_inv_3d)
    
    # Add labels for the video demo
    cv2.putText(result, "SALIENCY MIRROR: IDENTIFYING ATTENTION LEAKS", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow('Day 3: The Saliency Mirror', result.astype(np.uint8))
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
