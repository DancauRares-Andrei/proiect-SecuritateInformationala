from peewee import *
db=MySQLDatabase(database='si_proiect',user='rares',password='rares',host='localhost',port=3306)
class Chei(Model):
    CheieID = AutoField(primary_key=True)
    CheieCriptare = CharField(max_length=128)
    CheieDecriptare = CharField(max_length=128)    
    class Meta:
        database = db
class Frameworkuri(Model):
    FrameworkID = AutoField(primary_key=True)
    Nume = CharField(max_length=128) 
    class Meta:
        database = db
class Algoritmi(Model):
    AlgoritmID = AutoField(primary_key=True)
    Nume = CharField(max_length=128)
    CheieID = ForeignKeyField(Chei, backref='cheie_algoritm')
    FrameworkID = ForeignKeyField(Frameworkuri, backref='framework_algoritm') 
    class Meta:
        database = db
class Fisiere(Model):
    FisierID = AutoField(primary_key=True)
    AlgoritmID = ForeignKeyField(Algoritmi, backref='algoritm_fisier')
    Cale = CharField(max_length=255,unique=True)
    Criptat = BooleanField()
    Timp = BigIntegerField()#timp stocat ca milisecunde
    Hash = CharField(max_length=65)
    UsedRAM = CharField(max_length=20)#Stocat ca valoare numerica urmata de MB
    class Meta:
        database = db
db.connect()
if not Chei.table_exists() or not Frameworkuri.table_exists() or not Algoritmi.table_exists() or not Fisiere.table_exists():
    db.create_tables([Chei,Frameworkuri,Algoritmi,Fisiere])
    try:
        framework=Frameworkuri.get(Frameworkuri.Nume == "OpenSSL")
    except Frameworkuri.DoesNotExist:
        Frameworkuri.create(Nume="OpenSSL")
        Frameworkuri.create(Nume="LibreSSL")
        Frameworkuri.create(Nume="Themis")
        Frameworkuri.create(Nume="GnuTLS")
