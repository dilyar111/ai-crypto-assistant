#!/usr/bin/env python3
"""
Troubleshooting script for AI Crypto Assistant
Run this to diagnose and fix common issues
"""

import requests
import subprocess
import sys
import time
import json
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print('='*60)

def print_status(message, status):
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    print(f"{icons.get(status, '•')} {message}")

def check_python_version():
    print_header("Python Version Check")
    version = sys.version_info
    print_status(f"Python {version.major}.{version.minor}.{version.micro}", "info")
    
    if version >= (3, 8):
        print_status("Python version is compatible", "success")
        return True
    else:
        print_status("Python 3.8+ required", "error")
        return False

def check_ollama_installation():
    print_header("Ollama Installation Check")
    
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_status(f"Ollama installed: {result.stdout.strip()}", "success")
            return True
        else:
            print_status("Ollama not found in PATH", "error")
            return False
    except subprocess.TimeoutExpired:
        print_status("Ollama command timed out", "error")
        return False
    except FileNotFoundError:
        print_status("Ollama not installed", "error")
        print("\n💡 Install Ollama:")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        return False

def check_ollama_service():
    print_header("Ollama Service Check")
    
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print_status("Ollama service is running", "success")
            
            # Check available models
            data = response.json()
            models = data.get("models", [])
            if models:
                print_status(f"Found {len(models)} model(s):", "success")
                for model in models:
                    print(f"   • {model['name']}")
            else:
                print_status("No models found", "warning")
                print("\n💡 Pull a model:")
                print("   ollama pull llama2")
            
            return True
            
    except requests.exceptions.ConnectionError:
        print_status("Ollama service not running", "error")
        print("\n💡 Start Ollama service:")
        print("   ollama serve")
        return False
    except requests.exceptions.Timeout:
        print_status("Ollama service timeout", "error")
        return False
    except Exception as e:
        print_status(f"Ollama service error: {e}", "error")
        return False

def check_api_endpoints():
    print_header("External API Check")
    
    apis = [
        ("Binance", "https://api.binance.com/api/v3/ping"),
        ("CoinGecko", "https://api.coingecko.com/api/v3/ping"),
        ("CryptoPanic", "https://cryptopanic.com/api/v1/posts/?public=true")
    ]
    
    results = {}
    for name, url in apis:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print_status(f"{name} API: Working", "success")
                results[name] = True
            else:
                print_status(f"{name} API: Status {response.status_code}", "warning")
                results[name] = False
        except Exception as e:
            print_status(f"{name} API: Error - {e}", "error")
            results[name] = False
    
    return results

def check_dependencies():
    print_header("Python Dependencies Check")
    
    required_packages = [
        "streamlit",
        "requests", 
        "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_status(f"{package}: Installed", "success")
        except ImportError:
            print_status(f"{package}: Missing", "error")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n💡 Install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment_file():
    print_header("Environment Configuration Check")
    
    env_file = Path(".env")
    if env_file.exists():
        print_status(".env file found", "success")
        
        # Read and check for API keys
        with open(env_file, 'r') as f:
            content = f.read()
        
        if "CRYPTOPANIC_API_KEY" in content:
            print_status("CryptoPanic API key configured", "success")
        else:
            print_status("CryptoPanic API key not found", "warning")
            print("   Get free key at: https://cryptopanic.com/developers/api/")
        
        return True
    else:
        print_status(".env file not found", "warning")
        print("\n💡 Create .env file with:")
        print("   CRYPTOPANIC_API_KEY=your_api_key_here")
        return False

def test_ollama_generation():
    print_header("Ollama Generation Test")
    
    try:
        print("Testing simple generation...")
        
        url = "http://127.0.0.1:11434/api/generate"
        data = {
            "model": "llama2",
            "prompt": "Say 'Hello World' in one sentence.",
            "stream": False,
            "options": {"num_predict": 50}
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "")
            if generated_text:
                print_status("Generation test successful", "success")
                print(f"   Response: {generated_text.strip()}")
                return True
            else:
                print_status("Empty response from model", "error")
                return False
        else:
            print_status(f"Generation failed: Status {response.status_code}", "error")
            return False
            
    except requests.exceptions.Timeout:
        print_status("Generation timeout (>30s)", "error")
        print("💡 Try a smaller/faster model or restart Ollama")
        return False
    except Exception as e:
        print_status(f"Generation error: {e}", "error")
        return False

def suggest_fixes():
    print_header("Suggested Fixes")
    
    print("🚀 Quick Start Commands:")
    print("   1. Start Ollama:     ollama serve")
    print("   2. Pull model:       ollama pull llama2")
    print("   3. Test model:       ollama run llama2 'Hello'")
    print("   4. Install deps:     pip install -r requirements.txt")
    print("   5. Run app:          streamlit run app_debug.py")
    
    print("\n🔧 Common Issues:")
    print("   • Port 11434 busy:   Kill other Ollama processes")
    print("   • Slow generation:   Try smaller model (llama2:7b-chat)")
    print("   • API errors:        Check internet connection")
    print("   • Missing models:    ollama pull <model-name>")
    
    print("\n📚 Useful Commands:")
    print("   • List models:       ollama list")
    print("   • Remove model:      ollama rm <model>") 
    print("   • Check logs:        ollama logs")
    print("   • Test API:          curl http://localhost:11434/api/tags")

def main():
    print("🔍 AI Crypto Assistant - Troubleshooting Tool")
    print("This will check your setup and suggest fixes")
    
    all_checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_environment_file),
        ("Ollama Installation", check_ollama_installation),
        ("Ollama Service", check_ollama_service),
        ("External APIs", check_api_endpoints),
        ("Ollama Generation", test_ollama_generation)
    ]
    
    results = {}
    for name, check_func in all_checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_status(f"{name} check failed: {e}", "error")
            results[name] = False
    
    # Summary
    print_header("Summary")
    
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    print(f"✅ Passed: {success_count}/{total_count} checks")
    
    if success_count == total_count:
        print_status("All systems operational! 🎉", "success")
        print("\n🚀 You can run: streamlit run app.py")
    else:
        print_status("Issues found. See suggestions below:", "warning")
        suggest_fixes()
    
    # Failed checks
    failed_checks = [name for name, success in results.items() if not success]
    if failed_checks:
        print(f"\n❌ Failed checks: {', '.join(failed_checks)}")

if __name__ == "__main__":
    main()