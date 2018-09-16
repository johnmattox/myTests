# -*- coding: utf-8 -*-

class polytechnic:
    
    def __init__(self,course,energy=100):
        self.course = course
        self.energy = energy
        
    def study(self):
        self.energy -= 90
        
    def drink_coffee(self):
        self.energy += 30
        
    def sleep(self):
        self.energy = 100
        
tests = ['MecFlu','SisPot','EletroMag','Numérico','Eletrônica','Controle']
hoursLeft = 120
p = polytechnic('elétrica')

for t in tests:
    if p.energy <= 10:
        if hoursLeft >= 48:
            print('sleeping')
            p.sleep()
            hoursLeft -= 8
        else:
            while(p.energy <= 50):
                print('drinking coffee')
                p.drink_coffee()
    p.study()
    hoursLeft -= 16
    print('energy: %d | Left: %d'%(p.energy,hoursLeft))