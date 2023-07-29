from sqlalchemy import create_engine, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    sessionmaker,
    declarative_base,
)

from easy_reports import EasyReport


data = [
    (
        'Austria',
        '8,920,046',
        'Vienna',
        '1,897,491',
        'German',
        'Roman Catholicism, Protestantism, Islam, Judaism',
        '9.2',
        '9.6',
        'Danube, Mur',
        'Red, White',
        '83,879',
    ),
    (
        'Belgium',
        '11,632,186',
        'Brussels',
        '1,208,542',
        'Dutch, French, German',
        'Roman Catholicism, Protestantism, Islam, Judaism',
        '11.4',
        '9.9',
        'Scheldt, Meuse',
        'Black, Yellow, Red',
        '30,528',
    ),
    (
        'Bulgaria',
        '6,951,482',
        'Sofia',
        '1,260,120',
        'Bulgarian',
        'Bulgarian Orthodox, Islam, Roman Catholicism, Protestantism',
        '9.2',
        '15.3',
        'Danube, Maritsa',
        'White, Green, Red',
        '110,994',
    ),
    (
        'Croatia',
        '4,058,165',
        'Zagreb',
        '790,017',
        'Croatian',
        'Roman Catholicism, Eastern Orthodoxy',
        '8.6',
        '12.2',
        'Danube, Sava',
        'Red, White, Blue',
        '56,542',
    ),
    (
        'Cyprus',
        '1,207,359',
        'Nicosia',
        '310,355',
        'Greek, Turkish',
        'Christianity, Islam, Judaism',
        '10.6',
        '9.2',
        'Pedieos, Kouris',
        'White, Orange',
        '9,251',
    ),
    (
        'Czech Republic',
        '10,729,438',
        'Prague',
        '1,335,395',
        'Czech',
        'Roman Catholicism, Protestantism, Eastern Orthodoxy',
        '9.4',
        '10.6',
        'Vltava, Elbe',
        'White, Red, Blue',
        '78,866',
    ),
    (
        'Denmark',
        '5,854,146',
        'Copenhagen',
        '794,128',
        'Danish',
        'Church of Denmark, Roman Catholicism, Protestantism',
        '9.3',
        '10.3',
        'Gudena, Skjern',
        'Red, White',
        '42,951',
    ),
    (
        'Estonia',
        '1,325,648',
        'Tallinn',
        '437,619',
        'Estonian',
        'Evangelical Lutheranism',
        '10.4',
        '13.4',
        'Emajogi, Parnu',
        'Blue, Black, White',
        '45,227',
    ),
    (
        'Finland',
        '5,529,347',
        'Helsinki',
        '648,042',
        'Finnish, Swedish',
        'Evangelical Lutheran Church of Finland',
        '10.7',
        '9.7',
        'Kemijoki, Ounasjoki',
        'Blue, White',
        '338,424',
    ),
    (
        'Germany',
        '83,190,556',
        'Berlin',
        '3,769,495',
        'German',
        'Roman Catholicism, Protestantism, Islam, Judaism',
        '9.3',
        '11.2',
        'Rhine, Elbe',
        'Black, Red, Gold',
        '357,386',
    ),
    (
        'Poland',
        '38,433,600',
        'Warsaw',
        '1,790,658',
        'Polish',
        'Roman Catholicism',
        '9.4',
        '10.5',
        'Vistula, Oder',
        'White, Red',
        '312,696',
    ),
    (
        'Romania',
        '19,511,324',
        'Bucharest',
        '1,832,883',
        'Romanian',
        'Eastern Orthodox, Roman Catholicism, Protestantism',
        '9.0',
        '13.4',
        'Danube, Mures',
        'Blue, Yellow, Red',
        '238,391',
    ),
]


PREFIX = 'er_'
Base = declarative_base()


class Country(Base):
    __tablename__ = PREFIX + 'countries'

    id: Mapped[int] = mapped_column(primary_key=True)
    country: Mapped[str] = mapped_column(String(100))
    population: Mapped[int]
    capital: Mapped[str] = mapped_column(String(100))
    capital_population: Mapped[int]
    official_languages: Mapped[str] = mapped_column(String(100))
    religions: Mapped[str] = mapped_column(String(100))
    birth_rate: Mapped[float]
    death_rate: Mapped[float]
    longest_rivers: Mapped[str] = mapped_column(String(100))
    flag_colors: Mapped[str] = mapped_column(String(100))
    area_sq_km: Mapped[int]


def populate(db_conf):
    """Populate test dadabase with sample data"""

    engine = create_engine(db_conf['url'], echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # add languages

    countries = [
        Country(
            country=country,
            population=int(population.replace(',', '')),
            capital=capital,
            capital_population=int(capital_population.replace(',', '')),
            official_languages=official_languages,
            religions=religions,
            birth_rate=float(birth_rate),
            death_rate=float(death_rate),
            longest_rivers=longest_rivers,
            flag_colors=flag_colors,
            area_sq_km=int(area_sq_km.replace(',', '')),
        )
        for country, population, capital, capital_population, official_languages, religions, birth_rate, death_rate, longest_rivers, flag_colors, area_sq_km in data
    ]
    session.add_all(countries)
    session.commit()


def main():
    app = EasyReport()
    app.base_config.from_pyfile('./examples/settings.py')
    for db, db_conf in app.base_config.DB_LIST.items():
        populate(db_conf)


if __name__ == '__main__':
    main()
