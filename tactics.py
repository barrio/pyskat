#!/usr/bin/env python
# Last Change: Jul 14, 2009

from pyskatrc import *

def fehl(trumpf):
    return [x for x in [KARO, HERZ, PIK, KREUZ] if x != trumpf]

def smallest(farbe):
    return farbe[-1]

def splitCards(cards, trumpf):
    dic = {}
    # fehl karten aufsplitten
    for farbe in fehl(trumpf):
        clist = []
        for card in cards:
            if card.suit == farbe and card.rank != BUBE:
                clist.append(card)
        clist.sort(reverse=True)
        dic[farbe] = clist
    # trumpf aufsplitten
    clist = []
    for card in cards:
        if card.suit == trumpf or card.rank == BUBE:
            clist.append(card)
    clist.sort(reverse=True)
    dic[trumpf] = clist
    return dic

def rateCards(spieler):
    buben = 0
    max_farbe = 0
    max_fehlass = 0

    # TODO: rating fuer farben stechen

    for card in spieler.cards:
        if card.rank == BUBE:
            buben += 1
        elif card.suit == spieler.getBestSuit():
            max_farbe += 1
        elif card.rank == ASS:
            max_fehlass += 1

    return buben*1.5+max_farbe+max_fehlass

def aufspielen(spieler, tisch):
    # eigene karten 
    own = {}
    own = splitCards(spieler.cards, tisch.trumpf)

    # gespielte karten
    played = {}
    if len(tisch.playedStiche) > 0:
        clist = []
        for stiche in tisch.playedStiche:
            clist.extend(stiche)
        played = splitCards(clist, tisch.trumpf)

    if spieler.re == True:
        print "%s (Re) kommt raus" % spieler.name
    else:
        print "%s (Kontra) kommt raus" % spieler.name

    # ass spielen, wenn kein trumpf
    ace = None
    for card in spieler.cards:
        if card.rank == ASS and card.suit != tisch.trumpf:
            if not ace:
                ace = card
            # wenn mehrere, dann die kuerzeste farbe
            else:
                # TODO
                pass
    if ace:
        return ace

    # kurzen fehl spielen
    count = 12
    to_play = 0
    for farbe in fehl(tisch.trumpf):
        if len(own[farbe]) < count and len(own[farbe]) != 0:
            to_play = farbe
    # TODO: 10 spielen, wenn ass schon raus
    #       stechen/schmieren kalkulieren
    if to_play:
        return own[to_play][0]

    # hohen trumpf spielen
    # TODO: gespielte truempfe einberechnen
    return own[tisch.trumpf][0]

def bedienen(spieler, tisch, possible):
    # spielmacher
    if spieler.re:
        # sitzt hinten
        if len(tisch.stich) == 2:
            # hoechste karte
            if tisch.stich[0].isGreater(tisch.stich[1], tisch.trumpf):
                highest = tisch.stich[0]
            else:
                highest = tisch.stich[1]
            # versuche drueber zu kommen
            wahl = None
            for card in possible:
                if card.isGreater(highest, tisch.trumpf):
                    wahl = card
                else:
                    break
            if wahl:
                return wahl
            # ansonsten den kleinsten
            else:
                return possible[len(possible)-1]
        # sitzt in der mitte
        else:
            # versuche stich zu bekommen
            wahl = None
            for card in possible:
                if card.isGreater(tisch.stich[0], tisch.trumpf):
                    wahl = card
                else:
                    break
            if wahl:
                return wahl
            # ansonsten den kleinsten
            else:
                return smallest(possible)
    # kontra
    else:
        # sitzt hinten
        if len(tisch.stich) == 2:
            # hoechste karte
            if tisch.stich[0].isGreater(tisch.stich[1], tisch.trumpf):
                highest = tisch.stich[0]
            else:
                highest = tisch.stich[1]
            # partner hat den stich
            if not highest.owner.re:
                # kleinsten nehmen
                # TODO: AI
                return possible[len(possible)-1]
            # ansonsten, versuche stich zu bekommen
            else:
                wahl = None
                for card in possible:
                    if card.isGreater(highest, tisch.trumpf):
                        wahl = card
                    else:
                        break
                if wahl:
                    return wahl
                # ansonsten den kleinsten
                else:
                    return smallest(possible)
        # sitzt in der mitte
        else:
            # TODO: wo sitzt Partner?
            # versuche stich zu bekommen
            if possible[0].rank == ASS:
                return possible[0]

            wahl = None
            for card in possible:
                if card.isGreater(tisch.stich[0], tisch.trumpf):
                    wahl = card
                else:
                    break
            if wahl:
                return wahl
            # ansonsten den kleinsten
            else:
                return smallest(possible)

