# -*- coding: utf-8 -*-
__author__ = "Prem Raheja"
__copyright__ = "Copyright (©) 2019. University of Alberta  All rights reserved."

#python dependencies
import logging
import time
import traceback
import requests
import urllib
from urllib.parse import unquote
import json
import base64
import configparser
import uuid
import subprocess
import re
from os import path
import os
from videoprops import get_video_properties
from os import listdir
from os.path import isfile, join
import glob
import socket    


# Django related dependencies
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from rest_framework import viewsets
from rest_framework import status
from rest_framework.parsers import FileUploadParser

# Django rest framework related dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Project related Dependencies
from .models import VideoDetails,VideoEncoding,VideoUploadRequest,VideoUserTable,UserManagement,VideoEncodingFormat,VideoEncodingDetails
from .serializers import VideoDetailsSerializer,VideoEncodingSerializer,VideoUploadRequestSerializer,FileSerializer

# Google Cloud Dependencies
from google.cloud import storage



class VideoFeatureReading(APIView):
    def post(self,request,format=None):
        """
            @param:
                request = Input Request for extracting video details
            @returns:
                The request accepted message and video details extracted and stored in the database

        """
        print("Entered Here1234")
        destination_bucket='video-streaming-project-bucket'
        try:
            data = {
                "status_code": 200,
                "message": "Request is accepted",
                "video_id":""
                
            }   
            video_download_directory='/tmp'
            try:
                if path.exists(video_download_directory):
                    pass
            except Exception as e: 
                os.mkdir(video_download_directory)
            print(request.data)
            video_request_serializer=VideoUploadRequestSerializer(data=request.data)
            
            if(video_request_serializer.is_valid()):
                print("Entered Here too")
                is_bucket_path=request.data['is_bucket_path']
                if(is_bucket_path):
                    bucket_path=request.data['path']
                    storage_client = storage.Client()
                    bucket_name=bucket_path.split("/")[2]
                    prefix="/".join(bucket_path.split("/")[3:])
                    filename=bucket_path.split("/")[-1]
                    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
                    list_of_files=[]
                    for blob in blobs:
                        if str(blob.name).endswith("/"):
                            pass
                        else:
                            list_of_files.append(str(blob.name))
                    print(list_of_files)
                    for i in range(len(list_of_files)):
                        video_id=uuid.uuid4()
                        video_id_str=str(video_id).replace("-","")
                        video_name=".".join(list_of_files[i].split("/")[-1]).split(".")[:-1]
                        video_description=list_of_files[i].split("/")[1]
                        
                        if(path.exists(os.path.join(video_download_directory,str(video_id_str),'video'))):
                            pass
                        else:
                            print("Entered Here too")
                            os.mkdir(os.path.join(video_download_directory,str(video_id_str)))
                            os.mkdir(os.path.join(video_download_directory,str(video_id_str),'video'))
                        try:
                            cmd=(' '.join(['gsutil','-m','cp','gs://'+bucket_name+'/'+list_of_files[i],"\""+os.path.join(video_download_directory,str(video_id_str),'video')+"\""]))
                            p=subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
                            p.wait()
                            out,err=p.communicate()
                        except Exception as e:
                            print("Entered Here1111")
                            print(e)
                        mp4_conversion_cmd='ffmpeg -i '+'"'+os.path.join(video_download_directory,str(video_id_str),'video',filename)+'"'+ " "+'"'+os.path.join(video_download_directory,str(video_id_str),'video',filename.split(".")[0]+".mp4") +'"'
                        print(mp4_conversion_cmd)
                        filename=filename.split(".")[0]+".mp4"
                        p=subprocess.Popen(mp4_conversion_cmd,stdout=subprocess.PIPE,shell=True)
                        p.wait()
                        out,err=p.communicate()
                        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries","format=duration", "-of","default=noprint_wrappers=1:nokey=1", os.path.join(video_download_directory,str(video_id_str),'video',filename)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                        if(result.stdout!='N/A\n'):
                            video_duration=float(result.stdout)   
                        else:
                            video_duration=0 
                        props = get_video_properties( os.path.join(video_download_directory,str(video_id_str),'video',filename)) 
                        video_resolution=str(props['width'])+"X"+str(props['height'])
                        video_encoding=str(props['codec_name'])
                        video_size=os.path.getsize( os.path.join(video_download_directory,str(video_id_str),'video',filename))
                        thumbnail_command='ffmpeg -i ' +'"'+os.path.join(video_download_directory,str(video_id_str),"video",filename)+'"'+' -ss 00:00:01.000 -vframes 1 '+'"'+ os.path.join(video_download_directory,str(video_id_str),'thumbnail.png')+'"'
                        video_thumbnail=subprocess.Popen(thumbnail_command,shell=True,stdout=subprocess.PIPE)
                        out,err=video_thumbnail.communicate()
                        video_clip_command='ffmpeg -ss 00:00:05 -i '+'"'+os.path.join(video_download_directory,str(video_id_str),"video",filename)+'"'+' -t 00:00:05 -vcodec copy -acodec copy '+'"'+ os.path.join(video_download_directory,str(video_id_str),'clip.mp4')+'"'
                        video_clip=subprocess.Popen(video_clip_command,shell=True,stdout=subprocess.PIPE)
                        out,err=video_clip.communicate()
                        bucket = storage_client.bucket(destination_bucket)
                        destination_blob_name=video_id_str+'/video/'+filename
                        blob = bucket.blob(destination_blob_name)
                        blob.upload_from_filename(os.path.join(video_download_directory,str(video_id_str),'video',filename))
                        destination_blob_name_thumbnail='thumbnail/'+video_id_str+".png"
                        blob = bucket.blob(destination_blob_name_thumbnail)
                        blob.upload_from_filename(os.path.join(video_download_directory,str(video_id_str),'thumbnail.png'))
                        blob.make_public()
                        destination_blob_name_clip='clip/'+video_id_str+".mp4"
                        blob1 = bucket.blob(destination_blob_name_clip)
                        blob1.upload_from_filename(os.path.join(video_download_directory,str(video_id_str),'clip.mp4'))
                        blob1.make_public()

                        cmd='rmdir /s/q '+ '"'+os.path.join(video_download_directory,video_id_str)+'"'
                        delete_folder=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
                        out,err=delete_folder.communicate()
                        VideoDetails.objects.create(video_id=video_id,video_name=filename,video_description=video_description,thumbnail_url=blob.public_url,video_duration=video_duration,video_encoding=video_encoding,video_path="gs://"+destination_bucket+"/"+destination_blob_name,video_size=video_size,video_category=video_description,video_resolution=video_resolution,clip_url=blob1.public_url)
            else:
                data['status_code']=400
                data['message']='Bad Request'
            return Response(data,status=status.HTTP_200_OK,headers=None)
        except Exception as e:
            print(e)
            data['message']=str(e)
            return Response(data,status=status.HTTP_200_OK,headers=None)


