import dataclasses
import logging
import urllib.parse

import mal
import peewee
import wikipediaapi

import models
import my_secrets


@dataclasses.dataclass
class EntityInfo:
    title: str
    link: str
    creator: str
    note: str
    created_at: str
    db_id: str


class WikiHelper:

    @staticmethod
    def find_keywords(page, keywords):
        page_summary = page.summary.lower()

        for keyword in keywords:
            if keyword not in page_summary:
                return False

        return True

    @staticmethod
    def get_english_page(page_link):
        if "wikipedia.org/wiki/" not in page_link:
            raise Exception("Not a wikipedia link")

        info = page_link.split("//")[1].split("/")
        title = urllib.parse.unquote(info[2])
        language = info[0].split(".")[0]

        wiki_wiki = wikipediaapi.Wikipedia(user_agent=my_secrets.user_agent, language=language)
        page = wiki_wiki.page(title)

        if page.language != "en":
            page = page.langlinks.get("en")

        if not page.exists():
            raise Exception("Wikipedia page does not exist")

        return page


class WatchListRecord:
    type_name = "type_name was not set"
    cache = {}

    def __init__(self, db_record):
        self.information_url = db_record.information_url
        self.creator = db_record.creator
        self.note = db_record.note

        self.db_id = db_record.id
        self.status = db_record.status
        self.created_at = db_record.created_at

    def get_from_cache(self, key):
        result = self.__class__.cache.get(key)
        return result if result else self.set_cache(key)

    def set_cache(self, key):
        value = self.value_from_key(key)
        self.__class__.cache[key] = value

        return value

    def value_from_key(self, key):
        raise NotImplementedError(f"Function value_from_key was not implemented for type {self.type_name}")

    @staticmethod
    def validate_link(information_url):
        raise NotImplementedError(f"Function validate link was not implemented")

    def get_info(self):
        raise NotImplementedError(f"Function get_info for type {self.type_name} was not implemented")

    def __str__(self):
        record_info = self.get_info()

        text_link = f"[{record_info.title}]({record_info.link})"
        creator = record_info.creator
        created_at = f"{record_info.created_at:%B %#d}"
        note = f"with note: {record_info.note}" if record_info.note else ""

        str_information = f"{text_link} - added by {creator} on {created_at} {note}\n"

        return str_information


class AnimeWatchListRecord(WatchListRecord):
    type_name = 'anime'

    cache = {}

    def __init__(self, db_record):
        super().__init__(db_record)

        self.mal_title = self.get_from_cache(list(reversed(self.information_url.split('/')))[0])

    def value_from_key(self, key):
        return mal.Anime(key)

    @staticmethod
    def validate_link(information_url):
        info_link_list = list(information_url.split('/'))
        if not (info_link_list[3] == "anime") or not ("myanimelist" in info_link_list[2]):
            raise Exception("Unsupported link for type anime")
        return "/".join(info_link_list[0:5])

    def get_info(self):
        return EntityInfo(
            title=self.mal_title.title_english or self.mal_title.title,
            link=self.information_url,
            creator=self.creator,
            created_at=self.created_at,
            note=self.note,
            db_id=self.db_id

        )


class FilmWatchListRecord(WatchListRecord):
    type_name = 'film'

    def __init__(self, db_record):
        super().__init__(db_record)
        self.page = self.get_from_cache(self.information_url)

    def value_from_key(self, key):
        return WikiHelper.get_english_page(key)

    @staticmethod
    def validate_link(information_url):
        page = WikiHelper.get_english_page(information_url)

        is_film_keywords = ['film', 'directed by']
        is_cartoon_keywords = ['animated']
        banned_keywords = ['soundtrack']

        is_film = WikiHelper.find_keywords(page, is_film_keywords)
        is_cartoon = WikiHelper.find_keywords(page, is_cartoon_keywords)
        is_have_banned_keywords = WikiHelper.find_keywords(page, banned_keywords)

        if (not (is_film or is_cartoon)) or is_have_banned_keywords:
            raise Exception("Not a film related wikipedia page, if you think it is then contact perite")

        return page.canonicalurl

    def get_info(self):
        return EntityInfo(
            title=self.page.title,
            link=self.information_url,
            creator=self.creator,
            note=self.note,
            created_at=self.created_at,
            db_id=self.db_id

        )


class TvShowWatchListRecord(WatchListRecord):
    type_name = 'tv-show'

    def __init__(self, db_record):
        super().__init__(db_record)
        self.page = self.get_from_cache(self.information_url)

    def value_from_key(self, key):
        return WikiHelper.get_english_page(key)

    @staticmethod
    def validate_link(information_url):
        page = WikiHelper.get_english_page(information_url)

        is_television_series_keywords = ['television series']
        is_sitcom_keywords = ['sitcom']
        is_has_author_keywords = ['created by']
        banned_keywords = ['soundtrack']

        is_television_series = WikiHelper.find_keywords(page, is_television_series_keywords)
        is_sitcom = WikiHelper.find_keywords(page, is_sitcom_keywords)
        is_has_author = WikiHelper.find_keywords(page, is_has_author_keywords)
        is_have_banned_keywords = WikiHelper.find_keywords(page, banned_keywords)

        if (not (is_television_series or is_sitcom)) or (not is_has_author) or is_have_banned_keywords:
            raise Exception("Not a tv-show related wikipedia page, if you think it is then contact perite")

        return page.canonicalurl

    def get_info(self):
        return EntityInfo(
            title=self.page.title,
            link=self.information_url,
            creator=self.creator,
            note=self.note,
            created_at=self.created_at,
            db_id=self.db_id

        )


class TypesAndRecordsManagers:
    types = []

    @staticmethod
    def set_types(types):
        TypesAndRecordsManagers.types = types

    @staticmethod
    def get_type(type_name):
        type_class = list(filter(lambda type_class: type_class.type_name == type_name, TypesAndRecordsManagers.types))
        if not type_class:
            raise Exception("Unsupported type")

        return type_class[0]

    @staticmethod
    def get_db_records_of_type(type_name):
        db_records_of_type = list(models.WatchListRecord.select().where(
            (models.WatchListRecord.type_name == type_name) & (models.WatchListRecord.status != "watched"))
                                  .order_by(models.WatchListRecord.created_at.asc()))

        return db_records_of_type

    @staticmethod
    def all_db_records():
        return list(models.WatchListRecord.select().where(models.WatchListRecord.status != "watched"))

    @staticmethod
    def add_to_watchlist(**information):
        try:
            models.WatchListRecord.create(**information)
        except Exception as e:
            logging.critical(f"Error during saving to DB : {e}")
            raise Exception(f"Could not save to DB for some reason.\n\nTechnical error : {e}")

    @staticmethod
    def get_db_record_by_id(id):
        record = models.WatchListRecord.get_or_none(models.WatchListRecord.id == id)
        if not record:
            raise Exception(f"Record with id {id} does not exists")

        return record

    @staticmethod
    def get_random_db_record(type_name):
        query = models.WatchListRecord.select()

        if type_name:
            query = query.where(models.WatchListRecord.type_name == type_name)

        record = query.order_by(peewee.fn.Random()).limit(1).first()
        if record is None:
            raise Exception("No records found of this type")

        return record

    @staticmethod
    def db_record_to_record(type_class, db_record):
        try:
            return type_class(db_record)
        except Exception as e:
            msg = f"Something wrong with link for type {type_class.type_name}: {db_record.information_url} (id:{db_record.id})"
            logging.critical(msg)
            return None
