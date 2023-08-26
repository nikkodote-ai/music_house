from django.db import models
import string
import random
#FAT MODELS, THIN VIEWS meaning put most of your logic in your MODELS

def generate_unique_code():
    length = 6

    while True:
        code = "".join(random.choices(string.ascii_uppercase, k = length))
        #now make query database if it is unique
        if Room.objects.filter(code = code).count() == 0:
            break
        
    return code

# Create your models here.
# a layer of abstraction

#each object is a table
class Room(models.Model):
    #define fields, and default, important not to call generate_unique_code
    code = models.CharField(max_length=8, default = generate_unique_code, unique= True) #variable = data_type(contraints)
    #keep track who the host
    host = models.CharField(max_length=50, unique=True)
    guest_can_pause = models.BooleanField(null=False, default=False)
    votes_to_skip = models.IntegerField(null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    #you can also add method