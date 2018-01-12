
import warnings
import requests
from item_dict import * 
import requests
import urllib
from termcolor import colored, cprint
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")
print_blue_bold = lambda x: cprint(x, 'blue', attrs=['bold'])
print_green = lambda x: cprint(x, 'green')
print_red_bold = lambda x: cprint(x, 'red', attrs=['bold'], end="")
print_red_bold_nl = lambda x: cprint(x, 'red', attrs=['bold'])
print_bold = lambda x: cprint(x, 'grey', attrs=['bold'])
print_green_bold = lambda x: cprint(x, 'green', attrs=['bold'], end="")
def get_JSON(item_id):
	try:
		request = requests.get("https://api.rsbuddy.com/grandExchange?a=guidePrice&i="+str(item_id), verify=True, timeout=5)
		request_json = request.json()
		return request_json
	except requests.exceptions.HTTPError as errh:
		print("Http Error: ", errh)
		return {}
	except requests.exceptions.ConnectionError as errc:
		print("Error Connecting: ", errc)
		return {}
	except requests.exceptions.Timeout as errt:
		print("Timeout Error: ",errt)
		return {}
	except requests.exceptions.RequestException as err:
		print("OOPS: Something went wrong ", err)
		return {}
	except:
		print("404 Error: Unable to request JSON")
		return {}

def id_to_item_name(item_id):
	return id_name_dict[item_id]

def index_binary_search(lst, val, first, last):
	mid = (first + last)//2
	if last - first == 1:
		if abs(lst[last] - val) > abs(lst[first] - val):
			return first
		return last
	if val < lst[mid]:
		return index_binary_search(lst, val, first, mid)
	else:
		return index_binary_search(lst, val, mid, last)