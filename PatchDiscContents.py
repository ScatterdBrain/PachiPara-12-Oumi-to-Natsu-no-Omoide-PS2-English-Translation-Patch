import sys
import os
from python_scripts.ReinsertText import main as reinsert_text
from python_scripts.ReinsertFont import main as reinsert_font

work_dir = os.getcwd()
reinsert_text(work_dir)
reinsert_font(work_dir)

input('Press Enter to close.')
sys.exit()
