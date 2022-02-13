from scipy.linalg import lstsq
import numpy as np
import pandas as pd
import pygsheets
from IPython.core import display as ICD

relative_height = 1
relative_height_FII = 1

Aporte = -1
while Aporte < 0:
    Aporte = int(input('\rInsira o aporte (0 para apenas rebalanceamento): '))
permitir_retiradas = -1
while permitir_retiradas!=('S') and permitir_retiradas!=('N'):
    permitir_retiradas = input('\rPermitir retiradas para rebalanceamento? (S/N): ')
permitir_retiradas = permitir_retiradas=='S'

gc=pygsheets.authorize(service_file='spreadsheets-functions-5e4b27424a28.json')
sh = gc.open('Wallet')
wks_g = sh.worksheet('title','Balanceamento')
wks_fii = sh.worksheet('title','FII Distribuição')
wks_output = sh.worksheet('title','output_rebal')

def clean_float(v):
    v=v.strip()
    if v=="": return 0
    pct = "%" in v
    try:
        v = float(v.replace("R$","").replace("%","").replace(",",""))
    except:
        print(v)
    if pct: v/=100
    return v

def linear_solve(valores_atuais,montante_atual,Aporte,pcts_meta):
    MA = np.vstack((np.eye((len(valores_atuais))),np.ones(len(valores_atuais))))
    MB = np.hstack(((pcts_meta*(montante_atual+Aporte)-valores_atuais)/Aporte,[1]))
    return lstsq(MA,MB)[0]

def distribui_retiradas(results):
    results_list = list(results)
    results_adj_list = list(results[results>0]/sum(results[results>0]))
    i=0
    results_adj = []
    for r in results_list:
        if r>0: 
            results_adj+=[results_adj_list[i]]
            i+=1
        else: results_adj+=[0.0]
    return results_adj

def df_to_sheet(df):
    df_columns = [np.array(df.columns)]
    df_values = df.values.tolist()
    df_to_sheet = np.concatenate((df_columns, df_values)).tolist()
    return df_to_sheet

if Aporte==0: Aporte=1
# Carrega dados gerais (pivot table em 'Balanceamento')
dados_gerais = pd.DataFrame(wks_g.get_values("N%d"%(16+relative_height),"O%d"%(22+relative_height)),columns=['Categoria','Valor'])
dados_gerais['Valor'] = [clean_float(v) if type(v)==str else v for v in dados_gerais['Valor']]
# Junta "Caixa" com "Reserva de Emerg."
dados_gerais = dados_gerais.replace({'Categoria':{'Caixa':'Caixa_e_Emergencia','Reserva Emerg.':'Caixa_e_Emergencia'}}).groupby(by='Categoria').sum().reset_index()
# Carrega tabela geral em 'Balanceamento'
metas_gerais_brt = pd.DataFrame(wks_g.get_values("A3","H16"),columns=['Categoria','Cat_maior','Desc','Montante','pct_micro','pct_meta','pct_hoje','pct_atual_grupo'])
for col in metas_gerais_brt.columns[3:]:
    metas_gerais_brt[col] = [clean_float(v) if type(v)==str else v for v in metas_gerais_brt[col].fillna(0)]
# Junta "Caixa" com "Reserva de Emerg." e soma valores por categoria
metas_gerais = metas_gerais_brt.replace({'Categoria':{'Caixa':'Caixa_e_Emergencia','Reserva Emerg.':'Caixa_e_Emergencia'}}).groupby(by='Categoria').sum().reset_index().copy()
metas_gerais = metas_gerais[['Categoria','pct_meta','pct_hoje']].groupby(by='Categoria').sum().reset_index()
# Separa quebra entre Ações e FIIs
metas_rv = metas_gerais_brt.loc[metas_gerais_brt['Categoria']=='Renda Variável'].copy()
metas_rv.loc[:,'Desc'] = ['Ações' if 'Ações' in r else 'FII' for r in metas_rv['Desc']]
metas_rv = metas_rv[['Desc','pct_micro']].groupby(by='Desc').sum().reset_index()
# Carrega dados FIIs (pivot table em 'FII Distribuição')
dados_fiis = pd.DataFrame(wks_fii.get_values("Q9","U14"),columns=['Tipo','Valor','pct_hoje','div_esp','yield_categ'])
for col in dados_fiis.columns[1:]:
    dados_fiis[col] = [clean_float(v) if type(v)==str else v for v in dados_fiis[col]]
# Carrega metas de FIIs (tabela de metas no canto inferior direito em 'FII Distribuição)
metas_fiis = pd.DataFrame(wks_fii.get_values("Q%d"%(23+relative_height_FII),"R%d"%(27+relative_height_FII)),columns=['Tipo','pct_meta'])
metas_fiis['pct_meta'] = [clean_float(v) if type(v)==str else v for v in metas_fiis['pct_meta']]
metas_fiis = pd.merge(dados_fiis.loc[dados_fiis['Tipo']!='Grand Total',['Tipo','pct_hoje']],metas_fiis,on='Tipo',how='left')

