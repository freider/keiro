from django.db import models
import datetime
class Run(models.Model):
	scenario_name = models.CharField(max_length = 100)
	seed = models.IntegerField()
	ai_name = models.CharField(max_length = 100)
	crowd_size = models.IntegerField()
	collisions = models.IntegerField()
	timestep = models.FloatField()
	avg_iteration_time = models.FloatField()
	
	# time to completion
	# date
	# max_iteration_time = models.FloatField()
	# travelled_distance = models.FloatField()
	def __unicode__(self):
		return "Scenario %s with crowd_size = %d"%(self.scenario, self.crowd_size)
	