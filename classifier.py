from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
import uvicorn

from fastai import *
from fastai.vision import *

from io import BytesIO
import sys
import uvicorn
import aiohttp
import asyncio

path=Path('data/') 
char_to_id = pickle.load(open(path/'char_to_id.pkl','rb'))
classes = list(char_to_id.keys())

data = ImageDataBunch.single_from_classes(path,classes,tfms=get_transforms(),size=224)
learn = create_cnn(data, models.resnet34)
learn.load('stage-2')

async def get_bytes(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

app = Starlette()

@app.route("/classify-local", methods=["GET"])
async def classify_local(request):
    bytes = await get_bytes(request.query_params["url"])
    img = open_image(BytesIO(bytes))
    pred_class,pred_idx,outputs = learn.predict(img)
    return JSONResponse({
        "predictions": sorted(
            zip(learn.data.classes, map(float, outputs)),
            key=lambda p: p[1],
            reverse=True
            ), "pred_class":classes[pred_idx]
    })


@app.route("/classify-url", methods=["GET"])
async def classify_url(request):
    bytes = await get_bytes(request.query_params["url"])
    img = open_image(BytesIO(bytes))
    pred_class,pred_idx,outputs = learn.predict(img)
    return JSONResponse({
        "predictions": sorted(
            zip(learn.data.classes, map(float, outputs)),
            key=lambda p: p[1],
            reverse=True
            ), "pred_class":classes[pred_idx]
    })

@app.route("/upload", methods=["POST"])
async def upload(request):
    data = await request.form()
    bytes = await (data["file"].read())
    return predict_image_from_bytes(bytes)

def predict_image_from_bytes(bytes):
    img = open_image(BytesIO(bytes))
    pred_class,pred_idx,outputs = learn.predict(img)
    return JSONResponse({
        "predictions": sorted(
            zip(learn.data.classes, map(float, outputs)),
            key=lambda p: p[1],
            reverse=True
            ), "pred_class":classes[pred_idx]
    })
   
@app.route("/")
def form(request):
    return HTMLResponse(
        """
        <form action="/upload" method="post" enctype="multipart/form-data">
            Select image to upload:
            <input type="file" name="file">
            <input type="submit" value="Upload Image">
        </form>
        Or submit a URL:
        <form action="/classify-url" method="get">
            <input type="url" name="url">
            <input type="submit" value="Fetch and analyze image">
        </form>
    """)


@app.route("/form")
def redirect_to_homepage(request):
    return RedirectResponse("/")

@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    img_bytes = await (data['file'].read())
    img = open_image(BytesIO(img_bytes))
    pred_class, pred_idx, outputs = learn.predict(img)[0]
    return JSONResponse({'result': str(pred_class)})

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8888)
