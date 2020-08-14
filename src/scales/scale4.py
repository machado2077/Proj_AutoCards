#!venv/bin/python3

import os

from selenium.webdriver import Firefox

from src.clss.autoFlashCards import AutoFlashCards
from src.clss.cardDeliverers import SeleniumAnkiBot
from src.clss.cardWriter import DictBasedCardWriter
from src.clss.imageSources import GoogleDriveSource
from src.clss.TextExtractors import GoogleVision
from src.clss.sourceAdmins import ImageSourceAdmin
from src.clss.sourceAdmins import ShelveCardAdmin
from src.clss.sourceAdmins import ShelveIdAdmin
from src.funcs.textFunc import get_from_txt

path = os.path.join(os.getcwd(), 'data.json')
folder_path = login_path = path
drive_folder_target = 'Legendas'

writer = DictBasedCardWriter()
id_admin = ShelveIdAdmin('db', 'drive_file_id')
img_source = GoogleDriveSource(drive_folder_target, id_admin)
text_extractor = GoogleVision()

deliver = SeleniumAnkiBot(Firefox, login_path)
img_admin = ImageSourceAdmin(img_source, writer, text_extractor)
db = ShelveCardAdmin('db', 'cards')

automaton = AutoFlashCards(deliver, img_admin, db)