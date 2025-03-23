import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from functions import validate_client_list
from variables import client_csv_file_path, un_sc_url, number_of_matches


# Function to load data when the CSV file is selected
def load_data_from_csv(file_path):
    try:
        matched_clients = validate_client_list(file_path, un_sc_url, number_of_matches)

        # Check if there is any data to display
        if not matched_clients:
            messagebox.showinfo("No Data", "No clients matched the criteria.")
            return

        # Clear existing data in the table
        for row in tree.get_children():
            tree.delete(row)

        # Insert new data into the table
        for client in matched_clients:
            tree.insert('', 'end', values=(
            client['CEDULA'], client['NOMBRE_CLIENTE'], client['NOMBRE_UN'], ", ".join(client['COINCIDENCIAS'])))

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


# Function to save data as CSV
def save_as_csv():
    try:
        matched_clients = [tree.item(row)['values'] for row in tree.get_children()]
        if not matched_clients:
            messagebox.showwarning("No Data", "There is no data to save.")
            return

        # Ask for file location
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        # Write to CSV
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['CEDULA', 'NOMBRE_CLIENTE', 'NOMBRE_UN', 'COINCIDENCIAS'])  # Header row
            for client in matched_clients:
                writer.writerow(client)

        messagebox.showinfo("Success", "Data saved successfully as CSV.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


# Function to load data using the file path directly (Load Data button)
def load_data():
    # Ask the user to select a CSV file
    file_path = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        load_data_from_csv(file_path)  # Directly load the file after selection
        messagebox.showinfo("File Selected", f"CSV file selected: {file_path}")
    else:
        messagebox.showwarning("No File", "No file selected.")


# Create the main window
root = tk.Tk()
root.title("Client Data Viewer")
root.geometry("800x400")  # Set the window size

# Create the table (Treeview)
columns = ('CEDULA', 'NOMBRE_CLIENTE', 'NOMBRE_UN', 'COINCIDENCIAS')  # Columns for the data
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.pack(fill='both', expand=True, padx=10, pady=10)

# Define column headings
for col in columns:
    tree.heading(col, text=col)

# Frame to hold buttons horizontally
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Create the "Load CSV" button (on the left)
load_csv_button = tk.Button(button_frame, text="Load CSV", command=load_data)
load_csv_button.pack(side='left', padx=5)

# Create the "Save as CSV" button (on the right)
save_csv_button = tk.Button(button_frame, text="Save as CSV", command=save_as_csv)
save_csv_button.pack(side='right', padx=5)

# Run the Tkinter event loop
root.mainloop()
