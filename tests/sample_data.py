from typing import List
from sqlalchemy import create_engine, ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    sessionmaker,
    relationship,
    declarative_base,
)
import random

from easy_reports import EasyReport

PREFIX = 'er_test_'

Base = declarative_base()


class UserLanguage(Base):
    __tablename__ = PREFIX + 'user_language'

    user_id: Mapped[int] = mapped_column(
        ForeignKey("er_test_users.id"), primary_key=True
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("er_test_languages.id"), primary_key=True
    )
    user: Mapped['User'] = relationship(back_populates="languages")
    language: Mapped['Language'] = relationship(back_populates="users")
    # extra data fields
    level: Mapped[str] = mapped_column(String(15))


class User(Base):
    __tablename__ = PREFIX + 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    age: Mapped[int]
    languages: Mapped[List['UserLanguage']] = relationship(back_populates='user')

    def add_language(self, language, level):
        # Add a language to the user's languages with a given level of knowledge
        assoc = UserLanguage(level=level)
        assoc.language = language
        self.languages.append(assoc)

    def __repr__(self):
        return f"<User(name='{self.name}', age={self.age}, languages={self.languages})>"


class Language(Base):
    __tablename__ = PREFIX + 'languages'

    id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[str] = mapped_column(String(50))
    difficulty: Mapped[int]
    users: Mapped[List['UserLanguage']] = relationship(back_populates='language')

    def __repr__(self):
        return f"<Language(language='{self.language}', difficulty='{self.difficulty})>"


# (name, age)
USERS = [
    ('Tom', 20),
    ('Kate', 15),
    ('Sebastian', 34),
    ('Patric', 47),
    ('Luke', 60),
    ('Susan', 55),
    ('Monica', 12),
    ('Brad', 24),
    ('Julia', 31),
    ('Bob', 41),
    ('Ken', 18),
]

# (name, difficulty)
LANGUAGES = [
    ('english', 1),
    ('spanish', 2),
    ('french', 3),
    ('italian', 2),
    ('polish', 4),
    ('bulgarian', 4),
    ('japanese', 5),
    ('hungarian', 5),
    ('arabic', 5),
    ('greek', 5),
]


data = []
lang_list = [(language, difficulty) for language, difficulty in LANGUAGES]
user_list = [(name, age) for name, age in USERS]
for user in user_list:
    for lang in random.sample(LANGUAGES, random.randint(1, 4)):
        data.append(
            (
                user,
                lang,
                random.choice(['beginner', 'intermediate', 'advanced', 'native']),
            )
        )


def populate(db_conf):
    """Populate test database with sample data"""

    engine = create_engine(db_conf['url'], echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # add languages
    languages = [
        Language(language=language, difficulty=difficulty)
        for language, difficulty in lang_list
    ]
    session.add_all(languages)

    # add random user languages
    users = [User(name=name, age=age) for name, age in user_list]
    for user in users:
        for _user, _lang, level in data:
            if _user[0] == user.name:
                user.add_language(
                    language=next(_ for _ in languages if _.language == _lang[0]),
                    level=level,
                )
    session.add_all(users)

    session.commit()


def main():
    app = EasyReport()
    app.base_config.from_pyfile('./tests/settings_test_base.py')
    for db, db_conf in app.base_config.DB_LIST.items():
        populate(db_conf)


if __name__ == '__main__':
    main()
    # print(data)
