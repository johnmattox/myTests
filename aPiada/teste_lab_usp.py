# TODO: acho que podemos importar mais coisas
# Talvez seja bom mesclar com outros cursos de engenharia (?)
# Podemos importar as próprias ênfases da elétrica (PSI, PCS, PEA, PTC)...
from poli import SisPot, EletroMag, CalcNum, Eletronica, Controle
from keras.models import Sequential
from pandas import read_csv
# Perguntar para meninas do Turing se elas se sentem contempladas com "politacnico":
class politecnico:

    def __init__(self,curso,energia=100):
        self.curso = curso
        self.energia = energia
        self.modelo = Sequential()

    def estudar(self, train_data, validation_data):
        self.modelo.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
        self.modelo.fit(x='questoes', y='gabarito', epochs=3, batch_size=(lista.size()/4))
        self.energia -= 90

    def beber_cafe(self):
        self.energia += 30
        print('bebendo cafe')

    def dormir(self):
        self.energia = 100
        print('zzZZ... zzZZ...')


if __name__ == '__main__':

    train_data = read_csv('listas_de_exercícios.csv')
    # Gosto muito da idéia, talvez tenhamos que validar com o Itaú. validar... pegou essa ?!
    validation_data = read_csv('provas_antigas.csv')

    horasRestantes = 120
    p = politecnico('elétrica')
    while (horasRestantes > 0):

        try:
            p.estudar(train_data, validation_data)
            horasRestantes -= 10
        except OutOfEnergyError:
            print('Você precisa descansar!')
            if horasRestantes >= 24:
                p.dormir()
                horasRestantes -= 8
            else:
                p.beber_cafe()
	        print('O quê? São 3 da manhã e eu ainda não sei nada?!')
            #print('Energia: %d | Tempo restante: %d horas'%(p.energia,horasRestantes))

    # Hora do show
    p.evaluate(test_data=['P1', 'P2', 'P3'])
