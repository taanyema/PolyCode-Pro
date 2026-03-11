from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import io
import subprocess
import os
import json
import re
import numpy as np

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

def traduire_scilab_vers_python(scilab_code):
    """ 
    Traduit la syntaxe Scilab/Octave de la feuille en Python.
    Gère les boucles, les conditions, les intervalles et les deux-points.
    """
    lines = scilab_code.split('\n')
    py_code = []
    indent = 0
    
    for line in lines:
        line = line.strip()
        if not line: continue

        # 1. Nettoyage des commentaires et points-virgules de fin
        line = re.sub(r'//.*', '', line)
        line = line.rstrip(';')

        # 2. Traduction du FOR Scilab (ex: for i = 1:5)
        # On transforme "for var = deb:fin" en "for var in range(deb, fin+1):"
        if line.startswith('for'):
            match_for = re.search(r'for\s+(\w+)\s*=\s*(-?\d+\.?\d*):(-?\d+\.?\d*)', line)
            if match_for:
                var, debut, fin = match_for.groups()
                line = f"for {var} in range({int(float(debut))}, {int(float(fin)) + 1}):"
            else:
                # Gestion générique si format différent
                line = line.replace('for', 'for ').replace('=', ' in ')

        # 3. Traduction des conditions et boucles (mots-clés)
        line = re.sub(r'\bthen\b', ':', line)
        line = re.sub(r'\bdo\b', ':', line)
        line = line.replace('else if', 'elif')
        if line == 'else': 
            line = 'else:'

        # 4. Ajout automatique des ":" pour Python si manquants
        if any(line.startswith(x) for x in ['if', 'while', 'for', 'elif']) and not line.endswith(':'):
            line += ':'

        # 5. Traduction des vecteurs/intervalles (ex: X = 0:0.1:10)
        # Format complet [debut:pas:fin]
        line = re.sub(r'(\w+)\s*=\s*(-?\d+\.?\d*):(-?\d+\.?\d*):(-?\d+\.?\d*)', 
                      r'\1 = np.arange(\2, \4 + \3, \3)', line)
        # Format simple [debut:fin]
        line = re.sub(r'(\w+)\s*=\s*(-?\d+\.?\d*):(-?\d+\.?\d*)', 
                      r'\1 = np.arange(\2, \3 + 1)', line)

        # 6. Gestion de l'indentation via 'end'
        if line == 'end':
            indent = max(0, indent - 1)
            continue
            
        # Construction de la ligne avec l'indentation Python
        py_line = ("    " * indent) + line
        py_code.append(py_line)
        
        # Si la ligne finit par ':', la suivante augmente l'indentation
        if line.endswith(':'):
            indent += 1
            
    return "\n".join(py_code)

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
                chart_data = {
                    "labels": list(labels), 
                    "values": [float(v) for v in values], 
                    "type": type
                }
            import matplotlib.pyplot as plt
            plt.plot = tracer 
            exec_globals = {'tracer': tracer, 'plt': plt, 'np': np}
            exec(code, exec_globals)
            result = output_capture.getvalue()
        except Exception as e:
            result = f"ERREUR PYTHON : {str(e)}"
        finally:
            sys.stdout = sys.__stdout__
        
        return jsonify({"output": result if result else "Exécuté avec succès.", "chart_data": chart_data})

    # --- 2. MOTEUR C / C++ ---
    elif lang_choice in ["c", "cpp"]:
        extension = "c" if lang_choice == "c" else "cpp"
        compiler = "gcc" if lang_choice == "c" else "g++"
        filename = f"temp_code.{extension}"
        output_exec = "temp_prog"
        try:
            with open(filename, "w") as f:
                f.write(code)
            compile_proc = subprocess.run([compiler, filename, "-o", output_exec, "-lm"], capture_output=True, text=True)
            if compile_proc.returncode != 0:
                return jsonify({"output": f"ERREUR COMPILATION :\n{compile_proc.stderr}"})
            
            run_proc = subprocess.run([f"./{output_exec}"], capture_output=True, text=True)
            output = run_proc.stdout + run_proc.stderr

            if "PLOT:" in output:
                match = re.search(r"PLOT:(.*?)\|(.*?)\n", output)
                if match:
                    chart_data = {
                        "labels": match.group(1).split(","),
                        "values": [float(v) for v in match.group(2).split(",")],
                        "type": "line"
                    }
                    output = output.replace(match.group(0), "")

            return jsonify({"output": output if output.strip() else "Exécuté avec succès.", "chart_data": chart_data})
        except Exception as e:
            return jsonify({"output": f"ERREUR SYSTÈME : {str(e)}"})
        finally:
            if os.path.exists(filename): os.remove(filename)
            if os.path.exists(output_exec): os.remove(output_exec)

    # --- 3. MOTEUR SCILAB / OCTAVE (TRADUCTEUR) ---
    elif lang_choice in ["scilab", "octave"]:
        output_capture = io.StringIO()
        sys.stdout = output_capture
        try:
            def plot_mock(x, y):
                nonlocal chart_data
                chart_data = {
                    "labels": list(x) if isinstance(x, (list, np.ndarray)) else [x],
                    "values": [float(v) for v in y] if isinstance(y, (list, np.ndarray)) else [float(y)],
                    "type": "line"
                }

            exec_globals = {
                'np': np, 'plot': plot_mock, 'disp': print,
                'printf': lambda fmt, *args: print(fmt % args if args else fmt),
                'sin': np.sin, 'cos': np.cos, 'sqrt': np.sqrt, 'pi': np.pi, 'exp': np.exp
            }

            code_pythonise = traduire_scilab_vers_python(code)
            exec(code_pythonise, exec_globals)
            result = output_capture.getvalue()
            
            return jsonify({
                "output": result if result else "Calcul terminé avec succès.",
                "chart_data": chart_data
            })
        except Exception as e:
            return jsonify({"output": f"ERREUR SYNTAXE : {str(e)}"})
        finally:
            sys.stdout = sys.__stdout__

    return jsonify({"output": "Langage non supporté."})

@app.route('/aide_ia', methods=['POST'])
def aide_ia():
    data = request.get_json()
    error = data.get('error', '').lower()
    if "syntax" in error:
        conseil = "💡 Vérifie tes boucles (for/end) ou l'oubli de parenthèses."
    elif "indentation" in error:
        conseil = "📐 Alignement incorrect ! Vérifie tes blocs de code."
    else:
        conseil = "🚀 Ta logique semble correcte, vérifie tes variables."
    return jsonify({"conseil": conseil})

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('.', 'sw.js')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)