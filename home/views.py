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
# from home.models import Submit
from django.contrib import messages
from rest_framework.permissions import AllowAny
import base64
import tempfile
from django.http import FileResponse, Http404
import sqlite3
# Create your views here.
def index(request):
    return render(request,'index.html')

    
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
            generatedPdf=generate_resume2(jobRole,request)
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
        
def submit_resume(request):
    if request.method=="POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        linkedin=request.POST.get('linkedin')
        summary=request.POST.get('summary')

        request.session['first_name'] = first_name
        request.session['last_name'] = last_name
        request.session['email'] = email
        request.session['phone'] = phone
        request.session['linkedin'] = linkedin
        request.session['summary'] = summary

        # Project Details
        projects=[]
        i = 1
        while True:
            project_title = request.POST.get(f'project_title_{i}')
            project_start_date = request.POST.get(f'project_start_date_{i}')
            project_end_date = request.POST.get(f'project_end_date_{i}')
            project_description = request.POST.get(f'project_desc_{i}')

            # Break the loop if no more projects are found
            if not project_title:
                break

            # Add project to the list
            projects.append({
                'project_title': project_title,
                'project_start_date': project_start_date,
                'project_end_date': project_end_date,
                'project_description': project_description,
            })
            i += 1
        request.session['projects'] = projects


        # Experience Details
        experiences=[]
        i = 1
        while True:
            job_title = request.POST.get(f'job_title_{i}')
            job_description = request.POST.get(f'job_description_{i}')
            company_name = request.POST.get(f'company_name_{i}')
            employment_start_date = request.POST.get(f'employment_start_date_{i}')
            employment_end_date = request.POST.get(f'employment_end_date_{i}')  
            job_details = request.POST.get(f'job_details_{i}')

            # Break the loop if no more experiences are found
            if not job_title:
                break

            # Add experience to the list
            experiences.append({
                'job_title': job_title,
                'job_description': job_description,
                'company_name': company_name,
                'employment_start_date': employment_start_date,
                'employment_end_date': employment_end_date,
                'job_details': job_details,
            })
            i += 1
        request.session['experiences'] = experiences
        
        # Education Details
        education=[]
        i = 1
        while True:
            college_name = request.POST.get(f'college_name_{i}')
            degree = request.POST.get(f'degree_{i}')
            cgpa = request.POST.get(f'cgpa_{i}')
            college_start_date = request.POST.get(f'college_start_date_{i}')
            college_end_date = request.POST.get(f'college_end_date_{i}')    

            # Break the loop if no more education are found
            if not college_name:
                break

            # Add education to the list
            education.append({
                'college_name': college_name,
                'degree': degree,
                'cgpa': cgpa,
                'college_start_date': college_start_date,
                'college_end_date': college_end_date,
            })
            i += 1
        request.session['education'] = education

        # Skills Details
        skills_languages=request.POST.get('skills_languages')
        request.session['skills_languages'] = skills_languages

        # Certifications Details
        certification_1 = request.POST.get('certification_1')
        request.session['certification_1'] = certification_1

        # Research Papers Details
        research_papers = []    
        i = 1
        while True:
            research_title = request.POST.get(f'research_title_{i}')
            research_authors = request.POST.get(f'research_authors_{i}')
            research_publication = request.POST.get(f'research_publication_{i}')

            # Break the loop if no more research papers are found
            if not research_title:
                break

            # Add research paper to the list
            research_papers.append({
                'research_title': research_title,
                'research_authors': research_authors,
                'research_publication': research_publication,
            })
            i += 1  
        request.session['research_papers'] = research_papers    

        # Positions of Responsibility Details 
        position_1=request.POST.get('position_1')
        request.session['position_1'] = position_1








        
        # project_title_1=request.POST.get('project_title_1')
        # project_start_date_1=request.POST.get('project_start_date_1')
        # project_end_date_1=request.POST.get('project_end_date_1')
        # project_description_1=request.POST.get('project_description_1')

       
        
        # name = first_name + " " + last_name
        # personal_details = PersonalDetails(name,email,phone,linkedin)
        # personal_details, academic_details, chapters, professional_summary, skills, positions_of_responsibility, projects, research_papers = get_sample_data()
        # generate_resume2("chef",request)
        # return HttpResponse('success')
        return render(request, 'resumeForm.html')
    return HttpResponse('success')

        