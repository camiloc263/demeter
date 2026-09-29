from setuptools import setup, find_packages

setup(
    name="demeter_core",
    version="1.0.0",
    description="Librería compartida para los microservicios de la Granja Demeter",
    packages=find_packages(),
    # --- MEJORA: Especificar las dependencias ---
    # Al instalar 'demeter_core', pip también instalará pydantic y python-dateutil
    # si no están ya presentes. Esto evita errores de importación en los microservicios.
    install_requires=[
        "pydantic>=2.0,<3.0",
        "httpx>=0.27,<1.0",
    ],
)