class VideoDetailExtraction(APIView):
    def get(self,request,format=None):
        try:
            data = {
                "status_code": 200,
                "message": "All the videos are listed as below",
                "result":{},
                "trending":[]
                
            } 
            # permission_cmd="sudo chmod -R 777 /tmp/"
            # cmd_output = subprocess.Popen(permission_cmd, shell=True, stdout=subprocess.PIPE)
            # cmd_output.wait()
            # out,err=cmd_output.communicate(input=None, timeout=None)
            # permission_cmd="sudo chmod -R 777 /var/"
            # cmd_output = subprocess.Popen(permission_cmd, shell=True, stdout=subprocess.PIPE)
            # cmd_output.wait()
            # out,err=cmd_output.communicate(input=None, timeout=None)
            result=VideoDetails.objects.filter()
            trending=list(VideoDetails.objects.filter().order_by("-video_count").values()[:1])
            storage_client = storage.Client()
            bucket = storage_client.bucket("kubernetes-deployment-prem")
            blob = bucket.blob("private-key.json")
            blob.download_to_filename("/tmp/private-key.json")
            for i in range(len(trending)):
                video_url=trending[i].get('video_path')
                cmd = "gsutil signurl -d 60m \"{0}\" \"{1}\"".format("/tmp/private-key.json", video_url)
                print(cmd)
                cmd_output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                url = cmd_output.communicate()[0].decode("utf-8").split("\t")[-1]
                print(url)
                trending[i]['video_url']=str(url)[:-2]
            print(trending)
            data['trending']=trending
            
            
            result_list={}
            for i in range(len(result)):
                temp={}
                temp['video_id']=result[i].video_id
                temp['video_name']=result[i].video_name
                temp['video_description']=result[i].video_description
                temp['thumbnail_url']=result[i].thumbnail_url
                temp['video_duration']=result[i].video_duration
                temp['video_size']=result[i].video_size
                temp['date_created']=result[i].date_created
                temp['video_path']=result[i].video_path
                # encoding_result=list(VideoEncodingDetails.objects.filter(video_id=result[i].id,encoding_id__lte=15).order_by('-encoding_id').values('encoding_id'))[0]
                # resolution_list=['360X480','360X640','480X360','640X360','640X480','720X360','720X480','720X640','800X600','1024X768','1280X720','1280X800','1280X1024','1920X1080']
                # temp['resolutions']=resolution_list[:int(encoding_result.get('encoding_id'))]
                # temp['encoding_id']=[]
                # for i in range(0,int(encoding_result.get('encoding_id'))):
                #     temp['encoding_id'].append(i)
                #     temp['encoding_id'].append(i+15)
                #     temp['encoding_id'].append(i+30)
                
                if result[i].video_category in result_list:
                    result_list[result[i].video_category].append(temp)
                else:
                    temp1=[]
                    temp1.append(temp)
                    result_list[result[i].video_category]=temp1
            data['result']=result_list
            return Response(data,status=status.HTTP_200_OK,headers=None)
        except Exception as e:
            print(e)  
            data["message"]=str(e)
            return Response(data,status=status.HTTP_200_OK,headers=None)
