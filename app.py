
import numpy as np
import os
import gradio as gr
import shutil
import zipfile
import tempfile
from pathlib import Path
from launch_inference import launch_inference

#Variables

#Image example to be run on Faster Detector (Top-down view)
example = "/app/example.jpg"
#Image example to be run on Faster Detector (Top-down view)
uploaded_images = Path("/app/uploaded_images")

#Inference threshold
threshold = 0.4

#Functions
#Switch tab and go to tool setup
def change_tab():
    return gr.Tabs.update(selected=1)

#Switch tab and go to tool setup
def upload_visible():
    return zip_upload.update(visible=True)

#Activate re-run button when threshold has been changed 
def active_rerun():
    return rerun_btn.update(interactive=True)

#Change visibility of components groing runtime back to setup 
def change_visibility():
    return result_group.update(visible=False), setup_col.update(visible=True), input_col.update(visible=True)

#Clean the Conveyor tyoe and App type strings for folder name
def clean_string(conv, app):
    app_info = "_"+conv+"_"+app
    app_info = app_info.replace(" ","")
    return app_info

#Function to populate the Image Gallery with Faster Detector inference Results. 
#Hides Setup and Input Column and makes the Runtime Box visible
def gallery_results(conveyor_type, app_type):
    app_info = clean_string(conveyor_type, app_type)
    result_folder = launch_inference(uploaded_images,threshold, app_info)
    list_images = os.listdir(result_folder)
    list_image_path = [result_folder / img_name for img_name in list_images]
    return list_image_path, result_group.update(visible=True), setup_col.update(visible=False), input_col.update(visible=False)

#Functions to Upload Files
def list_images(img_path):
    list_images = os.listdir(img_path)
    list_image_path = [img_path / img_name for img_name in list_images]
    print(list_image_path)
    return list_image_path, 


