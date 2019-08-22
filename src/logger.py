import os
import logging
from src.static import log_dir, log_file


# Don't run if can't create logging dir
# Nothing will work without logging
if not os.path.exists(log_dir):
    try:
        os.mkdir(log_dir)
    except Exception:
        print("CRITICAL ERROR: can't create log directory '" + log_dir + "'. Exit")
        sys.exit()


logging_filename = log_file

logger = logging.getLogger('lftable')
logger.setLevel(logging.DEBUG)

filehandler = logging.FileHandler(filename=logging_filename)
filehandler.setFormatter(logging.Formatter('%(filename)s [LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'))
logger.addHandler(filehandler)

