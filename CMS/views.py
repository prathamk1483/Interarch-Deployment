from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from . imageHandler import upload_file
import os
from django.conf import settings
from getmac import get_mac_address as gma
import requests

import socket

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=20)
        return True
    except OSError:
        return False


def validateLicenseDeviceAndBusiness(license,mac,client):
    url="https://orconixlicensevalidation.vercel.app/validateLicense"
    params={
        "license":license,
        "macAddress":mac,
        "clientId":client,
    }

    if is_connected():
        print("✅ Internet is connected")
    else:
        print("❌ No internet connection")
        return {'valid':"No Internet" }
    
    try:
        response = requests.get(url,params)
    except:
        return True
    
    return response.json()

def list_uploads(request, folder_name):
    folder_path = os.path.join(settings.MEDIA_ROOT, folder_name)

    if not os.path.exists(folder_path):
        return HttpResponse("Folder not found", status=404)

    files = os.listdir(folder_path)
    links = []
    for file in files:
        # Build URL for each file
        file_url = f"{settings.MEDIA_URL}{folder_name}/{file}"
        links.append(f'<a href="{file_url}">{file}</a><br>')

    return HttpResponse(''.join(links))

def loginView(request):
    license = "bgYBll0A4pbqnDQ0e6gAZ8In5cQpRrJ79T232aA2d83zriWGZcdW3YeFflicense"
    ClientBusiness = "MZfvzFFWNYMd4ZI2SOAyfF0Jbusiness"
    if request.method == 'POST':
        email = request.POST.get('userName')
        password = request.POST.get('userPassword')
        validStatus = validateLicenseDeviceAndBusiness(license,gma(),ClientBusiness)
        print(validStatus)
        if validStatus['valid'] == False:
            return HttpResponse(validStatus["message"])
        elif validStatus['valid'] == "No Internet":
            return HttpResponse("Probably your device is offline, check connectivity")
        
        user = authenticate(request, username=email, password=password) 

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, 'CRUDmodule/login.html')



def serialize_customer(c):
    return {
        "id": c.id,
        "name": c.name.full_names,
        "referredBy": c.referred_by,
        "paymentStatus" :c.is_payment_pending,
        "projectStatus" :c.is_project_pending,
        "email": c.email.primary,
        "PhoneNo": c.phone_number.primary,
        "specialNotes" : c.specialNotes,
        "documentLink" : c.image_link,
        "ProfileCreated":c.date_of_registration.strftime("%d %B %Y"),
        "ProfileLastUpdated":c.last_updated.strftime("%d %B %Y"),
        "Address": {
            "completeAddress": c.address.complete_address,
            "city": c.address.city,
            "state": c.address.state,
            "pincode": c.address.pincode,
            "landmark": c.address.landmark,
        },
        "plotDetails": {
            "plotNumber": c.plot_details.plot_number,
            "plotArea": c.plot_details.plot_area,
            "roadDirection" : c.plot_details.roadDirection,
            "roadWidth" : c.plot_details.roadWidth,
            "plotDimensions" :{
                "east":c.plot_details.plot_dimensions.plotEast,
                "west":c.plot_details.plot_dimensions.plotWest,
                "north" :c.plot_details.plot_dimensions.plotNorth,
                "south" : c.plot_details.plot_dimensions.plotSouth,
            },
        },
        "clientRequirements": c.client_requirements.requirements,
        "Services":{
            "services" : c.services.services,
            "details" : c.services.details,
        },
        "paymentDetails": {
            "transactions": c.payment_details.transactions,
            "advancePaid" : c.payment_details.advancedPayment,
            "originalAmount": c.payment_details.original_amount,
            "discountAmount": c.payment_details.discount_amount,
            "totalPayableAmount" : c.payment_details.totalPayableAmount,
            "totalAmountPaid": c.payment_details.total_amount_paid,
            "totalAmountDue": c.payment_details.total_amount_due,
        },
    }

@login_required(login_url='login')
def index(request):
    return render(request, 'CRUDmodule/home.html')

login_required(login_url='login')
def userCreationPage(request):
    return render(request, 'CRUDmodule/createUserPage.html')


