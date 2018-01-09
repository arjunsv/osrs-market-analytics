print_blue_bold = lambda x: cprint(x, 'blue', attrs=['bold'])
print_green = lambda x: cprint(x, 'green')
print_red_bold = lambda x: cprint(x, 'red', attrs=['bold'])
print_bold = lambda x: cprint(x, 'grey', attrs=['bold'])

def get_JSON(item_id):
	try:
		json = requests.get("https://api.rsbuddy.com/grandExchange?a=guidePrice&i="+str(item_id)).json()
		return json
	except:
		print_red_bold("Error in JSON request")
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