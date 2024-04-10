import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import requests
import os
import logging
from tkinter import ttk
import time

logging.basicConfig(level=logging.INFO, filename='download.log', format='%(asctime)s - %(levelname)s - %(message)s')

def download_images(tag, num_images, save_directory, exclude_tags=None):
    images_per_request = 100  # Number of images to request per API call
    num_requests = (num_images + images_per_request - 1) // images_per_request  # Calculate number of requests needed

    logging.info(f"Downloading images with tag '{tag}', number of images: {num_images}, save directory: {save_directory}")

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    downloaded_ids = set()  # Set to keep track of downloaded image IDs

    progress_bar["maximum"] = num_images

    start_time = time.time()

    for request_num in range(num_requests):
        url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={tag}&limit={images_per_request}&pid={request_num + 1}"
        response = requests.get(url)
        data = response.json()

        logging.info(f"Downloading images with tag '{tag}', request {request_num + 1}/{num_requests}")

        for index, image_info in enumerate(data['post'], start=request_num * images_per_request + 1):
            if index > num_images:
                return

            # Skip image if it has any excluded tag
            if exclude_tags and any(tag in image_info['tags'] for tag in exclude_tags):
                logging.info(f"Skipping image with ID {image_info['id']} due to excluded tag")
                continue

            image_id = image_info['id']
            if image_id in downloaded_ids:
                logging.info(f"Skipping image with ID {image_id} as it's already downloaded")
                continue

            image_url = image_info['file_url']
            image_extension = os.path.splitext(image_url)[1]
            image_path = os.path.join(save_directory, f"{image_id}{image_extension}")

            try:
                image_response = requests.get(image_url)
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                logging.info(f"Downloaded {image_path}")
                downloaded_ids.add(image_id)  # Add downloaded image ID to the set
                progress_bar["value"] = index
                progress_bar.update()

                # Get estimated time until completion
                elapsed_time = time.time() - start_time
                images_remaining = num_images - index
                time_per_image = elapsed_time / index
                estimated_time_remaining = time_per_image * images_remaining

                # Download progress and images downloaded out of blank
                progress_label.config(text=f"Downloaded {index} out of {num_images} images. Estimated time remaining: {int(estimated_time_remaining)} seconds")
            except Exception as e:
                logging.error(f"Failed to download {image_url}: {e}")

def download_images_gui():
    root = tk.Tk()
    root.withdraw()  # Hides that odd fucking blank window, seriously tf.gg

    # Create dialog window
    dialog = tk.Toplevel(root)
    dialog.title("Rabbit's Booru Grabber")

    # Use transparent image as icon
    icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
    if os.path.exists(icon_path):
        dialog.iconphoto(True, tk.PhotoImage(file=icon_path))

    # Tag input
    tag_label = tk.Label(dialog, text="Tag:")
    tag_label.grid(row=0, column=0, padx=5, pady=5)
    tag_entry = tk.Entry(dialog)
    tag_entry.grid(row=0, column=1, padx=5, pady=5)

    # Number of images input
    num_images_label = tk.Label(dialog, text="Number of Images:")
    num_images_label.grid(row=1, column=0, padx=5, pady=5)
    num_images_entry = tk.Entry(dialog)
    num_images_entry.grid(row=1, column=1, padx=5, pady=5)

    # Save directory selection
    def select_directory():
        save_directory = filedialog.askdirectory(title="Save Directory")
        directory_var.set(save_directory)

    directory_var = tk.StringVar()
    save_directory_label = tk.Label(dialog, text="Save Directory:")
    save_directory_label.grid(row=2, column=0, padx=5, pady=5)
    save_directory_entry = tk.Entry(dialog, textvariable=directory_var)
    save_directory_entry.grid(row=2, column=1, padx=5, pady=5)
    browse_button = tk.Button(dialog, text="Browse", command=select_directory)
    browse_button.grid(row=2, column=2, padx=5, pady=5)

    # Gui stuff for tag exclusion.
    exclude_tags_label = tk.Label(dialog, text="Blacklist Tags (comma-separated):")
    exclude_tags_label.grid(row=3, column=0, padx=5, pady=5)
    exclude_tags_entry = tk.Entry(dialog)
    exclude_tags_entry.grid(row=3, column=1, padx=5, pady=5)

    global progress_bar
    progress_bar = ttk.Progressbar(dialog, orient="horizontal", length=200, mode="determinate")
    progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=10)

    # Label to show download progress and estimated time remaining
    global progress_label
    progress_label = tk.Label(dialog, text="")
    progress_label.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

    # Download button
    def start_download():
        tag = tag_entry.get()
        num_images = int(num_images_entry.get())
        save_directory = directory_var.get()
        exclude_tags = exclude_tags_entry.get().split(",")  # Split comma-separated tags

        if tag and num_images and save_directory:
            try:
                download_images(tag, num_images, save_directory, exclude_tags)
                messagebox.showinfo("Download Complete", "Images downloaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download images: {e}")
        else:
            messagebox.showerror("Error", "Please provide all required information.")

    download_button = tk.Button(dialog, text="Download", command=start_download)
    download_button.grid(row=6, column=0, columnspan=3, padx=5, pady=10)

    # Additional label for instructions
    instruction_label = tk.Label(dialog, text="Enter tag and number of images to grab stuff from booru sites.")
    instruction_label.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

    dialog.mainloop()

if __name__ == "__main__":
    download_images_gui()
