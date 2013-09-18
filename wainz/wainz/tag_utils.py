from wainz.models import Tag

def TagsFromText(text_representation):
    '''
    Creates or retrives Tag objects from a comma separated
    list of tag values.
    '''
    #We split tags into those we already have in the DB, and those 
    #we must add. This saves duplicating tags and probably stops some
    #weird things from happening.
    tag_values = [x for x in text_representation.split(",") if x]
    tags = []
    existing_values = []
    new_values = []
    for tag_text in tag_values:
        tag_text = tag_text.strip()
        tag_text = tag_text.strip('[]')
        if tag_text in [x.tag_text for x in Tag.objects.all()]:
            existing_values.append(tag_text)
        else:
            new_values.append(tag_text)         
    #new values are saved, existing values are retrieved.
    for new_value in new_values:
        t = Tag()
        t.tag_text = new_value
        t.save()
        tags.append(t)
    for exists in existing_values:
        tags.append(Tag.objects.get(tag_text = exists)) 
    return tags
