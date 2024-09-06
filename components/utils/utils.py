# components/utils.py

import subprocess

class Utils:
    def __init__(self, tool_path='esptool.py'):
        self.tool_path = tool_path

    def check_functionality(self):
        """
        Check if esptool is functioning correctly.
        
        Returns:
            bool: True if esptool is working, False otherwise.
        """
        try:
            # Attempt to run esptool with no arguments to check if it's available
            result = subprocess.run([self.tool_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Check if esptool provides help message (i.e., no unrecognized argument errors)
            if "usage:" in result.stdout or "usage:" in result.stderr:
                print("esptool is functioning correctly.")
                return True
            else:
                print("esptool encountered an error:", result.stderr.strip())
                return False
        
        except FileNotFoundError:
            print("esptool is not installed or not found in the system PATH.")
            return False
        except Exception as e:
            print(f"An error occurred while checking esptool: {e}")
            return False
        
    def read_order(self, file_path):
        """
        Read the order from the given file.
        """
        order_numbers = []
        with open(file_path, 'r') as file:
            for line in file:
                if 'order-no' in line:
                    order_number = line.split('order-no: ')[1].split(',')[0].strip()
                    if order_number not in order_numbers:
                        order_numbers.append(order_number)
        return order_numbers 
