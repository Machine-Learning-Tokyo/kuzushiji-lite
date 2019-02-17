from keras.models import load_model
from PIL import Image
import numpy as np

def classify_kmnist_classes(img_ar, model_file_path='naive_classifier.h5'):
  """img_ar contains a chunk float 0-1 shape (x, x) that will be resized to 28x28"""
  
  #resize
  resized_im_ar = np.array(Image.fromarray(img_ar).resize([28, 28]))
  
  loaded_model  = load_model(model_file_path)
  classes = loaded_model.predict_classes(resized_im_ar.reshape([1, 28, 28, 1]))
  
  my_class = int(classes[0])
  
  classes = ['お', 'き', 'す', 'つ', 'な', 'は', 'ま', 'や', 'れ', 'を']
  
  return classes[my_class]
  
  return int(classes[0])
