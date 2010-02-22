from django.db import models
import datetime

class Run(models.Model):
	date = models.DateTimeField()
	scenario = models.CharField(max_length = 100)
	agent = models.CharField(max_length = 100)
	seed = models.IntegerField()
	timestep = models.FloatField()
	collisions = models.IntegerField()
	avg_iteration_time = models.FloatField()
	max_iteration_time = models.FloatField()
	min_iteration_time = models.FloatField()
	completion_time = models.FloatField()
	
	def __unicode__(self):
		return "Scenario %s with agent %s"%(self.scenario_name, self.ai_name)
	