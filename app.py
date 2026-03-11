from flask import Flask, render_template, request, jsonify, send_from_directory
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
                chart_data = {
                    "labels": list(labels), 
                    "values": [float(v) for v in values], 
                    "type": type
                }
            import matplotlib.pyplot as plt
            plt.plot = tracer 
            exec_globals = {'tracer': tracer, 'plt': plt, 'np': __import__('numpy', fromlist=[''])}
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
            output = run_proc.stdout + run_proc.stderr

            if "PLOT:" in output:
                match = re.search(r"PLOT:(.*?)\|(.*?)\n", output)
                if match:
                    labels_str = match.group(1).split(",")
                    values_str = match.group(2).split(",")
                    chart_data = {"labels": [s.strip() for s in labels_str], "values": [float(v) for v in values_str], "type": "line"}
                    output = output.replace(match.group(0), "")

            return jsonify({"output": output if output.strip() else "Exécuté avec succès.", "chart_data": chart_data})
        except Exception as e:
            return jsonify({"output": f"ERREUR SYSTÈME : {str(e)}"})
        finally:
            if os.path.exists(filename): os.remove(filename)
            if os.path.exists(output_exec): os.remove(output_exec)

    # --- 3. MOTEUR OCTAVE / SCILAB (NETTOYÉ ET OPTIMISÉ) ---
    elif lang_choice in ["scilab", "octave"]:
        filename = "temp_code.m"
        try:
            # On force le mode silencieux et sans avertissements
            full_code = "warning('off', 'all');\n" + code
            with open(filename, "w") as f:
                f.write(full_code)
            
            # Configuration de l'environnement pour supprimer les déchets (erreurs Qt/écran)
            env = os.environ.copy()
            env["QT_QPA_PLATFORM"] = "offscreen"
            
            run_proc = subprocess.run(
                ["octave", "--no-gui", "--quiet", "--no-window-system", "--eval", f"source('{filename}');"], 
                capture_output=True, 
                text=True, 
                timeout=15,
                env=env
            )
            
            # On ne prend que le stdout (les sorties de tes calculs) pour éviter les déchets du stderr
            output = run_proc.stdout

            # Extraction du PLOT
            if "PLOT:" in output:
                match = re.search(r"PLOT:(.*?)\|(.*?)(?:\n|$)", output)
                if match:
                    labels_str = match.group(1).split(",")
                    values_str = match.group(2).split(",")
                    chart_data = {
                        "labels": [s.strip() for s in labels_str], 
                        "values": [float(v) for v in values_str], 
                        "type": "line"
                    }
                    output = output.replace(match.group(0), "")

            return jsonify({
                "output": output if output.strip() else "Exécuté avec succès.", 
                "chart_data": chart_data
            })
        except subprocess.TimeoutExpired:
            return jsonify({"output": "ERREUR : Temps d'exécution dépassé (Boucle infinie ?)."})
        except Exception as e:
            return jsonify({"output": f"ERREUR SYSTÈME : {str(e)}"})
        finally:
            if os.path.exists(filename): os.remove(filename)

    return jsonify({"output": "Langage non supporté."})

@app.route('/aide_ia', methods=['POST'])
def aide_ia():
    data = request.get_json()
    error = data.get('error', '').lower()
    if "syntax" in error:
        conseil = "💡 Oups ! Vérifie tes parenthèses, tes points-virgules ou tes deux-points (:)."
    elif "indentation" in error:
        conseil = "📐 Problème d'alignement ! En Python, les espaces comptent."
    else:
        conseil = "🚀 Vérifie la logique de ton code ou la syntaxe du langage."
    return jsonify({"conseil": conseil})

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('.', 'sw.js')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)