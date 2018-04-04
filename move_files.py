import yaml
import io
from datetime import date, timedelta
import os
import shutil
import re
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler  


with io.open('move_files.yaml', 'r') as stream:
	config = yaml.load(stream)



def prev_weekday (adate):
	adate -= timedelta(days=1)
	while adate.weekday() > 4: # Mon-Fri are 0-4
		adate -= timedelta(days=1)
	return adate

def dir_exists(s):
	return os.path.isdir(s) and os.path.exists(s)

def move_files(src_d, dst_d, files, suffix):
	# regular expressions are being defined in re package
	# after importing the re module, all re.compile() to create a Regex object
	# passing re.VERBOSE for the second argument will allow whitespace and comments
	# in the regex string to make it more readable
	# the '?' has two different meanings
	# 1. when it follows a character or a group it is a quantifier, matching 0 or 1 occurence preceeding
	# 2. when it follows a quantifier it modifies the matching behavior of that quantifier making it match lazy/ungreedy
	filepattern = "^(.*?)(\..*)$"

	for f in files:
		if os.path.exists(src_d+f):
			regex = re.search(filepattern, f)
			src_f = regex.group(1)
			f_ext = regex.group(2)
			dst_f = dst_d+src_f+suffix+f_ext
			shutil.move(src_d+f, dst_f)
		else:
			print ("File {0} does not exist".format(src_d+f))

def main():
	#read in the config
	from_dir = config["from_dir"]
	to_dir = config["to_dir"]
	src_files = config["src_files"]
	date_format = config["date_format"]

	#calculate previous BD
	prev_week_date = prev_weekday(date.today())
	prev_week_date = prev_week_date.strftime(date_format)

	if not dir_exists(from_dir) or not dir_exists(to_dir):
		print ("FROM_DIR {0} EXISTS: {1}\nTO_DIR {2} EXISTS: {3}".format(from_dir,dir_exists(from_dir),to_dir,dir_exists(to_dir)))
		exit(1)

	# move_files(from_dir, to_dir, src_files, prev_week_date)
	scheduler = BlockingScheduler()
	scheduler.add_job(move_files, 'interval', seconds=5, args=[from_dir, to_dir, src_files, prev_week_date])
	scheduler.start()
	
if __name__ == "__main__":
	main()