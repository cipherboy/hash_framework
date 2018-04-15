import numpy as np
import os, csv, random
from PIL import Image

"""
Code for extracting data and labels
Katherine Mayo 4/15/2018
"""

def unpack_image(image):
  #assumes all images come in as the same size
  #otherwise use Image.resize((width, height))
  im = Image.open(image, 'r')
  width, height = im.size
  pixels = list(im.getdata())
  pixels = np.array(pixels).astype(np.float32)
  return pixels, width, height

#goes through a directory and gets the labels and images
def load_data(directoryName):
  files = os.listdir(directoryName)
  labels = []
  data = []
  width = 0
  height = 0
  for f in files:
    labels.append(f.split('-')[0])
    im, width, height = unpack_image(directoryName + '/' + f)
    data.append(im)
  return data, labels, height, width

def formatData(data, num, height, width):
  data = np.array(data)
  data = (data.reshape((num, height*width*3)).astype("float32"))
  return data

def sampleData(trainData, trainLabels, div=0.1):
  x = np.random.choice(trainData.shape[0], size=int(len(trainData)*div))
  val_data = trainData[x, :]
  val_labels = []
  for i in x:
    val_labels.append(trainLabels[i])
  train_data = trainData[-x,:]
  train_labels = [i for i in trainLabels if i not in val_labels]
  return train_data, train_labels, val_data, val_labels
