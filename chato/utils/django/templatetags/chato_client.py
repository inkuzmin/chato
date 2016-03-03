# import os
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def chato_widget(context, include_css=True, include_jquery=True):
    chat_html = template.loader.get_template('chat.html')
    context['include_css'] = include_css
    context['include_jquery'] = include_jquery
    return mark_safe(chat_html.render(context))
