from keras.utils import np_utils
import matplotlib.pyplot as plt

"""
Utility methods for fixing categories and plotting graphs
Katherine Mayo 4/15/2018
"""

def setLabels(labels, numCategories):
  return np_utils.to_categorical(labels, numCategories)

def plotNetHistory(networkHistory):
  plot.figure()
  plt.xlabel('Epochs')
  plt.ylabel('Loss')
  plt.plot(networkHistory.history['loss'])
  plt.plot(networkHistory.history['val_loss'])
  plt.legend(['Training', 'Validation'])
  plt.figure()
  
  plt.xlabel('Epochs')
  plt.ylabel('Accuracy')
  plt.plot(networkHistory.history['acc'])
  plt.plot(networkHistory.history['val_acc'])
  plt.legend(['Training', 'Validation'], loc='lowerright')
  plt.show()
