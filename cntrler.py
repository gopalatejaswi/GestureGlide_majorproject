import pyautogui
import pygetwindow as gw
import time
import platform
import sys


class Master_control():
    def __init__(self):
        super().__init__()
        
        
    def zoom_in(self,times=1):
        """Zoom in using keyboard shortcuts"""
        modifier = 'ctrl' if platform.system() != 'Darwin' else 'command'
        for _ in range(times):
            pyautogui.hotkey(modifier, '+')
            time.sleep(0.2)
    
    def zoom_out(self,times=1):
        """Zoom out using keyboard shortcuts"""
        modifier = 'ctrl' if platform.system() != 'Darwin' else 'command'
        for _ in range(times):
            pyautogui.hotkey(modifier, '-')
            time.sleep(0.2)
    
    def move_an_application(self,app_title, x, y):
        try:
            # Find the window using pygetwindow
            window = gw.getWindowsWithTitle(app_title)[0]
            
            if not window:
                raise Exception(f"Window not found: {app_title}")
        
            # Activate the window
            window.activate()
            time.sleep(0.5)  # Wait for window to activate
            # Calculate absolute coordinates
            abs_x = window.left + x
            abs_y = window.top + y
            # Move and click using pyautogui
            pyautogui.moveTo(abs_x, abs_y)
            pyautogui.click()
        
            print(f"Clicked at ({x}, {y}) in window: {app_title}")
        except Exception as e:
            print(f"Error: {e}")

    def click_on_application(self,app_title, x, y, click_delay=0.5):
        """
        Click at specific coordinates within an application window
        :param app_title: Partial or full window title
        :param x: X coordinate relative to window
        :param y: Y coordinate relative to window
        :param click_delay: Delay before clicking (seconds)
        """
        try:
            # Find the window
            windows = gw.getWindowsWithTitle(app_title)
            if not windows:
                raise Exception(f"No windows found with title containing: {app_title}")
        
            window = windows[0]
        
            # Special handling for macOS
            if platform.system() == 'Darwin':
                window.activate()
                time.sleep(1)  # Extra delay for macOS
                # macOS requires this additional step
                pyautogui.moveTo(window.left + x, window.top + y)
                time.sleep(0.2)
                pyautogui.click()
            else:
                # Windows/Linux
                window.activate()
                time.sleep(click_delay)
                pyautogui.moveTo(window.left + x, window.top + y)
                pyautogui.click()
        
            print(f"Successfully clicked at ({x}, {y}) in window: {window.title}")
            return True
    
        except Exception as e:
            print(f"Error clicking on application: {e}", file=sys.stderr)
            return False
    
    def switch_app(self):
        """Zoom in using keyboard shortcuts"""
        modifier = 'ctrl' if platform.system() != 'Darwin' else 'command'
        pyautogui.hotkey(modifier, 'tab')
        time.sleep(0.2)
    
# Example usage