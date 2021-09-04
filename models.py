from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class Follows(db.Model):
    """Connection of a follower <-> followed_user."""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )

class User(db.Model):
    """User Table"""

    __tablename__ = "users"

    def __repr__(self) -> str:
        return f"id {self.id} {self.first_name} {self.last_name}"

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    username = db.Column(db.Text,
                        nullable=False,
                        unique=True)

    email = db.Column(db.Text,
                        nullable=False,
                        unique=True)

    password = db.Column(db.Text,
                        nullable=False)

    first_name = db.Column(db.String(50),
                            nullable=False)

    last_name = db.Column(db.String(50),
                            nullable=False)

    quote = db.Column(db.Text,
                        nullable=True)

    sex = db.Column(db.Text,
                    nullable=False)

    avatar = db.Column(db.Text,
                        nullable=True)

    points = db.Column(db.Integer,
                        default=0)

    @classmethod
    def register(cls,username,email,password,first,last,quote,sex,avatar,points):
        epw_hash = bcrypt.generate_password_hash(password).decode("utf8")
        return cls(
            username=username,
            email=email,
            password=epw_hash,
            first_name=first,
            last_name=last,
            quote=quote,
            sex=sex,
            avatar=avatar,
            points=points
        )

    @classmethod
    def authenticate(cls,username,password):
      current_user = User.query.filter_by(username=username).first()
      if current_user and bcrypt.check_password_hash(current_user.password,password):
        return current_user
      else:
        return False
    
    articles = db.relationship("Articles",secondary="user_reads",backref="user")

    import_category = db.relationship("ImportCategory")

    import_articles = db.relationship("ImportArticles",secondary="import_user_reads",backref="import_user")

    related_vocabulary_list = db.relationship("VocabularyListName",backref="list_owner")

    messages = db.relationship("Message",backref="message_owner")

    comment_message = db.relationship("CommentMessage",backref="comment_user")

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1


class Quotes(db.Model):
    """motivation quote for success"""

    __tablename__ = "quotes"

    def __repr__(self) -> str:
        return f"quote id {self.id}"

    id = db.Column(
            db.Integer,
            primary_key=True,
            autoincrement=True)

    quote = db.Column(db.Text,
                        nullable=True)

class Articles(db.Model):
  """article to read"""

  __tablename__ = "articles"

  def __repr__(self) -> str:
      return f"article id {self.id} title: {self.title}"

  id = db.Column(
    db.Integer,
    primary_key=True,
    autoincrement=True)

  author = db.Column(db.Text,
                      nullable=False)

  title = db.Column(db.Text,
                      nullable=False)
                      
  category = db.Column(db.Integer,
                      db.ForeignKey("proload_categories.id"),
                      nullable=False)

  description = db.Column(db.Text,
                            nullable=False)

  cover_url = db.Column(db.Text,
                        nullable=False)

  content = db.Column(
    db.Text,
    nullable=False)

  number_of_readings = db.Column(
    db.Integer,
    nullable=False,
    default=0)

  user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    nullable=True
  )

class Categories(db.Model):
  """preload article categories"""

  __tablename__ = "proload_categories"

  id = db.Column(
    db.Integer,
    primary_key=True,
    autoincrement=True
  )

  category = db.Column(
    db.Text,
    unique=True,
    nullable=False
  )

  description = db.Column(
    db.Text,
    nullable=False
  )

  articles = db.relationship("Articles",backref="theCategory",cascade='all,delete')

class VocabularyFromArticle(db.Model):
  """Vocabulary From Article"""

  __tablename__ = "vocabulary_from_article"

  def __repr__(self) -> str:
      return f"id {self.id} {self.spell}"

  id = db.Column(
    db.Integer,
    primary_key=True,
    autoincrement=True)

  spell = db.Column(
    db.Text,
    nullable=False)

  definition = db.Column(
    db.Text,
    nullable=False)

  part_of_speech = db.Column(
    db.Text,
    nullable=True
  )

  article_id = db.Column(
    db.Integer,
    db.ForeignKey("articles.id"),
  )

  user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
  )

  image_url = db.Column(
    db.Text,
    nullable=True)



class UserFinishReading(db.Model):
  """User Finish Reading"""

  __tablename__ = "user_reads"

  def __repr__(self) -> str:
      return f"user id {self.user_id} and article id {self.article_id}"

  user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    primary_key=True,
  )

  article_id = db.Column(
    db.Integer,
    db.ForeignKey("articles.id"),
    primary_key=True
  )

class VocabularyListName(db.Model):
  """user vocabulary list """

  __tablename__ = "vocabulary_list_name"

  def __repr__(self) -> str:
      return f"list name {self.list_name}  and id {self.id}"

  id = db.Column(
    db.Integer,
    primary_key=True,
    autoincrement=True)

  list_name = db.Column(
    db.Text,
    nullable=False)

  description = db.Column(
    db.Text,
    nullable=False)

  user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    nullable=False)

  vocabularies = db.relationship("VocabularyList",cascade='all,delete')

