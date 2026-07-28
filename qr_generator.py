#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RATCAT - QR Generator Module
Developed by: zaax
"""

import qrcode
from PIL import Image
import os
import sys
from datetime import datetime

class QRGenerator:
    """QR Code generator for RATCAT"""
    
    def __init__(self, output_dir="web"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, data, filename=None):
        """Generate QR code and save as image"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ratcat_qr_{timestamp}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate QR
        qr = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="#00ff00", back_color="#000000")
        img.save(filepath)
        
        return filepath
    
    def display_terminal(self, data):
        """Display QR in terminal using ASCII"""
        qr = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=2,
            border=2
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Print QR in terminal
        qr_matrix = qr.get_matrix()
        for row in qr_matrix:
            line = ''
            for col in row:
                if col:
                    line += '██'
                else:
                    line += '  '
            print('\033[92m' + line + '\033[0m')
    
    def decode(self, image_path):
        """Decode QR code from image"""
        try:
            from pyzbar.pyzbar import decode
            img = Image.open(image_path)
            decoded = decode(img)
            if decoded:
                return decoded[0].data.decode()
            return None
        except:
            return None