class VideoPlayLink(APIView):
    def get(self,request,format=None):
        try:
            data = {
                "status_code": 200,
                "message":"Result fetched successfully",
                "result":{}
                
                
            } 
            # permission_cmd="sudo chmod -R 777 /tmp/"
            # cmd_output = subprocess.Popen(permission_cmd, shell=True, stdout=subprocess.PIPE)
            # cmd_output.wait()
            # out,err=cmd_output.communicate(input=None, timeout=None)
            # permission_cmd="sudo chmod -R 777 /var/"
            # cmd_output = subprocess.Popen(permission_cmd, shell=True, stdout=subprocess.PIPE)
            # cmd_output.wait()
            # out,err=cmd_output.communicate(input=None, timeout=None)
            video_uuid=unquote(request.GET.get('video_id'))
            encoding_id=request.GET.get('encoding_id')
            encoding_type=request.GET.get('encoding_type')
            result=VideoDetails.objects.filter(video_id=video_uuid).values()
            result_obj=VideoDetails.objects.get(video_id=video_uuid)
            video_search_id=result[0].get("id")
            video_url=result[0].get("video_path")
            
            if(encoding_type=='mp4'):                
                encoding_result=VideoEncodingDetails.objects.filter(video_id=int(video_search_id),encoding_id=int(encoding_id))
               
            elif(encoding_type=='webm'):
                encoding_result=VideoEncodingDetails.objects.filter(video_id=int(video_search_id),encoding_id=int(encoding_id)+15)
               
            else:

                encoding_result=VideoEncodingDetails.objects.filter(video_id=int(video_search_id),encoding_id=int(encoding_id)+30)
            if not encoding_result:
                print("Entered Gereee")
                if(encoding_type=='mp4'):
                    encoding_result=list(VideoEncodingDetails.objects.filter(video_id=int(video_search_id),encoding_id__lte=15).order_by('-encoding_id').values('video_path'))[0]
                    video_url=encoding_result.get("video_path")
                elif(encoding_type=='webm'):
                    encoding_result=list(VideoEncodingDetails.objects.filter(video_id=int(video_search_id),encoding_id__lte=30).order_by('-encoding_id').values('video_path'))[0]
                    video_url=encoding_result.get("video_path")
                else:
                    encoding_result=list(VideoEncodingDetails.objects.filter(video_id=int(video_search_id),encoding_id__lte=45).order_by('-encoding_id').values('video_path'))[0]
                    video_url=encoding_result.get("video_path")
            else:
                for encoding_result_itt in encoding_result:
                    video_url=encoding_result_itt.video_path
           
            
           
            
            result_obj.video_count=int(result[0].get("video_count"))+1
            result_obj.save()
            
            video_name=result[0].get("video_name")
            video_duration=result[0].get("video_duration")
            storage_client = storage.Client()
            bucket = storage_client.bucket("kubernetes-deployment-prem")
            blob = bucket.blob("private-key.json")
            blob.download_to_filename("/tmp/private-key.json")
            cmd = "gsutil signurl -d 60m \"{0}\" \"{1}\"".format("/tmp/private-key.json", video_url)
            print(cmd)
            cmd_output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            url = cmd_output.communicate()[0].decode("utf-8").split("\t")[-1]
            print(url)
            data['result']['video_url']=str(url)[:-2]
            data['result']['video_name']=video_name
            data['result']['video_duration']=video_duration
            return Response(data,status=status.HTTP_200_OK,headers=None)
        except Exception as e:
            print(e)
            data['message']=str(e)
            return Response(data,status=status.HTTP_200_OK,headers=None)


