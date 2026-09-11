import ollama
import webbrowser
import datetime
import os
import re
import threading
import queue
import argparse
import time

# Optional server + CORS
try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
except Exception:
    Flask = None

# Optional nicer process priority control
try:
    import psutil
except Exception:
    psutil = None

# Optional TTS (pyttsx3)
try:
    import pyttsx3
except Exception:
    pyttsx3 = None


# configuration defaults
MODEL_NAME = 'jarvis'
MAX_TOKENS = None
SERVER_SPEAK = True
FAST_MODE = False
LITE_MODE = False

# ==========================================
# 0. INITIALIZE JARVIS'S VOICE (background TTS)
# ==========================================
_tts_queue = queue.Queue()
_tts_thread = None
engine = None

def _tts_worker():
    global engine
    if pyttsx3 is None:
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        voices = engine.getProperty('voices')
        for v in voices:
            if 'david' in v.name.lower() or 'male' in v.name.lower():
                engine.setProperty('voice', v.id)
                break
    except Exception:
        engine = None

    while True:
        text = _tts_queue.get()
        if text is None:
            break
        try:
            # clean text to avoid voice engine crashes on odd chars
            clean_text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
            if engine and clean_text.strip():
                engine.say(clean_text)
                engine.runAndWait()
        except Exception as e:
            print(f"[VOICE ERROR] {e}")

def speak(text):
    """Queue speech and print to console."""
    print(f"\nJarvis: {text}")
    if pyttsx3 is None:
        return
    # push to background tts thread
    _tts_queue.put(text)


# start tts thread lazily
def ensure_tts_thread():
    global _tts_thread
    if _tts_thread is None and pyttsx3 is not None:
        _tts_thread = threading.Thread(target=_tts_worker, daemon=True)
        _tts_thread.start()


def try_lower_process_priority():
    """Attempt to set the current process to a lower priority to reduce system lag."""
    try:
        if psutil:
            p = psutil.Process(os.getpid())
            if os.name == 'nt':
                # set to IDLE if available, otherwise BELOW_NORMAL
                try:
                    p.nice(psutil.IDLE_PRIORITY_CLASS)
                except Exception:
                    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            else:
                # on Unix, increase nice value
                p.nice(10)
            print('[SYSTEM]: Process priority lowered to reduce lag')
        else:
            # fallback: try os.nice where available
            if hasattr(os, 'nice'):
                try:
                    os.nice(10)
                    print('[SYSTEM]: Increased nice value via os.nice')
                except Exception:
                    pass
    except Exception as e:
        print(f'[SYSTEM]: Could not change process priority: {e}')


def generate_quick_reply(text: str) -> str:
    """Very small rule-based reply generator for ultra-fast local responses."""
    t = text.lower().strip()
    if not t:
        return "I didn't hear anything — please type a message."
    greetings = ['hi', 'hello', 'hey', 'yo']
    for g in greetings:
        if t.startswith(g):
            return "Hello — how can I help you?"
    if 'time' in t or 'what time' in t:
        return get_current_time()
    if 'open ' in t and 'http' not in t and '.' in t:
        # quick heuristic to open website
        domain = t.split('open',1)[1].strip().split()[0]
        try:
            open_website(domain)
            return f"Opening {domain} in your browser."
        except Exception:
            return "I couldn't open that site."
    if t.endswith('?') and len(t.split()) <= 6:
        return "Good question — I'll look into that when you ask for a full response."
    # Default short echo
    short = text.strip()
    if len(short) > 140:
        short = short[:137] + '...'
    return f"You said: {short}"

# ==========================================
# 1. DEFINE JARVIS'S TOOLS (PYTHON FUNCTIONS)
# ==========================================

def open_website(url: str) -> str:
    """Opens a website in the default web browser."""
    if not url.startswith('http'):
        url = 'https://' + url
    print(f"\n[SYSTEM]: Opening {url}...")
    webbrowser.open(url)
    return f"Successfully opened {url}"

