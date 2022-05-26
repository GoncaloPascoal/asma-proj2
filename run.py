# Python script that will run the model when invoked via mesa runserver

# temporary
from model import NSModel

empty_model = NSModel(10)
empty_model.step()