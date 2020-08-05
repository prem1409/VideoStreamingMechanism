from django.db import models
import uuid
from django.utils import timezone

# Create your models here.
class VideoDetails(models.Model):
    id=models.AutoField(primary_key = True)
    video_id=models.UUIDField(default = uuid.uuid4, editable=False)
    video_name=models.TextField(blank=False, null=False)
    video_description=models.TextField(blank=True, null=True)
    thumbnail_url=models.TextField(blank=True, null=True)
    video_duration=models.BigIntegerField(null=True)
    video_category=models.CharField(max_length=100 ,null=True)
    video_resolution=models.CharField(max_length=12,null=True)
    video_encoding=models.CharField(max_length=12,null=True)
    video_path=models.TextField(blank=True,null=True)
    date_created=models.DateTimeField(auto_now_add=True)
    video_size=models.BigIntegerField(null=True)
    video_count=models.BigIntegerField(null=True,default=0)
    clip_url=models.TextField(blank=True,null=True)
    class Meta:
        db_table='video_details'
        managed=False

class VideoEncoding(models.Model):
    id=models.AutoField(primary_key=True)
    video_id=models.ForeignKey(VideoDetails,db_column="video_id",on_delete=models.CASCADE)
    video_encoding=models.CharField(max_length=12,null=True)
    video_resolution=models.CharField(max_length=12,null=True)
    video_path=models.TextField(blank=True,null=True)
    video_thumbnail=models.TextField(blank=True, null=True)
    class Meta:
        db_table='video_encoding'
        managed=False

class VideoUploadRequest(models.Model):
    path=models.TextField()
    is_bucket_path=models.BooleanField(default=True)
    class Meta:
        managed=False

class VideoEncodingFormat(models.Model):
    id=models.AutoField(primary_key=True)
    encoding_type=models.TextField(blank=True, null=True,max_length=10)
    resolution=models.TextField(blank=True, null=True,max_length=10)
    class Meta:
        db_table='video_encoding_formats'
        managed=False

class VideoEncodingDetails(models.Model):
    id=models.AutoField(primary_key=True)
    video_id=models.ForeignKey(VideoDetails,db_column='video_id',on_delete=models.CASCADE)
    encoding_id=models.ForeignKey(VideoEncodingFormat,db_column='encoding_id',on_delete=models.CASCADE)
    video_path=models.TextField(blank=True,null=True)
    class Meta:
        db_table='encoded_video_details'
        managed=False

class UserManagement(models.Model):
    id=models.AutoField(primary_key = True,default=None)
    firstName=models.TextField(blank=False, null=False,max_length=25,default=None)
    lastName=models.TextField(blank=False, null=False,max_length=25,default=None)
    username=models.TextField(blank=False, null=False,max_length=50,default=None)
    password=models.TextField(blank=False, null=False,default=None)
    signUpDate=models.DateTimeField(auto_now_add=True)
    email=models.TextField(blank=False, null=False,max_length=40,default=None)
    isSubscribed=models.SmallIntegerField(max_length=4,blank=False,default=None)
    class Meta:
        db_table='user_credentials'
        managed=False
class VideoUserTable(models.Model):
    id=models.AutoField(primary_key=True)
    video_id=models.ForeignKey(VideoDetails,db_column='video_id',on_delete=models.CASCADE)
    user_id=models.ForeignKey(UserManagement,db_column='user_id',on_delete=models.CASCADE)
    duration=models.TextField(blank=True,null=True)
    class Meta:
        db_table='video_transcation'
        managed=False

class File(models.Model):
    image = models.FileField(blank=False, null=False)
    class Meta:
        managed=False
    def __str__(self):
        return self.image.name

    
