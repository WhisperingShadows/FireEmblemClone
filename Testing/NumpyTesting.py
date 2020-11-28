import numpy as np
import io

from time import sleep

from PIL import Image

myimage = Image.open(r"C:\Users\admin\PycharmProjects\FireEmblemClone\Resources\Backgrounds\Bg_Title.png")

data = np.asarray(myimage)

print("Type:", type(data))

print("Shape:", data.shape)

output = io.BytesIO()

np.savez(output, x=data)

content = output.getvalue()
splitvals = str(content).split(r"\\")

for i in range(len(splitvals)):
    print(splitvals[i])
