import importlib.metadata 
packages = [
    'langchain',
    'langchain_core',
    'python-dotenv',
    'streamlit'
]
for p in packages:
    try:
        version = importlib.metadata.version(p)
        print(f"{p}: {version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{p} is not installed.")