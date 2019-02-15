import 'babel-polyfill';

const MAX_DIM = 512;

/**
 * Main application to start on window load
 */
class Main {
  constructor() {
    this.fileSelect = document.getElementById('file-select');
    this.contentImg = document.getElementById('content-img');
    this.uploadBtn = document.getElementById('upload-button');
    this.processBtn = document.getElementById('process-button');

    this.contentCanvas = document.getElementById('content-canvas');
    this.contentCtx = this.contentCanvas.getContext('2d');

    this.setUploadBtn();
    this.setUpProcessBtn();
    this.drawImageOnCanvas();
  }

  drawImageOnCanvas() {
    this.contentCtx.clearRect(0, 0, this.contentCanvas.width, this.contentCanvas.height);
    let xH, yH;
    [xH, yH] = this.getResizedDimensions(this.contentImg.width, this.contentImg.height);
    this.contentCtx.drawImage(this.contentImg, 0, 0, xH, yH);
  }

  getResizedDimensions(xHeight, xWidth) {
    let larger;
    larger = xHeight > xWidth ? xHeight : xWidth;

    const scaling = MAX_DIM / larger;
    return [xHeight*scaling, xWidth*scaling];
  }

  setUpProcessBtn() {
    this.processBtn.onclick = () => {
      console.log('processing');
      this.contentCtx.strokeStyle = 'red';
      const segments = this.segmentImage();
      for (let i=0; i < segments.length; i++) {
        let s = segments[i];
        this.contentCtx.rect(s.x, s.y, s.width, s.height);
      }
      this.contentCtx.stroke();
    }
  }

  segmentImage() {
    return [
      {
        'x': 200,
        'y': 200,
        'width': 20,
        'height': 20,
      },
      {
        'x': 160,
        'y': 215,
        'width': 25,
        'height': 25,
      },
      {
        'x': 30,
        'y': 400,
        'width': 32,
        'height': 32,
      },
    ]
  }

  setUploadBtn() {
    this.uploadBtn.onclick = () => {
      console.log('uploading image');
      this.fileSelect.onchange = (evt) => {
        const f = evt.target.files[0];
        const fileReader = new FileReader();
        fileReader.onload = ((e) => {
          this.contentImg.src = e.target.result;
          this.contentImg.onload = () => {
            this.drawImageOnCanvas();
          }
        });
        fileReader.readAsDataURL(f);
        this.fileSelect.value = '';
      };
      this.fileSelect.click();
    };
  }
}

window.addEventListener('load', () => new Main());