def get_current_time() -> str:
    """Gets the current local system time."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    print(f"\n[SYSTEM]: Time checked ({time_str})")
    return f"The current time is {time_str}"

def open_notepad() -> str:
    """Opens the Notepad application on Windows."""
    print("\n[SYSTEM]: Opening Notepad...")
    os.system("notepad.exe") 
    return "Notepad has been opened."

def create_file(filename: str, content: str) -> str:
    """Creates a new text file with the specified content on the Desktop. Can also create folders."""
    desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", filename)
    
    folder_path = os.path.dirname(desktop_path)
    if folder_path:
        os.makedirs(folder_path, exist_ok=True)
        
    try:
        with open(desktop_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n[SYSTEM]: Created '{filename}' on your Desktop.")
        return f"Successfully created {filename}."
    except Exception as e:
        return f"Failed to create file: {str(e)}"

available_tools = {
    'open_website': open_website,
    'get_current_time': get_current_time,
    'open_notepad': open_notepad,
    'create_file': create_file,
}

# ==========================================
# 2. TELL JARVIS WHAT TOOLS HE HAS
# ==========================================

jarvis_tools = [
    {
        'type': 'function',
        'function': {
            'name': 'open_website',
            'description': 'Open a specific website URL in the web browser',
            'parameters': {
                'type': 'object',
                'properties': {
                    'url': {'type': 'string', 'description': 'The full URL of the website to open, e.g., https://youtube.com'}
                },
                'required': ['url']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_current_time',
            'description': 'Get the current local system time to tell the user.',
            'parameters': {'type': 'object', 'properties': {}}
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'open_notepad',
            'description': 'Launch the Notepad app. ONLY use this if the user explicitly asks to OPEN notepad. Do NOT use this to create, save, or write files.',
            'parameters': {'type': 'object', 'properties': {}}
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'create_file',
            'description': 'Creates folders and text files in the background. Use this whenever the user asks to make, write, save, or create a file or folder. NEVER use open_notepad for this.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'filename': {'type': 'string', 'description': 'The name of the file to create, e.g., notes.txt or FolderName/script.py'},
                    'content': {'type': 'string', 'description': 'The actual text content to write inside the file'}
                },
                'required': ['filename', 'content']
            }
        }
    }
]

# ==========================================
# 3. THE MAIN CHAT LOOP
# ==========================================

def run_jarvis():
    ensure_tts_thread()
    # try to lower process priority to reduce system lag
    try_lower_process_priority()

    speak("J.A.R.V.I.S. System Online. Awaiting your command, Sir.")
    print("(Type 'exit' to quit)")
    
    messages = []

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            speak("Powering down. Goodbye, Sir.")
            break

        messages.append({'role': 'user', 'content': user_input})

        try:
            if LITE_MODE:
                # ultra-light local reply (very fast, no model)
                class LiteResp:
                    def __init__(self, text):
                        self.message = type('m', (), {'content': text, 'tool_calls': []})
                reply = generate_quick_reply(user_input)
                response = LiteResp(reply)
            else:
                chat_kwargs = {'model': MODEL_NAME, 'messages': messages, 'tools': jarvis_tools}
                if MAX_TOKENS is not None:
                    chat_kwargs['max_tokens'] = MAX_TOKENS
                response = ollama.chat(**chat_kwargs)
        except Exception as e:
            print(f"\n[SYSTEM ERROR]: {str(e)}")
            break

        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                function_name = tool.function.name
                arguments = tool.function.arguments
                
                if function_name in available_tools:
                    function_to_call = available_tools[function_name]
                    function_result = function_to_call(**arguments)
                    
                    messages.append({
                        'role': 'tool',
                        'content': function_result,
                        'name': function_name
                    })

            chat_kwargs = {'model': MODEL_NAME, 'messages': messages}
            if MAX_TOKENS is not None:
                chat_kwargs['max_tokens'] = MAX_TOKENS
            final_response = ollama.chat(**chat_kwargs)
            if SERVER_SPEAK:
                speak(final_response.message.content)
            messages.append({'role': 'assistant', 'content': final_response.message.content})
            
        else:
            if SERVER_SPEAK:
                speak(response.message.content)
            messages.append({'role': 'assistant', 'content': response.message.content})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--serve', action='store_true', help='Run a local web server and serve jarvis.html')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--model', help='Model name to use with ollama (use a smaller model to reduce CPU/GPU load)')
    parser.add_argument('--max-tokens', help='Optional max tokens to request from the model')
    parser.add_argument('--no-tts', action='store_true', help='Disable server-side TTS (use browser TTS instead)')
    parser.add_argument('--fast', action='store_true', help='Use fast minimal-mode (no tools, single-turn messages)')
    parser.add_argument('--lite', action='store_true', help='Use ultra-light local rule-based replies (no model, instant)')
    args = parser.parse_args()

    if args.serve and Flask is not None:
        # apply CLI-configured options
        MODEL_NAME = args.model or MODEL_NAME
        if args.max_tokens:
            try:
                MAX_TOKENS = int(args.max_tokens)
            except Exception:
                MAX_TOKENS = None
        SERVER_SPEAK = not args.no_tts
        FAST_MODE = args.fast
        LITE_MODE = args.lite

        # create a minimal Flask app that proxies messages to jarvis logic
        app = Flask(__name__, static_folder='.')
        CORS(app)

        # single-request guard: do not run multiple heavy inferences simultaneously
        inference_lock = threading.Lock()

        # single messages per session (stateless simple proxy)
        @app.route('/')
        def index():
            return send_from_directory('.', 'jarvis.html')

        @app.route('/api/chat', methods=['POST'])
        def api_chat():
            data = request.get_json() or {}
            user_message = data.get('message', '')
            if not user_message:
                return jsonify({'error': 'no message'}), 400

            # Run a simplified chat exchange: send user message and return assistant reply
            messages = [{'role': 'user', 'content': user_message}]
            try:
                # avoid concurrent heavy calls
                if not inference_lock.acquire(blocking=False):
                    return jsonify({'error': 'busy', 'message': 'Server is busy. Try again shortly.'}), 429
                if FAST_MODE:
                    chat_kwargs = {'model': MODEL_NAME, 'messages': [{'role':'user','content': user_message}]}
                    if MAX_TOKENS is not None:
                        chat_kwargs['max_tokens'] = MAX_TOKENS
                    response = ollama.chat(**chat_kwargs)
                else:
                    chat_kwargs = {'model': MODEL_NAME, 'messages': messages, 'tools': jarvis_tools}
                    if MAX_TOKENS is not None:
                        chat_kwargs['max_tokens'] = MAX_TOKENS
                    response = ollama.chat(**chat_kwargs)
            except Exception as e:
                try:
                    inference_lock.release()
                except Exception:
                    pass
                return jsonify({'error': str(e)}), 500

            # If model requests tools, run them (limited)
            if FAST_MODE:
                # single-turn fast reply
                assistant_text = response.message.content
                try:
                    inference_lock.release()
                except Exception:
                    pass
            else:
                if response.message.tool_calls:
                    for tool in response.message.tool_calls:
                        func_name = tool.function.name
                        args_ = tool.function.arguments
                        if func_name in available_tools:
                            try:
                                result = available_tools[func_name](**args_)
                                messages.append({'role': 'tool', 'content': result, 'name': func_name})
                            except Exception as e:
                                messages.append({'role': 'tool', 'content': f'Tool error: {e}', 'name': func_name})

                    try:
                        chat_kwargs = {'model': MODEL_NAME, 'messages': messages}
                        if MAX_TOKENS is not None:
                            chat_kwargs['max_tokens'] = MAX_TOKENS
                        final = ollama.chat(**chat_kwargs)
                        assistant_text = final.message.content
                    finally:
                        try:
                            inference_lock.release()
                        except Exception:
                            pass
                else:
                    assistant_text = response.message.content
                    try:
                        inference_lock.release()
                    except Exception:
                        pass

            # speak on server side only if enabled
            try:
                if SERVER_SPEAK:
                    ensure_tts_thread()
                    speak(assistant_text)
            except Exception:
                pass

            return jsonify({'reply': assistant_text})

        # lower priority before serving
        try_lower_process_priority()
        print(f"Serving jarvis UI at http://{args.host}:{args.port}/")
        # open browser (best-effort)
        try:
            webbrowser.open(f'http://{args.host}:{args.port}/')
        except Exception:
            pass

        app.run(host=args.host, port=args.port, debug=False, use_reloader=False)
    else:
        run_jarvis()