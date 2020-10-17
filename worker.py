from discog import timer, collection_grab, title_flatten, list_to_xl, collection_lowest_price, test_listo


@timer
def main():
    flat_titles = list()
    #titles = collection_grab()
    #for title in titles:
    #    flat_titles.append(title_flatten(title))

    #list_to_xl(test_listo)
    collection_lowest_price(test_listo)

    return


if __name__ == '__main__':
    main()