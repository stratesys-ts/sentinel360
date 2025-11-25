from django.db import models, transaction
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class CostCenter(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Project(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'PLANNED', _('Planned')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        LATE = 'LATE', _('Late')

    class Currency(models.TextChoices):
        USD = 'USD', _('USD - US Dollar')
        BRL = 'BRL', _('BRL - Brazilian Real')
        EUR = 'EUR', _('EUR - Euro')

    class Industry(models.TextChoices):
        AGRO_MINING = 'AGRO_MINING', _('Agro & Mining')
        BANKING_INSURANCE = 'BANKING_INSURANCE', _('Banking & Insurance')
        CONSUMER_GOODS = 'CONSUMER_GOODS', _('Consumer Goods')
        CPG_RETAIL = 'CPG_RETAIL', _('CPG & Retail')
        ENERGY_UTILITIES = 'ENERGY_UTILITIES', _('Energy & Utilities')
        HEALTH_SERVICES = 'HEALTH_SERVICES', _('Health Services')
        INDUSTRY_MANUFACTURING = 'INDUSTRY_MANUFACTURING', _('Industry - Manufacturing - Logistics')
        INFRASTRUCTURE_CONSTRUCTION = 'INFRASTRUCTURE_CONSTRUCTION', _('Infrastructure & Construction')
        LIFE_SCIENCES_CHEMICAL = 'LIFE_SCIENCES_CHEMICAL', _('Life Sciences & Chemical')
        PASSENGER_TRANSPORT = 'PASSENGER_TRANSPORT', _('Passenger Transport')
        PUBLIC_SECTOR = 'PUBLIC_SECTOR', _('Public Sector, Education Sv & NGOs')
        REAL_ESTATE = 'REAL_ESTATE', _('Real Estate')
        RETAIL_DISTRIBUTION = 'RETAIL_DISTRIBUTION', _('Retail & Distribution')
        SERVICES = 'SERVICES', _('Services')
        TELECOM_MEDIA = 'TELECOM_MEDIA', _('Telecom & Media')
        TRAVEL_HOTELS = 'TRAVEL_HOTELS', _('Travel & Hotels')

    # Simplified list of countries for Geography
    class Geography(models.TextChoices):
        BRAZIL = 'BR', _('Brazil')
        USA = 'US', _('United States')
        CANADA = 'CA', _('Canada')
        UK = 'GB', _('United Kingdom')
        GERMANY = 'DE', _('Germany')
        FRANCE = 'FR', _('France')
        SPAIN = 'ES', _('Spain')
        PORTUGAL = 'PT', _('Portugal')
        ARGENTINA = 'AR', _('Argentina')
        CHILE = 'CL', _('Chile')
        COLOMBIA = 'CO', _('Colombia')
        MEXICO = 'MX', _('Mexico')
        OTHER = 'OTHER', _('Other')

    name = models.CharField(max_length=200)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='client_projects')
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # New Fields
    external_access = models.BooleanField(default=False, verbose_name=_("External Access"))
    cost_center = models.ForeignKey(CostCenter, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name=_("Cost Center"))
    project_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects', verbose_name=_("Project Manager"))
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.BRL, verbose_name=_("Currency"))
    project_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_projects', verbose_name=_("Project Owner"))
    geography = models.CharField(max_length=5, choices=Geography.choices, default=Geography.BRAZIL, verbose_name=_("Geography"))
    industry = models.CharField(max_length=50, choices=Industry.choices, default=Industry.SERVICES, verbose_name=_("Industry"))

    team = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='team_projects', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'TODO', _('To Do')
        DOING = 'DOING', _('Doing')
        DONE = 'DONE', _('Done')

    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    public_id = models.PositiveIntegerField(unique=True, null=True, editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.public_id is None:
            with transaction.atomic():
                last = Task.objects.aggregate(models.Max('public_id'))['public_id__max'] or 0
                self.public_id = last + 1
        return super().save(*args, **kwargs)