@login_required(login_url='login')
def createClient(request):
    if request.method == 'POST':
        fullNames = request.POST.get('full_names', '')
        name = Name.objects.create(full_names=fullNames)

        # Email
        primary_email = request.POST.get('primary_email')
        email = Email.objects.create(primary=primary_email)

        # Phone Number
        primary_numbers = request.POST.get('phone_numbers', '')
        phone = PhoneNumber.objects.create(primary=primary_numbers)

        # Address
        complete_address = request.POST.get('complete_address')
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")
        landmark = request.POST.get("landmark")
        address = Address.objects.create(
            complete_address=complete_address,
            city=city,
            state=state,
            pincode=pincode,
            landmark=landmark
        )

        # Plot Dimensions
        plot_dimensions = PlotDimensions.objects.create(
            plotEast=request.POST.get('plotEast'),
            plotWest=request.POST.get('plotWest'),
            plotNorth=request.POST.get('plotNorth'),
            plotSouth=request.POST.get('plotSouth')
        )

        # Plot Details
        plot_details = PlotDetails.objects.create(
            plot_number=request.POST.get("customerPlotNumber", 0),
            plot_area=request.POST.get('plot_area'),
            plot_dimensions=plot_dimensions,
            roadDirection=request.POST.get('roadDirection'),
            roadWidth=request.POST.get('roadWidth')
        )

        # Client Requirements
        requirements = request.POST.get('requirements', '')
        client_requirements = ClientRequirements.objects.create(requirements=requirements)

        # Services
        services = {
            "Architecture Planning": request.POST.get('Architecture_Planning') == 'on',
            "RCC Design": request.POST.get('RCC_Design') == 'on',
            "3D Elevation": request.POST.get('T3D_Elevation') == 'on',
            "Blueprint": request.POST.get('Blueprint') == 'on',
            "Municipal Data": request.POST.get('Municipal_Data') == 'on',
            "Estimations": request.POST.get('Estimations') == 'on',
            "Site Visits": request.POST.get('Site_Visits') == 'on',
            "Interior": request.POST.get('Interior') == 'on'
        }

        details = {
            "Architecture Planning": request.POST.get('Architecture_Planning_detail'),
            "RCC Design": request.POST.get('RCC_Design_detail'),
            "3D Elevation": request.POST.get('T3D_Elevation_detail'),
            "Blueprint": request.POST.get('Blueprint_detail'),
            "Municipal Data": request.POST.get('Municipal_Data_detail'),
            "Estimations": request.POST.get('Estimations_detail'),
            "Site Visits": request.POST.get('Site_Visits_detail'),
            "Interior": request.POST.get('Interior_detail'),
        }

        services = Services.objects.create(services=services, details=details)

        #  Handle ALL Payment Transactions
        modes = request.POST.getlist("paymentMode")
        statuses = request.POST.getlist("paymentStatus")
        dates = request.POST.getlist("paymentDate")
        amounts = request.POST.getlist("paymentAmount")

        transactions = []
        for mode, status, date, amount in zip(modes, statuses, dates, amounts):
            if mode and date and amount:
                transactions.append({
                    "mode": mode,
                    "paymentStatus": status,
                    "paymentDate": date,
                    "amountPaid": amount
                })

        payment = PaymentDetails.objects.create(
            transactions=transactions,
            advancedPayment=amounts[0] if amounts else 0,
            original_amount=request.POST.get("customerTotalAmount", 0),
            discount_amount=request.POST.get('Discount_Amount_detail', 0),
            totalPayableAmount=request.POST.get("customerTotalPayableAmount", 0),
            total_amount_paid=request.POST.get('TotalAmountPaids', 0),
            total_amount_due=request.POST.get('TotalAmountDue', 0),
        )

        # Image Upload to Google Drive
        referred_by = request.POST.get('customerRefferedBy', 'Self')
        image_file = request.FILES.get("imageUpload")
        image_url = None
        if image_file:
            try:
                image_url = upload_file(
                    file_obj=image_file,
                    filename=image_file.name,
                    clientName=fullNames.split(",")[0].strip() or "Unknown_Client"
                )
            except Exception as e:
                messages.error(request, f"Image upload failed: {e}")
                print("Image upload failed:", e)
                image_url = None
        else:
            print("Could not get image")

        # Final Customer Creation
        Customer.objects.create(
            name=name,
            referred_by=referred_by,
            email=email,
            phone_number=phone,
            address=address,
            plot_details=plot_details,
            image_link=image_url,
            client_requirements=client_requirements,
            services=services,
            payment_details=payment,
            specialNotes=request.POST.get("specialNotes"),
        )

        return redirect('home')

    return render(request, 'CRUDmodule/home.html')



@login_required(login_url='login')
def userSearchingPage(request):
    return render(request, 'CRUDmodule/searchUserPage.html')


