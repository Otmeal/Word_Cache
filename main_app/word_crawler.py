import re
import requests

from .models import Word, PartOfSpeech, DefinitionSet, DefinitionUnit, Pronunciations
from bs4 import BeautifulSoup
from bs4.element import Tag
from main_app import db


class Processor:
    def __init__(self):
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78"
        }

    def get_url_data(self, url: str) -> str:
        return requests.get(url, headers=self.header).text

    def append_header(self, key, value) -> None:
        self.header[key] = value


class WordCrawler:
    def __init__(self):
        self.word_body: BeautifulSoup = None
        self.word_name: str = None

    def commit_word(self) -> bool:
        if not self.word_body:
            return None
        word_def = Word()
        entrys = self.find_all_items(self.word_body, "entry") or self.find_all_items(
            self.word_body, "idiom_block"
        )
        word_def.name = self.word_name
        db.session.add(word_def)

        self.add_pos_to_word_def(word_def, entrys)

        db.session.commit()
        return True

    def add_pos_to_word_def(self, word_def: Word, entrys) -> None:
        for entry in entrys:
            part_of_speech = PartOfSpeech(word=word_def)
            part_of_speech.form = self.find_item_text(entry, "title")
            part_of_speech.pos = self.find_item_text(entry, "pos")
            part_of_speech.counting = self.find_item_text(entry, "counting")

            self.add_pron_to_pos(part_of_speech, entry)
            self.add_definition_set_to_pos(part_of_speech, entry)

    def add_pron_to_pos(self, part_of_speech: PartOfSpeech, entry) -> None:
        pron_set = Pronunciations(pos=part_of_speech)
        pron_tag = self.find_item(entry, "uk_pron")
        if pron_tag:
            pron_set.uk_pron = self.find_item_text(pron_tag, "pron")
        pron_tag = self.find_item(entry, "us_pron")
        if pron_tag:
            pron_set.us_pron = self.find_item_text(pron_tag, "pron")

    def add_definition_set_to_pos(
        self, part_of_speech: PartOfSpeech, entry: Tag
    ) -> None:
        for sense in self.find_all_items(entry, "sense_block") + self.find_all_items(
            entry, "not_sense_block"
        ):
            definition_set = DefinitionSet(pos=part_of_speech)
            definition_set.sense = self.find_item_text(sense, "sense")
            self.add_definition_unit_to_set(definition_set, sense)

    def add_definition_unit_to_set(
        self, definition_set: DefinitionSet, sense: Tag
    ) -> None:
        for def_block in self.get_normal_and_phrase_blocks(sense):
            definition_unit = DefinitionUnit(definition_set=definition_set)
            definition_unit.phrase_title = self.find_item_text(
                def_block, "phrase_title"
            )
            definition_unit.counting = self.find_item_text(def_block, "counting")
            if self.find_item(def_block, "variant_name"):
                definition_unit.variant_name = self.find_item_text(
                    def_block, "variant_name"
                )
            else:
                definition_unit.label = self.find_item_text(def_block, "label")
            definition_unit.english_definition = self.find_item_text(
                def_block, "english_definition"
            )
            definition_unit.chinese_definition = self.find_item_text(
                def_block, "chinese_definition"
            )

    def get_normal_and_phrase_blocks(self, sense: Tag) -> list:
        phrase_blocks = self.find_all_items(sense, "phrase_block")
        def_blocks = self.find_all_items(sense, "def_block")
        return def_blocks[: len(def_blocks) - len(phrase_blocks)] + phrase_blocks

    def set_word_name(self, word: str):
        self.word_body: BeautifulSoup = self.get_word_definition_tag(word)
        if self.word_body:
            word_name = self.find_item_text(self.word_body, "title").split()
            self.word_name = "-".join(word_name)
        else:
            self.word_name = None

    def get_word_definition_tag(self, word: str) -> Tag:
        soup = BeautifulSoup(self.crawl_word(word), "lxml")
        return soup.find("div", "di-body")

    def crawl_word(self, word: str) -> str:

        html = Processor().get_url_data(
            "https://dictionary.cambridge.org/dictionary/english-chinese-traditional/"
            + word
        )
        soup = BeautifulSoup(html, "lxml")
        if self.is_soup_def_page(soup):
            return html

        html = Processor().get_url_data(
            "https://dictionary.cambridge.org/dictionary/english/" + word
        )
        soup = BeautifulSoup(html, "lxml")
        if self.is_soup_def_page(soup):
            return html
        else:
            return ""

    def is_soup_def_page(self, soup: BeautifulSoup) -> bool:
        if self.find_item(soup, "def_body"):
            return True
        else:
            return False

    def find_all_items(self, tag: Tag, item_name: str) -> list[Tag]:
        if item_name in item_dict:
            item: Item = item_dict[item_name]
            return tag.find_all(item.name, class_=item.class_)
        else:
            return []

    def find_item(self, tag: Tag, item_name: str) -> Tag:
        if item_name in item_dict:
            item: Item = item_dict[item_name]
            return tag.find(item.name, class_=item.class_)
        else:
            return None

    def find_item_text(self, tag: Tag, item_name: str) -> str:
        if self.find_item(tag, item_name):
            return self.find_item(tag, item_name).get_text()
        else:
            return None


class Item:
    def __init__(self, name: str, class_: str) -> None:
        self.name: str = name
        self.class_: str = class_


item_dict = {
    "def_body": Item("div", "di-body"),
    "idiom_block": Item("div", "pr idiom-block"),
    "entry": Item("div", "pr entry-body__el"),
    "title": Item("div", "di-title"),
    "pos": Item("span", "pos dpos"),
    "counting": Item("span", "gram dgram"),
    "uk_pron": Item("span", "uk dpron-i"),
    "us_pron": Item("span", "us dpron-i"),
    "pron_region": Item("span", "region dreg"),
    "pron": Item("span", "pron dpron"),
    "sense_block": Item("div", "pr dsense"),
    "not_sense_block": Item("div", "pr dsense dsense-noh"),
    "sense": Item("h3", "dsense_h"),
    "def_block": Item("div", "def-block ddef_block"),
    "phrase_block": Item("div", re.compile("^pr phrase-block dphrase-block.*")),
    "phrase_title": Item("span", "phrase-title dphrase-title"),
    "variant_name": Item("span", "var dvar"),
    "label": Item("span", "lab dlab"),
    "english_definition": Item("div", "def ddef_d db"),
    "chinese_definition": Item("span", "trans dtrans dtrans-se break-cj"),
    "phrase_header": Item("div", "phrase-head dphrase_h"),
}
