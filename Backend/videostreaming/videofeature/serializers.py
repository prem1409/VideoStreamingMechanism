# -*- coding: utf-8 -*-
__author__ = "Prem Raheja"
__copyright__ = "Copyright (©) 2019. University of Alberta  All rights reserved."

# Django rest framework related dependencies
from rest_framework import serializers
#Project related dependencies
from .models import VideoDetails,VideoEncoding,VideoUploadRequest
from rest_framework import serializers
from .models import File
class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"

class VideoDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model= VideoDetails
        fields=('__all__')
class VideoEncodingSerializer(serializers.ModelSerializer):
    class Meta:
        model=VideoEncoding
        fields=('__all__')
class VideoUploadRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model =VideoUploadRequest
        fields=('__all__')