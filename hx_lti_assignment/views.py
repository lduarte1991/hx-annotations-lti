from hx_lti_assignment.forms import AssignmentForm, AssignmentTargetsForm, AssignmentTargetsFormSet
from hx_lti_assignment.models import Assignment, AssignmentTargets
from hx_lti_initializer.utils import debug_printer
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
import uuid


@login_required
def create_new_assignment(request):
    """
    """
    debug = "Nothing"
    form = ""
    if request.method == "POST":
        targets_form = AssignmentTargetsFormSet(request.POST)
        if targets_form.is_valid():
            assignment_targets = targets_form.save(commit=False)
            targets = 'assignment_objects=' + str(assignment_targets[0].target_object.id)
            for x in range(len(assignment_targets)-1):
                targets += '&' + 'assignment_objects=' + str(assignment_targets[x+1].target_object.id)
            post_values = QueryDict(targets, mutable=True)
            post_values.update(request.POST)
            form = AssignmentForm(post_values)
            if form.is_valid():
                assignment = form.save(commit=False)
                random_id = uuid.uuid4()
                assignment.assignment_id = str(random_id)
                assignment.save()
                for at in assignment_targets:
                    at.assignment = assignment
                    at.save()
                assignment.save()
                messages.success(request, 'Assignment was successfully created!')
                return redirect('hx_lti_initializer:course_admin_hub')
            else:
                target_num = len(assignment_targets)
                debug = "Assignment Form is NOT valid" + str(request.POST) + "What?"
                debug_printer(form.errors)
        else:
            target_num = len(assignment_targets)
            form = AssignmentForm(request.POST)
            debug = "Targets Form is NOT valid: " + str(request.POST)
            debug_printer(targets_form.errors)

    else:
        form = AssignmentForm()
        targets_form = AssignmentTargetsFormSet()
        target_num = 0
    return render(
        request,
        'hx_lti_assignment/create_new_assignment.html',
        {
            'form': form,
            'targets_form': targets_form,
            'user': request.user,
            'number_of_targets': target_num,
            'debug': debug
        }
    )

@login_required
def edit_assignment(request, id):
    """
    """
    assignment = get_object_or_404(Assignment, pk=id)
    target_num = len(AssignmentTargets.objects.filter(assignment=assignment))
    debug = 'Debug:\n\nAssignment Objects:\n'
    for obj in assignment.assignment_objects.all():
        debug += str(obj) + '\n'
    if request.method == "POST":
        targets_form = AssignmentTargetsFormSet(request.POST, instance=assignment)
        targets = 'id=' + id + '&assignment_id=' + assignment.assignment_id
        if targets_form.is_valid():
            assignment_targets = targets_form.save(commit=False)
            changed=False
            debug += str(request.POST)
            debug += str(assignment_targets)
            if len(targets_form.deleted_objects) > 0:
                debug += "Trying to delete a bunch of assignments\n"
                for del_obj in targets_form.deleted_objects:
                    del_obj.delete()
                changed=True
            debug += "\nLength of Targets to be added/edited: " + str(len(assignment_targets)) + "\n"
            if len(assignment_targets) > 0:
                debug += "Trying to add a bunch of assignments\n"
                for at in assignment_targets:
                    at.save()
                changed=True
            if changed:
                targets_form = AssignmentTargetsFormSet(instance=assignment)
        for targs in assignment.assignment_objects.all():
            targets += '&assignment_objects=' + str(targs.id)
        post_values = QueryDict(targets, mutable=True)
        post_values.update(request.POST)
        debug += str(targets)
        form = AssignmentForm(post_values, instance=assignment)
        if form.is_valid():
            assign1 = form.save(commit=False)
            assign1.save()
            messages.success(request, 'Assignment was successfully created!')
            return redirect('hx_lti_initializer:course_admin_hub')
    else:
        targets_form = AssignmentTargetsFormSet(instance=assignment)
        form = AssignmentForm(instance=assignment)

    return render(
        request,
        'hx_lti_assignment/create_new_assignment.html',
        {
            'form': form,
            'targets_form': targets_form,
            'number_of_targets': target_num,
            'user': request.user,
            'debug': debug,
        }
    )