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
    [xH, yH] = this.getStartingDimensions(this.contentImg.width, this.contentImg.height);

    this.contentCtx.drawImage(this.contentImg, xH, yH, MAX_DIM, MAX_DIM, 0, 0, MAX_DIM, MAX_DIM);
  }

  getStartingDimensions(xHeight, xWidth) {
    let xOut, yOut;
    if (MAX_DIM >= xHeight) {
      xOut = 0;
    } else {
      xOut = (xHeight - MAX_DIM) / 2;
    }

    if (MAX_DIM >= xWidth) {
      yOut = 0;
    } else {
      yOut = (xWidth - MAX_DIM) / 2;
    }
    console.log(xOut, yOut);
    return [xOut, yOut];
  }

  getResizedDimensions(xHeight, xWidth) {
    let larger;
    larger = xHeight > xWidth ? xHeight : xWidth;

    const scaling = MAX_DIM / larger;
    return [xHeight*scaling, xWidth*scaling];
  }

  drawSegmentsFromObject(segments) {
    console.log('drawing segments', segments)
    this.contentCtx.font = "30px Georgia";
    this.contentCtx.fillStyle = "red";
    this.contentCtx.strokeStyle = "red";
    for (let i=0; i < segments.length; i++) {
      let s = segments[i];
      this.contentCtx.fillRect(s.x-5, s.y-5, 10, 10);
      this.contentCtx.fillText(s.char, s.x+5, s.y+5);
    }
    this.contentCtx.stroke();
  }

  setUpProcessBtn() {
    this.processBtn.onclick = () => {
      this.processBtn.disabled = true;
      console.log('processing');
      const canvasData = this.contentCanvas.toDataURL('image/jpeg');
      const ajax = new XMLHttpRequest();
      ajax.open('POST', 'http://localhost:8008/upload');
      ajax.setRequestHeader('Content-Type', 'application/upload');
      ajax.send(canvasData);
      ajax.onload = (x) => {
        const resp = JSON.parse(x.target.response);
        this.drawSegmentsFromObject(resp);
      }
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