def getCustomerData(first_name, phone_number,pendingPayment,pendingProject,reference=None):
    customer = Customer.objects.all()
    if first_name:
        customer = customer.filter(Q(name__full_names__icontains=first_name))
    if phone_number:
        customer = customer.filter(Q(phone_number__primary__icontains=phone_number))
    if reference:
        customer = customer.filter(Q(referred_by__icontains=reference))
    if pendingPayment:
        customer = customer.filter(Q(is_payment_pending = True))
    if pendingProject:
        customer = customer.filter(Q(is_project_pending = True))

    data = [{"customerDetails": serialize_customer(c)} for c in customer]
    return data

@login_required(login_url='login')
def searchClient(request):
    if request.method == 'POST':
        first_name = request.POST.get('customerFirstName', '').strip()
        phone_number = request.POST.get('customerNumber', '').strip()
        reference = request.POST.get('customerReference', '').strip()
        pendingPayment = request.POST.get("pendingPayment", "off") == "on"
        pendingProject = request.POST.get("pendingProject", "off") == "on"

        data = None
        data = getCustomerData(first_name, phone_number,pendingPayment,pendingProject,reference,)

        return render(request, 'CRUDmodule/searchUserPage.html', {
            "data": data,
            "key": "search"
        })

    return render(request, 'CRUDmodule/searchUserPage.html')

@login_required(login_url='login')
def userUpdationPage(request):
    return render(request, 'CRUDmodule/searchUserPage.html',{"key" : "update"})

@login_required(login_url='login')
def updateClientInfo(request, client_id):
    if request.method == 'POST':
        # Retrieve the existing customer object
        customer = get_object_or_404(Customer, id=client_id)
        # Update Name
        customer.is_payment_pending = request.POST.get("pendingPayment") == "on"
        customer.is_project_pending = request.POST.get("pendingProject") == "on"
        if 'full_names' in request.POST:
            customer.name.first_name = request.POST.get('full_names')
        customer.name.save()
        if "specialNotes" in request.POST:
            customer.specialNotes = request.POST.get("specialNotes")

        # Update Email
        if 'primary_email' in request.POST:
            customer.email.primary = request.POST.get('primary_email')
        customer.email.save()

        # Update PhoneNumber
        if 'phone_numbers' in request.POST:
            customer.phone_number.primary = request.POST.get('phone_numbers')
        customer.phone_number.save()

        # Update Address
        if 'complete_address' in request.POST:
            customer.address.complete_address = request.POST.get('complete_address', '')
        if 'city' in request.POST:
            customer.address.city = request.POST.get('city', '')
        if 'state' in request.POST:
            customer.address.state = request.POST.get('state', '')
        if 'pincode' in request.POST:
            customer.address.pincode = request.POST.get('pincode', '')
        if 'landmark' in request.POST:
            customer.address.landmark = request.POST.get('landmark', '')
        customer.address.save()

        # Update PlotDimensions
        if 'plotEast' in request.POST:
            customer.plot_details.plot_dimensions.plotEast = request.POST.get('plotEast', 0)
        if 'plotWest' in request.POST:
            customer.plot_details.plot_dimensions.plotWest = request.POST.get('plotWest', 0)
        if 'plotNorth' in request.POST:
            customer.plot_details.plot_dimensions.plotNorth = request.POST.get('plotNorth', 0)
        if 'plotSouth' in request.POST:
            customer.plot_details.plot_dimensions.plotSouth = request.POST.get('plotSouth', 0)
        customer.plot_details.plot_dimensions.save()

        # Update PlotDetails
        if 'customerPlotNumber' in request.POST:
            customer.plot_details.plot_number = request.POST.get("customerPlotNumber", "")
        if 'plot_area' in request.POST:
            customer.plot_details.plot_area = request.POST.get('plot_area', 0)
        if 'roadDirection' in request.POST:
            customer.plot_details.roadDirection = request.POST.get('roadDirection', 0)
        if 'roadWidth' in request.POST:
            customer.plot_details.roadWidth = request.POST.get('roadWidth', 0)
        customer.plot_details.save()

        # Update ClientRequirements
        if 'requirements' in request.POST and request.POST.get("requirements", "") != "":
            reqs = request.POST.get('requirements')
            customer.client_requirements.requirements = reqs
            customer.client_requirements.save()

        customer.services.Architecture_Planning = request.POST.get('Architecture Planning', False) == "on"
        if request.POST.get("Architecture Planning details", "") != "":
            customer.services.Architecture_Planning_text = request.POST.get("Architecture Planning details", "")

        customer.services.RCC_Design = request.POST.get('RCC Design', False) == "on"
        if request.POST.get('RCC Design details') != "":
            customer.services.RCC_Design_text = request.POST.get('RCC Design details')

        customer.services.T3D_Elevation = request.POST.get('3D Elevation', False) == "on"
        if request.POST.get('3D Elevation details') != "":
            customer.services.T3D_Elevation_text = request.POST.get('3D Elevation details')

        customer.services.Blueprint = request.POST.get('Blueprint', False) == "on"
        if request.POST.get('Blueprint details') != "":
            customer.services.Blueprint_text = request.POST.get('Blueprint details')

        customer.services.Municipal_Data = request.POST.get('Municipal Data', False) == "on"
        if request.POST.get('Municipal Data details') != "":
            customer.services.Municipal_Data_text = request.POST.get('Municipal Data details')

        customer.services.Estimations = request.POST.get('Estimations', False) == "on"
        if request.POST.get('Estimations details') != "":
            customer.services.Estimations_text = request.POST.get('Estimations details')

        customer.services.Site_Visits = request.POST.get('Site Visits', False) == "on"
        if request.POST.get('Site Visits details') != "":
            customer.services.Site_Visits_text = request.POST.get('Site Visits details')

        customer.services.Interior = request.POST.get('Interior', False) == "on"
        if request.POST.get('Interior details') != "":
            customer.services.Interior_text = request.POST.get('Interior details')

        customer.services.save()

        # Update PaymentDetails (fixed duplication logic)
        existing_transactions = customer.payment_details.transactions
        if 'paymentMode' in request.POST:
            # Create new transactions from the form data
            new_transactions = []
            payment_modes = request.POST.getlist('paymentMode')
            payment_statuses = request.POST.getlist('paymentStatus')
            payment_dates = request.POST.getlist('paymentDate')
            payment_amounts = request.POST.getlist('paymentAmount')

            for mode, status, date, amount in zip(payment_modes, payment_statuses, payment_dates, payment_amounts):
                new_transactions.append({
                    'mode': mode,
                    'paymentStatus': status,
                    'paymentDate': date,
                    'amountPaid': float(amount) if amount else 0.0
                })

            # **Replace** the transaction list entirely rather than appending
            customer.payment_details.transactions = new_transactions
            customer.payment_details.total_amount_paid = sum(tx['amountPaid'] for tx in new_transactions)
            customer.payment_details.total_amount_due = float(request.POST.get('TotalAmountDue', 0))
            customer.payment_details.save()

        # Save the updated customer object
        customer.save()

        return redirect('home')
    return redirect('home')

