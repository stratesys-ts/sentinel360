import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.timesheet.models import Timesheet, TimeEntry, Activity
from apps.projects.models import Project, Task
from django.test import RequestFactory
from apps.timesheet.views import TimesheetActionView

User = get_user_model()

def run():
    # Setup data
    user, _ = User.objects.get_or_create(username='test_user_repro', defaults={'email': 'test@example.com'})
    project, _ = Project.objects.get_or_create(name='Test Project', defaults={'status': 'IN_PROGRESS', 'start_date': date(2025, 1, 1), 'end_date': date(2025, 12, 31)})
    activity, _ = Activity.objects.get_or_create(name='Test Activity')
    
    start_date = date(2026, 1, 12)
    timesheet, _ = Timesheet.objects.get_or_create(user=user, start_date=start_date, defaults={'end_date': start_date + timedelta(days=6)})
    
    # Clear existing entries
    TimeEntry.objects.filter(timesheet=timesheet).delete()
    
    # 1. Simulate "Add Row" (Anchor creation)
    print("--- Simulating Add Row ---")
    TimeEntry.objects.create(
        timesheet=timesheet,
        project=project,
        activity=activity,
        date=start_date,
        hours=0
    )
    print(f"Entries after add_row: {TimeEntry.objects.filter(timesheet=timesheet).count()}")
    
    # 2. Simulate "Save Grid"
    print("--- Simulating Save Grid ---")
    factory = RequestFactory()
    
    # Construct POST data
    # Simulate inputs for 7 days
    # Key format: hours_{proj}_{task}_{act}_{date}
    # Task is None
    
    post_data = {
        'action': 'save_grid',
    }
    
    current_date = start_date
    for i in range(7):
        # Use 'None' string for task as template does
        key = f"hours_{project.id}_None_{activity.id}_{current_date.strftime('%Y-%m-%d')}"
        # Set some hours for the second day (index 1), 0 for others
        val = "8" if i == 1 else "0"
        post_data[key] = val
        current_date += timedelta(days=1)
        
    print(f"POST data keys sample: {list(post_data.keys())[0]} ...")
    
    request = factory.post(f'/timesheet/{timesheet.pk}/action/', post_data)
    request.user = user
    
    view = TimesheetActionView()
    view.request = request
    view.kwargs = {'pk': timesheet.pk}
    
    # Mock get_object
    view.get_object = lambda: timesheet
    
    # Run the post method
    response = view.post(request)
    
    print(f"Response status: {response.status_code}")
    
    # Check entries
    entries = TimeEntry.objects.filter(timesheet=timesheet).order_by('date')
    print(f"Entries after save_grid: {entries.count()}")
    for entry in entries:
        print(f"  {entry.date}: {entry.hours} (ID: {entry.id})")

    # Verify persistence
    if entries.count() < 7:
        print("FAILURE: Entries missing!")
    else:
        day_2 = entries.filter(date=start_date + timedelta(days=1)).first()
        if day_2 and day_2.hours == 8:
            print("SUCCESS: Hours saved correctly.")
        else:
            print(f"FAILURE: Hours not saved correctly. Expected 8, got {day_2.hours if day_2 else 'None'}")

if __name__ == '__main__':
    run()
