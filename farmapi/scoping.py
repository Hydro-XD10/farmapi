"""Shared serializer helper for object-level create/update security.

Problem: get_queryset() in the viewsets scopes what a user can *list/read/update/
delete*, but on CREATE the client supplies parent ids (farm/crop/category) in the
body. Without a check, a user could POST a crop/task/transaction referencing SOMEONE
ELSE'S farm id — injecting rows into another user's account.

Fix: restrict each foreign-key field's queryset to objects the requesting user is
allowed to reference. DRF then rejects any id outside that set with a clean 400
("object does not exist"), for both create and update, without leaking whether the
id exists for another user.

Usage: mix this in and declare `owner_scoped_fields` mapping a field name to a
callable(user) -> queryset.
"""


class OwnerScopedSerializerMixin:
    owner_scoped_fields = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            for field_name, get_queryset in self.owner_scoped_fields.items():
                if field_name in self.fields:
                    self.fields[field_name].queryset = get_queryset(user)
