from fastapi import FastAPI, File, UploadFile, Request, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from utils import extract_graph_image
import pymupdf
from dotenv import load_dotenv

load_dotenv()
templates = Jinja2Templates(directory="../templates")
app = FastAPI()
app.mount("/static", StaticFiles(directory="../static"), name="static")
app.mount("/data", StaticFiles(directory="../data"), name="data")

@app.get("/", response_class=HTMLResponse)
def return_homepage(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

def convert_to_image(uploaded_file):
    doc = pymupdf.open(f'../data/{uploaded_file.filename}')
    for page_index in range(len(doc)): 
        page = doc[page_index] 
        pix = page.get_pixmap()
        pix.save("../data/page.png") 
    
@app.post("/")
def upload_pdf_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if file.filename.endswith('.pdf'):
        contents = file.file.read()
        with open(f'../data/{file.filename}', 'wb') as f:
            f.write(contents)
        file.file.close()
    background_tasks.add_task(convert_to_image, file)
    return RedirectResponse(url="/output",
                            status_code=status.HTTP_303_SEE_OTHER, 
                            background=background_tasks)

@app.get("/output", response_class=HTMLResponse)
def return_out_page(request: Request):
    extract_graph_image('../data/page.png')
    return templates.TemplateResponse(request=request, name="output.html")