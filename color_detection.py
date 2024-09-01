import cv2
import numpy as np
from webcolors import rgb_to_name

# Initialize global variables
click_x, click_y = None, None
color_updated = False

def mouse_callback(event, x, y, flags, param):
    """Callback function to capture mouse click."""
    global click_x, click_y, color_updated
    if event == cv2.EVENT_LBUTTONDOWN:
        click_x, click_y = x, y
        color_updated = True

def get_color_name(rgb):
    """Convert RGB color to a color name."""
    try:
        return rgb_to_name(rgb)
    except ValueError:
        return "Unknown"

def color_to_hex(rgb):
    """Convert RGB color to HEX."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def average_color(img, x, y, size=10):
    """Average the color in a region around the click."""
    x_start = max(x - size, 0)
    x_end = min(x + size, img.shape[1])
    y_start = max(y - size, 0)
    y_end = min(y + size, img.shape[0])
    
    region = img[y_start:y_end, x_start:x_end]
    avg_color = np.mean(region, axis=(0, 1))
    
    return tuple(reversed(avg_color.astype(int)))  # Convert BGR to RGB

def apply_median_filter(img, ksize=5):
    """Apply median filter to reduce noise."""
    return cv2.medianBlur(img, ksize)

def draw_color_overlay(img, color, color_name, color_hex):
    """Draw a color overlay with swatch and text."""
    overlay = np.zeros((220, 400, 3), dtype=np.uint8)
    
    # Draw rounded rectangle for color swatch
    cv2.rectangle(overlay, (10, 10), (160, 190), (0, 0, 0), 2)
    overlay[10:190, 10:160] = color[::-1]  # Color swatch
    
    # Draw rounded rectangle for text area
    cv2.rectangle(overlay, (180, 10), (390, 210), (0, 0, 0), 2)
    
    # Put text on the overlay
    cv2.putText(overlay, f'Color Name:', (190, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(overlay, f'{color_name}', (190, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(overlay, f'Color HEX:', (190, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(overlay, f'{color_hex}', (190, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(overlay, f'RGB: {color}', (190, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return overlay

def main():
    global click_x, click_y, color_updated

    # Open the camera
    cap = cv2.VideoCapture(0)  # Try changing the index if 0 does not work

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video capture.")
        return

    # Set up the mouse callback
    cv2.namedWindow('Video Feed')
    cv2.setMouseCallback('Video Feed', mouse_callback)

    while True:
        # Capture frame-by-frame
        ret, img = cap.read()

        # Check if the frame was captured successfully
        if not ret:
            print("Error: Failed to capture image.")
            break

        # Apply median filter to reduce noise
        filtered_img = apply_median_filter(img)

        # Convert to HSV color space
        hsv_img = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2HSV)

        # Draw crosshair on the image
        if click_x is not None and click_y is not None:
            cv2.drawMarker(img, (click_x, click_y), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)

        # Display the resulting frame
        cv2.imshow('Video Feed', img)

        # If a click has occurred, process the color
        if color_updated:
            if 0 <= click_x < img.shape[1] and 0 <= click_y < img.shape[0]:
                # Get the average color in a region around the clicked position
                pixel_color_rgb = average_color(filtered_img, click_x, click_y)
                
                # Convert the RGB color to HEX
                pixel_color_hex = color_to_hex(pixel_color_rgb)
                
                # Get the color name
                pixel_color_name = get_color_name(pixel_color_rgb)
                
                # Print color information to the console
                print(f'Clicked Position: ({click_x}, {click_y})')
                print(f'Color Name: {pixel_color_name}')
                print(f'Color HEX: {pixel_color_hex}')
                print(f'RGB: {pixel_color_rgb}')
                
                # Create an overlay with color swatch and information
                color_overlay = draw_color_overlay(img, pixel_color_rgb, pixel_color_name, pixel_color_hex)
                
                # Display the color overlay
                cv2.imshow('Color Info', color_overlay)
                
                # Reset color update flag
                color_updated = False
            else:
                print("Click coordinates out of frame bounds.")
                color_updated = False

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('x'):
            break

    # Release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
