import sys
import logging

from PyQt5 import QtWidgets
from main_window import MainWindow
from logger_builder import get_logger


logger = get_logger(__name__)


def main():
	logger.debug("Starting the programm")
	app = QtWidgets.QApplication(sys.argv)
	mw = MainWindow()
	mw.show()
	exec = app.exec()
	logger.debug("Programm was stoped")
	sys.exit(exec)

	# print(PyQt5.QtWidgets.QStyleFactory.keys())


if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		logging.exception(f"Type: {type(e)}, Description: {e}")
	
	



