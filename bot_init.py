import os
import logging
from logging.handlers import TimedRotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.loggers import event

from table.methods import CitizensAppeals, EveningReport, MorningReport


KEY_PATH = os.getenv('KEY_PATH')
TABLE_KEY = os.getenv('TABLE_KEY')
OUR_ID = int(os.getenv('OUR_ID'))

handler = TimedRotatingFileHandler(filename='bot_log.log', 
                                   when='D', 
                                   interval=31, 
                                   backupCount=2
                                   )
logging.basicConfig(level=logging.INFO, 
					handlers=[handler], 
					format="%(asctime)s %(levelname)s %(message)s"
					)

event.setLevel(logging.ERROR)
logger = logging.getLogger('main_logger')
client_for_registration = CitizensAppeals(KEY_PATH, TABLE_KEY, 
                                          index_sheet=0, 
                                          logger=logger
                                          )
client_for_evening_report = EveningReport(KEY_PATH, TABLE_KEY, 
                                          index_sheet=0, 
                                          logger=logger, 
                                          dump_name='report_dump.txt'
                                          )
client_for_morning_report = MorningReport()

bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
bd = Dispatcher()