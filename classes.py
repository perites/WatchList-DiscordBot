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


class WikiHelper:
    @staticmethod
    def get_english_page(page_link):
        if "wikipedia.org/wiki/" not in page_link:
            raise Exception("Not a wikipedia link")

        info = page_link.split("//")[1].split("/")
        title = info[2]
        language = info[0].split(".")[0]

        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent=secrets.user_agent, language=language)

        if language == "en":
            page = wiki_wiki.page(title)
        else:
            page = wiki_wiki.page(title).langlinks.get("en", None)

        if not page.exists():
            raise Exception("Wikipedia page does not exist")

        return page


class WatchListRecord:
    type = "None"

    def __init__(self, db_record):
        self.information_url = db_record.information_url
        self.creator = db_record.creator
        self.note = db_record.note

        self.status = db_record.status
        self.created_at = db_record.created_at

    @staticmethod
    def validate_link(information_url):
        raise NotImplementedError(f"Function validate link was not implemented")

    def _get_info(self):
        raise NotImplementedError(f"Function get_info for type {self.type} was not implemented")

    def __str__(self):
        record_info = self._get_info()

        text_link = f"[{record_info.title}]({record_info.link})"
        creator = record_info.creator
        created_at = f"{record_info.created_at:%B %#d}"
        note = f"with note: {record_info.note}" if record_info.note else ""

        str_information = f"{text_link} - added by {creator} on {created_at} {note}\n"

        return str_information


class AnimeWatchListRecord(WatchListRecord):
    type = 'anime'

    def __init__(self, db_record):
        super().__init__(db_record)
        self.mal_title = mal.Anime(list(reversed(self.information_url.split('/')))[1])

    @staticmethod
    def validate_link(information_url):
        info_link_list = list(reversed(information_url.split('/')))
        if not (info_link_list[2] == "anime") or not ("myanimelist" in info_link_list[3]):
            raise Exception("Unsupported link for type anime")

        return True

    def _get_info(self):
        return EntityInfo(
            title=self.mal_title.title_english or self.mal_title.title,
            link=self.information_url,
            creator=self.creator,
            created_at=self.created_at,
            note=self.note

        )


class FilmWatchListRecord(WatchListRecord):
    type = 'film'

    def __init__(self, db_record):
        super().__init__(db_record)
        self.page = WikiHelper.get_english_page(self.information_url)

    @staticmethod
    def validate_link(information_url):
        page = WikiHelper.get_english_page(information_url)
        if (("film" in page.summary.lower()) and ("directed by" in page.summary.lower())) or (
                "animated" in page.summary.lower()):
            return True

        raise Exception("Not a film related wikipedia page")

    def _get_info(self):
        return EntityInfo(
            title=self.page.title,
            link=self.page.canonicalurl,
            creator=self.creator,
            note=self.note,
            created_at=self.created_at,

        )


class TvShowWatchListRecord(WatchListRecord):
    type = 'tv-show'

    def __init__(self, db_record):
        super().__init__(db_record)
        self.page = WikiHelper.get_english_page(self.information_url)

    @staticmethod
    def validate_link(information_url):
        page = WikiHelper.get_english_page(information_url)
        if ("television series" in page.summary.lower()) and ("created by" in page.summary.lower()):
            return True

        raise Exception("Not a tv-show related wikipedia page")

    def _get_info(self):
        return EntityInfo(
            title=self.page.title,
            link=self.page.canonicalurl,
            creator=self.creator,
            note=self.note,
            created_at=self.created_at,

        )


class TypesAndRecordsManagers:
    types = {}

    def set_types(self, types):
        self.types = types

    def get_type(self, type_name):
        return self.types.get(type_name)

    def indexes_to_db_records(self):
        indexes_to_records = {}
        for type in self.types.keys():
            db_records_of_type = list(models.WatchListRecord.select().where(
                (models.WatchListRecord.type == type) & (models.WatchListRecord.status != "watched"))
                                      .order_by(models.WatchListRecord.created_at))

            if not db_records_of_type:
                continue
            indexes_to_records[type] = {}
            for actual_index, db_record in enumerate(db_records_of_type):
                index = actual_index + 1

                indexes_to_records[type][index] = db_record

        print(indexes_to_records)
        return indexes_to_records
