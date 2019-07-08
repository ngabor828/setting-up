from django.db import models
from django.forms.models import model_to_dict

import json

class Board(models.Model):
    board_id = models.IntegerField(default=0)
    board_name = models.CharField(max_length=200)

    @classmethod
    def create(cls, board_id, board_name):
        return cls(board_id=board_id, board_name=board_name)

    def toJSON(self):
        dict_obj = model_to_dict(self)
        return json.dumps(dict_obj)
