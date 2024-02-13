<h1> Event management app (version 1.0) </h1>

<h2> Purpose </h2>

I've built this app with 3 goals in mind:
1. Refreshing and further strengthening my knowledge of Python gained
   in a past project at Zuhlke.
2. Do a deep dive for the first time into a Python framework. I've chosen
   Django since it seems to be the most popular one at the moment.
   It also seems to be aiming to be the go-to Python framework for
   performing backend integrations of AI technologies (such as the trendy LLMs).
3. Dual backend language application development - I've also wanted
   to build an application that uses both Python and Java in the backend
   (event scheduler is written in Python and event viewer is in Java).


<h2> Application usage </h2>

<p>
This app allows event organizers to determine the best timing for events so that they can ensure the highest possible attendance. This is achieved by collecting and processing availability data from registered users.
</p>

<p>
As a first step, employees can sign up for using this app by providing
employee details such as name and location and login credentials. Once
signed up, they can login to the app using their username and password.
</p>

<p>
Once logged in, a user can visualize the existing events and can register
for any of them by providing his/her availability. Users can also discard
events they're not interested in attending. If an event is discarded by
a user, it is not shown anymore in the list of current events for that user.
</p>

<p>
Currently, event scheduling can be done by any user by pressing the
'Preview schedules' button on the /events page. If more users are expected to enter availability in the future (and thus potentially change the best timing for the event), the user requesting the scheduling can clear the existing scheduling and can request a new scheduling at a later time when more users have entered their availability.
</p>

<p>
By clicking on the link 'Past events' on the /events page, users can
visualize the list of events that ended. Next to each event there is
a link, 'View recording' that allows the user to view the event recording, if one has been previously uploaded in the app. Please note,
video uploading is not available in this app version.
</p>


<h2> Technical description </h2>

<p>
The application is comprised of 2 modules: event-scheduler and event-viewer.
</p>

<h3> event-scheduler module </h3>

<p>
event-scheduler module is written in Python Django 5.0. As such, the overall architecture is MVT (Model-View-Template). 
</p>

<h4> Views </h4>

The routes, defined in the scheduler app, in urls.py, are the following:

<p>
1. /signup
   
   This route maps to signup view which displays the sign-up form for new users.
</p>

<p>
2. /login and /logout

   These are the routes that map to the login and logout views respectively.
</p>

<p>
3. /events

   This route maps to list_events view which renders the list of upcoming
   events where the logged in user is currently registered.
</p>

<p>
4. /events/register/<int:event_id>

   This route maps to register_for_event view. In this view, an availability form is displayed for users to enter their availability.
   Availability can be entered as single days (eg.: 20.01.2024) as well
   as an availability interval (eg.: 01.01.2024 - 20.01.2024 - in this case, use is available every day from the Jan. 1st to Jan. 20th).
   Example with mixed format availability: 
   01.02.2024, 10.02.2024 - 24.02.2024, 04.03.2024, 10.04.2024
</p>  

<p>
5. /events/discard/<int:event_id>

   This route maps to discard_event view. This view is invoked when the
   user clicks on the 'Discard' link next to a chosen event. It removes
   the logged in user from the registered participants of the selected
   event. As a consequence, when the list of events is re-rendered for
   the current user, the discarded event won't be visible anymore.
</p>

<p>
6. /events/add

   This route maps to add_event view. This view allows the logged in user
   to add a new event. Once the event is created, all the existing users
   within the company of the logged in user are automatically registered
   as potential attendeed of the event. As such, all users from the same
   company, can view the newly created event in the /events page.
</p>

<p>
7. /events/past_events

   This route maps to list_past_events view. This view renders all the
   events that have concluded. Similarly to the /events page, the events listed are those from the company of the logged in user.
</p>

<p>
8. /events/view/<int:event_id>

   This route maps to view_event view. This view makes a request to the
   video server hosted in the event-viewer module. The video server
   responds with the video recording corresponding to the event (event is
   identified by the path parameter 'event_id').
</p>

<p>
9. Other routes are available for: listing existing employees and
   application users, deleting registered employees as well as confirmation pages (for successful sign-up and successful entering of availability).
</p>

<h4> Models </h4>

<p>
   There are 3 models defined in models.py: the Employee, Event and AvailabilityMessage. The AvailabilityMessage model is used to store
   a date when a given user is available to attend a given event. The Employee model has a one to one relationship with the User model.
</p>

<p>
   Model instances are stored in MySql database. Model changes and
   related MySql schema alterations have been done using Django migrations. Migration history can be found at event_manager/scheduler/migrations. 
</p>

<h4> Templates </h4>

<p>
   The event-scheduler module has templates for the following:
   sign up, login, managing events (adding events, viewing events and
   recordings). These can be found in the 'templates' folder 
   (event_manager/scheduler/templates).
</p>

<h4> Forms </h4>
<p>
   There are 4 forms defined in forms.py: the UserForm, EmployeeForm,
   EventForm and AvailabilityForm. Each of those extends Django's forms.ModelForm.
</p> 

<p>
   1. User Form

   The UserForm is tied to Django's User model. This model is at the basis of Django's solution for authentication, authorization and secured logging capabilities. Since this model is part of the framework, it's not present in models.py. In terms of saving corresponding model data to the underlying MySql table, the user password is stored encrypted. This allows using the authenticate method from django.contrib.auth module to authenticate users.
   This method expects the raw password as input and the encrypted password to be stored in the User table. 
</p>

<p>
   2. Employee Form

   Together with the Employee and User models (that are tied via the one to one relationship), the EmployeeForm is used to create an inline formset called the EmployeeFormSet. This formset allows the capture of both employee and user data from within the same HTML form. By entering this data and then clicking the Submit button on the /signup page, the employee data will be saved to the Employee model and the user data (username and password) will be saved to the User model.
</p>

<h4> Static resources </h4>

<p>
   In the current version, when a user clicks on the 'View recording'
   link on the /past_events page, a HTTP GET request is sent to the video server in order to obtain the event recording. The response
   is saved as an MPEG4 video file in the static resources folder found at event_manager/scheduler/static/event_videos.
</p>

<h3> event-viewer module </h3>

<p>
   event-viewer module is written in Java Spring Boot 3.2. As such, the video server is a Spring Boot application that can be started by running the VideoStreamingApp class in the tech.events.streaming package. Video files are stored in the resources folder (in the /static/events subfolder) and are retrieved by the video controller (VideoController class) upon receiving HTTP GET requests. Configuration data such as video file path and file extension are stored in application.properties and the VideoConfiguration class,
   annotated with @ConfigurationProperties, automatically maps to the video service configuration data.
</p>