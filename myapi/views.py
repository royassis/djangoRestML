import logging
import pickle
import shutil
from pathlib import Path

from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, serializers
from rest_framework.views import APIView

from .forms import UploadFileForm
from .models import MlModel, MlProject
from .serializers import MlModelSerializer, MlProjectSerializer

logging.basicConfig(level=logging.DEBUG)


def delete_project_folder(instance, *args, **kwargs):
    try:
        p = Path(settings.MEDIA_MLMODELS_ROOT).joinpath(str(instance.project.name))
        shutil.rmtree(p)
    except FileNotFoundError:
        pass


class ModelViewSet(viewsets.ModelViewSet):
    queryset = MlModel.objects.all().order_by(r'name')
    serializer_class = MlModelSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_project_folder(instance)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.name = serializer.validated_data.get("name")
        instance.project = serializer.validated_data.get("project")
        instance.upload = request.data.get("file")

        instance.save()

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
    return render(request, 'myapi/upload.html', {'form': form})

class Predict(APIView):
    def post(self, request, id, *args, **kwargs):
        proj = MlProject.objects.get(id=id)
        last_model_orm_object = proj.mlmodels.last()
        m_as_bytes = last_model_orm_object.upload.read()
        m = pickle.loads(m_as_bytes)
        prediction = m.predict(request.data.get("data"))
        return JsonResponse({"data": prediction.tolist()})