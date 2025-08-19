import os
import argparse
from pathlib import Path


def should_ignore_folder(folder_name):
    """Determine if a folder should be ignored based on its name."""
    ignore_prefixes = ['.', '__']
    ignore_names = ['venv', 'node_modules', '__pycache__']
    return (any(folder_name.startswith(prefix) for prefix in ignore_prefixes) or
            folder_name in ignore_names)


def should_ignore_file(file_name):
    """Determine if a file should be ignored based on its name or extension."""
    ignore_extensions = ['.pyc', '.pyo', '.pyd', '.so', '.dll']
    ignore_prefixes = ['.', '#', '~']
    ignore_names = ['Thumbs.db', 'desktop.ini']
    file_ext = os.path.splitext(file_name)[1]
    return (file_ext.lower() in (ext.lower() for ext in ignore_extensions) or
            any(file_name.startswith(prefix) for prefix in ignore_prefixes) or
            file_name.lower() in (name.lower() for name in ignore_names))


def is_allowed_path(current_path, root_dir, allowed_folders):
    """Check if the current path should be processed."""
    if current_path == root_dir:
        return True

    # Convert to Path objects for proper comparison
    current_path = Path(current_path)
    root_dir = Path(root_dir)

    # Check if we're in an allowed subfolder
    try:
        relative_path = current_path.relative_to(root_dir)
        path_parts = relative_path.parts

        # Check each component of the path
        for part in path_parts:
            if part in allowed_folders:
                return True
    except ValueError:
        pass  # Path is not under root_dir

    return False


def generate_directory_report(root_dir, output_file, allowed_folders=None):
    """Generate a report of directory structure and file contents."""
    if allowed_folders is None:
        allowed_folders = []

    root_dir = str(Path(root_dir).resolve())  # Normalize the path

    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write(f"Directory Report for: {root_dir}\n")
        f_out.write("=" * 50 + "\n\n")

        for root, dirs, files in os.walk(root_dir):
            # Remove ignored folders
            dirs[:] = [d for d in dirs if not should_ignore_folder(d)]

            # Check if this path should be processed
            if not is_allowed_path(root, root_dir, allowed_folders):
                dirs[:] = []  # Don't recurse further
                continue

            # Remove ignored files
            files = [f for f in files if not should_ignore_file(f)]

            # Skip empty directories
            if not dirs and not files:
                continue

            # Write directory info
            f_out.write(f"\nDirectory: {root}\n")
            f_out.write("-" * 50 + "\n")

            if dirs:
                f_out.write("Subdirectories:\n")
                for d in dirs:
                    f_out.write(f"  - {d}\n")
                f_out.write("\n")

            if files:
                f_out.write("Files:\n")
                for file in files:
                    file_path = os.path.join(root, file)
                    f_out.write(f"  - {file}\n")

                    if file.endswith(('.py', '.frag', '.vert', '.yaml')):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f_in:
                                f_out.write("\n    Contents:\n")
                                f_out.write("    " + "-" * 46 + "\n")
                                for line in f_in:
                                    f_out.write(f"    {line.rstrip()}\n")
                                f_out.write("    " + "-" * 46 + "\n\n")
                        except Exception as e:
                            f_out.write(f"    [Error reading file: {str(e)}]\n\n")


def main():
    parser = argparse.ArgumentParser(description='Generate a directory report with file contents.')
    parser.add_argument('directory', nargs='?',
                        default=r'D:\git_repositories\alexandrepv\simple_3d_graphics_engine\src3',
                        help='Root directory to scan')
    args = parser.parse_args()

    OUTPUT_FILE = Path(__file__).parent / "all_files.txt"
    ALLOWED_FOLDERS = [
        # Add folder names here that should be included recursively
        "components",
        "editors",
        "entities",
        "gizmos",
        "io",
        "shaders",
    ]

    print(f"Generating report for: {args.directory}")
    print(f"Allowed folders for recursion: {ALLOWED_FOLDERS}")

    generate_directory_report(args.directory, OUTPUT_FILE, ALLOWED_FOLDERS)

    print(f"Report generated successfully at: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()