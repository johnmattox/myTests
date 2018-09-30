# TODO: acho que podemos importar mais coisas
# J: Talvez seja bom mesclar com outros cursos de engenharia (?)
# L: Pensei nisso. talvez "from poli import Mecanica, Minas, Civil, ...", etc

# J: Podemos importar as próprias ênfases da elétrica (PSI, PCS, PEA, PTC)...
# L: E se pegarmos mais matérias comuns? Estatística, Probabilidade, AlgeLin...
from poli import cursos_e_habilitações
from keras.models import Sequential
from pandas import read_csv
import numpy as np
class estudante_poli:

    def __init__(self,curso,energia=100):
        self.curso = curso
        self.energia = energia
        self.modelo = Sequential() 
                                   
    def estudar(self, train_data, validation_data):
        self.modelo.compile(loss='categorical_crossentropy', optimizer=sgd,
                            metrics=['accuracy'])
        self.modelo.fit(x=train_data['questoes'], y=train_data['gabaritos'],
                        validation_data=validation_data, epochs=3,
                        batch_size=(train_data.size()/5))
        self.energia -= 90

    def beber_cafe(self):
        self.energia += 30
        print('bebendo cafe')

    def dormir(self):
        self.energia = 100
        print('zzZZ... zzZZ...')


if __name__ == '__main__':
    # J: Gosto muito da idéia, talvez tenhamos que validar com o Itaú. validar... pegou essa ?!
    # L: hahahahah, entendo... e que tal...
    try:
        train_data = read_csv('listas_de_exercícios.csv')
        validation_data = read_csv('provas_antigas.csv')
    except ProvaAntigaNotFoundError:
        print('Não tem prova no Moodle?!')
        tudo_o_que_temos = read_csv('listas_de_exercícios.csv')
	train_data = tudo_o_que_temos.loc[: int(np.floor(tudo_o_que_temos.shape[0]*0.7)-1)]
	validation_data = tudo_o_que_temos.loc[int(np.floor(tudo_o_que_temos.shape[0]*0.7)):]
        #train_data      = tudo_o_que_temos[size(tudo_o_que_temos)*0.8 :]
        #validation_data = tudo_o_que_temos[: size(tudo_o_que_temos)*0.8]

    horasRestantes = 120
    p = estudante_poli('elétrica')
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
	        print('O quê? São 3 da manhã e eu ainda não sei nada?!') # L: HAHAHAHAHAHAHAHAHAHAHAHAHA
            #print('Energia: %d | Tempo restante: %d horas'%(p.energia,horasRestantes))

    # Hora do show
    p.evaluate(test_data=['P1', 'P2', 'P3'])
