from models import User, Quotes,db,Articles,Categories,Message,Follows,Likes
from articles_preload import articles_business,articles_entertainment,articles_health,articles_technology
from app import app

# Create all tables
db.drop_all()
db.create_all()

default_quote1 = Quotes(quote="if you want something you never had,you have todo something you've never done")
default_quote2 = Quotes(quote="difficult roads lead to beautiful destinations")
default_quote3 = Quotes(quote="the best view comes after the hardest climb")
default_quote4 = Quotes(quote="a journey of a thousand miles must begin with a sample step")
default_quote5 = Quotes(quote="people will throw stones at you. Don't throw them back.Collect them all and build an empire")
default_quote6 = Quotes(quote="The Pessimist Sees Difficulty In Every Opportunity. The Optimist Sees Opportunity In Every Difficulty")
default_quote7 = Quotes(quote="You Learn More From Failure Than From Success. Don’t Let It Stop You. Failure Builds Character")
default_quote8 = Quotes(quote="It’s Not Whether You Get Knocked Down, It’s Whether You Get Up")
default_quote9 = Quotes(quote="If You Are Working On Something That You Really Care About, You Don’t Have To Be Pushed. The Vision Pulls You")
default_quote10 = Quotes(quote="People Who Are Crazy Enough To Think They Can Change The World, Are The Ones Who Do")
default_quote11 = Quotes(quote="Failure Will Never Overtake Me If My Determination To Succeed Is Strong Enough")
default_quote12 = Quotes(quote="Entrepreneurs Are Great At Dealing With Uncertainty And Also Very Good At Minimizing Risk")
default_quote13 = Quotes(quote="We May Encounter Many Defeats But We Must Not Be Defeated")
default_quote14 = Quotes(quote="Knowing Is Not Enough; We Must Apply. Wishing Is Not Enough; We Must Do")
default_quote15 = Quotes(quote="Imagine Your Life Is Perfect In Every Respect; What Would It Look Like?")
default_quote16 = Quotes(quote="We Generate Fears While We Sit. We Overcome Them By Action")
default_quote17 = Quotes(quote="Whether You Think You Can Or Think You Can’t, You’re Right")
default_quote18 = Quotes(quote="Security Is Mostly A Superstition. Life Is Either A Daring Adventure Or Nothing")
default_quote19 = Quotes(quote="The Man Who Has Confidence In Himself Gains The Confidence Of Others")
default_quote20 = Quotes(quote="The Only Limit To Our Realization Of Tomorrow Will Be Our Doubts Of Today")
default_quote21 = Quotes(quote="Creativity Is Intelligence Having Fun")

db.session.add_all([
    default_quote1,
    default_quote2,
    default_quote3,
    default_quote4,
    default_quote5,
    default_quote6,
    default_quote7,
    default_quote8,
    default_quote9,
    default_quote10,
    default_quote11,
    default_quote12,
    default_quote13,
    default_quote14,
    default_quote15,
    default_quote16,
    default_quote17,
    default_quote18,
    default_quote19,
    default_quote20,
    default_quote21])

db.session.add(default_quote1)

db.session.commit()

default_user1 = User.register(
    "shuminzhou",
    "smz121@gmail.com",
    "shuminzhou",
    "Shumin",
    "Zhou",
    "if you want something you never had,you have todo something you've never done",
    "male",
    "/static/avatar/avatar1.jpeg",
    300)

default_user2 = User.register(
    "nickzhou",
    "smz122@gmail.com",
    "shuminzhou",
    "Nick",
    "Yang",
    "difficult roads lead to beautiful destinations",
    "male",
    "/static/avatar/avatar2.jpeg",
    250)

default_user3 = User.register(
    "stephenzhou",
    "smz123@gmail.com",
    "shuminzhou",
    "Stephen",
    "Lee",
    "the best view comes after the hardest climb",
    "male",
    "/static/avatar/avatar3.jpeg",
    200)


db.session.add(default_user1)
db.session.add(default_user2)
db.session.add(default_user3)
db.session.commit()

business = Categories(category="business",description="deafult article all about business")
db.session.add(business)
db.session.commit()
entertainment = Categories(category="entertainment",description="default article all about entertainment")
db.session.add(entertainment)
db.session.commit()
health = Categories(category="health",description="deafult articles all about health")
db.session.add(health)
db.session.commit()
technology = Categories(category="technology",description="default articles all about technology")
db.session.add(technology)
db.session.commit()

default_business = [Articles(author=article["author"],title=article["title"],category=1,description=article["description"],cover_url=article["cover_url"],content=article["content"]) for article in articles_business]
db.session.add_all(default_business)
default_entertainment = [Articles(author=article["author"],title=article["title"],category=2,description=article["description"],cover_url=article["cover_url"],content=article["content"]) for article in articles_entertainment]
db.session.add_all(default_entertainment)
default_health = [Articles(author=article["author"],title=article["title"],category=3,description=article["description"],cover_url=article["cover_url"],content=article["content"]) for article in articles_health]
db.session.add_all(default_health)
default_technology = [Articles(author=article["author"],title=article["title"],category=4,description=article["description"],cover_url=article["cover_url"],content=article["content"]) for article in articles_technology]
db.session.add_all(default_technology)
db.session.commit()

message1 = Message(text="Month seat sea role something. Field however suggest entire",timestamp="2021-07-21 11:04:53.522807",user_id=1)
message2 = Message(text="Whole rich cut. Claim reason sport computer. Plan arm night our find. Put character member level method price",timestamp="2021-07-20 11:04:53.522807",user_id=1)
message3 = Message(text="From seek argue inside prepare. Almost off kid record employee air",timestamp="2021-07-24 11:04:53.522807",user_id=1)
db.session.add_all([message1,message2,message3])
db.session.commit()

message6 = Message(text="Population base security shake single example every. Loss nice indeed large perform size. Space simple fill capital hold final catch impact",timestamp="2021-07-21 11:04:53.522807",user_id=2)
message7 = Message(text="Challenge thought discuss final though feeling. Little best cost data type require own perform",timestamp="2021-07-20 11:04:53.522807",user_id=2)
message8 = Message(text="Step clearly official major. Huge leader want big health not. Soon owner population open hair. Determine beat find true",timestamp="2021-07-24 11:04:53.522807",user_id=2)
db.session.add_all([message6,message7,message8])
db.session.commit()

message11 = Message(text="Son his yard important behavior. Size response time front. Similar ahead arm gun which Mr third",timestamp="2021-07-21 11:04:53.522807",user_id=3)
message12 = Message(text="Security ahead situation. Cold southern nature story may affect fly thousand",timestamp="2021-07-20 11:04:53.522807",user_id=3)
message13 = Message(text="Whatever difficult continue reach leader end guy. Four religious never end want manage president. Speech from operation talk end reach",timestamp="2021-07-24 11:04:53.522807",user_id=3)
db.session.add_all([message11,message12,message13])
db.session.commit()