import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
from collections import OrderedDict
import numpy as np
import matplotlib
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as lines
from matplotlib.patches import Polygon
from PIL import Image
import cv2

# Root directory of the project
ROOT_DIR = os.path.abspath("/food-recognizer-tools")

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn import utils
from mrcnn import visualize
from mrcnn.visualize import display_images
import mrcnn.model as modellib
from mrcnn.model import log


from mrcnn.config import Config

# Weird bug with the detect method that prints a matrix
# this class is just to block it from outputing to the stdout
class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


class InferenceConfig(Config):
    NAME = "food"

    # GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 1

    # Uncomment to train on 8 GPUs (default is 1)
    GPU_COUNT = 1
    BACKBONE = 'resnet50'
    # Number of classes (including background)
    NUM_CLASSES = 41  # 1 Background + 40 classes

    STEPS_PER_EPOCH=10
    VALIDATION_STEPS=10

    DETECTION_MIN_CONFIDENCE = 0

    LEARNING_RATE=0.001
    IMAGE_MAX_DIM=256
    IMAGE_MIN_DIM=256

# intializes mask rcnn with the inference config and the trained model
def init_mask_rcnn():
    inference_config = InferenceConfig()
    inference_config.display()
    model_path = "mask_rcnn_food_0001.h5"  # Trained model weights
    model = modellib.MaskRCNN(mode='inference', 
                          config=inference_config,
                          model_dir=ROOT_DIR)
    # Load trained weights (fill in path to trained weights here)
    print("Loading weights from ", model_path) # using the trained model to perform inference
    model.load_weights(model_path, by_name=True)
    return model

model = init_mask_rcnn()

# food classes we have 40 + 1 and the 1 is the background or BG
food_classes = ['BG',
 'bread-wholemeal',
 'potatoes-steamed',
 'broccoli',
 'butter',
 'hard-cheese',
 'water',
 'banana',
 'wine-white',
 'bread-white',
 'apple',
 'pizza-margherita-baked',
 'salad-leaf-salad-green',
 'zucchini',
 'water-mineral',
 'coffee-with-caffeine',
 'avocado',
 'tomato',
 'dark-chocolate',
 'white-coffee-with-caffeine',
 'egg',
 'mixed-salad-chopped-without-sauce',
 'sweet-pepper',
 'mixed-vegetables',
 'mayonnaise',
 'rice',
 'chips-french-fries',
 'carrot',
 'tomato-sauce',
 'cucumber',
 'wine-red',
 'cheese',
 'strawberries',
 'espresso-with-caffeine',
 'tea',
 'chicken',
 'jam',
 'leaf-spinach',
 'pasta-spaghetti',
 'french-beans',
 'bread-whole-wheat'
 ]




###########################################################################################
# Get the image path and read it using PIL since cv2 doesn't read the channels correctly
image_path = "006563.jpg"
pil_img = Image.open(image_path) # Returns a PIL jpg object
img = np.array(pil_img) # Convert to numpy array
###########################################################################################





############################################################################
# Read the image, remove axis and save the fig as png 
# NOTE: matplotlib doesn't support jpg
# plt.imshow(img)
# plt.axis('off')
# plt.savefig('/food-recognizer/pred.png', bbox_inches='tight', pad_inches = 0)
# plt.close()
#############################################################################


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf, bbox_inches='tight', pad_inches = -0.27)
    buf.seek(0)
    img = Image.open(buf)
    return img

# Function responsible for adding the predicted mask, bbox and label
def display_instances(image, boxes, masks, class_ids, class_names,
                      scores=None, title="",
                      figsize=(16, 16), ax=None):
    """
    boxes: [num_instance, (y1, x1, y2, x2, class_id)] in image coordinates.
    masks: [height, width, num_instances]
    class_ids: [num_instances]
    class_names: list of class names of the dataset
    scores: (optional) confidence scores for each box
    figsize: (optional) the size of the image.
    """
    # Number of instances
    N = boxes.shape[0]
    if not N:
        print("\n*** No instances to display *** \n")
    else:
        assert boxes.shape[0] == masks.shape[-1] == class_ids.shape[0]

    if not ax:
        _, ax = plt.subplots(1, figsize=figsize)

    # Generate random colors
    colors = visualize.random_colors(N)

    # Show area outside image boundaries.
    height, width = image.shape[:2]
    ax.set_ylim(height + 10, -10)
    ax.set_xlim(-10, width + 10)
    ax.axis('off')
    ax.set_title(title)

    masked_image = image.astype(np.uint32).copy()
    
    # labels to keep track of classes
    labels = []
    for i in range(N):
        color = colors[i]

        # Bounding box
        if not np.any(boxes[i]):
            # Skip this instance. Has no bbox. Likely lost in image cropping.
            continue
        y1, x1, y2, x2 = boxes[i]
        p = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2,
                              alpha=0.7, linestyle="dashed",
                              edgecolor=color, facecolor='none')
        ax.add_patch(p)

        # Label
        class_id = class_ids[i]
        score = scores[i] if scores is not None else None
        label = class_names[class_id]
        labels.append(label)
        x = random.randint(x1, (x1 + x2) // 2)
        caption = "{} {:.3f}".format(label, score) if score else label
        ax.text(x1, y1 + 8, caption,
                color='w', size=11, backgroundcolor="none")

        # Mask
        mask = masks[:, :, i]
        masked_image = visualize.apply_mask(masked_image, mask, color)

        # Mask Polygon
        # Pad to ensure proper polygons for masks that touch image edges.
        padded_mask = np.zeros(
            (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
        padded_mask[1:-1, 1:-1] = mask
        contours =  visualize.find_contours(padded_mask, 0.5)
        for verts in contours:
            # Subtract the padding and flip (y, x) to (x, y)
            verts = np.fliplr(verts) - 1
            p = Polygon(verts, facecolor="none", edgecolor=color)
            ax.add_patch(p)
    ax.imshow(masked_image.astype(np.uint8))
    plt.axis('off')
    fig = plt.gcf()
    mask_img = fig2img(fig)
    # plt.savefig('/food-recognizer/pred.png', bbox_inches='tight', pad_inches = -0.27) # saves in Secondary storage not needed and reduces W/R cycles of the storage
    # plt.close()
    return labels, mask_img
    # plt.show()


##############################################################
with HiddenPrints():
    results = model.detect([img])
r = results[0]
print(results)
labels, mask_img = display_instances(img, r['rois'], r['masks'], r['class_ids'], 
                                food_classes, r['scores'])

print(type(mask_img))

img = np.array(mask_img)

img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
print(labels)
cv2.imwrite('test2.png', img)

##############################################################




# def pred_img(img, model):
#     with HiddenPrints():
#         results = model.detect([img])
#     r = results[0]
#     print(results)
#     labels = display_instances(img, r['rois'], r['masks'], r['class_ids'], 
#                                 food_classes, r['scores'])
#     return labels

