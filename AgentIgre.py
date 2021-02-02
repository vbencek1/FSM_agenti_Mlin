#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade import quit_spade
from random import randint
import argparse
from pyxf import pyxf


class AgentIgre(Agent):
    def __init__(self, *args, xsb, igraci, pauza):
        super().__init__(*args)
        self.xsb = xsb
        self.agenti=igraci
        self.pauza=pauza
        self.kb = pyxf.xsb(self.xsb)
        self.kb.load("bazaMlin.P")

    class BehaviourFSM(FSMBehaviour):
        async def on_start(self):
            self.agent.say("Započinjem FSM ponašanje")
            print("Izgled ploče i njene pozicije:")
            print("01------------02-----------03")
            print("|             |             |")
            print("|  09---------10--------11  |")
            print("|  |          |         |   |")
            print("|  |     17---18---19   |   |")
            print("|  |     |         |    |   |")
            print("08--16---24        20---12--4")
            print("|  |     |         |    |   |")
            print("|  |     23---22---21   |   |")
            print("|  |          |         |   |")
            print("|  15---------14--------13  |")
            print("|             |             |")
            print("07------------06------------05")

        async def on_end(self):
            self.agent.say("Završavam FSM ponašanje")

    class State1(State):
        async def run(self):
            self.agent.say("Stanje1 -> Dohvat agenata")
            brojac=0
            for primatelj in self.agent.agenti:
                msg = spade.message.Message(
                        to=primatelj,
                        body="Želiš li igrati?")
                await self.send(msg)
                msgD = await self.receive(timeout=20)
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                if (msgD.body=="Da želim igrati!"):
                    brojac=brojac+1
            if brojac ==2:
                self.set_next_state("State2")
            else:
                self.set_next_state("State5")

    class State2(State):
        async def run(self):
            self.agent.say("Stanje2 -> PočetakIgre/Postavljanje Žetona")
            for primatelj in self.agent.agenti:
                msg = spade.message.Message(
                        to=primatelj,
                        body="PocetnaPloca;"+str(self.agent.postavljeniZetoni(0))+";"+str(self.agent.postavljeniZetoni(1)))
                await self.send(msg)
                msgD = await self.receive(timeout=20)
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                index=self.agent.agenti.index(primatelj)
                self.agent.zetoni[index]=self.agent.zetoni[index]-1
                self.agent.postaviZeton(index,msgD.body)
                if self.agent.provjeriMlin(index,msgD.body):
                    self.agent.say("MLIN!")
                    msg = spade.message.Message(
                            to=primatelj,
                            body="Mlin;"+str(self.agent.postavljeniZetoni(0))
                             +";"+str(self.agent.postavljeniZetoni(1)))
                    await self.send(msg)
                    msgD = await self.receive(timeout=20)
                    self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                    self.agent.say(f"Maknut žeton na poziciji {msgD.body}!")
                    self.agent.makniZetonSuparnika(index,msgD.body)
                time.sleep(self.agent.pauza)
            if (self.agent.zetoni[0]>0 or self.agent.zetoni[1]>0):
                self.set_next_state("State2")
            else:
                for primatelj in self.agent.agenti:
                    msg = spade.message.Message(
                            to=primatelj,
                            body="Kraj")
                    await self.send(msg)
                self.agent.zetoniIgra[0]=self.agent.zetoniIgra[0]-self.agent.maknutiZetoni[0]
                self.agent.zetoniIgra[1]=self.agent.zetoniIgra[1]-self.agent.maknutiZetoni[1]
                self.set_next_state("State3")

    class State3(State):
        async def run(self):
            self.agent.say("Stanje3 -> Kretanje zetonima po ploci")
            for primatelj in self.agent.agenti:
                if(self.agent.zetoniIgra[0]==2 or self.agent.zetoniIgra[1]==2):
                    self.set_next_state("State4")
                else:
                    msg = spade.message.Message(
                            to=primatelj,
                            body="KretanjePloca;"+str(self.agent.postavljeniZetoni(0))
                            +";"+str(self.agent.postavljeniZetoni(1)))
                    await self.send(msg)
                    msgD = await self.receive(timeout=20)
                    self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                    index=self.agent.agenti.index(primatelj)
                    self.agent.say(f"Pomak žetona: {msgD.body.split(';')[0]} -> {msgD.body.split(';')[1]}")
                    self.agent.pomakniZeton(index,msgD.body.split(";")[0],msgD.body.split(";")[1])
                    if self.agent.provjeriMlin(index,msgD.body.split(";")[1]):
                        self.agent.say("MLIN!")
                        msg = spade.message.Message(
                                to=primatelj,
                                body="Mlin;"+str(self.agent.postavljeniZetoni(0))
                                 +";"+str(self.agent.postavljeniZetoni(1)))
                        await self.send(msg)
                        msgD = await self.receive(timeout=20)
                        self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                        self.agent.say(f"Maknut žeton na poziciji {msgD.body}!")
                        self.agent.makniZetonSuparnikaFazaIgre(index,msgD.body)
                        suparnik=0
                        if index==0:
                            suparnik=1
                        if self.agent.zetoniIgra[suparnik]==4 and self.agent.brojac[suparnik]==0:
                            self.agent.brojac[suparnik]=1
                            msg = spade.message.Message(
                                to=self.agent.agenti[suparnik],
                                body="Skaci")
                            await self.send(msg)
                    time.sleep(self.agent.pauza)
            if (self.agent.zetoniIgra[0]>2 and self.agent.zetoniIgra[1]>2):
                self.set_next_state("State3")
            else:
                self.set_next_state("State4")

    class State4(State):
        async def run(self):
            self.agent.say("Stanje4 -> Proglašenje pobjednika")
            for primatelj in self.agent.agenti:
                msg = spade.message.Message(
                        to=primatelj,
                        body="Kraj")
                await self.send(msg)
            pobjednik=0
            if self.agent.zetoniIgra[0]==2:
                pobjednik=1
                self.agent.say(f"Pobjednik je:{self.agent.agenti[1]} Čestitke!")
            else:
                pobjednik=0
                self.agent.say(f"Pobjednik je:{self.agent.agenti[0]} Čestitke!")
            for primatelj in self.agent.agenti:
                index=self.agent.agenti.index(primatelj)
                poruka="Čestitke na pobjedi!"
                if pobjednik !=index:
                    poruka="Nažalost nisi pobjedio. Više sreće drugi put!"
                msg = spade.message.Message(
                        to=primatelj,
                        body=poruka)
                await self.send(msg)
            self.set_next_state("State5")


    class State5(State):
        async def run(self):
            self.agent.say("Stanje5 -> Kraj")
            await self.agent.stop()


    async def setup(self):
        fsm = self.BehaviourFSM()
        self.zetoni=[9,9] #0 - žetoni prvog igrača 1-žetoni drugog igrača
        self.maknutiZetoni=[0,0] #0 - žetoni prvog igrača 1-žetoni drugog igrača
        self.zetoniIgra=[9,9] #0 - žetoni prvog igrača 1-žetoni drugog igrača
        self.brojac=[0,0]
        self.pozicije=['null','¤','¤','¤','¤','¤','¤','¤','¤','¤','¤'
            ,'¤','¤','¤','¤','¤','¤','¤','¤','¤','¤','¤','¤','¤','¤']
        fsm.add_state(name="State1", state=self.State1(), initial=True)  #Pozdrav
        fsm.add_state(name="State2", state=self.State2())   #Pocetno postavljanje zetona
        fsm.add_state(name="State3", state=self.State3())   #Kretanje zetona po ploci
        fsm.add_state(name="State4", state=self.State4())   #Zavrsetak igre i proglasenje pobjednika
        fsm.add_state(name="State5", state=self.State5())   #Kraj
        fsm.add_transition(source="State1", dest="State2")
        fsm.add_transition(source="State2", dest="State3")
        fsm.add_transition(source="State2", dest="State2")
        fsm.add_transition(source="State3", dest="State4")
        fsm.add_transition(source="State3", dest="State3")
        fsm.add_transition(source="State4", dest="State5")
        fsm.add_transition(source="State1", dest="State5")
        self.add_behaviour(fsm)

    def say(self, line):
        print(f"{self.name}: {line}")

    def postaviZeton(self,igrac,pozicija):
        self.kb.query("assert(pocetnaPozicija("+str(igrac)+","+str(pozicija)+")).")
        novaPozicija="O"
        if igrac==1:
            novaPozicija="X"
        self.pozicije[int(pozicija)]=novaPozicija
        print(str(self.agenti[0])+" (Broj žetona za postaviti): "+str(self.zetoni[0]))
        print(str(self.agenti[1])+" (Broj žetona za postaviti): "+str(self.zetoni[1]))
        self.ispisiPlocu()

    def pomakniZeton(self,igrac,staraPoz,novaPoz):
        self.kb.query("retract(pocetnaPozicija("+str(igrac)+","+str(staraPoz)+")).")
        self.kb.query("assert(pocetnaPozicija("+str(igrac)+","+str(novaPoz)+")).")
        novaPozicija="O"
        if igrac==1:
            novaPozicija="X"
        self.pozicije[int(staraPoz)]="¤"
        self.pozicije[int(novaPoz)]=novaPozicija
        print(str(self.agenti[0])+" (Broj žetona): "+str(self.zetoniIgra[0]))
        print(str(self.agenti[1])+" (Broj žetona): "+str(self.zetoniIgra[1]))
        self.ispisiPlocu()

    def makniZetonSuparnika(self,igrac,pozicija):
        suparnik=0
        if igrac==0:
            suparnik=1
        self.kb.query("retract(pocetnaPozicija("+str(suparnik)+","+str(pozicija)+")).")
        self.pozicije[int(pozicija)]="¤"
        self.maknutiZetoni[suparnik]=self.maknutiZetoni[suparnik]+1
        self.ispisiPlocu()

    def makniZetonSuparnikaFazaIgre(self,igrac,pozicija):
        suparnik=0
        if igrac==0:
            suparnik=1
        self.kb.query("retract(pocetnaPozicija("+str(suparnik)+","+str(pozicija)+")).")
        self.pozicije[int(pozicija)]="¤"
        self.zetoniIgra[suparnik]=self.zetoniIgra[suparnik]-1
        print(str(self.agenti[0])+" (Broj žetona): "+str(self.zetoniIgra[0]))
        print(str(self.agenti[1])+" (Broj žetona): "+str(self.zetoniIgra[1]))
        self.ispisiPlocu()

    def provjeriMlin(self,igrac,pozicija):
        mlin=self.kb.query("ProvjeriMlin("+str(igrac)+",Y).")
        if not mlin:
            return False
        for p in mlin:
            if str(p['Y'])==str(pozicija):
                return True
        return False

    def postavljeniZetoni(self,igrac):
        zetoni=self.kb.query("pocetnaPozicija("+str(igrac)+",Y).")
        return zetoni

    def ispisiPlocu(self):
        polje=self.pozicije
        print(f"{polje[1]}----------{polje[2]}----------{polje[3]}")
        print(f"|          |          |")
        print(f"|  {polje[9]}-------{polje[10]}-------{polje[11]}  |")
        print(f"|  |       |       |  |")
        print(f"|  |   {polje[17]}---{polje[18]}---{polje[19]}   |  |")
        print(f"|  |   |       |   |  |")
        print(f"{polje[8]}--{polje[16]}---{polje[24]}       {polje[20]}---{polje[12]}--{polje[4]}")
        print(f"|  |   |       |   |  |")
        print(f"|  |   {polje[23]}---{polje[22]}---{polje[21]}   |  |")
        print(f"|  |       |       |  |")
        print(f"|  {polje[15]}-------{polje[14]}-------{polje[13]}  |")
        print(f"|          |          |")
        print(f"{polje[7]}----------{polje[6]}----------{polje[5]}")


