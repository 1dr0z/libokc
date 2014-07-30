class Profile(object):
    def __init__(self, userid=None, name=None, age=None,
                 location=None, match=None, rating=None,
                 gender=None, favorite=None):
        self._id = userid
        self._name = name
        self._age = age
        self._location = location
        self._match = match
        self._rating = rating
        self._gender = gender
        self._favorite = favorite

    ## TODO: If the below properties are not set at the time they are accessed, populate all basic profile data
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def age(self):
        return self._age

    @property
    def location(self):
        return self._location

    @property
    def match(self):
        return self._match

    @property
    def rating(self):
        return self._rating

    @property
    def gender(self):
        return self._gender

    @property
    def is_favorite(self):
        return self._favorite


    ## TODO: write generator to iterate over questions
    def questions(self, **kwargs):
        """
        i_care=None, they_care=None, disagree=None,
        unanswered=None, notes=None, sex=None, dating=None,
        lifestyle=None, ethics=None, religion=None, other=None

        :param kwargs:
        :return:
        """
        return []

    def __str__(self):
        return '<Profile of {0}>'.format(self._name)