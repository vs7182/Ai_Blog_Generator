from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
import json
from pytube import YouTube
import os 
import assemblyai as aai
import openai
from .models import BlogPost


# Create your views here.
@login_required
def index(request):
    return render(request,'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            return JsonResponse({'Content': yt_link})
        except(KeyError,json.JSONDecodeError):
            return JsonResponse({'error' : 'Invalid data sent '},status= 400)
        
        # get yt title
        title = yt_tittle(yt_link)
        #get transcript
        transcription =get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error':"Failed to get transcript"},status= 500)
        



        # use OpenAi to generate the  blog

        blog_content =  generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error':"Failed to get generate"},status= 500)

        # save blog article to database

        new_blog_article  =  BlogPost.ojects.create(
            user= request.user ,
            youtube_title = title,
            youtube_link = yt_link,
            generated_content = blog_content,
        )
        new_blog_article.save()
        # return blog article as a responce
        return JsonResponse({'content': blog_content})

    else:
        return JsonResponse({'error' : 'Invalid request method'},status= 405)

def yt_tittle(link):
    yt = YouTube(link)
    title  = yt.title
    return title


def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_File = video.download(output_path= settings.MEDIA_ROOT)
    base,ext = os.path.splitext(out_File)
    new_File = base + '.mp3'
    os.rename(out_File,new_File)
    return new_File



    

def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = "You aai, key"

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript.text

def generate_blog_from_transcription(transcription):
    openai.api_key = "Your key to add this "

    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    response = openai.completions.create(
        model= "text-daninci-003",
        prompt= prompt,
        max_tokens=1000
    )

    gererated_content  = response.choices[0].text.strip()
    return gererated_content



def blog_list(request):
    blog_article = BlogPost.objects.filter(user=request.user)
    return render(request,'all-blog.html',{'blog_article': blog_article})

def blog_details(request,pk):
    blog_article_details = BlogPost.objects.get(id = pk)
    if request.user == blog_article_details.user:
        return render(request,'blog-details.html',{' blog_article_details' :  blog_article_details})
    
    else:
        return redirect('/')

    
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request,username = username , password=password)
        if user is not  None:
            login(request,user)
            return redirect('/')
        else:
            error_message = 'Ivalid Username or password'
            return render(request,'login.html',{'error_message' : error_message})        
    return render(request,'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['Email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']   

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username,email,password)
                user.save()
                login(request,user)
                return redirect('/')

            except:
                error_message = 'Error Creating account' 


        else:
            error_message = 'Password do not match '
            return render ( request,'signup.html' ,{'error_message': error_message})
            return render (request,'signup.html')



    return render (request,'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')
