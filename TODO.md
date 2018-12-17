TODO
----

 - Unit tests
 - ListField non prende verbose_name (labels in modeladmin) -> NO: dipende dalla dichiarazione del form!
 - aggregate lookup for evaluating min max on records
 
 - ["Il valore '20181106' ha un formato di data invalido. Deve essere nel formato AAAA-MM-GG."] (schacDateOfBirth)

 - Se uso una classe astratta le iterazioni di admin_action su queryset falliscono con "Unsupported dn lookup: in"
   ... bisogna fixare Base.py di django-ldapdb perchè inizializza di default dn anche quando è astratta!
