# Brněnské (jihomoravské) jízdní řády

Data z [data.brno.cz](https://data.brno.cz/datasets/j%C3%ADzdn%C3%AD-%C5%99%C3%A1d-ids-jmk-ve-form%C3%A1tu-gtfs-gtfs-timetable-data/about) ve formátu [GTFS](https://developers.google.com/transit/gtfs/reference/)

Výcuc z dokumentace výše:
- `routes.txt`
    -  číslo linky – ID linky (route_id)
    - route_short_name – číslo linky
- `trips.txt`
    - ID linky (route_id) - kam jede (konečná)
    - trip_id – ID cesty
    - (volitelně) service_id – ID obsluhy, kde calendar.txt udává, kdy daná obsluha platí. Nejdříve naprogramujte bez přihlédnutí ke kalendáři (předpokládejte, že v jeden den jezdí spoje ze všech dnů), zbyde-li čas, vyfiltrujte jen na spoje, které jezdí v pondělí.
- `stops.txt`
    - stop_id: ID zastávky (resp. konkrétního nástupiště)
    - parent_station je stop_id hlavní zastávky – v některých případech má zastávka více podzastávek, když je například více nástupišť. Vynecháváte-li transfers.txt, berte místo každé ze zastávek jen její parent_station, existuje-li.
    - stop_name: jméno zastávky
- `stop_times.txt`: Časy odjezdů jednotlivých spojů (cest) z jednotlivých zastávek.
    - ID cesty trip_id
    - arrival time
    - departure time
    - stop_id
- (volitelně) transfers.txt: pěší přechod z jedné zastávky na druhou a jak dlouho trvá. každá zastávka může mít více nástupišť, mezi nimi je nutné se transferovat. Každé nástupiště má jednu stop_id. Lze vynechat.

**Úkol**: napište funkci, která dostane ID zastávky, čas a počet minut vrátí množinu všech zastávek, na které se v danou dobu dá za daný počet minut dostat.

Neřešte efektivitu programu. Jádro úkolu je prohledávání do šířky – během prohledávání si držíte haldu, ze které vybíráte zastávku a do haldy přidáváte všechny zastávky, na které jste schopni se z ní dostat. V každém kroku z haldy vytáhnete zastávku, na které se dostanete za nejkratší dobu a zároveň jste ji zatím nezpracovali a zpracujete ji – do haldy a množiny výsledků přidáte každou zastávku, na kterou se z ní lze přímo dostat. Doporučuju použití modulu heapq.

Pracujete ve dvojicích. Nejdřív se společně dohodněte na signaturách funkcí a následně si rozdělte práci – jeden může programovat hledání, druhý získávání dat z textových (CSV) souborů, které se vám později může hodit. Nebo můžete zkusit pair programming – jeden ovládá klávesnici, druhý "naviguje" a po chvíli se vystřídáte.

V souboru sol.py máte k dispozici kostru řešení.

Kód si můžete stáhnout jako ZIP pod zeleným tlačítkem Code -> Download ZIP.

## Práce ve dvojici:

Neumíte git, který je taky složitý jak mlátička, takže pokud s ním nemáte zkušenosti, nedoporučuju ho.

Na sdílení kódu můžete použít [Live Share](https://marketplace.visualstudio.com/items?itemName=MS-vsliveshare.vsliveshare), pokud používáte VSCode, nebo Repl.it.

### Máte hotovo?

Rozšiřte hledání do šířky tak, aby bylo možné najít nejkratší trasu do každé ze zastávek, do které jsme se stihli do časového limitu dostat. Máte tak hledání nejkratší trasy.

Zakomponujte transfery z `transfers.txt` (pak už nemusíte vždycky brát v úvahu jen kanonickou variantu zastávky) nebo berte v úvahu, které spoje jezdí v který den podle `calendar.txt`.
