from flask import Flask, render_template, request, jsonify
import sys
import io
import subprocess
import os
import base64
import tempfile 

# Configuration pour dessiner sans écran
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    code = data.get('code', '')
    lang_choice = str(data.get('lang', 'python')).lower()
    
    plot_base64 = None 

    # --- MOTEUR PYTHON ---
    if lang_choice == "python":
        output_capture = io.StringIO()
        sys.stdout = output_capture
        try:
            plt.clf() 
            exec_globals = {'plt': plt}
            exec(code, exec_globals, exec_globals)
            result = output_capture.getvalue()

            # On vérifie si une figure contient vraiment un dessin (lignes, points, etc.)
            if plt.get_fignums():
                fig = plt.gcf()
                # On regarde s'il y a des axes ET si ces axes contiennent des données
                if fig.get_axes() and any(len(ax.get_lines()) > 0 or len(ax.get_children()) > 5 for ax in fig.get_axes()):
                    img_buf = io.BytesIO()
                    plt.savefig(img_buf, format='png', bbox_inches='tight')
                    img_buf.seek(0)
                    plot_base64 = base64.b64encode(img_buf.getvalue()).decode('utf-8')
                plt.close('all')

        except Exception as e:
            result = f"ERREUR PYTHON : {str(e)}"
        finally:
            sys.stdout = sys.__stdout__
            
        return jsonify({
            "output": result if result else "Exécuté avec succès.",
            "plot": plot_base64
        })

    # --- MOTEUR C / C++ ---
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
            for f in [filename, output_exec]:
                if os.path.exists(f): os.remove(f)

    # --- MOTEUR SCILAB (OCTAVE) - VERSION BLOCAGE TOTAL ---
    elif lang_choice == "scilab":
        fd, plot_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        
        # Le script force le silence complet et désactive les warnings
        scilab_script = (
            "graphics_toolkit('gnuplot');\n"
            "warning('off', 'all');\n"
            "page_screen_output(0);\n"
            f"{code}\n"
            f"if (isempty(get(0, 'Children')) == 0) print('{plot_path}', '-dpng', '-S800,600'); end"
        )
        
        try:
            run_process = subprocess.run(
                ["octave", "--no-gui", "--quiet", "--eval", scilab_script],
                capture_output=True, 
                text=True, 
                timeout=15,
                env={**os.environ, "GNUTERM": "canvas", "PAGER": "cat"}
            )
            
            # BLOCAGE : On ne regarde QUE stdout (les résultats demandés)
            # On ignore totalement stderr qui contient les déchets système
            lines = run_process.stdout.splitlines()
            
            blacklist = ["qstandardpaths", "xdg_runtime", "warning", "gnuplot", "graphics", "fontconfig", "maintained", "interpreter"]
            
            clean_lines = []
            for line in lines:
                l_lower = line.lower()
                # On bloque si la ligne contient un mot de la blacklist
                if any(bad in l_lower for bad in blacklist):
                    continue
                
                # On nettoie le "> " et les espaces
                clean = line.replace(">", "").strip()
                if clean:
                    clean_lines.append(clean)
            
            final_output = "\n".join(clean_lines).strip()

            # Gestion de l'image (Plot)
            if os.path.exists(plot_path) and os.path.getsize(plot_path) > 0:
                with open(plot_path, "rb") as img_file:
                    plot_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
            return jsonify({
                "output": final_output if final_output else "Exécution terminée.",
                "plot": plot_base64
            })
            
        except Exception as e:
            return jsonify({"output": f"ERREUR SYSTÈME : {str(e)}"})
        finally:
            if os.path.exists(plot_path): os.remove(plot_path)

    return jsonify({"output": "Langage non supporté."})

# --- ROUTE AIDE IA ---
@app.route('/aide_ia', methods=['POST'])
def aide_ia():
    data = request.get_json()
    error = data.get('error', '').lower()
    conseil = "💡 Erreur de structure. Vérifie tes points-virgules." if "syntax" in error else "🚀 Logique correcte."
    return jsonify({"conseil": conseil})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)