import os
import sys
import django
from django.apps import apps
from pydoc import render_doc, html
from datetime import datetime

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    django.setup()

def log_documentation(app_name, module_name, log_path):
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - Documented: {app_name}.{module_name}\n")

def generate_docs(apps_list, docs_dir):
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    log_path = os.path.join(docs_dir, "doc_log.txt")

    for app in apps_list:
        print(f"Generating documentation for {app}...")
        try:
            if apps.is_installed(app):
                for module_name in ['views', 'models', 'forms']:
                    module = __import__(f'{app}.{module_name}', fromlist=[module_name])
                    doc_html = html.document(module, f"Documentation for {app}.{module_name}")
                    output_file = os.path.join(docs_dir, f'{app}_{module_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}.html')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(doc_html)
                    log_documentation(app, module_name, log_path)
            else:
                print(f"La aplicación {app} no está instalada o no está correctamente configurada.")
        except Exception as e:
            print(f"Error generating documentation for {app}: {e}")

if __name__ == "__main__":
    setup_django()

    # Directorio donde se guardarán los documentos y el archivo de log
    docs_dir = os.path.join(os.getcwd(), "docs")

    # Lista de aplicaciones Django
    apps_list = ['Categorias', 'Plantillas', 'usuarios']

    generate_docs(apps_list, docs_dir)
    print(f"Documentación generada con éxito en {docs_dir}.")

