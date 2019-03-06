from django.utils.translation import gettext as _
from collections import OrderedDict

DEFAULT_AFFILIATION = {("studente [student, member]") : ["student", "member"]}

idem_affiliation_map_extended = {
_('assistente universitario [staff, member]'): ['staff', 'member'],
_('associato (ad es. CNR) [member]'): ['member'],
_('cessato'): [],
_('collaboratore coordinato continuativo [staff, member]'): ['staff', 'member'],
_('collaboratore linguistico [staff, member]'): ['staff', 'member'],
_("consorziato (membro del consorzio a cui l'ente appartiene) [member]"): ['member'],
_('convenzionato (cliente delle convenzioni) [affiliate]'): ['affiliate'],
_('cultore della materia [staff, member]'): ['staff', 'member'],
_('dipendente [staff, member]'): ['staff', 'member'],
_('dipendente altra università [member]'): ['member'],
_('dipendente altro ente di ricerca [member]'): ['member'],
_('dipendente azienda ospedaliera/policlinico [member]'): ['member'],
_('dipendente di altra azienda sanitaria [member]'): ['member'],
_('direttore amministrativo [staff, member]'): ['staff', 'member'],
_('dirigente [staff, member]'): ['staff', 'member'],
_('dirigente a contratto [staff, member]'): ['staff', 'member'],
_('dirigente di ricerca [staff, member]'): ['staff', 'member'],
_('dirigente tecnologo [staff, member]'): ['staff', 'member'],
_('docente a contratto [staff, member]'): ['staff', 'member'],
_('dottorando [staff, member, student]'): ['staff', 'member', 'student'],
_('dottorando di altra università (consorziata) [member]'): ['member'],
_('esperto linguistico [staff, member]'): ['staff', 'member'],
_('fornitore (dipendente o titolare delle ditte fornitrici) [affiliate]'): ['affiliate'],
_('interinale [staff, member]'): ['staff', 'member'],
_('ispettore generale [affiliate]'): ['affiliate'],
_('laureato frequentatore/collaboratore di ricerca (a titolo gratuito) [member]'): ['member'],
_('lavoratore occasionale (con contratto personale senza partita iva) [staff, member]'): ['staff','member'],
_('lettore di scambio [member]'): ['member'],
_('libero professionista (con contratto personale con partita iva) [staff, member]'): ['staff','member'],
_('ospite / visitatore [affiliate]'): ['affiliate'],
_('personale tecnico-amministrativo [staff, member]'): ['staff', 'member'],
_('personale tecnico-amministrativo a tempo determinato [staff, member]'): ['staff','member'],
_('primo ricercatore [staff, member]'): ['staff', 'member'],
_('primo tecnologo [staff, member]'): ['staff', 'member'],
_('professore associato [staff, member]'): ['staff', 'member'],
_('professore emerito [member]'): ['member'],
_('professore incaricato esterno [staff, member]'): ['staff', 'member'],
_('professore incaricato interno [staff, member]'): ['staff', 'member'],
_('professore ordinario [staff, member]'): ['staff', 'member'],
_('ricercatore [staff, member]'): ['staff', 'member'],
_('specializzando [staff, member, student]'): ['staff', 'member', 'student'],
_('studente [student, member]'): ['student', 'member'],
_('studente erasmus in ingresso [student]'): ['student'],
_('studente fuori sede (tesista, tirocinante, ...) [student, member]'): ['student','member'],
_('studente laurea specialistica [student, member]'): ['student', 'member'],
_('studente master [student, member]'): ['student', 'member'],
_('studente siss [student, member]'): ['student', 'member'],
_('supervisore siss [staff, member]'): ['staff', 'member'],
_('supplente docente [staff, member]'): ['staff', 'member'],
_('tecnologo [staff, member]'): ['staff', 'member'],
_('titolare di assegno di ricerca [staff, member]'): ['staff', 'member'],
_('titolare di borsa di studio [member]'): ['member'],
_('tutor [staff, member]'): ['staff', 'member'],
_('volontario servizio civile nazionale [member]'): ['member']
}


idem_affiliation_map = {
_('dipendente, \
professore, ricercatore, \
titolare di assegno di ricerca, \
tutor, \
assistente universitario, \
collaboratore coordinato continuativo, \
collaboratore linguistico, \
cultore della materia'): ['staff', 'member'],

_('associato (ad es. CNR), \
consorziato (membro del consorzio a cui l\'ente appartiene), \
dipendente altra università o ente di \
ricerca o azienda sanitaria/ospedaliera/policlinico, \
dottorando di altra università (consorziata), \
laureato frequentatore/collaboratore di ricerca (a titolo gratuito), \
'): ['member'],

_('cessato'): [],

_('convenzionato (cliente delle convenzioni), \
fornitore (dipendente o titolare delle ditte fornitrici), \
ispettore, ospite / visitatore'): ['affiliate'],

_('lettore di scambio, \
titolare di borsa di studio, \
volontario servizio civile nazionale'): ['member'],

_('studente erasmus in ingresso [student]'): ['student'],

_('dottorando, specializzando'): ['staff', 'member', 'student'],

_('studente, \
studente fuori sede (tesista, tirocinante, ...), \
studente laurea specialistica, \
studente master, \
studente siss'): ['student', 'member'],
}


IDEM_AFFILIATION_MAP = OrderedDict(DEFAULT_AFFILIATION)
IDEM_AFFILIATION_MAP.update(OrderedDict(sorted(idem_affiliation_map.items(), key=lambda t: t[0])))
