import os
import django
from django.apps import apps
from datetime import datetime
from inspect import getmembers, isclass, isfunction
from inspect import signature

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    django.setup()

def log_documentation(app_name, module_name, log_path):
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - Documented: {app_name}.{module_name}\n")

def write_css(docs_dir):
    css_path = os.path.join(docs_dir, "style.css")
    css_content = """
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        margin: 20px;
    }
    h1, h2, h3 {
        color: #333;
    }
    pre {
        background-color: #f4f4f4;
        padding: 10px;
        border-left: 5px solid #ccc;
    }
    a {
        text-decoration: none;
        color: #1a73e8;
    }
    a:hover {
        text-decoration: underline;
    }
    """
    with open(css_path, "w", encoding='utf-8') as css_file:
        css_file.write(css_content)


from inspect import signature, isfunction, ismethod

def document_class(cls):
    """Genera la documentación de una clase, excluyendo los métodos y atributos heredados."""
    doc = f"<h2>{cls.__name__}</h2>"
    doc += f"<p>{cls.__doc__}</p>" if cls.__doc__ else "<p>No hay docstring disponible</p>"

    # Atributos (solo los que pertenecen a la clase actual, no los heredados)
    doc += "<h3>Atributos:</h3><ul>"
    for attr_name, attr_value in cls.__dict__.items():
        if not callable(attr_value) and not attr_name.startswith("_"):
            doc += f"<li>{attr_name}</li>"
    doc += "</ul>"

    # Métodos (solo los definidos en la clase actual)
    doc += "<h3>Métodos:</h3><ul>"
    for method_name, method in cls.__dict__.items():
        if (isfunction(method) or ismethod(method)) and not method_name.startswith("__"):
            try:
                # Obtener la firma del método
                method_signature = signature(method)
                params = ', '.join(str(p) for p in method_signature.parameters.values())
                doc += f"<li>{method_name}({params}): {method.__doc__ if method.__doc__ else 'No hay docstring disponible'}</li>"
            except (ValueError, TypeError):
                doc += f"<li>{method_name}: No se puede obtener la firma (tipo especial o interno)</li>"
    doc += "</ul>"

    return doc


def generate_docs(apps_list, docs_dir):
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    log_path = os.path.join(docs_dir, "doc_log.txt")
    index_content = "<html><head><title>Documentation Index</title><link rel='stylesheet' href='style.css'></head><body>"
    index_content += "<h1>Documentation Index</h1><ul>"

    write_css(docs_dir)  # Write CSS file for styling

    for app in apps_list:
        print(f"Generating documentation for {app}...")
        try:
            if apps.is_installed(app):
                for module_name in ['models', 'views']:  # Limit to models and views
                    module = __import__(f'{app}.{module_name}', fromlist=[module_name])
                    doc_html = f"<h1>{app}.{module_name}</h1>"

                    # **Nuevo código para documentar funciones a nivel de módulo**
                    functions = [member for member in getmembers(module) if isfunction(member[1]) and member[1].__module__ == module.__name__]
                    if functions:
                        doc_html += "<h2>Funciones</h2><ul>"
                        for func_name, func in functions:
                            doc_html += document_function(func)
                        doc_html += "</ul>"
                    else:
                        doc_html += "<p>No se encontraron funciones.</p>"
                    # Documentar las clases dentro del módulo
                    classes = [member for member in getmembers(module) if isclass(member[1])]
                    if classes:
                        doc_html += "<h2>Clases</h2>"
                        for class_name, cls in classes:
                            doc_html += document_class(cls)
                    else:
                        doc_html += "<p>No se encontraron clases.</p>"

                   

                    # Agregar la estructura HTML
                    doc_html = f"""
                    <html>
                    <head>
                        <title>{app}.{module_name} Documentation</title>
                        <link rel='stylesheet' href='style.css'>
                    </head>
                    <body>
                        <nav><a href='index.html'>Back to Index</a></nav>
                        {doc_html}
                    </body>
                    </html>
                    """

                    output_file = os.path.join(docs_dir, f'{app}_{module_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}.html')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(doc_html)

                    log_documentation(app, module_name, log_path)

                    # Add to the index file
                    index_content += f"<li><a href='{os.path.basename(output_file)}'>{app}.{module_name} Documentation</a></li>"
            else:
                print(f"La aplicación {app} no está instalada o no está correctamente configurada.")
        except Exception as e:
            print(f"Error generating documentation for {app}: {e}")

    # Finalize index file
    index_content += "</ul></body></html>"
    index_file = os.path.join(docs_dir, "index.html")
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)

from inspect import signature, Signature

from typing import get_type_hints

def document_function(func):
    """Genera la documentación de una función incluyendo su docstring, parámetros y tipo de retorno."""
    doc = f"<h3>{func.__name__}</h3>"

    # Obtener la firma de la función (parámetros y retorno)
    try:
        func_signature = signature(func)
        params = ', '.join(str(p) for p in func_signature.parameters.values())
        
        # Intentar obtener el tipo de retorno de la función
        type_hints = get_type_hints(func)
        return_annotation = type_hints.get('return', 'None') if type_hints else 'None'

        # Agregar parámetros y retorno a la documentación
        doc += f"<p><strong>Parámetros:</strong> ({params})</p>"
    except (ValueError, TypeError):
        # Si no se puede obtener la firma, agregar una nota
        doc += "<p>No se pudo obtener la firma de la función.</p>"

    # Agregar el docstring de la función
    doc += f"<p>{func.__doc__}</p>" if func.__doc__ else "<p>No hay docstring disponible</p>"

    return doc



if __name__ == "__main__":
    setup_django()

    # Directorio donde se guardarán los documentos y el archivo de log
    docs_dir = os.path.join(os.getcwd(), "docs")

    # Lista de aplicaciones Django
    apps_list = ['Categorias', 'Plantillas', 'usuarios','content','roles','reportes']

    generate_docs(apps_list, docs_dir)
    print(f"Documentación generada con éxito en {docs_dir}.")
