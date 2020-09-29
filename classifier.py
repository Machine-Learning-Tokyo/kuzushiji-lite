from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from segment import *
import uvicorn
import matplotlib.image as mpimg

from fastai import *
from fastai.vision import *
from PIL import Image as PILImage
from io import BytesIO
import sys
import uvicorn
import aiohttp
import asyncio

from pathlib import Path
import pickle

path=Path('data/')
char_to_id = pickle.load(open(path/'char_to_id.pkl','rb'))
classes = list(char_to_id.keys())
tfms = get_transforms(do_flip=False)
data = ImageDataBunch.single_from_classes(path,classes,tfms=tfms,size=224)
learn = create_cnn(data, models.resnet34)
learn.load('stage-2')

unet = build_unet_model()

async def get_bytes(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

app = Starlette(debug=True)
#app.mount('/static', StaticFiles(directory='web'), name='static')
app.add_middleware(CORSMiddleware,
allow_origins=['*'],
allow_methods=['GET', 'POST'],
allow_headers=['*'],
allow_credentials=True,
expose_headers=['*'])

@app.route("/upload", methods=["POST"])
async def upload(request):
    data = await request.body()
    data = str(data)
    data = data.split(',')[1]
    data = base64.b64decode(data)
    file_like = BytesIO(data)
    data = Image.open(file_like)
    return predict_image_from_bytes(data)


def get_chunks(centers, img):
    crops = []
    #w, h = img.shape
    sq = 20
    for point in centers:

        dY = dX = 30
        nw_pnts = [max(0,point[0]-dX),min(512,point[0]+dX),max(point[1]-dY,0),min(512,point[1]+dY)]
        #if point[0]- dX <0: nw_pnts[0] = point[0]- dX
        #if point[1]- dY <0: nw_pnts[2] = point[1]- dY
        #if point[0]+ dX >512: nw_pnts[3] = point[0]- dX
        #if point[1]+ dY >512: nw_pnts[4] = point[1]- dY
        char_cut = img[nw_pnts[0]:nw_pnts[1],nw_pnts[2]:nw_pnts[3]]
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
async def upload_form(request):
    data = await request.form()
    bytes = await (data["file"].read())
    return predict_image_from_bytes(bytes)

@app.route("/predict",methods=["GET"])
def predict_image_from_bytes(bytes):
    img = open_image(BytesIO(bytes))
    img_g = np.array(PILImage.open(BytesIO(bytes)))
    img_g = 1- img_g.astype(np.float)/255.
    segmented_image = segment_img(img_g,unet,'small-ckpt/model.ckpt')
    com = calc_pred_centers_of_mass(segmented_image)
    chunks = get_chunks(com,img_g)
    chunk_preds = []
    for chunk in chunks:
        chunk = PILImage.fromarray(np.uint8((1-chunk)*255))
        chunk = pil2tensor(chunk,'float').float()
        chunk = chunk.repeat(3,1,1)
        chunk = Image(chunk)
        pred_class,pred_idx,outputs = learn.predict(chunk)
        #chunk_preds.append(classes[pred_idx])
        chunk_preds.append(classes[pred_idx])
    json_res = [{'x':int(com[i][0]),'y':int(com[i][-1]),'char':chunk_preds[i].lower().replace('+','\\')} for i in range(len(chunk_preds))]
    return JSONResponse(json_res)
   #    return JSONResponse({
    ##        "predictions": sorted(
     #           zip(learn.data.classes, map(float, outputs)),
     #           key=lambda p: p[1],
     #           reverse=True
     #           ), "pred_class":classes[pred_idx]
   # })



#@app.route('/')
#async def homepage(request):
    #template = app.get_template('index.html')
    #content = template.render(request=request)
#    return HTMLResponse(open('web/index.html','r').read())

#@app.route("/")
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


#@app.route("/form")
#def redirect_to_homepage(request):
#@    return RedirectResponse("/")

@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    img_bytes = await (data['file'].read())
    img = open_image(BytesIO(img_bytes))
    pred_class, pred_idx, outputs = learn.predict(img)[0]
    return JSONResponse({'result': str(pred_class)})

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8888)
