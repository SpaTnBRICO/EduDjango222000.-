import random as rnd
from django.shortcuts import render
from .forms import *
from useraccess.models import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .render import Render
from django.views.generic import View

# Genetic Algorithm Constants
POPULATION_SIZE = 9
NUMB_OF_ELITE_SCHEDULES = 1
TOURNAMENT_SELECTION_SIZE = 3
MUTATION_RATE = 0.05

# ---------- Data Wrapper ----------
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

# ---------- Class Definition ----------
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

# ---------- Schedule ----------
class Schedule:
    def __init__(self):
        self._data = Data()
        self._classes = []
        self._classNumb = 0
        self._fitness = -1
        self._numberOfConflicts = 0
        self.initialize()

    def initialize(self):
        self._classes = []
        for level in self._data.get_levels():
            units = Unit.objects.filter(level=level)
            for unit in units:
                eligible_teachers = Teacher.objects.filter(course=unit.course, is_approved=True)
                if not eligible_teachers.exists():
                    continue
                new_class = Class(self._classNumb, unit, level)
                self._classNumb += 1
                new_class.set_meetingTime(rnd.choice(self._data.get_meetingTimes()))
                new_class.set_room(rnd.choice(self._data.get_rooms()))
                new_class.set_instructor(rnd.choice(eligible_teachers))
                self._classes.append(new_class)
        return self

    def get_classes(self): return self._classes

    def get_fitness(self):
        if self._fitness == -1:
            self._fitness = self.calculate_fitness()
        return self._fitness

    def calculate_fitness(self):
        self._numberOfConflicts = 0
        for i in range(len(self._classes)):
            for j in range(i + 1, len(self._classes)):
                if self._classes[i].meeting_time == self._classes[j].meeting_time:
                    if self._classes[i].room == self._classes[j].room:
                        self._numberOfConflicts += 1
                    if self._classes[i].instructor == self._classes[j].instructor:
                        self._numberOfConflicts += 1
                    if self._classes[i].level == self._classes[j].level:
                        self._numberOfConflicts += 1
        return 1 / (1.0 * self._numberOfConflicts + 1)

# ---------- Population ----------
class Population:
    def __init__(self, size):
        self._schedules = [Schedule() for _ in range(size)]

    def get_schedules(self):
        return self._schedules

# ---------- Genetic Algorithm ----------
class GeneticAlgorithm:
    def evolve(self, population):
        return self._mutate_population(self._crossover_population(population))

    def _crossover_population(self, pop):
        crossover_pop = Population(0)
        elite = pop.get_schedules()[:NUMB_OF_ELITE_SCHEDULES]
        crossover_pop.get_schedules().extend(elite)

        for i in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            parent1 = self._select_tournament_population(pop).get_schedules()[0]
            parent2 = self._select_tournament_population(pop).get_schedules()[0]
            child = self._crossover_schedule(parent1, parent2)
            crossover_pop.get_schedules().append(child)

        return crossover_pop

    def _mutate_population(self, pop):
        for i in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            if rnd.random() < MUTATION_RATE:
                pop.get_schedules()[i].initialize()
        return pop

    def _crossover_schedule(self, s1, s2):
        child = Schedule()
        for i in range(len(s1.get_classes())):
            if rnd.random() > 0.5:
                child.get_classes()[i] = s1.get_classes()[i]
            else:
                child.get_classes()[i] = s2.get_classes()[i]
        return child

    def _select_tournament_population(self, pop):
        tournament = Population(0)
        for _ in range(TOURNAMENT_SELECTION_SIZE):
            tournament.get_schedules().append(rnd.choice(pop.get_schedules()))
        tournament.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        return tournament

# ---------- Context Manager for Rendering ----------
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

# ---------- Main Timetable View ----------
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

    # Clear old schedule
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

    # Render to template
    return render(request, 'timetable.html', {
        'schedule': context_manager(best_schedule),
        'levels': Level.objects.all(),
        'times': MeetingTime.objects.all(),
    })