class VideoUserController(APIView):
    def get(self,request,format=None):
        try:
            data = {
                "status_code": 200,
                "message":"Result Fetched",
                "result":{}
                
            } 
            video_id=request.GET.get("video_id")
            user_id=request.GET.get("user_id")
            user_result=UserManagement.objects.get(id=user_id)
            video_result=VideoDetails.objects.get(video_id=video_id)
            result=list(VideoUserTable.objects.filter(video_id=video_result,user_id=user_result).values())

            data['result']=result[0]
            return Response(data,status=status.HTTP_200_OK,headers=None)
        except Exception as e:
            print(e)
            data['message']=str(e)
            return Response(data,status=status.HTTP_200_OK,headers=None)
    def post(self,request,format=None):
        try:
            data = {
                "status_code": 200,
                "message":"Result Fetched",
                "result":{}
                
            } 
            request_data=request.data
            user_id=request_data['user_id']
            user_result=UserManagement.objects.get(id=user_id)
            video_id=request_data['video_id']
            video_result=VideoDetails.objects.get(video_id=video_id)
            duration=request_data['duration']
            result=VideoUserTable.objects.filter(user_id=user_result,video_id=video_result)
            if(len(list(result))>0):
                result1=VideoUserTable.objects.get(user_id=user_result,video_id=video_result)
                result1.duration=duration
                result1.save()
            else:
                VideoUserTable.objects.create(user_id=user_result,video_id=video_result,duration=duration)
            return Response(data,status=status.HTTP_200_OK,headers=None)
        except Exception as e:
            print(e)
            data['message']=str(e)
            return Response(data,status=status.HTTP_200_OK,headers=None)




