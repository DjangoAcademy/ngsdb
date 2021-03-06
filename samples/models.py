from django.db import models
from django.contrib.auth.models import User
from ngsdbview.models import Author, Organism, Lifestage, Phenotype, Librarytype, Collaborator, Growthphase, Genotype

# Create your models here.
TEMPLATE_MATERIALS_CHOICES = (
    ('total RNA', 'total RNA'),
    ('polyA purified mRNA', 'polyA purified mRNA'),
    ('gDNA', 'gDNA'),
    ('Ribosome Bound RNA', 'Ribosome Bound RNA')
)

SAMPLE_TYPE_CHOICES = (
    ('RNA', 'RNA'),
    ('DNA', 'DNA'),
    ('cDNA', 'cDNA'),
)

CULTURE_METHOD_TYPE_CHOICES = (
    ('axenic-culture', 'axenic-culture'),
    ('intracellular-culture', 'intracellular-culture'),
    ('animal derived', 'animal derived'),
)

LIBRARYFILE_CATEGORY_CHOICES = (
    ('fastqqc', 'fastqqc'),
    ('rnaqc', 'rnaqc'),
    ('readcount_distri', 'readcount_distri')
)


class Bioproject(models.Model):
    bioproject_code = models.CharField(unique=True, max_length=12)
    organisms = models.CharField(max_length=100, blank=True)
    sharepoint_projectcode = models.CharField(blank=True, max_length=12)
    notes = models.TextField(max_length=400, blank=True)

    class Meta:
        ordering = ['organisms']
    def __unicode__(self):
        return unicode(self.bioproject_code)

class Biosample(models.Model):
    biosample_code = models.CharField(unique=True, max_length=12)
    organisms = models.CharField(max_length=100, blank=True)
    collected_on_test = models.DateField(null=False, blank=False)
    notes = models.TextField(max_length=400, blank=True)

    def __unicode__(self):
        return unicode(self.biosample_code)

class Protocol(models.Model):
    protocol_name = models.CharField(unique=True, max_length=50)
    protocol_file = models.FileField(upload_to="protocols", blank=True)
    protocol_link = models.URLField(max_length=1000, blank=True)
    notes = models.CharField(max_length=400, default=None)

    def __unicode__(self):
        return unicode(self.protocol_name)

    # todo-me remove this model


