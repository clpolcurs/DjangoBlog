from django.db import models


# Create your models here.
class Commands(models.Model):
    title = models.CharField('Command title', max_length=300)
    command = models.CharField('Command', max_length=2000)
    describe = models.CharField('Command describe', max_length=300)
    created_time = models.DateTimeField('Created at', auto_now_add=True)
    last_mod_time = models.DateTimeField('Modified at', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Command'
        verbose_name_plural = "Commands"


class EmailSendLog(models.Model):
    emailto = models.CharField('Recipient', max_length=300)
    title = models.CharField('Email title', max_length=2000)
    content = models.TextField('Email content')
    send_result = models.BooleanField('Result', default=False)
    created_time = models.DateTimeField('Created at', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Sending email log'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
