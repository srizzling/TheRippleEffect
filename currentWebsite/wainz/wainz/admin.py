from wainz.models import Image, ImageComment, Tag
from django.contrib import admin
from voting.models import Vote

def approve(modeladmin, request, queryset):
    queryset.update(is_approved=True)

def unapprove(modeladmin, request, queryset):
    queryset.update(is_approved=False)

def sticky(modeladmin, request, queryset):
    queryset.update(is_sticky=True)

def unsticky(modeladmin, request, queryset):
    queryset.update(is_sticky=False)

class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'object', 'vote')
    list_filter = ('content_type', 'vote')
    radio_fields = { 'vote': admin.VERTICAL }

class ImageAdmin(admin.ModelAdmin):
    def tags_(self, obj):
        return ', '.join(["`%s'" % v[1] for v in obj.tags.get_query_set().values_list()])
    tags_.admin_order_field="tags__tag_text"
    def vote_num(self, obj):
        return Vote.objects.get_weighted_score(obj)['num_votes']
    def vote_sum(self, obj):
        return Vote.objects.get_weighted_score(obj)['score']
    def weight(self, obj):
        return Vote.objects.get_weighted_score(obj)['weight']
    list_display = ('image_name', 'is_approved', 'tags_', 'submitter', 'vote_num', 'vote_sum', 'weight', 'is_sticky')
    list_filter = ('is_approved', 'is_sticky',)

    search_fields = ['tags__tag_text', 'submitter__username', 'image_name', 'image_description']

    readonly_fields = ('extension', 'image_path')

    actions = (approve, unapprove, sticky, unsticky)

    # TODO Working joined queryset

class ImageCommentAdmin(admin.ModelAdmin):
    list_display = ('comment_text', 'image', 'submitter', 'submission_date')

admin.site.unregister(Vote)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(ImageComment, ImageCommentAdmin)
admin.site.register(Tag)