class VocabularyList(db.Model):
  """vocabulary list"""

  __tablename__ = "vocabulary_list"

  def __repr__(self) -> str:
      return f"id {self.id} spell {self.spell}"

  id = db.Column(
    db.Integer,
    primary_key=True,
    autoincrement=True
  )

  spell = db.Column(
    db.Text,
    nullable=False
  )

  definition = db.Column(
    db.Text,
    nullable=False
  )

  part_of_speech = db.Column(
    db.Text,
    nullable=False
  )

  list_id = db.Column(
    db.Integer,
    db.ForeignKey("vocabulary_list_name.id"),
    nullable=False
  )

  image_url = db.Column(
    db.Text,
    nullable=True
  )

class ImportCategory(db.Model):
  """table hold import category"""

  __tablename__ = "import_categories"

  def __repr__(self) -> str:
      return f"{self.category} id {self.id}"

  id = db.Column(
    db.Integer,
    primary_key=True,
    autoincrement=True
  )

  category = db.Column(
    db.Text,
    nullable=False,
    unique=True
  )

  description = db.Column(
    db.Text,
    nullable=False
  )

  user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id")
  )

  articles = db.relationship("ImportArticles",secondary="import_category_articles",backref="the_category")

class ImportArticles(db.Model):
  """import article to read"""

  __tablename__ = "import_articles"

  def __repr__(self) -> str:
      return f"import article id {self.id} title: {self.title}"

  id = db.Column(
    db.Integer,
    primary_key=True,
    autoincrement=True)

  author = db.Column(db.Text,
                      nullable=False)

  title = db.Column(db.Text,
                      nullable=False)

  category = db.Column(db.Integer,
                      db.ForeignKey("import_categories.id",ondelete='CASCADE'),
                      nullable=False)

  description = db.Column(db.Text,
                            nullable=False)

  cover_url = db.Column(db.Text,
                        nullable=False,
                        default="https://thumbs.dreamstime.com/b/not-available-stamp-seal-watermark-distress-style-designed-rectangle-circles-stars-black-vector-rubber-print-title-138796185.jpg")

  content = db.Column(
    db.Text,
    nullable=False)

  number_of_readings = db.Column(
    db.Integer,
    nullable=False,
    default=0)

  user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    nullable=True
  )

class FinishImportReading(db.Model):
  """user finish import reading"""

  __tablename__ = "import_user_reads"

  user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    primary_key=True
  )

  import_article_id = db.Column(
    db.Integer,
    db.ForeignKey("import_articles.id"),
    primary_key=True
  )


class ImportCategoryArticles(db.Model):
  """import category articles"""

  __tablename__ = "import_category_articles"

  category_id = db.Column(
    db.Integer,
    db.ForeignKey("import_categories.id"),
    primary_key=True
  )

  article_id = db.Column(
    db.Integer,
    db.ForeignKey("import_articles.id"),
    primary_key=True
  )

class VocabularyFromImportArticle(db.Model):
  """Vocabulary From Import Article"""

  __tablename__ = "vocabulary_from_import_article"

  def __repr__(self) -> str:
      return f"id {self.id} {self.spell} from import article"

  id = db.Column(
    db.Integer,
    primary_key=True,
    autoincrement=True)

  spell = db.Column(
    db.Text,
    nullable=False)

  definition = db.Column(
    db.Text,
    nullable=False)

  part_of_speech = db.Column(
    db.Text,
    nullable=True)

  article_id = db.Column(
    db.Integer,
    db.ForeignKey("import_articles.id",ondelete="cascade"))

  user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"))

  image_url = db.Column(
    db.Text,
    nullable=True)


class Message(db.Model):
    """An individual message ("warble")."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    text = db.Column(
        db.String(140),
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    comments = db.relationship("CommentMessage",backref="message",cascade="all, delete")

    likes = db.relationship("Likes",backref="like_message",cascade="all, delete")

class CommentMessage(db.Model):
  """Add Comment Message"""

  __tablename__ = "commentsmessage"

  id = db.Column(
        db.Integer,
        primary_key=True
    )

  text = db.Column(
        db.String(140),
        nullable=False
    )

  timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )

  user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

  message_id = db.Column(
    db.Integer,
    db.ForeignKey("messages.id",ondelete='CASCADE'),
    nullable=False
  )

  comment_owner = db.relationship("User",backref="comment")

  likes = db.relationship("CommentLikes",backref="like_comment",cascade="all, delete")



class Likes(db.Model):
    """Mapping user likes to warbles."""

    __tablename__ = 'likes' 

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        primary_key=True
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete='cascade'),
        primary_key=True
    )

class CommentLikes(db.Model):
  """storing likes for comments"""

  __tablename__= "commentlikes"

  comment_id = db.Column(
    db.Integer,
    db.ForeignKey('commentsmessage.id',ondelete='cascade'),
    primary_key=True
  )

  user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id",ondelete="cascade"),
    primary_key=True
  )

