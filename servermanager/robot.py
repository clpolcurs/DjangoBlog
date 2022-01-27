import os
import re

import jsonpickle
from werobot import WeRoBot
from werobot.replies import ArticlesReply, Article
from django.conf import settings
from djangoblog.utils import get_sha256
from servermanager.api.blogapi import BlogApi
from servermanager.api.commonapi import TuLing
from servermanager.models import Commands
from .MemcacheStorage import MemcacheStorage

robot = WeRoBot(token=os.environ.get('DJANGO_WEROBOT_TOKEN')
                      or 'lylinux', enable_session=True)
memstorage = MemcacheStorage()
if memstorage.is_available:
    robot.config['SESSION_STORAGE'] = memstorage
else:
    from werobot.session.filestorage import FileStorage
    import os
    from django.conf import settings

    if os.path.exists(os.path.join(settings.BASE_DIR, 'werobot_session')):
        os.remove(os.path.join(settings.BASE_DIR, 'werobot_session'))
    robot.config['SESSION_STORAGE'] = FileStorage(filename='werobot_session')
blogapi = BlogApi()
tuling = TuLing()


def convert_to_articlereply(articles, message):
    reply = ArticlesReply(message=message)
    from blog.templatetags.blog_tags import truncatechars_content
    for post in articles:
        imgs = re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:png|jpg)', post.body)
        imgurl = imgs[0] if imgs else ''
        article = Article(
            title=post.title,
            description=truncatechars_content(post.body),
            img=imgurl,
            url=post.get_full_url()
        )
        reply.add_article(article)
    return reply


@robot.filter(re.compile(r"^\?.*"))
def search(message, session):
    s = message.content
    searchstr = str(s).replace('?', '')
    result = blogapi.search_articles(searchstr)
    if result:
        articles = list(map(lambda x: x.object, result))
        return convert_to_articlereply(articles, message)
    else:
        return 'No related articles were found.'


@robot.filter(re.compile(r'^category\s*$', re.I))
def category(message, session):
    categories = blogapi.get_category_lists()
    content = ','.join(map(lambda x: x.name, categories))
    return 'All article categories：' + content


@robot.filter(re.compile(r'^recent\s*$', re.I))
def recents(message, session):
    articles = blogapi.get_recent_articles()
    return convert_to_articlereply(articles, message) if articles else "No articles yet"


@robot.filter(re.compile('^help$', re.I))
def help(message, session):
    return '''欢迎关注!
            默认会与图灵机器人聊天~~
        你可以通过下面这些命令来获得信息
        ?关键字搜索文章.
        如?python.
        category获得文章分类目录及文章数.
        category-***获得该分类目录文章
        如category-python
        recent获得最新文章
        help获得帮助.
        weather:获得天气
        如weather:西安
        idcard:获得身份证信息
        如idcard:61048119xxxxxxxxxx
        music:音乐搜索
        如music:阴天快乐
        PS:以上标点符号都不支持中文标点~~
        '''


@robot.filter(re.compile(r'^weather\:.*$', re.I))
def weather(message, session):
    return "Building in progress ..."


@robot.filter(re.compile(r'^idcard\:.*$', re.I))
def idcard(message, session):
    return "Building in progress .."


@robot.handler
def echo(message, session):
    handler = MessageHandler(message, session)
    return handler.handler()


class CommandHandler:
    def __init__(self):
        self.commands = Commands.objects.all()

    def run(self, title):
        cmd = list(
            filter(
                lambda x: x.title.upper() == title.upper(),
                self.commands))
        if cmd:
            return self.__run_command__(cmd[0].command)
        else:
            return "No related command found, please enter helpme for help."

    def __run_command__(self, cmd):
        try:
            return os.popen(cmd).read()
        except BaseException:
            return 'Command execution error!'

    def get_help(self):
        return ''.join('{c}:{d}\n'.format(c=cmd.title, d=cmd.describe) for cmd in self.commands)


cmdhandler = CommandHandler()


class MessageHandler:
    def __init__(self, message, session):
        userid = message.source
        self.message = message
        self.session = session
        self.userid = userid
        try:
            info = session[userid]
            self.userinfo = jsonpickle.decode(info)
        except BaseException:
            userinfo = WxUserInfo()
            self.userinfo = userinfo

    @property
    def is_admin(self):
        return self.userinfo.isAdmin

    @property
    def is_password_set(self):
        return self.userinfo.isPasswordSet

    def savesession(self):
        info = jsonpickle.encode(self.userinfo)
        self.session[self.userid] = info

    def handler(self):
        info = self.message.content

        if self.userinfo.isAdmin and info.upper() == 'EXIT':
            return self._extracted_from_handler_5("Exit successfully")
        if info.upper() == 'ADMIN':
            self.userinfo.isAdmin = True
            self.savesession()
            return "Enter administrator password"
        if self.userinfo.isAdmin and not self.userinfo.isPasswordSet:
            passwd = '123' if settings.TESTING else settings.WXADMIN
            if passwd.upper() == get_sha256(get_sha256(info)).upper():
                self.userinfo.isPasswordSet = True
                self.savesession()
                return "The verification is passed, please enter the command or the command code to be executed: " \
                       "Enter helpme for help "
            else:
                if self.userinfo.Count >= 3:
                    return self._extracted_from_handler_5("Exceeded the number of verifications")
                self.userinfo.Count += 1
                self.savesession()
                return "Authentication failed, please re-enter the administrator password:"
        if self.userinfo.isAdmin and self.userinfo.isPasswordSet:
            if self.userinfo.Command != '' and info.upper() == 'Y':
                return cmdhandler.run(self.userinfo.Command)
            if info.upper() == 'HELPME':
                return cmdhandler.get_help()
            self.userinfo.Command = info
            self.savesession()
            return "Confirm execution: " + info + " command?"
        return tuling.getdata(info)

    # TODO Rename this here and in `handler`
    def _extracted_from_handler_5(self, arg0):
        self.userinfo = WxUserInfo()
        self.savesession()
        return arg0


class WxUserInfo():
    def __init__(self):
        self.isAdmin = False
        self.isPasswordSet = False
        self.Count = 0
        self.Command = ''


"""
@robot.handler
def hello(message, session):
    blogapi = BlogApi()
    result = blogapi.search_articles(message.content)
    if result:
        articles = list(map(lambda x: x.object, result))
        reply = convert_to_articlereply(articles, message)
        return reply
    else:
        return '没有找到相关文章。'
"""