# Create your views here.
class LoginManagementController(APIView):
    def get(self,request,format=None):
        try:
            data = {
                    "status_code": 200,
                    "message": "User Created",                    
                } 
            print("Get Request")
            username=request.GET.get("username")
            password=(request.GET.get("password"))
            message_bytes = password.encode('ascii')
            base64_bytes = base64.b64encode(message_bytes)
            password = base64_bytes.decode('ascii')
            result=UserManagement.objects.filter(username=username,password=password).values()
            result_list=[]
            for i in range(len(result)):
                base64_bytes = result[i]['password'].encode('ascii')
                message_bytes = base64.b64decode(base64_bytes)
                result[i]['password'] = message_bytes.decode('ascii')
                result_list.append(result[i])
            data['message']=result
            return Response(data, status=status.HTTP_200_OK, headers=None)
        except Exception as e:
            print(e)
            data['status_code']=400
            data['message']=str(e)
            return Response(data, status=status.HTTP_200_OK, headers=None)
        
    def post(self,request,format=None):
        try:
            data = {
                "status_code": 200,
                "message": "User Created",
                "result":{}
                
            } 
            print("Entered Here")
            firstName=request.data['firstname']
            lastName=request.data['lastname']
            username=request.data['username']
            password=(request.data['password'])
            
            message_bytes = password.encode('ascii')
            base64_bytes = base64.b64encode(message_bytes)
            password = base64_bytes.decode('ascii')
            email=request.data['email']
            isSubscribed=request.data['isSubscribed']
            try:
                UserManagement.objects.create(firstName=firstName,lastName=lastName,username=username,password=password,email=email,isSubscribed=isSubscribed)
                print("Object created")
            except Exception as e:
                print(e)
            data['result']=list(UserManagement.objects.filter(firstName=firstName,lastName=lastName,username=username,password=password,email=email,isSubscribed=isSubscribed).values())[0]
            return Response(data, status=status.HTTP_200_OK, headers=None)
        except Exception as e:
            print(e)
            data['status_code']=400
            data['message']=str(e)
            return Response(data, status=status.HTTP_200_OK, headers=None)

class VideoEncodingConversionController(APIView):
    def post(self,request,format=None):
        try:
            data = {
                "status_code": 200,
                "message": "Requested Accepted"
                
            } 
            video_id=request.data['video_id']
            video_download_directory='/tmp'
            os.mkdir(os.path.join(video_download_directory,video_id))
            object_download_path=os.path.join(video_download_directory,video_id,"original_video.mp4")
            storage_client = storage.Client()
            video_path=list(VideoDetails.objects.filter(video_id=video_id).values('video_path'))[0]['video_path']
            print(video_path)
            bucket_name=video_path.split("/")[2]
            object_path="/".join(video_path.split("/")[3:])
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(object_path)
            blob.download_to_filename(object_download_path)
            video_resolution_list=list(VideoEncodingFormat.objects.filter().values('resolution'))[0:15]
            width_list=[]
            height_list=[]
            for i in range(len(video_resolution_list)):
                width,height=video_resolution_list[i]['resolution'].split("X")
                width_list.append(int(width))
                height_list.append(int(height))
            
            min_w=3360
            min_h=2100
            index=0
            props = get_video_properties( os.path.join(video_download_directory,str(video_id),'original_video.mp4')) 
            print(str(props['width'])+"X"+str(props['height']))
            for i in range(len(width_list)):
                if((int(props['width'])-width_list[i])>=0 and (int(props['width'])-width_list[i])<=min_w and (int(props['height'])-height_list[i])>=0 and (int(props['height'])-height_list[i])<=min_h):
                    min_h=(props['height']-height_list[i])
                    min_w=(props['width']-width_list[i])
                    index=i
            os.mkdir(os.path.join(video_download_directory,video_id,'encoding'))
            for i in range(0,index+1):
                cmd='ffmpeg -i '+'"'+os.path.join(video_download_directory,str(video_id),'original_video.mp4')+'"'+' -s '+str(width_list[i])+'x'+str(height_list[i])+ ' -c:a copy '+ '"'+os.path.join(video_download_directory,video_id,'encoding',str(i+1)+'.mp4')+'"'
                cmd_output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                cmd_output.wait()
                out,err=cmd_output.communicate(input=None, timeout=None)
                webm_cmd='ffmpeg -i '+ '"'+os.path.join(video_download_directory,str(video_id),'original_video.mp4')+'"'+' -s '+str(width_list[i])+'x'+str(height_list[i])+  ' -c:v libvpx-vp9 -crf 30 -b:v 0 ' +'"'+os.path.join(video_download_directory,video_id,'encoding',str(i+1)+'.webm')+'"'
                webm_cmd_output = subprocess.Popen(webm_cmd, shell=True, stdout=subprocess.PIPE)
                out,err=webm_cmd_output.communicate(input=None, timeout=None)
                ogg_cmd='ffmpeg -i '+'"'+os.path.join(video_download_directory,video_id,'encoding',str(i+1)+'.mp4')+'"'+' -c:v libtheora -q:v 7 -c:a libvorbis -q:a 4 ' +'"'+os.path.join(video_download_directory,video_id,'encoding',str(i+1)+'.ogv')+'"'
                ogg_cmd_output = subprocess.Popen(ogg_cmd, shell=True, stdout=subprocess.PIPE)
                out,err=ogg_cmd_output.communicate(input=None, timeout=None)
                bucket = storage_client.bucket(bucket_name)
                mp4_destination_blob_name=str(video_id).replace("-","")+"/encoding/"+str(i+1)+'.mp4'
                mp4_blob = bucket.blob(mp4_destination_blob_name)
                mp4_blob.upload_from_filename(os.path.join(video_download_directory,video_id,'encoding',str(i+1)+'.mp4'))
                web_destination_blob_name=str(video_id).replace("-","")+"/encoding/"+str(i+1)+'.webm'
                web_blob=bucket.blob(web_destination_blob_name)
                web_blob.upload_from_filename(os.path.join(video_download_directory,video_id,'encoding',str(i+1)+'.webm'))
                ogg_destination_blob_name=str(video_id).replace("-","")+"/encoding/"+str(i+1)+'.ogv'
                ogg_blob=bucket.blob(ogg_destination_blob_name)
                ogg_blob.upload_from_filename(os.path.join(video_download_directory,video_id,'encoding',str(i+1)+'.ogv'))
                video_id_object=VideoDetails.objects.get(video_id=video_id)
                mp4_encoding_id_object=VideoEncodingFormat.objects.get(id=i+1)
                web_encoding_id_object=VideoEncodingFormat.objects.get(id=i+16)
                ogv_encoding_id_object=VideoEncodingFormat.objects.get(id=i+31)
                VideoEncodingDetails.objects.create(video_id=video_id_object,encoding_id=mp4_encoding_id_object,video_path='gs://'+bucket_name+"/"+str(video_id).replace("-","")+"/encoding/"+str(i+1)+'.mp4')
                VideoEncodingDetails.objects.create(video_id=video_id_object,encoding_id=web_encoding_id_object,video_path='gs://'+bucket_name+"/"+str(video_id).replace("-","")+"/encoding/"+str(i+1)+'.webm')
                VideoEncodingDetails.objects.create(video_id=video_id_object,encoding_id=ogv_encoding_id_object,video_path='gs://'+bucket_name+"/"+str(video_id).replace("-","")+"/encoding/"+str(i+1)+'.ogv')

            cmd='rmdir /s/q '+ '"'+os.path.join(video_download_directory,video_id)+'"'
            delete_folder=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
            out,err=delete_folder.communicate()
            return Response(data, status=status.HTTP_200_OK, headers=None)
        except Exception as e:
            print("****************************************************")
            print(e)
            print("****************************************************")
            data['status_code']=400
            data['message']=str(e)
            return Response(data, status=status.HTTP_200_OK, headers=None)


