"""
Cleanup module for the project.

Directories to be cleaned up recursively:
- .gradio/
- .vscode/
- data/
- logs/
- __pycache__/

Specific directories to be cleaned up:
- %USERPROFILE%/AppData/Local/Temp/gradio/
- %USERPROFILE%/AppData/Local/Temp/agent_audio_output/
- %USERPROFILE%/.deepface/
"""
import os
import shutil
import tempfile


def recursive_cleanup(directory: str) -> None:
    """
    Recursively clean up the specified directory.

    Parameters:
        directory (str): The directory path to clean up.
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)
        print(f"Directory cleaned up: {directory}")
    else:
        print(f"Directory not found: {directory}")


def specific_cleanup(directory: str) -> None:
    """
    Clean up the specified directory.

    Parameters:
        directory (str): The directory path to clean up.
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)
        print(f"Directory cleaned up: {directory}")
    else:
        print(f"Directory not found: {directory}")


if __name__ == "__main__":
    # Directories to be cleaned up recursively
    recursive_directories = [
        ".gradio",
        ".vscode",
        "data",
        "logs",
        "__pycache__",
        "conversation/__pycache__",
    ]

    for directory in recursive_directories:
        recursive_cleanup(directory)

    # Specific directories to be cleaned up
    specific_directories = [
        os.path.join(tempfile.gettempdir(), "gradio"),
        os.path.join(tempfile.gettempdir(), "agent_audio_output"),
        os.path.join(os.getenv("USERPROFILE"), ".deepface")
    ]

    for directory in specific_directories:
        specific_cleanup(directory)
    