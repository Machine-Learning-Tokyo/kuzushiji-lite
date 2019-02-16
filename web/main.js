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
    this.takePicBtn = document.getElementById('take-pic-button');

    this.contentCanvas = document.getElementById('content-canvas');
    this.contentCtx = this.contentCanvas.getContext('2d');

    this.initalizeWebcamVariables();
    this.setUploadBtn();
    this.setUpProcessBtn();
    this.drawImageOnCanvas();
    this.setUpTakePicBtn();
  }

  setUpTakePicBtn() {
    this.takePicBtn.onclick = () => {
      console.log('taking pic');
      this.openModal();
    }
  }

  openModal() {
    this.camModal.modal('show');
    this.snapButton.onclick = () => {
      const hiddenCanvas = document.getElementById('hidden-canvas');
      const hiddenContext = hiddenCanvas.getContext('2d');
      hiddenCanvas.width = this.webcamVideoElement.width;
      hiddenCanvas.height = this.webcamVideoElement.height;
      hiddenContext.drawImage(this.webcamVideoElement, 0, 0, 
        hiddenCanvas.width, hiddenCanvas.height);
      const imageDataURL = hiddenCanvas.toDataURL('image/jpg');
      this.contentImg.src = imageDataURL;
      this.contentImg.onload = () => {
        this.drawImageOnCanvas();
      }
      this.camModal.modal('hide');
    };
  }

  initalizeWebcamVariables() {
    this.camModal = $('#cam-modal');

    this.snapButton = document.getElementById('snap-button');
    this.webcamVideoElement = document.getElementById('webcam-video');

    navigator.getUserMedia = navigator.getUserMedia ||
        navigator.webkitGetUserMedia || navigator.mozGetUserMedia ||
        navigator.msGetUserMedia;

    this.camModal.on('hidden.bs.modal', () => {
      this.stream.getTracks()[0].stop();
    })

    this.camModal.on('shown.bs.modal', () => {
      navigator.getUserMedia(
        {
          video: true
        },
        (stream) => {
          this.stream = stream;
          this.webcamVideoElement.srcObject = stream;
          this.webcamVideoElement.play();
        },
        (err) => {
          console.error(err);
        }
      );
    })
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
      this.processBtn.disabled = true;
      console.log('processing');
      this.contentCtx.font = "20px Georgia";
      this.contentCtx.fillStyle = "red";
      this.contentCtx.strokeStyle = 'red';
      const segments = this.segmentImage();
      for (let i=0; i < segments.length; i++) {
        let s = segments[i];
        this.contentCtx.rect(s.x, s.y, s.width, s.height);
        this.contentCtx.fillText(s.char, s.x, s.y+15)
      }
      this.contentCtx.stroke();
      this.processBtn.disabled = false;
    }
  }

  segmentImage() {
    return [
      {
        'x': 200,
        'y': 200,
        'width': 20,
        'height': 20,
        'char': "\u3041"
      },
      {
        'x': 160,
        'y': 215,
        'width': 25,
        'height': 25,
        'char': "\u3045"
      },
      {
        'x': 30,
        'y': 400,
        'width': 32,
        'height': 32,
        'char': "\u3043"
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
