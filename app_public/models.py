from django.contrib.auth.models import User
from django.db import models
from django.contrib.flatpages.models import FlatPage


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
    start_date = models.DateField()
    end_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=5, decimal_places=2)
    date_paid = models.DateField()
    plan_id = models.CharField(max_length=20) # The id of the plan on braintree
    braintree_id = models.CharField(max_length=20) # The id of the subscription on braintree


class Account(models.Model):
    # TODO i don't think this should have a user...should it?
    user = models.ForeignKey(User)
    subscription = models.ForeignKey(Subscription)

    def __unicode__(self):
        return u'%s' % (self.user.username)


class Person(models.Model):
    user = models.ForeignKey(User)
    # openid identity string, used to find which User has logged in
    identity = models.TextField()
    friend = models.ManyToManyField('self', through='Relationship', symmetrical=False)
    signup_token = models.CharField(max_length=64)
    token_created = models.DateTimeField(auto_now_add=True)
    # customer_id for braintree which we can use in transactions and subscriptions
    customer_id = models.CharField(max_length=20)
    # FIXME - need to determine how to store this info in db
    # encrypt or hash ?
    """
    card_number = models.CharField(max_length=32, required = True)
    card_expiry_date = models.DateField(required = True)
    card_csv = models.CharField(max_length=3, required = True)
    yearly_total = models.IntegerField()
    yearly_reniew = models.BooleanField()
    total = models.IntegerField()
    """
    
    
    def get_customer_id(self):
        '''
        Return either our customer_id or None if we don't have one yet.
        '''
        return self.customer_id or None


class Relationship(models.Model):
    from_person = models.ForeignKey(Person, related_name='from_people')
    to_person = models.ForeignKey(Person, related_name='to_people')


# this is just so that the app-wide sample data works (we don't have data for it yet)
class Dev(models.Model):
    test = models.TextField()
