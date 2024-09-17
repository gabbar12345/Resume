import ast
import logging
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import Http404, HttpResponse, JsonResponse
from django.http import HttpResponse
import os

from home.prompts import *
from home.utilities import ResumePDF, create_resume, formatedResponse, generate_resume2, get_home_directory, get_response, get_sample_data, save_resume
from home.constants import pdf_path
from home.models import Submit
from django.contrib import messages
from rest_framework.permissions import AllowAny
import base64
import tempfile
from django.http import FileResponse, Http404
# Create your views here.
def index(request):
    return render(request,'index.html')

def submit(request):
    if request.method=="POST":
        email=request.POST.get('email')
        password=request.POST.get('pwd')
        sub=Submit(email=email,password=password)
        sub.save()
        messages.success(request,"Data updated successfully")

    return HttpResponse(Submit.objects.all())
    
def form_view(request):
    return render(request, 'resumeForm.html')

class Home(APIView):
    def post(self, request):
        try:
            jobRole = request.data.get('jobRole')
            fields = {
            "name": "John Doe",
            "contact information": "Email: john.doe@example.com | Phone: 555-555-5555 | LinkedIn: linkedin.com/in/johndoe",
            "sections": {
                "Summary": [
                    "Motivated software engineer with 5+ years of experience in developing scalable applications."
                ],
                "Experience": [
                    "Led Implementation of Anaplan TPM solution for Pepsi Bottling Ventures. Managed project lifecycle from requirements gathering to post-deployment optimization. Streamlined Funding, Claims (Payment), and Accruals processes, improving operational efficiency and reducing processing time by 63%",
                    "Pioneered an innovative GPT-based AI solution for revenue growth management, integrating labeled RGM data to deliver actionable insights through charts and queries",
                    "Supported Functional Testing, UAT and Hypercare of Salesforce TPM solution implementation for Duracell Co.",
                    "Developed comprehensive Anaplan TPM product for PwC, featuring modules for Annual Operating Plans, Promotion Management, Fund Management, Payments, Accruals, and Reporting",
                    "Implemented SAP BTP iFlow for Anaplan-SAP S/4HANA integration. Achieved 98% data transfer accuracy and 75% reduction in manual entry",
                    "Supported data-driven market scan for AT&T Inc., analyzed customer data & competitor offerings to identify market opportunities & enhance competitive benchmarking. Provided analysis of results through reports, narratives, and presentations",
                    "Supported financial planning and analysis for Google LLC, aiding in budget management and financial forecasting to optimize operational efficiency",
                    "Developed and implemented Microsoft Power Platform solution of dynamic resource management, enhancing efficiency, visibility, and data-driven decision-making for Customer Transformation Team leadership"
                ],
                "Education": [
                    "B.S. in Computer Science, XYZ University, 2017"
                ],
                "Skills": [
                    "Python, Java, C++",
                    "Django, Flask, Spring Boot",
                    "SQL, MongoDB",
                    "Version Control: Git"
                ],
                "Projects": [
                    "Project hashedIn: Developed a web application for ABC Corp, which improved their internal processes by 20%."
                ],
                "Certifications": [
                    "Certified Kubernetes Administrator (CKA)",
                    "AWS Certified Solutions Architect"
                ]
            }
        }
            experience_prompt=pre_experience.format(experience=fields["sections"]["Experience"],data=jobRole)
            et=get_response(user_prompt=experience_prompt)
            f = ast.literal_eval(et)
            fields["sections"]["Experience"]=f
            document=create_resume(fields)
            save_resume(document)
            return HttpResponse("success")
        
        except Exception as err:
            logging.error(f"Exception occurred ->{err}")
            return HttpResponse(f"Error -> {err}", status=500)
              
class Resume2(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try: 
            jobRole = request.data.get('jobRole', '')
            generatedPdf=generate_resume2(jobRole)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            generatedPdf.output(temp_file.name)
            temp_file.close()
            request.session['temp_pdf_path'] = temp_file.name
            message = f"Successfully created resume for {jobRole}"
            messages.success(request, message)
            return render(request, 'resumeForm.html', {'message': message})
            # output_dir = get_home_directory()
            # os.makedirs(output_dir, exist_ok=True)
            # pdf.output(os.path.join(output_dir, 'resume.pdf'))
           
        except Exception as err:
            logging.error(f"Exception occurred ->{err}")
            return HttpResponse(f"Error -> {err}", status=500)
        
class Preview(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try: 
            # jobRole = request.data.get('jobRole', '')
            generatedPdf=request.session.get('temp_pdf_path')
            if not generatedPdf or not os.path.exists(generatedPdf):
                raise Http404("PDF not found. Please generate First")
            return FileResponse(open(generatedPdf, 'rb'), content_type='application/pdf')
        except Exception as err:
            logging.error(f"Exception occurred ->{err}")
            return HttpResponse(f"Error -> {err}", status=500)

        