from django import forms

from django_filters import MethodFilter, FilterSet

from apps.mentions.models import ToDo, Mention


class ResolvedFilter(FilterSet):
    """Filter for TODOs by it's status.

    Model has Boolean field `is_closed` which we interpret as status of the
    TODO: resolved or unresolved.

    """
    STATUS_CHOICES = (
        ('all', 'All'),
        ('resolved', 'Resolved'),
        ('unresolved', 'Unresolved'),
    )

    status = MethodFilter(
        action='filter_status',
        widget=forms.widgets.Select(choices=STATUS_CHOICES,
                                    attrs={'class': 'form-control'}))

    class Meta:
        model = ToDo
        fields = ['status']

    def filter_status(self, queryset, value):
        """Method for filtering TODOs by status.

        Args:
          queryset: QuerySet of TODOs
          value: value of the status (all, resolved or unresolved)

        Returns:
          QuerySet: filtered TODOs

        """
        if value == 'resolved':
            return queryset.filter(is_closed=True)
        if value == 'unresolved':
            return queryset.filter(is_closed=False)
        return queryset


class AssignedFilter(FilterSet):
    """Filter to show assigned or unassigned mentions.

    Should were used pretty tools from  StatusModel manager, but
    would will use not good way for filtering. Bad 'choices' were defined
    in model.

    """
    # choices for Mentions statuses
    MENTIONS_CHOICES = (
        ('all', 'All'),
        ('assigned', 'Assigned'),
        ('unassigned', 'Unassigned'),
        ('flagged', 'Not Mine')
    )

    mention_status = MethodFilter(
        action='filter_status',
        widget=forms.widgets.Select(choices=MENTIONS_CHOICES,
                                    attrs={'class': 'form-control'}))

    class Meta:
        model = ToDo
        fields = ['mention_status']

    def filter_status(self, queryset, value):
        value = value.lower()

        if value == Mention.ASSIGNED.lower():
            return queryset.filter(status=Mention.ASSIGNED)
        if value == Mention.UNASSIGNED.lower():
            return queryset.exclude(
                status__in=[Mention.ASSIGNED, Mention.FLAGGED]
            )
        if value == Mention.FLAGGED.lower():
            return queryset.filter(status=Mention.FLAGGED)

        return queryset
