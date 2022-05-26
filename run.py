# Python script that will run the model when invoked via mesa runserver

# temporary
from model import NSModel

model = NSModel(10, 10, 10)

for i in  range(10):
    model.step()