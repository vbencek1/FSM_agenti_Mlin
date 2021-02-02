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
import random
import ast


class DrugiIgrac(Agent):
    def __init__(self, *args, xsb):
        super().__init__(*args)
        self.xsb = xsb
        self.kb = pyxf.xsb(self.xsb)
        self.kb.load("bazaMlin.P")

    class BehaviourFSM(FSMBehaviour):
        async def on_start(self):
            self.agent.say("Započinjem FSM ponašanje")

        async def on_end(self):
            self.agent.say("Završavam FSM ponašanje")

    class State1(State):
        async def run(self):
            self.agent.say("Stanje 1 -> Pozdravna poruka")
            msgD = await self.receive(timeout=20)
            if msgD:
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                msg = spade.message.Message(
                        to=str(msgD.sender),
                        body="Da želim igrati!")
                await self.send(msg)
                self.set_next_state("State2")
            else:
                self.set_next_state("State6")

    class State2(State):
        async def run(self):
            self.agent.say("Stanje 2 -> Početno postavljanje žetona")
            msgD = await self.receive(timeout=20)
            if msgD.body.split(";")[0]=="PocetnaPloca":
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                self.agent.zabiljeziPozicije(msgD.body)
                pozicija=self.agent.randomStrategija()
                msg = spade.message.Message(
                        to=str(msgD.sender),
                        body=str(pozicija))
                await self.send(msg)
                self.agent.mojiZetoni=self.agent.mojiZetoni-1
            if msgD.body.split(";")[0]=="Mlin":
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                self.agent.zabiljeziPozicije(msgD.body)
                zetonZaMaknut=self.agent.makniRandomZeton()
                msg = spade.message.Message(
                        to=str(msgD.sender),
                        body=str(zetonZaMaknut))
                await self.send(msg)
            if msgD.body=="Kraj":
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                self.set_next_state("State3")
            else:
                self.set_next_state("State2")

    class State3(State):
        async def run(self):
            self.agent.say("Stanje3 -> Kretanje zetonima po ploci")
            msgD = await self.receive(timeout=20)
            if msgD.body.split(";")[0]=="KretanjePloca":
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                self.agent.zabiljeziPozicije(msgD.body)
                pozicije=self.agent.randomStrategijaKretanja()
                msg = spade.message.Message(
                        to=str(msgD.sender),
                        body=str(pozicije))
                await self.send(msg)
                self.agent.mojiZetoni=self.agent.mojiZetoni-1
            if msgD.body.split(";")[0]=="Mlin":
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                self.agent.zabiljeziPozicije(msgD.body)
                zetonZaMaknut=self.agent.makniRandomZeton()
                msg = spade.message.Message(
                        to=str(msgD.sender),
                        body=str(zetonZaMaknut))
                await self.send(msg)
            if msgD.body=="Skaci":
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                self.set_next_state("State4")
            elif msgD.body=="Kraj":
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                self.set_next_state("State5")
            else:
                self.set_next_state("State3")

    class State4(State):
        async def run(self):
            self.agent.say("Stanje4 -> Skakanje zetonima po ploci")
            msgD = await self.receive(timeout=20)
            if msgD.body.split(";")[0]=="KretanjePloca":
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                self.agent.zabiljeziPozicije(msgD.body)
                pozicije=self.agent.offensiveStrategijaSkakanja()
                msg = spade.message.Message(
                        to=str(msgD.sender),
                        body=str(pozicije))
                await self.send(msg)
                self.agent.mojiZetoni=self.agent.mojiZetoni-1
            if msgD.body.split(";")[0]=="Mlin":
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                self.agent.zabiljeziPozicije(msgD.body)
                zetonZaMaknut=self.agent.makniRandomZeton()
                msg = spade.message.Message(
                        to=str(msgD.sender),
                        body=str(zetonZaMaknut))
                await self.send(msg)
            if msgD.body=="Kraj":
                self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
                self.set_next_state("State5")
            else:
                self.set_next_state("State4")

    class State5(State):
        async def run(self):
            self.agent.say("Stanje5 -> Pozdravne poruke za kraj")
            msgD = await self.receive(timeout=20)
            self.agent.say(f"{msgD.sender} šalje poruku: {msgD.body}")
            self.set_next_state("State6")

    class State6(State):
        async def run(self):
            self.agent.say("Stanje6 -> Kraj rada")
            await self.agent.stop()

    async def setup(self):
        fsm = self.BehaviourFSM()
        self.mojiZetoni=9
        self.pozicijePrvog=[]
        self.pozicijeDrugog=[]
        fsm.add_state(name="State1", state=self.State1(), initial=True) #Pozdrav
        fsm.add_state(name="State2", state=self.State2()) #Pocetno postavljanje zetona
        fsm.add_state(name="State3", state=self.State3()) #Kretanje zetonima po ploci
        fsm.add_state(name="State4", state=self.State4()) #Skakanje zetonima po ploci
        fsm.add_state(name="State5", state=self.State5()) #Aktivnosti kraja
        fsm.add_state(name="State6", state=self.State6()) #Kraj
        fsm.add_transition(source="State1", dest="State1")
        fsm.add_transition(source="State1", dest="State2")
        fsm.add_transition(source="State2", dest="State3")
        fsm.add_transition(source="State2", dest="State2")
        fsm.add_transition(source="State3", dest="State4")
        fsm.add_transition(source="State3", dest="State3")
        fsm.add_transition(source="State3", dest="State5")
        fsm.add_transition(source="State4", dest="State5")
        fsm.add_transition(source="State4", dest="State4")
        fsm.add_transition(source="State5", dest="State6")
        fsm.add_transition(source="State1", dest="State6")
        self.add_behaviour(fsm)

    def say(self, line):
        print(f"{self.name}: {line}")

    def zabiljeziPozicije(self,poruka):
        polje=poruka.split(";")
        pozPrvog=ast.literal_eval(polje[1])
        pozDrugog=ast.literal_eval(polje[2])
        pomocnaListaPr=[]
        pomocnaListaDr=[]
        if pozPrvog !=False:
            for broj in pozPrvog:
                pomocnaListaPr.append(broj['Y'])
        if pozDrugog !=False:
            for broj in pozDrugog:
                pomocnaListaDr.append(broj['Y'])
        self.pozicijePrvog=pomocnaListaPr
        self.pozicijeDrugog=pomocnaListaDr

    def randomStrategija(self):
        broj=randint(1,24)
        while(True):
            if str(broj) not in self.pozicijePrvog and str(broj) not in self.pozicijeDrugog:
                break
            else:
                broj=randint(1,24)
        return broj

    def randomStrategijaKretanja(self):
        brojTo=randint(1,24)
        brojFrom=randint(1,24)
        while(True):
            if str(brojTo) not in self.pozicijePrvog and str(brojTo) not in self.pozicijeDrugog:
                upit=self.kb.query("pozicija(X,"+str(brojTo)+").")
                opcije=[]
                for poz in upit:
                    opcije.append(poz['X'])
                brojFrom=random.choice(opcije)
                if str(brojFrom) in self.pozicijeDrugog:
                    break
                else:
                    brojTo=randint(1,24)
            else:
                brojTo=randint(1,24)
        return str(brojFrom)+";"+str(brojTo)

    def randomStrategijaSkakanja(self):
        brojTo=randint(1,24)
        brojFrom=randint(1,24)
        while(True):
            if str(brojTo) not in self.pozicijePrvog and str(brojTo) not in self.pozicijeDrugog:
                break
            else:
                brojTo=randint(1,24)
        while(True):
            if str(brojFrom) in self.pozicijeDrugog:
                break
            else:
                brojFrom=randint(1,24)
        return str(brojFrom)+";"+str(brojTo)

    def offensiveStrategijaSkakanja(self):
        slobodnePozicije=[]
        for x in range(1,25):
            if str(x) not in self.pozicijePrvog and str(x) not in self.pozicijeDrugog:
                slobodnePozicije.append(x)
        for x in slobodnePozicije:
            upit=self.kb.query("mlin("+str(x)+",Y,Z).")
            for poz in upit:
                if poz['Y'] in self.pozicijeDrugog and poz['Z'] in self.pozicijeDrugog:
                    upit2=self.pozicijeDrugog
                    for y in upit2:
                        if y!=poz['Y'] and y!=poz['Z']:
                            self.say("Aktivirana strategija ofenzive")
                            return str(y)+";"+str(x)

        return self.randomStrategijaSkakanja()

    def makniRandomZeton(self):
        broj=randint(1,24)
        while(True):
            if str(broj) in self.pozicijePrvog:
                break
            else:
                broj=randint(1,24)
        return broj

if __name__ == '__main__':
    #/home/vjezbe/software/Flora-2/XSB/bin
    parser = argparse.ArgumentParser(description="Primjer pokretanja: %(prog)s -p /home/vjezbe/software/Flora-2/XSB/bin/xsb -jid agentVB@localhost -pwd 123456")
    parser.add_argument("-p", "--putanja", type=str, help="Putanja do XSB", default="/home/vjezbe/software/Flora-2/XSB/bin/xsb")
    parser.add_argument("-jid", type=str, help="JID Drugog Igraca", default="agentVB@localhost")
    parser.add_argument("-pwd", type=str, help="Lozinka Drugog Igraca", default="123456")
    args = parser.parse_args()
    agentAutomaton = DrugiIgrac(args.jid, args.pwd, xsb=args.putanja)
    agentAutomaton.start()
    input("Pritisni Enter za izlaz.\n")
    agentAutomaton.stop()
    quit_spade()
