import pandas as pd
import helper as utl


def prep_data(dataframe): ...


def main():
    """
    Entry point for the script.
    :return: None.
    :rtype: None.
    """
    pres_outcomes = utl.get_wiki_pres_elections(
        "https://en.wikipedia.org/wiki/List_of_United_States_presidential_elections_by_popular_vote_margin",
        2,
    )

    test = utl.get_wiki_pres_elections(
        "https://www.britannica.com/topic/United-States-Presidential-Election-Results-1788863"
    )


if __name__ == "__main__":
    main()