class Source(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    notes = models.TextField()

    def __unicode__(self):
        return unicode(self.name)

def get_bioanalyzer_upload_destination(instance, filename):
    return "bioanalyzer/{file}".format(file=filename)


class Sample(models.Model):
    sampleid = models.CharField(max_length=25, unique=True, db_index=True)
    samplename = models.CharField(max_length=20, db_index=True, default='None', help_text="Human readable name for the Sample")
    biosample = models.ForeignKey(Biosample, help_text="Local or NCBI assigned Biosample ID")
    sampletype = models.CharField(max_length=100, choices=SAMPLE_TYPE_CHOICES)
    label_ontube = models.CharField(max_length=250, db_index=True, blank=True, help_text="Text/Label found on the tube containing sample")
    organism = models.ForeignKey('ngsdbview.Organism', related_name="sample_organism", help_text="The organism/parasite sample is isolated from")
    lifestage = models.ForeignKey('ngsdbview.Lifestage', related_name="ngsdbview.lifestageS", help_text="Lifecycle stage of the parasites the sample is isolated from", verbose_name="Lifecycle Stage")
    growthphase = models.ForeignKey('ngsdbview.Growthphase', related_name="ngsdbview.growthphaseS")
    phenotype = models.CharField(max_length=254, default="wildtype", help_text="Define the phenotype. e.g., short and round")
    genotype = models.ForeignKey('ngsdbview.Genotype', related_name="ngsdbview.genotypeS", help_text="Eg., Wildtype, JBP2KO")
    collaborator = models.ForeignKey('ngsdbview.Collaborator', related_name="ngsdbview.collaboratorS")
    source = models.CharField(max_length=100, help_text="Eg., Subcutaneous Leishion of an adult male, Lab culture, chimeric mouse liver")
    sourcename = models.ForeignKey(Source)
    culture_method = models.CharField(max_length=100, choices=CULTURE_METHOD_TYPE_CHOICES, default="axenic-culture")
    treatment = models.CharField(max_length=100, help_text="Type of treatment and treatment duration. e.g., BrdU 10uM for 10mins or heatshock or pH")
    time_after_treatment = models.CharField(max_length=25, blank=True, help_text="The time between treatment and harvesting of cells. e.g., 10hrs, 10mins")
    collected_on = models.DateField(null=True, blank=True, verbose_name="Sample isolated on", help_text="Date the sample was isolated from cells")
    collected_at = models.CharField(max_length=100, blank=True, verbose_name="Sample isolated at", help_text="Name of the lab and country where the sample was isolated")
    collected_by = models.CharField(max_length=50, blank=True, help_text="Name of the person isolated the sample", verbose_name="Sample isolated by")
    collected_by_emailid = models.EmailField(max_length=254, blank=True, verbose_name="Sample isolated by : Email-id", help_text="Emailid of the person isolated the sample")
    isolation_method = models.CharField(max_length=100, blank=True, verbose_name="Sample isolation method", help_text="Enter the name of the procedure or entire method")
    date_received = models.DateField(null=True, blank=True, verbose_name="Date samples received at SBRI")
    sample_concentration = models.DecimalField(max_digits=10, decimal_places=4, blank=True, help_text="in ng/ul")
    sample_volume = models.DecimalField(max_digits=6, decimal_places=2,  blank=True, help_text="in ul")
    sample_quantity = models.DecimalField(max_digits=10, decimal_places=4,  blank=True, help_text="total quantity in ug")
    parent_sampleid = models.CharField(max_length=25, db_index=True, blank=True, verbose_name="Parent sampleid if its a dilution", help_text="Name of the parent sample this one is derived from")
    sample_dilution = models.CharField(max_length=25, blank=True, default="Original Concentration", help_text="times dilution created from original sample, referred in parent sampleid filed above. e.g., 1:100")
    biological_replicate_of = models.CharField(max_length=25, blank=True, default="No Replicate", help_text="comma separated sample names of its biological replicates, needed for original samples only, not for dilutions")
    bioanalyzer_analysis = models.FileField(upload_to=get_bioanalyzer_upload_destination, blank=True, help_text="Upload bioanalyzer trace file")
    freezer_location = models.CharField(max_length=100, blank=True, help_text="Name of the freezer, rack, box etc. e.g., -80/Drawer_3/Rack3/A3")
    is_clonal = models.BooleanField(default=False, verbose_name="Check this if the culture is clonal population", help_text="Are the cells cloned to single cell before growing for this library?")
    sample_notes = models.TextField(blank=True, help_text="Any other information related to sample, sample collection etc")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    author_modified = models.ForeignKey(User, verbose_name="Person Modified this entry last")

    class Meta:
        ordering = ['sampleid']
    def __unicode__(self):
        return unicode(self.sampleid)

    def bioanalyzer_file_link(self):
        if self.bioanalyzer_analysis:
            return "<a href='%s'>download</a>" % (self.bioanalyzer_analysis.url,)
        else:
            return "No attachment"

    bioanalyzer_file_link.allow_tags = True

class Library(models.Model):
    library_code = models.CharField(max_length=10, db_index=True, unique=True, blank=True, help_text="Only Settle BioMed\'s internal users may use this. eg. ES001, AH002")
    sampleid = models.ForeignKey(Sample, null=True)
    author = models.ForeignKey('ngsdbview.Author', related_name="ngsdbview.authors", help_text="Person constructed the library")
    collaborator = models.ForeignKey('ngsdbview.Collaborator', related_name="ngsdbview.collaborator", help_text="Initials of the PI collaborating on this project")
    bioproject = models.ForeignKey(Bioproject, help_text="Bioproject ID from NCBI")

    librarytype = models.ForeignKey('ngsdbview.Librarytype', related_name="ngsdbview.librarytype", help_text="Type of library to be constructed")
    template_material = models.CharField(max_length=200, choices=TEMPLATE_MATERIALS_CHOICES)
    protocol = models.ForeignKey('ngsdbview.Protocol', related_name="ngsdbview.protocol", help_text="Add a new protocol using '+' before selecting here. Use the Protocol additional notes to describe any changes in protocol")
    protocol_notes = models.TextField(blank=True, default="None")
    library_gelimage = models.FileField(upload_to="libraryimages", blank=True, default="NA", help_text="Upload annotated library image file")

    library_creation_date = models.DateField(blank=True, null=True)
    submitted_for_sequencing_on = models.DateField(blank=True, null=True)
    sequence_downloaded_on = models.DateField(blank=True, null=True)
    flowcell_number = models.CharField(max_length=15, blank=True)
    lane_number = models.CharField(max_length=3, blank=True)
    index_sequence = models.CharField(max_length=25, blank=True)
    fastqfile_name = models.CharField(max_length=254, blank=True, null=True)
    fastqfile_readcount = models.DecimalField(max_digits=25, decimal_places=2,  blank=True, null=True)
    fastqfile_md5sum = models.CharField(max_length=50, blank=True, null=True)
    fastqfile_size_inbytes = models.DecimalField(max_digits=50, decimal_places=2, blank=True, null=True)
    experiment_notes = models.TextField(blank=True,)

    suggested_reference_genome = models.CharField(max_length=100, blank=True, help_text="Name and version of genome to align the reads against", default="Genome: xxxxx ; Version: xxxx")
    note_for_analysis = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    author_modified = models.ForeignKey(User)

    class Meta:
        verbose_name_plural="Libraries"
    def __unicode__(self):
        return unicode(self.library_code)
    def libcode_samplename(self):
        if self.libcode_samplename:
            return "%s+'(+%s+')' "%(self.library_code, self.sampleid.samplename)

def get_libraryfile_upload_destination(instance, filename):
    return "libraryfiles/{id}/{file}".format(id=instance.library.library_code, file=filename)

class Libraryfile(models.Model):
    library = models.ForeignKey(Library, null=True)
    category = models.CharField(max_length=100, db_index=True, choices=LIBRARYFILE_CATEGORY_CHOICES, help_text="Broad level category for the file")
    subcategory = models.CharField(max_length=200, db_index=True, help_text="Sub level category for the file")
    file = models.FileField(upload_to=get_libraryfile_upload_destination, blank=True, help_text="Upload files related to a library")
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return unicode(self.library)

class Reserve(models.Model):
    author = models.ForeignKey(User)
    notes = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Reserve"
    def __unicode__(self):
        return unicode(self.author)

class Reservedcode(models.Model):
    reserve = models.ForeignKey(Reserve)
    code = models.CharField(max_length=5, help_text="Library or Samples code")

    def __unicode__(self):
        return unicode(self.code)
