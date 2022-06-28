# Nutrimeter


---
## Design Prototype
1. Sign-up page 1  

![Sign Up 1](Prototype/sign%20up1.png)

2. Sign-up page 2  

![Sign Up 2](Prototype/sign%20up2.png)

3. Sign-up page 3  

![Sign Up 3](Prototype/sign%20up%203.png)

4. Home page  

![Home Page](Prototype/Home%20Screen.png)

5. Profile and settings  

![Profile Page](Prototype/Settings.png)


6. Recipes page  

![Recipes](Prototype/Recipes.png)

7. Camera page  

![Camera](Prototype/output%20after%20scanning.png)

---
## Mask R-CNN service
* build docker image from the `Dockerfile` located `Docker/ai/prod` or `Docker/ai/dev` __prod__ for production and __dev__ for devlopment and testing.  
#### Note:
When running the development image make sure to use bind mounting.

When deploying make sure the image has a copy of the source code.

In both cases you need to expose a port, 5000 being the default flask API port

---
### Testing Mask R-CNN
Once the container is up and running on port 5000 for example

1. open any http client like `Postman` or `CURL` or anyother http client
2. In the body section of the request select `form-data`
3. Give the key as image of type file and select the image in your local system
4. Make a HTTP POST request to the following endpoint `http://127.0.0.1:5000/pred-img`
![Postman HTTP request](assets/postman-mask-rcnn-http-req.png)
5. Mask R-CNN will generate an image in the mounted volume
