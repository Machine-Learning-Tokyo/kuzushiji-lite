from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from segment import *
import uvicorn
import matplotlib.image as mpimg

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

unet = build_unet_model()

async def get_bytes(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

app = Starlette(debug=True)
#app.mount('/static', StaticFiles(directory='web'), name='static')

def get_chunks(centers, img):
    crops = []
    #w, h = img.shape
    for point in centers:
        char_cut = img[point[0]-50:point[0]+50,point[1]-50:point[1]+50]
        crops.append(char_cut)
    return crops

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

@app.route("/predict",methods=["GET"])
def predict_image_from_bytes(bytes):
    img = open_image(BytesIO(bytes))
    np_img = to_np(img)
    segmented_image = segment_img(np_img.T,unet)
    com = calc_pred_centers_of_mass(segmented_image)
    chunks = get_chunks(np_img.T,com)
    for chunk in chunks:
        pred_class,pred_idx,outputs = learn.predict(chunk)
        return JSONResponse({
            "predictions": sorted(
                zip(learn.data.classes, map(float, outputs)),
                key=lambda p: p[1],
                reverse=True
                ), "pred_class":classes[pred_idx]
    })



#@app.route('/')
#async def homepage(request):
    #template = app.get_template('index.html')
    #content = template.render(request=request)
#    return HTMLResponse(open('web/index.html','r').read())

#@app.route("/")
#def form(request):
#    return HTMLResponse(
#        """

#        <form action="/upload" method="post" enctype="multipart/form-data">
#            Select image to upload:
#            <input type="file" name="file">
#            <input type="submit" value="Upload Image">
#        </form>
#        Or submit a URL:
#        <form action="/classify-url" method="get">
#            <input type="url" name="url">
#            <input type="submit" value="Fetch and analyze image">
#        </form>
#    """)


#@app.route("/form")
#def redirect_to_homepage(request):
#    return RedirectResponse("/")

@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    img_bytes = await (data['file'].read())
    img = open_image(BytesIO(img_bytes))
    pred_class, pred_idx, outputs = learn.predict(img)[0]
    return JSONResponse({'result': str(pred_class)})

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8888)
