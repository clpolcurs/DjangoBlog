import logging

from djangoblog.utils import get_current_site
from djangoblog.utils import send_email

logger = logging.getLogger(__name__)


def send_comment_email(comment):
    site = get_current_site().domain
    subject = 'Thanks for your comment'
    article_url = "https://{site}{path}".format(
        site=site, path=comment.article.get_absolute_url())
    html_content = """
                   <p>Thank you very much for your comment on this site</p>
                   You can visit
                   <a href="%s" rel="bookmark">%s</a>
                   to see your comments,
                   Thank you！
                   <br />
                   If the link above does not work, please copy the link to your browser.
                   %s
                   """ % (article_url, comment.article.title, article_url)
    tomail = comment.author.email
    send_email([tomail], subject, html_content)
    try:
        if comment.parent_comment:
            html_content = """
                    Your comment on <a href="%s" rel="bookmark">%s</a> <br/> %s <br/> received a reply. Check it out.
                    <br/>
                    If the link above does not work, please copy the link to your browser.
                    %s
                    """ % (article_url, comment.article.title, comment.parent_comment.body, article_url)
            tomail = comment.parent_comment.author.email
            send_email([tomail], subject, html_content)
    except Exception as e:
        logger.error(e)
