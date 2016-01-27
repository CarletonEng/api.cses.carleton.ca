import os
import sys

os.environ["CSESAPI_DEBUG"] = "TRUE"

sys.path[0:0] = [os.path.dirname(os.path.realpath(__file__))+"/../"]
