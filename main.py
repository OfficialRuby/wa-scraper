from utils.helper_class import WAScrapper
was = WAScrapper()
was.SCROLL_COUNT = 10
was.fetch_messages()
