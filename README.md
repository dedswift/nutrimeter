# Mask R-CNN microservice

**If you want to test in the container use bind mount**

**if you want to deploy remove bind mount and copy the model inside the container**

---

1. open any http client like `Postman` or `CURL` or anyother http client
2. Run the container exposing port **5000**
3. In the body section of the request select `form-data`
4. Give the key as image of type file and select the image in your local system
5. Make a HTTP POST request to the following endpoint `http://127.0.0.1:5000/pred-img`
6. Mask R-CNN will generate an image in the mounted volume
