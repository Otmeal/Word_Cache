from .word_crawler import WordCrawler
from flask import url_for, render_template, request, make_response
from main_app import app, db
from .models import Word

SECONDS_OF_WEEK = 7 * 24 * 60 * 60


class SearchResult:
    def __init__(self):
        self.words = []
        self.cookie: str = ""


class ServerUrls:
    def __init__(self):
        self.url_dict = {
            "add_words": url_for("add_words", words_request="", _external=True),
            "delete_words": url_for("delete_words", words_deleted="", _external=True),
            "delete_all_words": url_for("delete_all_words", _external=True),
        }


@app.route("/", methods=["GET", "POST"])
def index():
    result = search_words(request.cookies.get("words") or "")
    response = make_response(
        render_template(
            "Dictionary.html", words=result.words, SERVER_URLS=ServerUrls().url_dict
        )
    )
    response.set_cookie("words", result.cookie, max_age=SECONDS_OF_WEEK)

    return response


@app.route("/add_words/<words_request>", methods=["GET", "POST"])
def add_words(words_request: str):
    words_cookie = request.cookies.get("words") or ""
    result = search_words(words_request)
    response = make_response(render_template("Word_block.html", words=result.words))
    response.set_cookie(
        "words", words_cookie + " " + result.cookie, max_age=SECONDS_OF_WEEK
    )

    return response


@app.route("/delete_words/<words_deleted>", methods=["GET", "POST"])
def delete_words(words_deleted: str):
    words_cookie = request.cookies.get("words")
    words = words_cookie.split()
    for word in words_deleted.split():
        words.remove(word)
    words_cookie = " ".join(words)
    response = make_response()
    response.set_cookie("words", words_cookie, max_age=SECONDS_OF_WEEK)

    return response


@app.route("/delete_all/", methods=["GET", "POST"])
def delete_all_words():
    response = make_response()
    response.set_cookie("words", "", max_age=SECONDS_OF_WEEK)
    return response


def search_words(word_request: str) -> SearchResult:
    result = SearchResult()
    crawler = WordCrawler()
    result.words = []
    words_needed = word_request.lower().split()
    if words_needed:
        for word in words_needed[:]:
            word_data = get_word_data(word)
            if word_data:
                result.words.append(word_data)
                continue
            else:
                crawler.set_word_name(word)
            if not word == crawler.word_name:
                words_needed.remove(word)

            word_data = get_word_data(crawler.word_name)
            if word_data:
                result.words.append(word_data)
            elif crawler.word_name:
                crawler.commit_word()
                print(f"Added word: {crawler.word_name} to the database")
                word_data = get_word_data(crawler.word_name)
                result.words.append(word_data)
            else:
                print(f"Word: {word} not found.")
                continue
            if not word == crawler.word_name:
                words_needed.append(crawler.word_name)
    result.cookie = " ".join(words_needed)
    return result


def get_word_data(word_name: str):
    return Word.query.filter_by(name=word_name).first()


if __name__ == "__main__":
    app.run()
