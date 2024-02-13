from datetime import datetime, timedelta
import requests

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from .forms import EmployeeFormSet, UserForm, AvailabilityForm, EventForm
from .models import Employee, User, AvailabilityMessage, Event


def signup(request):
    user_form = UserForm()
    employee_formset = EmployeeFormSet()

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        employee_formset = EmployeeFormSet(request.POST, instance=user_form.instance)
        if user_form.is_valid() and employee_formset.is_valid():
            user_form.save()
            employee = employee_formset.save()[0]
            events = Event.objects.filter(company=employee.company)
            for event in events:
                event.employees.add(employee)
            return redirect('signup_success')

    return render(request, 'signup/signup_form.html', {
        'user_form': user_form,
        'employee_formset': employee_formset
    })


def signup_success(request):
    return render(request, 'signup/signup_success.html')


def user_login(request):
    user_form = UserForm()
    error_message = ''
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST["password"]
        authenticated_user = authenticate(request, username=username, password=password)
        if authenticated_user is not None:
            login(request, authenticated_user)
            return redirect('list_events')
        else:
            error_message = 'Invalid username or password!'
    return render(request, 'login/login.html',
                  context={'user_form': user_form, 'error_message': error_message})


def user_logout(request):
    logout(request)
    return render(request, 'login/logout.html')


def list_employees(request):
    if request.user.is_authenticated:
        employees = Employee.objects.all()
        registered_users = """
            <h1>Registered employees</h1>
            <ul>
        """

        for employee in employees:
            registered_users += (f'<li><b>Name:</b> {employee.name} | <b>Email:</b> {employee.email} | '
                                 f'<b>Company:</b> {employee.company} | <b>Country:</b> {employee.country} </li>')
            registered_users += '<br>'
        registered_users += '</ul>'
        return HttpResponse(registered_users)
    else:
        return render(request, 'login/not_logged_in.html')


def list_users(request):
    if request.user.is_authenticated:
        users = User.objects.all()
        registered_users = """
            <h1>Registered users</h1>
            <ul>
        """
        for user in users:
            registered_users += f'<li> <b>Username:</b> {user.username} | <b>Password:</b> {user.password}</li>'
            registered_users += '<br>'
        registered_users += '</ul>'
        return HttpResponse(registered_users)
    else:
        return render(request, 'login/not_logged_in.html')


def __trim_date(date):
    date = date.replace('[', '')
    date = date.replace("'", '')
    date = date.replace(']', '')
    date = date.strip()
    return date


def add_event(request):
    if request.user.is_authenticated:
        event_form = EventForm()
        if request.method == "POST":
            event_form = EventForm(request.POST)
            if event_form.is_valid():
                event = event_form.save()
                employees = Employee.objects.filter(company=request.user.employee.company)
                for employee in employees:
                    event.employees.add(employee)
                event.company = request.user.employee.company
                event.save()
                return redirect('list_events')

        return render(request, 'event/add_event.html',
                      context={'event_form': event_form})
    else:
        return render(request, 'login/not_logged_in.html')


def __get_attendance(employee_data):
    attendance = {}
    for employee in employee_data:
        dates = employee['availability']
        company = employee['company']
        event = employee['event']
        name = employee['name']
        email = employee['email']
        for i in range(len(dates) - 1):
            dates[i] = __trim_date(dates[i])
            date = datetime.strptime(dates[i], '%d-%m-%Y').date()
            next_day = date + timedelta(days=1)
            next_day_string = next_day.strftime('%d-%m-%Y')
            if __trim_date(dates[i + 1]) == next_day_string:
                key = company + '~' + event + '~' + dates[i]
                attendees = attendance.get(key)
                names = []
                if attendees is not None:
                    for attendee in attendees:
                        names.append(attendee[0])
                if attendees is None:
                    attendance[key] = [(name, email)]
                elif name not in names:
                    attendance[key].append((name, email))

    return attendance


def __get_events(attendance_per_company):
    events = {}
    for key, employees in attendance_per_company.items():
        tokens = key.split("~")
        company = tokens[0]
        event = tokens[1]
        date = tokens[2]
        company_events = events.get(company)
        if company_events is None:
            company_events = {}
        if company_events.get(event) is None:
            company_events[event] = {"date": date, "employees": employees}
        else:
            if len(employees) > len(company_events[event]["employees"]):
                company_events[event] = {"date": date, "employees": employees}

        events[company] = company_events

    return events


def __to_string_list(availability_messages):
    availability = []
    for message in availability_messages:
        availability.append(message.availability)
    return availability


def __schedule_events(user_company):
    employees = Employee.objects.filter(company=user_company)
    availability_messages = AvailabilityMessage.objects.filter(employee__in=employees)
    events = Event.objects.filter(company=user_company)
    employees_data = []
    for i in range(len(employees) - 1):
        for event in events:
            employee_data = {}
            employee_data['availability'] = __to_string_list(
                availability_messages.filter(employee=employees[i], event=event))
            if employee_data['availability']:
                employee_data['name'] = employees[i].name
                employee_data['company'] = employees[i].company
                employee_data['email'] = employees[i].email
                employee_data['event'] = event.name
                employees_data.append(employee_data)

    attendance_per_company = __get_attendance(employees_data)
    return __get_events(attendance_per_company)


