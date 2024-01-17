# by kennethrrosen@proton.me
# user needs to add their API and Pi-Hole IP

import subprocess
import requests
import json
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class PiHoleTrayApp(Gtk.Application):
    def __init__(self):
        super().__init__()
        self.tray_icon = Gtk.StatusIcon()
        self.create_menu()
        self.update_icon()

    def create_menu(self):
        # Create a right-click menu
        self.menu = Gtk.Menu()

        # Add 'Enable' menu item
        self.enable_item = Gtk.MenuItem(label="Enable Pi-hole")
        self.enable_item.connect("activate", self.enable_pihole)
        self.menu.append(self.enable_item)

        # Add 'Disable' menu item
        self.disable_item = Gtk.MenuItem(label="Disable Pi-hole")
        self.disable_item.connect("activate", self.disable_pihole)
        self.menu.append(self.disable_item)

        # Add 'Blocked DNS Requests' menu item
        self.blocked_requests_item = Gtk.MenuItem(label="Blocked Requests: Loading...")
        self.menu.append(self.blocked_requests_item)

        self.menu.show_all()

        # Connect the menu to the tray icon
        self.tray_icon.connect("popup-menu", self.on_right_click)

    def on_right_click(self, icon, button, time):
        self.update_blocked_requests()  # Update the blocked requests count
        self.menu.popup(None, None, None, icon, button, time)

    def update_blocked_requests(self):
        # Fetch the number of blocked requests
        try:
            response = requests.get("http://[YOUR-PI-HOLE-IP OR LOCALHOST HERE]/admin/api.php?summary")
            if response.status_code == 200:
                data = response.json()
                blocked = data.get('ads_blocked_today', 'N/A')
                self.blocked_requests_item.set_label(f"Blocked Requests: {blocked}")
        except requests.exceptions.RequestException:
            self.blocked_requests_item.set_label("Blocked Requests: Error")
  
    def enable_pihole(self, widget):
        try:
            response = requests.get(
                "http://[YOUR-PI-HOLE-IP OR LOCALHOST HERE]/admin/api.php?enable&auth=[YOURAPIHERE]"
            )
            if response.status_code == 200:
                print("Pi-hole enabled")
            else:
                print("Failed to enable Pi-hole")
        except requests.exceptions.RequestException as e:
            print("Error enabling Pi-hole:", e)

    def disable_pihole(self, widget):
        try:
            response = requests.get(
                "http://[YOUR-PI-HOLE-IP OR LOCALHOST HERE]/admin/api.php?disable&auth=[YOURAPIHERE]"
            )
            if response.status_code == 200:
                print("Pi-hole disabled")
            else:
                print("Failed to disable Pi-hole")
        except requests.exceptions.RequestException as e:
            print("Error disabling Pi-hole:", e)

    def check_pihole_service(self):
        try:
            response = subprocess.run(
                ["systemctl", "is-active", "pihole-FTL"],
                text=True,
                capture_output=True,
                check=True,
            )
            return response.stdout.strip() == "active"
        except subprocess.CalledProcessError:
            return False

    def update_icon(self):
        if not self.check_pihole_service():
            print("Pi-hole service is not running.")
            return


        # Check Pi-hole status
        pihole_enabled = self.check_pihole_status('https://[YOUR-PI-HOLE-IP OR LOCALHOST HERE]')

        # Update icon based on status
        if pihole_enabled:
            icon_name = "/home/user/pihole.svg"  # Replace with path to enabled icon
        else:
            icon_name = (
                "/home/user/pihole-color.svg"  # Replace with path to disabled icon
            )

        self.tray_icon.set_from_file(icon_name)
        GLib.timeout_add_seconds(60, self.update_icon)  # Update every 60 seconds

    def check_pihole_status(self, ip_address):
        try:
            response = subprocess.run(['ping', '-c', '1', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return response.returncode == 0
        except Exception as e:
            print(f"Error pinging Pi-Hole server: {e}")
            return False

#    def check_pihole_status(self):
#        try:
#            # Replace with your Pi-hole status API endpoint
#            response = requests.get("http://[YOUR-PI-HOLE-IP OR LOCALHOST HERE]/admin/api.php?status")
#            if response.status_code == 200:
#                data = response.json()
#                print("Data received:", data)
#                if isinstance(data, list):
#                    return data[0].get('status','') == 'enabled'
#                elif isinstance(data, dict):
#                     return data.get('status','') == 'enabled'
#                else:
#                     print("Unexpected Data Format")
#                     return False
#            else:
#                print("Error: HTTP status code", response.status_code)
#                return False
#        except requests.exceptions.RequestException as e:
#            print("Error fetching Pi-Hole status:", e)
#            return False

app = PiHoleTrayApp()
Gtk.main()
