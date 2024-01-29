import tkinter as tk
import webbrowser
from tkinter import Label, Button, messagebox, Text, StringVar, OptionMenu, Spinbox
import requests
import socket
from PIL import Image, ImageTk
from tkinter import filedialog
import psutil


class ZPLPrintApp:
    def __init__(self, master):
        self.master = master
        master.title("ZPL Print Application")
        master.geometry("900x500")
        master.resizable(False, False)

        Label(master, text="Printer IP:").place(x=10, y=10)

        default_ip = "123.123.123.123"
        other_ips = ["123.123.123.123", "123.123.123.123", "123.123.123.123"]

        self.printer_ip_var = StringVar(master)
        self.printer_ip_var.set(default_ip)

        printer_ip_menu = OptionMenu(master, self.printer_ip_var, default_ip, *other_ips)
        printer_ip_menu.place(x=150, y=10, width=150)

        Label(master, text="Printer Port:").place(x=10, y=50)

        default_port = "9999"
        other_ports = ["9999", "9999", "9999", "9999"]

        self.printer_port_var = StringVar(master)
        self.printer_port_var.set(default_port)

        printer_port_menu = OptionMenu(master, self.printer_port_var, default_port, *other_ports)
        printer_port_menu.place(x=150, y=50, width=150)

        Label(master, text="Quantity:").place(x=10, y=90)

        self.aantal_var = tk.IntVar(master)
        self.aantal_var.set(1)

        aantal_spinbox = Spinbox(master, from_=1, to=10, textvariable=self.aantal_var)
        aantal_spinbox.place(x=150, y=90, width=50)

        Label(master, text="ZPL Data to Send:").place(x=10, y=130)
        self.zpl_data_entry = Text(master)
        self.zpl_data_entry.place(x=150, y=130, height=200, width=400)

        print_button = Button(master, text="Send to intern Printer", command=self.send_print_job)
        print_button.place(x=10, y=350)

        # New button to send ZPL data to an external or cloud service
        cloud_button = Button(master, text="Send to Cloud", command=self.send_to_cloud)
        cloud_button.place(x=150, y=350)

        url_button = Button(master, text="Online viewer ZPL", command=self.open_url)
        url_button.place(x=250, y=350)

        # Display computer name and IP address
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)

        # Display computer name
        computer_name_label = Label(master, text=f"Computer Name: {hostname}")
        computer_name_label.place(x=350, y=15)

        # Display computer IP address
        computer_ip_label = Label(master, text=f"Computer IP Address: {IPAddr}")
        computer_ip_label.place(x=350, y=35)

        # Display running browsers
        browsers_label = Label(master, text="Running Browsers:")
        browsers_label.place(x=350, y=60)

        self.browsers_text = Text(master, height=2, width=25)
        self.browsers_text.place(x=350, y=60)

        # image converter
        Label(self.master, text="Je kunt hier een afbeelding converteren naar ZPL-code.").place(x=570, y=125)

        upload_button = tk.Button(self.master, text="Upload Image", command=self.upload_image)
        upload_button.place(x=570, y=160)

        self.image_label = Label(self.master)
        self.image_label.place(x=600, y=200)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;")],
            defaultextension=".png"
        )

        if file_path:
            self.display_image(file_path)
            zpl_code = self.convert_image_to_zpl(file_path)
            self.zpl_data_entry.delete(1.0, tk.END)
            self.zpl_data_entry.insert(tk.END, zpl_code)

    def convert_image_to_zpl(self, image_path, output_format='zpl'):
        api_url = 'http://api.labelary.com/v1/graphics'
        accept_header = f'application/{output_format}'

        with open(image_path, 'rb') as image_file:
            files = {'file': image_file}
            headers = {'Accept': accept_header}

            response = requests.post(api_url, files=files, headers=headers)

            if response.status_code == 200:
                return response.content.decode('utf-8')
            else:
                print(f'Error: {response.status_code}, {response.text}')

    def display_image(self, image_path):
        image = Image.open(image_path)
        width, height = image.size
        new_width = 200
        new_height = int((new_width / width) * height)
        image.thumbnail((new_width, new_height))
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

    def open_url(self):
        webbrowser.open("https://labelary.com/viewer.html")

    def update_running_browsers(self):
        running_browsers = self.check_browsers()

        if running_browsers:
            browsers_info = "\n".join(running_browsers)
            self.browsers_text.delete(1.0, tk.END)
            self.browsers_text.insert(tk.END, browsers_info)
        else:
            self.browsers_text.delete(1.0, tk.END)
            self.browsers_text.insert(tk.END, "No Browsers Running")

    def check_browsers(self):
        browser_names = ["firefox", "chrome", "brave", "safari", "opera", "duckduckgo"]
        browsers_found = set()

        for proc in psutil.process_iter(['pid', 'name']):
            process_name = proc.info['name'].lower()

            for browser in browser_names:
                if browser in process_name:
                    browsers_found.add(process_name)

        return browsers_found

    def send_zpl_data(self, ip, port, zpl_data):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, port))
            s.sendall(zpl_data.encode('utf-8'))
            print("ZPL data sent successfully")
        except ConnectionRefusedError:
            print("Connection refused. Check the printer's IP and port.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            s.close()

    def send_to_cloud(self):
        printer_ip = self.printer_ip_var.get()
        printer_port = int(self.printer_port_var.get())
        aantal = int(self.aantal_var.get())
        zpl_data_to_send = self.zpl_data_entry.get("1.0", "end")  # Remove tk.END

        if not printer_ip or not printer_port or not aantal or not zpl_data_to_send:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        for _ in range(aantal):
            # Use the new function to send data to the cloud
            self.send_zpl_data_to_cloud(printer_ip, printer_port, zpl_data_to_send)

        messagebox.showinfo("Print Job Information", "Print job sent successfully to the cloud")

    def send_zpl_data_to_cloud(self, ip, port, zpl_data):
        url = "https://xxxx.xxxxxxx.com:99/xxxxx/print.php"

        data = {
            'addr': ip,
            'port': port,
            'data': zpl_data
        }

        try:
            response = requests.post(url, data=data)

            if response.status_code == 200:
                print("ZPL data sent successfully to the cloud")
            else:
                print(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error: {e}")

    def send_print_job(self):
        printer_ip = self.printer_ip_var.get()
        printer_port = int(self.printer_port_var.get())
        aantal = int(self.aantal_var.get())
        zpl_data_to_send = self.zpl_data_entry.get("1.0", "end")  # Remove tk.END

        if not printer_ip or not printer_port or not aantal or not zpl_data_to_send:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        for _ in range(aantal):
            self.send_zpl_data(printer_ip, printer_port, zpl_data_to_send)

        messagebox.showinfo("Print Job Information", "Print job sent successfully")

    def open_url(self):
        webbrowser.open("https://labelary.com/viewer.html")


if __name__ == "__main__":
    app = tk.Tk()
    zpl_app = ZPLPrintApp(app)
    update_browsers_button = Button(app, text="Update Running Browsers", command=zpl_app.update_running_browsers)
    update_browsers_button.place(x=570, y=70)
    app.mainloop()

print("copyright Yasin Horani (～￣▽￣)～  -.-- .- ... .. -. / .... --- .-. .- -. ..")