def extract_images(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

def move_images(source_folder, destination_folder):

    # Get a list of image files in the source folder
    image_files = [f for f in os.listdir(source_folder)]

    # Move each image file to the destination folder
    for image_file in image_files:
        source_path = os.path.join(source_folder, image_file)
        destination_path = os.path.join(destination_folder, image_file)
        shutil.move(source_path, destination_path)

    # Remove the empty TestImages folder
    os.rmdir(source_folder)


def process_files(fileobjs):
    destination_dir = Path.cwd()
    # destination_dir = Pathe("/home/g5_team3/Demo")
    img_path = destination_dir / "Uploaded_Images"
    if img_path.exists():
        shutil.rmtree(img_path)
    img_path.mkdir()
    for fileobj in fileobjs:
        path = os.path.join(destination_dir, os.path.basename(fileobj.name))
        shutil.copyfile(fileobj.name, path)
        print(fileobj.name)
        zip_fname = fileobj.name.split('/')[-1]
        extract_images(destination_dir / zip_fname, img_path)
    if len(os.listdir(img_path)) == 1:
        move_images(source_folder = img_path / os.listdir(img_path)[-1], destination_folder = img_path)
    list_images(img_path)
    return run_btn.update(visible=True)

#Function to Make Run button and results tab visible
#def uploadClick():
    #return {
        #run_btn: gr.update(visible=True),
        #result_group: gr.update(visible=True),
    #}            

#######################################################################################################################

#Main user interface
with gr.Blocks() as demo:

    #App Title
    gr.Markdown("# Logistics Faster Detector Demo")

    #Landing Page 
    #Getting started Tab 
    #Contains information about FD, proper use, and requirements.
    with gr.Tabs() as tabs: 
        with gr.TabItem("Getting Started", id=0)as start_tab:
            gr.Markdown("""
                        ## Logistics Faster Detector
                        
                        ### Motivation 

                        Validate a lightweight pre-trained package detector that performs reliably at high 
                        inspection speeds & complex item(s) positioning.
                        <br>
                        
                        This tool has been **pre-trained** with common Logistics application images.
                        <br>

                        > Pretrained model version currently in use:
                        <br>
                        > **v4**  *(Trained on 7/28/2023)*

                        ### Disclaimer
                        This tool is still in **testing phase**


                        Our team will keep a copy of all the images uploaded and information provided by the user to this app


                        ### Support

                        Contact [Carlos Velasquez](carlos.velasquez@cognex.com), [Lauren Chang](lauren.chang@cognex.com), or [Aaron Horrowitz](aaron.horowitz@cognex.com) for suggestions/troubleshooting 
                        <br>
                        <br>
                        """)

            start_btn = gr.Button(value="Start", variant="primary")
            start_btn.click(change_tab, None, tabs)

    #Run Tool tab
    #Upload test images, and view inference results
        with gr.TabItem("Faster Detector", id=1) as run_tab:
            with gr.Row():
                with gr.Column(scale=1, visible=True) as setup_col:
                    with gr.Box():
                        gr.Markdown("## Image Requirements & Tips")
                        gr.Markdown("""
                                    <br>

                                    Must be provided as a **.zip archive**


                                    Must be in one of the following formats: **JPEG (JPG), BMP, PNG**


                                    Image angle must be **top-down view**

                                    
                                    Tool accepts both **monochrome and colored** images from different applications and conveyor types.


                                    For best perfomance use **cropped images**

                                    <br>
                                    """)
                        example_image = gr.Image(label="Example images for reference", value=example, width=500, show_download_button=False)

                with gr.Column(scale=2, visible=True)as input_col:
                    with gr.Box():
                        gr.Markdown("## Setup Faster Detector")
                        gr.Markdown("<br>")
                        gr.Markdown("### 1) Application Details")
                        gr.Markdown("Please provide information about the application you are trying to solve")
                        gr.Markdown("<br>")

                        conveyor_type = gr.Dropdown(
                            ["Flat", "CrossBelt", "Roller", "Tilt Tray", "Bombay"], 
                            label="Conveyor Type", info="What conveyor was used in the application you are trying to solve?" 
                        )

                        app_type = gr.Dropdown(
                            ["Singulated objects", "Side By Side"], 
                            label="Application Type", info="How are the objects positioned in the application you are trying to solve?"
                        )

                        gr.Markdown("<br>")

                        zip_upload = gr.File(label="Upload Images", type="file", file_count="multiple", visible=False)

                        gr.Markdown("<br>")
                        run_btn = gr.Button("Run", visible=False, variant="primary", size="lg", scale=1)
                        app_type.change(upload_visible, [], zip_upload)
                        zip_upload.change(process_files, zip_upload, run_btn)

                
            with gr.Box(visible=False) as result_group:
                gr.Markdown("## Results")
                gr.Markdown("*Current Faster Detector creates axis aligned bounding boxes*")

                gr.Markdown("<br>")
                with gr.Row():
                    with gr.Column(scale=1) as info_col:
                        with gr.Box() as _box:     
                            gr.Markdown("**Inference Threshold**")
                            gr.Markdown("*Move slider to change threshold*")
                            threshold_slider = gr.Slider(minimum=0, maximum=1, value=threshold, step=0.01, info="Default threshold value is "+ str(threshold), show_label=False, interactive=False )
                            gr.Markdown("<br>")
                            gr.Markdown("*Click to run inference with chosen theshold*")
                            gr.Markdown("<br>")

                            rerun_btn = gr.Button("Re-run", variant="secondary", size="lg", interactive=False)
                            threshold_slider.change(active_rerun, [], [rerun_btn])

                        with gr.Box() as rerun_box:     
                            gr.Markdown("### Run another dataset?")
                            gr.Markdown("<br>")
                            back_to_setup = gr.ClearButton(value="Back to setup", variant="secondary", size="sm")

                    with gr.Column(scale=4) as runtime_col:
                        with gr.Box() as info_box:
                            gr.Markdown("""
                                    Use **left & right arrow keys** to navigate.

                                        
                                    Exit the gallery view by clicking the **"X" button**.
                                    """)
                        image_input = gr.Gallery(preview=True, show_share_button=False, show_download_button=False)
                       

                        
                        
            run_btn.click(gallery_results,[conveyor_type, app_type],[image_input, result_group, setup_col,input_col])
            back_to_setup.add([image_input, conveyor_type, app_type, zip_upload])
            back_to_setup.click(change_visibility,[], [result_group, setup_col, input_col])

    demo.launch(share=True, server_name = "0.0.0.0")