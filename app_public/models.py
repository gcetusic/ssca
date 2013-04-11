from django.contrib.auth.models import User
from django.db import models
from django.contrib.flatpages.models import FlatPage
from django.utils import timezone


class MenuItem(models.Model):
    title = models.CharField(max_length=100)
    show_after = models.ForeignKey('self',
        null=True, blank=True, default=None,
        related_name="predecessor")
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child')

    def _recurse_for_parents(self, cat_obj):
        p_list = []
        if cat_obj.parent_id:
            p = cat_obj.parent
            p_list.append(p.title)
            more = self._recurse_for_parents(p)
            p_list.extend(more)
        if cat_obj == self and p_list:
            p_list.reverse()
        return p_list

    def get_separator(self):
        return ' -> '

    def _parents_repr(self):
        p_list = self._recurse_for_parents(self)
        return self.get_separator().join(p_list)
    _parents_repr.short_description = "Category parents"

    def _pre_save(self):
        p_list = self._recurse_for_parents(self)
        if self.title in p_list:
            raise "You must not save a category in itself!"

    def __repr__(self):
        p_list = self._recurse_for_parents(self)
        p_list.append(self.title)
        return self.get_separator().join(p_list)

    def __unicode__(self):
        return u'%s' % (self.__repr__())


class Image(models.Model):
    title = models.CharField(max_length=255)
    file = models.ImageField(upload_to='pages')

    def get_absolute_url(self):
        return (self.file and self.file.url) or ''

    def render(self):
        return """<img src="%s" alt="">""" % self.get_absolute_url()

    def __unicode__(self):
        return (self.file and self.file.url) or ''


class Page(FlatPage):
    picture = models.ManyToManyField(Image, null=True, blank=True, editable=True)
    show_after = models.ForeignKey('Page',
        null=True, blank=True, default=None,
        related_name="flatpage_predecessor",
        help_text="Page that this one should appear after (if any)")
    child_of = models.ManyToManyField(MenuItem,
        null=True, blank=True, default=None,
        related_name="flatpage_parent",
        help_text="Page that shis one should appear under (if any)")


class Subscription(models.Model):

    ELECTRONIC = "E"
    FIRST_CLASS = "First"
    BULK_MAIL = "Bulk"
    AIR_MAIL = "Air"
    SURFACE_MAIL = "Surface"

    SUBSCRIPTION_CHOICES = (
        (ELECTRONIC, 'Electronic'),
        ('US', (
                (FIRST_CLASS, 'First Class'),
                (BULK_MAIL, 'Bulk Mail'),
            )
        ),
        ('North America (Canada / Mexico)', (
                (AIR_MAIL, 'Air Mail'),
                (SURFACE_MAIL, 'Surface Mail'),
            )
        ),
    )

    subscription_type = models.CharField(max_length=150,
                                        choices=SUBSCRIPTION_CHOICES,
                                        default=ELECTRONIC
                                    )

    start_date = models.DateField()
    end_date = models.DateField(blank=True)
    amount_paid = models.DecimalField(max_digits=5, decimal_places=2)
    date_paid = models.DateField()


class Account(models.Model):
    subscription = models.ManyToManyField(Subscription)
    yearly_renew = models.BooleanField(default=True, verbose_name="Auto renew")
    joindate = models.DateField(default=timezone.now())
    last_renewed = models.DateTimeField()

    # FIXME - per subscription or per account?
    #expiration_date
    # source, cruise_status??? EXPLAIN

    # FIXME - need to determine how to store this info in db
    # encrypt or hash ?
    """
    card_number = models.CharField(max_length=32, required=True)
    card_expiry_date = models.DateField(required = True)
    card_csv = models.CharField(max_length=3, required=True)
    yearly_total = models.IntegerField()
    total = models.IntegerField()
    """


class Person(User):
    account = models.ForeignKey(Account, related_name="person_account")

    # openid identity string, used to find which User has logged in
    identity = models.TextField()
    friend = models.ManyToManyField('self', through='Relationship', symmetrical=False)

    membership_type = models.ForeignKey('MembershipType')

    def __unicode__(self):
        return u'%s' % (self.username)


class PersonInfo(models.Model):
    person = models.OneToOneField(Person, primary_key=True)
    middle_name = models.CharField(blank=True, max_length="35")
    address1 = models.CharField(max_length=150, verbose_name="Primary address")
    address2 = models.CharField(blank=True, max_length=150, verbose_name="Secondary address")
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=150, blank=True)
    postcode = models.IntegerField(max_length=50)
    country = models.CharField(max_length=50)
    phone1 = models.CharField(max_length=50, verbose_name="Primary phone number")
    phone2 = models.CharField(blank=True, max_length=50, verbose_name="Secondary phone number")
    fax = models.CharField(max_length=50)
    email1 = models.EmailField(max_length=50, verbose_name="Primary email address")
    email2 = models.EmailField(blank=True, max_length=50, verbose_name="Secondary email address")
    website = models.CharField(blank=True, max_length=150)


class Relationship(models.Model):
    from_person = models.ForeignKey(Person, related_name='from_people')
    to_person = models.ForeignKey(Person, related_name='to_people')


class MembershipType(models.Model):
    pass


# this is just so that the app-wide sample data works (we don't have data for it yet)
class Dev(models.Model):
    test = models.TextField()
