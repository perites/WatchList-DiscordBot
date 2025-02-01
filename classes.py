import dataclasses
import logging

import mal
import wikipediaapi

import models
import secrets


@dataclasses.dataclass
class EntityInfo:
    title: str
    link: str
    creator: str
    created_at: str
    note: str
    id: int = 45


class WatchListEntity:
    type = "None"

    def __init__(self, info_link, created_at, creator, note):
        self.info_link = info_link
        self.created_at = created_at
        self.creator = creator
        self.note = note

    def validate(self):
        pass

    def get_info(self):
        pass

    def add_to_watchlist(self):
        try:
            models.WatchListEntity.create(info_link=self.info_link, type=self.type,
                                          creator=self.creator,
                                          created_at=self.created_at, status=0, note=self.note)
        except Exception as e:
            logging.critical(f"Error during saving to DB : {e}")
            raise Exception(f"Could not save to DB for some reason.\n\nTechnical error : {e}")


class WikiHelper:

    def get_english_page(self, page_link):
        if "wikipedia.org/wiki/" not in page_link:
            raise Exception("Not a wikipedia link")

        info = page_link.split("//")[1].split("/")
        title = info[2]
        language = info[0].split(".")[0]

        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent=secrets.user_agent, language=language)

        if not language == "en":
            page = wiki_wiki.page(title).langlinks.get("en", None)
        else:
            page = wiki_wiki.page(title)

        if not page.exists():
            raise Exception("Wikipedia page does not exist")

        self.info_link = page.canonicalurl
        return page

    def get_info(self):

        # dt_object = datetime.datetime.fromtimestamp(self.created_at)

        return EntityInfo(
            title=self.page.title,
            link=self.info_link,
            creator=self.creator,
            created_at=self.created_at,
            note=self.note,

        )


class AnimeListEntity(WatchListEntity):
    type = 'anime'

    def __init__(self, info_link, created_at, author, note):
        super().__init__(info_link, created_at, author, note)
        self.mal_title = mal.Anime(list(reversed(self.info_link.split('/')))[1])

    def validate(self):
        info_link_list = list(reversed(self.info_link.split('/')))
        if not (info_link_list[2] == "anime") or not ("myanimelist" in info_link_list[3]):
            raise Exception("Unsupported link for type anime")

        return True

    def get_info(self):
        return EntityInfo(
            title=self.mal_title.title_english or self.mal_title.title,
            link=self.info_link,
            creator=self.creator,
            created_at=self.created_at,
            note=self.note

        )


class FilmListEntity(WikiHelper, WatchListEntity):
    type = 'film'

    def __init__(self, info_link, created_at, author, note):
        super().__init__(info_link, created_at, author, note)
        self.page = self.get_english_page(self.info_link)

    def validate(self):
        if (("film" in self.page.summary.lower()) and ("directed by" in self.page.summary.lower())) or (
                "animated" in self.page.summary.lower()):
            return True

        raise Exception("Not a film related wikipedia page")


class TvShowListEntity(WikiHelper, WatchListEntity):
    type = 'tv-show'

    def __init__(self, info_link, created_at, author, note):
        super().__init__(info_link, created_at, author, note)
        self.page = self.get_english_page(self.info_link)

    def validate(self):
        if ("television series" in self.page.summary.lower()) and ("created by" in self.page.summary.lower()):
            return True

        raise Exception("Not a tv-show related wikipedia page")


type_to_list_entity = {
    AnimeListEntity.type: AnimeListEntity,
    FilmListEntity.type: FilmListEntity,
    TvShowListEntity.type: TvShowListEntity
}
