from __future__ import division, print_function

from tf_unet import unet
import numpy as np
from scipy import ndimage
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

def build_unet_model(model_ckpt='model.ckpt'):
  return unet.Unet(channels=1, n_class=2, layers=3, features_root=16)

def segment_img(img_array, net):
  """
  img_array is shape (512, 512) np.float from 0 to 1.
  net contains the unet returned by build_unet_model
  return value is shape (512, 512) mask for use in 
  calc_pred_centers_of_mass
  """
  prediction = net.predict(model_ckpt, img_array.reshape(1, 512, 512, 1))
  prediction = prediction[0, :, :, 0]
  return prediction

def calc_pred_centers_of_mass(prediction_ar):
  """
  prediction_ar contains return value of segment_img
  returns a list of centroids.
  """
  bool_pred = prediction_ar > 0.8
  bool_pred = ~bool_pred
  int_pred = bool_pred.astype(int)
  structure = np.ones((3, 3), dtype=np.int)  # this defines the connection filter
  labeled, ncomponents = ndimage.measurements.label(int_pred, structure)
  indices = np.indices(int_pred.shape).T[:,:,[1, 0]]
  centers_of_mass = []

  for i in range(1, ncomponents+1):
    if len(indices[labeled==i]) > 30:
      com = np.mean(indices[labeled==i], axis=0)
      centers_of_mass.append(com)
    else:
      print('dropping center')

  centers_of_mass = np.array(centers_of_mass).astype(int)
  centers_of_mass += [[16, 16]]
  return centers_of_mass
