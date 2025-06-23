# Name: Amir Ali Malekani Nezhad
# Student ID: S2009460

from django.contrib import messages  # type: ignore
from django.contrib.auth import authenticate, login, logout  # type: ignore
from django.contrib.auth.decorators import login_required  # type: ignore
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render, get_object_or_404  # type: ignore

from .models import AidRequest, DisasterReport, Shelter, User, VolunteerAssignment


def home(request):
    return render(request, 'home.html')

# Register View
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        phone_number = request.POST.get('phone_number')

        # Prevent public registration for Authority role
        if role == 'Authority':
            return redirect('home')  # Or show an error message

        if username and password and role:
            User.objects.create_user(username=username, password=password, role=role, phone_number=phone_number)
            return redirect('login')

    return render(request, 'register.html')

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')

    return render(request, 'login.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('home')

# Submit disaster reports
@login_required
def submit_disaster(request):
    if request.user.role != 'Citizen':
        return redirect('home')

    if request.method == 'POST':
        disaster_type = request.POST.get('disaster_type')
        gps_coordinates = request.POST.get('gps_coordinates')
        severity = request.POST.get('severity')
        description = request.POST.get('description')

        if disaster_type and gps_coordinates and severity:
            from .models import DisasterReport
            DisasterReport.objects.create(
                reporter=request.user,
                disaster_type=disaster_type,
                gps_coordinates=gps_coordinates,
                severity=int(severity),
                description=description
            )
            return redirect('disaster_reports')

    return render(request, 'submit_disaster_form.html')

# Volunteer Information Form
@login_required
def volunteer_info(request):
    if request.user.role != 'Volunteer':
        return redirect('home')

    from .models import Skill, VolunteerInfo

    volunteer_info, _ = VolunteerInfo.objects.get_or_create(user=request.user)
    all_skills = Skill.objects.all()

    if request.method == 'POST':
        selected_skill_ids = request.POST.getlist('skills')
        is_available = request.POST.get('is_available') == 'True'

        volunteer_info.is_available = is_available
        volunteer_info.skills.set(selected_skill_ids)
        volunteer_info.save()

        return redirect('home')

    selected_skills = volunteer_info.skills.values_list('id', flat=True)
    context = {
        'skills': all_skills,
        'selected_skills': selected_skills,
        'is_available': volunteer_info.is_available,
    }
    return render(request, 'volunteer_info_form.html', context)

# Disaster Reports
@login_required
def disaster_reports(request):
    reports = DisasterReport.objects.all()

    disaster_type = request.GET.get('type')
    severity = request.GET.get('severity')
    location = request.GET.get('location')
    date = request.GET.get('date')

    if disaster_type:
        reports = reports.filter(disaster_type=disaster_type)
    if severity:
        reports = reports.filter(severity=severity)
    if location:
        reports = reports.filter(gps_coordinates__icontains=location)
    if date:
        reports = reports.filter(timestamp__date=date)

    return render(request, 'disaster_reports.html', {'reports': reports})

# Aid Request
@login_required
def aid_request(request):
    if request.method == 'POST':
        disaster_id = request.POST.get('disaster_report')
        aid_type = request.POST.get('aid_type')
        details = request.POST.get('details')

        if disaster_id and aid_type:
            disaster = DisasterReport.objects.get(id=disaster_id)
            AidRequest.objects.create(
                requester=request.user,
                disaster_report=disaster,
                aid_type=aid_type,
                details=details
            )
            return redirect('disaster_reports')
    return render(request, 'aid_request_form.html')

# Citizen requests visible to themselves
@login_required
def my_requests(request):
    if request.user.role != 'Citizen':
        return redirect('home')

    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        assignment = VolunteerAssignment.objects.get(id=assignment_id)

        if assignment.aid_request.requester == request.user:
            assignment.citizen_confirmed = True
            assignment.aid_request.status = 'Completed'  # Set aid request as completed
            assignment.aid_request.save()
            assignment.save()
            messages.success(request, "Thank you for confirming. The request is now marked as completed.")

    status_filter = request.GET.get('status')
    sort_option = request.GET.get('sort')

    requests = AidRequest.objects.filter(requester=request.user).select_related('disaster_report')

    if status_filter:
        requests = requests.filter(status=status_filter)

    if sort_option == 'oldest':
        requests = requests.order_by('request_time')
    else:
        requests = requests.order_by('-request_time')

    requests_with_volunteers = []
    for req in requests:
        assignment = VolunteerAssignment.objects.filter(aid_request=req).first()
        requests_with_volunteers.append({
            'request': req,
            'assignment': assignment
        })

    return render(request, 'my_requests.html', {
        'requests_with_volunteers': requests_with_volunteers,
        'status_filter': status_filter,
        'sort_option': sort_option
    })

# Admin-Only: Volunteer Assignment
@user_passes_test(lambda u: u.is_authenticated and u.role == 'Authority')  # type: ignore
def assign_volunteer(request):
    from .models import VolunteerInfo, VolunteerAssignment, AidRequest, User

    # Only available volunteers, prefetch skills for efficiency
    available_infos = VolunteerInfo.objects.filter(is_available=True).select_related('user').prefetch_related('skills')

    # Create list of dicts: each with user and their skills
    volunteers_with_skills = []
    for info in available_infos:
        volunteers_with_skills.append({
            'user': info.user,
            'skills': info.skills.all()
        })

    # Aid requests excluding shelter
    aid_requests = AidRequest.objects.filter(status='Pending').exclude(aid_type='Shelter')

    if request.method == 'POST':
        volunteer_id = request.POST.get('volunteer')
        aid_request_id = request.POST.get('aid_request')
        task_description = request.POST.get('task_description')

        aid_request = AidRequest.objects.get(id=aid_request_id)

        # Prevent assigning shelter requests
        if aid_request.aid_type == "Shelter":
            return redirect('assign_volunteer')

        volunteer = User.objects.get(id=volunteer_id, role='Volunteer')

        VolunteerAssignment.objects.create(
            volunteer=volunteer,
            aid_request=aid_request,
            task_description=task_description
        )

        aid_request.status = 'In Progress'
        aid_request.save()

        return redirect('home')

    return render(request, 'assign_volunteer.html', {
        'volunteer_infos': volunteers_with_skills,
        'aid_requests': aid_requests
    })

# Volunteer sees their tasks
@login_required
def my_tasks(request):
    if request.user.role != 'Volunteer':
        return redirect('home')

    from .models import VolunteerAssignment

    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        assignment = VolunteerAssignment.objects.get(id=assignment_id, volunteer=request.user)
        assignment.status = 'Completed'
        assignment.save()

    assignments = VolunteerAssignment.objects.filter(volunteer=request.user).select_related('aid_request', 'aid_request__disaster_report')

    return render(request, 'my_tasks.html', {'assignments': assignments})

# Shelter Directory
@login_required
def shelters(request):
    shelters_list = Shelter.objects.all()

    if request.method == 'POST' and request.user.role == 'Authority':
        name = request.POST.get('name')
        location = request.POST.get('location')
        capacity = request.POST.get('capacity')

        if name and location and capacity:
            Shelter.objects.create(
                name=name,
                location=location,
                capacity=int(capacity),
                availability=int(capacity),
                managed_by=request.user
            )

    return render(request, 'shelters.html', {'shelters': shelters_list})

@login_required
def edit_shelter(request, shelter_id):
    shelter = get_object_or_404(Shelter, id=shelter_id)

    if request.user.role != 'Authority' or shelter.managed_by != request.user:
        return redirect('shelters')

    if request.method == 'POST':
        shelter.name = request.POST.get('name')
        shelter.location = request.POST.get('location')
        shelter.capacity = int(request.POST.get('capacity'))
        shelter.availability = int(request.POST.get('availability'))
        shelter.save()
        return redirect('shelters')

    return render(request, 'edit_shelter.html', {'shelter': shelter})

@login_required
def delete_shelter(request, shelter_id):
    shelter = get_object_or_404(Shelter, id=shelter_id)

    if request.user.role == 'Authority' and shelter.managed_by == request.user:
        shelter.delete()

    return redirect('shelters')

@user_passes_test(lambda u: u.is_authenticated and u.role == 'Authority') # type: ignore
def assign_shelter(request):
    from .models import AidRequest, Shelter

    # Find pending shelter requests with no shelter assigned
    pending_requests = AidRequest.objects.filter(
        aid_type="Shelter",
        status="Pending",
        admitted_shelter__isnull=True
    )

    # Only shelters with available space
    shelters = Shelter.objects.filter(availability__gt=0)

    if request.method == 'POST':
        aid_request_id = request.POST.get('aid_request')
        shelter_id = request.POST.get('shelter')

        aid_request = AidRequest.objects.get(id=aid_request_id)
        shelter = Shelter.objects.get(id=shelter_id)

        if shelter.availability > 0:
            aid_request.admitted_shelter = shelter # type: ignore
            aid_request.status = "Completed"
            aid_request.save()

            shelter.availability -= 1
            shelter.save()

    return render(request, 'assign_shelter.html', {
        'pending_requests': pending_requests,
        'shelters': shelters
    })

@login_required
def leave_shelter(request):
    from .models import AidRequest

    aid_request = AidRequest.objects.filter(requester=request.user, admitted_shelter__isnull=False).first()

    if aid_request and request.method == 'POST':
        shelter = aid_request.admitted_shelter
        shelter.availability += 1 # type: ignore
        shelter.save() # type: ignore

        aid_request.admitted_shelter = None
        aid_request.save()

    return redirect('my_requests')