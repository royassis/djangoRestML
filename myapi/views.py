import logging
import pickle

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from .forms import UploadFileForm
from .models import MlModel, MlProject
from .serializers import MlModelSerializer, MlProjectSerializer

logging.basicConfig(level=logging.DEBUG)


class ModelViewSet(viewsets.ModelViewSet):
    queryset = MlModel.objects.all().order_by(r'name')
    serializer_class = MlModelSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.serializer_class(data=request.POST)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        logging.debug(serializer.data)
        logging.debug(data)
        logging.debug("*" * 100)

        new_name = data["name"]
        new_project = data["project"]
        new_upload = serializer.data["upload"]

        mymodel = MlModel.objects.get(pk=instance.id)
        mymodel.name = new_name
        mymodel.project = new_project
        mymodel.upload = new_upload

        mymodel.save()

        return JsonResponse(serializer.data)


class MlProjectViewSet(viewsets.ModelViewSet):
    queryset = MlProject.objects.all().order_by(r'name')
    serializer_class = MlProjectSerializer


class PredictView(APIView):
    queryset = MlModel.objects.all().order_by(r'name')
    serializer_class = MlModelSerializer

    class IncredibleInputSerializer(serializers.Serializer):
        model_input = serializers.CharField()
        id = serializers.IntegerField()

    def get(self, request):
        # Validate the incoming input (provided through query parameters)
        serializer = self.IncredibleInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # Get the model input
        data = serializer.validated_data
        model_input = data["model_input"]
        model_id = data["id"]

        mymodel = MlModel.objects.get(pk=model_id)
        mymodel = pickle.loads(mymodel.model)

        # Perform the complex calculations
        complex_result = model_input + str(mymodel)

        # Return it in your custom format
        return JsonResponse({"complex_result": complex_result, })


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            new_model = MlModel(name=form.cleaned_data['title'], model=f.read())
            new_model.save()
            logging.debug(f"model saved")
            return HttpResponseRedirect('')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