if __name__ == '__main__':
    #/home/vjezbe/software/Flora-2/XSB/bin
    parser = argparse.ArgumentParser(description="Primjer pokretanja: %(prog)s -p /home/vjezbe/software/Flora-2/XSB/bin/xsb  -jid vbencekIgra@localhost -pwd 123456 -jidp vbencek@localhost -jidd agentVB@localhost -t 1")
    parser.add_argument("-p", "--putanja", type=str, help="Putanja do XSB", default="/home/vjezbe/software/Flora-2/XSB/bin/xsb")
    parser.add_argument("-jid", type=str, help="JID Agenta Igre", default="vbencekIgra@localhost")
    parser.add_argument("-pwd", type=str, help="Lozinka Agenta Igre", default="123456")
    parser.add_argument("-jidp", "--prviA", type=str, help="JID Prvog Igraca", default="vbencek@localhost")
    parser.add_argument("-jidd", "--drugiA", type=str, help="JID Drugog Igraca", default="agentVB@localhost")
    parser.add_argument("-t", "--pauza", type=int, help="pauza prilikom ispisa", default="1")
    args = parser.parse_args()
    agenti=[args.prviA,args.drugiA]
    agentAutomaton = AgentIgre(args.jid, args.pwd, xsb=args.putanja,igraci=agenti,pauza=args.pauza)
    agentAutomaton.start()
    input("Pritisni Enter za izlaz.\n")
    agentAutomaton.stop()
    quit_spade()
