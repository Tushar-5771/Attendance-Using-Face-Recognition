from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout
from imutils import paths
import face_recognition
import pickle
import cv2
import os
import tkinter as tk
import numpy as np
import requests
import json
from .models import Faculty

# Create your views here.


def Index(request):
    if request.user.is_anonymous:
        return render(request, 'login.html')
    return render(request, 'CapImg.html',{'cap': 1})


def Userlogin(request):

    if request.method == 'POST':
        inUser = request.POST.get('userName').strip()
        inPass = request.POST.get('userPassword').strip()

        user = authenticate(username=inUser, password=inPass)

        if user is not None:

            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'flag': 1})

    return render(request, 'login.html', {'flag': 1})




def CaptureImg(request):
    if request.user.is_anonymous:
        return render(request, 'login.html')
    if request.method == 'POST':
        #camera Initialization
        cam = cv2.VideoCapture(0)

        #Er Input
        path = str(request.POST['CapErno'].strip())

        #Class Input
        className = str(request.POST['CapClass'].strip())
        classPath = os.getcwd()+"/"+className

        #To Create Class
        if (os.path.isdir(classPath)):
            pass
        else:
            os.mkdir(classPath)
        pathName = classPath + "/" + path

        #To Create Student Folder
        if(os.path.isdir(pathName)):
            pass
        else:
            os.mkdir(pathName)
        count = 0

        #To capture Images
        while True:

            #To read image
            ret, img = cam.read()
            cv2.imshow("Test", img)
            if not ret:
                break
            k = cv2.waitKey(1)
            if k % 256 == 27:
                # For Q key
                print("Close")
                break
            elif k % 256 == 32:
                # For Space key
                print("Image saved")
                count += 1
                file = pathName+"/"+str(count)+'.jpg'
                cv2.imwrite(file, img)
        cam.release()
        cv2.destroyAllWindows()

        return render(request, 'CapImg.html',{'cap': 1})
    return render(request, 'CapImg.html',{'cap': 1})




def EncodeImg(request):
    if request.user.is_anonymous:
        return render(request, 'login.html')
    if request.method == 'POST':
        # get paths of each file in folder named Images
        # Images here contains my data(folders of various persons)
        Class_Name = str(request.POST['EncClass'].strip())
        if (os.path.isdir(Class_Name)):
            imagePaths = list(paths.list_images(Class_Name))
            knownEncodings = []
            knownNames = []
            # loop over the image paths
            for (i, imagePath) in enumerate(imagePaths):
                # extract the person name from the image path
                print(imagePath)
                name = imagePath.split(os.path.sep)[-2]
                # load the input image and convert it from BGR (OpenCV ordering)
                # to dlib ordering (RGB)
                image = cv2.imread(imagePath)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                # Use Face_recognition to locate faces
                boxes = face_recognition.face_locations(rgb, model='hog')
                # compute the facial embedding for the face
                encodings = face_recognition.face_encodings(rgb, boxes)
                # loop over the encodings
                for encoding in encodings:
                    knownEncodings.append(encoding)
                    knownNames.append(name)
            # save emcodings along with their names in dictionary data
            data = {"encodings": knownEncodings, "names": knownNames}
            Path_Name = str(os.getcwd()+"/Encode/" + Class_Name+"_Encode")
            # use pickle to save data into a file for later use
            f = open(Path_Name, "wb")
            f.write(pickle.dumps(data))
            f.close()
        else:
            return render(request, 'EncImg.html', {'Enc_Flag': 1,'enc': 1})
    return render(request, 'EncImg.html',{'enc': 1})



