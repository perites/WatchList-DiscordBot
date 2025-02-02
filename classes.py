import dataclasses

import mal
import wikipediaapi

import models
import secrets


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
    def get_english_page(page_link):
        if "wikipedia.org/wiki/" not in page_link:
            raise Exception("Not a wikipedia link")

        info = page_link.split("//")[1].split("/")
        title = info[2]
        language = info[0].split(".")[0]

        wiki_wiki = wikipediaapi.Wikipedia(user_agent=secrets.user_agent, language=language)

        if language == "en":
            page = wiki_wiki.page(title)
        else:
            page = wiki_wiki.page(title).langlinks.get("en", None)

        try:
            if not page.exists():
                raise Exception("Wikipedia page does not exist")

        except AttributeError:
            raise Exception("Some problem with wikipedia, please try again")

        return page


class WatchListRecord:
    type = "None"

    def __init__(self, db_record):
        self.information_url = db_record.information_url
        self.creator = db_record.creator
        self.note = db_record.note

        self.db_id = db_record.id
        self.status = db_record.status
        self.created_at = db_record.created_at

    @staticmethod
    def validate_link(information_url):
        raise NotImplementedError(f"Function validate link was not implemented")

    def get_info(self):
        raise NotImplementedError(f"Function get_info for type {self.type} was not implemented")

    def __str__(self):
        record_info = self.get_info()

        text_link = f"[{record_info.title}]({record_info.link})"
        creator = record_info.creator
        created_at = f"{record_info.created_at:%B %#d}"
        note = f"with note: {record_info.note}" if record_info.note else ""

        str_information = f"{text_link} - added by {creator} on {created_at} {note}\n"

        return str_information


class AnimeWatchListRecord(WatchListRecord):
    name = 'anime'

    def __init__(self, db_record):
        super().__init__(db_record)
        self.mal_title = mal.Anime(list(reversed(self.information_url.split('/')))[1])

    @staticmethod
    def validate_link(information_url):
        info_link_list = list(reversed(information_url.split('/')))
        if not (info_link_list[2] == "anime") or not ("myanimelist" in info_link_list[3]):
            raise Exception("Unsupported link for type anime")

        return information_url

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
    name = 'film'

    def __init__(self, db_record):
        super().__init__(db_record)
        self.page = WikiHelper.get_english_page(self.information_url)

    @staticmethod
    def validate_link(information_url):
        page = WikiHelper.get_english_page(information_url)
        page_summary = page.summary.lower()
        if (("film" in page_summary) and ("directed by" in page_summary)) or ("animated" in page_summary):
            return page.canonicalurl

        raise Exception("Not a film related wikipedia page, if you think it is then contact perite")

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
    name = 'tv-show'

    def __init__(self, db_record):
        super().__init__(db_record)
        self.page = WikiHelper.get_english_page(self.information_url)

    @staticmethod
    def validate_link(information_url):
        page = WikiHelper.get_english_page(information_url)
        page_summary = page.summary.lower()

        if (("television series" in page_summary) or ("sitcoms" in page_summary)) and ("created by" in page_summary):
            return page.canonicalurl

        raise Exception("Not a tv-show related wikipedia page, if you think it is then contact perite")

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
        type_class = list(filter(lambda type_class: type_class.name == type_name, TypesAndRecordsManagers.types))
        if not type_class:
            raise Exception("Unsupported type")

        return type_class[0]

    @staticmethod
    def get_db_records_of_type(type_name):
        db_records_of_type = list(models.WatchListRecord.select().where(
            (models.WatchListRecord.type == type_name) & (models.WatchListRecord.status != "watched"))
                                  .order_by(models.WatchListRecord.created_at.asc()))

        return db_records_of_type

    @staticmethod
    def db_record_to_record(type_class, db_record):
        return type_class(db_record)