# GERAL

montante_atual = dados_gerais.loc[dados_gerais['Categoria']=='Grand Total','Valor'].values[0]

categorias = np.array(dados_gerais.sort_values(by='Categoria').loc[dados_gerais['Categoria']!='Grand Total','Categoria'])
valores_atuais = np.array(dados_gerais.sort_values(by='Categoria').loc[dados_gerais['Categoria']!='Grand Total','Valor'])
pcts_meta = np.array(metas_gerais.sort_values(by='Categoria')['pct_meta'])

# Gera matrizes para sistema linear e resolve
results = linear_solve(valores_atuais,montante_atual,Aporte,pcts_meta)

# Gera dataframe com resultados
final_geral = pd.DataFrame({'Categoria':categorias,'Aportar/Rebal':results*Aporte})
# Se o usuário não deseja realizar vendas para rebalanceamento, redistribui as porcentagens das vendas
if not permitir_retiradas: 
    results_adj = distribui_retiradas(results)
    final_geral['Só Aportar'] = np.array(results_adj)*Aporte

# FIIs

montante_atual_fii = dados_fiis.loc[dados_fiis['Tipo']=='Grand Total','Valor'].values[0]
# Calcula quanto to aporte em RV deve ir pra FII (baseado na porcentagem "micro" de RV)
pct_aporte_rv_em_fii = (metas_rv.loc[metas_rv['Desc']=='FII','pct_micro']/sum(metas_rv['pct_micro'])).values[0]
if permitir_retiradas: 
    Aporte_fii = pct_aporte_rv_em_fii*final_geral.loc[final_geral['Categoria']=='Renda Variável']['Aportar/Rebal'].values[0]
    Aporte_acoes = (1-pct_aporte_rv_em_fii)*final_geral.loc[final_geral['Categoria']=='Renda Variável']['Aportar/Rebal'].values[0]
else : 
    Aporte_fii = pct_aporte_rv_em_fii*final_geral.loc[final_geral['Categoria']=='Renda Variável']['Só Aportar'].values[0]
    Aporte_acoes = (1-pct_aporte_rv_em_fii)*final_geral.loc[final_geral['Categoria']=='Renda Variável']['Só Aportar'].values[0]

categorias_fii = np.array(dados_fiis.sort_values(by='Tipo').loc[dados_fiis['Tipo']!='Grand Total','Tipo'])
valores_atuais_fii = np.array(dados_fiis.sort_values(by='Tipo').loc[dados_fiis['Tipo']!='Grand Total','Valor'])
pcts_meta_fii = np.array(metas_fiis.sort_values(by='Tipo')['pct_meta'])

# Gera matrizes para sistema linear e resolve
results_fii = linear_solve(valores_atuais_fii,montante_atual_fii,Aporte_fii,pcts_meta_fii)

# Gera dataframe com resultados Fii
final_fii = pd.DataFrame({'Categoria':categorias_fii,'Aportar/Rebal':results_fii*Aporte_fii})
# Se o usuário não deseja realizar vendas para rebalanceamento, redistribui as porcentagens das vendas
if not permitir_retiradas: 
    results_adj_fii = distribui_retiradas(results_fii)
    final_fii['Só Aportar'] = np.array(results_adj_fii)*Aporte_fii
    
print("Resultados para carteira Geral:")
ICD.display(final_geral)
print("\n\nResultados para carteira Renda Variável:")
print("\nAporte em Ações: R$%.2f"%Aporte_acoes)
ICD.display(final_fii)

# Atualiza sheet da planilha Wallet
wks_output.clear()
wks_output.update_value("A1","Aporte de R$%.2f"%Aporte)
if permitir_retiradas: wks_output.update_value("A2","Rebalancear com retiradas")
else: wks_output.update_value("A2","Apenas aportar (sem retiradas)")
row_ini=4
wks_output.update_value("A%d"%(row_ini),"Resultados para Carteira Geral")
wks_output.update_values("A%d"%(row_ini+1),df_to_sheet(final_geral))

wks_output.update_value("A%d"%(row_ini+3+final_geral.shape[0]),"Resultados para Carteira RV")
wks_output.update_values("A%d"%(row_ini+4+final_geral.shape[0]),df_to_sheet(final_fii))
wks_output.update_value("A%d"%(row_ini+5+final_geral.shape[0]+final_fii.shape[0]),"Aporte em Ações: R$%.2f"%Aporte_acoes)

input("Pressione qualquer tecla para sair.")