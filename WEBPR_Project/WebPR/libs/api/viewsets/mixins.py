import collections


class PushNotificationActionMixin(object):

    """
    Used to add functionality for sending push notification
    to any APIView or Viewset.
    You have 2 options to defined push notifications

    class Name(APIView):
        push_notification_classes = (TaskChatPushNotification, )

    or for a router's method like this:

    @detail_route(methods=['POST'], permission_classes=[IsAuthenticated])
    @parser_classes((JSONParser,))
    @push_notification(push_notification_classes=[NewTaskPushNotification, ])
    def dispute(self, request, *args, **kwargs):
        ....
        self.push_notification(key=Value, key2=Value2, ...)

    """

    def push_notification(self, **kwargs):
        action = getattr(self, self.action)

        if hasattr(action, 'push_notification_classes'):
            pnc = action.push_notification_classes
        elif hasattr(self, 'push_notification_classes'):
            pnc = self.push_notification_classes

        if pnc:
            if isinstance(pnc, collections.Iterable):
                for pn in pnc:
                    # Initiate and call push notifications in the same order
                    # as listed in pnc list/tuple
                    pn(**kwargs)
            # it's possible to pass a single class as the option (instead of
            # the iterable)
            elif (type(pnc).__name__ == '__PushNotificationMetaClass__' and
                    pnc.__base__.__name__ == 'PushNotification'):
                pnc(**kwargs)


class MultiSerializerViewSetMixin(object):

    def get_serializer_class(self):
        """
        Look for serializer class in self.serializer_action_classes, which
        should be a dict mapping action name (key) to serializer class (value),
        i.e.:

        class MyViewSet(MultiSerializerViewSetMixin, ViewSet):
            serializer_class = MyDefaultSerializer
            serializer_action_classes = {
               'list': MyListSerializer,
               'my_action': MyActionSerializer,
            }

            @action
            def my_action:
                ...

        If there's no entry for that action then just fallback to the regular
        get_serializer_class lookup: self.serializer_class, DefaultSerializer.

        Thanks gonz: http://stackoverflow.com/a/22922156/11440

        """

        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class CustomErrorMessagesMixin(object):

    """
    Replaces built-in validator messages with messages, defined in Meta class.
    This mixin should be inherited before the actual Serializer class
    in order to call __init__ method.

    Example of Meta class:

    >>> class Meta:
    >>>     model = User
    >>>     fields = ('url', 'username', 'email', 'groups')
    >>>     custom_error_messages_for_validators = {
    >>>         'username': {
    >>>             UniqueValidator: _('This username is already taken.'),
    >>>             RegexValidator: _('Invalid username')
    >>>         }
    >>>     }
    """

    def __init__(self, *args, **kwargs):
        # noinspection PyArgumentList
        super().__init__(*args, **kwargs)
        self.replace_validators_messages()

    def replace_validators_messages(self):
        for field_name, validators_lookup in self.custom_error_messages_for_validators.items():
            # noinspection PyUnresolvedReferences
            for validator in self.fields[field_name].validators:
                if type(validator) in validators_lookup:
                    validator.message = validators_lookup[type(validator)]

    @property
    def custom_error_messages_for_validators(self):
        meta = getattr(self, 'Meta', None)
        return getattr(meta, 'custom_error_messages_for_validators', {})