def stechenSchmieren(spieler, tisch):
    # eigene karten 
    own = {}
    own = splitCards(spieler.cards, tisch.trumpf)

    # gespielte karten
    played = {}
    if len(tisch.playedStiche) > 0:
        clist = []
        for stiche in tisch.playedStiche:
            clist.extend(stiche)
        played = splitCards(clist, tisch.trumpf)

    # spielmacher
    if spieler.re:
        # sitzt hinten
        if len(tisch.stich) == 2:
            # hoechste karte
            if tisch.stich[0].isGreater(tisch.stich[1], tisch.trumpf):
                highest = tisch.stich[0]
            else:
                highest = tisch.stich[1]
            # nicht nur luschen?
            if (tisch.stich[0].point + tisch.stich[1].point) >= 3:
                # versuche drueber zu kommen
                wahl = None
                for card in own[tisch.trumpf]:
                    if card.isGreater(highest, tisch.trumpf):
                        wahl = card
                    else:
                        break
                if wahl:
                    return wahl
            # abwerfen, wenn nur luschen oder nicht drueber kommt
            wahl = None
            for farbe in fehl(tisch.trumpf):
                for card in own[farbe]:
                    # kleinsten fehl aufwaehlen
                    if not wahl or wahl.point > card.point:
                        wahl = card
                    # wenn gleich, farbe stechen
                    elif wahl.point == card.point:
                        if len(own[farbe]) == 1:
                            wahl = card
            # TODO: AI
            # wenn wahl eine 10 oder ass, evtl doch kleinen trumpf
            if not wahl or wahl.rank == 10 or wahl.rank == ASS:
                wahl = smallest(own[tisch.trumpf])
            return wahl
        # sitzt in der mitte
        else:
            # wenn noch truempfe, dann stechen
            if len(own[tisch.trumpf]) > 0:
                # TODO: AI
                # hoechsten trumpf spielen
                return own[tisch.trumpf][0]
            # wenn keine truempfe, abwerfen
            else:
                wahl = None
                for farbe in fehl(tisch.trumpf):
                    for card in own[farbe]:
                        # kleinsten fehl aufwaehlen
                        if not wahl or wahl.point > card.point:
                            wahl = card
                        # wenn gleich, farbe stechen
                        elif wahl.point == card.point:
                            if len(own[farbe]) == 1:
                                wahl = card
                return wahl
    # kontra
    else:
        # sitzt hinten
        if len(tisch.stich) == 2:
            # hoechste karte
            if tisch.stich[0].isGreater(tisch.stich[1], tisch.trumpf):
                highest = tisch.stich[0]
            else:
                highest = tisch.stich[1]
            # partner hat den stich
            if not highest.owner.re:
                # TODO: AI
                # mit hoechstem fehl schmieren
                wahl = None
                for farbe in fehl(tisch.trumpf):
                    for card in own[farbe]:
                        if not wahl or card.point > wahl.point:
                            wahl = card
                        elif wahl.point == card.point:
                            if len(own[farbe]) == 1:
                                wahl = card
                if wahl:
                    return wahl
                # wenn kein fehl mehr, kleinen trumpf
                else:
                    return smallest(own[tisch.trumpf])
            # ansonsten, versuche stich zu bekommen
            else:
                # wenn noch truempfe, dann stechen
                if len(own[tisch.trumpf]) > 0:
                    # TODO: AI
                    # kleinst noetigsten trumpf spielen
                    wahl = None
                    for card in own[tisch.trumpf]:
                        if card.isGreater(tisch.stich[0], tisch.trumpf):
                            wahl = card
                        else:
                            break
                    if wahl:
                        return wahl
                # wenn keine ausreichenden truempfe, abwerfen
                wahl = None
                for farbe in fehl(tisch.trumpf):
                    for card in own[farbe]:
                        # kleinsten fehl aufwaehlen
                        if not wahl or wahl.point > card.point:
                            wahl = card
                        # wenn gleich, farbe stechen
                        elif wahl.point == card.point:
                            if len(own[farbe]) == 1:
                                wahl = card
                if wahl:
                    return wahl
                else:
                    return smallest(own[tisch.trumpf])
        # sitzt in der mitte
        else:
            # TODO: wo sitzt Partner?
            #       kann der Partner stechen?
            # wenn noch truempfe, dann stechen
            if len(own[tisch.trumpf]) > 0:
                # TODO: AI
                # hoechsten trumpf spielen
                return own[tisch.trumpf][0]
            # wenn keine truempfe, abwerfen
            else:
                wahl = None
                for farbe in fehl(tisch.trumpf):
                    for card in own[farbe]:
                        # kleinsten fehl aufwaehlen
                        if not wahl or wahl.point > card.point:
                            wahl = card
                        # wenn gleich, farbe stechen
                        elif wahl.point == card.point:
                            if len(own[farbe]) == 1:
                                wahl = card
                return wahl
