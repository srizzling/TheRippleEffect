from django import template

register = template.Library()

@register.inclusion_tag('wainz/components/twitter.html')
def twitter_component(account):
    return { "twitter_account": account }

@register.inclusion_tag('wainz/components/image_list.html')
def image_list_component(images_and_votes, images_length):
    return { "images_and_votes": images_and_votes, "images_length":images_length }
