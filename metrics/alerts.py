import os

def display_alert(title, message):
    script = f'display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK" with icon caution'
    os.system(f'osascript -e \'{script}\'')