def RecImg(request):
    if request.user.is_anonymous:
        return render(request, 'login.html')
    
    if request.method == 'POST':
        Class_Name = str(request.POST['RecClass'].strip())
        Path_Name = str(os.getcwd()+"/Encode/" + Class_Name+"_Encode")
        
        if (os.path.isfile(Path_Name)):
            # load the known faces and embeddings saved in last file
            data = pickle.loads(open(Path_Name, "rb").read())
            print("Streaming started")
            video_capture = cv2.VideoCapture(0)
            # Marking attendence in csv file

            def markAttendence(name):
                with open('Attendence.csv', 'r+') as f:
                    myDataList = f.readlines()
                    nameList = []
                    for line in myDataList:
                        entry = line.split(',')
                        nameList.append(str(entry[0]))
                    if name not in nameList:
                        f.write(f'\n{name},')

            while True:
                success, img = video_capture.read()
                
                # convert image BGR to RGB
                imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # Face location for detection of face
                facesCurFrame = face_recognition.face_locations(imgS)
                # Face encoding
                encodeCurFrame = face_recognition.face_encodings(
                    imgS, facesCurFrame)
                for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
                    # compare faces
                    matches = face_recognition.compare_faces(
                        data["encodings"], encodeFace)
                    faceDis = face_recognition.face_distance(
                        data["encodings"], encodeFace)
                    
                    matchIndex = np.argmin(faceDis)
                    
                    dis = float(min(faceDis))
                    
                    if matches[matchIndex] and dis < 0.45:
                        name = data["names"][matchIndex].upper()
                        y1, x2, y2, x1 = faceLoc
                        
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.rectangle(img, (x1, y2 - 35), (x2, y2),
                                    (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, name, (x1 + 6, y2 - 6),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                        markAttendence(name)

                    cv2.imshow('Webcam', img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            video_capture.release()
            cv2.destroyAllWindows()
        else:
            return render(request, 'Rec.html', {'Rec_Flag': 1,'RecPage': 1})
    return render(request,'Rec.html',{'RecPage': 1})


def SMS(request):
    if request.user.is_anonymous:
        return render(request, 'login.html')

    ListOfNumbers = Faculty.objects.all()

    
    if request.method == 'POST':
        Mobile = str(request.POST['SMSClass'].strip()).split("-")
        
        Er_numbers = ""
        with open('Attendence.csv', 'r') as f:
            myDataList = f.readlines()
            for line in myDataList:
                Er_numbers += ","+str(line.split(',')[0])

        url = "https://www.fast2sms.com/dev/bulk"
        querystring = {"authorization": "Ya7GckPp2E8Ib13vL5ztmyXdOrWQTNqeoAM0uFg6xZK4DiCJhwTmzl5XOFHPDw4fkN1EujryV2Lg8tUW",
                    "sender_id": "Attendence", "message": Er_numbers, "language": "english", "route": "p", "numbers": Mobile}
        headers = {
            'cache-control': "no-cache"
        }
        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        print(response.text)
        return render(request,'SMS.html',{'sms': 1,'List':ListOfNumbers,'smsFlag':1})     

    return render(request,'SMS.html',{'sms': 1,'List': ListOfNumbers})


def ViewStu(request):
    return render(request,'ViewStu.html',{'view': 1})

def getData(request):
    if request.user.is_anonymous:
        return render(request, 'login.html')
    Class_Name = str(request.POST['C_Name'].strip())
    Path_Name = str(os.getcwd()+"/Encode/" + Class_Name+"_Encode")
    ListOfStu = []
    Data_List = {}
    if (os.path.isfile(Path_Name)):
        data = pickle.loads(open(Path_Name, "rb").read())
        dataSet = list(set(data["names"]))

        for i in dataSet:
            ListOfStu.append(i)

        Data_List['Status'] = 'ok'
        Data_List['Data'] = sorted(ListOfStu)

        return HttpResponse(json.dumps(Data_List))

    else:
        Data_List['Status'] = 'notFound'
        Data_List['Data'] = []

        return HttpResponse(json.dumps(Data_List))


def FacultyPage(request):
    if request.method == 'POST':
        fName = str(request.POST['FacClass'].strip())
        fPhone = request.POST['FacNoClass'].strip()
        facData = Faculty(facultyName=fName,mobileNo=fPhone)
        try:
            facData.save()
            return render(request,'Faculty.html',{'save_Flage' : 1,'fac': 1})
        except:
            return render(request,'Faculty.html',{'unsave':1,'fac': 1})
    return render(request,'Faculty.html',{'fac': 1})


def Userlogout(request):
    auth.logout(request)
    return redirect('/')
