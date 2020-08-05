"""videostreaming URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import home
from videofeature.views import VideoFeatureReading,VideoDetailExtraction,VideoPlayLink,VideoUserController,LoginManagementController,VideoEncodingConversionController,ResolutionFormats,FileUploadView

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('videoupload',VideoFeatureReading.as_view()),
    re_path('videodetails',VideoDetailExtraction.as_view()),
    re_path('videoplay',VideoPlayLink.as_view()),
    re_path('upload',FileUploadView.as_view()),
    path("",home),
    re_path(r'api/login$',LoginManagementController.as_view()),
    re_path('videowatch',VideoUserController.as_view()),
    re_path('encoding',VideoEncodingConversionController.as_view()),
    re_path('resolution',ResolutionFormats.as_view())
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)