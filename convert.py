import os

def convert_to_utf8(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.py', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-16') as f:
                        content = f.read()
                    if content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Converted {filepath} to UTF-8")
                except UnicodeError:
                    pass
                except Exception as e:
                    print(f"Error {filepath}: {e}")

convert_to_utf8("frontend/src")
convert_to_utf8("backend/app")
