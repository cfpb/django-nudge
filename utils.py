from reversion.models import Version

def latest_objects():
    """
    returns list of lastest versions for each distinct object
    """
     
    distinct_objects = Version.objects.values('object_id_int').distinct()
    latest = []
    for o in distinct_objects:
        latest_obj = Version.objects.filter(object_id_int=o['object_id_int']).order_by('-revision__date_created')[:1]
        latest.append(latest_obj[0])

    return latest