class ResolutionFormats(APIView):
    def get(self,request,format=None):
        try:
            data={
                "status_code": 200,
                "message": "Requested Accepted",
                "result":[]

            }
            result_list=[]
            resolution_list=['360X480','360X640','480X360','640X360','640X480','720X360','720X480','720X640','800X600','1024X768','1280X720','1280X800','1280X1024','1920X1080']
            for i in range(1,15):
                temp={}
                temp["id"]=i
                temp["url"]="http://storage.googleapis.com/video-streaming-project-bucket/resolution_formats/"+str(i)+".mp4"
                temp['resolution']=resolution_list[i-1]
                result_list.append(temp)
            data['result']=result_list
            return Response(data, status=status.HTTP_200_OK, headers=None)
        except Exception as e:
            print(e)
            data['status_code']=400
            data['message']=str(e)
            return Response(data, status=status.HTTP_200_OK, headers=None)



class FileUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, format=None):
        print("Entered Here")
        print((request.data))
        destination_bucket='video-streaming-project-bucket'
        data = {
                "status_code": 200,
                "message": "Request is accepted"  ,
                "result":{}            
        } 
        
        storage_client = storage.Client()
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            video_id=uuid.uuid4()
            video_id_str=str(video_id).replace("-","")
            mypath=os.path.join(os.getcwd(),"media")
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            filename=onlyfiles[0]
            if((os.path.exists(os.path.join(os.getcwd(),"media",onlyfiles[0].split(".")[0]+".mp4")))==False):
                mp4_conversion_cmd='ffmpeg -i '+'"'+os.path.join(os.getcwd(),"media",onlyfiles[0])+'"'+ " "+'"'+os.path.join(os.getcwd(),"media",onlyfiles[0].split(".")[0]+".mp4") +'"'            
                
                filename=filename.split(".")[0]+".mp4"
                p=subprocess.Popen(mp4_conversion_cmd,stdout=subprocess.PIPE,shell=True)
                p.wait()
                out,err=p.communicate()
            video_description='file uploaded'
            
            result = subprocess.run(["ffprobe", "-v", "error", "-show_entries","format=duration", "-of","default=noprint_wrappers=1:nokey=1", os.path.join(os.getcwd(),"media",filename)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            if(result.stdout!='N/A\n'):
                video_duration=float(result.stdout)   
            else:
                video_duration=0
            props = get_video_properties( os.path.join(os.getcwd(),"media",filename)) 
            video_resolution=str(props['width'])+"X"+str(props['height'])
            video_encoding=str(props['codec_name'])
            video_size=os.path.getsize( os.path.join(os.getcwd(),"media",filename))
            thumbnail_command='ffmpeg -i ' +'"'+os.path.join(os.getcwd(),"media",filename)+'"'+' -ss 00:00:01.000 -vframes 1 '+'"'+ os.path.join(os.getcwd(),"media",video_id_str+'.png')+'"'
            video_thumbnail=subprocess.Popen(thumbnail_command,shell=True,stdout=subprocess.PIPE)
            out,err=video_thumbnail.communicate()
            bucket = storage_client.bucket(destination_bucket)
            destination_blob_name=video_id_str+'/video/'+filename
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(os.path.join(os.getcwd(),"media",filename))
            destination_blob_name_thumbnail='thumbnail/'+video_id_str+".png"
            blob = bucket.blob(destination_blob_name_thumbnail)
            blob.upload_from_filename(os.path.join(os.getcwd(),"media",video_id_str+'.png'))
            blob.make_public()
            video_clip_command='ffmpeg -ss 00:00:05 -i '+'"'+os.path.join(os.getcwd(),"media",filename)+'"'+' -t 00:00:05 -vcodec copy -acodec copy '+'"'+ os.path.join(os.getcwd(),"media",video_id_str+'.mp4')+'"'
            video_clip=subprocess.Popen(video_clip_command,shell=True,stdout=subprocess.PIPE)
            out,err=video_clip.communicate()
            destination_blob_name_clip='clip/'+video_id_str+".mp4"
            blob1 = bucket.blob(destination_blob_name_clip)
            blob1.upload_from_filename(os.path.join(os.getcwd(),"media",video_id_str+'.mp4'))
            blob1.make_public()
            print("Blob {} is publicly accessible at {}".format(blob.name, blob.public_url))                        
            print(video_resolution)
            data['result']['video_id']=video_id
            VideoDetails.objects.create(video_id=video_id,video_name=filename,video_description=video_description,thumbnail_url=blob.public_url,video_duration=video_duration,video_encoding=video_encoding,video_path="gs://"+destination_bucket+"/"+destination_blob_name,video_size=video_size,video_category=video_description,video_resolution=video_resolution,clip_url=blob1.public_url)
            cmd='rmdir /s/q '+ '"'+os.path.join(os.getcwd(),"media")+'"'
            delete_folder=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
            out,err=delete_folder.communicate()
            hostname = socket.gethostname()    
            IPAddr = socket.gethostbyname(hostname)
            response=requests.post('http://192.168.0.22:8000/encoding',data={'video_id':str(video_id)})
            

            try:
                os.mkdir(os.path.join(os.getcwd(),"media"))
            except OSError:
                print ("Creation of the directory %s failed" % path)
            if response.status_code==200:
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                data['status_code']=400
                data['message']="Upload failed"
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
