from discog import timer, collection_grab, title_flatten, list_to_xl, collection_lowest_price


@timer
def main():
    flat_titles = list()
    titles = collection_grab()
    for title in titles:
        flat_titles.append(title_flatten(title))

    collection_lowest_price(test_listo)
    list_to_xl(test_listo)

    return


if __name__ == '__main__':
    main()