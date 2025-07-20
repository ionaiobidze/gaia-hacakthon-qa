#!/usr/bin/env python3
"""
Server Launcher for React Applications
Manages starting and stopping both React v1 and v2 apps
"""

import subprocess
import time
import os
import sys
import signal
import requests
from typing import Dict

class ReactServerManager:
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.ports = {"react_v1": 3000, "react_v2": 3001}

    def start_server(self, app_name: str, port: int) -> bool:
        """Start a React development server"""
        try:
            print(f"🚀 Starting {app_name} on port {port}...")

            if self._is_port_in_use(port):
                print(f"⚠️  Port {port} is already in use. Assuming server is running.")
                return True

            app_dir = os.path.abspath(app_name)
            if not os.path.exists(os.path.join(app_dir, 'package.json')):
                print(f"❌ 'package.json' not found in {app_dir}. Is this a valid React project?")
                return False

            env = os.environ.copy()
            env['PORT'] = str(port)
            env['BROWSER'] = 'none'

            # Windows compatibility - use proper command format
            if os.name == 'nt':
                # Windows - use cmd /c to run npm
                cmd = ['cmd', '/c', 'npm', 'start']
                shell = False
                preexec_fn = None
            else:
                # Linux/Mac
                cmd = ['npm', 'start']
                shell = False
                preexec_fn = os.setsid

            print(f"📝 Running command: {' '.join(cmd)} in {app_dir}")

            process = subprocess.Popen(
                cmd,
                cwd=app_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=shell,
                preexec_fn=preexec_fn
            )

            self.processes[app_name] = process

            # Give the server more time to start and show progress
            if self._wait_for_server(port, timeout=240):  # 4 minutes
                print(f"✅ {app_name} is running on http://localhost:{port}")
                return True
            else:
                print(f"❌ Failed to start {app_name} on port {port}")
                # Show process output for debugging
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    if stderr:
                        print(f"🔍 Error output: {stderr.decode()[:500]}...")
                    if stdout:
                        print(f"🔍 Standard output: {stdout.decode()[:500]}...")
                return False

        except Exception as e:
            print(f"❌ Error starting {app_name}: {e}")
            return False

    def stop_server(self, app_name: str) -> bool:
        """Stop a React development server"""
        if app_name not in self.processes:
            return True

        try:
            process = self.processes[app_name]
            print(f"🛑 Stopping {app_name}...")

            if os.name == 'nt':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)

            process.wait(timeout=10)
            del self.processes[app_name]
            print(f"✅ {app_name} stopped")
            return True

        except subprocess.TimeoutExpired:
            print(f"⚠️  Force killing {app_name}...")
            if os.name != 'nt':
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            del self.processes[app_name]
            return True

        except Exception as e:
            print(f"❌ Error stopping {app_name}: {str(e)}")
            return False

    def start_all_servers(self) -> bool:
        """Start both React servers"""
        success = True
        for app_name, port in self.ports.items():
            if not self.start_server(app_name, port):
                success = False
        return success

    def stop_all_servers(self) -> bool:
        """Stop all React servers"""
        success = True
        for app_name in list(self.processes.keys()):
            if not self.stop_server(app_name):
                success = False
        return success

    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use by trying to connect"""
        try:
            requests.get(f"http://localhost:{port}", timeout=2)
            return True
        except requests.exceptions.RequestException:
            return False

    def _wait_for_server(self, port: int, timeout: int = 180) -> bool:
        """Wait for server to be ready by polling it."""
        print(f"⏳ Waiting for React dev server on port {port} to compile and be ready...")
        start_time = time.time()
        attempt = 0
        while time.time() - start_time < timeout:
            attempt += 1
            if self._is_port_in_use(port):
                print(f"✅ Server on port {port} is ready after {attempt} attempts!")
                return True
            
            # Show progress every 30 seconds
            elapsed = time.time() - start_time
            if attempt % 10 == 0:  # Every 30 seconds (10 attempts * 3 seconds)
                print(f"   Still waiting... {elapsed:.0f}s elapsed, {timeout - elapsed:.0f}s remaining")
            
            time.sleep(3)
        
        print(f"❌ Timed out waiting for server on port {port} after {timeout} seconds.")
        print(f"💡 Try manually starting: cd ui/react_v{'1' if port == 3000 else '2'} && npm start")
        return False
