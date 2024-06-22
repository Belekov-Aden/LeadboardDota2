from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/#{reqion}", response_class=HTMLResponse)
def read_root(request: Request, reqion: str = 'europe'):
    return templates.TemplateResponse(
        request=request, name='main/main.html', context={"reqion": reqion}
    )
