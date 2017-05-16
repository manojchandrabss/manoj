import re
import json
import inspect
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models.query import QuerySet
from push_notifications.models import APNSDevice, GCMDevice
from push_notifications.gcm import GCMError
from push_notifications.apns import APNSError, APNSServerError


class EmailNotification(object):

    """
    Wrapper class for django send_mail function.
    Allow to store all email-specific data in class.
    Example usage:
    ```
    class EmailInviteSignForm(EmailNotification):
        subject = 'Invitation to fill Consent Form'
        template_name = 'consent_forms/email_send_form'
    ```

    You can set following properties:
        subject - subject of the email
        body_text - text body of the message (second parameter of send_mail
                                              function)
        body_html - html body of the message (html_message parameter of
                                              send_mail function)
        from_email - email whic will be used as sender's email
        to_emails - list of recepients (recepients_list parameter of send_mail
                                        function)
        template_name - name of the template with content of the email.
                        You should create two templates:
                            *template_name*.txt for text body of the message
                            *template_name*.html for html body
        context_variables - variables (dict) that would be used to render
                            text and html message body

        There is a method for getting all of this preperties, that you can
        override in child class.
        If you won't provide `template_name` attribute and do not redefine
        `get_body_text` and `get_body_html` methods, the template_name
        would be created automatically from child class name. For example:
            `MyEmailNotification` -> 'notifications/my_email_notification'

        To send the email, you just call .send() method, which has the same
        arguments as django send_mail. But you can call it without any
        params if you define everything within child class
    """

    subject = None
    body_text = None
    body_html = None
    from_email = None
    to_emails = None
    template_name = None
    context_variables = {}

    def __init__(self, context_variables={}):
        if context_variables:
            self.context_variables = context_variables

    def get_subject(self):
        return self.subject

    def get_from_email(self):
        if self.from_email:
            return self.from_email
        else:
            return settings.DEFAULT_FROM_EMAIL

    def get_to_emails(self):
        return self.to_emails

    def get_context_variables(self):
        return self.context_variables

    def convert_class_name(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def get_template_name(self):
        if self.template_name:
            return self.template_name
        else:
            return self.convert_class_name(self.__class__.__name__)

    def get_body_text(self):
        if self.body_text:
            return self.body_text
        else:
            template_name = self.get_template_name() + '.txt'
            return render_to_string(template_name,
                                    self.get_context_variables())

    def get_body_html(self):
        if self.body_html:
            return self.body_html
        else:
            template_name = self.get_template_name() + '.html'
            return render_to_string(template_name,
                                    self.get_context_variables())

    def send(self, subject=None, body_text=None, from_email=None,
             to_emails=None, html_message=None):
        if not subject:
            subject = self.get_subject()
        if not body_text:
            body_text = self.get_body_text()
        if not from_email:
            from_email = self.get_from_email()
        if not to_emails:
            to_emails = self.get_to_emails()
        if not html_message:
            html_message = self.get_body_html()

        if isinstance(to_emails, str):
            to_emails = [to_emails, ]

        if not subject:
            raise ValueError("Email subject not set")

        if not body_text:
            raise ValueError("body_text not set")

        if not from_email:
            raise ValueError("from_email not set")

        if not to_emails:
            raise ValueError("to_emails not set")

        return send_mail(subject, body_text, from_email, to_emails,
                         fail_silently=False, html_message=html_message)


class SimplePushNotification(object):

    """
    Class for simple push notifications.
    Example usage:
    ```
    # notifications.py
    class PostCreatedPNS(PushNotification):
        def __init__(self, post):
            self.recepients = post.readers.values_list('id')
            self.payload = {
                "message": "New post: {}".format(post.name)
                "extra":
                    {
                        "type": "post.created",
                        "post_id": post.id,
                    }
            }
    ...
    # somewhere else:
    PostCreatedPNS(new_post).send()
    ```
    This class shares the same logic as EmailNotification.
    So you can define:
        recepients - ID of users who should get this PNS
        payload - data that will be send to device
    """
    recepients = None
    payload = None

    def get_recepients(self):
        return self.recepients

    def get_payload(self):
        return self.payload

    def set_payload(self, payload):
        self.payload = payload
        try:
            pns_type = self.payload['extra']['type']
        except KeyError:
            raise ValueError('event type should be present inside push '
                             'notification payload')

    def send(self, recepients=None, payload=None):
        if not recepients:
            recepients = self.get_recepients()
        if not payload:
            payload = self.get_payload()

        try:
            pns_type = payload['extra']['type']
        except KeyError:
            raise ValueError('event type should be present inside push '
                             'notification payload')

        if not recepients:
            return

        gcmd = GCMDevice.objects.filter(user_id__in=recepients,
                                        active=True).distinct('registration_id')

        try:
            gcmd.send_message(**payload)
        except GCMError as e:
            pass

        apnsd = APNSDevice.objects.filter(user_id__in=recepients,
                                          active=True).distinct('registration_id')
        for x in apnsd:
            x.send_message(**payload)


class SMSNotification(object):

    """
    This class shares the same logic as EmailNotification.
    Twilio used as SMS backend, so this class properties the same as
    params of twilio.messages.create function
    """

    to = None
    body = None
    from_ = None
    template_name = None
    context_variables = {}

    def __init__(self, context_variables={}):
        if context_variables:
            self.context_variables = context_variables

    def get_from_(self):
        if self.from_:
            return self.from_
        else:
            return settings.TWILIO_FROM_NUMBER

    def get_to(self):
        return self.to

    def get_context_variables(self):
        return self.context_variables

    def convert_class_name(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def get_template_name(self):
        if self.template_name:
            return self.template_name
        else:
            return self.convert_class_name(self.__class__.__name__) + '.txt'

    def get_body(self):
        if self.body:
            return self.body
        else:
            template_name = self.get_template_name()
            return render_to_string(template_name,
                                    self.get_context_variables())

    def send(self, to=None, from_=None, body=None):
        if not to:
            to = self.get_to()
        if not from_:
            from_ = self.get_from_()
        if not body:
            body = self.get_body()

        if not body:
            raise ValueError("body not set")

        if not from_:
            raise ValueError("from not set")

        if not to:
            raise ValueError("to not set")

        return settings.TWILIO.messages.create(
            to=to, from_=from_,
            body=body
        )


class __PushNotificationMetaClass__(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(__PushNotificationMetaClass__, cls).__new__
        parents = [b for b in bases if isinstance(
            b, __PushNotificationMetaClass__)]
        # do not adjust any settings to PushNotifications class itself (it has
        # no parents)
        if not parents:
            return super_new(cls, name, bases, attrs)

        # adjust meta
        module = attrs.pop('__module__')
        meta = attrs.pop('Meta', None)
        new_class = super_new(cls, name, bases, {'__module__': module})

        # make sure Meta is defined per class
        if not meta:
            raise AttributeError('Meta class should be defined')

        if not hasattr(meta, 'required'):
            raise AttributeError(
                'Meta class should have required fields to be defined')

        # if Meta.type is not set in child class set it automatically to
        # converted value
        if not hasattr(meta, 'type'):
            meta.type = convert(name.strip(parents[0].__name__))

        # assign it back to new class
        new_class.Meta = meta

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        # assign function to check that incoming parameters are valid
        def _validate_required_params(self):
            diff = set(self.Meta.required).difference(set(self.__dict__))
            if diff:
                raise AttributeError(
                    "Provide the following kwargs to your init of the {}.__init__({}=value)".
                    format(name, list(diff).pop(0)))
        # add method to new_class
        new_class.add_to_class(
            '_validate_required_params', _validate_required_params)

        # return and init new class
        return new_class

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class PushNotification(object, metaclass=__PushNotificationMetaClass__):

    """
    Class used to send push notifications and wraps inside functionality
    to send APNS or GCM PNS

    Child class should have Meta class defined as follow

    class Meta:
        message = "Task Deleted!"
        type = "task.cancelled"
        badge = True

    Meta.badge is optional parameter only used by APNS functionality,
    if it's set to true, then child class also should implement get_badge
    method that should return the integer value for given push notification

    Meta.message and Meta.type are required parameters,
    however if Meta.type is not defined in child class, it will be assigned
    automatically in parent class via convert function inside
    PushNotification.get_payload class
    """

    def __init__(self, **kwargs):
        """
        :param recepients:
         This list (if provided) will overwrite list created by 
         child's get_recepients
        """

        self.__dict__ = dict(kwargs)
        recepients = kwargs.get('recepients', None)

        # this is defined inside meta class
        self._validate_required_params()

        # obtain recepients
        if not recepients:
            self.recepients = self.get_recepients()
        else:
            self.recepients = recepients

        # raise error if we don't know who to deliver PN
        payload = self.get_payload()
        if self.recepients:
            self.send(payload)

    def __str__(self):
        return json.dumps(self.payload)

    def get_recepients(self):
        """
        This method should be implemented in child class if you want to have
        a custom logic around getting a list of receipients
        :return:
            list of IDs of users
        """
        raise NotImplementedError('`get_recepients()` must be implemented.')

    def get_badge(self):
        """
        This method should be implemented in child class if you want to have
        a custom badge attached to APNS push notification. This is only
        required to be implemented in child class if Child's Meta.badge = True
        :return:
            integer, value of the badge to attach with APNS push notification
        """
        raise NotImplementedError(
            '`get_badge()` must be implemented if Meta.badge is set.')

    def get_payload(self, extra=None):
        if hasattr(self, 'payload'):
            return self.payload

        payload = {}
        payload['message'] = self.Meta.message
        payload['extra'] = extra
        payload['extra']['type'] = self.Meta.type
        self.payload = payload
        return self.payload

    def send(self, payload=None):
        """
        Send push notification
        :return:
        """
        if not payload:
            payload = self.get_payload()

        # this is only related to APNS endpoints
        badge = None
        # Should be implemented inside inherited class
        # This is only for APNS functionality
        if hasattr(self.Meta, 'badge'):
            badge = self.get_badge() if self.Meta.badge else None

        # deliver to GCM endpoints
        gcmd = GCMDevice.objects.filter(user_id__in=self.recepients,
            active=True).distinct('registration_id')
        try:
            gcmd.send_message(**payload)
        except GCMError as e:
            pass

        # deliver to APNS endpoints
        apnsd = APNSDevice.objects.filter(user_id__in=self.recepients,
            active=True).distinct('registration_id')
        for x in apnsd:
            x.send_message(badge=badge, **payload)

    def __call__(self, *args, **kwargs):
        self.send()
