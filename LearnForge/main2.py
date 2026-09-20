from pprint import pprint

from vectorDb import learningCollection


def get_all_learning_items():
    return learningCollection.get()


if __name__ == "__main__":
    result = get_all_learning_items()
    pprint(result)
    