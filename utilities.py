import random
import math


def check_within(x, y, a1, b1, a2, b2):
	if not a1 <= x <= a2:
		return False
	if not b1 <= y <= b2:
		return False
	return True