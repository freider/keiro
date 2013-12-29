from django.db import models


class Record(models.Model):
    date = models.DateTimeField()
    revision = models.CharField(max_length=42)  # git revision
    scenario = models.CharField(max_length=100)
    scenario_parameter = models.IntegerField(null=True)
    agent = models.CharField(max_length=100)
    agent_parameter = models.IntegerField(null=True)
    view_range = models.FloatField()
    seed = models.IntegerField()
    timestep = models.FloatField()
    collisions = models.IntegerField()
    avg_iteration_time = models.FloatField()
    max_iteration_time = models.FloatField()
    min_iteration_time = models.FloatField()
    completion_time = models.FloatField()

    def __unicode__(self):
        return "Scenario %s with agent %s" % (self.scenario, self.agent)
