from django.db import models
import datetime
class Run(models.Model):
	date = models.DateTimeField()
	scenario_name = models.CharField(max_length = 100)
	seed = models.IntegerField()
	ai_name = models.CharField(max_length = 100)
	timestep = models.FloatField()
	collisions = models.IntegerField()
	avg_iteration_time = models.FloatField()
	
	# time to completion
	# date
	# max_iteration_time = models.FloatField()
	# travelled_distance = models.FloatField()
	def __unicode__(self):
		return "Scenario %s with agent %s"%(self.scenario_name, self.ai_name)
	