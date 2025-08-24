from django.shortcuts import render, HttpResponse
from .forms import UserRegistrationForm
from .models import UserRegistrationModel,UserImagePredictinModel,UserLiveImagePredictinModel
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .utility.GetImageStressDetection import ImageExpressionDetect
from .utility.MyClassifier import KNNclassifier
from subprocess import Popen, PIPE
import subprocess
from django.conf import settings
from PyEmotion import *
import cv2 as cv
# Create your views here.

def getLiveDetects(username, loginid, email):
    print("Streaming Started")
    filepath = settings.MEDIA_ROOT + "\\frames\\"

    if not os.path.exists(filepath):
        os.makedirs(filepath)

    PyEmotion()
    er = DetectFace(device='cpu', gpu_id=0)
    # Open your default camera 
    cap = cv.VideoCapture(0)
    while (True):
        ret, frame = cap.read()
        if not ret:
            break
        frame, emotion = er.predict_emotion(frame)
        # print("emotion::",emotion)
        # print("ytpe::",type(emotion))

        if emotion != "NoFace":
            # Let the model generate the unique filename using default
            file_path = os.path.join(filepath, f"temp_{int(cv.getTickCount())}.jpg")  # Temporary filename for saving
            cv.imwrite(file_path, frame)
            fs = FileSystemStorage()
            with open(file_path, 'rb') as f:
                uploaded_file = fs.save(f.name.split('\\')[-1], f)
            uploaded_file_url = fs.url(uploaded_file)
            print("path::", uploaded_file_url)

            # Create the model instance without setting filename manually
            UserLiveImagePredictinModel.objects.create(
                username=username,
                email=email,
                loginid=loginid,
                emotions=emotion,
                file=uploaded_file_url  # The URL to the saved image
            )

            # Clean up the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

        cv.imshow('Press Q to Exit', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv.destroyAllWindows()

# Create your views here.
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHome.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    return render(request, 'users/UserHome.html', {})

def UploadImageForm(request):
    loginid = request.session['loginid']
    data = UserImagePredictinModel.objects.filter(loginid=loginid)
    return render(request, 'users/UserImageUploadForm.html', {'data': data})

def UploadImageAction(request):
    image_file = request.FILES['file']

    # let's check if it is a csv file
    if not image_file.name.endswith('.jpg'):
        messages.error(request, 'THIS IS NOT A JPG  FILE')

    fs = FileSystemStorage()
    filename = fs.save(image_file.name, image_file)
    # detect_filename = fs.save(image_file.name, image_file)
    uploaded_file_url = fs.url(filename)
    obj = ImageExpressionDetect()
    emotion = obj.getExpression(filename)
    username = request.session['loggeduser']
    loginid = request.session['loginid']
    email = request.session['email']
    UserImagePredictinModel.objects.create(username=username,email=email,loginid=loginid,filename=filename,emotions=emotion,file=uploaded_file_url)
    data = UserImagePredictinModel.objects.filter(loginid=loginid)
    return render(request, 'users/UserImageUploadForm.html', {'data':data})

def UserLiveResults(request):
    username = request.session['loggeduser']
    loginid = request.session['loginid']
    email = request.session['email']
    data = UserLiveImagePredictinModel.objects.filter(loginid=loginid)
    return render(request, 'users/UserLiveImage.html', {'data':data})

def UserEmotionsDetect(request):
    if request.method=='GET':
        imgname = request.GET.get('imgname')
        obj = ImageExpressionDetect()
        emotion = obj.getExpression(imgname)
        loginid = request.session['loginid']
        data = UserImagePredictinModel.objects.filter(loginid=loginid)
        return render(request, 'users/UserImageUploadForm.html', {'data': data})

def UserLiveCameDetect(request):
    obj = ImageExpressionDetect()

    username = request.session['loggeduser']
    loginid = request.session['loginid']
    email = request.session['email']

    # obj.getLiveDetect()
    getLiveDetects(username,loginid,email)
    return render(request, 'users/UserLiveHome.html', {})

def UserKerasModel(request):
    # p = Popen(["python", "kerasmodel.py --mode display"], cwd='StressDetection', stdout=PIPE, stderr=PIPE)
    # out, err = p.communicate()
    subprocess.call("python kerasmodel.py --mode display")
    return render(request, 'users/UserLiveHome.html', {})

def UserCNNResults(request):
    obj = KNNclassifier()
    df,accuracy,classificationerror,sensitivity,Specificity,fsp,precision = obj.getKnnResults()
    df.rename(columns={'Target': 'Target', 'ECG(mV)': 'Time pressure', 'EMG(mV)': 'Interruption', 'Foot GSR(mV)': 'Stress', 'Hand GSR(mV)': 'Physical Demand', 'HR(bpm)': 'Performance', 'RESP(mV)': 'Frustration', }, inplace=True)
    data = df.to_html()
    return render(request,'users/UserCNNResults.html',{'data':data,'accuracy':accuracy,'classificationerror':classificationerror,
                                                       'sensitivity':sensitivity,"Specificity":Specificity,'fsp':fsp,'precision':precision})
