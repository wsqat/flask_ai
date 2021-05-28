import io
import json

from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request


app = Flask(__name__)  # 固定写法
imagenet_class_index = json.load(open('imagenet_class_index.json'))
model = models.densenet121(pretrained=True)
model.eval()


def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)


def get_prediction(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    return imagenet_class_index[predicted_idx]

#'/predict'是会影响请求的格式，可自由改名。
# 需要添加“get”方法，才能直接通过浏览器发送请求
# 请求的路径path是图片的路径，一般是在服务端本机
# 浏览器输入实例,请换自己的ip和路径：http://127.0.0.1:5000/predict?path=/data/Projects/Flask/deploy/flask_ai/cat.jpeg


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':  # 接收传输的图片
        file = request.files['file']
    # zxy add for GET
    else:
        image_file = request.args.get("path") #接收其他客户端浏览器发送的请求
        file = open(image_file, 'rb')
    img_bytes = file.read()
    class_id, class_name = get_prediction(image_bytes=img_bytes)
    return jsonify({'class_id': class_id, 'class_name': class_name})


if __name__ == '__main__':
    # app.run() # 原工程的写法，默认只能本机访问
    app.run(host='0.0.0.0', port=5005)  # 使其他主机可以访问服务
