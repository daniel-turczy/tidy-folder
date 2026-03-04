import os
from shutil import move
from file_categories import FILE_CATEGORIES

def get_unique_filename(destination_folder, filename):
    """
    Returns a filename that does not exist in the destination folder.
    If a file with the same name exists, add a counter (e.g. file(1).txt).
    """
    final_path = os.path.join(destination_folder, filename)
    counter = 1 # If a file has the same name, the counter will be added to the filename
    while os.path.exists(final_path): # While a file in this folder has the same name...
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}({counter}){ext}" # Add the counter to the filename
        final_path = os.path.join(destination_folder, new_filename)
        counter += 1
    return final_path


def move_file_safely(original_path, destination_folder, moved_files):
    """
    Moves a file to a folder and ensures there are no overwrites.
    Records the move in moved_files to allow an undo.
    """
    os.makedirs(destination_folder, exist_ok=True) # Make the folder unless it already exists
    filename = os.path.basename(original_path)
    final_path = get_unique_filename(destination_folder, filename)

    move(original_path, final_path) # Moves the file
    moved_files.append((final_path, original_path)) # Record move for undo
    return final_path


def remove_empty_folder(folder_path):
    """Removes a folder if it exists and is empty."""
    if os.path.exists(folder_path) and not os.listdir(folder_path):
        os.rmdir(folder_path)


def organise_folder(folder_path):
    """
    Organises files in the given folder into subfolders based on filetype.
    Returns a list of (final_path, original_path) tuples so that moves can be undone.
    """
    moved_files = []  # Stores (final_path, original_path) for each file to allow undo

    for filename in os.listdir(folder_path): # Loop through everything in the folder
        original_path = os.path.join(folder_path, filename) # Original path for the file
        
        if os.path.isfile(original_path): # Only process files, skip folders
            moved = False
            
            for category, extensions in FILE_CATEGORIES.items(): # Go through each file category
                for ext in extensions:# Go through each extension in the category
                    if filename.lower().endswith(ext): # If file has a valid extension...
                        destination_folder = os.path.join(folder_path, category)
                        move_file_safely(original_path, destination_folder, moved_files)
                        moved = True
                        break
                if moved:
                    break # On to the next file

            if not moved: # If no category matched, move to Others folder
                others_folder = os.path.join(folder_path, "Others")
                move_file_safely(original_path, others_folder, moved_files)

    return moved_files


def undo_moves(moved_files):
    """Undo the moves stored in moved_files and remove empty folders."""
    undone_any = False

    for final_path, original_path in reversed(moved_files): # Reverse the list of moves to start from most recent
        folder_to_check = os.path.dirname(final_path) # The folder that the file was in before undo

        if os.path.exists(final_path): # Check file still exists before moving to prevent errors
            original_folder = os.path.dirname(original_path) # Get the original folder path without the filename in it
            os.makedirs(original_folder, exist_ok=True) # Create the original folder if it doesn't exist
            move(final_path, original_path)
            undone_any = True

            remove_empty_folder(folder_to_check)
        else:
            filename = os.path.basename(final_path) # Only prints the filename, not the whole path
            print(f"{filename} not found. Could not move this file.")
            
    if undone_any:
        print("Undo completed.")
    else:
        print("No files were moved.")


if __name__ == "__main__":
    while True:
        folder_path = input("\nEnter the path to the folder you want to organise (q to quit):\n")

        if folder_path.lower() == "q":
            print("Exiting program.")
            break

        elif os.path.exists(folder_path):
            moved_files = organise_folder(folder_path)
            if moved_files:  # If any files were moved...
                print("Folder organised successfully!")
                undo = input("Type 'u' to undo this move or press ENTER to continue: ")
                if undo.lower() == "u":
                    undo_moves(moved_files)
                elif undo != "":
                    print("You could've just hit ENTER but ok...")
            else:
                print("No files were found to organise.")

        else:
            print("Folder path does not exist. Please try again.")