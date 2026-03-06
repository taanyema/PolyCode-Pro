from flask import Flask, render_template, request, jsonify
import sys
import io
import subprocess
import os
import json
import re

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    code = data.get('code', '')
    lang_choice = str(data.get('lang', 'python')).lower()
    
    chart_data = None 
    result = ""

    # --- 1. MOTEUR PYTHON ---
    if lang_choice == "python":
        output_capture = io.StringIO()
        sys.stdout = output_capture
        try:
            def tracer(labels, values, type='line'):
                nonlocal chart_data
                chart_data = {"labels": labels, "values": values, "type": type}

            exec_globals = {'tracer': tracer}
            exec(code, exec_globals)
            result = output_capture.getvalue()
        except Exception as e:
            result = f"ERREUR PYTHON : {str(e)}"
        finally:
            sys.stdout = sys.__stdout__
        
        return jsonify({
            "output": result if result else "Exécuté avec succès.",
            "chart_data": chart_data
        })

    # --- 2. MOTEUR C / C++ ---
    elif lang_choice in ["c", "cpp"]:
        extension = "c" if lang_choice == "c" else "cpp"
        compiler = "gcc" if lang_choice == "c" else "g++"
        filename = f"temp_code.{extension}"
        output_exec = "temp_prog"
        try:
            with open(filename, "w") as f:
                f.write(code)
            compile_proc = subprocess.run([compiler, filename, "-o", output_exec], capture_output=True, text=True)
            if compile_proc.returncode != 0:
                return jsonify({"output": f"ERREUR COMPILATION :\n{compile_proc.stderr}"})
            run_proc = subprocess.run([f"./{output_exec}"], capture_output=True, text=True)
            return jsonify({"output": run_proc.stdout + run_proc.stderr})
        except Exception as e:
            return jsonify({"output": f"ERREUR SYSTÈME : {str(e)}"})
        finally:
            if os.path.exists(filename): os.remove(filename)
            if os.path.exists(output_exec): os.remove(output_exec)

    # --- 3. MOTEUR OCTAVE / SCILAB ---
    elif lang_choice == "scilab":
        pre_code = """
        function tracer(x, y)
          printf("CHART_DATA:labels=%s;values=%s\\n", char(jsonencode(x)), char(jsonencode(y)));
        endfunction
        """
        full_code = pre_code + code
        
        try:
            process = subprocess.run(
                ["octave", "--no-gui", "--quiet", "--eval", full_code],
                capture_output=True, text=True, timeout=15,
                env={**os.environ, "PAGER": "cat"}
            )
            output = process.stdout + process.stderr
            
            # Nettoyage des logs parasites (Drivers, QStandardPaths, Warnings)
            output = re.sub(r"QStandardPaths:.*?\n", "", output)
            output = re.sub(r"warning:.*?\n", "", output)
            
            # Extraction des données CHART_DATA
            if "CHART_DATA:" in output:
                match = re.search(r"CHART_DATA:labels=(.*?);values=(.*?)\n", output)
                if match:
                    labels_raw = match.group(1)
                    values_raw = match.group(2)
                    chart_data = {
                        "labels": [round(float(x), 2) for x in json.loads(labels_raw)],
                        "values": [round(float(v), 2) for v in json.loads(values_raw)]
                    }
                    # On retire la ligne technique de l'affichage console
                    output = output.replace(match.group(0), "") 
            
            return jsonify({
                "output": output if output.strip() else "Exécuté avec succès (Octave).",
                "chart_data": chart_data
            })
        except Exception as e:
            return jsonify({"output": f"Erreur Octave : {str(e)}"})

    # Réponse par défaut
    return jsonify({"output": "Langage non supporté."})

@app.route('/aide_ia', methods=['POST'])
def aide_ia():
    data = request.get_json()
    error = data.get('error', '').lower()
    conseil = "💡 Erreur de structure détectée." if "syntax" in error else "🚀 Logique correcte, vérifiez vos variables."
    return jsonify({"conseil": conseil})

if __name__ == '__main__':
    # Configuration pour accès réseau local (Termux/Replit)
    app.run(host='0.0.0.0', port=5000)