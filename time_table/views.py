from django.http import request
from django.shortcuts import render, redirect
from . forms import *
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .render import Render
from django.views.generic import View


# Create your views here.


class Data:
    def __init__(self):
        self._rooms = Room.objects.all()
        self._meetingTimes = MeetingTime.objects.all()
        self._instructors = Teacher.objects.all()
        self._units = Unit.objects.all()
        self._levels = Level.objects.all()

    def get_rooms(self): return self._rooms
    def get_instructors(self): return self._instructors
    def get_units(self): return self._units
    def get_levels(self): return self._levels
    def get_meetingTimes(self): return self._meetingTimes

class Class:
    def __init__(self, id, unit, level):
        self.id = id
        self.unit = unit
        self.level = level
        self.instructor = None
        self.meeting_time = None
        self.room = None

    def set_instructor(self, instructor): self.instructor = instructor
    def set_meetingTime(self, meetingTime): self.meeting_time = meetingTime
    def set_room(self, room): self.room = room

def initialize(self):
    self._classes = []
    levels = data.get_levels()
    for level in levels:
        units = Unit.objects.filter(level=level)
        for unit in units:
            eligible_teachers = Teacher.objects.filter(course=unit.course, is_approved=True)
            if not eligible_teachers.exists():
                continue  # Skip if no eligible teacher
            new_class = Class(self._classNumb, unit, level)
            self._classNumb += 1
            new_class.set_meetingTime(rnd.choice(data.get_meetingTimes()))
            new_class.set_room(rnd.choice(data.get_rooms()))
            new_class.set_instructor(rnd.choice(eligible_teachers))
            self._classes.append(new_class)
    return self


def calculate_fitness(self):
    self._numberOfConflicts = 0
    classes = self.get_classes()
    for i in range(len(classes)):
        for j in range(i + 1, len(classes)):
            if classes[i].meeting_time == classes[j].meeting_time:
                if classes[i].room == classes[j].room:
                    self._numberOfConflicts += 1
                if classes[i].instructor == classes[j].instructor:
                    self._numberOfConflicts += 1
                if classes[i].level == classes[j].level:
                    self._numberOfConflicts += 1
    return 1 / (1.0 * self._numberOfConflicts + 1)

def context_manager(schedule):
    classes = schedule.get_classes()
    context = []
    for c in classes:
        context.append({
            "level": c.level.name,
            "unit": c.unit.name,
            "course": c.unit.course.name,
            "room": f'{c.room.r_number} ({c.room.seating_capacity})',
            "instructor": f'{c.instructor.first_name} {c.instructor.last_name} ({c.instructor.staff_number})',
            "meeting_time": f"{c.meeting_time.day} {c.meeting_time.time}",
        })
    return context


def timetable(request):
    population = Population(POPULATION_SIZE)
    generation_num = 0
    population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
    geneticAlgorithm = GeneticAlgorithm()

    while population.get_schedules()[0].get_fitness() != 1.0:
        generation_num += 1
        population = geneticAlgorithm.evolve(population)
        population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)

    best_schedule = population.get_schedules()[0]

    # Clear previous sessions if needed
    Session.objects.all().delete()

    # Save new schedule
    for c in best_schedule.get_classes():
        Session.objects.create(
            unit=c.unit,
            instructor=c.instructor,
            room=c.room,
            meeting_time=c.meeting_time,
            level=c.level
        )

    return render(request, 'gentimetable.html', {
        'schedule': context_manager(best_schedule),
        'levels': Level.objects.all(),
        'times': MeetingTime.objects.all(),
    })
