from keras.datasets import mnist
from neuralNet import *
import utils as ut
from data_utils import *

"""
Main code for running Neural Network
"""

if __name__ == '__main__':

  trainDir = ""
  testDir = ""
  classes = 2
  
  train_data, train_labels, height, width = load_data(trainDir)
  test_data, test_labels, _, _ = load_data(testDir)
  train_data = formatData(train_data, classes, height, width)
  test_data = formatData(test_data, classes, height, width)
  train_data, train_labels, val_data, val_labels = sampleData(train_data, train_labels)
  
  data = {'train_data': train_data, 'val_data': val_data, 'train_labels': train_labels, 'val_labels': val_labels, 'test_data': test_data, 'test_labels': test_labels}
  
  model = neuralNet(input_dim=height*width*3, num_classes=classes, dropout=0, use_bn=False, reg=0.0)
  net = model.buildNet(neurons=100, optimizer='sgd', optParam={'lr': 0.001, 'momentum': 0, 'decay': 0}, bnorm={'momentum': 0.99, 'epsilon': 0.001}, dropout=0)
  hist = model.fitNet(net, data, batchSize=128, numEpochs=2, verbose=1)
