from flask import Flask, jsonify, make_response, request, Response
import numpy as np
import cv2
import mask_rcnn_infer

app = Flask(__name__)


@app.route('/pred-img', methods=['POST'])
def pred_img():

    img_str = request.files['image'].read()

    img = np.fromstring(img_str, np.uint8)

    # cv2 reads images in BGR order aslong as you are using cv2 for all image processing
    # You don't need to switch the order to RGB
    # Other image processing libraries use RGB ordering like matplotlib and PIL
    # in this case you need to convert BGR to RGB 
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # do Mask R-CNN processing here

    labels, mask_image = mask_rcnn_infer.pred_img(img, model)

    cv2.imwrite('pred.png', mask_image)
    
    # Return Mask R-CNN predicted labels
    return make_response(jsonify({'ingredients': labels}))


    


if __name__ == '__main__':
    model = mask_rcnn_infer.init_mask_rcnn()
    app.run(host="0.0.0.0", port=5000)