from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.optimizers import SGD, RMSprop, Adagrad, Adam

"""
Fully Connected Neural Network class
--size adjustable [number of layers and neurons in each layer]
Katherine Mayo 4/15/2018
"""

class neuralNet(object):

  def __init__(self, numLayers=2, input_dim=734, num_classes=10, dropout=0, use_bn = False, reg=0.0):
    self.use_batchnorm = use_bn
    self.use_dropout = dropout > 0
    self.reg = reg
    self.numlayers = numLayers
    self.num_classes = num_classes
    
  """
  default values batch norm used only if the network uses batch normalization
  momentum and decay values are used only if the SGD variations are desired
  """
  def buildNet(self, neurons=4, optimizer='sgd', optParam={'lr': 0.001, 'momentum': 0, 'decay': 0}, bnorm={'momentum': 0.99, 'epsilon': 0.001}, dropout=0):
    """
    {affine - [batch norm] - relu - [dropout]} x (L - 1) - affine - softmax
    """
    model = Sequential()
    model.add(Dense(neurons, input_shape=(784,), use_bias = True))
    for i in range(self.numlayers-1):
      model.add(Dense(neurons, use_bias=True))
      if self.use_batchnorm:
        model.add(BatchNormalization(momentum=bnorm['momentum'], epsilon=bnorm['epsilon']))
      model.add(Activation('relu'))
      if self.use_dropout:
        model.add(Dropout(rate=dropout))
    model.add(Dense(self.num_classes, activation='softmax'))
    
    if optimizer == 'sgd':
      opt = SGD(optParam['lr'], optParam['momentum'], optParam['decay'])
    elif optimizer == 'rmsprop':
      opt = RMSprop(optParam['lr'])
    elif optimizer == 'adagrad':
      opt = Adagrad(optParam['lr'])
    else:
      opt = Adam(optParam['lr'])
    model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    return model
  
  def fitNet(self, model, data, batchSize=128, numEpochs=1, verbose=1):
    trainData = data['train_data']
    valData = data['val_data']
    trainLab = data['train_labels']
    valLab = data['val_labels']
    
    networkHistory = model.fit(trainData, trainLab, batchSize, numEpochs, verbose, validation_data=(valData, valLab))
    return networkHistory
  
  """
  ONLY USE THE FOLLOWING WHEN TESTING
  """
  def testModel(model, testData, testLabels):
    loss, accuracy = model.evaluate(testData, testLabels, verbos=1)
    return loss, accuracy
  
  def predictTest(model, testData, testLabels):
    predictions = model.predict(testData)
    return predictions
