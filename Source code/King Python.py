import customtkinter as ctk
import types
import inspect
import threading
import time

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.allowed_builtins = {
            "abs": abs, "min": min, "max": max, "len": len,
            "sum": sum, "range": range, "round": round,
            "print": print, "type": type, "isinstance": isinstance,
            "int": int, "str": str, "float": float, "bool": bool,
            "list": list, "dict": dict, "set": set,
        }
        self.allowed_modules = {
            "math": __import__("math"),
            "random": __import__("random"),
            "os": __import__("os"),
            "sys": __import__("sys"),
        }

    def evaluate(self, expression):
        try:
            # Safely evaluate expressions with built-ins and variables
            result = eval(expression, {"__builtins__": None, **self.allowed_builtins, **self.variables}, self.variables)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    def process_line(self, line):
        # Ignore comments
        if line.startswith("#"):
            return None

        # Handle print statements
        if line.startswith("print(") and line.endswith(")"):
            expression = line[6:-1].strip()  # Extract the content inside print()
            value = self.evaluate(expression)
            return value if not isinstance(value, str) else value  # Don't add "Output:" label

        # Handle imports
        if line.startswith("import "):
            module_name = line.split("import", 1)[1].strip()
            if module_name in self.allowed_modules:
                self.variables[module_name] = self.allowed_modules[module_name]
                return f"Module '{module_name}' imported successfully"
            else:
                return f"Error: Module '{module_name}' not allowed"

        # Handle variable assignments with type checks
        if "=" in line:
            var_name, expression = map(str.strip, line.split("=", 1))
            if var_name.isidentifier():
                value = self.evaluate(expression)
                if not isinstance(value, str):  # Ensure it's not an error message
                    self.variables[var_name] = value
                    return f"{var_name} = {value}"
                else:
                    return value
            else:
                return "Error: Invalid variable name"

        # Otherwise, evaluate the expression directly
        return self.evaluate(line)

    def process_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
                results = []
                for line in lines:
                    line = line.strip()
                    if line:  # Ignore empty lines
                        result = self.process_line(line)
                        if result is not None:
                            results.append(f">>> {line}\n{result}")
                return "\n".join(results)
        except FileNotFoundError:
            return "Error: File not found"
        except Exception as e:
            return f"Error: {str(e)}"

    def execute_code_in_thread(self, code_str):
        """Runs the code asynchronously in a separate thread."""
        def target():
            try:
                result = self.evaluate(code_str)
                print(result)
            except Exception as e:
                print(f"Error: {str(e)}")
        
        thread = threading.Thread(target=target)
        thread.start()

class InterpreterApp:
    def __init__(self, root):
        self.root = root
        self.interpreter = Interpreter()

        # Configure the main window
        self.root.title("King Python (Interpreter)")
        self.root.geometry("600x500")
        ctk.set_appearance_mode("System")  # Options: "System", "Light", "Dark"
        ctk.set_default_color_theme("blue")

        # Create widgets
        self.output_box = ctk.CTkTextbox(self.root, height=300, width=560, wrap="word")
        self.output_box.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.output_box.insert("1.0", "Press Esc to exit\n\n")
        self.output_box.configure(state="disabled")

        self.input_box = ctk.CTkEntry(self.root, width=560, placeholder_text="Enter an expression or assignment...")
        self.input_box.grid(row=1, column=0, padx=20, pady=(0, 20))
        self.input_box.bind("<Return>", self.process_input)

        self.run_button = ctk.CTkButton(self.root, text="Run", command=self.process_input)
        self.run_button.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.load_button = ctk.CTkButton(self.root, text="Load .kp File", command=self.load_file)
        self.load_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Bind the Esc key to exit the application
        self.root.bind("<Escape>", self.exit)

    def append_output(self, text):
        self.output_box.configure(state="normal")
        self.output_box.insert("end", "\n" + text + "\n")  # Add newlines before and after output
        self.output_box.configure(state="disabled")
        self.output_box.see("end")

    def process_input(self, event=None):
        user_input = self.input_box.get().strip()
        if user_input.lower() == "exit":
            self.append_output("Goodbye!")
            self.root.after(1000, self.root.destroy)
            return

        if user_input:
            self.append_output(f">>> {user_input}")
            # Execute input asynchronously in a separate thread
            self.interpreter.execute_code_in_thread(user_input)

        self.input_box.delete(0, "end")

    def load_file(self):
        import tkinter.filedialog as fd

        file_path = fd.askopenfilename(filetypes=[("King Python Files", "*.kp"), ("All Files", "*.*")])
        if file_path:
            self.append_output(f"Loading file: {file_path}\n")
            output = self.interpreter.process_file(file_path)
            self.append_output(output)

    def exit(self, event=None):
        self.append_output("Goodbye!")
        self.root.after(1000, self.root.destroy)

if __name__ == "__main__":
    app = ctk.CTk()
    InterpreterApp(app)
    app.mainloop()
