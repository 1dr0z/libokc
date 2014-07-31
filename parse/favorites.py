from libokc.parse.base.paginated import BasePaginated
from libokc.parse.helpers import has_class
import re

class Favorites(BasePaginated):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'https://www.okcupid.com/favorites'

    def get_next_page_link(self, tree):
        try:
            return tree.xpath(".//*[contains(@class, 'pages')]//*[contains(@class, 'next')]//a/@href")[0]
        except IndexError:
            return None

    def has_next_page(self, tree):
        next_btn = tree.xpath(".//*[contains(@class, 'pages')]//*[contains(@class, 'next')]")[0]
        return not has_class(next_btn, 'disabled')

    def iter_element(self, tree):
        return (elem for elem in tree.iterfind(".//div[@class='user_list']//div")
                if has_class(elem, 'user_row_item'))

    def parse_element(self, element):
        info = element.xpath(".//div[@class='profile_info']")[0]
        name = info.xpath(".//*[@class='name']/text()")[0]
        age = info.xpath(".//*[@class='age']/text()")[0]
        location = info.xpath(".//*[@class='location']/text()")[0]

        id_raw = element.xpath(".//*[contains(@class, 'star-rating')]/@id")[0]
        id = id_raw.replace('user_row_rating_', '')

        rating_raw = element.xpath(".//*[@class='current-rating']/@style")[0]
        rating_re = re.match(r'[Ww]idth\s?:\s?(\d+)%', rating_raw).group(1)
        rating = 5 * (float(rating_re) / 100)

        match_raw = element.xpath(".//*[@class='percentage']/text()")[0]
        match = match_raw.replace('%', '')

        gender_raw = element.xpath(".//input[@data-gender]/@data-gender")[0]
        gender = {'1': 'M', '2': 'F'}[gender_raw]

        return {
            'userid': id,
            'name': name,
            'age': int(age),
            'location': location,
            'rating': rating,
            'match': float(match),
            'gender': gender,
            'favorite': True,
        }