def list_events(request):
    if request.user.is_authenticated:
        user_company = request.user.employee.company
        events = Event.objects.filter(company=user_company)
        upcoming_events = []
        if request.method == "GET":
            for company_event in list(events):
                if company_event.employees.filter(id=request.user.employee.id).exists():
                    list_item = (f'<li><b>Event:</b> {company_event.name} | '
                                 f'<b>Country:</b> {company_event.country} | '
                                 f'<a href="/events/register/{company_event.id}">Register</a> | '
                                 f'<a href="/events/discard/{company_event.id}">Discard</a></li>')
                    upcoming_events.append(mark_safe(list_item))

            return render(request, 'event/list_events.html',
                          context={'upcoming_events': upcoming_events})
        else:
            company_events = __schedule_events(user_company)[user_company]
            for event, event_data in company_events.items():
                print(f'Event {event} at company {user_company} is on {event_data["date"]} '
                      f'and has the following attendance: {event_data["employees"]}')

            for event_name, event_data in company_events.items():
                event = Event.objects.get(name=event_name, company=user_company)
                if event.employees.filter(id=request.user.employee.id).exists():
                    list_item = (f'<li><b>Event:</b> {event.name} | '
                                 f'<b>Country:</b> {event.country} | '
                                 f'<a href="/events/signup/{event.id}">Sign up</a> | '
                                 f'<a href="/events/discard/{event.id}">Discard</a></li>'
                                 f'<br><b>(Start date:</b>{event_data["date"]})')

                    upcoming_events.append(mark_safe(list_item))

            return render(request, 'event/list_events.html',
                          context={'upcoming_events': upcoming_events})

    else:
        return render(request, 'login/not_logged_in.html')


def list_past_events(request):
    if request.user.is_authenticated:
        user_company = request.user.employee.company
        events = Event.objects.filter(company=user_company)
        past_events = []

        for company_event in list(events):
            list_item = (f'<li><b>Event:</b> {company_event.name} | '
                         f'<b>Country:</b> {company_event.country} | '
                         f'<a href="/events/view/{company_event.id}">View recording</a>')
            past_events.append(mark_safe(list_item))

        return render(request, 'event/list_past_events.html',
                      context={'past_events': past_events})
    else:
        return render(request, 'login/not_logged_in.html')


def __save_video(event_id, video):
    with open(f'scheduler/static/event_videos/{event_id}.mp4', 'wb') as f:
        f.write(video.content)
        f.close()


def view_event(request, event_id):
    if request.user.is_authenticated:
        try:
            event_video = requests.get(f'http://localhost:8084/events/view/{event_id}')
            __save_video(event_id, event_video)
            if 200 <= event_video.status_code < 300:
                return render(request, 'event/view_event.html',
                              context={'event_id': event_id})
            else:
                return render(request, 'event/event_video_not_found.html')
        except requests.exceptions.ConnectionError as e:
            print(f'Connection error: {e}')
            return render(request, 'event/event_video_not_found.html')
    else:
        return render(request, 'login/not_logged_in.html')


def __parse_availability(times):
    times = times.split(',')
    available_days = []
    for time in times:
        if '-' in time:
            period = time.split('-')
            start_time = __trim_date(period[0])
            end_time = __trim_date(period[1])
            start_time = datetime.strptime(start_time, '%d.%m.%y')
            end_time = datetime.strptime(end_time, '%d.%m.%y')
            while start_time <= end_time:
                available_days.append(start_time.strftime('%d-%m-%Y'))
                start_time += timedelta(days=1)
        else:
            time = __trim_date(time)
            single_day = datetime.strptime(time, '%d.%m.%y')
            available_days.append(__trim_date(single_day.strftime('%d-%m-%Y')))
    return available_days


def register_for_event(request, event_id):
    availability_form = AvailabilityForm()
    if request.user.is_authenticated:
        if request.method == "POST":
            availability_form = AvailabilityForm(request.POST)
            if availability_form.is_valid():
                msg = availability_form.save(commit=False)
                availability = __parse_availability(msg.availability)
                if availability:
                    event = Event.objects.get(id=event_id)
                    event.employees.add(request.user.employee)
                    event.save()
                for time in availability:
                    msg = AvailabilityMessage()
                    msg.employee = request.user.employee
                    msg.event = Event.objects.get(id=event_id)
                    msg.availability = time
                    msg.save()

                return redirect('list_events')
        return render(request, 'availability/availability_form.html',
                      {'availability_form': availability_form})
    else:
        return render(request, 'login/not_logged_in.html')


def discard_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.employees.remove(request.user.employee)
    event.save()
    AvailabilityMessage.objects.filter(employee=request.user.employee, event=event).delete()
    return redirect('list_events')


def availability_success(request):
    return render(request, 'availability/availability_success.html')


def list_availability(request):
    if request.user.is_authenticated:
        availability_times = AvailabilityMessage.objects.all()
        availability_list = """
            <h1>Availability times</h1>
            <ul>
        """

        event_ids = availability_times.values_list('event', flat=True).distinct()
        availability_list += f'<ol>'
        for event_id in event_ids:
            company_event = Event.objects.get(id=event_id)
            availability_list += f'<li><b>{company_event.name}</b></li>'
            availability_list += f'<ul>'
            event_availability_time = availability_times.filter(
                event=company_event,
                employee=request.user.employee)
            for time in event_availability_time:
                availability_list += f'<li>{time.availability}</li>'
            availability_list += f'</ul>'
            availability_list += f'<br>'
        availability_list += '</ol>'
        response = availability_list
        response += f'<br>'
        response += f'<a href="/logout">Logout</a>'
        return HttpResponse(response)
    else:
        return render(request, 'login/not_logged_in.html')


def delete_employees(request):
    Employee.objects.all().delete()
    return HttpResponse('<h1>Employee registrations deleted.</h1>')


def delete_users(request):
    return HttpResponse('<h1>User registrations deleted.</h1>')