@login_required(login_url='login')
def updateClient(request):
    if request.method == 'POST':
        first_name = request.POST.get('customerFirstName', '').strip()
        phone_number = request.POST.get('customerNumber', '').strip()
        pendingPayment = request.POST.get("pendingPayment", "off") == "on"
        pendingProject = request.POST.get("pendingProject", "off") == "on"

        data = getCustomerData(first_name,phone_number,pendingPayment,pendingProject)
        return render(request, 'CRUDmodule/searchUserPage.html', {"data": data , "key" : "update"})

    elif request.method == "GET":
        customer = request.GET
        data = getPrintingData(customer)
        return render(request, 'CRUDmodule/userUpdatePage.html', {"data": data , "key" : "update"})

@login_required(login_url='login')
def userDeletionPage(request):
   return render(request,"CRUDmodule/deleteUserPage.html")

@login_required(login_url='login')
def deleteClient(request):
    if request.method == 'POST':
        try:
            client = Customer.objects.get(pk=request.POST.get("customerID"))
        except :
            return HttpResponse("Customer with given ID doesn't exist ,Probably this client is already deleted")
        client.delete()
        return redirect('home')
    return redirect('home')

def getPrintingData(customer):
    customer_id = customer.get("id")
    c = get_object_or_404(Customer, id=customer_id)
    return serialize_customer(c)

@login_required(login_url='login')
def getInvoice(request):
    customer = request.GET
    data = getPrintingData(customer)
    return render(request, 'CRUDmodule/invoice.html', {"data": data})

from django.contrib.auth import logout
from django.shortcuts import redirect

@login_required(login_url='login')
def logoutView(request):
    logout(request)
    return redirect('login')