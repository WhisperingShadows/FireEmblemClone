from PIL import Image
import numpy as np
from os import listdir
from os.path import isfile, join

mypath = r"C:\Users\admin\PycharmProjects\FireEmblemClone\Resources\Images\Atlas Files"
savepath = r"C:\Users\admin\PycharmProjects\FireEmblemClone\Resources\Images\Cropped Atlas Files"
imagefiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

imagefile = (r"C:\Users\admin\PycharmProjects\FireEmblemClone\Resources\Images\Common_Window.png")


def singleton(image, top, left, bottom, right):
    original = Image.open(image)

    width, height = original.size  # Get dimensions
    left = left
    top = top
    right = right
    bottom = bottom
    cropped_example = original.crop((left, top, right, bottom))

    cropped_example.save(join(savepath) + r"\Test.png", "PNG")
    print("Singleton Complete")


# singleton(imagefile, 0, 0, 375, 1483)

def multiImage():
    for i in imagefiles:
        image = Image.open(join(mypath, i))
        image.load()

        image_data = np.asarray(image)
        image_data_bw = image_data.max(axis=2)
        non_empty_columns = np.where(image_data_bw.max(axis=0) > 0)[0]
        non_empty_rows = np.where(image_data_bw.max(axis=1) > 0)[0]
        cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))

        image_data_new = image_data[cropBox[0]:cropBox[1] + 1, cropBox[2]:cropBox[3] + 1, :]

        new_image = Image.fromarray(image_data_new)
        new_image.save(join(savepath + r"\Cropped_" + i))


multiImage()

print("Task complete")
