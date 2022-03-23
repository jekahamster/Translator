import googletrans


class Translator:
	def __init__(self, translator=googletrans.Translator()):
		self._translator = translator

	def translate(self, text, lang_src="en", lang_dst="ru"):
		return self._translator.translate(text, src=lang_src, dest=lang_dst).text
